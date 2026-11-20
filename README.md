# Miau Market

Tienda web inteligente de productos para mascotas pensada para usuarios con distintos niveles de experiencia digital (incluidos adultos mayores). Integra catálogo administrable por categorías, detalle de producto, favoritos, perfiles de mascotas, carrito, pedidos con stock atómico y cancelación, reseñas, notificaciones, panel de administración con dashboard y el asistente conversacional **MiauBot** (motor local en BD + soporte opcional de Gemini).

**Repositorio:** https://github.com/juancamilop1/Miau-Market  
**Frontend en producción:** https://miau-market.juancamilobarragan2.workers.dev  
**API Health:** https://miau-market-api.onrender.com/api/health/

## Integrantes

- Juan Camilo Barragán Pottes
- Angely Liced Herrera Roldán

---

## Tecnologías

| Área | Tecnología |
|------|------------|
| Frontend | Angular 20, TypeScript 5.9, Chart.js (desplegado en Cloudflare Workers) |
| Backend | Python 3.12+, Django 5.0, Django REST Framework (token + throttling, desplegado en Render) |
| Base de datos | TiDB Cloud / MySQL 8 con TLS en producción; MySQL 8 local (o SQLite con `DB_ENGINE=sqlite`) |
| IA (MiauBot) | Motor local en base de datos + Google Gemini API opcional (`gemini-2.0-flash`) |
| Control de versiones | Git + GitHub |

Justificación detallada: [docs/stack_tecnologico.md](docs/stack_tecnologico.md).

---

## Arquitectura

Cliente-servidor en tres capas con frontend y backend desacoplados:

```text
Navegador ──HTTPS──> Angular SPA (Cloudflare Workers / :4200)
                        │ REST/JSON + Token
                        ▼
                     Django REST API (Render / :8000) ──ORM/PyMySQL TLS──> TiDB Cloud / MySQL
                        └──HTTPS (opcional)──> Google Gemini API
```

Las reglas de negocio (precios, stock con `select_for_update`, caducidad, permisos y catálogos) se validan en el servidor. Detalle en [docs/arquitectura.md](docs/arquitectura.md) y [docs/modelo_c4.md](docs/modelo_c4.md).

---

## Instalación y ejecución local

**Requisitos:** Python 3.12+, Node.js 20+ y MySQL 8 (o `DB_ENGINE=sqlite` en `Backend/.env`).

### Opción rápida (Windows)

1. Clonar el repositorio: `git clone https://github.com/juancamilop1/Miau-Market.git`
2. Configurar `Backend/.env` a partir de `Backend/.env.example` (credenciales MySQL o `DB_ENGINE=sqlite`).
3. Doble clic en **`iniciar_miau_market.bat`**.
4. Abrir **http://localhost:4200**.

### Opción manual

```bash
# Backend
cd Backend
python -m venv venv
venv\Scripts\activate            # Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env           # Linux/macOS: cp .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 8000

# Frontend (otra terminal)
cd frontend
npm install
npx ng serve --port 4200
```

### Pruebas automatizadas (Backend)

```bash
cd Backend
python manage.py test usuarios
```

---

## Usuarios de prueba (seed local)

| Rol | Usuario / correo | Contraseña |
|-----|------------------|------------|
| **Administrador** | `adminmarket` o `admin@miau.market` | `miauadmin2026` |
| **Cliente** | `clientedemo` o `cliente@miau.market` | `cliente2026` |

---

## Variables de entorno

Se definen en `Backend/.env` (plantilla: `Backend/.env.example`). **No commitear `Backend/.env` ni secretos reales.**

| Variable | Descripción | Ejemplo desarrollo |
|----------|-------------|--------------------|
| `DJANGO_SECRET_KEY` | Clave criptográfica de Django (obligatoria y única en prod) | `dev-cambiar-en-produccion` |
| `DJANGO_DEBUG` | Modo depuración (`False` en producción) | `True` |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos separados por coma | `localhost,127.0.0.1` |
| `DB_ENGINE` | `mysql` (por defecto) o `sqlite` | `mysql` |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Credenciales MySQL / TiDB Cloud | `127.0.0.1`, `3306`, `miau_market` |
| `DB_SSL`, `DB_SSL_CA` | TLS para MySQL remoto / TiDB Cloud | `False` en local; `True` en Render |
| `CORS_ALLOWED_ORIGINS` | Orígenes frontend autorizados | `http://localhost:4200` |
| `CSRF_TRUSTED_ORIGINS` | Orígenes confiables HTTPS en producción | `https://...` |
| `GEMINI_API_KEY` | Clave opcional de Google Gemini (vacía = motor local) | *(vacía)* |
| `GEMINI_MODEL` | Modelo de Gemini | `gemini-2.0-flash` |

---

## Despliegue

| Entorno | Estado | Detalle |
|---------|--------|---------|
| **Producción (nube)** | **Activo** | Cloudflare Workers (`workers.dev`) + Render Web Service (`onrender.com`) + TiDB Cloud Starter (MySQL TLS). |
| **Local (desarrollo y demo)** | **Activo** | `iniciar_miau_market.bat` (Django `:8000` + Angular `:4200`). |

---

## Documentación técnica

| Documento | Contenido |
|-----------|-----------|
| [docs/requerimientos.md](docs/requerimientos.md) | Necesidad, objetivo, actores, RF/RNF, reglas, restricciones, casos de prueba y trazabilidad |
| [docs/stack_tecnologico.md](docs/stack_tecnologico.md) | Tecnologías, despliegue y justificación |
| [docs/arquitectura.md](docs/arquitectura.md) | Arquitectura en capas, endpoints, seguridad y despliegue |
| [docs/modelo_entidad_relacion.md](docs/modelo_entidad_relacion.md) · [docs/MER.png](docs/MER.png) | Modelo entidad-relación y relaciones FK |
| [Data Base/ESQUEMA_BD.md](Data%20Base/ESQUEMA_BD.md) | Detalle de tablas, migraciones `0001`–`0018` y convenciones SQL |
| [docs/BPMN.png](docs/BPMN.png) | Proceso de compra (BPMN) |
| [docs/modelo_c4.md](docs/modelo_c4.md) | Modelo C4 (contexto, contenedores, componentes, código UML) |
