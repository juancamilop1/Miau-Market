from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    login = serializers.CharField(required=False, allow_blank=True)
    Email = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        identificador = (attrs.get('login') or attrs.get('Email') or '').strip()
        if not identificador:
            raise serializers.ValidationError({'login': 'Ingresa tu correo o usuario.'})
        attrs['login'] = identificador
        return attrs
