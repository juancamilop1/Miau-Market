from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0013_miaubot_aprendizaje'),
    ]

    operations = [
        migrations.CreateModel(
            name='MiauBotMemoriaUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usuario_id', models.IntegerField(unique=True)),
                ('mascotas', models.JSONField(blank=True, default=list)),
                ('seguimiento', models.JSONField(blank=True, default=dict)),
                ('mascota_activa_idx', models.IntegerField(default=0)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Memoria MiauBot',
                'verbose_name_plural': 'Memorias MiauBot',
                'db_table': 'MiauBot_Memoria',
            },
        ),
    ]
