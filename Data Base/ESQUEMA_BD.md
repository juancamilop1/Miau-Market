# Esquema de base de datos — Miau Market

Patron alineado con **ROADEX / bia-system**: SQL versionado, credenciales en `.env`, migraciones incrementales y documentacion junto al codigo.

---

## Stack

| Capa | Tecnologia |
|------|------------|
| Motor | MySQL 8+ / MariaDB 10.4+ |
| ORM | Django (Users, Products, Notificaciones, Pedidos, Resenas) |
| Servicios | pedidos_service, ratings_service |
| Charset | utf8mb4 / utf8mb4_unicode_ci |
| Engine | InnoDB |

---

## Diagrama de relaciones

```
Users ──< Products (created_by)
Users ──< PaymentOrders
Users ──< Product_Reviews
Users ──< Notificaciones

PaymentOrders ──< Orders_Details
Products ──< Orders_Details
Products ──< Product_Reviews

Product_Ratings (VISTA sobre Products + Product_Reviews)
```

---

## Tablas y responsabilidad

| Tabla | Gestionada por | Descripcion |
|-------|----------------|-------------|
| `Users` | Django ORM | Usuarios (AUTH_USER_MODEL) |
| `Products` | Django ORM | Catalogo de productos |
| `Notificaciones` | Django ORM | Alertas de pedidos y caducidad |
| `PaymentOrders` | Django ORM | Cabecera de pedidos |
| `Orders_Details` | Django ORM | Lineas de pedido |
| `Product_Reviews` | Django ORM | Resenas por producto |
| `Product_Ratings` | Vista SQL (opcional) | Promedio de calificaciones |
| `django_*`, `authtoken_*` | Django migrate | Framework y tokens |

---

## Campos clave

### Users
| Campo | Tipo | Notas |
|-------|------|-------|
| Id_User | INT PK | Auto |
| Email | VARCHAR(150) UNIQUE | Login (USERNAME_FIELD) |
| Telefono | VARCHAR(20) NOT NULL | Solo numeros |
| is_staff | BOOLEAN | Acceso admin panel |

### Products
| Campo | Tipo | Notas |
|-------|------|-------|
| Precio | INT | Pesos COP (entero, sin decimales) |
| Fecha_Caducidad | DATE | Obligatorio |
| Imagen | VARCHAR(255) | Ruta en /media/productos/ |

### PaymentOrders
| Campo | Tipo | Notas |
|-------|------|-------|
| Estado | VARCHAR(50) | Default `Pendiente` |
| Direccion_Envio | VARCHAR(200) | Envio |
| Telefono_Envio | VARCHAR(20) | Contacto entrega |

---

## Convenciones de nombres (estilo ROADEX)

| Elemento | Patron | Ejemplo |
|----------|--------|---------|
| Tablas negocio | PascalCase historico | `PaymentOrders`, `Users` |
| Indices | `idx_<tabla>_<columna>` | `idx_paymentorders_user` |
| FK | `fk_<tabla>_<ref>` | `fk_orders_details_factura` |
| Unique | `uk_<tabla>_<columnas>` | `uk_reviews_user_product` |
| Scripts base | `Tables.sql`, `Reviews.sql` | En `Data Base/sql/` |
| Scripts incrementales | `alter_<feature>.sql` | Futuras evoluciones |

---

## Instalacion (recomendada — Django-first)

### 1. Configurar entorno

```powershell
cd Backend
copy .env.example .env
# Editar .env con DB_PASSWORD y demas valores
pip install -r requirements.txt
```

### 2. Crear base de datos

```powershell
mysql -u root -p < "../Data Base/sql/00_database.sql"
```

### 3. Aplicar migraciones Django (crea Users, Products, Notificaciones, pedidos, resenas)

```powershell
python manage.py migrate
```

### 4. Verificar conexion

```powershell
python scripts/verificar_conexion.py
```

### 5. Crear administrador

```powershell
python manage.py make_admin --bootstrap
```

---

## Instalacion alternativa (SQL manual)

Si prefieres ejecutar SQL en Workbench despues de `migrate`:

```text
1. sql/00_database.sql
2. python manage.py migrate
3. sql/Tables.sql      (solo si migrate no creo pedidos)
4. sql/Reviews.sql     (solo si migrate no creo resenas)
```

No mezclar scripts SQL manuales con `migrate` salvo instalacion alternativa abajo.

---

## Inicio rapido (Windows)

Doble clic en `iniciar_miau_market.bat` en la raiz del proyecto. El script:

1. Crea/activa el entorno virtual Python
2. Copia `.env.example` si falta `.env`
3. Instala dependencias y ejecuta `migrate`
4. Abre backend (8000) y frontend (4200) en ventanas separadas

## Archivos SQL

| Archivo | Proposito |
|---------|-----------|
| `sql/00_database.sql` | CREATE DATABASE + USE |
| `sql/Tables.sql` | PaymentOrders, Orders_Details |
| `sql/Reviews.sql` | Product_Reviews + vista Product_Ratings |

---

## Migraciones Django

| Migracion | Cambio |
|-----------|--------|
| 0001–0006 | Users, Products, Notificaciones |
| 0007 | Columnas envio en PaymentOrders |
| 0008 | Tablas de pedidos (IF NOT EXISTS) |
| 0009 | Resenas + vista Product_Ratings |
| 0010 | Modelos ORM completos + authtoken_token |

---

## Seguridad

- Credenciales en `Backend/.env` (nunca en git)
- Plantilla en `Backend/.env.example`
- Rotar claves si estuvieron expuestas en commits anteriores
- `GEMINI_API_KEY` solo via entorno

---

## Mantenimiento

```powershell
# Nueva columna / cambio de esquema
python manage.py makemigrations
python manage.py migrate

# O script incremental (estilo ROADEX)
# Data Base/sql/alter_<feature>.sql
```

Siempre documentar cambios en este archivo y en la migracion correspondiente.
