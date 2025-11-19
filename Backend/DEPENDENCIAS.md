# Dependencias de Backend (Django)

## Instalar Python
- Python 3.10+ (https://www.python.org/downloads/)
- pip (viene con Python)

## Instalar MySQL
- MySQL 8.0+ (https://dev.mysql.com/downloads/)
- O XAMPP (https://www.apachefriends.org/)

## Crear Virtual Environment
```bash
python -m venv venv
```

## Activar Virtual Environment
```bash
# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

## Instalar dependencias
```bash
pip install -r requirements.txt
```

## Dependencias (desde requirements.txt):
- Django>=4.2.0,<5.0 (framework web)
- djangorestframework>=3.14.0 (API REST)
- django-cors-headers>=4.3.0 (CORS frontend)
- pymysql>=1.1.0 (conector MySQL)
- google-generativeai>=0.7.0 (chatbot Gemini)
- Pillow>=10.0.0 (imágenes)

## Configurar Base de Datos:
1. Crear database: `miau_market`
2. Importar: `Data Base/Tablas_V3.SQL`

## Ejecutar:
```bash
python manage.py runserver
```

## Ejecutar en red (celular):
```bash
python manage.py runserver 0.0.0.0:8000
```
