# Requerimientos del sistema — Miau Market

**Proyecto:** plataforma web de comercio de productos para mascotas con asistente conversacional (MiauBot).  
**Versión del documento:** 1.3 (entrega académica)  
**Fecha:** 2026-10-12  
**Autores:** Juan Camilo Barragán Pottes · Angely Liced Herrera Roldán  

---

## Introducción

El presente documento describe la necesidad que atiende **Miau Market**, el objetivo del sistema, los actores involucrados, los requerimientos funcionales y no funcionales, las reglas de negocio y las restricciones bajo las cuales fue diseñado e implementado. Los requerimientos funcionales están formulados de manera **comprobable**: cada uno incluye criterios de aceptación y casos de prueba (CP) que permiten verificar su cumplimiento durante la evaluación del proyecto.

---

## 1. Problema o necesidad identificada

En Colombia, muchas personas en especial **adultos mayores** o usuarios **poco familiarizados con la tecnología** desean comprar alimento, accesorios y servicios para sus mascotas por internet, pero encuentran obstáculos como:

- **Desconfianza** ante sitios complejos, con pasos confusos o lenguaje técnico.
- **Dificultad para aclarar dudas** (qué producto elegir, caducidad, formas de pago) sin un acompañamiento paciente.
- **Presión por comprar rápido** en plataformas que no explican ni repiten las instrucciones.
- **Catálogos sin asesoría** o asistentes automáticos que no recuerdan al usuario ni el contexto de su mascota.

La necesidad central consiste en una **aplicación web accesible y tranquilizadora**, en la que la persona pueda **preguntar con confianza**, **obtener respuestas claras** y **completar una compra a su propio ritmo**, sin sentirse evaluada por su nivel de experiencia digital.

Asimismo, la operación comercial exige **gestión centralizada** de productos, pedidos, usuarios y del conocimiento del asistente virtual, de forma ordenada y segura.

---

## 2. Objetivo general del sistema

Desarrollar **Miau Market**, un sistema web que integre **tienda en línea** y **asistente MiauBot**, de modo que personas con distintos niveles de experiencia digital puedan:

1. Explorar productos para mascotas (gatos, perros y categorías relacionadas).
2. Recibir orientación conversacional sobre dudas frecuentes y productos disponibles.
3. Crear cuenta, armar carrito, confirmar pedidos con **pago contra entrega** y consultar el estado de sus compras.
4. Publicar reseñas que orienten a otros compradores.

igualmente, el sistema debe permitir a los **administradores** mantener el catálogo, los pedidos, los usuarios y el conocimiento del chatbot, aplicando reglas de negocio consistentes.

**Meta de experiencia de usuario:** *comprar con paciencia* interfaces legibles, mensajes comprensibles en español, asistente disponible y procesos que no exigen prisa ni conocimientos avanzados de internet.

---

## 3. Actores o tipos de usuario

| Actor | Descripción | Interacción con el sistema |
|--------|-------------|----------------------------|
| **Cliente (comprador)** | Persona registrada que adquiere productos para su mascota. Incluye perfiles con baja experiencia digital o adultos mayores. | Tienda, carrito, confirmación de pedido, historial de pedidos, perfil personal, reseñas, MiauBot y notificaciones. |
| **Visitante** | Persona que accede sin cuenta. | Puede consultar el catálogo; para comprar, usar memoria persistente del asistente y cerrar compras debe registrarse o iniciar sesión. |
| **Administrador** | Usuario autorizado con rol de personal de gestión (*staff*). | Panel de administración: productos, usuarios, pedidos, indicadores analíticos y supervisión del aprendizaje de MiauBot. |
| **MiauBot** | Asistente conversacional del sistema (componente software). | Responde consultas, orienta sobre productos y, para usuarios autenticados, utiliza contexto previo; su conocimiento ampliado se valida por un administrador. |
| **Servicio externo de IA (Google Gemini)** | Proveedor opcional de lenguaje natural. | Enriquece las respuestas del chatbot cuando la institución o el despliegue disponen de credenciales configuradas de forma segura. |

