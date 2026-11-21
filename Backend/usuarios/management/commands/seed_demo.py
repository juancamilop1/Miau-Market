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
    help = 'Carga datos de demostracion idempotentes (admin, cliente, productos, mascotas, resenas y pedidos)'

    def handle(self, *args, **options):
        admin = _ensure_user(DEMO_ADMIN, staff=True)
        cliente = _ensure_user(DEMO_CLIENT, staff=False)

        hoy = date.today()
        productos = [
            ('Croquetas premium gato', 'Nutricion completa para gato adulto, rica en omega 3 y taurina', 'COMIDA_GATO', 45000, 25, hoy + timedelta(days=180)),
            ('Alimento humedo gato salmon', 'Sobre 85g con trozos de salmon natural en salsa', 'COMIDA_GATO', 14500, 30, hoy + timedelta(days=150)),
            ('Alimento humedo perro', 'Lata 400g sabor pollo y vegetales para perro adulto', 'COMIDA_PERRO', 12000, 40, hoy + timedelta(days=120)),
            ('Snacks dentales perro', 'Paquete 500g ayuda a reducir el sarro y refrescar el aliento', 'COMIDA_PERRO', 22000, 35, hoy + timedelta(days=150)),
            ('galletas chunky', 'Galletas horneadas para perro (ejemplo de producto caducado)', 'COMIDA_PERRO', 10000, 2, hoy - timedelta(days=1)),
            ('Rascador vertical', 'Poste en sisal natural con plataforma y pompon colgante', 'JUGUETES', 89000, 10, hoy + timedelta(days=365)),
            ('Pelota interactiva', 'Pelota con movimiento automatico y luz LED para gatos', 'JUGUETES', 25000, 30, hoy + timedelta(days=200)),
            ('Collar ajustable', 'Collar reflectivo acolchado tallas S a L con hebilla segura', 'ACCESORIOS', 18000, 50, hoy + timedelta(days=300)),
            ('Cama ortopedica', 'Espuma viscoelastica talla M con funda lavable', 'ACCESORIOS', 120000, 8, hoy + timedelta(days=400)),
            ('Bebedero automatico', 'Fuente de agua filtrada de 1.5 litros silenciosa', 'ACCESORIOS', 65000, 15, hoy + timedelta(days=250)),
            ('Transportador viaje', 'Guacal ventilado mediano hasta 8 kg con puerta metalica', 'ACCESORIOS', 95000, 6, hoy + timedelta(days=500)),
            ('Arena aglomerante 10kg', 'Arena sanitaria sin polvo con control de olores', 'HIGIENE', 35000, 20, hoy + timedelta(days=90)),
            ('Shampoo hipoalergenico mascotas', 'Formula suave con avena y aloe vera para piel sensible', 'HIGIENE', 29000, 18, hoy + timedelta(days=240)),
            ('Antipulgas pipeta gato y perro', 'Proteccion mensual externa contra pulgas y garrapatas', 'FARMACIA', 38000, 22, hoy + timedelta(days=210)),
            ('Vitamins mascotas', 'Suplemento multivitaminico para defensas y pelaje brillante', 'FARMACIA', 28000, 12, hoy + timedelta(days=100)),
            ('Bano y peluqueria mascotas', 'Servicio completo de bano, cepillado y corte de unas', 'SERVICIOS', 55000, 15, hoy + timedelta(days=365)),
        ]

        categorias = {c.codigo.upper(): c for c in CatCategoria.objects.all()}

        creados = 0
        productos_map = {}
        for titulo, desc, codigo, precio, stock, cad in productos:
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
                    'Fecha_Caducidad': cad,
                    'created_by': admin,
                },
            )
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
        for titulo in ('Croquetas premium gato', 'Rascador vertical'):
            prod = productos_map.get(titulo)
            if prod:
                ListaDeseos.objects.get_or_create(usuario=cliente, producto=prod)

        # Resenas iniciales
        croquetas = productos_map.get('Croquetas premium gato')
        rascador = productos_map.get('Rascador vertical')
        pelota = productos_map.get('Pelota interactiva')
        if croquetas:
            ResenaProducto.objects.get_or_create(
                usuario=cliente,
                producto=croquetas,
                defaults={
                    'Rating': 5,
                    'Comentario': 'A mi gato le encantaron y el pedido llego muy rapido.',
                },
            )
        if rascador:
            ResenaProducto.objects.get_or_create(
                usuario=admin,
                producto=rascador,
                defaults={
                    'Rating': 4,
                    'Comentario': 'Muy firme, estable y facil de armar.',
                },
            )

        # Pedidos demo iniciales (solo si la tabla esta vacia)
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
            f'productos nuevos={creados}, total={Producto.objects.count()}, '
            f'pedidos={Pedido.objects.count()}'
        ))
