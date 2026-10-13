@echo off

setlocal EnableExtensions

chcp 65001 >nul 2>&1



title Miau Market

set "ROOT=%~dp0"

set "BACKEND=%ROOT%Backend"

set "FRONTEND=%ROOT%frontend"



echo ============================================================

echo   MIAU MARKET

echo   Un solo script: instala deps, BD SQLite y abre la app

echo   Ver README.md (usuarios de prueba)

echo ============================================================

echo.



cd /d "%BACKEND%"

if not exist "venv\Scripts\activate.bat" (

    echo Creando entorno virtual...

    python -m venv venv

    if errorlevel 1 goto error_python

)



if not exist ".env" (

    if exist ".env.example" copy /Y ".env.example" ".env" >nul

)



call venv\Scripts\activate.bat

pip install -r requirements.txt -q

if errorlevel 1 goto error_pip



echo Base de datos local SQLite...

python manage.py migrate --noinput

if errorlevel 1 goto error_bd

python manage.py seed_demo

if errorlevel 1 goto error_bd



cd /d "%FRONTEND%"

if not exist "node_modules\" call npm install

if errorlevel 1 goto error_npm



echo.

echo Backend:  http://localhost:8000

echo Frontend: http://localhost:4200

echo.



start "Miau Market - Backend" cmd /k "cd /d "%BACKEND%" && call venv\Scripts\activate.bat && python manage.py runserver"

timeout /t 3 /nobreak >nul

start "Miau Market - Frontend" cmd /k "cd /d "%FRONTEND%" && npx ng serve --open"



goto fin



:error_python

echo ERROR: Instala Python 3.11+

goto fin

:error_pip

echo ERROR: pip install fallo

goto fin

:error_bd

echo ERROR: migrate o seed_demo fallo

goto fin

:error_npm

echo ERROR: npm install fallo

goto fin



:fin

pause

endlocal