---

## 4. Requerimientos funcionales

Los requerimientos funcionales definen **qué debe hacer** el sistema. Cada uno se identifica con **RF-XX**, tiene prioridad **Alta (A)** o **Media (M)**, un **criterio de aceptación** observable y uno o más **casos de prueba** para su verificación.

**Convención para la evaluación:** un requerimiento se considera **cumplido** cuando el caso de prueba asociado se ejecuta con resultado **satisfactorio**, conforme al criterio de aceptación descrito.

### 4.1 Acceso e identidad

| ID | Pri. | Requerimiento | Criterio de aceptación | Caso de prueba |
|----|------|---------------|------------------------|----------------|
| RF-01 | A | Registro de nuevos clientes con datos obligatorios (nombre, apellido, correo, teléfono, dirección, ciudad, edad). | Con datos válidos, el sistema crea la cuenta y permite el acceso posterior. Con datos incompletos, edad no válida o correo duplicado, el sistema rechaza el registro e informa el motivo. | CP-01 Registro desde la pantalla de creación de cuenta. CP-02 Registro vía servicio web de registro (datos completos e incompletos). |
| RF-02 | A | Inicio y cierre de sesión. | Credenciales correctas permiten el acceso; credenciales incorrectas son rechazadas. Al cerrar sesión, el usuario no accede a funciones reservadas sin autenticarse de nuevo. | CP-03 Inicio de sesión en la aplicación. CP-04 Validación del servicio de autenticación. CP-05 Cierre de sesión desde el menú principal. |
| RF-03 | A | Consulta y actualización del perfil, incluido cambio de contraseña. | Los datos personales se actualizan correctamente. El cambio de contraseña solo procede si se valida la contraseña actual. | CP-06 Edición del perfil en pantalla Mi perfil. CP-07 Actualización de perfil mediante servicio web autenticado. |

### 4.2 Catálogo y búsqueda

| ID | Pri. | Requerimiento | Criterio de aceptación | Caso de prueba |
|----|------|---------------|------------------------|----------------|
| RF-04 | A | Visualización del catálogo de productos. | Cada producto muestra al menos nombre, precio en pesos colombianos (COP), stock, categoría e imagen o representación sustituta. | CP-08 Acceso a la tienda en línea. CP-09 Consulta del listado de productos vía servicio web. |
| RF-05 | A | Búsqueda de productos por texto. | Al ingresar un término de búsqueda, solo se muestran productos coincidentes; si no hay resultados, el sistema lo comunica de forma clara. | CP-10 Búsqueda con término existente y con término inexistente. |
| RF-06 | M | Organización por categorías. | Los productos se presentan agrupados por categorías (por ejemplo alimentos, juguetes, accesorios). Las categorías provienen de un catálogo administrable en base de datos: una categoría nueva o desactivada se refleja en la tienda y en el formulario de productos sin modificar el código. | CP-11 Revisión de secciones por categoría en la tienda. |
| RF-07 | A | Restricción de venta de productos caducados. | Los productos vencidos se identifican como no disponibles para compra y no pueden añadirse al carrito. | CP-12 Visualización y comportamiento de un producto caducado. |
| RF-08 | M | Detalle de producto, calificación y reseñas. | Al consultar un producto, el usuario ve descripción, promedio de calificación y comentarios de otros clientes cuando existen. | CP-13 Apertura del detalle de producto con reseñas. |

### 4.3 Carrito y compra

