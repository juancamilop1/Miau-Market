from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from usuarios.models import Producto, Notificacion
from datetime import date

Usuario = get_user_model()


class Command(BaseCommand):
    help = 'Verifica productos de categoria Comida caducados y notifica a los administradores'

    def handle(self, *args, **kwargs):
        hoy = date.today()

        productos_caducados = Producto.objects.filter(
            Categoria='Comida',
            Fecha_Caducidad=hoy
        )

        if not productos_caducados.exists():
            self.stdout.write('No hay productos de comida caducados hoy')
            return

        admins = Usuario.objects.filter(is_staff=True)

        for producto in productos_caducados:
            self.stdout.write(f'Producto caducado: {producto.Titulo} (ID {producto.id})')

            for admin in admins:
                notif_existe = Notificacion.objects.filter(
                    usuario=admin,
                    Tipo='producto_caducado',
                    Mensaje__contains=f'ID {producto.id}'
                ).exists()

                if not notif_existe:
                    Notificacion.objects.create(
                        usuario=admin,
                        Titulo='Producto Caducado',
                        Mensaje=f'El producto de comida "{producto.Titulo}" (ID {producto.id}) ha caducado hoy.',
                        Tipo='producto_caducado'
                    )

                    notifs = Notificacion.objects.filter(usuario=admin).order_by('-Fecha_Creacion')
                    if notifs.count() > 10:
                        ids = list(notifs.values_list('id', flat=True)[:10])
                        Notificacion.objects.filter(usuario=admin).exclude(id__in=ids).delete()

        self.stdout.write(self.style.SUCCESS(
            f'{productos_caducados.count()} productos de comida caducados procesados'
        ))
