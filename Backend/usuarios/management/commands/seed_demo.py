from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Q

from usuarios.models import (
    CatCategoria,
    CatEstadoPedido,
    CatMetodoPago,
    DetallePedido,
    ListaDeseos,
    MascotaUsuario,
    Pedido,
    Producto,
    ResenaProducto,
)

Usuario = get_user_model()

DEMO_ADMIN = {
    'username': 'adminmarket',
    'email': 'admin@miau.market',
    'password': 'miauadmin2026',
    'nombre': 'Admin',
    'apellido': 'Market',
}

DEMO_CLIENT = {
    'username': 'clientedemo',
    'email': 'cliente@miau.market',
    'password': 'cliente2026',
    'nombre': 'Maria',
    'apellido': 'Demo',
}


def _ensure_user(data: dict, staff: bool = False) -> Usuario:
    user = Usuario.objects.filter(
        Q(Email__iexact=data['email']) | Q(Username__iexact=data['username'])
    ).first()
    if user:
        if not Usuario.objects.filter(Email__iexact=data['email']).exclude(pk=user.pk).exists():
            user.Email = data['email']
        if not Usuario.objects.filter(Username__iexact=data['username']).exclude(pk=user.pk).exists():
            user.Username = data['username']
        user.set_password(data['password'])
        user.is_staff = staff
        user.is_superuser = staff
        user.is_active = True
        user.save()
        return user
    return Usuario.objects.create_user(
        Email=data['email'],
        Username=data['username'],
        password=data['password'],
        Nombre=data['nombre'],
        Apellido=data['apellido'],
        Telefono='3001234567',
        Address='Calle Demo 123',
        City='Bogotá D.C.',
        BirthDate=date(1995, 6, 15),
        is_staff=staff,
        is_superuser=staff,
    )


