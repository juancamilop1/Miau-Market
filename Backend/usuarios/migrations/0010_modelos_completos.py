from django.db import migrations, models
import django.db.models.deletion
from django.core.validators import MinValueValidator, MaxValueValidator


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0009_reviews_tables'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='Pedido',
                    fields=[
                        ('id', models.AutoField(db_column='Id_Factura', primary_key=True, serialize=False)),
                        ('Fecha', models.DateTimeField(auto_now_add=True)),
                        ('Total', models.DecimalField(decimal_places=2, max_digits=10)),
                        ('Metodo_Pago', models.CharField(blank=True, max_length=50)),
                        ('Estado', models.CharField(default='Pendiente', max_length=50)),
                        ('Direccion_Envio', models.CharField(blank=True, max_length=200)),
                        ('Telefono_Envio', models.CharField(blank=True, max_length=20)),
                        ('usuario', models.ForeignKey(
                            db_column='Id_User',
                            on_delete=django.db.models.deletion.CASCADE,
                            related_name='pedidos',
                            to='usuarios.usuario',
                        )),
                    ],
                    options={
                        'db_table': 'PaymentOrders',
                        'ordering': ['-Fecha'],
                    },
                ),
                migrations.CreateModel(
                    name='DetallePedido',
                    fields=[
                        ('id', models.AutoField(db_column='Id_Detalle', primary_key=True, serialize=False)),
                        ('Cantidad', models.IntegerField()),
                        ('Precio_Unitario', models.DecimalField(decimal_places=2, max_digits=10)),
                        ('Subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                        ('pedido', models.ForeignKey(
                            db_column='Id_Factura',
                            on_delete=django.db.models.deletion.CASCADE,
                            related_name='detalles',
                            to='usuarios.pedido',
                        )),
                        ('producto', models.ForeignKey(
                            db_column='Id_Products',
                            on_delete=django.db.models.deletion.CASCADE,
                            to='usuarios.producto',
                        )),
                    ],
                    options={
                        'db_table': 'Orders_Details',
                    },
                ),
                migrations.CreateModel(
                    name='ResenaProducto',
                    fields=[
                        ('id', models.AutoField(db_column='Id_Review', primary_key=True, serialize=False)),
                        ('Rating', models.PositiveSmallIntegerField(
                            validators=[MinValueValidator(1), MaxValueValidator(5)],
                        )),
                        ('Comentario', models.TextField(blank=True)),
                        ('Fecha', models.DateTimeField(auto_now_add=True)),
                        ('producto', models.ForeignKey(
                            db_column='Id_Products',
                            on_delete=django.db.models.deletion.CASCADE,
                            related_name='resenas',
                            to='usuarios.producto',
                        )),
                        ('usuario', models.ForeignKey(
                            db_column='Id_User',
                            on_delete=django.db.models.deletion.CASCADE,
                            related_name='resenas',
                            to='usuarios.usuario',
                        )),
                    ],
                    options={
                        'db_table': 'Product_Reviews',
                    },
                ),
                migrations.AddConstraint(
                    model_name='resenaproducto',
                    constraint=models.UniqueConstraint(
                        fields=('usuario', 'producto'),
                        name='uk_reviews_user_product',
                    ),
                ),
                migrations.RemoveField(model_name='notificacion', name='Id_User'),
                migrations.RemoveField(model_name='notificacion', name='Id_Factura'),
                migrations.AddField(
                    model_name='notificacion',
                    name='usuario',
                    field=models.ForeignKey(
                        db_column='Id_User',
                        default=1,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='notificaciones',
                        to='usuarios.usuario',
                    ),
                    preserve_default=False,
                ),
                migrations.AddField(
                    model_name='notificacion',
                    name='pedido',
                    field=models.ForeignKey(
                        blank=True,
                        db_column='Id_Factura',
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to='usuarios.pedido',
                    ),
                ),
            ],
            database_operations=[
                migrations.RunSQL(
                    sql="""
                        CREATE TABLE IF NOT EXISTS authtoken_token (
                            `key` VARCHAR(40) NOT NULL PRIMARY KEY,
                            created DATETIME(6) NOT NULL,
                            user_id INT NOT NULL,
                            UNIQUE KEY authtoken_token_user_id_key (user_id),
                            CONSTRAINT authtoken_token_user_id_fk
                                FOREIGN KEY (user_id) REFERENCES Users(Id_User)
                                ON DELETE CASCADE
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                    """,
                    reverse_sql="DROP TABLE IF EXISTS authtoken_token;",
                ),
            ],
        ),
    ]
