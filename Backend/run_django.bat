@echo off
echo ========================================
echo   Iniciando Backend Django (Local)
echo ========================================
echo.

REM Intentar activar venv si existe
if exist "venv\Scripts\activate.bat" (
    echo Activando virtual environment...
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo Activando virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo ADVERTENCIA: No se encontro virtual environment
    echo Asegurate de tener Django instalado globalmente
    echo.
)

echo Servidor corriendo en: http://localhost:8000
echo Presiona Ctrl+C para detener
echo ========================================
echo.

python manage.py runserver
