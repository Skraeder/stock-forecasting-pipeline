"""Descargas reanudables. No crea noticias ni credenciales ficticias."""
import json
import os
import time
from pathlib import Path
import pandas as pd
import requests
from src.utils.common import (parser, config, fingerprint, checksum,
                              write_json, utc_now, event, fail_main)

def download_prices(c, root):
    import yfinance as yf
    start = (pd.Timestamp(c['start'])-pd.Timedelta(days=c['warmup_days'])).strftime('%Y-%m-%d')
    path = root/'raw'/'prices'/f"{c['ticker']}_{start}_{c['end']}.csv"
    meta_path = path.with_suffix('.meta.json')
    if path.exists() and meta_path.exists():
        meta = json.loads(meta_path.read_text())
        if meta['sha256'] != checksum(path):
            raise RuntimeError('El snapshot de precios fue modificado. Restaura el archivo o usa otra carpeta data-root.')
        event(root, source='yahoo', status='cached', file=path.name)
        return path, meta
    try:
        df = yf.download(c['ticker'], start=start, end=c['end'], interval='1d',
                         auto_adjust=False, actions=True, multi_level_index=False,
                         progress=False, threads=False, timeout=30)
    except Exception:
        event(root, source='yahoo', status='error', reason='download_failed')
        raise RuntimeError('Falló Yahoo Finance. Revisa acceso a internet y vuelve a ejecutar.') from None
    if df is None or df.empty or not {'Close','Adj Close'}.issubset(df.columns):
        event(root, source='yahoo', status='error', reason='empty_or_missing_adjusted_close')
        raise RuntimeError('Yahoo no entregó precios completos con Adj Close.')
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.csv.tmp')
    # Snapshot tal como lo entrega el cliente: sin limpieza ni ajuste propio.
    df.to_csv(temp, index_label='Date')
    temp.replace(path)
    meta = {'source':'Yahoo Finance via yfinance','ticker':c['ticker'],
            'start':start,'end_exclusive':c['end'],'downloaded_at_utc':utc_now(),
            'rows':len(df),'sha256':checksum(path),'yfinance_version':yf.__version__}
    write_json(meta_path, meta)
    event(root, source='yahoo', status='ok', file=path.name, rows=len(df))
    return path, meta

def month_windows(a, b):
    while a < b:
        end = min(a+pd.offsets.MonthBegin(1), b)
        yield a, end
        a = end

