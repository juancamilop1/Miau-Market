# Miau Market — Stack tecnológico y justificación

**Proyecto:** Miau Market — tienda en línea de productos para mascotas con asistente virtual (MiauBot).
**Autores:** Juan Camilo Barragán Pottes · Angely Liced Herrera Roldán

Las tecnologías se eligieron a partir de las necesidades del sistema descritas en `requerimientos.md`: una tienda fácil de usar para personas mayores o con poca experiencia digital, un asistente conversacional paciente, información de pedidos con integridad entre usuarios, productos y detalles, y un proyecto que el evaluador pueda descargar y ejecutar sin instalar servidores adicionales.

## Resumen

| Área | Tecnología | Versión |
|------|-----------|---------|
| Lenguaje frontend | TypeScript | 5.9 |
| Framework frontend | Angular (componentes standalone, signals, SSR) | 20 |
| Lenguaje backend | Python | 3.13 |
| Framework backend | Django + Django REST Framework | 4.2 LTS / 3.14+ |
| Base de datos (desarrollo, pruebas y demostración) | SQLite | Incluida en Python |
| Base de datos (producción, proyectada) | MySQL | 8 |
| Servicio externo / nube | Google Gemini API (`google-generativeai`) | gemini-2.0-flash |
| Gráficas | Chart.js + ng2-charts | 4.5 / 8 |
| Control de versiones | Git + GitHub | — |
| Despliegue | Entorno local con script `iniciar_miau_market.bat` | — |

---

## 1. Frontend

### Angular 20
Se utiliza Angular porque el sistema tiene muchas pantallas con estado compartido (carrito, sesión, notificaciones, chat) y Angular ofrece en un solo framework el enrutamiento, los formularios, el cliente HTTP y la inyección de dependencias, sin depender de librerías externas para cada tarea.

- **Componentes standalone y signals:** cada pantalla (tienda, carrito, checkout, pedidos, perfil, administración, chat) es un componente independiente. Los *signals* actualizan la interfaz de inmediato cuando cambia el carrito o llega una notificación, algo importante para que el usuario vea el efecto de cada acción.
- **Formularios con validación:** el registro, el checkout y el perfil muestran mensajes claros cuando falta un dato, lo que reduce la frustración de usuarios poco experimentados.
- **Renderizado del lado del servidor (Angular SSR + Express):** las páginas se generan previamente, por lo que la primera carga es más rápida en equipos o conexiones lentas.

### TypeScript 5.9
Se utiliza TypeScript porque el tipado estático detecta errores en tiempo de compilación, por ejemplo al armar el pedido que se envía al backend (`productos`, `direccion_envio`, `telefono_envio`). Esto evita fallos que el usuario solo vería al comprar.

### Chart.js + ng2-charts
Se utilizan en el panel del administrador para mostrar ventas y pedidos en gráficas. Chart.js es liviano y ng2-charts lo integra directamente con Angular.

### CSS propio con variables de diseño
Se usa CSS con variables globales (colores, tipografía Plus Jakarta Sans, tarjetas, alertas, ventanas modales) en lugar de un framework visual pesado. Así se controla el tamaño de letra, el contraste y el tamaño de los botones, que son decisivos para la accesibilidad de personas mayores.

---

## 2. Backend

### Python 3.13
Se utiliza Python porque tiene una sintaxis legible, facilita mantener la lógica de negocio y cuenta con librerías oficiales para la IA de Google, necesaria para MiauBot.

### Django 4.2 LTS
Se utiliza Django porque el sistema maneja entidades relacionadas (usuarios, productos, pedidos, detalles, reseñas, notificaciones) y Django aporta:

- **ORM y migraciones:** el esquema de la base de datos se define en código (`models.py`) y se crea con `migrate`, por lo que cualquier persona obtiene la misma estructura al descargar el proyecto.
- **Transacciones:** la creación de un pedido se ejecuta con `@transaction.atomic`. Si un producto no tiene stock, no se guarda nada, lo que protege la integridad del inventario.
- **Seguridad incluida:** contraseñas cifradas, protección contra inyección SQL y un modelo de usuario propio con roles (`is_staff`).
- **Panel de administración** (`/admin/`) para revisar datos sin desarrollo adicional.
- **Versión LTS:** soporte extendido de seguridad, adecuado para un proyecto que debe mantenerse estable.

### Django REST Framework (DRF)
Se utiliza DRF porque el frontend y el backend son aplicaciones separadas que se comunican por JSON. DRF ofrece:

- **Serializers** que validan en el servidor los datos recibidos (precios, cantidades, campos obligatorios).
- **Autenticación por token**, que el frontend guarda tras el inicio de sesión.
- **Permisos explícitos** (`IsAuthenticated`, `IsAdminUser`) para que un cliente no pueda acceder a funciones de administrador.

