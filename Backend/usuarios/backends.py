from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

Usuario = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    """Autentica por correo o nombre de usuario; email y contraseña sin distinguir mayusculas."""

    def authenticate(self, request, login=None, password=None, **kwargs):
        identificador = login or kwargs.get('Email') or kwargs.get('username')
        if not identificador or not password:
            return None

        identificador = identificador.strip()
        usuario = (
            Usuario.objects.filter(Email__iexact=identificador).first()
            or Usuario.objects.filter(Username__iexact=identificador).first()
        )
        if not usuario or not usuario.is_active:
            return None

        clave = password.casefold()
        if usuario.check_password(clave) or usuario.check_password(password):
            return usuario
        return None

    def get_user(self, user_id):
        try:
            return Usuario.objects.get(pk=user_id)
        except Usuario.DoesNotExist:
            return None
