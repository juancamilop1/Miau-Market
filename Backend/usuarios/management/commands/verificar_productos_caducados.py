from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from usuarios.models import Producto, Notificacion
from datetime import date

Usuario = get_user_model()

class Command(BaseCommand):
    help = 'Verifica productos de categoría Comida caducados y notifica a los administradores'

    def handle(self, *args, **kwargs):
        hoy = date.today()
        
        # Buscar solo productos de categoría Comida que caducaron hoy
        productos_caducados = Producto.objects.filter(
            Categoria='Comida',
            Fecha_Caducidad=hoy
        )
        
        if productos_caducados.exists():
            # Obtener todos los admins
            admins = Usuario.objects.filter(is_staff=True)
            
            for producto in productos_caducados:
                self.stdout.write(f'Producto de comida caducado: {producto.Titulo} (ID: {producto.id})')
                
                # Crear notificación para cada admin
                for admin in admins:
                    # Verificar si ya existe una notificación para este producto
                    notif_existe = Notificacion.objects.filter(
                        usuario=admin,
                        tipo='producto_caducado',
                        mensaje__contains=f'ID {producto.id}'
                    ).exists()
                    
                    if not notif_existe:
                        Notificacion.objects.create(
                            usuario=admin,
                            titulo='⚠️ Producto Caducado',
                            mensaje=f'El producto de comida "{producto.Titulo}" (ID {producto.id}) ha caducado hoy.',
                            tipo='producto_caducado'
                        )
                        
                        # Limpiar notificaciones antiguas del admin
                        notifs_admin = Notificacion.objects.filter(usuario=admin).order_by('-fecha_creacion')
                        if notifs_admin.count() > 10:
                            ids_mantener = list(notifs_admin.values_list('id', flat=True)[:10])
                            Notificacion.objects.filter(usuario=admin).exclude(id__in=ids_mantener).delete()
                
            self.stdout.write(self.style.SUCCESS(f'{productos_caducados.count()} productos de comida caducados procesados'))
        else:
            self.stdout.write('No hay productos de comida caducados hoy')
