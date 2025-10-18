--Tablas Usuarios
CREATE TABLE Users (
    Id_User INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Apellido VARCHAR(100) NOT NULL,
    Email VARCHAR(150) UNIQUE,
    Telefono VARCHAR(20),
    Address VARCHAR(40) NOT NULL,
    City VARCHAR(40) NOT NULL,
    BirthDate DATE NOT NULL,
    FechaRegistro DATETIME DEFAULT CURRENT_TIMESTAMP
);

--Tablas Productos
CREATE TABLE Products (
    Id_Products INT AUTO_INCREMENT PRIMARY KEY,
    Titulo VARCHAR(150) NOT NULL,
    Descripcion TEXT,
    Categoria VARCHAR(100),
    Precio DECIMAL(10,2) NOT NULL,
    Stock INT NOT NULL DEFAULT 0,
    Fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
);

--Relacion de Facturación con la Tabla de Users
CREATE TABLE PaymentOrders (
    Id_Factura INT AUTO_INCREMENT PRIMARY KEY,
    Id_User INT NOT NULL,
    Fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    Total DECIMAL(10,2) NOT NULL,
    Metodo_Pago VARCHAR(50),
    Estado VARCHAR(50) DEFAULT 'Enviado',
    FOREIGN KEY (Id_User) REFERENCES Users(Id_User)
);

-- Detalles de factura vinculada con las tablas(PaymentOrders,Products)
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

--Pendiente validacion de tabla de roles para los usuarios 
--que pueden tener permisos de modificacion sobre los productos 