| ID | Pri. | Requerimiento | Criterio de aceptación | Caso de prueba |
|----|------|---------------|------------------------|----------------|
| RF-09 | A | Gestión del carrito de compras. | El cliente autenticado puede agregar productos, modificar cantidades y eliminar ítems; el total se refleja en la interfaz. | CP-14 Flujo desde tienda hasta carrito. |
| RF-10 | M | Selección parcial de ítems para compra. | El usuario marca qué productos desea enviar; solo los seleccionados pasan a la confirmación del pedido. | CP-15 Selección de un subconjunto de productos en el carrito. |
| RF-11 | A | Datos de entrega en la confirmación del pedido. | Dirección y teléfono son obligatorios; si ya existen en el perfil, se precargan. | CP-16 Confirmación con datos completos e incompletos. |
| RF-12 | A | Registro del pedido con pago contra entrega. | El sistema guarda el pedido con método de pago contra entrega, detalle de productos, total y datos de envío. | CP-17 Confirmación de pedido en pantalla. CP-18 Registro de pedido vía servicio web. |
| RF-13 | A | Actualización de inventario y visibilidad del pedido. | Tras una compra exitosa, disminuye el stock y el pedido aparece en el historial del cliente. | CP-19 Verificación de stock. CP-20 Consulta en Mis pedidos. |
| RF-14 | A | Historial y estado de pedidos. | Cada cliente consulta únicamente sus pedidos y el estado actual de cada uno (por ejemplo Pendiente, Enviado, Entregado). | CP-21 Listado de pedidos y cambio de estado por administración. |

### 4.4 Reseñas

| ID | Pri. | Requerimiento | Criterio de aceptación | Caso de prueba |
|----|------|---------------|------------------------|----------------|
| RF-15 | M | Publicación y edición de reseña. | El cliente autenticado califica (1 a 5) y comenta; puede actualizar su propia reseña sin duplicar registros indebidos. | CP-22 Crear y editar reseña en detalle de producto. |
| RF-16 | M | Promedio de calificaciones. | El detalle del producto muestra un promedio coherente con las reseñas registradas. | CP-23 Comparación del promedio mostrado y las reseñas existentes. |

### 4.5 MiauBot (acompañamiento al usuario)

| ID | Pri. | Requerimiento | Criterio de aceptación | Caso de prueba |
|----|------|---------------|------------------------|----------------|
| RF-17 | A | Disponibilidad del chatbot en la aplicación. | El asistente está accesible en las pantallas principales de compra; envía y recibe mensajes con respuesta del servidor. | CP-24 Conversación inicial con MiauBot. CP-25 Envío de mensaje al servicio del chatbot. |
| RF-18 | A | Orientación sobre productos en lenguaje natural. | Ante consultas del tipo “comida para gato”, el sistema responde con información útil y/o referencia a productos, sin fallo del servicio. | CP-26 Consultas por categoría de producto. *Nota:* la profundidad de la respuesta puede variar si el servicio de IA externo está activo. |
| RF-19 | A | Memoria de contexto para usuarios autenticados. | Tras mencionar una mascota o tema de interés, interacciones posteriores reflejan ese contexto. Los visitantes no autenticados no disponen de memoria persistente entre sesiones. | CP-27 Secuencia de mensajes con usuario registrado. |
| RF-20 | M | Supervisión del aprendizaje del asistente. | El administrador aprueba o rechaza propuestas de aprendizaje antes de que formen parte del conocimiento operativo. | CP-28 Gestión en panel MiauBot. CP-29 Consulta del servicio de aprendizaje. |
| RF-21 | M | Configuración administrativa del chatbot. | Parámetros y mensajes base del asistente pueden consultarse y ajustarse desde administración. | CP-30 Ajuste de configuración del chatbot. |

### 4.6 Notificaciones

| ID | Pri. | Requerimiento | Criterio de aceptación | Caso de prueba |
|----|------|---------------|------------------------|----------------|
| RF-22 | M | Notificaciones al usuario. | El sistema informa eventos relevantes (por ejemplo pedidos); el usuario puede marcarlas como leídas individualmente o todas. | CP-31 Uso del centro de notificaciones tras un evento generador. |

### 4.7 Administración

