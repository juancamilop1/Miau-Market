import os
from datetime import date

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from dotenv import load_dotenv
from pathlib import Path

Usuario = get_user_model()

ENV_PATH = Path(__file__).resolve().parents[3] / '.env'


class Command(BaseCommand):
    help = 'Crea o actualiza un usuario administrador (credenciales desde .env o argumentos)'

    def add_arguments(self, parser):
        parser.add_argument('--username', default=os.environ.get('ADMIN_USERNAME', ''))
        parser.add_argument('--email', default=os.environ.get('ADMIN_EMAIL', ''))
        parser.add_argument('--password', default=os.environ.get('ADMIN_PASSWORD', ''))
        parser.add_argument('--nombre', default=os.environ.get('ADMIN_NOMBRE', 'Admin'))
        parser.add_argument('--apellido', default=os.environ.get('ADMIN_APELLIDO', 'Market'))

    def handle(self, *args, **options):
        load_dotenv(ENV_PATH)

        username = (options['username'] or os.environ.get('ADMIN_USERNAME', '')).strip().lower()
        email = (options['email'] or os.environ.get('ADMIN_EMAIL', '')).strip().lower()
        password = options['password'] or os.environ.get('ADMIN_PASSWORD', '')

        if not username or not email or not password:
            raise CommandError(
                'Define ADMIN_USERNAME, ADMIN_EMAIL y ADMIN_PASSWORD en Backend/.env '
                'o pasa --username, --email y --password.'
            )

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
                Telefono=os.environ.get('ADMIN_TELEFONO', '3000000000'),
                Address=os.environ.get('ADMIN_ADDRESS', 'Admin'),
                City=os.environ.get('ADMIN_CITY', 'Bogota'),
                BirthDate=date(1990, 1, 1),
                is_staff=True,
                is_superuser=True,
            )
            accion = 'creado'

        self.stdout.write(self.style.SUCCESS(
            f'Administrador {accion}: usuario={user.Username}, email={user.Email}'
        ))
