#!/usr/bin/env python
"""Exporta miau_market a .sql sin necesitar mysqldump en PATH."""

import os
import sys
from datetime import datetime
from pathlib import Path

import pymysql
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
load_dotenv(ROOT / '.env')

CONFIG = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'miau_market'),
    'charset': 'utf8mb4',
}


def _escape(value) -> str:
    if value is None:
        return 'NULL'
    if isinstance(value, bool):
        return '1' if value else '0'
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (bytes, bytearray)):
        value = value.decode('utf-8', errors='replace')
    text = str(value)
    text = text.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n').replace('\r', '\\r')
    return f"'{text}'"


def exportar(ruta_salida: Path) -> None:
    conn = pymysql.connect(**CONFIG)
    lineas: list[str] = []

    lineas.append('-- Backup Miau Market')
    lineas.append(f'-- Fecha: {datetime.now().isoformat(timespec="seconds")}')
    lineas.append(f'-- Base: {CONFIG["database"]}')
    lineas.append('')
    lineas.append(f'CREATE DATABASE IF NOT EXISTS `{CONFIG["database"]}` '
                  f'CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;')
    lineas.append(f'USE `{CONFIG["database"]}`;')
    lineas.append('SET FOREIGN_KEY_CHECKS=0;')
    lineas.append('')

    try:
        with conn.cursor() as cur:
            cur.execute('SHOW TABLES')
            tablas = [row[0] for row in cur.fetchall()]

            for tabla in tablas:
                cur.execute(f'SHOW CREATE TABLE `{tabla}`')
                create_sql = cur.fetchone()[1]
                lineas.append(f'DROP TABLE IF EXISTS `{tabla}`;')
                lineas.append(f'{create_sql};')
                lineas.append('')

                cur.execute(f'SELECT * FROM `{tabla}`')
                columnas = [desc[0] for desc in cur.description]
                filas = cur.fetchall()
                if not filas:
                    lineas.append(f'-- Tabla `{tabla}` vacia')
                    lineas.append('')
                    continue

                cols = ', '.join(f'`{c}`' for c in columnas)
                for fila in filas:
                    vals = ', '.join(_escape(v) for v in fila)
                    lineas.append(f'INSERT INTO `{tabla}` ({cols}) VALUES ({vals});')
                lineas.append('')

        lineas.append('SET FOREIGN_KEY_CHECKS=1;')
        lineas.append('')

        ruta_salida.write_text('\n'.join(lineas), encoding='utf-8')
        size_kb = ruta_salida.stat().st_size / 1024
        print(f'Backup OK: {ruta_salida}')
        print(f'Tablas: {len(tablas)} | Tamano: {size_kb:.1f} KB')
    finally:
        conn.close()


def main() -> int:
    nombre = f'miau_market_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sql'
    destino = PROJECT / nombre
    if len(sys.argv) > 1:
        destino = Path(sys.argv[1]).resolve()

    print('=' * 60)
    print('BACKUP BASE DE DATOS - Miau Market')
    print('=' * 60)
    print(f"Host: {CONFIG['host']}:{CONFIG['port']}")
    print(f"Base: {CONFIG['database']}")
    print()

    try:
        exportar(destino)
        print('=' * 60)
        return 0
    except pymysql.Error as exc:
        print(f'ERROR MySQL: {exc}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
