"""raw -> interim -> processed. Alinea noticias con cierres reales NASDAQ."""
import json
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import pandas_market_calendars as mcal
from src.utils.common import (parser, config, fingerprint, checksum,
                              write_json, utc_now, fail_main)

def read_manifest(root, name, c):
    path = root/'raw'/name
    if not path.exists():
        raise RuntimeError(f'Falta {name}. Completa la adquisición correspondiente.')
    result = json.loads(path.read_text(encoding='utf-8'))
    if result['config'] != fingerprint(c):
        raise RuntimeError(f'{name} no corresponde a la configuración. Usa otra data-root para otro periodo.')
    return result

def checked_file(root, ref):
    path = (root/ref['file']).resolve()
    if not path.is_relative_to(root.resolve()) or not path.exists():
        raise RuntimeError('Archivo del manifiesto fuera de data-root o inexistente.')
    if checksum(path) != ref['sha256']:
        raise RuntimeError('Checksum distinto: un snapshot crudo cambió después de adquirirlo.')
    return path

def clean_prices(frame, c):
    rename = {'Date':'date','Open':'open','High':'high','Low':'low','Close':'close',
              'Adj Close':'adjusted_close','Volume':'volume','Dividends':'dividends',
              'Stock Splits':'stock_splits'}
    need = {'Date','Open','High','Low','Close','Adj Close','Volume'}
    if not need.issubset(frame.columns):
        raise RuntimeError('Faltan columnas de precios requeridas.')
    df = frame.rename(columns=rename).copy()
    df['date'] = pd.to_datetime(df['date'], errors='raise').dt.tz_localize(None).dt.normalize()
    df['ticker'] = c['ticker']
    for col in ['open','high','low','close','adjusted_close','volume']:
        df[col] = pd.to_numeric(df[col], errors='raise')
    if df[['open','high','low','close','adjusted_close','volume']].isna().any().any():
        raise RuntimeError('Precios faltantes: no se imputan ni eliminan automáticamente.')
    if (df[['open','high','low','close','adjusted_close']] <= 0).any().any() or (df.volume < 0).any():
        raise RuntimeError('Precio no positivo o volumen negativo.')
    conflicts = df.drop_duplicates().duplicated(['ticker','date']).any()
    if conflicts:
        raise RuntimeError('Precios distintos para una misma acción y fecha; revisar origen.')
    df = df.drop_duplicates(['ticker','date']).sort_values('date').reset_index(drop=True)
    calendar = mcal.get_calendar(c['calendar'])
    schedule = calendar.schedule(start_date=df.date.min(), end_date=pd.Timestamp(c['end'])+pd.Timedelta(days=7))
    valid = pd.DatetimeIndex(schedule.index).normalize()
    if not pd.DatetimeIndex(df.date).isin(valid).all():
        raise RuntimeError('Hay precios en fechas que no son sesiones del calendario elegido.')
    expected = valid[(valid >= df.date.min()) & (valid <= df.date.max())]
    if not expected.equals(pd.DatetimeIndex(df.date)):
        raise RuntimeError('Faltan sesiones intermedias: no calcular rendimientos saltando observaciones sin revisión.')
    study = schedule.loc[(schedule.index>=c['start'])&(schedule.index<c['end'])]
    if not pd.DatetimeIndex(study.index).isin(df.date).all():
        raise RuntimeError('Faltan precios para sesiones del periodo solicitado.')
    df['return_pct'] = 100*np.log(df.adjusted_close/df.adjusted_close.shift(1))
    return df, schedule

def clean_news(manifest, root, c):
    rows, rejected, raw_count = [],[],0
    for leaf in manifest['windows']:
        path = checked_file(root,leaf)
        feed = json.loads(path.read_text(encoding='utf-8'))['feed']
        left,right = pd.Timestamp(leaf['start_utc']),pd.Timestamp(leaf['end_exclusive_utc'])
        for article in feed:
            raw_count += 1
            entries = [e for e in article.get('ticker_sentiment',[]) if e.get('ticker')==c['ticker']]
            if len(entries) != 1:
                rejected.append({'source_file':path.name,'reason':'ticker_sentiment_missing_or_multiple'})
                continue
            entry = entries[0]
            try:
                timestamp = pd.to_datetime(article['time_published'],format='%Y%m%dT%H%M%S',utc=True)
                if not left <= timestamp < right:
                    continue # Evita doble conteo de fronteras inclusivas del proveedor.
                score,rel = float(entry['ticker_sentiment_score']),float(entry['relevance_score'])
                url = str(article['url']).strip()
                if not url or not np.isfinite(score) or not -1<=score<=1 or not np.isfinite(rel) or not 0<=rel<=1:
                    raise ValueError('invalid_fields')
            except (KeyError,TypeError,ValueError):
                rejected.append({'source_file':path.name,'reason':'invalid_date_url_sentiment_or_relevance'})
                continue
            key = f"{c['ticker']}|{url}|{timestamp.isoformat()}"
            rows.append({'article_id':hashlib.sha256(key.encode()).hexdigest(),
                         'ticker':c['ticker'],'published_utc':timestamp,'url':url,
                         'source':str(article.get('source','')),'sentiment':score,'relevance':rel,
                         'source_file':path.name})
    columns = ['article_id','ticker','published_utc','url','source','sentiment','relevance','source_file']
    df = pd.DataFrame(rows,columns=columns)
    if df.empty:
        raise RuntimeError('No hay noticias válidas para el ticker y periodo. Revisar cobertura antes de seguir.')
    conflicts = df.drop(columns='source_file').drop_duplicates().duplicated('article_id').any()
    if conflicts:
        raise RuntimeError('Sentimientos diferentes para una misma noticia; revisar revisiones del proveedor.')
    df = df.drop_duplicates('article_id').sort_values('published_utc').reset_index(drop=True)
    return df, {'raw_articles_examined':raw_count,'unique_articles':len(df),
                'rejected_articles':len(rejected),'rejections':rejected}

