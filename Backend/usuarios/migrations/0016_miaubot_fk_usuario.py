from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def limpiar_huerfanos(apps, schema_editor):
    Usuario = apps.get_model('usuarios', 'Usuario')
    Aprendizaje = apps.get_model('usuarios', 'MiauBotAprendizaje')
    Memoria = apps.get_model('usuarios', 'MiauBotMemoriaUsuario')
    ids_validos = set(Usuario.objects.values_list('id', flat=True))
    Aprendizaje.objects.exclude(usuario_id__isnull=True).exclude(usuario_id__in=ids_validos).update(usuario_id=None)
    Memoria.objects.exclude(usuario_id__in=ids_validos).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0015_categorias'),
    ]

    operations = [
        migrations.RunPython(limpiar_huerfanos, migrations.RunPython.noop),
        # La columna usuario_id se conserva; solo pasa a ser llave foranea hacia Users.
        migrations.AlterField(
            model_name='miaubotaprendizaje',
            name='usuario_id',
            field=models.IntegerField(blank=True, null=True, db_column='usuario_id'),
        ),
        migrations.RenameField(
            model_name='miaubotaprendizaje',
            old_name='usuario_id',
            new_name='usuario',
        ),
        migrations.AlterField(
            model_name='miaubotaprendizaje',
            name='usuario',
            field=models.ForeignKey(blank=True, db_column='usuario_id', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='aprendizajes_miaubot', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='miaubotmemoriausuario',
            name='usuario_id',
            field=models.IntegerField(unique=True, db_column='usuario_id'),
        ),
        migrations.RenameField(
            model_name='miaubotmemoriausuario',
            old_name='usuario_id',
            new_name='usuario',
        ),
        migrations.AlterField(
            model_name='miaubotmemoriausuario',
            name='usuario',
            field=models.OneToOneField(db_column='usuario_id', on_delete=django.db.models.deletion.CASCADE, related_name='memoria_miaubot', to=settings.AUTH_USER_MODEL),
        ),
    ]
