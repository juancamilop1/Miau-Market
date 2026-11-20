# Miau Market — Modelo C4

**Proyecto:** Miau Market — tienda en línea de productos para mascotas con asistente virtual (MiauBot).
**Autores:** Juan Camilo Barragán Pottes · Angely Liced Herrera Roldán

El modelo describe la arquitectura en cuatro niveles. Cada nivel amplía un elemento del nivel anterior:

| Nivel | Elemento que se amplía | Qué muestra |
|-------|------------------------|-------------|
| 1. Contexto | — | El sistema Miau Market, sus usuarios y los sistemas externos. |
| 2. Contenedores | Sistema *Miau Market* | Aplicación web, API REST, base de datos relacional y almacén de imágenes. |
| 3. Componentes | Contenedor *API REST* | Módulos internos del backend y su responsabilidad. |
| 4. Código | Componente *Gestión de pedidos* | Clases, servicio transaccional y modelos que implementan pedidos y catálogos. |

---

## Nivel 1 — Contexto

```mermaid
flowchart TB
  cliente(["<b>Cliente</b><br/>[Persona]<br/>Dueño de mascota, incluso adulto mayor<br/>o con poca experiencia en compras en línea"])
  admin(["<b>Administrador</b><br/>[Persona]<br/>Personal de la tienda"])

  miau["<b>Miau Market</b><br/>[Sistema de software]<br/>Tienda en línea de productos para mascotas<br/>con perfiles de mascota y asistente MiauBot"]

  gemini["<b>Google Gemini API</b><br/>[Sistema externo, opcional]<br/>IA en la nube que enriquece las<br/>respuestas conversacionales de MiauBot"]

  cliente -->|"Busca productos, registra mascotas,<br/>pregunta a MiauBot, compra y sigue pedidos<br/>[Navegador web]"| miau
  admin -->|"Administra catálogo, pedidos, usuarios<br/>y conocimiento del bot<br/>[Navegador web]"| miau
  miau -->|"Envía consulta con catálogo y contexto,<br/>recibe respuesta<br/>[HTTPS/JSON]"| gemini

  classDef persona fill:#08427b,stroke:#052e56,color:#fff
  classDef sistema fill:#1168bd,stroke:#0b4884,color:#fff
  classDef externo fill:#999999,stroke:#6b6b6b,color:#fff
  class cliente,admin persona
  class miau sistema
  class gemini externo
```

**Elementos:**

- **Cliente:** usuario final; actor principal del proceso de compra.
- **Administrador:** usuario con permiso de personal (`is_staff`). Opera el panel de administración y el dashboard.
- **Miau Market:** sistema web desarrollado y desplegado.
- **Google Gemini API:** sistema externo opcional. Si no está disponible o no hay clave configurada, MiauBot responde con su motor local y la base de conocimiento/aprendizaje aprobada.

No existe integración con pasarela de pagos en esta versión; el método operativo principal es **contra entrega**.

---

## Nivel 2 — Contenedores

```mermaid
flowchart TB
  cliente(["<b>Cliente</b><br/>[Persona]"])
  admin(["<b>Administrador</b><br/>[Persona]"])

  subgraph miau["Miau Market [Sistema de software]"]
    web["<b>Aplicación web</b><br/>[Contenedor: Angular 20, TypeScript]<br/>Cloudflare Workers (prod) / :4200 (local)<br/>Tienda, PDP, carrito, favoritos, checkout,<br/>pedidos, perfil/mascotas, admin y MiauBot"]
    api["<b>API REST</b><br/>[Contenedor: Python 3.12+, Django 5.0, DRF]<br/>Render + Gunicorn (prod) / :8000 (local)<br/>Auth, catálogos, pedidos, reseñas, wishlist,<br/>mascotas, notificaciones y MiauBot"]
    db[("<b>Base de datos relacional</b><br/>[Contenedor: TiDB Cloud / MySQL 8]<br/>(SQLite opcional en local)<br/>Usuarios, catálogos, productos, pedidos,<br/>reseñas, favoritos, mascotas y MiauBot")]
    media[("<b>Almacén de imágenes</b><br/>[Contenedor: sistema de archivos /media]<br/>Imágenes de productos")]
  end

  gemini["<b>Google Gemini API</b><br/>[Sistema externo, opcional]<br/>IA conversacional"]

  cliente -->|"Usa [HTTPS]"| web
  admin -->|"Usa [HTTPS]"| web
  web -->|"Consume /api/usuarios/...<br/>[HTTPS/JSON + Token]"| api
  api -->|"Lee y escribe<br/>[Django ORM / PyMySQL TLS]"| db
  api -->|"Guarda y sirve imágenes"| media
  api -->|"Solicita respuestas de MiauBot<br/>[HTTPS/JSON]"| gemini

  classDef persona fill:#08427b,stroke:#052e56,color:#fff
  classDef contenedor fill:#438dd5,stroke:#2e6295,color:#fff
  classDef externo fill:#999999,stroke:#6b6b6b,color:#fff
  class cliente,admin persona
  class web,api,db,media contenedor
  class gemini externo
  style miau fill:none,stroke:#444,stroke-dasharray:5 5
```

