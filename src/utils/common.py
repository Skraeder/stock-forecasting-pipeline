"""Configuración, escritura atómica y metadatos compartidos."""
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

def parser(description):
    p = argparse.ArgumentParser(description=description)
    p.add_argument('--config', default=str(PROJECT_ROOT/'config/config.example.json'))
    p.add_argument('--data-root', default=str(PROJECT_ROOT/'data'))
    return p

def config(path):
    c = json.loads(Path(path).read_text(encoding='utf-8'))
    if not re.fullmatch(r'[A-Z][A-Z0-9.-]{0,14}', c['ticker']):
        raise ValueError('Ticker inválido.')
    a = datetime.strptime(c['start'], '%Y-%m-%d')
    b = datetime.strptime(c['end'], '%Y-%m-%d')
    if a >= b:
        raise ValueError('start debe ser anterior a end.')
    if not 1 <= int(c['news_limit']) <= 1000:
        raise ValueError('news_limit debe estar entre 1 y 1000.')
    if int(c['max_news_requests']) < 1 or float(c['request_pause_seconds']) < 0:
        raise ValueError('Presupuesto de solicitudes o pausa inválidos.')
    if int(c['sample_rows']) < 1 or int(c['warmup_days']) < 1:
        raise ValueError('Muestra y warmup deben ser positivos.')
    return c

def fingerprint(c):
    # Los parámetros operativos no cambian la identidad del conjunto.
    return {k:c[k] for k in ['ticker','start','end','warmup_days','calendar']}

def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
    temp.replace(path)

def checksum(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def event(root, **fields):
    path = Path(root)/'raw'/'ingestion_log.jsonl'
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as f:
        f.write(json.dumps({'at_utc':utc_now(), **fields}, ensure_ascii=False)+'\n')

def fail_main(fn):
    try:
        fn()
    except (ValueError, RuntimeError, OSError) as exc:
        # Mensajes internos controlados; nunca imprimir la URL autenticada.
        raise SystemExit(str(exc)) from None
