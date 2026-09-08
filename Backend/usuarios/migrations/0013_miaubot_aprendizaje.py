from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0012_miaubot_bd'),
    ]

    operations = [
        migrations.CreateModel(
            name='MiauBotAprendizaje',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pregunta', models.TextField()),
                ('respuesta', models.TextField()),
                ('palabras_clave', models.TextField(blank=True, help_text='Auto-generadas desde la pregunta')),
                ('animal', models.CharField(default='general', max_length=20)),
                ('usuario_id', models.IntegerField(blank=True, null=True)),
                ('estado', models.CharField(
                    choices=[('pendiente', 'Pendiente'), ('aprobado', 'Aprobado'), ('rechazado', 'Rechazado')],
                    default='pendiente',
                    max_length=20,
                )),
                ('veces_usada', models.PositiveIntegerField(default=0)),
                ('Fecha_Creacion', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Aprendizaje MiauBot',
                'verbose_name_plural': 'Aprendizajes MiauBot',
                'db_table': 'MiauBot_Aprendizaje',
                'ordering': ['-Fecha_Creacion'],
            },
        ),
    ]
