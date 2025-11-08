from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Producto

Usuario = get_user_model()

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ('id', 'Nombre', 'Apellido', 'Email', 'Telefono', 'Address', 'City', 'BirthDate', 'FechaRegistro', 'is_staff')
        read_only_fields = ('id', 'FechaRegistro', 'is_staff')

class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Usuario
        fields = ('Nombre', 'Apellido', 'Email', 'password', 'password2', 'Telefono', 
                 'Address', 'City', 'BirthDate')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        Email = validated_data.pop('Email')  # Get and remove Email from validated_data
        user = Usuario.objects.create_user(
            Email=Email,  # Pass Email with correct case
            password=password,
            **validated_data
        )
        return user


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ('id', 'Titulo', 'Descripcion', 'Categoria', 'Precio', 'Stock', 'Imagen', 'Fecha_creacion', 'created_by')
        read_only_fields = ('id', 'Fecha_creacion', 'created_by')
    
    def to_representation(self, instance):
        """Cambiar 'id' a 'Id_Products' en la respuesta"""
        data = super().to_representation(instance)
        data['Id_Products'] = data.pop('id')
        return data

