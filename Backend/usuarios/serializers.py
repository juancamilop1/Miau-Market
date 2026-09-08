from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Producto
from datetime import date
import re

Usuario = get_user_model()

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ('id', 'Username', 'Nombre', 'Apellido', 'Email', 'Telefono', 'Address', 'City', 'BirthDate', 'FechaRegistro', 'is_staff')
        read_only_fields = ('id', 'FechaRegistro', 'is_staff')

class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    Telefono = serializers.CharField(required=True, max_length=20)
    Address = serializers.CharField(required=True, max_length=40)
    Username = serializers.CharField(required=True, max_length=50)

    class Meta:
        model = Usuario
        fields = ('Username', 'Nombre', 'Apellido', 'Email', 'password', 'password2', 'Telefono',
                 'Address', 'City', 'BirthDate')

    def validate_Email(self, value):
        return value.strip().lower()

    def validate_Username(self, value):
        username = value.strip().lower()
        if not re.match(r'^[a-z0-9_]+$', username):
            raise serializers.ValidationError(
                'El usuario solo puede contener letras, numeros y guion bajo.'
            )
        if Usuario.objects.filter(Username__iexact=username).exists():
            raise serializers.ValidationError('Este nombre de usuario ya esta registrado.')
        return username

    def validate_BirthDate(self, value):
        """Validar que el usuario sea mayor de 18 años"""
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        
        if age < 18:
            raise serializers.ValidationError("Debes ser mayor de 18 años para registrarte.")
        
        return value

    def validate_Telefono(self, value):
        """Validar que el teléfono no esté vacío y no contenga +57"""
        if not value or value.strip() == '':
            raise serializers.ValidationError("El teléfono es obligatorio.")
        
        # Verificar que no contenga +57
        if '+57' in value or '+' in value:
            raise serializers.ValidationError("No agregues el código de país (+57). Solo ingresa el número de teléfono.")
        
        # Verificar que el teléfono no esté duplicado
        if Usuario.objects.filter(Telefono=value).exists():
            raise serializers.ValidationError("Este número de teléfono ya está registrado.")
        
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        
        # Verificar que la combinación Nombre + Apellido no esté duplicada
        nombre = attrs.get('Nombre')
        apellido = attrs.get('Apellido')
        
        if Usuario.objects.filter(Nombre=nombre, Apellido=apellido).exists():
            raise serializers.ValidationError({
                "Nombre": "Ya existe un usuario registrado con este nombre y apellido."
            })
        
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        Email = validated_data.pop('Email')
        Username = validated_data.pop('Username')
        user = Usuario.objects.create_user(
            Email=Email,
            Username=Username,
            password=password,
            **validated_data
        )
        return user


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ('id', 'Titulo', 'Descripcion', 'Categoria', 'Precio', 'Stock', 'Imagen', 'Fecha_creacion', 'Fecha_Caducidad', 'created_by')
        read_only_fields = ('id', 'Fecha_creacion', 'created_by')
    
    def to_representation(self, instance):
        """Cambiar 'id' a 'Id_Products' en la respuesta"""
        data = super().to_representation(instance)
        data['Id_Products'] = data.pop('id')
        return data


class AdminUsuarioUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Usuario
        fields = (
            'Username', 'Nombre', 'Apellido', 'Email', 'Telefono',
            'Address', 'City', 'BirthDate', 'is_staff', 'is_superuser', 'is_active', 'password',
        )

    def validate_Email(self, value):
        email = value.strip().lower()
        qs = Usuario.objects.filter(Email__iexact=email)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Este correo ya esta registrado.')
        return email

    def validate_Username(self, value):
        username = value.strip().lower()
        if not re.match(r'^[a-z0-9_]+$', username):
            raise serializers.ValidationError(
                'El usuario solo puede contener letras, numeros y guion bajo.'
            )
        qs = Usuario.objects.filter(Username__iexact=username)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Este nombre de usuario ya esta registrado.')
        return username

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