| Contenedor | Tecnología | Responsabilidad |
|------------|-----------|-----------------|
| Aplicación web | Angular 20 (componentes standalone, signals, guards, interceptor 401) en Cloudflare Workers | Presentación, navegación, carrito y sesión (`localStorage`). No contiene reglas de negocio críticas. |
| API REST | Django 5.0 + DRF + Gunicorn + WhiteNoise en Render | Valida datos, precios y stock; aplica permisos (`IsAuthenticated`, `IsAdminUser`, `IsSelfOrAdmin`), throttling y orquesta MiauBot. |
| Base de datos | TiDB Cloud Starter (MySQL-compatible, TLS) en producción; MySQL 8 o SQLite en local | Persistencia relacional con integridad referencial (FK) para todas las entidades y catálogos. |
| Almacén de imágenes | Carpeta `Backend/media/productos/` | Archivos de imagen referenciados desde `Products`. |

No se desarrolla aplicación móvil nativa: la aplicación web es adaptable (*responsive*).

---

## Nivel 3 — Componentes del contenedor *API REST*

```mermaid
flowchart TB
  web["<b>Aplicación web</b><br/>[Contenedor: Angular 20]"]

  subgraph api["API REST [Contenedor: Django + DRF]"]
    auth["<b>Autenticación, perfil y mascotas</b><br/>[RegistroView, LoginView, UsuarioDetailView,<br/>ActualizarPerfilView, MascotasView, IsSelfOrAdmin]<br/>Registro, login con throttle, token,<br/>perfil y mascotas del usuario"]
    gusuarios["<b>Gestión de usuarios</b><br/>[UsuarioListView, GestionUsuariosView,<br/>ConvertirAdministradorView, BulkDeleteUsersView]<br/>Cuentas y rol administrador. Solo staff"]
    catalogo["<b>Catálogo y lista de deseos</b><br/>[CatalogosView, CategoriaListView,<br/>ProductoListView, ProductoDetailView, WishlistView]<br/>Catálogos DB, CRUD de productos y favoritos"]
    pedidos["<b>Gestión de pedidos</b><br/>[CrearPedidoView, ActualizarPedidoView,<br/>CancelarPedidoView, MisPedidosView, pedidos_service]<br/>Stock atómico con select_for_update,<br/>cancelación y restauración de inventario"]
    resenas["<b>Reseñas y calificaciones</b><br/>[ProductReviewsView, UserReviewView,<br/>ProductRatingsView, ratings_service]<br/>Una reseña por usuario y producto"]
    notif["<b>Notificaciones</b><br/>[NotificacionesView,<br/>VerificarProductosCaducadosView]<br/>Avisos de pedidos y caducidad"]
    bot["<b>MiauBot</b><br/>[ChatbotView, ChatbotConfigView, miaubot_service]<br/>Orquesta conversación con throttle"]
    botdatos["<b>Conocimiento, memoria y aprendizaje</b><br/>[miaubot_knowledge, miaubot_memoria,<br/>miaubot_aprendizaje]<br/>Motor local, memoria privada por usuario<br/>y respuestas aprendidas aprobadas"]
    llm["<b>Cliente de IA</b><br/>[miaubot_llm]<br/>Prompt con catálogo y memoria;<br/>fallback automático al motor local"]
    orm["<b>Modelos de datos</b><br/>[Django ORM: Usuario, Cat*, Producto, Pedido,<br/>DetallePedido, Resena, Wishlist, Mascota, ...]"]
  end

  db[("<b>Base de datos</b><br/>[TiDB Cloud / MySQL]")]
  gemini["<b>Google Gemini API</b><br/>[Sistema externo, opcional]"]

  web -->|"Registro / login / perfil / mascotas"| auth
  web -->|"Administra usuarios [Token staff]"| gusuarios
  web -->|"Catálogos, productos y favoritos"| catalogo
  web -->|"Crea, consulta y cancela pedidos [Token]"| pedidos
  web -->|"Crea y lee reseñas"| resenas
  web -->|"Consulta notificaciones [Token]"| notif
  web -->|"Mensajes del chat"| bot

  pedidos -->|"Genera avisos"| notif
  bot -->|"Busca productos"| catalogo
  bot -->|"Consulta y actualiza"| botdatos
  bot -->|"Pide respuesta"| llm
  llm -->|"HTTPS/JSON"| gemini

  auth --> orm
  gusuarios --> orm
  catalogo --> orm
  pedidos --> orm
  resenas --> orm
  notif --> orm
  botdatos --> orm
  orm -->|"SQL (PyMySQL)"| db

  classDef componente fill:#85bbf0,stroke:#5d82a8,color:#000
  classDef contenedor fill:#438dd5,stroke:#2e6295,color:#fff
  classDef externo fill:#999999,stroke:#6b6b6b,color:#fff
  class auth,gusuarios,catalogo,pedidos,resenas,notif,bot,botdatos,llm,orm componente
  class web,db contenedor
  class gemini externo
  style api fill:none,stroke:#444,stroke-dasharray:5 5
```

