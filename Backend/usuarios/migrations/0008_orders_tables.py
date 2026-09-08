from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0007_paymentorders_shipping_columns'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS PaymentOrders (
                    Id_Factura INT AUTO_INCREMENT PRIMARY KEY,
                    Id_User INT NOT NULL,
                    Fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
                    Total DECIMAL(10,2) NOT NULL,
                    Metodo_Pago VARCHAR(50),
                    Estado VARCHAR(50) DEFAULT 'Pendiente',
                    Direccion_Envio VARCHAR(200),
                    Telefono_Envio VARCHAR(20),
                    CONSTRAINT fk_paymentorders_user
                        FOREIGN KEY (Id_User) REFERENCES Users(Id_User)
                        ON UPDATE CASCADE ON DELETE RESTRICT
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

                CREATE TABLE IF NOT EXISTS Orders_Details (
                    Id_Detalle INT AUTO_INCREMENT PRIMARY KEY,
                    Id_Factura INT NOT NULL,
                    Id_Products INT NOT NULL,
                    Cantidad INT NOT NULL,
                    Precio_Unitario DECIMAL(10,2) NOT NULL,
                    Subtotal DECIMAL(10,2) NOT NULL,
                    CONSTRAINT fk_orders_details_factura
                        FOREIGN KEY (Id_Factura) REFERENCES PaymentOrders(Id_Factura)
                        ON UPDATE CASCADE ON DELETE CASCADE,
                    CONSTRAINT fk_orders_details_product
                        FOREIGN KEY (Id_Products) REFERENCES Products(Id_Products)
                        ON UPDATE CASCADE ON DELETE RESTRICT
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """,
            reverse_sql="""
                DROP TABLE IF EXISTS Orders_Details;
                DROP TABLE IF EXISTS PaymentOrders;
            """,
        ),
    ]
