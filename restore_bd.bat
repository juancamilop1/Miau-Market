@echo off
setlocal
cd /d "%~dp0Backend"

if "%~1"=="" (
    echo Uso: restore_bd.bat ruta\al\miau_market_backup.sql
    echo Ejemplo: restore_bd.bat ..\miau_market_backup_20260907_221414.sql
    pause
    exit /b 1
)

if not exist "venv\Scripts\activate.bat" (
    echo Creando entorno virtual...
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -q pymysql python-dotenv
python scripts\restore_bd.py "%~1"
echo.
pause
