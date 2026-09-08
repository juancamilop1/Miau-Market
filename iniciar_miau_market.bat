@echo off
setlocal EnableExtensions
chcp 65001 >nul 2>&1

title Miau Market - Iniciador
set "ROOT=%~dp0"
set "BACKEND=%ROOT%Backend"
set "FRONTEND=%ROOT%frontend"

echo ============================================================
echo   MIAU MARKET - Inicio del proyecto
echo ============================================================
echo.

REM --- Backend: entorno virtual ---
if not exist "%BACKEND%\venv\Scripts\activate.bat" (
    echo [1/5] Creando entorno virtual Python...
    cd /d "%BACKEND%"
    python -m venv venv
    if errorlevel 1 goto error_venv
) else (
    echo [1/5] Entorno virtual OK
)

REM --- Backend: .env ---
if not exist "%BACKEND%\.env" (
    if exist "%BACKEND%\.env.example" (
        echo [2/5] Copiando .env.example a .env ...
        copy /Y "%BACKEND%\.env.example" "%BACKEND%\.env" >nul
        echo       Edita Backend\.env con tu DB_PASSWORD antes de continuar.
    ) else (
        echo ERROR: Falta Backend\.env y Backend\.env.example
        goto fin
    )
) else (
    echo [2/5] Archivo .env OK
)

REM --- Backend: dependencias y migraciones ---
echo [3/5] Instalando dependencias backend...
cd /d "%BACKEND%"
call "%BACKEND%\venv\Scripts\activate.bat"
if errorlevel 1 goto error_venv

pip install -r requirements.txt -q
if errorlevel 1 goto error_pip

echo [4/5] Aplicando migraciones...
python manage.py migrate --noinput
if errorlevel 1 goto error_migrate

REM --- Frontend: dependencias ---
echo [5/5] Verificando dependencias frontend...
cd /d "%FRONTEND%"
if not exist "node_modules\" (
    echo       Instalando npm packages - primera vez...
    call npm install
    if errorlevel 1 goto error_npm
) else (
    echo       node_modules OK
)

echo.
echo ============================================================
echo   Iniciando servidores...
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:4200
echo ============================================================
echo.

start "Miau Market - Backend" cmd /k "cd /d "%BACKEND%" && call venv\Scripts\activate.bat && python manage.py runserver"
timeout /t 3 /nobreak >nul
start "Miau Market - Frontend" cmd /k "cd /d "%FRONTEND%" && npx ng serve --open"

echo Ventanas abiertas. Cierra cada ventana para detener el servicio.
goto fin

:error_venv
echo.
echo ERROR: No se pudo usar Python/venv. Instala Python 3.11+ y vuelve a intentar.
goto fin

:error_pip
echo.
echo ERROR: pip install fallo en Backend.
goto fin

:error_migrate
echo.
echo ERROR: migrate fallo. Revisa Backend\.env y que MySQL este encendido.
goto fin

:error_npm
echo.
echo ERROR: npm install fallo en frontend.
goto fin

:fin
echo.
pause
endlocal
