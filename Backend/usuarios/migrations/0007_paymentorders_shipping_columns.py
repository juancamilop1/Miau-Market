from django.db import migrations


class Migration(migrations.Migration):
    """
    Supersedida por 0008_orders_tables (columnas de envio incluidas al crear la tabla).
    Se mantiene vacia para no romper historial de migraciones ya aplicadas.
    """

    dependencies = [
        ('usuarios', '0006_notificacion'),
    ]

    operations = []