| ID | Pri. | Requerimiento | Criterio de aceptación | Caso de prueba |
|----|------|---------------|------------------------|----------------|
| RF-23 | A | Gestión de productos (solo administradores). | Crear, modificar y eliminar productos; usuarios sin rol administrativo no pueden ejecutar estas operaciones. | CP-32 Operaciones en panel de productos. CP-33 Intento de gestión con cuenta de cliente. |
| RF-24 | A | Gestión de usuarios. | Listar, editar, eliminar y asignar roles según permisos instituidos; operaciones masivas cuando aplique. | CP-34 Gestión de usuarios en administración. |
| RF-25 | A | Gestión de estados de pedidos. | El administrador actualiza el estado; el cliente visualiza el cambio en su historial. | CP-35 Cambio de estado y verificación en cuenta cliente. |
| RF-26 | M | Panel de indicadores (dashboard). | Se presentan métricas de ventas, pedidos, productos y usuarios para apoyo a la gestión. | CP-36 Acceso al dashboard analítico. |

### 4.8 Verificación y cumplimiento

Los autores implementaron los requerimientos RF-01 a RF-26 en la versión entregada del sistema.

| Aspecto | Descripción |
|---------|-------------|
| **Comprobación** | Mediante ejecución de casos CP-01 a CP-36, documentados en el **Anexo A** de este informe. |
| **Evidencia recomendada** | Capturas de pantalla, registro fecha/ejecutor/resultado (Satisfactorio / No satisfactorio). |
| **Alcance parcial declarado** | RF-18: la calidad y detalle de las respuestas del asistente dependen de la configuración del proveedor de IA externo; el chatbot mantiene operación básica sin dicho servicio. |

### Anexo A — Matriz de casos de prueba (resumen)

| Caso | Requerimiento | Objetivo de la prueba |
|------|---------------|------------------------|
| CP-01 a CP-07 | RF-01 a RF-03 | Registro, sesión y perfil |
| CP-08 a CP-13 | RF-04 a RF-08 | Catálogo y búsqueda |
| CP-14 a CP-21 | RF-09 a RF-14 | Carrito y pedidos |
| CP-22 a CP-23 | RF-15 a RF-16 | Reseñas |
| CP-24 a CP-30 | RF-17 a RF-21 | MiauBot |
| CP-31 | RF-22 | Notificaciones |
| CP-32 a CP-36 | RF-23 a RF-26 | Administración |

**Formato de registro por caso ejecutado:**

| Campo | Contenido |
|-------|-----------|
| Identificador | CP-XX / RF-YY |
| Fecha y ejecutor | |
| Precondiciones | Sistema en ejecución; cuentas de prueba disponibles |
| Pasos | Secuencia numerada de acciones del evaluador |
| Resultado esperado | Según criterio de aceptación del RF |
| Resultado obtenido | |
| Conclusión | Satisfactorio / No satisfactorio |
| Evidencia | Captura o anexo |

---

## 5. Requerimientos no funcionales

| ID | Requerimiento | Categoría | Criterio de verificación (resumen) |
|----|---------------|-----------|-----------------------------------|
| RNF-01 | Interfaz en **español**, mensajes claros y jerarquía visual comprensible. | Usabilidad | Revisión heurística de pantallas principales. |
| RNF-02 | Flujos de registro, carrito y compra completables **sin conocimientos técnicos**; el asistente apoya dudas. | Usabilidad | CP-01, CP-14, CP-17 y CP-24. |
| RNF-03 | Secretos y credenciales en **variables de entorno**, no en el código publicado. | Seguridad | Revisión del repositorio y archivo de ejemplo de configuración. |
| RNF-04 | Operaciones sensibles exigen **autenticación**; gestión solo para **administradores**. | Seguridad | CP-33 y pruebas de acceso sin permiso. |
| RNF-05 | Integración mediante **API REST** con intercambio **JSON**. | Arquitectura | Documentación de servicios y pruebas API. |
| RNF-06 | Tiempo de respuesta del catálogo **inferior a 3 segundos** en red local de demostración. | Rendimiento | Medición en CP-08. |
| RNF-07 | Persistencia en base de datos relacional con soporte **UTF-8** (tildes y ñ): **SQLite** en desarrollo y demostración, **MySQL 8** proyectado para producción. | Datos | Esquema creado por migraciones de Django; archivo `Backend/db.sqlite3` incluido con datos de demostración. |
| RNF-08 | Diseño **adaptable** a computador y dispositivo móvil. | Usabilidad | CP-08 en distintos tamaños de pantalla. |
| RNF-09 | **Tema claro y oscuro** disponible. | Usabilidad | Alternancia desde el menú principal. |
| RNF-10 | Ventanas emergentes cerrables de forma **predecible** (incluida tecla Escape). | Usabilidad | Prueba en detalle de producto y menú móvil. |
| RNF-11 | Servicio de IA **opcional**; el sistema continúa operando con respuestas locales si no hay proveedor externo. | Disponibilidad | CP-24 sin clave de IA externa. |
| RNF-12 | Código en **repositorio Git** con instrucciones de instalación. | Mantenibilidad | README del proyecto. |

