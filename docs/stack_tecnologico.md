# Miau Market — Stack tecnológico y justificación

**Proyecto:** Miau Market — tienda en línea de productos para mascotas con asistente virtual (MiauBot).
**Autores:** Juan Camilo Barragán Pottes · Angely Liced Herrera Roldán

Las tecnologías se eligieron a partir de las necesidades descritas en `requerimientos.md`: una tienda accesible para usuarios con distintos niveles de experiencia digital (incluidos adultos mayores), un asistente conversacional paciente con motor local, integridad transaccional en pedidos y un despliegue reproducible tanto en entorno local como en la nube.

## Resumen

| Área | Tecnología | Versión / detalle |
|------|-----------|-------------------|
| Lenguaje frontend | TypeScript | 5.9 |
| Framework frontend | Angular (standalone, signals, guards, interceptor HTTP) | 20 |
| Lenguaje backend | Python | 3.12+ |
| Framework backend | Django + Django REST Framework | 5.0 (`>=4.2,<5.1`) / DRF 3.14+ |
| Servidor WSGI / estáticos | Gunicorn + WhiteNoise | 22+ / 6.6+ |
| Base de datos (producción) | TiDB Cloud Starter (MySQL-compatible, TLS vía PyMySQL) | MySQL 8 protocol |
| Base de datos (local) | MySQL 8 (o SQLite opcional con `DB_ENGINE=sqlite`) | MySQL 8 / SQLite |
| Asistente conversacional | Motor local en BD (`MiauBot_*`) + Google Gemini API opcional | `gemini-2.0-flash` |
| Gráficas | Chart.js + ng2-charts | 4.5 / 8 |
| Control de versiones | Git + GitHub | — |
| Despliegue nube | Cloudflare Workers (frontend) + Render (API) + TiDB Cloud (BD) | Activo (V2) |
| Despliegue local | Script `iniciar_miau_market.bat` | Activo |

---

## 1. Frontend

### Angular 20
Se utiliza Angular porque el sistema integra múltiples vistas con estado compartido (carrito, sesión, favoritos, notificaciones, MiauBot) y ofrece en un solo framework enrutamiento con guards (`authGuard`, `adminGuard`), interceptores HTTP (`authInterceptor`), formularios y cliente HTTP.

- **Componentes standalone y signals:** cada pantalla (tienda, detalle de producto `/product/:id`, carrito, checkout, pedidos, favoritos, perfil/mascotas, administración, dashboard y chat) es modular y reacciona de inmediato ante cambios de estado.
- **Formularios con validación:** registro, checkout y perfil informan errores claros en español antes y después de consultar la API.
- **Compilación estática para nube (`build:pages`):** genera el bundle SPA servido por Cloudflare Workers con `wrangler.toml` (`not_found_handling = "single-page-application"`).

### TypeScript 5.9
El tipado estático previene errores en contratos de API (productos, catálogos, pedidos, reseñas y mascotas) antes de ejecutar la aplicación.

### Chart.js + ng2-charts
Presentan en `/dashboard` las métricas administrativas de ventas, estados de pedidos y distribución por categorías.

### CSS propio con variables de diseño
Permite controlar tipografía, contraste, modo claro/oscuro y tamaño de botones sin sobrecargar el bundle, favoreciendo la legibilidad para adultos mayores.

---

## 2. Backend

### Python 3.12+
Sintaxis clara, ecosistema maduro para web y soporte oficial para clientes de IA.

### Django 5.0 + Django REST Framework
Elegidos por su soporte nativo para sistemas relacionales con reglas de negocio estrictas:

- **ORM y migraciones incrementales (`0001`–`0018`):** versionan todo el esquema (usuarios, catálogos, productos, pedidos, reseñas, favoritos, mascotas y MiauBot).
- **Transacciones atómicas y bloqueo de filas:** `@transaction.atomic` + `select_for_update()` evitan sobreventa de inventario y garantizan restauración segura de stock al cancelar o devolver pedidos.
- **Seguridad y permisos:** autenticación por token (`TokenAuthentication`), permisos explícitos (`IsAuthenticated`, `IsAdminUser`, `IsSelfOrAdmin`), *throttling* en login (`10/min`) y chatbot (`30/min`), y contraseñas cifradas.
- **Serializers:** validan entradas en servidor sin confiar en precios ni estados enviados desde el cliente.