### Librerías complementarias
| Librería | Por qué se usa |
|----------|----------------|
| `django-cors-headers` | Permite que la aplicación Angular (puerto 4200) consuma la API (puerto 8000) de forma controlada. |
| `python-dotenv` | Carga las claves y la configuración desde `Backend/.env`, de modo que los secretos (por ejemplo la clave de Gemini) no se suben al repositorio. |
| `Pillow` | Procesa las imágenes de productos que sube el administrador. |
| `google-generativeai` | Cliente oficial de Google para comunicarse con Gemini. |

---

## 3. Base de datos

Se utiliza una base de datos **relacional** porque la información está relacionada (un pedido pertenece a un usuario y contiene detalles que referencian productos) y requiere llaves foráneas, restricciones de unicidad (una reseña por usuario y producto) y consultas estructuradas.

El proyecto usa dos motores según el entorno. Ambos se manejan con el mismo código, porque todo el acceso a datos pasa por el ORM de Django.

### SQLite — desarrollo, pruebas y demostración
Es el motor configurado en la versión entregada. Se eligió para este entorno porque:

- **No requiere instalar un servidor:** la base es un archivo (`Backend/db.sqlite3`) incluido en el repositorio con datos de demostración. El evaluador descarga el proyecto y lo ejecuta sin configurar credenciales.
- **Soporta lo que el sistema necesita para probarse:** llaves foráneas, transacciones, vistas (`Product_Ratings`) y texto UTF-8 con tildes y ñ.
- **Permite pruebas repetibles:** si se borra el archivo, `migrate` y `seed_demo` lo recrean con los mismos datos.

### MySQL 8 — producción (proyectada)
Para un despliegue real se proyecta MySQL, porque SQLite no está pensado para muchos usuarios comprando al mismo tiempo, y MySQL sí maneja concurrencia, usuarios y permisos del motor, y copias de seguridad en servidor.

- El modelo entidad-relación se diseñó en **MySQL Workbench** (`docs/DIAGRAMA MODELO ENTIDAD.mwb`).
- Las migraciones del proyecto ya contemplan ambos motores.
- El cambio consiste en instalar el conector de MySQL y ajustar la configuración `DATABASES` en `settings.py`; no requiere modificar modelos, vistas ni servicios.

---

## 4. Servicios externos, APIs y servicios en la nube

### Google Gemini API
Se utiliza Gemini como servicio de inteligencia artificial en la nube para que MiauBot entienda preguntas escritas con lenguaje natural, incluso con errores de ortografía o de forma informal, que es como suelen escribir los usuarios con poca experiencia digital.

- El backend envía a Gemini la pregunta junto con el **catálogo real** y la **memoria del usuario** (mascotas, temas anteriores), de forma que las recomendaciones son personalizadas y solo incluyen productos existentes.
- El modelo `gemini-2.0-flash` responde rápido y tiene un nivel de uso gratuito suficiente para el proyecto.
- **Tolerancia a fallos:** si no hay conexión o no hay clave configurada, MiauBot responde con su motor local (conocimiento y respuestas aprendidas guardadas en la base de datos), por lo que el sistema nunca queda sin asistente.

No se usan otros servicios en la nube: el pago es contra entrega (RS-04) y la aplicación se ejecuta localmente para la demostración académica (RS-02).

---

## 5. Herramientas de despliegue

| Herramienta | Por qué se usa |
|-------------|----------------|
| `iniciar_miau_market.bat` | Un solo archivo crea el entorno virtual, instala dependencias, aplica migraciones, carga los datos de demostración y abre backend y frontend. Así el evaluador ejecuta el sistema con doble clic. |
| Entorno virtual de Python (`venv`) + `pip` | Aísla las dependencias del backend y las instala con las versiones de `requirements.txt`. |
| `npm` + Angular CLI | Instala las dependencias del frontend y lo compila (`ng build`) o lo sirve en desarrollo (`ng serve`). |
| Comando `seed_demo` | Carga usuarios de prueba y productos de ejemplo de forma repetible. |

---

## 6. Control de versiones

### Git + GitHub
Se utiliza Git porque permite trabajar en equipo sobre el mismo código, registrar cada cambio y volver a versiones anteriores si algo falla. GitHub aloja el repositorio (`github.com/juancamilop1/Miau-Market`) para que ambos integrantes y el evaluador accedan a la misma versión. El archivo `.gitignore` excluye secretos (`.env`), dependencias (`node_modules`, `venv`) y archivos generados.

---

## 7. Otras tecnologías

| Tecnología | Uso |
|-----------|-----|
| Visual Studio Code / Cursor | Editor de desarrollo para frontend y backend. |
| MySQL Workbench | Diseño y visualización del modelo entidad-relación. |
| bpmn.io | Modelado del proceso de compra en BPMN (`bpmn_proceso_compra.bpmn`). |
| Mermaid | Diagramas del modelo C4 dentro de la documentación (`modelo_c4.md`). |