---

## 6. Reglas de negocio relevantes

| ID | Regla |
|----|--------|
| RN-01 | Los precios se expresan en **pesos colombianos (COP)**; el total del pedido coincide con la suma validada en servidor de las líneas del pedido. |
| RN-02 | No se venden más unidades que el **stock** disponible al confirmar la compra. |
| RN-03 | Los productos **caducados** no se ofrecen para venta. |
| RN-04 | Solo **administradores** gestionan catálogo, usuarios y pedidos desde el panel de administración. |
| RN-05 | El método de pago ofrecido al cliente es **contra entrega**; no hay pasarela de tarjeta en esta versión. |
| RN-06 | Para crear un pedido el cliente debe estar **autenticado** y registrar **dirección y teléfono** de entrega. |
| RN-07 | En el registro y perfil, la **edad** debe estar en el rango validado por el sistema (18 a 120 años). |
| RN-08 | Cada reseña asocia **un usuario y un producto**; el cliente edita su propia reseña según las reglas del sistema. |
| RN-09 | El conocimiento aprendido por MiauBot requiere **aprobación administrativa** antes de usarse como respuesta oficial. |
| RN-10 | La memoria conversacional del asistente es **privada** por cuenta de usuario autenticada. |

---

## 7. Restricciones del sistema

| ID | Restricción |
|----|-------------|
| RS-01 | **Tecnologías:** cliente Angular, servidor Django REST, base de datos SQLite en desarrollo, pruebas y demostración; MySQL 8 proyectado para producción. |
| RS-02 | **Demostración académica:** servicios en entorno local (puertos definidos en documentación de instalación). |
| RS-03 | **Inteligencia artificial externa** sujeta a conectividad, cuotas y configuración institucional. |
| RS-04 | **Sin pago en línea** integrado en la versión actual. |
| RS-05 | **Enfoque Colombia:** ciudades de registro, moneda COP, entrega conceptual contra entrega. |
| RS-06 | **Navegadores modernos** con JavaScript habilitado. |
| RS-07 | **Imágenes de producto** según archivos cargados en administración. |
| RS-08 | **Concurrencia alta** de compras no es objetivo de esta versión académica. |
| RS-09 | MiauBot **no sustituye** atención veterinaria profesional. |
| RS-10 | En producción real, el tratamiento de **datos personales** debe cumplir normativa colombiana (Habeas Data); el proyecto académico aplica buenas prácticas de configuración segura. |

---

## 8. Trazabilidad

Cadena **Necesidad → Requerimientos → Proceso (BPMN) → Arquitectura (C4) → Datos (MER) → Código**.