### Librerías complementarias

| Librería | Propósito |
|----------|-----------|
| `pymysql` + `cryptography` | Conexión MySQL/TiDB Cloud con cifrado TLS sin dependencias nativas de compilación en Render. |
| `django-cors-headers` | Controla el acceso CORS entre el dominio de Cloudflare Workers y la API en Render. |
| `gunicorn` + `whitenoise` | Servidor WSGI de producción y servicio de archivos estáticos del admin de Django. |
| `python-dotenv` | Carga configuración y credenciales desde `Backend/.env` en local. |
| `Pillow` | Procesamiento de imágenes de productos. |
| `google-generativeai` | Cliente opcional para enriquecer respuestas de MiauBot cuando `GEMINI_API_KEY` está configurada. |

---

## 3. Base de datos

Se emplea una base de datos **relacional** porque el comercio electrónico exige integridad referencial, transacciones ACID y unicidad (correo, usuario, una reseña por usuario/producto, favoritos sin duplicados y catálogos con llaves foráneas reales).

- **Producción — TiDB Cloud Starter (compatible con MySQL 8):** motor distribuido compatible con el protocolo MySQL sobre TLS (`DB_SSL=True`, puerto 4000), con las migraciones `0001`–`0018` aplicadas y `utf8mb4_unicode_ci`.
- **Desarrollo local — MySQL 8 (y respaldo SQLite):** el proyecto soporta MySQL 8 local por defecto y permite activar SQLite con `DB_ENGINE=sqlite` para pruebas rápidas sin servidor de BD.
- El diseño base del MER se elaboró en **MySQL Workbench** (`docs/DIAGRAMA MODELO ENTIDAD.mwb`).

---

## 4. Servicios externos, IA y nube

### MiauBot (motor local + Google Gemini opcional)
El asistente conversacional está implementado **dentro del backend de Miau Market** (`Backend/usuarios/services/miaubot_*.py`), no depende de herramientas externas del entorno de desarrollo:

- **Motor local en base de datos:** gestiona configuración, base de conocimiento por especie/tema, memoria privada de mascotas por usuario y aprendizaje supervisado con aprobación del administrador.
- **Google Gemini API (`gemini-2.0-flash`, opcional):** cuando existe `GEMINI_API_KEY`, redacta respuestas más naturales con contexto del catálogo real y la memoria del cliente. Si no hay clave o cuota, el motor local responde sin interrumpir el servicio (RNF-11).

### Infraestructura de despliegue en nube (V2)

| Componente | Servicio | URL / rol |
|------------|----------|-----------|
| Frontend SPA | Cloudflare Workers (Static Assets) | `https://miau-market.juancamilobarragan2.workers.dev` |
| Backend API | Render Web Service (Free) | `https://miau-market-api.onrender.com` (`/api/health/`) |
| Base de datos | TiDB Cloud Starter (MySQL-compatible) | Base `miau_market` con conexión TLS |

*Limitaciones conocidas del plan gratuito:* Render suspende el servicio tras ~15 min de inactividad (*cold start* de 30–60 s) y su disco `/media` es efímero al redeploy.

---

## 5. Herramientas de desarrollo y documentación

| Herramienta | Uso |
|-------------|-----|
| Git + GitHub | Control de versiones colaborativo (`github.com/juancamilop1/Miau-Market`). |
| Cursor / VS Code | Entorno de desarrollo asistido por IA para apoyo a programación y revisión de código (no es componente en tiempo de ejecución del recomendador). |
| `iniciar_miau_market.bat` + `seed_demo` | Arranque reproducible en Windows y carga de datos de demostración. |
| MySQL Workbench / bpmn.io / Mermaid | Modelado de MER, proceso BPMN y arquitectura C4. |
