# Miau Market

Tienda web de productos para mascotas pensada para personas con poca experiencia digital (incluidos adultos mayores). Integra catálogo por categorías, carrito, pedidos con **pago contra entrega**, reseñas, notificaciones, panel de administración con dashboard y el asistente conversacional **MiauBot**, que recuerda a la mascota del usuario y recomienda productos del catálogo.

**Repositorio:** https://github.com/juancamilop1/Miau-Market

## Integrantes

- Juan Camilo Barragán Pottes
- Angely Liced Herrera Roldán

---

## Tecnologías

| Área | Tecnología |
|------|------------|
| Frontend | Angular 20, TypeScript 5.9, Chart.js |
| Backend | Python 3.11+, Django 4.2 LTS, Django REST Framework (token) |
| Base de datos | SQLite (`Backend/db.sqlite3`) en desarrollo y demostración; MySQL 8 proyectado para producción |
| IA (opcional) | Google Gemini API |
| Control de versiones | Git + GitHub |

Justificación detallada: [docs/stack_tecnologico.md](docs/stack_tecnologico.md).

---

## Arquitectura

Cliente-servidor en tres capas con frontend y backend desacoplados:

```
Navegador ──HTTPS──> Angular (:4200) ──REST/JSON + Token──> Django API (:8000) ──ORM──> SQLite / MySQL
                                                                   └──HTTPS──> Google Gemini (opcional)
```

Las reglas de negocio (precios, stock, caducidad, permisos) se validan en el servidor. Detalle en [docs/arquitectura.md](docs/arquitectura.md) y [docs/modelo_c4.md](docs/modelo_c4.md).

---

## Instalación y ejecución

**Requisitos:** Python 3.11+ y Node.js 20+.

### Opción rápida (Windows)

1. Clonar el repositorio: `git clone https://github.com/juancamilop1/Miau-Market.git`
2. Doble clic en **`iniciar_miau_market.bat`**.
3. Abrir **http://localhost:4200**.

La primera vez crea el entorno virtual, copia `Backend/.env.example` a `Backend/.env` e instala dependencias. En cada arranque aplica migraciones pendientes, asegura los datos de demostración (`seed_demo`) y abre backend y frontend en dos ventanas.

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

### Base de datos

`Backend/db.sqlite3` va incluido en el repositorio con datos de demostración. Si se borra, `migrate` + `seed_demo` lo recrean. El esquema está en [docs/modelo_entidad_relacion.md](docs/modelo_entidad_relacion.md).

---

## Usuarios de prueba

| Rol | Usuario / correo | Contraseña |
|-----|------------------|------------|
| **Administrador** | `adminmarket` o `admin@miau.market` | `miauadmin2026` |
| **Cliente** | `clientedemo` o `cliente@miau.market` | `cliente2026` |

Las contraseñas no distinguen mayúsculas. El administrador ve además el menú **Administración** y el dashboard.

---

## Variables de entorno

Se definen en `Backend/.env` (plantilla: `Backend/.env.example`). **No commitear `Backend/.env` con valores reales.**

| Variable | Descripción | Valor de desarrollo |
|----------|-------------|---------------------|
| `DJANGO_SECRET_KEY` | Clave criptográfica de Django. Obligatorio cambiarla en producción. | `dev-cambiar-en-produccion` |
| `DJANGO_DEBUG` | Modo depuración. `False` en producción. | `True` |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos, separados por coma. | `localhost,127.0.0.1` |
| `SQLITE_PATH` | Ruta del archivo SQLite, relativa a `Backend/`. | `db.sqlite3` |
| `CORS_ALLOWED_ORIGINS` | Orígenes del frontend autorizados a llamar la API. | `http://localhost:4200,http://127.0.0.1:4200` |
| `CORS_ALLOW_ALL_ORIGINS` | Permite cualquier origen (solo desarrollo). | `True` |
| `GEMINI_API_KEY` | Clave de Google Gemini para MiauBot. Vacía = motor local. | *(vacía)* |
| `GEMINI_MODEL` | Modelo de Gemini. | `gemini-2.0-flash` |

---

## Despliegue

| Entorno | Estado |
|---------|--------|
| Local (desarrollo y demostración) | **Activo** — `iniciar_miau_market.bat` |
| Producción pública | **No desplegado.** Propuesta: Angular compilado como estático, Django con Gunicorn tras proxy HTTPS, MySQL 8, `DJANGO_DEBUG=False`. |

---

## Documentación

| Documento | Contenido |
|-----------|-----------|
| [docs/requerimientos.md](docs/requerimientos.md) | Necesidad, objetivo, actores, RF/RNF, reglas, restricciones y trazabilidad |
| [docs/stack_tecnologico.md](docs/stack_tecnologico.md) | Tecnologías y justificación |
| [docs/arquitectura.md](docs/arquitectura.md) | Arquitectura, comunicación y justificación |
| [docs/modelo_entidad_relacion.md](docs/modelo_entidad_relacion.md) · [docs/MER.png](docs/MER.png) | Modelo entidad-relación |
| [docs/BPMN.png](docs/BPMN.png) | Proceso de compra (BPMN) |
| [docs/modelo_c4.md](docs/modelo_c4.md) | Modelo C4 (contexto, contenedores, componentes, código) |
