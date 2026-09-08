@echo off
setlocal
cd /d "%~dp0Backend"
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Ejecuta primero iniciar_miau_market.bat para crear el venv.
    pause
    exit /b 1
)
call venv\Scripts\activate.bat
python scripts\backup_bd.py
echo.
pause
