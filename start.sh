#!/bin/bash
# Script de inicio para Railpack: Django + Angular

# Iniciar backend Django
cd Backend
python manage.py migrate
python manage.py runserver 0.0.0.0:8000 &

# Iniciar frontend Angular
cd ../frontend
npm install
npm run build
npx http-server ./dist -p 4200
