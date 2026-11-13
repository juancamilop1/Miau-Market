@echo off
setlocal EnableExtensions
chcp 65001 >nul 2>&1

title Miau Market - Iniciador
set "ROOT=%~dp0"
set "BACKEND=%ROOT%Backend"
set "FRONTEND=%ROOT%frontend"

REM Node.js recien instalado no siempre esta en el PATH de esta ventana
if exist "%ProgramFiles%\nodejs\npm.cmd" set "PATH=%ProgramFiles%\nodejs;%PATH%"
if exist "%ProgramFiles(x86)%\nodejs\npm.cmd" set "PATH=%ProgramFiles(x86)%\nodejs;%PATH%"

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
    ) else (
        echo ERROR: Falta Backend\.env y Backend\.env.example
        goto fin
    )
) else (
    echo [2/5] Archivo .env encontrado
)

set "DB_IS_SQLITE=0"
findstr /i /b /x /c:"DB_ENGINE=sqlite" "%BACKEND%\.env" >nul
if not errorlevel 1 set "DB_IS_SQLITE=1"
if "%DB_IS_SQLITE%"=="1" (
    echo       DB_ENGINE=sqlite ^(sin MySQL^)
    goto env_ok
)

findstr /i /b /c:"DB_PASSWORD=tu_" /c:"DB_PASSWORD=CAMBIAR" /c:"DB_PASSWORD=changeme" /c:"DB_PASSWORD=your_" "%BACKEND%\.env" >nul
if not errorlevel 1 goto error_env_password
findstr /b /x /c:"DB_PASSWORD=" "%BACKEND%\.env" >nul
if not errorlevel 1 goto error_env_password
echo       DB_PASSWORD configurado
:env_ok

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
if "%DB_IS_SQLITE%"=="1" (
    python manage.py seed_demo
    if errorlevel 1 goto error_migrate
)

REM --- Frontend: dependencias ---
echo [5/5] Verificando dependencias frontend...
where npm >nul 2>&1
if errorlevel 1 goto error_npm_missing
cd /d "%FRONTEND%"

REM Si node_modules esta incompleto/corrupto (avisos TAR_ENTRY_ERROR), reinstalar
set "NEED_NPM_INSTALL=0"
if not exist "node_modules\" set "NEED_NPM_INSTALL=1"
if not exist "node_modules\@angular\cli\package.json" set "NEED_NPM_INSTALL=1"
if not exist "node_modules\typescript\package.json" set "NEED_NPM_INSTALL=1"

if "%NEED_NPM_INSTALL%"=="1" (
    echo       Instalando npm packages...
    echo       Cierra otras ventanas de ng serve / npm antes si ves TAR_ENTRY_ERROR.
    if exist "node_modules\" (
        echo       Limpiando node_modules incompleto...
        rmdir /s /q "node_modules" 2>nul
    )
    call npm install --no-fund --no-audit
    if errorlevel 1 goto error_npm
    if not exist "node_modules\@angular\cli\package.json" goto error_npm
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

:error_env_password
echo.
echo ERROR: Backend\.env todavia tiene la contrasena de ejemplo.
echo Edita DB_PASSWORD con la clave de root de MySQL local, guarda y reejecuta este script.
echo.
start "" notepad "%BACKEND%\.env"
goto fin

:error_migrate
echo.
echo ERROR: migrate fallo. Revisa Backend\.env (DB_PASSWORD) y que el servicio MySQL este Running.
goto fin

:error_npm_missing
echo.
echo ERROR: No se encontro npm. Instala Node.js LTS (https://nodejs.org) y vuelve a ejecutar.
goto fin

:error_npm
echo.
echo ERROR: npm install fallo en frontend.
echo Cierra ventanas "ng serve" / Node del proyecto, borra frontend\node_modules
echo y vuelve a ejecutar este script. Antivirus a veces bloquea la extraccion tar.
goto fin

:fin
echo.
pause
endlocal
