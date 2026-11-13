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
    # TiDB Starter no permite ADD COLUMN + UNIQUE en un solo ALTER.
    atomic = False

    dependencies = [
        ('usuarios', '0010_modelos_completos'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='Username',
            field=models.CharField(db_column='Username', max_length=50, null=True),
        ),
        migrations.RunPython(asignar_usernames, migrations.RunPython.noop),
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="UPDATE Users SET Username = CONCAT('user', Id_User) WHERE Username IS NULL OR Username = ''",
                    reverse_sql=migrations.RunSQL.noop,
                ),
                migrations.RunSQL(
                    sql='ALTER TABLE Users MODIFY COLUMN Username VARCHAR(50) NOT NULL',
                    reverse_sql='ALTER TABLE Users MODIFY COLUMN Username VARCHAR(50) NULL',
                ),
                migrations.RunSQL(
                    sql='CREATE UNIQUE INDEX Username ON Users (Username)',
                    reverse_sql='DROP INDEX Username ON Users',
                ),
            ],
            state_operations=[
                migrations.AlterField(
                    model_name='usuario',
                    name='Username',
                    field=models.CharField(db_column='Username', max_length=50, unique=True),
                ),
            ],
        ),
    ]
