from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

Usuario = get_user_model()


class Command(BaseCommand):
    help = 'Convierte un usuario en administrador (is_staff e is_superuser)'

    def add_arguments(self, parser):
        parser.add_argument(
            'email',
            nargs='?',
            help='Email del usuario a promover'
        )
        parser.add_argument(
            '--bootstrap',
            action='store_true',
            help='Si no hay admins, promueve al primer usuario registrado'
        )

    def handle(self, *args, **options):
        email = options.get('email')
        bootstrap = options.get('bootstrap')

        if bootstrap:
            if Usuario.objects.filter(is_staff=True).exists():
                self.stdout.write(self.style.WARNING('Ya existe al menos un administrador.'))
                return

            user = Usuario.objects.order_by('id').first()
            if not user:
                raise CommandError('No hay usuarios registrados.')

            user.is_staff = True
            user.is_superuser = True
            user.save(update_fields=['is_staff', 'is_superuser'])
            self.stdout.write(self.style.SUCCESS(
                f'Administrador inicial: {user.Email} ({user.Nombre} {user.Apellido})'
            ))
            return

        if not email:
            raise CommandError('Indica un email o usa --bootstrap')

        try:
            user = Usuario.objects.get(Email=email)
        except Usuario.DoesNotExist as exc:
            raise CommandError(f'No existe usuario con email: {email}') from exc

        user.is_staff = True
        user.is_superuser = True
        user.save(update_fields=['is_staff', 'is_superuser'])
        self.stdout.write(self.style.SUCCESS(
            f'{user.Email} ahora es administrador.'
        ))
