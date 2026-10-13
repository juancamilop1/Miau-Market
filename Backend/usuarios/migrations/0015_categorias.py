import importlib
import re
import unicodedata

from django.db import migrations, models
import django.db.models.deletion

VIEW_SQL = importlib.import_module('usuarios.migrations.0009_reviews_tables').VIEW_SQL


# SQLite reconstruye Products al cambiar columnas y falla si la vista depende de ella.
def quitar_vista(apps, schema_editor):
    if schema_editor.connection.vendor == 'sqlite':
        schema_editor.execute('DROP VIEW IF EXISTS Product_Ratings;')


def crear_vista(apps, schema_editor):
    if schema_editor.connection.vendor == 'sqlite':
        schema_editor.execute(VIEW_SQL)


CATEGORIAS = [
    # Codigo, Nombre, Icono, Animal, Tema, Perecedero, Orden
    ('COMIDA_GATO', 'Comida de Gato', '🐱', 'gato', 'comida', True, 1),
    ('COMIDA_PERRO', 'Comida de Perro', '🐶', 'perro', 'comida', True, 2),
    ('JUGUETES', 'Juguetes', '🧸', 'general', 'juguete', False, 3),
    ('ACCESORIOS', 'Accesorios', '🦴', 'general', 'accesorio', False, 4),
    ('SERVICIOS', 'Productos útiles', '🩺', 'general', 'salud', False, 5),
]

# Textos libres usados antes de la tabla Categories -> Codigo canonico.
ALIAS = {
    'comida de gato': 'COMIDA_GATO',
    'comida gato': 'COMIDA_GATO',
    'comida de perro': 'COMIDA_PERRO',
    'comida perro': 'COMIDA_PERRO',
    'juguetes': 'JUGUETES',
    'juguete': 'JUGUETES',
    'accesorios': 'ACCESORIOS',
    'accesorio': 'ACCESORIOS',
    'servicios': 'SERVICIOS',
    'servicio': 'SERVICIOS',
    'productos utiles': 'SERVICIOS',
}


def _normalizar(texto):
    texto = unicodedata.normalize('NFKD', texto or '').encode('ascii', 'ignore').decode()
    return re.sub(r'\s+', ' ', texto).strip().lower()


def poblar_categorias(apps, schema_editor):
    Categoria = apps.get_model('usuarios', 'Categoria')
    Producto = apps.get_model('usuarios', 'Producto')

    por_codigo = {}
    for codigo, nombre, icono, animal, tema, perecedero, orden in CATEGORIAS:
        por_codigo[codigo], _ = Categoria.objects.get_or_create(
            Codigo=codigo,
            defaults={
                'Nombre': nombre, 'Icono': icono, 'Animal': animal, 'Tema': tema,
                'Perecedero': perecedero, 'Orden': orden,
            },
        )

    siguiente_orden = len(CATEGORIAS) + 1
    for producto in Producto.objects.all():
        texto = _normalizar(producto.Categoria)
        codigo = ALIAS.get(texto)
        if codigo is None:
            texto_original = (producto.Categoria or '').strip() or 'General'
            codigo = re.sub(r'[^A-Z0-9]+', '_', _normalizar(texto_original).upper()).strip('_')[:30] or 'GENERAL'
            if codigo not in por_codigo:
                por_codigo[codigo], _ = Categoria.objects.get_or_create(
                    Codigo=codigo,
                    defaults={
                        'Nombre': texto_original[:100],
                        'Perecedero': 'comida' in texto,
                        'Tema': 'comida' if 'comida' in texto else 'general',
                        'Orden': siguiente_orden,
                    },
                )
                siguiente_orden += 1
        producto.categoria = por_codigo[codigo]
        producto.save(update_fields=['categoria'])


def restaurar_texto(apps, schema_editor):
    Producto = apps.get_model('usuarios', 'Producto')
    for producto in Producto.objects.select_related('categoria'):
        producto.Categoria = producto.categoria.Nombre if producto.categoria_id else None
        producto.save(update_fields=['Categoria'])


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0014_miaubot_memoria'),
    ]

    operations = [
        migrations.RunPython(quitar_vista, crear_vista),
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.AutoField(db_column='Id_Category', primary_key=True, serialize=False)),
                ('Codigo', models.CharField(max_length=30, unique=True)),
                ('Nombre', models.CharField(max_length=100, unique=True)),
                ('Icono', models.CharField(blank=True, max_length=8)),
                ('Animal', models.CharField(choices=[('gato', 'Gato'), ('perro', 'Perro'), ('general', 'General')], default='general', max_length=10)),
                ('Tema', models.CharField(choices=[('comida', 'Comida'), ('juguete', 'Juguete'), ('accesorio', 'Accesorio'), ('higiene', 'Higiene'), ('salud', 'Salud'), ('servicio', 'Servicio'), ('general', 'General')], default='general', max_length=20)),
                ('Perecedero', models.BooleanField(default=False)),
                ('Orden', models.PositiveSmallIntegerField(default=0)),
                ('Activo', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'Categories',
                'ordering': ['Orden', 'Nombre'],
            },
        ),
        migrations.AddField(
            model_name='producto',
            name='categoria',
            field=models.ForeignKey(db_column='Id_Category', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='productos', to='usuarios.categoria'),
        ),
        migrations.RunPython(poblar_categorias, restaurar_texto),
        migrations.RemoveField(
            model_name='producto',
            name='Categoria',
        ),
        migrations.AlterField(
            model_name='producto',
            name='categoria',
            field=models.ForeignKey(db_column='Id_Category', on_delete=django.db.models.deletion.PROTECT, related_name='productos', to='usuarios.categoria'),
        ),
        migrations.RunPython(crear_vista, quitar_vista),
    ]
