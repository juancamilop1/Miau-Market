from django.db import migrations, models
import django.db.models.deletion


CATEGORIAS = [
    ('comida_gato', 'Comida de Gato', 1),
    ('comida_perro', 'Comida de Perro', 2),
    ('juguetes', 'Juguetes', 3),
    ('servicios', 'Servicios', 4),
    ('higiene', 'Higiene', 5),
    ('accesorios', 'Accesorios', 6),
    ('farmacia', 'Farmacia', 7),
]

METODOS = [
    ('contra_entrega', 'Contra Entrega', False, 1),
    ('transferencia', 'Transferencia', False, 2),
    ('nequi', 'Nequi', False, 3),
    ('pse', 'PSE', True, 4),
]

ESTADOS = [
    ('pendiente', 'Pendiente', False, 1),
    ('enviado', 'Enviado', False, 2),
    ('entregado', 'Entregado', False, 3),
    ('devuelto', 'Devuelto', True, 4),
    ('cancelado', 'Cancelado', True, 5),
]


def seed_catalogos(apps, schema_editor):
    CatCategoria = apps.get_model('usuarios', 'CatCategoria')
    CatMetodoPago = apps.get_model('usuarios', 'CatMetodoPago')
    CatEstadoPedido = apps.get_model('usuarios', 'CatEstadoPedido')
    Producto = apps.get_model('usuarios', 'Producto')
    Pedido = apps.get_model('usuarios', 'Pedido')

    for codigo, nombre, orden in CATEGORIAS:
        CatCategoria.objects.update_or_create(
            codigo=codigo,
            defaults={'nombre': nombre, 'activo': True, 'orden': orden},
        )
    for codigo, nombre, pasarela, orden in METODOS:
        CatMetodoPago.objects.update_or_create(
            codigo=codigo,
            defaults={
                'nombre': nombre,
                'activo': True,
                'requiere_pasarela': pasarela,
                'orden': orden,
            },
        )
    for codigo, nombre, restaura, orden in ESTADOS:
        CatEstadoPedido.objects.update_or_create(
            codigo=codigo,
            defaults={
                'nombre': nombre,
                'activo': True,
                'restaura_stock': restaura,
                'orden': orden,
            },
        )

    cats = {c.nombre: c for c in CatCategoria.objects.all()}
    for producto in Producto.objects.all():
        nombre = (producto.Categoria or '').strip()
        cat = cats.get(nombre)
        if cat:
            producto.categoria_id = cat.id
            producto.save(update_fields=['categoria_id'])

    metodos = {m.nombre: m for m in CatMetodoPago.objects.all()}
    estados = {e.nombre: e for e in CatEstadoPedido.objects.all()}
    for pedido in Pedido.objects.all():
        updates = []
        metodo = metodos.get((pedido.Metodo_Pago or '').strip())
        estado = estados.get((pedido.Estado or '').strip())
        if metodo:
            pedido.metodo_pago_id = metodo.id
            updates.append('metodo_pago_id')
        if estado:
            pedido.estado_id = estado.id
            updates.append('estado_id')
        if updates:
            pedido.save(update_fields=updates)


def add_fk_columns(apps, schema_editor):
    """TiDB no soporta bien ADD COLUMN + FK en un solo ALTER de Django."""
    stmts = [
        'ALTER TABLE Products ADD COLUMN categoria_id BIGINT NULL',
        'ALTER TABLE PaymentOrders ADD COLUMN metodo_pago_id BIGINT NULL',
        'ALTER TABLE PaymentOrders ADD COLUMN estado_id BIGINT NULL',
        'CREATE INDEX Products_categoria_id_idx ON Products (categoria_id)',
        'CREATE INDEX PaymentOrders_metodo_pago_id_idx ON PaymentOrders (metodo_pago_id)',
        'CREATE INDEX PaymentOrders_estado_id_idx ON PaymentOrders (estado_id)',
    ]
    for sql in stmts:
        try:
            schema_editor.execute(sql)
        except Exception:
            # Idempotente si la columna/indice ya existe
            pass


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ('usuarios', '0014_miaubot_memoria'),
    ]

    operations = [
        migrations.CreateModel(
            name='CatCategoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=40, unique=True)),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('activo', models.BooleanField(default=True)),
                ('orden', models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                'db_table': 'cat_categoria',
                'ordering': ['orden', 'nombre'],
            },
        ),
        migrations.CreateModel(
            name='CatMetodoPago',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=40, unique=True)),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('activo', models.BooleanField(default=True)),
                ('requiere_pasarela', models.BooleanField(default=False)),
                ('orden', models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                'db_table': 'cat_metodo_pago',
                'ordering': ['orden', 'nombre'],
            },
        ),
        migrations.CreateModel(
            name='CatEstadoPedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=40, unique=True)),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('activo', models.BooleanField(default=True)),
                ('restaura_stock', models.BooleanField(default=False)),
                ('orden', models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                'db_table': 'cat_estado_pedido',
                'ordering': ['orden', 'nombre'],
            },
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(add_fk_columns, migrations.RunPython.noop),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='producto',
                    name='categoria',
                    field=models.ForeignKey(
                        blank=True,
                        db_column='categoria_id',
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='productos',
                        to='usuarios.catcategoria',
                    ),
                ),
                migrations.AddField(
                    model_name='pedido',
                    name='metodo_pago',
                    field=models.ForeignKey(
                        blank=True,
                        db_column='metodo_pago_id',
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='pedidos',
                        to='usuarios.catmetodopago',
                    ),
                ),
                migrations.AddField(
                    model_name='pedido',
                    name='estado',
                    field=models.ForeignKey(
                        blank=True,
                        db_column='estado_id',
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='pedidos',
                        to='usuarios.catestadopedido',
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='ListaDeseos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Fecha_Creacion', models.DateTimeField(auto_now_add=True)),
                ('producto', models.ForeignKey(
                    db_column='Id_Products',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='en_listas_deseos',
                    to='usuarios.producto',
                )),
                ('usuario', models.ForeignKey(
                    db_column='Id_User',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='lista_deseos',
                    to='usuarios.usuario',
                )),
            ],
            options={
                'db_table': 'Lista_Deseos',
            },
        ),
        migrations.CreateModel(
            name='MascotaUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=80)),
                ('especie', models.CharField(
                    choices=[('gato', 'Gato'), ('perro', 'Perro'), ('otro', 'Otro')],
                    default='gato',
                    max_length=20,
                )),
                ('edad_anios', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('notas', models.TextField(blank=True)),
                ('activo', models.BooleanField(default=True)),
                ('Fecha_Creacion', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(
                    db_column='Id_User',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='mascotas',
                    to='usuarios.usuario',
                )),
            ],
            options={
                'db_table': 'Mascotas_Usuario',
                'ordering': ['nombre'],
            },
        ),
        migrations.AddConstraint(
            model_name='listadeseos',
            constraint=models.UniqueConstraint(
                fields=('usuario', 'producto'),
                name='uk_wishlist_user_product',
            ),
        ),
        migrations.RunPython(seed_catalogos, migrations.RunPython.noop),
    ]