def align_news(prices, news, schedule, c):
    # Cada noticia se asigna al primer cierre >= su publicación. Incluye cierres tempranos.
    close = pd.DatetimeIndex(schedule.market_close)
    publication = pd.DatetimeIndex(news.published_utc)
    positions = np.searchsorted(close.asi8, publication.asi8, side='left')
    valid = positions < len(schedule)
    aligned = news.loc[valid].copy()
    aligned['asof_date'] = pd.DatetimeIndex(schedule.index)[positions[valid]].to_numpy()
    aligned['available_at_close_utc'] = close[positions[valid]].to_numpy()
    aligned['neg_intensity'] = (-aligned.sentiment).clip(lower=0)
    daily = []
    for day,g in aligned.groupby('asof_date',sort=True):
        # Convención explícita del piloto: piso de 0.01 para relevancia.
        weights = g.relevance.clip(lower=0.01)
        daily.append({'date':day,'news_count':len(g),
                      'sentiment_mean':np.average(g.sentiment,weights=weights),
                      'neg_intensity':np.average(g.neg_intensity,weights=weights),
                      'negative_share':float((g.sentiment<0).mean())})
    model = prices.loc[(prices.date>=c['start'])&(prices.date<c['end'])].copy()
    if model.empty or model.return_pct.isna().any():
        raise RuntimeError('No hay suficientes precios previos para calcular rendimientos del periodo.')
    aggregates = pd.DataFrame(daily,columns=['date','news_count','sentiment_mean','neg_intensity','negative_share'])
    model = model.merge(aggregates,on='date',how='left',validate='one_to_one').sort_values('date')
    model['has_news'] = model.news_count.notna()
    # Cero significa SIN noticias válidas recuperadas, no sentimiento positivo/neutro.
    for col in ['news_count','sentiment_mean','neg_intensity','negative_share']:
        model[col] = model[col].fillna(0)
    model['news_count'] = model.news_count.astype('int64')
    model['news_neg_lag1'] = model.neg_intensity.shift(1)
    model['target_return_next_pct'] = model.return_pct.shift(-1)
    model['target_date'] = model.date.shift(-1)
    model['target_variance_proxy_next'] = model.target_return_next_pct.pow(2)
    model['year'] = model.date.dt.year.astype('int64')
    # Nada de dropna global: conserva primer rezago y última etiqueta faltante, documentados.
    return aligned, model

def build(c, root):
    p_manifest = read_manifest(root,'prices_manifest.json',c)
    n_manifest = read_manifest(root,'news_manifest.json',c)
    if n_manifest.get('complete') is not True:
        raise RuntimeError('La adquisición de noticias está incompleta.')
    prices,schedule = clean_prices(pd.read_csv(checked_file(root,p_manifest)),c)
    news,quality = clean_news(n_manifest,root,c)
    aligned,model = align_news(prices,news,schedule,c)
    for layer in ['interim','processed','sample']:
        (root/layer).mkdir(parents=True,exist_ok=True)
    prices.to_parquet(root/'interim'/'prices.parquet',index=False)
    aligned.to_parquet(root/'interim'/'news.parquet',index=False)
    # CSV y Parquet comparten exactamente la misma tabla para el benchmark del compañero.
    model.to_parquet(root/'processed'/'model_dataset.parquet',index=False)
    model.to_csv(root/'processed'/'model_dataset.csv',index=False)
    # Particiones deterministas, reemplazo de solo archivos administrados de este proceso.
    for (_,year),group in model.groupby(['ticker','year']):
        dest = root/'processed'/'partitioned'/f"ticker={c['ticker']}"/f'year={year}'
        dest.mkdir(parents=True,exist_ok=True)
        group.drop(columns=['ticker','year']).to_parquet(dest/'part.parquet',index=False)
    prices.head(c['sample_rows']).to_csv(root/'sample'/'prices_sample.csv',index=False)
    # No redistribuir URLs/textos de artículos en muestras públicas; metadatos analíticos mínimos.
    aligned.drop(columns=['url','source_file']).head(c['sample_rows']).to_csv(root/'sample'/'news_sample.csv',index=False)
    model.head(c['sample_rows']).to_csv(root/'sample'/'model_sample.csv',index=False)
    quality.update({'config':fingerprint(c),'created_at_utc':utc_now(),
                    'sessions':len(model),'sessions_with_news':int(model.has_news.sum()),
                    'news_session_coverage':float(model.has_news.mean()),
                    'checksum_model_parquet':checksum(root/'processed'/'model_dataset.parquet'),
                    'status':'TRANSFORMED_NOT_TEAM_VALIDATED'})
    write_json(root/'processed'/'processing_summary.json',quality)
    print(f'Dataset preparado: {len(model)} sesiones; cobertura de noticias {model.has_news.mean():.1%}.')
    print('Pendiente: validación independiente, pruebas y benchmark del equipo.')
    return model

def main():
    args = parser('Construir dataset analítico de precios y sentimiento.').parse_args()
    build(config(args.config),Path(args.data_root).expanduser().resolve())

if __name__ == '__main__':
    fail_main(main)
