"""Exploración reproducible. Se ejecuta solo sobre archivos existentes."""
import json
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.utils.common import parser, write_json, utc_now, fail_main

def explore(data_root, reports_root):
    data_root, reports_root = Path(data_root),Path(reports_root)
    files = {'prices':data_root/'interim/prices.parquet',
             'news':data_root/'interim/news.parquet',
             'model':data_root/'processed/model_dataset.parquet'}
    if any(not p.exists() for p in files.values()):
        raise RuntimeError('Faltan tablas: ejecuta adquisición y procesamiento primero.')
    figures,tables = reports_root/'figures',reports_root/'tables'
    figures.mkdir(parents=True,exist_ok=True)
    tables.mkdir(parents=True,exist_ok=True)
    summary = {'created_at_utc':utc_now(),'tables':{}}
    frames = {}
    keys = {'prices':['ticker','date'],'news':['article_id'],'model':['ticker','date']}
    for name,path in files.items():
        df = pd.read_parquet(path)
        frames[name] = df
        summary['tables'][name] = {'rows':len(df),'columns':len(df.columns),
            'types':{c:str(t) for c,t in df.dtypes.items()},
            'missing_count':{c:int(v) for c,v in df.isna().sum().items()},
            'duplicate_keys':int(df.duplicated(keys[name]).sum()),
            'memory_bytes':int(df.memory_usage(deep=True).sum())}
        df.describe(include='all').astype(str).to_csv(tables/f'{name}_descriptive.csv')
    model = frames['model']
    chart_specs = [('adjusted_close','Precio de cierre ajustado','USD ajustados'),
                   ('return_pct','Rendimiento logarítmico diario','%'),
                   ('news_count','Noticias válidas asignadas a cada cierre','Artículos')]
    for col,title,ylabel in chart_specs:
        fig,ax = plt.subplots(figsize=(10,4))
        ax.plot(model.date,model[col],linewidth=1,color='#2563eb')
        ax.set(title=title,xlabel='Fecha de sesión',ylabel=ylabel)
        ax.grid(alpha=.2)
        fig.tight_layout();fig.savefig(figures/f'{col}.png',dpi=160);plt.close(fig)
    fig,axes = plt.subplots(1,2,figsize=(10,4))
    axes[0].hist(model.return_pct.dropna(),bins=35,color='#2563eb')
    axes[0].set(title='Distribución de rendimientos',xlabel='%')
    axes[1].hist(frames['news'].sentiment,bins=35,color='#0d9488')
    axes[1].set(title='Sentimiento por noticia',xlabel='Puntuación')
    fig.tight_layout();fig.savefig(figures/'distributions.png',dpi=160);plt.close(fig)
    summary['news_coverage'] = float(model.has_news.mean())
    write_json(tables/'exploration_summary.json',summary)
    print(f'Exploración guardada en {reports_root.resolve()}')
    return summary

def main():
    p = parser('Exploración de calidad, dimensiones y distribuciones.')
    p.add_argument('--reports-root',default='reports')
    args = p.parse_args()
    explore(args.data_root,args.reports_root)

if __name__ == '__main__':
    fail_main(main)
