@echo off
echo ========================================
echo   Iniciando Frontend en Red Local
echo ========================================
echo.

REM Obtener IP local
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /C:"IPv4"') do (
    set IP=%%a
    goto :found
)
:found
set IP=%IP:~1%

echo Tu IP local es: %IP%
echo.
echo El frontend estara disponible en:
echo   - Local:   http://localhost:4200
echo   - Red:     http://%IP%:4200
echo.
echo IMPORTANTE: Asegura que el backend este corriendo en http://%IP%:8000
echo.
echo Presiona Ctrl+C para detener el servidor
echo ========================================
echo.

REM Iniciar servidor Angular en todas las interfaces
npx ng serve --host 0.0.0.0
