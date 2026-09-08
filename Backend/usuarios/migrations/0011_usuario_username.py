from django.db import migrations, models


def asignar_usernames(apps, schema_editor):
    Usuario = apps.get_model('usuarios', 'Usuario')
    usados = set()
    for user in Usuario.objects.all().order_by('id'):
        base = (user.Email.split('@')[0] if user.Email else f'user{user.id}').lower()
        base = ''.join(c for c in base if c.isalnum() or c == '_') or f'user{user.id}'
        candidato = base
        n = 1
        while candidato in usados or Usuario.objects.filter(Username=candidato).exclude(pk=user.pk).exists():
            candidato = f'{base}{n}'
            n += 1
        user.Username = candidato
        user.save(update_fields=['Username'])
        usados.add(candidato)


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0010_modelos_completos'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='Username',
            field=models.CharField(db_column='Username', max_length=50, null=True, unique=True),
        ),
        migrations.RunPython(asignar_usernames, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='usuario',
            name='Username',
            field=models.CharField(db_column='Username', max_length=50, unique=True),
        ),
    ]