class NewsClient:
    def __init__(self, c, root):
        self.c, self.root = c, root
        self.key = os.getenv('ALPHAVANTAGE_API_KEY','').strip()
        self.calls = 0
        self.session = requests.Session()

    def fetch(self, a, b):
        path = self.root/'raw'/'news'/f"{self.c['ticker']}_{a:%Y%m%dT%H%M}_{b:%Y%m%dT%H%M}.json"
        meta_path = path.with_suffix('.meta.json')
        if path.exists() and meta_path.exists():
            meta = json.loads(meta_path.read_text())
            if meta['sha256'] != checksum(path):
                raise RuntimeError('Un JSON de noticias fue modificado. Restaura el snapshot antes de procesar.')
            body = json.loads(path.read_text(encoding='utf-8'))
            event(self.root, source='alpha_vantage', status='cached', file=path.name)
        else:
            if not self.key:
                raise RuntimeError('Falta ALPHAVANTAGE_API_KEY. Usa una clave con acceso a NEWS_SENTIMENT; no la subas a GitHub.')
            if self.calls >= self.c['max_news_requests']:
                raise RuntimeError('Se alcanzó el presupuesto de solicitudes de esta ejecución. Las respuestas válidas quedaron guardadas; reanuda cuando tu cuota lo permita.')
            self.calls += 1
            params = {'function':'NEWS_SENTIMENT','tickers':self.c['ticker'],
                      'time_from':a.strftime('%Y%m%dT%H%M'),
                      'time_to':b.strftime('%Y%m%dT%H%M'),
                      'sort':'EARLIEST','limit':self.c['news_limit'],'apikey':self.key}
            try:
                response = self.session.get('https://www.alphavantage.co/query',params=params,timeout=40)
                if response.status_code != 200:
                    event(self.root, source='alpha_vantage', status='error', reason=f'http_{response.status_code}')
                    raise RuntimeError(f'Alpha Vantage respondió HTTP {response.status_code}; reanuda cuando el servicio esté disponible.')
                body = response.json()
            except (requests.RequestException, ValueError):
                event(self.root, source='alpha_vantage', status='error', reason='network_or_json')
                raise RuntimeError('Error de red o JSON en Alpha Vantage. No se imprimió la URL ni la clave.') from None
            finally:
                time.sleep(self.c['request_pause_seconds'])
            if not isinstance(body, dict) or not isinstance(body.get('feed'), list):
                event(self.root, source='alpha_vantage', status='error', reason='no_feed')
                raise RuntimeError('Alpha Vantage no entregó feed: revisa clave, permisos NEWS_SENTIMENT, cuota e histórico. No se considera una ventana sin noticias.')
            # Conservar el texto JSON sin modificar los registros.
            path.parent.mkdir(parents=True, exist_ok=True)
            temp = path.with_suffix('.json.tmp')
            temp.write_text(response.text, encoding='utf-8')
            temp.replace(path)
            meta = {'source':'Alpha Vantage NEWS_SENTIMENT','ticker':self.c['ticker'],
                    'window_start_utc':str(a),'window_end_exclusive_utc':str(b),
                    'downloaded_at_utc':utc_now(),'rows':len(body['feed']),
                    'requested_limit':self.c['news_limit'],'sha256':checksum(path)}
            write_json(meta_path, meta)
            event(self.root, source='alpha_vantage', status='ok', file=path.name, rows=len(body['feed']))
        if not isinstance(body.get('feed'), list):
            raise RuntimeError('Caché inválida: falta feed.')
        if len(body['feed']) >= int(meta['requested_limit']):
            minutes = int((b-a).total_seconds()//60)
            if minutes <= self.c['minimum_news_window_minutes'] or minutes < 2:
                raise RuntimeError('Ventana mínima saturada; no se puede garantizar cobertura. No se procesarán datos truncados.')
            mid = a+pd.Timedelta(minutes=minutes//2)
            return self.fetch(a, mid)+self.fetch(mid, b)
        # Solo hojas no saturadas. El procesamiento aplicará [a,b) y deduplicación.
        return [{'file':str(path.relative_to(self.root)), 'sha256':checksum(path),
                 'start_utc':str(a),'end_exclusive_utc':str(b),'returned_articles':len(body['feed'])}]

def download_news(c, root):
    leaves = []
    client = NewsClient(c, root)
    a,b = pd.Timestamp(c['start'],tz='UTC'),pd.Timestamp(c['end'],tz='UTC')
    try:
        windows = list(month_windows(a,b))
        for i,(left,right) in enumerate(windows,1):
            leaves.extend(client.fetch(left,right))
            print(f'Noticias: ventana {i}/{len(windows)} terminada; nuevas solicitudes: {client.calls}')
    finally:
        client.session.close()
    path = root/'raw'/'news_manifest.json'
    manifest = {'config':fingerprint(c),'complete':True,'created_at_utc':utc_now(),
                'coverage_note':'Ventanas respondidas sin alcanzar el límite; no prueba exhaustividad del proveedor.',
                'windows':leaves}
    write_json(path, manifest)
    return path

def main():
    p = parser('Adquisición de precios y noticias de una acción.')
    p.add_argument('--source', choices=['prices','news','all'], default='all')
    args = p.parse_args()
    c,root = config(args.config),Path(args.data_root).expanduser().resolve()
    if args.source in ('prices','all'):
        path,meta = download_prices(c,root)
        write_json(root/'raw'/'prices_manifest.json', {'config':fingerprint(c),
                   'file':str(path.relative_to(root)),'sha256':meta['sha256']})
        print(f"Precios guardados/reutilizados: {meta['rows']} registros.")
    if args.source in ('news','all'):
        download_news(c,root)
        print('Manifiesto de noticias completo para el periodo solicitado.')

if __name__ == '__main__':
    fail_main(main)
