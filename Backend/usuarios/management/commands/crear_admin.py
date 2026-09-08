from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import date

Usuario = get_user_model()

DEFAULTS = {
    'username': 'adminmarket',
    'email': 'cadminmarket@gmail.com',
    'password': '70119953juan',
    'nombre': 'Admin',
    'apellido': 'Market',
}


class Command(BaseCommand):
    help = 'Crea o actualiza el usuario administrador por defecto de Miau Market'

    def add_arguments(self, parser):
        parser.add_argument('--username', default=DEFAULTS['username'])
        parser.add_argument('--email', default=DEFAULTS['email'])
        parser.add_argument('--password', default=DEFAULTS['password'])
        parser.add_argument('--nombre', default=DEFAULTS['nombre'])
        parser.add_argument('--apellido', default=DEFAULTS['apellido'])

    def handle(self, *args, **options):
        username = options['username'].strip().lower()
        email = options['email'].strip().lower()
        password = options['password']

        user = (
            Usuario.objects.filter(Username__iexact=username).first()
            or Usuario.objects.filter(Email__iexact=email).first()
        )

        if user:
            user.Username = username
            user.Email = email
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.save()
            accion = 'actualizado'
        else:
            user = Usuario.objects.create_user(
                Email=email,
                Username=username,
                password=password,
                Nombre=options['nombre'],
                Apellido=options['apellido'],
                Telefono='3000000000',
                Address='Admin',
                City='Bogota',
                BirthDate=date(1990, 1, 1),
                is_staff=True,
                is_superuser=True,
            )
            accion = 'creado'

        self.stdout.write(self.style.SUCCESS(
            f'Administrador {accion}: usuario={user.Username}, email={user.Email}'
        ))
