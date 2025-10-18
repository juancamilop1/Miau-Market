-- Eliminación de tablas si existen para evitar conflictos
DROP TABLE IF EXISTS Orders_Details;
DROP TABLE IF EXISTS PaymentOrders;
DROP TABLE IF EXISTS Products;
DROP TABLE IF EXISTS auth_group_permissions;
DROP TABLE IF EXISTS auth_user_groups;
DROP TABLE IF EXISTS auth_user_permissions;
DROP TABLE IF EXISTS auth_group;
DROP TABLE IF EXISTS auth_permission;
DROP TABLE IF EXISTS Users;

-- Tabla Users con campos adicionales para Django (manteniendo el nombre original)
CREATE TABLE Users (
    Id_User INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Apellido VARCHAR(100) NOT NULL,
    Email VARCHAR(150) UNIQUE NOT NULL,
    Telefono VARCHAR(20),
    Address VARCHAR(40) NOT NULL,
    City VARCHAR(40) NOT NULL,
    BirthDate DATE NOT NULL,
    FechaRegistro DATETIME DEFAULT CURRENT_TIMESTAMP,
    password VARCHAR(128) NOT NULL,  -- Campo para almacenar el hash de la contraseña
    is_active BOOLEAN DEFAULT TRUE,  -- Campo requerido por Django
    is_staff BOOLEAN DEFAULT FALSE,  -- Campo para acceso al admin
    is_superuser BOOLEAN DEFAULT FALSE,  -- Campo para permisos de superusuario
    last_login DATETIME DEFAULT NULL  -- Campo para último inicio de sesión
);

-- Tabla de Productos (nombre original)
CREATE TABLE Products (
    Id_Products INT AUTO_INCREMENT PRIMARY KEY,
    Titulo VARCHAR(150) NOT NULL,
    Descripcion TEXT,
    Categoria VARCHAR(100),
    Precio DECIMAL(10,2) NOT NULL,
    Stock INT NOT NULL DEFAULT 0,
    Fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT,  -- Campo para rastrear quién creó el producto
    FOREIGN KEY (created_by) REFERENCES Users(Id_User)
);

-- Tabla de Órdenes de Pago (nombre original)
CREATE TABLE PaymentOrders (
    Id_Factura INT AUTO_INCREMENT PRIMARY KEY,
    Id_User INT NOT NULL,
    Fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    Total DECIMAL(10,2) NOT NULL,
    Metodo_Pago VARCHAR(50),
    Estado VARCHAR(50) DEFAULT 'Enviado',
    FOREIGN KEY (Id_User) REFERENCES Users(Id_User)
);

-- Tabla de Detalles de Órdenes (nombre original)
CREATE TABLE Orders_Details (
    Id_Detalle INT AUTO_INCREMENT PRIMARY KEY,
    Id_Factura INT NOT NULL,
    Id_Products INT NOT NULL,
    Cantidad INT NOT NULL,
    Precio_Unitario DECIMAL(10,2) NOT NULL,
    Subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (Id_Factura) REFERENCES PaymentOrders(Id_Factura),
    FOREIGN KEY (Id_Products) REFERENCES Products(Id_Products)
);

-- Tablas de autenticación de Django con nombres estándar
CREATE TABLE auth_group (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE auth_permission (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    content_type_id INT NOT NULL,
    codename VARCHAR(100) NOT NULL
);

CREATE TABLE auth_user_groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    group_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(Id_User),
    FOREIGN KEY (group_id) REFERENCES auth_group(id)
);

CREATE TABLE auth_user_permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    permission_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(Id_User),
    FOREIGN KEY (permission_id) REFERENCES auth_permission(id)
);

CREATE TABLE auth_group_permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT NOT NULL,
    permission_id INT NOT NULL,
    FOREIGN KEY (group_id) REFERENCES auth_group(id),
    FOREIGN KEY (permission_id) REFERENCES auth_permission(id)
);

-- Índices para mejorar el rendimiento
CREATE INDEX idx_users_email ON Users(Email);
CREATE INDEX idx_products_categoria ON Products(Categoria);
CREATE INDEX idx_paymentorders_estado ON PaymentOrders(Estado);
CREATE INDEX idx_paymentorders_user ON PaymentOrders(Id_User);