| Componente | Archivos | Responsabilidad |
|------------|----------|-----------------|
| Autenticación, perfil y mascotas | `views.py`, `permissions.py`, `login_serializer.py`, `backends.py` | Registro, login con throttle, token, aislamiento de usuario (`IsSelfOrAdmin`), perfil y mascotas. |
| Gestión de usuarios | `views.py` (`UsuarioListView`, `Gestion*`, `Bulk*`) | Administración de cuentas y roles. Requiere `IsAdminUser`. |
| Catálogo y lista de deseos | `views.py`, `serializers.py` | Catálogos (`cat_categoria`, `cat_metodo_pago`, `cat_estado_pedido`), CRUD de productos y favoritos (`Lista_Deseos`). |
| Gestión de pedidos | `views.py`, `pedidos_serializers.py`, `services/pedidos_service.py` | Pedido transaccional, bloqueo de stock, cancelación del cliente y restauración automática. |
| Reseñas y calificaciones | `views.py`, `reviews_serializers.py`, `services/ratings_service.py` | Reseñas y promedio por producto. |
| Notificaciones | `views.py`, `notificaciones_serializers.py` | Avisos al cliente y al administrador. |
| MiauBot | `ai_views.py`, `services/miaubot_service.py` | Orquestación del asistente y configuración administrativa. |
| Conocimiento, memoria y aprendizaje | `services/miaubot_knowledge.py`, `miaubot_memoria.py`, `miaubot_aprendizaje.py` | Motor local, memoria persistente y flujo de aprobación de respuestas. |
| Cliente de IA | `services/miaubot_llm.py` | Integración opcional con Google Gemini. |
| Modelos de datos | `models.py` | Entidades, catálogos y relaciones FK. |

---

## Nivel 4 — Código del componente *Gestión de pedidos*

