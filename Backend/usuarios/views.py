from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from usuarios.serializers import RegistroSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

class RegistroUsuario(generics.CreateAPIView):
    """
    Vista para registrar nuevos usuarios.
    Permite enviar los datos mediante un método POST y guarda el usuario en la base de datos.
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegistroSerializer


class LoginUsuario(ObtainAuthToken):
    """
    Vista para iniciar sesión.
    Si el usuario y la contraseña son correctos, devuelve un token de autenticación.
    """
    def post(self, request, *args, **kwargs):
        response = super(LoginUsuario, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        return Response({
            'token': token.key,
            'usuario_id': token.user_id,
            'usuario': token.user.username
        })
