# 📦 Instalación Completa de MiauMarket

Este documento contiene **todas las dependencias** necesarias para ejecutar MiauMarket desde cero.

---

## 🖥️ **BACKEND (Django + MySQL)**

### **Requisitos Previos:**
- ✅ **Python 3.10+** - [Descargar](https://www.python.org/downloads/)
- ✅ **MySQL 8.0+** o **XAMPP** - [Descargar MySQL](https://dev.mysql.com/downloads/) o [XAMPP](https://www.apachefriends.org/)
- ✅ **pip** (viene con Python)

### **Instalación Backend:**

#### **1. Crear Virtual Environment (Recomendado)**
```powershell
cd Backend
python -m venv venv
```

#### **2. Activar Virtual Environment**
```powershell
# Windows PowerShell
.\venv\Scripts\activate

# Windows CMD
venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate
```

#### **3. Instalar Dependencias**
```powershell
pip install -r requirements.txt
```

**Dependencias instaladas (desde requirements.txt):**
- `Django>=4.2.0,<5.0` - Framework web
- `djangorestframework>=3.14.0` - API REST
- `django-cors-headers>=4.3.0` - CORS para frontend
- `pymysql>=1.1.0` - Conector MySQL
- `google-generativeai>=0.7.0` - API de Gemini para chatbot
- `Pillow>=10.0.0` - Procesamiento de imágenes

#### **4. Configurar Base de Datos**

**Opción A: XAMPP**
1. Iniciar XAMPP Control Panel
2. Iniciar Apache y MySQL
3. Abrir phpMyAdmin: `http://localhost/phpmyadmin`
4. Crear base de datos: `miau_market`
5. Importar SQL: `Data Base/Tablas_V3.SQL`

**Opción B: MySQL Directo**
```powershell
mysql -u root -p
CREATE DATABASE miau_market;
USE miau_market;
SOURCE "Data Base/Tablas_V3.SQL";
```

#### **5. Configurar Django (settings.py)**

Verificar en `Backend/core/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'miau_market',
        'USER': 'root',
        'PASSWORD': '',  # Tu contraseña de MySQL
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

#### **6. Migraciones (si es necesario)**
```powershell
python manage.py migrate
```

#### **7. Crear Superusuario (Opcional)**
```powershell
python manage.py createsuperuser
```

#### **8. Ejecutar Backend**

**Desarrollo Local:**
```powershell
.\run_django.bat
# O manualmente:
python manage.py runserver
```

**En Red Local (para celular):**
```powershell
.\run_network.bat
# O manualmente:
python manage.py runserver 0.0.0.0:8000
```

✅ Backend corriendo en: `http://localhost:8000`

---

## 🌐 **FRONTEND (Angular 20)**

### **Requisitos Previos:**
- ✅ **Node.js 18+** - [Descargar](https://nodejs.org/)
- ✅ **npm** (viene con Node.js)
- ✅ **Angular CLI** (opcional, el proyecto usa `npx`)

### **Instalación Frontend:**

#### **1. Verificar Node y npm**
```powershell
node --version  # Debe ser v18+
npm --version
```

#### **2. Instalar Dependencias**
```powershell
cd frontend
npm install
```

**Dependencias instaladas (desde package.json):**

**Producción:**
- `@angular/animations: ^20.3.6`
- `@angular/common: ^20.3.6`
- `@angular/compiler: ^20.3.6`
- `@angular/core: ^20.3.6`
- `@angular/forms: ^20.3.6`
- `@angular/platform-browser: ^20.3.6`
- `@angular/platform-browser-dynamic: ^20.3.6`
- `@angular/platform-server: ^20.3.6`
- `@angular/router: ^20.3.6`
- `@angular/ssr: ^20.3.6`
- `chart.js: ^5.0.2` - Gráficos del dashboard
- `express: ^4.18.2` - Servidor SSR
- `rxjs: ~7.8.0` - Programación reactiva
- `tslib: ^2.3.0`
- `zone.js: ~0.15.0`

**Desarrollo:**
- `@angular-devkit/build-angular: ^20.3.5`
- `@angular/cli: ^20.3.5`
- `@angular/compiler-cli: ^20.3.6`
- `@types/express: ^4.17.17`
- `@types/node: ^18.18.0`
- `typescript: ~5.7.2`

#### **3. Ejecutar Frontend**

**Desarrollo Local:**
```powershell
.\run_angular.bat
# O manualmente:
npx ng serve
```

**En Red Local (para celular):**
```powershell
.\run_network.bat
# O manualmente:
npx ng serve --host 0.0.0.0
```

✅ Frontend corriendo en: `http://localhost:4200`

---

## 🔥 **FIREWALL (Para Red Local)**

Si quieres acceder desde tu celular, ejecuta en PowerShell **como Administrador**:

```powershell
New-NetFirewallRule -DisplayName "MiauMarket Frontend" -Direction Inbound -Protocol TCP -LocalPort 4200 -Action Allow
New-NetFirewallRule -DisplayName "MiauMarket Backend" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

---

## 📱 **ACCESO DESDE CELULAR**

1. Asegúrate de que PC y celular estén en la **misma WiFi**
2. Ejecuta los scripts de red:
   ```powershell
   # Backend
   cd Backend
   .\run_network.bat
   
   # Frontend (en otra terminal)
   cd frontend
   .\run_network.bat
   ```
3. Abre en tu celular: `http://192.168.X.X:4200` (usa la IP que te muestre el script)

---

## 🛠️ **EXTENSIONES RECOMENDADAS PARA VS CODE**

### **Generales:**
- `ms-python.python` - Python
- `ms-python.vscode-pylance` - Python IntelliSense
- `angular.ng-template` - Angular Language Service
- `esbenp.prettier-vscode` - Formatear código
- `dbaeumer.vscode-eslint` - Linter JavaScript

### **Frontend (Angular):**
- `johnpapa.angular2` - Angular Snippets
- `cyrilletuzi.angular-schematics` - Angular Schematics
- `mikael.angular-beastcode` - Angular Snippets

### **Backend (Django):**
- `batisteo.vscode-django` - Django Templates
- `wholroyd.jinja` - Jinja Templates
- `cstrap.python-snippets` - Python Snippets

### **Base de Datos:**
- `mysql.mysql-shell` - MySQL Shell
- `weijan.database-client` - Database Client

### **Desarrollo Web:**
- `bradlc.vscode-tailwindcss` - Tailwind CSS IntelliSense (si lo usas)
- `formulahendry.auto-rename-tag` - Auto Rename Tag
- `naumovs.color-highlight` - Color Highlight

---

## 📋 **RESUMEN DE COMANDOS**

### **Primera Instalación:**
```powershell
# Backend
cd Backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser

# Frontend
cd frontend
npm install

# Firewall (como Admin)
New-NetFirewallRule -DisplayName "MiauMarket Frontend" -Direction Inbound -Protocol TCP -LocalPort 4200 -Action Allow
New-NetFirewallRule -DisplayName "MiauMarket Backend" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

### **Ejecución Diaria:**
```powershell
# Terminal 1 - Backend
cd Backend
.\run_django.bat

# Terminal 2 - Frontend
cd frontend
.\run_angular.bat
```

### **Ejecución en Red (Celular):**
```powershell
# Terminal 1 - Backend
cd Backend
.\run_network.bat

# Terminal 2 - Frontend
cd frontend
.\run_network.bat
```

---

## 🎯 **VERIFICAR INSTALACIÓN**

### **Backend:**
1. Abre: `http://localhost:8000/admin`
2. Deberías ver el panel de administración de Django
3. Login con tu superusuario

### **Frontend:**
1. Abre: `http://localhost:4200`
2. Deberías ver la página de MiauMarket
3. Intenta registrarte/iniciar sesión

### **API:**
1. Abre: `http://localhost:8000/api/usuarios/productos/`
2. Deberías ver JSON con los productos

---

## 🐛 **SOLUCIÓN DE PROBLEMAS**

### **Error: "No module named 'django'"**
```powershell
# Asegúrate de activar el venv
cd Backend
.\venv\Scripts\activate
pip install -r requirements.txt
```

### **Error: "ng no se reconoce como comando"**
```powershell
# Usa npx en lugar de ng
npx ng serve
# O instala Angular CLI globalmente
npm install -g @angular/cli
```

### **Error: "Access denied for user 'root'@'localhost'"**
- Verifica usuario y contraseña en `Backend/core/settings.py`
- Asegúrate de que MySQL esté corriendo

### **Error: Celular no se conecta**
- Verifica que ambos estén en la misma WiFi
- Ejecuta las reglas de firewall
- Usa los scripts `run_network.bat`
- Verifica la IP con `ipconfig`

---

## 📞 **SOPORTE**

Si tienes problemas:
1. Verifica los logs en las terminales
2. Revisa la consola del navegador (F12)
3. Verifica que MySQL esté corriendo
4. Asegúrate de que los puertos 4200 y 8000 no estén en uso

---

**Autor:** GitHub Copilot  
**Proyecto:** MiauMarket  
**Versión:** 1.0  
**Fecha:** Noviembre 2025