```mermaid
classDiagram
  direction LR

  class CrearPedidoView {
    <<APIView>>
    +permission_classes: IsAuthenticated
    +post(request) Response
  }
  class ActualizarPedidoView {
    <<APIView>>
    +permission_classes: IsAuthenticated, IsAdminUser
    +put(request, pk) Response
  }
  class CancelarPedidoView {
    <<APIView>>
    +permission_classes: IsAuthenticated
    +post(request, pk) Response
  }
  class MisPedidosView {
    <<APIView>>
    +permission_classes: IsAuthenticated
    +get(request) Response
  }
  class CrearPedidoSerializer {
    <<Serializer>>
    +Metodo_Pago: str
    +productos: DetallePedidoSerializer[]
    +direccion_envio: str
    +telefono_envio: str
  }
  class DetallePedidoSerializer {
    <<Serializer>>
    +Id_Products: int
    +Cantidad: int
    +Precio_Unitario: Decimal
  }
  class pedidos_service {
    <<módulo de servicio>>
    +crear_pedido(usuario, data) Pedido
    +actualizar_estado_pedido(pedido_id, nuevo_estado) Pedido
    +cancelar_pedido_usuario(pedido_id, usuario_id) Pedido
    +listar_pedidos_usuario(usuario_id) list
    +listar_pedidos_admin() list
    -_restaurar_stock(pedido)
    -_notificar_admins(pedido)
  }
  class Pedido {
    <<Model: PaymentOrders>>
    +id: int
    +Fecha: datetime
    +Total: Decimal
    +Metodo_Pago: str
    +metodo_pago: CatMetodoPago
    +Estado: str
    +estado: CatEstadoPedido
    +Direccion_Envio: str
    +Telefono_Envio: str
  }
  class CatMetodoPago {
    <<Model: cat_metodo_pago>>
    +codigo: str
    +nombre: str
    +requiere_pasarela: bool
    +activo: bool
  }
  class CatEstadoPedido {
    <<Model: cat_estado_pedido>>
    +codigo: str
    +nombre: str
    +restaura_stock: bool
    +activo: bool
  }
  class DetallePedido {
    <<Model: Orders_Details>>
    +Cantidad: int
    +Precio_Unitario: Decimal
    +Subtotal: Decimal
  }
  class Producto {
    <<Model: Products>>
    +Titulo: str
    +Precio: int
    +Stock: int
    +Fecha_Caducidad: date
  }
  class CatCategoria {
    <<Model: cat_categoria>>
    +codigo: str
    +nombre: str
    +animal: str
    +tema: str
    +perecedero: bool
    +activo: bool
  }
  class Usuario {
    <<Model: Users>>
    +Email: str
    +Username: str
    +Nombre: str
    +is_staff: bool
  }
  class Notificacion {
    <<Model: Notificaciones>>
    +Titulo: str
    +Mensaje: str
    +Tipo: str
    +Leida: bool
  }

  CrearPedidoView ..> CrearPedidoSerializer : valida con
  CrearPedidoSerializer *-- DetallePedidoSerializer : productos
  CrearPedidoView ..> pedidos_service : crear_pedido()
  ActualizarPedidoView ..> pedidos_service : actualizar_estado_pedido()
  CancelarPedidoView ..> pedidos_service : cancelar_pedido_usuario()
  MisPedidosView ..> pedidos_service : listar_pedidos_usuario()
  pedidos_service ..> Pedido : crea / actualiza
  pedidos_service ..> DetallePedido : crea
  pedidos_service ..> Producto : bloquea y actualiza Stock
  pedidos_service ..> Notificacion : crea avisos
  Usuario "1" --> "*" Pedido : realiza
  Pedido "*" --> "1" CatMetodoPago : metodo_pago
  Pedido "*" --> "1" CatEstadoPedido : estado
  Pedido "1" *-- "1..*" DetallePedido : contiene
  DetallePedido "*" --> "1" Producto : referencia
  Producto "*" --> "1" CatCategoria : pertenece a
  Notificacion "*" --> "1" Usuario : destinatario
  Notificacion "*" --> "0..1" Pedido : sobre
```

**Reglas implementadas en este nivel:**

1. `crear_pedido` se ejecuta dentro de `@transaction.atomic` y bloquea los productos con `select_for_update()`: si un producto no existe o no tiene stock suficiente, la transacción se revierte por completo.
2. El precio se toma de la base de datos (nunca del navegador), el método de pago y estado se resuelven contra `cat_metodo_pago` y `cat_estado_pedido`, y el total lo calcula el servidor.
3. Al crear el pedido se descuenta el stock y se notifica a los administradores.
4. `actualizar_estado_pedido` valida estados del catálogo (`Pendiente`, `Enviado`, `Entregado`, `Devuelto`, `Cancelado`); cuando transiciona a un estado con `restaura_stock=True` (`Devuelto` o `Cancelado`) sin haber restaurado previamente, reintegra el inventario y notifica al cliente.
5. `cancelar_pedido_usuario` permite al propietario cancelar únicamente pedidos en estado `Pendiente`, delegando en `actualizar_estado_pedido(..., 'cancelado')`.
