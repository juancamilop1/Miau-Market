#!/usr/bin/env python
"""Restaura un backup .sql en miau_market (sin mysql en PATH)."""

import os
import sys
from pathlib import Path

import pymysql
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')

CONFIG = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'miau_market'),
    'charset': 'utf8mb4',
}


def _split_sql(text: str) -> list[str]:
    statements = []
    current = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith('--'):
            continue
        current.append(line)
        if stripped.endswith(';'):
            stmt = '\n'.join(current).strip()
            if stmt:
                statements.append(stmt)
            current = []
    if current:
        tail = '\n'.join(current).strip()
        if tail:
            statements.append(tail)
    return statements


def restaurar(archivo: Path) -> None:
    if not archivo.exists():
        raise FileNotFoundError(f'No existe: {archivo}')

    sql = archivo.read_text(encoding='utf-8')
    statements = _split_sql(sql)

    conn = pymysql.connect(
        host=CONFIG['host'],
        port=CONFIG['port'],
        user=CONFIG['user'],
        password=CONFIG['password'],
        charset=CONFIG['charset'],
    )

    try:
        with conn.cursor() as cur:
            for stmt in statements:
                cur.execute(stmt)
        conn.commit()
    finally:
        conn.close()


def main() -> int:
    if len(sys.argv) < 2:
        print('Uso: python scripts/restore_bd.py ruta\\al\\backup.sql')
        return 1

    archivo = Path(sys.argv[1]).resolve()
    print('=' * 60)
    print('RESTAURAR BASE DE DATOS - Miau Market')
    print('=' * 60)
    print(f'Archivo: {archivo}')
    print(f"Host:    {CONFIG['host']}:{CONFIG['port']}")
    print(f"Base:    {CONFIG['database']}")
    print()

    try:
        restaurar(archivo)
        print('Restauracion OK')
        print('=' * 60)
        return 0
    except Exception as exc:
        print(f'ERROR: {exc}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