class Command(BaseCommand):
    help = 'Carga datos de demostracion idempotentes (admin, cliente, productos con imagenes, mascotas, resenas y pedidos)'

    def handle(self, *args, **options):
        admin = _ensure_user(DEMO_ADMIN, staff=True)
        cliente = _ensure_user(DEMO_CLIENT, staff=False)

        hoy = date.today()
        productos = [
            # Comida de Gato
            ('Croquetas premium gato', 'Agility Gold gatos 1.5 kg: nutricion super premium que previene bolas de pelo y cuida la salud renal.', 'COMIDA_GATO', 45000, 25, hoy + timedelta(days=180), '/productos/adulto.jpg'),
            ('Cat Chow Adultos 1.5 kg', 'Alimento completo para gatos adultos con defensa natural, proteinas de alta calidad y vitaminas.', 'COMIDA_GATO', 34000, 28, hoy + timedelta(days=190), '/productos/adulto_cat_chaw.jpg'),
            ('Alimento humedo gato salmon', 'Nutricion equilibrada para gatos adultos con alto contenido de taurina y omega 3.', 'COMIDA_GATO', 14500, 30, hoy + timedelta(days=150), '/productos/adulto.jpg'),

            # Comida de Perro
            ('Royal Canin Maxi Adult', 'Concentrado premium para perros adultos de razas grandes con soporte digestivo y articular.', 'COMIDA_PERRO', 135000, 14, hoy + timedelta(days=240), '/productos/royal_canin_adulto.jpg'),
            ('Royal Canin Puppy Medium', 'Nutricion especializada para cachorros de 2 a 12 meses de razas medianas.', 'COMIDA_PERRO', 118000, 16, hoy + timedelta(days=220), '/productos/royal_canin_cachorro.jpg'),
            ('Taste of the Wild Puppy', 'Receta libre de granos con bisonte y venado asado para cachorros activos (2.27 kg).', 'COMIDA_PERRO', 129000, 12, hoy + timedelta(days=260), '/productos/taste_of_teh_wild.webp'),
            ('Dog Chow Adultos 2 kg', 'Alimento balanceado con prebiotico natural para perros adultos sanos y con energia.', 'COMIDA_PERRO', 36000, 32, hoy + timedelta(days=180), '/productos/dog_chow_adulto.jpg'),
            ('Dog Chow Cachorros 2 kg', 'Formula con DHA y calcio para el crecimiento fuerte de cachorros.', 'COMIDA_PERRO', 38000, 24, hoy + timedelta(days=180), '/productos/dog_chow_cachorro.jpg'),
            ('Dogourmet Adultos Carne', 'Croquetas crocantes sabor carne a la parrilla con vitaminas y minerales esenciales.', 'COMIDA_PERRO', 29500, 35, hoy + timedelta(days=160), '/productos/dogourmet_adultos.jpg'),
            ('Alimento humedo perro', 'Formula suave y nutritiva para perros cachorros y adultos de facil digestion.', 'COMIDA_PERRO', 12000, 40, hoy + timedelta(days=120), '/productos/dogourmet_cachorros.jpg'),
            ('Snacks dentales perro', 'Huesito masticable natural que ayuda a reducir el sarro y fortalece la mandibula.', 'COMIDA_PERRO', 22000, 35, hoy + timedelta(days=150), '/productos/huesito.jpg'),
            ('galletas chunky', 'Concentrado Chunky 2 kg (ejemplo de producto caducado para validacion RF-07).', 'COMIDA_PERRO', 10000, 2, hoy - timedelta(days=1), '/productos/chunky_2k.webp'),

            # Juguetes
            ('Rascador vertical', 'Poste en sisal natural con base estable y pompon colgante para gatos.', 'JUGUETES', 89000, 10, hoy + timedelta(days=365), '/productos/rascador.jpg'),
            ('Pelota interactiva', 'Pelota de tenis resistente ideal para juegos de lanzamiento y ejercicio diario.', 'JUGUETES', 25000, 30, hoy + timedelta(days=200), '/productos/pelota_tenis.jpg'),
            ('Pelota con pinchos masajeadora', 'Pelota de goma flexible con puntas suaves que limpian encias mientras juega.', 'JUGUETES', 19500, 26, hoy + timedelta(days=300), '/productos/pelota_con_pinchos.jpg'),
            ('Raton de juguete para gato', 'Raton felpudo liviano que estimula el instinto natural de caza felino.', 'JUGUETES', 15000, 40, hoy + timedelta(days=320), '/productos/raton_dej_uguete_.jpg'),

            # Accesorios
            ('Cama ortopedica', 'Cama acolchada talla M de tela suave lavable para descanso comodo de perros y gatos.', 'ACCESORIOS', 120000, 8, hoy + timedelta(days=400), '/productos/cama_para_perro.jpg'),
            ('Collar ajustable', 'Collar reflectivo acolchado tallas S a L con hebilla reforzada y placa.', 'ACCESORIOS', 18000, 50, hoy + timedelta(days=300), '/productos/collar_ajustable.svg'),
            ('Bebedero automatico', 'Fuente de agua filtrada de 1.5 litros silenciosa para hidratacion constante.', 'ACCESORIOS', 65000, 15, hoy + timedelta(days=250), '/productos/bebedero_automatico.svg'),
            ('Transportador viaje', 'Guacal ventilado mediano hasta 8 kg con puerta metalica y manija ergonomica.', 'ACCESORIOS', 95000, 6, hoy + timedelta(days=500), '/productos/transportador_viaje.svg'),

            # Higiene
            ('Arena aglomerante 10kg', 'Caja sanitaria cerrada con filtro antiolor y compuerta abatible para gatos.', 'HIGIENE', 85000, 20, hoy + timedelta(days=365), '/productos/caja_de_arena_.jpg'),
            ('Shampoo hipoalergenico mascotas', 'Formula suave con avena y aloe vera sin parabenos para piel sensible.', 'HIGIENE', 29000, 18, hoy + timedelta(days=240), '/productos/shampoo_mascotas.svg'),

            # Farmacia
            ('Antipulgas pipeta gato y perro', 'Proteccion externa mensual de amplio espectro contra pulgas y garrapatas.', 'FARMACIA', 38000, 22, hoy + timedelta(days=210), '/productos/antipulgas_pipeta.svg'),
            ('Vitamins mascotas', 'Suplemento multivitaminico con complejo B para defensas y pelaje brillante.', 'FARMACIA', 28000, 12, hoy + timedelta(days=100), '/productos/vitaminas_mascotas.svg'),

            # Servicios
            ('Bano y peluqueria mascotas', 'Servicio completo de bano medicado o cosmetico, cepillado y corte de unas.', 'SERVICIOS', 55000, 15, hoy + timedelta(days=365), '/productos/bano_peluqueria.svg'),
            ('Chequeo veterinario preventivo', 'Valoracion general presencial en sede aliada: peso, oidos, piel y esquema de vacunas.', 'SERVICIOS', 68000, 10, hoy + timedelta(days=365), '/productos/consulta_veterinaria.svg'),
        ]

        categorias = {c.codigo.upper(): c for c in CatCategoria.objects.all()}

        creados = 0
        imagenes_actualizadas = 0
        productos_map = {}
        for titulo, desc, codigo, precio, stock, cad, imagen in productos:
            cat = categorias.get(codigo.upper())
            if not cat:
                continue
            prod, created = Producto.objects.get_or_create(
                Titulo=titulo,
                defaults={
                    'Descripcion': desc,
                    'categoria': cat,
                    'Categoria': cat.nombre,
                    'Precio': precio,
                    'Stock': stock,
                    'Imagen': imagen,
                    'Fecha_Caducidad': cad,
                    'created_by': admin,
                },
            )
            if not created and not prod.Imagen and imagen:
                prod.Imagen = imagen
                prod.save(update_fields=['Imagen'])
                imagenes_actualizadas += 1
            productos_map[titulo] = prod
            if created:
                creados += 1

        # Perfiles de mascotas del cliente demo
        MascotaUsuario.objects.get_or_create(
            usuario=cliente,
            nombre='Michi',
            defaults={
                'especie': 'gato',
                'edad_anios': 3,
                'notas': 'Gato esterilizado, prefiere alimento de salmon y juguetes interactivos.',
                'activo': True,
            },
        )
        MascotaUsuario.objects.get_or_create(
            usuario=cliente,
            nombre='Toby',
            defaults={
                'especie': 'perro',
                'edad_anios': 5,
                'notas': 'Perro mediano, le gustan los snacks dentales y paseos diarios.',
                'activo': True,
            },
        )

        # Favoritos iniciales del cliente demo
        for titulo in ('Croquetas premium gato', 'Rascador vertical', 'Cama ortopedica'):
            prod = productos_map.get(titulo)
            if prod:
                ListaDeseos.objects.get_or_create(usuario=cliente, producto=prod)

        # Resenas iniciales en varias categorias
        resenas_seed = [
            ('Croquetas premium gato', cliente, 5, 'A mi gato le encantaron y el pedido llego muy rapido.'),
            ('Rascador vertical', admin, 4, 'Muy firme, estable y facil de armar.'),
            ('Royal Canin Maxi Adult', cliente, 5, 'Excelente calidad, mejoro muchisimo el pelaje de mi perro.'),
            ('Cama ortopedica', cliente, 5, 'Super acolchada y muy facil de lavar, a Toby le encanto.'),
        ]
        for titulo, autor, rating, comentario in resenas_seed:
            prod = productos_map.get(titulo)
            if prod:
                ResenaProducto.objects.get_or_create(
                    usuario=autor,
                    producto=prod,
                    defaults={'Rating': rating, 'Comentario': comentario},
                )

        # Pedidos demo iniciales (solo si la tabla esta vacia)
        croquetas = productos_map.get('Croquetas premium gato')
        pelota = productos_map.get('Pelota interactiva')
        if Pedido.objects.count() == 0 and croquetas and pelota:
            metodo = CatMetodoPago.objects.filter(codigo='contra_entrega').first()
            est_entregado = CatEstadoPedido.objects.filter(codigo='entregado').first()
            est_pendiente = CatEstadoPedido.objects.filter(codigo='pendiente').first()

            if metodo and est_entregado:
                p1 = Pedido.objects.create(
                    usuario=cliente,
                    Total=Decimal(croquetas.Precio * 2),
                    Metodo_Pago=metodo.nombre,
                    metodo_pago=metodo,
                    Estado=est_entregado.nombre,
                    estado=est_entregado,
                    Direccion_Envio='Calle 45 # 18-22, Chapinero, Bogota',
                    Telefono_Envio='3001234567',
                )
                DetallePedido.objects.create(
                    pedido=p1,
                    producto=croquetas,
                    Cantidad=2,
                    Precio_Unitario=Decimal(croquetas.Precio),
                    Subtotal=Decimal(croquetas.Precio * 2),
                )

            if metodo and est_pendiente:
                p2 = Pedido.objects.create(
                    usuario=cliente,
                    Total=Decimal(pelota.Precio),
                    Metodo_Pago=metodo.nombre,
                    metodo_pago=metodo,
                    Estado=est_pendiente.nombre,
                    estado=est_pendiente,
                    Direccion_Envio='Calle 45 # 18-22, Chapinero, Bogota',
                    Telefono_Envio='3001234567',
                )
                DetallePedido.objects.create(
                    pedido=p2,
                    producto=pelota,
                    Cantidad=1,
                    Precio_Unitario=Decimal(pelota.Precio),
                    Subtotal=Decimal(pelota.Precio),
                )

        self.stdout.write(self.style.SUCCESS(
            f'Demo OK: admin={admin.Username} ({admin.Email}), '
            f'cliente={cliente.Username} ({cliente.Email}), '
            f'productos nuevos={creados}, imgs={imagenes_actualizadas}, '
            f'total={Producto.objects.count()}, pedidos={Pedido.objects.count()}'
        ))
