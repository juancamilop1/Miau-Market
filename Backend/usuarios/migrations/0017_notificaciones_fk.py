from django.db import migrations

# 0010 declaro estas FK solo en el estado de Django; la tabla quedo con enteros sueltos.


def agregar_fk(apps, schema_editor):
    Notificacion = apps.get_model('usuarios', 'Notificacion')
    Usuario = apps.get_model('usuarios', 'Usuario')
    Pedido = apps.get_model('usuarios', 'Pedido')

    Notificacion.objects.exclude(usuario_id__in=Usuario.objects.values('id')).delete()
    Notificacion.objects.filter(pedido_id__isnull=False).exclude(
        pedido_id__in=Pedido.objects.values('id')
    ).update(pedido_id=None)

    if schema_editor.connection.vendor == 'sqlite':
        schema_editor._remake_table(Notificacion)
        return

    for nombre in ('usuario', 'pedido'):
        campo = Notificacion._meta.get_field(nombre)
        schema_editor.execute(
            schema_editor._create_fk_sql(Notificacion, campo, '_fk_%(to_table)s_%(to_column)s')
        )


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ('usuarios', '0016_miaubot_fk_usuario'),
    ]

    operations = [
        migrations.RunPython(agregar_fk, migrations.RunPython.noop),
    ]
