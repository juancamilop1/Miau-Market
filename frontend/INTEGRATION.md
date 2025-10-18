# Integración Frontend-Backend MiauMarket

## Cambios Realizados

### 1. Servicio API (`src/app/services/api.service.ts`)
- ✅ Creado servicio para comunicación con el backend
- ✅ Endpoints configurados:
  - `POST /api/usuarios/login/` - Inicio de sesión
  - `POST /api/usuarios/registro/` - Registro de usuario
- ✅ Interfaces TypeScript para request/response

### 2. AuthService Actualizado (`src/app/auth.service.ts`)
- ✅ Modificado para recibir datos reales del backend
- ✅ Interface `User` con id, name, email

### 3. Componente Login (`src/app/app/login/`)
- ✅ Integrado con API de login
- ✅ Formulario con ngModel para email y password
- ✅ Manejo de errores y estados de carga
- ✅ Mensajes de error visuales

### 4. Componente Register (`src/app/app/register/`)
- ✅ Integrado con API de registro
- ✅ Formulario completo con todos los campos del backend:
  - Nombre* (requerido)
  - Apellido* (requerido)
  - Email* (requerido)
  - Teléfono (opcional)
  - Dirección (opcional)
  - Ciudad (opcional)
  - Fecha de nacimiento (opcional)
  - Contraseña* (requerido)
  - Confirmar contraseña* (requerido)
- ✅ Auto-login después de registro exitoso
- ✅ Validación de contraseñas coincidentes
- ✅ Manejo de errores del backend

### 5. Configuración HTTP (`src/app/app.config.ts`)
- ✅ Agregado `provideHttpClient` para habilitar llamadas HTTP

## Requisitos del Backend

El backend debe estar corriendo en `http://localhost:8000` con los siguientes endpoints disponibles:

### Login
```
POST http://localhost:8000/api/usuarios/login/
Content-Type: application/json

{
  "Email": "usuario@example.com",
  "password": "password123"
}
```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "email": "usuario@example.com",
    "nombre": "Usuario"
  }
}
```

**Respuesta error (401):**
```json
{
  "error": "Email o contraseña incorrectos"
}
```

### Registro
```
POST http://localhost:8000/api/usuarios/registro/
Content-Type: application/json

{
  "Nombre": "Juan",
  "Apellido": "Pérez",
  "Email": "juan@example.com",
  "password": "password123",
  "password2": "password123",
  "Telefono": "+57 300 123 4567",
  "Address": "Calle 123 #45-67",
  "City": "Bogotá",
  "BirthDate": "1990-01-15"
}
```

**Respuesta exitosa (201):**
```json
{
  "id": 1,
  "Nombre": "Juan",
  "Apellido": "Pérez",
  "Email": "juan@example.com",
  "Telefono": "+57 300 123 4567",
  "Address": "Calle 123 #45-67",
  "City": "Bogotá",
  "BirthDate": "1990-01-15",
  "FechaRegistro": "2025-10-18T12:00:00Z"
}
```

## Cómo Probar

1. **Iniciar el backend:**
```bash
cd Backend
python manage.py runserver
```

2. **Iniciar el frontend:**
```bash
cd frontend
npm start
```

3. **Probar el flujo:**
   - Ir a http://localhost:4200/register
   - Registrar un nuevo usuario
   - Automáticamente te llevará a /shop después del registro
   - Cerrar sesión
   - Ir a http://localhost:4200/login
   - Iniciar sesión con las credenciales creadas

## Configuración CORS

Si el backend devuelve errores CORS, asegúrate de tener configurado en `Backend/core/settings.py`:

```python
INSTALLED_APPS = [
    ...
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",
]

# O durante desarrollo:
CORS_ALLOW_ALL_ORIGINS = True
```

## Manejo de Errores

El frontend maneja los siguientes escenarios:

- ✅ Campos vacíos
- ✅ Contraseñas que no coinciden
- ✅ Email ya registrado
- ✅ Credenciales incorrectas
- ✅ Errores de red
- ✅ Validación de contraseña del backend
- ✅ Estados de carga (botones deshabilitados)

## Próximos Pasos (Opcional)

- [ ] Implementar tokens JWT para autenticación persistente
- [ ] Guardar sesión en localStorage
- [ ] Agregar interceptor HTTP para tokens
- [ ] Implementar refresh tokens
- [ ] Agregar "Recordarme"
- [ ] Recuperación de contraseña
