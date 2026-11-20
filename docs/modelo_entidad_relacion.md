# Miau Market — Modelo entidad-relación (MER)

**Autores:** Juan Camilo Barragán Pottes · Angely Liced Herrera Roldán

Esquema relacional completo y migraciones en [../Data Base/ESQUEMA_BD.md](../Data%20Base/ESQUEMA_BD.md). Diagrama visual en [MER.png](MER.png) y fuente MySQL Workbench en `DIAGRAMA MODELO ENTIDAD.mwb`.

---

## 1. Tablas del dominio

| Grupo | Tablas |
|-------|--------|
| Identidad y cliente | `Users`, `Mascotas_Usuario`, `Lista_Deseos` |
| Catálogos | `cat_categoria`, `cat_metodo_pago`, `cat_estado_pedido` |
| Tienda y operación | `Products`, `PaymentOrders`, `Orders_Details`, `Product_Reviews`, `Notificaciones` |
| Asistente MiauBot | `MiauBot_Config`, `MiauBot_Conocimiento`, `MiauBot_Frases`, `MiauBot_Aprendizaje`, `MiauBot_Memoria` |
| Vista SQL | `Product_Ratings` |

---

## 2. Relaciones y cardinalidades

| Relación | Cardinalidad | FK | Al borrar el padre |
|----------|--------------|----|--------------------|
| `Users` → `PaymentOrders` | 1 : N | `PaymentOrders.Id_User` | Se borran sus pedidos (`CASCADE`) |
| `PaymentOrders` → `Orders_Details` | 1 : N (mínimo 1) | `Orders_Details.Id_Factura` | Se borran los detalles (`CASCADE`) |
| `Products` → `Orders_Details` | 1 : N | `Orders_Details.Id_Products` | Se borran los detalles (`CASCADE`) |
| `cat_categoria` → `Products` | 1 : N | `Products.categoria_id` | **Prohibido** si tiene productos (`PROTECT`); se desactiva con `activo` |
| `cat_metodo_pago` → `PaymentOrders` | 1 : N | `PaymentOrders.metodo_pago_id` | **Prohibido** si tiene pedidos (`PROTECT`); se desactiva con `activo` |
| `cat_estado_pedido` → `PaymentOrders` | 1 : N | `PaymentOrders.estado_id` | **Prohibido** si tiene pedidos (`PROTECT`); se desactiva con `activo` |
| `Users` → `Products` | 0..1 : N | `Products.created_by` | Queda en `NULL` (`SET_NULL`) |
| `Users` → `Product_Reviews` | 1 : N | `Product_Reviews.Id_User` | Se borran sus reseñas (`CASCADE`) |
| `Products` → `Product_Reviews` | 1 : N | `Product_Reviews.Id_Products` | Se borran sus reseñas (`CASCADE`) |
| `Users` → `Lista_Deseos` | 1 : N | `Lista_Deseos.Id_User` | Se borran sus favoritos (`CASCADE`) |
| `Products` → `Lista_Deseos` | 1 : N | `Lista_Deseos.Id_Products` | Se borran de favoritos (`CASCADE`) |
| `Users` → `Mascotas_Usuario` | 1 : N | `Mascotas_Usuario.Id_User` | Se borran los perfiles de mascota (`CASCADE`) |
| `Users` → `Notificaciones` | 1 : N | `Notificaciones.Id_User` | Se borran sus notificaciones (`CASCADE`) |
| `PaymentOrders` → `Notificaciones` | 0..1 : N | `Notificaciones.Id_Factura` | Queda en `NULL` (`SET_NULL`) |
| `Users` → `MiauBot_Aprendizaje` | 0..1 : N | `MiauBot_Aprendizaje.usuario_id` | Queda en `NULL` (`SET_NULL`, conserva conocimiento) |
| `Users` → `MiauBot_Memoria` | 1 : 0..1 | `MiauBot_Memoria.usuario_id` (única) | Se borra la memoria (`CASCADE`) |

---

## 3. Restricciones e integridad

| Restricción | Tabla | Regla de negocio |
|-------------|-------|------------------|
| `Email` y `Username` únicos | `Users` | Una cuenta por correo y nombre de usuario (RF-01). |
| `codigo` y `nombre` únicos | `cat_categoria`, `cat_metodo_pago`, `cat_estado_pedido` | Catálogos sin duplicados (RF-06). |
| `uk_reviews_user_product` (`Id_User`, `Id_Products`) | `Product_Reviews` | Una reseña por usuario y producto (RN-08). |
| `uk_wishlist_user_product` (`Id_User`, `Id_Products`) | `Lista_Deseos` | Sin duplicados en favoritos por usuario. |
| `Rating` entre 1 y 5 | `Product_Reviews` | Validado en el modelo y el serializador (RF-15). |
| `usuario_id` único | `MiauBot_Memoria` | Memoria privada por usuario (RN-10). |
| `estado_id` ∈ `cat_estado_pedido` | `PaymentOrders` | Validado en `pedidos_service` (RF-25); `restaura_stock` controla reintegro automático. |
| `Stock` suficiente y precio tomado de BD | `Orders_Details` | Validado en `pedidos_service.crear_pedido` con `@transaction.atomic` y `select_for_update()` (RN-01, RN-02). |
| Edad 18 a 120 años | `Users` (`BirthDate`) | Validado en registro y edición de perfil (RN-07). |

---

## 4. Vista SQL

**`Product_Ratings`**: calcula por cada producto `Total_Reviews`, `Rating_Promedio` y el conteo por estrellas (`Reviews_5_Estrellas` … `Reviews_1_Estrella`) a partir de `Products LEFT JOIN Product_Reviews`. La utiliza `ratings_service` para mostrar calificaciones (RF-16).

*Nota sobre el diagrama visual:* `docs/MER.png` y `DIAGRAMA MODELO ENTIDAD.mwb` reflejan el núcleo transaccional inicial; las migraciones `0015`–`0018` incorporaron los catálogos (`cat_categoria`, `cat_metodo_pago`, `cat_estado_pedido`), `Lista_Deseos`, `Mascotas_Usuario` y llaves foráneas definitivas en `Notificaciones` y `MiauBot_*`.
