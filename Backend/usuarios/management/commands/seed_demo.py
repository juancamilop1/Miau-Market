from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from usuarios.models import Categoria, Producto

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
    user = Usuario.objects.filter(Username__iexact=data['username']).first()
    if user:
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
    help = 'Carga datos de demostracion en SQLite (admin, cliente y productos)'

    def handle(self, *args, **options):
        admin = _ensure_user(DEMO_ADMIN, staff=True)
        _ensure_user(DEMO_CLIENT, staff=False)

        hoy = date.today()
        productos = [
            ('Croquetas premium gato', 'Nutricion completa adulto', 'COMIDA_GATO', 45000, 25, hoy + timedelta(days=180)),
            ('Alimento humedo perro', 'Lata 400g sabor pollo', 'COMIDA_PERRO', 12000, 40, hoy + timedelta(days=120)),
            ('Rascador vertical', 'Con sisal y plataforma', 'JUGUETES', 89000, 10, hoy + timedelta(days=365)),
            ('Pelota interactiva', 'Luz LED para gatos', 'JUGUETES', 25000, 30, hoy + timedelta(days=200)),
            ('Collar ajustable', 'Tallas S a L', 'ACCESORIOS', 18000, 50, hoy + timedelta(days=300)),
            ('Cama ortopedica', 'Espuma viscoelastica M', 'ACCESORIOS', 120000, 8, hoy + timedelta(days=400)),
            ('Arena aglomerante 10kg', 'Bajo polvo', 'ACCESORIOS', 35000, 20, hoy + timedelta(days=90)),
            ('Snacks dentales perro', 'Paquete 500g', 'COMIDA_PERRO', 22000, 35, hoy + timedelta(days=150)),
            ('Bebedero automatico', '1.5 litros', 'ACCESORIOS', 65000, 15, hoy + timedelta(days=250)),
            ('Vitamins mascotas', 'Suplemento multivitaminico', 'SERVICIOS', 28000, 12, hoy + timedelta(days=100)),
            ('galletas chunky', 'ricas galletas acarameladas', 'COMIDA_PERRO', 10000, 2, hoy - timedelta(days=1)),
            ('Transportador viaje', 'Mediano hasta 8kg', 'ACCESORIOS', 95000, 6, hoy + timedelta(days=500)),
        ]
        categorias = {c.Codigo: c for c in Categoria.objects.all()}

        creados = 0
        for titulo, desc, codigo, precio, stock, cad in productos:
            _, created = Producto.objects.get_or_create(
                Titulo=titulo,
                defaults={
                    'Descripcion': desc,
                    'categoria': categorias[codigo],
                    'Precio': precio,
                    'Stock': stock,
                    'Fecha_Caducidad': cad,
                    'created_by': admin,
                },
            )
            if created:
                creados += 1

        self.stdout.write(self.style.SUCCESS(
            f'Demo OK: admin={DEMO_ADMIN["username"]}, cliente={DEMO_CLIENT["username"]}, '
            f'productos nuevos={creados}, total={Producto.objects.count()}'
        ))
