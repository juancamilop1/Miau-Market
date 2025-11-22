-- Tabla de Reseñas y Calificaciones de Productos
-- Ejecutar esto en tu base de datos MariaDB

-- Seleccionar la base de datos (cambia 'miau_market' por el nombre de tu base de datos)
USE railway;

CREATE TABLE IF NOT EXISTS Product_Reviews (
    Id_Review INT AUTO_INCREMENT PRIMARY KEY,
    Id_Products INT NOT NULL,
    Id_User INT NOT NULL,
    Rating TINYINT NOT NULL CHECK (Rating >= 1 AND Rating <= 5),
    Comentario TEXT,
    Fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Id_Products) REFERENCES Products(Id_Products) ON DELETE CASCADE,
    FOREIGN KEY (Id_User) REFERENCES Users(Id_User) ON DELETE CASCADE,
    UNIQUE KEY unique_user_product (Id_User, Id_Products)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Índices para mejorar rendimiento
CREATE INDEX idx_product_reviews ON Product_Reviews(Id_Products);
CREATE INDEX idx_user_reviews ON Product_Reviews(Id_User);
CREATE INDEX idx_rating ON Product_Reviews(Rating);
CREATE INDEX idx_fecha ON Product_Reviews(Fecha DESC);

-- Vista para obtener calificación promedio por producto
CREATE OR REPLACE VIEW Product_Ratings AS
SELECT 
    p.Id_Products,
    p.Titulo,
    COUNT(r.Id_Review) AS Total_Reviews,
    COALESCE(AVG(r.Rating), 0) AS Rating_Promedio,
    COALESCE(SUM(CASE WHEN r.Rating = 5 THEN 1 ELSE 0 END), 0) AS Reviews_5_Estrellas,
    COALESCE(SUM(CASE WHEN r.Rating = 4 THEN 1 ELSE 0 END), 0) AS Reviews_4_Estrellas,
    COALESCE(SUM(CASE WHEN r.Rating = 3 THEN 1 ELSE 0 END), 0) AS Reviews_3_Estrellas,
    COALESCE(SUM(CASE WHEN r.Rating = 2 THEN 1 ELSE 0 END), 0) AS Reviews_2_Estrellas,
    COALESCE(SUM(CASE WHEN r.Rating = 1 THEN 1 ELSE 0 END), 0) AS Reviews_1_Estrella
FROM Products p
LEFT JOIN Product_Reviews r ON p.Id_Products = r.Id_Products
GROUP BY p.Id_Products, p.Titulo;
