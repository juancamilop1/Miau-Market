from django.db import migrations, models


META = {
    'comida_gato': {
        'codigo': 'COMIDA_GATO', 'icono': '🐱', 'animal': 'gato', 'tema': 'comida', 'perecedero': True, 'orden': 1,
    },
    'COMIDA_GATO': {
        'codigo': 'COMIDA_GATO', 'icono': '🐱', 'animal': 'gato', 'tema': 'comida', 'perecedero': True, 'orden': 1,
    },
    'comida_perro': {
        'codigo': 'COMIDA_PERRO', 'icono': '🐶', 'animal': 'perro', 'tema': 'comida', 'perecedero': True, 'orden': 2,
    },
    'COMIDA_PERRO': {
        'codigo': 'COMIDA_PERRO', 'icono': '🐶', 'animal': 'perro', 'tema': 'comida', 'perecedero': True, 'orden': 2,
    },
    'juguetes': {
        'codigo': 'JUGUETES', 'icono': '🧸', 'animal': 'general', 'tema': 'juguete', 'perecedero': False, 'orden': 3,
    },
    'JUGUETES': {
        'codigo': 'JUGUETES', 'icono': '🧸', 'animal': 'general', 'tema': 'juguete', 'perecedero': False, 'orden': 3,
    },
    'accesorios': {
        'codigo': 'ACCESORIOS', 'icono': '🦴', 'animal': 'general', 'tema': 'accesorio', 'perecedero': False, 'orden': 4,
    },
    'ACCESORIOS': {
        'codigo': 'ACCESORIOS', 'icono': '🦴', 'animal': 'general', 'tema': 'accesorio', 'perecedero': False, 'orden': 4,
    },
    'servicios': {
        'codigo': 'SERVICIOS', 'icono': '🩺', 'animal': 'general', 'tema': 'salud', 'perecedero': False, 'orden': 5,
    },
    'SERVICIOS': {
        'codigo': 'SERVICIOS', 'icono': '🩺', 'animal': 'general', 'tema': 'salud', 'perecedero': False, 'orden': 5,
    },
    'higiene': {
        'codigo': 'HIGIENE', 'icono': '🧴', 'animal': 'general', 'tema': 'higiene', 'perecedero': False, 'orden': 6,
    },
    'HIGIENE': {
        'codigo': 'HIGIENE', 'icono': '🧴', 'animal': 'general', 'tema': 'higiene', 'perecedero': False, 'orden': 6,
    },
    'farmacia': {
        'codigo': 'FARMACIA', 'icono': '💊', 'animal': 'general', 'tema': 'salud', 'perecedero': False, 'orden': 7,
    },
    'FARMACIA': {
        'codigo': 'FARMACIA', 'icono': '💊', 'animal': 'general', 'tema': 'salud', 'perecedero': False, 'orden': 7,
    },
}


def enriquecer_categorias(apps, schema_editor):
    CatCategoria = apps.get_model('usuarios', 'CatCategoria')
    Producto = apps.get_model('usuarios', 'Producto')
    vistos = set()
    for cat in list(CatCategoria.objects.all()):
        meta = META.get(cat.codigo)
        if not meta:
            continue
        destino = meta['codigo']
        if destino != cat.codigo and CatCategoria.objects.filter(codigo=destino).exclude(pk=cat.pk).exists():
            canon = CatCategoria.objects.get(codigo=destino)
            Producto.objects.filter(categoria_id=cat.id).update(categoria_id=canon.id)
            cat.delete()
            continue
        cat.codigo = destino
        cat.icono = meta['icono']
        cat.animal = meta['animal']
        cat.tema = meta['tema']
        cat.perecedero = meta['perecedero']
        cat.orden = meta['orden']
        cat.save()
        vistos.add(destino)


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0017_notificaciones_fk'),
    ]

    operations = [
        migrations.AddField(
            model_name='catcategoria',
            name='icono',
            field=models.CharField(blank=True, default='', max_length=8),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='catcategoria',
            name='animal',
            field=models.CharField(
                choices=[('gato', 'Gato'), ('perro', 'Perro'), ('general', 'General')],
                default='general',
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name='catcategoria',
            name='tema',
            field=models.CharField(
                choices=[
                    ('comida', 'Comida'),
                    ('juguete', 'Juguete'),
                    ('accesorio', 'Accesorio'),
                    ('higiene', 'Higiene'),
                    ('salud', 'Salud'),
                    ('servicio', 'Servicio'),
                    ('general', 'General'),
                ],
                default='general',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='catcategoria',
            name='perecedero',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(enriquecer_categorias, migrations.RunPython.noop),
    ]
