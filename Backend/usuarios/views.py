from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model
from .serializers import RegistroSerializer, UsuarioSerializer, ProductoSerializer
from .models import Producto
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
                
                # Devolvemos la información del usuario con token e is_staff
                return Response({
                    'success': True,
                    'token': token.key,
                    'user': {
                        'id': user.id,
                        'email': user.Email,
                        'nombre': user.Nombre,
                        'is_staff': user.is_staff
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
    """
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    parser_classes = (MultiPartParser, FormParser)

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