| Necesidad del usuario | Requerimientos | Tarea del BPMN | Componente C4 (nivel 3) | Tablas | Código principal |
|------------------------|----------------|----------------|-------------------------|--------|------------------|
| Comprar con calma sin saber de tecnología | RF-01, RF-02, RF-03, RNF-01, RNF-02 | Iniciar sesión o registrarse | Autenticación y perfil | Users | `views.py` (`RegistroView`, `LoginView`, `ActualizarPerfilView`), `serializers.py`, `backends.py`; `register/`, `login/`, `profile/` |
| Encontrar el producto adecuado | RF-04 a RF-08 | Buscar productos y agregarlos al carrito | Catálogo de productos | Categories, Products, Product_Ratings | `CategoriaListView`, `ProductoListView`, `ProductoSerializer`; `shop/` |
| No sabe qué producto elegir | RF-17 a RF-21 | Buscar productos (apoyo de MiauBot) | MiauBot; Conocimiento, memoria y aprendizaje; Cliente de IA | MiauBot_Config, MiauBot_Conocimiento, MiauBot_Frases, MiauBot_Aprendizaje, MiauBot_Memoria | `ai_views.py`, `services/miaubot_*.py`; `chatbot/` |
| Elegir qué comprar y cuánto | RF-09, RF-10 | Seleccionar productos e ir a pagar; Ajustar cantidades del carrito | Aplicación web (carrito en el navegador) | — | `cart/`, `auth.service.ts` (carrito) |
| Confirmar la compra con pago contra entrega | RF-11, RF-12, RF-13, RN-01, RN-02, RN-05, RN-06 | Ingresar dirección y teléfono; Validar productos y stock; Registrar pedido y descontar stock; Enviar confirmación | Gestión de pedidos | PaymentOrders, Orders_Details, Products | `CrearPedidoView`, `CrearPedidoSerializer`, `services/pedidos_service.py`; `checkout/` |
| Saber en qué va su compra | RF-14, RF-22, RF-25 | Notificar a administradores; Marcar como Enviado / Entregado / Devuelto; Guardar estado y notificar al cliente | Gestión de pedidos; Notificaciones | PaymentOrders, Notificaciones | `ActualizarPedidoView`, `MisPedidosView`, `NotificacionesView`; `my-orders/`, `notifications-bell/` |
| Confiar en opiniones de otros | RF-15, RF-16, RN-08 | — (posterior a la compra) | Reseñas y calificaciones | Product_Reviews, Product_Ratings | `ProductReviewsView`, `UserReviewView`, `services/ratings_service.py`; `shop/` (detalle) |
| No comprar productos vencidos | RF-07, RN-03 | Validar productos y stock disponible | Catálogo; Notificaciones | Products, Categories (`Perecedero`), Notificaciones | `ProductoListView`, `VerificarProductosCaducadosView`, comando `verificar_productos_caducados` |
| Operar el negocio | RF-23, RF-24, RF-26, RN-04 | Revisar pedido y preparar despacho | Catálogo; Gestión de usuarios | Products, Categories, Users | `ProductoListView`/`ProductoDetailView` (admin), `Gestion*View`, `Bulk*View`; `admin/`, `dashboard/` |

Documentos relacionados: [BPMN.png](BPMN.png), [arquitectura.md](arquitectura.md), [modelo_c4.md](modelo_c4.md), [modelo_entidad_relacion.md](modelo_entidad_relacion.md), [stack_tecnologico.md](stack_tecnologico.md).

---

## 9. Entregables de la documentación

| Punto | Documento |
|-------|-----------|
| Requerimientos, actores, reglas y trazabilidad | `docs/requerimientos.md` |
| Stack tecnológico y justificación | `docs/stack_tecnologico.md` |
| Arquitectura del sistema | `docs/arquitectura.md` |
| Modelo entidad-relación | `docs/modelo_entidad_relacion.md`, `docs/MER.png`, `docs/DIAGRAMA MODELO ENTIDAD.mwb` |
| Proceso de compra (BPMN) | `docs/BPMN.png` |
| Modelo C4 | `docs/modelo_c4.md` |
| Instalación, ejecución y usuarios de prueba | `README.md` |

---

*Fin del documento de requerimientos — Miau Market.*
