from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db import transaction
from .serializers import RegistroSerializer, UsuarioSerializer, ProductoSerializer
from .pedidos_serializers import CrearPedidoSerializer
from .notificaciones_serializers import NotificacionSerializer
from .models import Producto, Notificacion
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
    Vista para iniciar sesión usando Email.
    Solo requiere Email y password.
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['Email']
            password = serializer.validated_data['password']
            
            # Autenticar usuario
            user = authenticate(request, Email=email, password=password)
            
            if user:
                # Obtener o crear token
                token, created = Token.objects.get_or_create(user=user)
                
                # Calcular edad a partir de fecha de nacimiento
                from datetime import date
                today = date.today()
                edad = today.year - user.BirthDate.year - ((today.month, today.day) < (user.BirthDate.month, user.BirthDate.day))
                
                # Devolvemos la información del usuario con token e is_staff
                return Response({
                    'success': True,
                    'token': token.key,
                    'user': {
                        'id': user.id,
                        'email': user.Email,
                        'name': user.Nombre,
                        'Apellido': user.Apellido,
                        'is_staff': user.is_staff,
                        'Address': user.Address,
                        'Telefono': user.Telefono,
                        'Ciudad': user.City,
                        'Edad': edad
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Email o contraseña incorrectos'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UsuarioListView(generics.ListCreateAPIView):
    """
    Lista todos los usuarios o crea uno nuevo.
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]

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
            return [IsAuthenticated()]
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        print("Datos recibidos:", request.data)
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Errores de validación:", serializer.errors)
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
            from django.db import connection
            with connection.cursor() as cursor:
                # Obtener pedidos
                cursor.execute("""
                    SELECT 
                        p.Id_Factura,
                        p.Id_User,
                        p.Fecha,
                        p.Total,
                        p.Metodo_Pago,
                        p.Estado,
                        p.Direccion_Envio,
                        p.Telefono_Envio,
                        u.Nombre,
                        u.Apellido,
                        u.Email
                    FROM PaymentOrders p
                    LEFT JOIN Users u ON p.Id_User = u.Id_User
                    ORDER BY p.Fecha DESC
                """)
                
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
                # Formatear datos para el frontend
                orders = []
                for row in results:
                    # Obtener productos de este pedido
                    cursor.execute("""
                        SELECT 
                            od.Id_Products,
                            od.Cantidad,
                            od.Precio_Unitario,
                            od.Subtotal,
                            pr.Titulo
                        FROM Orders_Details od
                        LEFT JOIN Products pr ON od.Id_Products = pr.Id_Products
                        WHERE od.Id_Factura = %s
                    """, [row['Id_Factura']])
                    
                    productos_cols = [col[0] for col in cursor.description]
                    productos = [dict(zip(productos_cols, prod)) for prod in cursor.fetchall()]
                    
                    orders.append({
                        'Id_Factura': row['Id_Factura'],
                        'Id_User': row['Id_User'],
                        'Fecha': row['Fecha'],
                        'Total': row['Total'],
                        'Metodo_Pago': row['Metodo_Pago'],
                        'Estado': row['Estado'],
                        'Direccion_Envio': row['Direccion_Envio'],
                        'Telefono_Envio': row['Telefono_Envio'],
                        'usuario_nombre': f"{row['Nombre']} {row['Apellido']}" if row['Nombre'] else 'N/A',
                        'usuario_email': row['Email'] or 'N/A',
                        'productos': productos
                    })
                
                return Response(orders, status=status.HTTP_200_OK)
        
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
            with transaction.atomic():
                # Obtener datos validados
                data = serializer.validated_data
                
                # Crear la orden de pago
                from django.db import connection
                with connection.cursor() as cursor:
                    # Primero verificar que hay suficiente stock para todos los productos
                    for producto in data['productos']:
                        cursor.execute("""
                            SELECT Stock FROM Products WHERE Id_Products = %s
                        """, [producto['Id_Products']])
                        
                        result = cursor.fetchone()
                        if not result:
                            return Response({
                                'success': False,
                                'error': f'Producto con ID {producto["Id_Products"]} no encontrado'
                            }, status=status.HTTP_404_NOT_FOUND)
                        
                        stock_disponible = result[0]
                        if stock_disponible < producto['Cantidad']:
                            return Response({
                                'success': False,
                                'error': f'Stock insuficiente para el producto ID {producto["Id_Products"]}. Disponible: {stock_disponible}, Solicitado: {producto["Cantidad"]}'
                            }, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Si hay suficiente stock, proceder con la creación del pedido
                    # Insertar en PaymentOrders con dirección y teléfono
                    cursor.execute("""
                        INSERT INTO PaymentOrders (Id_User, Fecha, Total, Metodo_Pago, Estado, Direccion_Envio, Telefono_Envio)
                        VALUES (%s, NOW(), %s, %s, 'Pendiente', %s, %s)
                    """, [
                        data['Id_User'],
                        data['Total'],
                        data['Metodo_Pago'],
                        data['direccion_envio'],
                        data['telefono_envio']
                    ])
                    
                    # Obtener el ID de la factura recién creada
                    cursor.execute("SELECT LAST_INSERT_ID()")
                    id_factura = cursor.fetchone()[0]
                    
                    # Insertar los detalles de cada producto y restar del stock
                    for producto in data['productos']:
                        subtotal = producto['Cantidad'] * producto['Precio_Unitario']
                        
                        # Insertar detalle del pedido
                        cursor.execute("""
                            INSERT INTO Orders_Details 
                            (Id_Factura, Id_Products, Cantidad, Precio_Unitario, Subtotal)
                            VALUES (%s, %s, %s, %s, %s)
                        """, [
                            id_factura,
                            producto['Id_Products'],
                            producto['Cantidad'],
                            producto['Precio_Unitario'],
                            subtotal
                        ])
                        
                        # Restar del stock
                        cursor.execute("""
                            UPDATE Products 
                            SET Stock = Stock - %s 
                            WHERE Id_Products = %s
                        """, [
                            producto['Cantidad'],
                            producto['Id_Products']
                        ])
                
                # Crear notificación para todos los admins
                admins = Usuario.objects.filter(is_staff=True)
                for admin in admins:
                    Notificacion.objects.create(
                        Id_User=admin.id,
                        Titulo='Nuevo Pedido Recibido',
                        Mensaje=f'Se ha confirmado un nuevo pedido #{id_factura} por COP {data["Total"]}',
                        Tipo='nuevo_pedido',
                        Id_Factura=id_factura
                    )
                    
                    # Limpiar notificaciones antiguas del admin (mantener solo las últimas 10)
                    notifs_admin = Notificacion.objects.filter(Id_User=admin.id).order_by('-Fecha_Creacion')
                    if notifs_admin.count() > 10:
                        ids_mantener = list(notifs_admin.values_list('id', flat=True)[:10])
                        Notificacion.objects.filter(Id_User=admin.id).exclude(id__in=ids_mantener).delete()
                
                return Response({
                    'success': True,
                    'message': 'Pedido creado exitosamente',
                    'id_factura': id_factura,
                    'direccion_envio': data['direccion_envio'],
                    'telefono_envio': data['telefono_envio']
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
            from django.db import connection
            with connection.cursor() as cursor:
                # Obtener información del pedido y usuario
                cursor.execute("""
                    SELECT Id_User, Total FROM PaymentOrders WHERE Id_Factura = %s
                """, [pk])
                
                pedido_info = cursor.fetchone()
                if not pedido_info:
                    return Response({
                        'success': False,
                        'error': 'Pedido no encontrado'
                    }, status=status.HTTP_404_NOT_FOUND)
                
                id_user, total = pedido_info
                
                # Actualizar estado del pedido
                cursor.execute("""
                    UPDATE PaymentOrders 
                    SET Estado = %s 
                    WHERE Id_Factura = %s
                """, [nuevo_estado, pk])
            
            # Crear notificación para el usuario
            mensajes = {
                'Pendiente': f'Tu pedido #{pk} está pendiente de procesamiento.',
                'Enviado': f'¡Tu pedido #{pk} ha sido enviado! Pronto llegará a tu dirección.',
                'Entregado': f'Tu pedido #{pk} ha sido entregado. ¡Gracias por tu compra!',
                'Devuelto': f'Tu pedido #{pk} ha sido devuelto.'
            }
            
            try:
                usuario = Usuario.objects.get(id=id_user)
                Notificacion.objects.create(
                    Id_User=usuario.id,
                    Titulo=f'Pedido {nuevo_estado}',
                    Mensaje=mensajes[nuevo_estado],
                    Tipo=nuevo_estado.lower(),
                    Id_Factura=pk
                )
                
                # Limpiar notificaciones antiguas del usuario (mantener solo las últimas 7)
                notifs_usuario = Notificacion.objects.filter(Id_User=usuario.id).order_by('-Fecha_Creacion')
                if notifs_usuario.count() > 7:
                    ids_mantener = list(notifs_usuario.values_list('id', flat=True)[:7])
                    Notificacion.objects.filter(Id_User=usuario.id).exclude(id__in=ids_mantener).delete()
                    
            except Usuario.DoesNotExist:
                pass  # Si no se encuentra el usuario, continuar sin crear notificación
            
            return Response({
                'success': True,
                'message': f'Pedido actualizado a {nuevo_estado}'
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MisPedidosView(APIView):
    """
    Obtiene todos los pedidos del usuario autenticado con sus productos.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            from django.db import connection
            
            cursor = connection.cursor()
            
            # Obtener pedidos del usuario autenticado
            cursor.execute("""
                SELECT 
                    po.Id_Factura,
                    po.Total,
                    po.Fecha,
                    po.Estado,
                    po.Direccion_Envio,
                    po.Telefono_Envio
                FROM PaymentOrders po
                WHERE po.Id_User = %s
                ORDER BY po.Fecha DESC
            """, [request.user.id])
            
            columns = [col[0] for col in cursor.description]
            pedidos_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Para cada pedido, obtener sus productos
            orders = []
            for row in pedidos_data:
                cursor.execute("""
                    SELECT 
                        od.Id_Products,
                        od.Cantidad,
                        od.Precio_Unitario,
                        p.Titulo,
                        p.Imagen
                    FROM Orders_Details od
                    INNER JOIN Products p ON od.Id_Products = p.Id_Products
                    WHERE od.Id_Factura = %s
                """, [row['Id_Factura']])
                
                productos_columns = [col[0] for col in cursor.description]
                productos = [dict(zip(productos_columns, prod_row)) for prod_row in cursor.fetchall()]
                
                orders.append({
                    'Id_Factura': row['Id_Factura'],
                    'Total': row['Total'],
                    'Fecha_Compra': row['Fecha'],
                    'Estado': row['Estado'],
                    'Direccion_Envio': row['Direccion_Envio'],
                    'Telefono_Envio': row['Telefono_Envio'],
                    'productos': productos
                })
            
            return Response(orders, status=status.HTTP_200_OK)
        
        except Exception as e:
            import traceback
            print("Error en MisPedidosView:")
            print(traceback.format_exc())
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
            Id_User=request.user.id
        ).order_by('-Fecha_Creacion')
        
        # Contar cuántas tiene
        total = todas_notificaciones.count()
        
        # Si excede el límite, eliminar las más antiguas
        if total > limite:
            # Obtener IDs de las que se deben mantener (las más recientes)
            ids_mantener = list(todas_notificaciones.values_list('id', flat=True)[:limite])
            
            # Eliminar las que no están en la lista de mantener
            Notificacion.objects.filter(
                Id_User=request.user.id
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
                Id_User=request.user.id
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
            Id_User=request.user.id,
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
                            Id_User=admin.id,
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
                                Id_User=admin.id,
                                Titulo='⚠️ Producto Caducado',
                                Mensaje=mensaje,
                                Tipo='producto_caducado'
                            )
                            notificaciones_creadas += 1
                            
                            # Limpiar notificaciones antiguas del admin
                            notifs_admin = Notificacion.objects.filter(Id_User=admin.id).order_by('-Fecha_Creacion')
                            if notifs_admin.count() > 10:
                                ids_mantener = list(notifs_admin.values_list('id', flat=True)[:10])
                                Notificacion.objects.filter(Id_User=admin.id).exclude(id__in=ids_mantener).delete()
                
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
from .reviews_serializers import CrearReviewSerializer, ReviewSerializer, ProductoConCalificacionSerializer
from django.db import connection

class ProductReviewsView(APIView):
    """
    Vista para gestionar reseñas de productos
    GET: Obtener todas las reseñas de un producto
    POST: Crear una nueva reseña (usuario autenticado)
    """
    
    def get(self, request, product_id):
        """Obtener todas las reseñas de un producto específico"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        r.Id_Review,
                        r.Id_Products,
                        r.Id_User,
                        u.Nombre,
                        u.Apellido,
                        r.Rating,
                        r.Comentario,
                        r.Fecha
                    FROM Product_Reviews r
                    INNER JOIN Users u ON r.Id_User = u.Id_User
                    WHERE r.Id_Products = %s
                    ORDER BY r.Fecha DESC
                """, [product_id])
                
                columns = [col[0] for col in cursor.description]
                reviews = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
            return Response({
                'reviews': reviews,
                'total': len(reviews)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error al obtener reseñas: {str(e)}")
            return Response({
                'error': 'Error al obtener reseñas'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request, product_id):
        """Crear una nueva reseña para un producto"""
        if not request.user.is_authenticated:
            return Response({
                'error': 'Debes iniciar sesión para dejar una reseña'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Agregar el product_id y user_id a los datos
        data = request.data.copy()
        data['Id_Products'] = product_id
        
        serializer = CrearReviewSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with connection.cursor() as cursor:
                # Verificar si el usuario ya dejó una reseña para este producto
                cursor.execute("""
                    SELECT Id_Review FROM Product_Reviews 
                    WHERE Id_User = %s AND Id_Products = %s
                """, [request.user.id, product_id])
                
                existing_review = cursor.fetchone()
                
                if existing_review:
                    return Response({
                        'error': 'Ya has dejado una reseña para este producto'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Insertar nueva reseña
                cursor.execute("""
                    INSERT INTO Product_Reviews (Id_Products, Id_User, Rating, Comentario)
                    VALUES (%s, %s, %s, %s)
                """, [
                    product_id,
                    request.user.id,
                    serializer.validated_data['Rating'],
                    serializer.validated_data.get('Comentario', '')
                ])
                
            return Response({
                'message': 'Reseña creada exitosamente'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"Error al crear reseña: {str(e)}")
            return Response({
                'error': 'Error al crear la reseña'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserReviewView(APIView):
    """
    Vista para gestionar la reseña propia del usuario
    GET: Obtener la reseña del usuario para un producto
    PUT: Actualizar la reseña del usuario
    DELETE: Eliminar la reseña del usuario
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, product_id):
        """Obtener la reseña del usuario para un producto específico"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT Id_Review, Id_Products, Id_User, Rating, Comentario, Fecha
                    FROM Product_Reviews
                    WHERE Id_User = %s AND Id_Products = %s
                """, [request.user.id, product_id])
                
                row = cursor.fetchone()
                if not row:
                    return Response({
                        'review': None
                    }, status=status.HTTP_200_OK)
                
                columns = [col[0] for col in cursor.description]
                review = dict(zip(columns, row))
                
            return Response({
                'review': review
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error al obtener reseña del usuario: {str(e)}")
            return Response({
                'error': 'Error al obtener la reseña'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request, product_id):
        """Actualizar la reseña del usuario"""
        serializer = CrearReviewSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE Product_Reviews
                    SET Rating = %s, Comentario = %s
                    WHERE Id_User = %s AND Id_Products = %s
                """, [
                    serializer.validated_data['Rating'],
                    serializer.validated_data.get('Comentario', ''),
                    request.user.id,
                    product_id
                ])
                
                if cursor.rowcount == 0:
                    return Response({
                        'error': 'No se encontró la reseña'
                    }, status=status.HTTP_404_NOT_FOUND)
                
            return Response({
                'message': 'Reseña actualizada exitosamente'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error al actualizar reseña: {str(e)}")
            return Response({
                'error': 'Error al actualizar la reseña'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, product_id):
        """Eliminar la reseña del usuario"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM Product_Reviews
                    WHERE Id_User = %s AND Id_Products = %s
                """, [request.user.id, product_id])
                
                if cursor.rowcount == 0:
                    return Response({
                        'error': 'No se encontró la reseña'
                    }, status=status.HTTP_404_NOT_FOUND)
                
            return Response({
                'message': 'Reseña eliminada exitosamente'
            }, status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            print(f"Error al eliminar reseña: {str(e)}")
            return Response({
                'error': 'Error al eliminar la reseña'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductRatingsView(APIView):
    """
    Vista para obtener estadísticas de calificación de productos
    GET: Obtener calificación promedio y distribución de estrellas
    """
    
    def get(self, request, product_id=None):
        """Obtener estadísticas de calificación"""
        try:
            with connection.cursor() as cursor:
                if product_id:
                    # Obtener rating de un producto específico
                    cursor.execute("""
                        SELECT * FROM Product_Ratings
                        WHERE Id_Products = %s
                    """, [product_id])
                else:
                    # Obtener ratings de todos los productos
                    cursor.execute("SELECT * FROM Product_Ratings")
                
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                ratings = [dict(zip(columns, row)) for row in rows]
                
            if product_id:
                return Response({
                    'rating': ratings[0] if ratings else None
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'ratings': ratings
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            print(f"Error al obtener ratings: {str(e)}")
            return Response({
                'error': 'Error al obtener calificaciones'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


