# 📱 Guía: Compartir MiauMarket en Red Local

## 🎯 ¿Qué es esto?

Esta guía te permite **compartir tu aplicación** con otros dispositivos (celulares, tablets, computadoras) en la **misma red WiFi** sin necesidad de desplegarla en internet.

---

## 📋 Requisitos Previos

✅ **Todos los dispositivos deben estar en la misma red WiFi**
✅ **Firewall de Windows debe permitir las conexiones** (ver más abajo)
✅ **Backend (Django) y Frontend (Angular) instalados**

---

## 🚀 Pasos para Compartir

### **Paso 1: Iniciar Backend (Django)**

1. Abre **PowerShell** o **CMD**
2. Navega a la carpeta del backend:
   ```powershell
   cd c:\Users\ang01\OneDrive\Documentos\GitHub\Miau-Market-\Backend
   ```
3. Ejecuta el script de red:
   ```powershell
   .\run_network.bat
   ```
4. **Verás algo así:**
   ```
   Tu IP local es: 192.168.1.100
   
   El backend estará disponible en:
     - Local:   http://localhost:8000
     - Red:     http://192.168.1.100:8000
   ```
5. **¡Anota tu IP!** (ejemplo: `192.168.1.100`)

---

### **Paso 2: Iniciar Frontend (Angular)**

1. Abre **OTRA** PowerShell o CMD (mantén el backend corriendo)
2. Navega a la carpeta del frontend:
   ```powershell
   cd c:\Users\ang01\OneDrive\Documentos\GitHub\Miau-Market-\frontend
   ```
3. Ejecuta el script de red:
   ```powershell
   .\run_network.bat
   ```
4. **Verás algo así:**
   ```
   Tu IP local es: 192.168.1.100
   
   El frontend estará disponible en:
     - Local:   http://localhost:4200
     - Red:     http://192.168.1.100:4200
   ```

---

### **Paso 3: Acceder desde Otros Dispositivos**

#### **Desde un Celular/Tablet:**

1. Conéctate a la **misma red WiFi**
2. Abre el navegador (Chrome, Safari, etc.)
3. Escribe en la barra de dirección:
   ```
   http://192.168.1.100:4200
   ```
   *(Usa la IP que viste en el Paso 1)*

#### **Desde Otra Computadora:**

1. Conéctate a la **misma red WiFi**
2. Abre el navegador
3. Escribe:
   ```
   http://192.168.1.100:4200
   ```

---

## 🔍 ¿Cómo Encontrar Mi IP Local?

Si necesitas verificar tu IP manualmente:

### **En Windows:**
```powershell
ipconfig
```
Busca la línea que dice `IPv4 Address` bajo tu adaptador WiFi.

### **En macOS/Linux:**
```bash
ifconfig | grep "inet "
```
O:
```bash
ip addr show
```

---

## 🛡️ Configurar Firewall de Windows

Si otros dispositivos **no pueden conectarse**, debes permitir las conexiones:

### **Opción 1: Firewall Gráfico**

1. Presiona `Win + R` → escribe `wf.msc` → Enter
2. Click derecho en **"Reglas de entrada"** → **"Nueva regla"**
3. Tipo de regla: **Puerto** → Siguiente
4. Protocolo: **TCP**, Puerto: **4200, 8000** → Siguiente
5. Acción: **Permitir la conexión** → Siguiente
6. Perfil: Marca **Privado** y **Público** → Siguiente
7. Nombre: **MiauMarket** → Finalizar

### **Opción 2: PowerShell (Más Rápido)**

Ejecuta en PowerShell **como Administrador**:

```powershell
New-NetFirewallRule -DisplayName "MiauMarket Frontend" -Direction Inbound -Protocol TCP -LocalPort 4200 -Action Allow
New-NetFirewallRule -DisplayName "MiauMarket Backend" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

---

## 🔧 Solución de Problemas

### **❌ "No puedo acceder desde mi celular"**

1. **Verifica que ambos scripts estén corriendo** (backend Y frontend)
2. **Verifica que estés en la misma WiFi** (no usar datos móviles)
3. **Desactiva temporalmente el firewall** para probar:
   - Panel de Control → Sistema y seguridad → Firewall de Windows → Desactivar
   - Prueba la conexión
   - **Reactiva el firewall después** y agrega las reglas (ver arriba)

### **❌ "Veo la página pero no carga datos"**

- El **backend** probablemente no está corriendo
- Verifica que `run_network.bat` del **Backend** esté ejecutándose
- Abre http://TU-IP:8000/admin desde el celular para verificar

### **❌ "Error de CORS"**

- Abre el navegador de tu celular
- Presiona F12 (DevTools)
- Si ves errores de CORS, verifica que `settings.py` tenga:
  ```python
  CORS_ALLOW_ALL_ORIGINS = True
  ```

### **❌ "La IP cambia cada vez"**

Tu router asigna IPs dinámicas. Puedes:
1. **Asignar IP estática** en configuración del router
2. O simplemente usar la IP que te muestra el script cada vez

---

## 📊 URLs Importantes

| Servicio | Local | Red Local |
|----------|-------|-----------|
| **Frontend** | http://localhost:4200 | http://TU-IP:4200 |
| **Backend API** | http://localhost:8000 | http://TU-IP:8000 |
| **Admin Panel** | http://localhost:8000/admin | http://TU-IP:8000/admin |

---

## ⚠️ Advertencias de Seguridad

🔴 **¡SOLO PARA DESARROLLO!**

- `ALLOWED_HOSTS = ['*']` permite **CUALQUIER** host
- `CORS_ALLOW_ALL_ORIGINS = True` permite **CUALQUIER** origen
- Estas configuraciones son **INSEGURAS** en producción

🔐 **Para producción:**

1. Especifica dominios exactos en `ALLOWED_HOSTS`
2. Lista orígenes específicos en `CORS_ALLOWED_ORIGINS`
3. Usa HTTPS con certificados SSL
4. Configura variables de entorno para secretos

---

## 📱 Pruebas Recomendadas

Una vez conectado desde tu celular, prueba:

✅ Registro de usuario  
✅ Login  
✅ Ver productos (catálogo)  
✅ Agregar al carrito  
✅ Checkout (compra)  
✅ Ver mis pedidos  
✅ Chatbot  
✅ Notificaciones  
✅ Panel de administrador  
✅ Dashboard  

---

## 🎉 ¡Listo!

Ahora puedes compartir tu aplicación con amigos, familia o testers sin necesidad de desplegarla en internet.

**Para detener los servidores:**
- Presiona `Ctrl + C` en ambas ventanas de PowerShell

---

## 📞 Ayuda Adicional

Si tienes problemas:

1. Verifica los logs en las ventanas de PowerShell
2. Revisa la consola del navegador (F12)
3. Verifica que MySQL esté corriendo (para el backend)
4. Asegúrate de que el puerto 4200 y 8000 no estén en uso por otros programas

---

**Autor:** GitHub Copilot  
**Versión:** 1.0  
**Fecha:** 2025
