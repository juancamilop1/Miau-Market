#!/usr/bin/env python
"""Verifica conexion a MySQL usando variables de entorno (.env)."""

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


def main() -> int:
    print('=' * 60)
    print('VERIFICACION DE BASE DE DATOS - Miau Market')
    print('=' * 60)
    print(f"Host:     {CONFIG['host']}:{CONFIG['port']}")
    print(f"Usuario:  {CONFIG['user']}")
    print(f"Base:     {CONFIG['database']}")
    print()

    try:
        conn = pymysql.connect(**CONFIG)
        with conn.cursor() as cursor:
            cursor.execute('SELECT DATABASE(), VERSION()')
            db_name, version = cursor.fetchone()
            print(f'Conexion OK')
            print(f'Base activa: {db_name}')
            print(f'MySQL: {version}')

            cursor.execute('SHOW TABLES')
            tables = [row[0] for row in cursor.fetchall()]
            print(f'Tablas ({len(tables)}): {", ".join(sorted(tables))}')
        conn.close()
        print('=' * 60)
        print('RESULTADO: OK')
        return 0
    except pymysql.Error as exc:
        print(f'ERROR: {exc}')
        print()
        print('Revisa Backend/.env (copia desde .env.example)')
        print('=' * 60)
        return 1


if __name__ == '__main__':
    sys.exit(main())
