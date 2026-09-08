from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import RegistroSerializer, UsuarioSerializer, ProductoSerializer, AdminUsuarioUpdateSerializer
from .pedidos_serializers import CrearPedidoSerializer
from .notificaciones_serializers import NotificacionSerializer
from django.db.models import Sum, Count
from .models import Producto, Notificacion, Pedido
from .services import pedidos_service, ratings_service
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

Usuario = get_user_model()

class RegistroView(generics.CreateAPIView):
    """
    Vista para registrar nuevos usuarios.
    Permite enviar los datos mediante un método POST y guarda el usuario en la base de datos.
    """
    queryset = Usuario.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegistroSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                'success': True,
                'data': serializer.data,
                'message': 'Usuario registrado exitosamente'
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

from django.contrib.auth import authenticate
from .login_serializer import LoginSerializer

class LoginView(generics.GenericAPIView):
    """
    Inicio de sesion con correo o nombre de usuario (sin distinguir mayusculas).
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            login = serializer.validated_data['login']
            password = serializer.validated_data['password']

            user = authenticate(request, login=login, password=password)

            if user:
                token, created = Token.objects.get_or_create(user=user)

                from datetime import date
                edad = None
                if user.BirthDate:
                    today = date.today()
                    edad = today.year - user.BirthDate.year - (
                        (today.month, today.day) < (user.BirthDate.month, user.BirthDate.day)
                    )

                return Response({
                    'success': True,
                    'token': token.key,
                    'user': {
                        'id': user.id,
                        'username': user.Username,
                        'email': user.Email,
                        'name': user.Nombre,
                        'Apellido': user.Apellido,
                        'is_staff': user.is_staff,
                        'is_superuser': user.is_superuser,
                        'Address': user.Address,
                        'Telefono': user.Telefono,
                        'Ciudad': user.City,
                        'Edad': edad
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Usuario, correo o contrasena incorrectos'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UsuarioListView(generics.ListCreateAPIView):
    """
    Lista todos los usuarios o crea uno nuevo (solo admin).
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [IsAuthenticated()]

class UsuarioDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Recupera, actualiza o elimina un usuario.
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        if user == request.user:
            return Response(
                {"error": "No puedes eliminar tu propio usuario"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().delete(request, *args, **kwargs)


# ==================== VISTAS DE GESTIÓN DE USUARIOS (ADMIN) ====================

class GestionUsuariosView(APIView):
    """
    Vista para listar todos los usuarios con sus detalles completos
    Solo accesible para staff (is_staff=True)
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """Listar todos los usuarios con información completa"""
        try:
            # Obtener todos los usuarios directamente con el ORM
            usuarios_qs = Usuario.objects.all().order_by('-FechaRegistro')
            
            usuarios = []
            for usuario in usuarios_qs:
                stats = Pedido.objects.filter(usuario_id=usuario.id).aggregate(
                    total=Count('id'),
                    gastado=Sum('Total'),
                )
                usuarios.append({
                    'Id_User': usuario.id,
                    'Username': usuario.Username,
                    'Nombre': usuario.Nombre,
                    'Apellido': usuario.Apellido,
                    'Email': usuario.Email,
                    'Telefono': usuario.Telefono,
                    'Address': usuario.Address,
                    'City': usuario.City,
                    'BirthDate': usuario.BirthDate,
                    'is_staff': usuario.is_staff,
                    'is_superuser': usuario.is_superuser,
                    'is_active': usuario.is_active,
                    'FechaRegistro': usuario.FechaRegistro,
                    'Total_Pedidos': stats['total'] or 0,
                    'Total_Gastado': float(stats['gastado'] or 0),
                })
            
            return Response({
                'usuarios': usuarios,
                'total': len(usuarios)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error al listar usuarios: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({
                'error': 'Error al obtener la lista de usuarios'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConvertirAdministradorView(APIView):
    """
    Vista para convertir un usuario en administrador
    Solo accesible para superusuarios (is_superuser=True)
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, user_id):
        """Convertir usuario en staff/admin"""
        # Verificar que el usuario actual es superusuario
        if not request.user.is_superuser:
            return Response({
                'error': 'Solo los superusuarios pueden crear administradores'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            usuario = Usuario.objects.get(id=user_id)
            
            # No permitir que se modifique a sí mismo
            if usuario.id == request.user.id:
                return Response({
                    'error': 'No puedes modificar tus propios permisos'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Toggle is_staff
            nuevo_estado = request.data.get('is_staff', not usuario.is_staff)
            usuario.is_staff = nuevo_estado
            usuario.save()
            
            mensaje = f"Usuario {'convertido en administrador' if nuevo_estado else 'removido como administrador'} exitosamente"
            
            return Response({
                'success': True,
                'message': mensaje,
                'usuario': {
                    'id': usuario.id,
                    'Nombre': usuario.Nombre,
                    'Apellido': usuario.Apellido,
                    'is_staff': usuario.is_staff
                }
            }, status=status.HTTP_200_OK)
            
        except Usuario.DoesNotExist:
            return Response({
                'error': 'Usuario no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error al convertir administrador: {str(e)}")
            return Response({
                'error': 'Error al modificar el usuario'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ActualizarUsuarioAdminView(APIView):
    """Actualiza toda la informacion y roles de un usuario (solo staff)."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, user_id):
        return self._update(request, user_id)

    def patch(self, request, user_id):
        return self._update(request, user_id)

    def _update(self, request, user_id):
        try:
            usuario = Usuario.objects.get(id=user_id)
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        if usuario.id == request.user.id and (
            'is_staff' in request.data or 'is_superuser' in request.data or 'is_active' in request.data
        ):
            return Response(
                {'error': 'No puedes modificar tus propios permisos'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if 'is_superuser' in request.data and not request.user.is_superuser:
            return Response(
                {'error': 'Solo superusuarios pueden asignar rol de superusuario'},
                status=status.HTTP_403_FORBIDDEN,
            )

        if usuario.is_superuser and not request.user.is_superuser:
            return Response(
                {'error': 'No puedes modificar a un superusuario'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AdminUsuarioUpdateSerializer(usuario, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        usuario = serializer.save()
        stats = Pedido.objects.filter(usuario_id=usuario.id).aggregate(
            total=Count('id'),
            gastado=Sum('Total'),
        )

        return Response({
            'success': True,
            'message': 'Usuario actualizado correctamente',
            'usuario': {
                'Id_User': usuario.id,
                'Username': usuario.Username,
                'Nombre': usuario.Nombre,
                'Apellido': usuario.Apellido,
                'Email': usuario.Email,
                'Telefono': usuario.Telefono,
                'Address': usuario.Address,
                'City': usuario.City,
                'BirthDate': usuario.BirthDate,
                'is_staff': usuario.is_staff,
                'is_superuser': usuario.is_superuser,
                'is_active': usuario.is_active,
                'FechaRegistro': usuario.FechaRegistro,
                'Total_Pedidos': stats['total'] or 0,
                'Total_Gastado': float(stats['gastado'] or 0),
            },
        }, status=status.HTTP_200_OK)


class EliminarUsuarioView(APIView):
    """
    Vista para eliminar un usuario
    Accesible para staff (is_staff=True)
    Restricciones:
    - Staff NO puede eliminar superusuarios (a menos que el staff sea superusuario)
    - Nadie puede eliminarse a sí mismo
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def delete(self, request, user_id):
        """Eliminar un usuario"""
        try:
            usuario = Usuario.objects.get(id=user_id)
            
            # No permitir auto-eliminación
            if usuario.id == request.user.id:
                return Response({
                    'error': 'No puedes eliminar tu propia cuenta'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Si el usuario a eliminar es superusuario, solo otro superusuario puede eliminarlo
            if usuario.is_superuser and not request.user.is_superuser:
                return Response({
                    'error': 'Solo los superusuarios pueden eliminar cuentas de superusuario'
                }, status=status.HTTP_403_FORBIDDEN)
            
            nombre_completo = f"{usuario.Nombre} {usuario.Apellido}"
            usuario.delete()
            
            return Response({
                'success': True,
                'message': f'Usuario {nombre_completo} eliminado exitosamente'
            }, status=status.HTTP_200_OK)
            
        except Usuario.DoesNotExist:
            return Response({
                'error': 'Usuario no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error al eliminar usuario: {str(e)}")
            return Response({
                'error': 'Error al eliminar el usuario'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BulkDeleteUsersView(APIView):
    """
    Vista para eliminar múltiples usuarios a la vez
    Solo accesible para administradores
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def post(self, request):
        """Eliminar múltiples usuarios"""
        try:
            user_ids = request.data.get('user_ids', [])
            
            if not user_ids or not isinstance(user_ids, list):
                return Response({
                    'error': 'Debes proporcionar una lista de IDs de usuarios'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Filtrar el ID del usuario actual
            user_ids = [uid for uid in user_ids if uid != request.user.id]
            
            if not user_ids:
                return Response({
                    'error': 'No hay usuarios válidos para eliminar'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener usuarios a eliminar
            usuarios = Usuario.objects.filter(id__in=user_ids)
            
            # Si no es superusuario, no puede eliminar superusuarios
            if not request.user.is_superuser:
                # Verificar si hay superusuarios en la lista
                superusuarios_en_lista = usuarios.filter(is_superuser=True).exists()
                if superusuarios_en_lista:
                    return Response({
                        'error': 'Solo los superusuarios pueden eliminar cuentas de superusuario'
                    }, status=status.HTTP_403_FORBIDDEN)
            
            count = usuarios.count()
            usuarios.delete()
            
            return Response({
                'success': True,
                'message': f'{count} usuario{"s" if count != 1 else ""} eliminado{"s" if count != 1 else ""} exitosamente'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error en eliminación masiva: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({
                'error': 'Error al eliminar usuarios'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BulkMakeAdminView(APIView):
    """
    Vista para convertir múltiples usuarios en administradores
    Solo accesible para superusuarios
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Convertir múltiples usuarios en administradores"""
        # Verificar que el usuario actual es superusuario
        if not request.user.is_superuser:
            return Response({
                'error': 'Solo los superusuarios pueden crear administradores'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            user_ids = request.data.get('user_ids', [])
            
            if not user_ids or not isinstance(user_ids, list):
                return Response({
                    'error': 'Debes proporcionar una lista de IDs de usuarios'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Filtrar el ID del usuario actual y superusuarios
            usuarios = Usuario.objects.filter(
                id__in=user_ids,
                is_superuser=False
            ).exclude(id=request.user.id)
            
            if not usuarios.exists():
                return Response({
                    'error': 'No hay usuarios válidos para convertir en administradores'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            count = usuarios.update(is_staff=True)
            
            return Response({
                'success': True,
                'message': f'{count} usuario{"s" if count != 1 else ""} convertido{"s" if count != 1 else ""} en administrador{"es" if count != 1 else ""} exitosamente'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error en conversión masiva: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({
                'error': 'Error al convertir usuarios en administradores'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Vistas para Productos
class ProductoListView(generics.ListCreateAPIView):
    """
    Lista todos los productos o crea uno nuevo (solo admin).
    Para usuarios normales: solo muestra productos no caducados.
    Para admins: muestra todos los productos.
    """
    serializer_class = ProductoSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        from datetime import date
        
        # Si es un usuario admin, mostrar todos los productos
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return Producto.objects.all()
        
        # Para usuarios normales o no autenticados, filtrar productos caducados de categoría Comida
        hoy = date.today()
        # Mostrar todos los productos EXCEPTO los de Comida que ya caducaron (hoy o antes)
        return Producto.objects.exclude(
            Categoria='Comida',
            Fecha_Caducidad__lte=hoy
        )

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ProductoDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Recupera, actualiza o elimina un producto (solo admin puede editar/eliminar).
    """
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    lookup_field = 'id'
    parser_classes = (MultiPartParser, FormParser)

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def perform_update(self, serializer):
        serializer.save(created_by=self.request.user)


# Vista para crear pedidos
class CrearPedidoView(APIView):
    """
    Crea un nuevo pedido con sus detalles.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Lista todos los pedidos con información del usuario y productos (solo para staff).
        """
        if not request.user.is_staff:
            return Response({
                'success': False,
                'error': 'No tienes permisos para ver todos los pedidos'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            return Response(pedidos_service.listar_pedidos_admin(), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        serializer = CrearPedidoSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            pedido = pedidos_service.crear_pedido(request.user, serializer.validated_data)
            return Response({
                'success': True,
                'message': 'Pedido creado exitosamente',
                'id_factura': pedido.id,
                'total': pedido.Total,
                'direccion_envio': pedido.Direccion_Envio,
                'telefono_envio': pedido.Telefono_Envio
            }, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ActualizarPedidoView(APIView):
    """
    Actualiza el estado de un pedido (solo para staff) y crea notificación para el usuario.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, pk):
        nuevo_estado = request.data.get('Estado')
        
        if not nuevo_estado:
            return Response({
                'success': False,
                'error': 'Estado es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar que el estado sea válido
        estados_validos = ['Pendiente', 'Enviado', 'Entregado', 'Devuelto']
        if nuevo_estado not in estados_validos:
            return Response({
                'success': False,
                'error': f'Estado inválido. Valores permitidos: {", ".join(estados_validos)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            pedidos_service.actualizar_estado_pedido(pk, nuevo_estado)
            return Response({
                'success': True,
                'message': f'Pedido actualizado a {nuevo_estado}'
            }, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MisPedidosView(APIView):
    """
    Obtiene todos los pedidos del usuario autenticado con sus productos.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            return Response(
                pedidos_service.listar_pedidos_usuario(request.user.id),
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificacionesView(APIView):
    """
    Obtiene las notificaciones del usuario autenticado.
    Limita automáticamente a las últimas N notificaciones según el tipo de usuario.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Definir límite según tipo de usuario
        limite = 10 if request.user.is_staff else 7
        
        # Obtener todas las notificaciones del usuario ordenadas por fecha
        todas_notificaciones = Notificacion.objects.filter(
            usuario_id=request.user.id
        ).order_by('-Fecha_Creacion')
        
        # Contar cuántas tiene
        total = todas_notificaciones.count()
        
        # Si excede el límite, eliminar las más antiguas
        if total > limite:
            # Obtener IDs de las que se deben mantener (las más recientes)
            ids_mantener = list(todas_notificaciones.values_list('id', flat=True)[:limite])
            
            # Eliminar las que no están en la lista de mantener
            Notificacion.objects.filter(
                usuario_id=request.user.id
            ).exclude(id__in=ids_mantener).delete()
            
            # Obtener las notificaciones actualizadas
            notificaciones = todas_notificaciones.filter(id__in=ids_mantener)
        else:
            # Si no excede el límite, devolver todas
            notificaciones = todas_notificaciones[:limite]
        
        serializer = NotificacionSerializer(notificaciones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MarcarNotificacionLeidaView(APIView):
    """
    Marca una notificación como leída.
    """
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            notificacion = Notificacion.objects.get(
                id=pk,
                usuario_id=request.user.id
            )
            notificacion.Leida = True
            notificacion.save()
            
            return Response({
                'success': True,
                'message': 'Notificación marcada como leída'
            }, status=status.HTTP_200_OK)
        
        except Notificacion.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Notificación no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)


class MarcarTodasLeidasView(APIView):
    """
    Marca todas las notificaciones del usuario como leídas.
    """
    permission_classes = [IsAuthenticated]

    def put(self, request):
        Notificacion.objects.filter(
            usuario_id=request.user.id,
            Leida=False
        ).update(Leida=True)
        
        return Response({
            'success': True,
            'message': 'Todas las notificaciones marcadas como leídas'
        }, status=status.HTTP_200_OK)


class VerificarProductosCaducadosView(APIView):
    """
    Verifica productos caducados de categoría Comida y notifica a los administradores.
    Se ejecuta automáticamente al cargar notificaciones.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from datetime import date
        
        try:
            hoy = date.today()
            
            # Buscar TODOS los productos de categoría Comida que ya caducaron (hoy o antes)
            productos_caducados = Producto.objects.filter(
                Categoria='Comida',
                Fecha_Caducidad__lte=hoy
            )
            
            # Notificar solo si el usuario es admin
            es_admin = getattr(request.user, 'is_staff', False)
            
            if productos_caducados.exists() and es_admin:
                # Solo notificar a admins
                admins = Usuario.objects.filter(is_staff=True)
                
                notificaciones_creadas = 0
                for producto in productos_caducados:
                    for admin in admins:
                        # Verificar si ya existe una notificación para este producto
                        notif_existe = Notificacion.objects.filter(
                            usuario_id=admin.id,
                            Tipo='producto_caducado',
                            Mensaje__contains=f'ID {producto.id}'
                        ).exists()
                        
                        if not notif_existe:
                            # Calcular hace cuánto caducó
                            dias_caducado = (hoy - producto.Fecha_Caducidad).days
                            
                            if dias_caducado == 0:
                                mensaje = f'El producto de comida "{producto.Titulo}" (ID {producto.id}) ha caducado hoy.'
                            elif dias_caducado == 1:
                                mensaje = f'El producto de comida "{producto.Titulo}" (ID {producto.id}) caducó ayer.'
                            else:
                                mensaje = f'El producto de comida "{producto.Titulo}" (ID {producto.id}) caducó hace {dias_caducado} días.'
                            
                            Notificacion.objects.create(
                                usuario=admin,
                                Titulo='Producto Caducado',
                                Mensaje=mensaje,
                                Tipo='producto_caducado'
                            )
                            notificaciones_creadas += 1
                            
                            # Limpiar notificaciones antiguas del admin
                            notifs_admin = Notificacion.objects.filter(usuario_id=admin.id).order_by('-Fecha_Creacion')
                            if notifs_admin.count() > 10:
                                ids_mantener = list(notifs_admin.values_list('id', flat=True)[:10])
                                Notificacion.objects.filter(usuario_id=admin.id).exclude(id__in=ids_mantener).delete()
                
                return Response({
                    'success': True,
                    'productos_caducados': productos_caducados.count(),
                    'notificaciones_creadas': notificaciones_creadas
                }, status=status.HTTP_200_OK)
            
            return Response({
                'success': True,
                'productos_caducados': productos_caducados.count() if productos_caducados.exists() else 0,
                'notificaciones_creadas': 0
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ActualizarPerfilView(APIView):
    """
    Actualiza el perfil del usuario autenticado.
    Permite cambiar nombre, teléfono, dirección, ciudad, edad y contraseña.
    """
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            user = request.user
            data = request.data

            # Validar campos obligatorios
            if not data.get('name') or not data.get('Apellido') or not data.get('Telefono') or not data.get('Address') or not data.get('Ciudad') or not data.get('Edad'):
                return Response({
                    'error': 'Todos los campos son obligatorios'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validar edad y calcular fecha de nacimiento
            try:
                edad = int(data.get('Edad'))
                if edad < 18 or edad > 120:
                    return Response({
                        'error': 'La edad debe estar entre 18 y 120 años'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Calcular fecha de nacimiento aproximada (año actual - edad)
                from datetime import date
                año_nacimiento = date.today().year - edad
                fecha_nacimiento = date(año_nacimiento, 1, 1)
                
            except (ValueError, TypeError):
                return Response({
                    'error': 'La edad debe ser un número válido'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Si se está cambiando la contraseña
            if 'password_actual' in data and 'password_nueva' in data:
                # Verificar contraseña actual
                if not user.check_password(data.get('password_actual')):
                    return Response({
                        'error': 'La contraseña actual es incorrecta'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Validar nueva contraseña
                if len(data.get('password_nueva')) < 6:
                    return Response({
                        'error': 'La contraseña debe tener al menos 6 caracteres'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Cambiar contraseña
                user.set_password(data.get('password_nueva'))

            # Actualizar datos del usuario
            user.Nombre = data.get('name').strip()
            user.Apellido = data.get('Apellido').strip()
            user.Telefono = data.get('Telefono')
            user.Address = data.get('Address')
            user.City = data.get('Ciudad')  # Ciudad va a City
            user.BirthDate = fecha_nacimiento
            user.save()

            return Response({
                'success': True,
                'message': 'Perfil actualizado exitosamente',
                'user': {
                    'id': user.id,
                    'email': user.Email,
                    'name': user.Nombre,
                    'Apellido': user.Apellido,
                    'Telefono': user.Telefono,
                    'Address': user.Address,
                    'Ciudad': user.City,
                    'Edad': edad,
                    'is_staff': user.is_staff
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print("Error en ActualizarPerfilView:")
            print(traceback.format_exc())
            return Response({
                'error': 'Error al actualizar el perfil'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== VISTAS DE RESEÑAS DE PRODUCTOS ====================
from .reviews_serializers import (
    CrearReviewSerializer, ActualizarReviewSerializer,
    ReviewSerializer, ProductoConCalificacionSerializer
)

class ProductReviewsView(APIView):
    """
    Vista para gestionar reseñas de productos
    GET: Obtener todas las reseñas de un producto
    POST: Crear una nueva reseña (usuario autenticado)
    """
    
    def get(self, request, product_id):
        try:
            reviews = ratings_service.listar_resenas_producto(product_id)
            return Response({'reviews': reviews, 'total': len(reviews)}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Error al obtener reseñas'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request, product_id):
        if not request.user.is_authenticated:
            return Response({'error': 'Debes iniciar sesión para dejar una reseña'}, status=status.HTTP_401_UNAUTHORIZED)
        
        data = request.data.copy()
        data['Id_Products'] = product_id
        
        serializer = CrearReviewSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            ratings_service.crear_resena(
                request.user.id,
                product_id,
                serializer.validated_data['Rating'],
                serializer.validated_data.get('Comentario', ''),
            )
            return Response({'message': 'Reseña creada exitosamente'}, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Error al crear la reseña'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserReviewView(APIView):
    """
    Vista para gestionar la reseña propia del usuario
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, product_id):
        try:
            review = ratings_service.obtener_resena_usuario(request.user.id, product_id)
            return Response({'review': review}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Error al obtener la reseña'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request, product_id):
        serializer = ActualizarReviewSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            ratings_service.actualizar_resena(
                request.user.id,
                product_id,
                serializer.validated_data['Rating'],
                serializer.validated_data.get('Comentario', ''),
            )
            return Response({'message': 'Reseña actualizada exitosamente'}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'Error al actualizar la reseña'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, product_id):
        try:
            ratings_service.eliminar_resena(request.user.id, product_id)
            return Response({'message': 'Reseña eliminada exitosamente'}, status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'Error al eliminar la reseña'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductRatingsView(APIView):
    """
    Vista para obtener estadísticas de calificación de productos
    """
    
    def get(self, request, product_id=None):
        try:
            if product_id:
                rating = ratings_service.obtener_rating_producto(product_id)
                return Response({'rating': rating}, status=status.HTTP_200_OK)
            ratings = ratings_service.obtener_ratings_todos()
            return Response({'ratings': ratings}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Error al obtener calificaciones'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


