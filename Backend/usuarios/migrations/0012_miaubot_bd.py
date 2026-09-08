from django.db import migrations, models


def seed_miaubot(apps, schema_editor):
    Config = apps.get_model('usuarios', 'MiauBotConfig')
    Conocimiento = apps.get_model('usuarios', 'MiauBotConocimiento')
    Frase = apps.get_model('usuarios', 'MiauBotFrase')

    if Config.objects.exists():
        return

    Config.objects.create(
        nombre_bot='MiauBot',
        prompt_sistema=(
            'Eres MiauBot, asistente calido y experto de MiauMarket. '
            'Hablas en espanol, de forma cercana y clara. Personalizas segun el animal '
            '(gato o perro). Recomiendas SOLO productos reales del catalogo. '
            'Das consejos practicos de cuidado. Nunca inventas productos ni precios.'
        ),
        mensaje_bienvenida=(
            'Hola! Soy MiauBot, tu asistente en MiauMarket.\n'
            'Cuéntame de tu mascota (gato o perro, edad, que necesita) '
            'y te recomiendo productos reales de nuestra tienda.'
        ),
        mensaje_bienvenida_retorno=(
            'Hola {nombre}! Me alegra verte de nuevo.\n'
            'Cuéntame como esta tu mascota hoy y te ayudo con productos o consejos.'
        ),
        activo=True,
    )

    conocimientos = [
        ('gato', 'alimentacion', 'comida,alimento,croqueta,alimentar,taurina,comer,dieta',
         'Los gatos necesitan proteina animal y taurina en su dieta. Adultos: 2 porciones al dia. '
         'Evita leche de vaca. Si tu gato es sensible, cambia alimento gradualmente en 7 dias.'),
        ('gato', 'arena', 'arena,arenera,sanitario,orina,olor',
         'Limpia desechos a diario y cambia la arena completa cada semana. '
         'Una arenera por gato mas una extra reduce accidentes fuera del arenero.'),
        ('gato', 'juguetes', 'juguete,jugar,aburrid,estimul,raton,pelota',
         'Los gatos cazan por instinto. Rota juguetes cada 3-4 dias: ratones, varitas y tunel '
         'mantienen mente activa y evitan aranazos en muebles.'),
        ('gato', 'salud', 'salud,veterin,enferm,vomito,diarrea,vacuna',
         'Ante vomitos repetidos, falta de apetito o letargia, consulta al veterinario. '
         'Vacunas y desparasitacion al dia protegen a largo plazo.'),
        ('gato', 'pelaje', 'pelo,pelaje,cepill,bola,bano',
         'Cepilla 2-3 veces por semana. En epoca de muda, aumenta a diario para menos bolas de pelo.'),
        ('perro', 'alimentacion', 'comida,alimento,croqueta,perro,perra,cachorro,comer',
         'Los perros necesitan rutina: 2 comidas al dia en adultos. Elige alimento segun tamano '
         'y edad. Siempre agua fresca disponible.'),
        ('perro', 'ejercicio', 'paseo,correr,ejercicio,energia,aburrid',
         'El ejercicio diario controla peso y ansiedad. Minimo 30 min de paseo en razas medianas. '
         'Juguetes interactivos complementan en casa.'),
        ('perro', 'salud', 'salud,veterin,enferm,vacuna,garrapata,pulga',
         'Revision anual, vacunas y antiparasitarios son esenciales. '
         'Revisa orejas y patas despues de cada paseo.'),
        ('general', 'compra', 'comprar,carrito,pagar,checkout,pedido',
         'En Tienda agregas productos al carrito. Con sesion iniciada vas a Checkout, '
         'confirmas envio y metodo de pago. Tu pedido queda registrado al instante.'),
    ]
    for animal, tema, keys, resp in conocimientos:
        Conocimiento.objects.create(
            animal=animal, tema=tema, palabras_clave=keys,
            respuesta=resp, prioridad=5, activo=True,
        )

    frases = [
        ('saludo', 'gato', 'Que bueno saludarte!'),
        ('saludo', 'gato', 'Miau! Estoy aqui para ayudarte.'),
        ('saludo', 'perro', 'Guau! Que gusto ayudarte hoy.'),
        ('saludo', 'general', 'Hola! Listo para ayudarte con tu mascota.'),
        ('intro_producto', 'gato', 'Revisé el catalogo y esto le vendria genial a tu gatito:'),
        ('intro_producto', 'gato', 'Encontre opciones que encajan con lo que buscas:'),
        ('intro_producto', 'perro', 'Para tu perrito tengo estas opciones en stock:'),
        ('intro_producto', 'general', 'Estas son mis mejores opciones para ti:'),
        ('cierre_producto', 'general', 'Puedes agregarlos al carrito desde Tienda. ¿Te muestro algo mas?'),
        ('cierre_producto', 'general', 'Si te gusta alguno, ve a Tienda y agrégalo. ¿Seguimos buscando?'),
        ('empatia', 'gato', 'Ademas del consejo, en tienda tengo esto disponible:'),
        ('empatia', 'perro', 'Para apoyar ese cuidado, mira estos productos:'),
        ('despedida', 'general', 'Hasta pronto! Cuida mucho a tu mascota.'),
        ('despedida', 'general', 'Aqui estare cuando me necesites. Miau!'),
    ]
    for tipo, animal, texto in frases:
        Frase.objects.create(tipo=tipo, animal=animal, texto=texto, activo=True)


def unseed_miaubot(apps, schema_editor):
    apps.get_model('usuarios', 'MiauBotConfig').objects.all().delete()
    apps.get_model('usuarios', 'MiauBotConocimiento').objects.all().delete()
    apps.get_model('usuarios', 'MiauBotFrase').objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0011_usuario_username'),
    ]

    operations = [
        migrations.CreateModel(
            name='MiauBotConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_bot', models.CharField(default='MiauBot', max_length=50)),
                ('prompt_sistema', models.TextField(help_text='Instrucciones internas de personalidad y tono del bot')),
                ('mensaje_bienvenida', models.TextField()),
                ('mensaje_bienvenida_retorno', models.TextField(blank=True, help_text='Saludo cuando el usuario ya tiene sesion. Use {nombre} para personalizar.')),
                ('activo', models.BooleanField(default=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Configuracion MiauBot',
                'db_table': 'MiauBot_Config',
            },
        ),
        migrations.CreateModel(
            name='MiauBotConocimiento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('animal', models.CharField(choices=[('gato', 'Gato'), ('perro', 'Perro'), ('general', 'General')], default='gato', max_length=20)),
                ('tema', models.CharField(max_length=50)),
                ('palabras_clave', models.TextField(help_text='Palabras separadas por coma')),
                ('respuesta', models.TextField()),
                ('prioridad', models.PositiveSmallIntegerField(default=0)),
                ('activo', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name_plural': 'Conocimientos MiauBot',
                'db_table': 'MiauBot_Conocimiento',
                'ordering': ['-prioridad', 'tema'],
            },
        ),
        migrations.CreateModel(
            name='MiauBotFrase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('saludo', 'Saludo'), ('intro_producto', 'Intro productos'), ('cierre_producto', 'Cierre productos'), ('empatia', 'Empatia'), ('despedida', 'Despedida')], max_length=30)),
                ('animal', models.CharField(default='general', max_length=20)),
                ('texto', models.TextField()),
                ('activo', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'MiauBot_Frases',
            },
        ),
        migrations.RunPython(seed_miaubot, unseed_miaubot),
    ]
