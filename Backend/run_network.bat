@echo off
echo ========================================
echo   Iniciando Backend en Red Local
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
    echo.
)

REM Obtener IP local
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /C:"IPv4"') do (
    set IP=%%a
    goto :found
)
:found
set IP=%IP:~1%

echo Tu IP local es: %IP%
echo.
echo El backend estara disponible en:
echo   - Local:   http://127.0.0.1:8000
echo   - Red:     http://%IP%:8000
echo   - Admin:   http://%IP%:8000/admin
echo.
echo Presiona Ctrl+C para detener el servidor
echo ========================================
echo.

REM Iniciar servidor Django en todas las interfaces (0.0.0.0)
python manage.py runserver 0.0.0.0:8000
