from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import RegistroSerializer, UsuarioSerializer
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
                # Por ahora, solo devolvemos la información del usuario sin token
                return Response({
                    'success': True,
                    'user': {
                        'id': user.id,
                        'email': user.Email,
                        'nombre': user.Nombre
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
