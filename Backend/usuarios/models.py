from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class UsuarioManager(BaseUserManager):
    def create_user(self, Email, password=None, **extra_fields):
        if not Email:
            raise ValueError('El Email es obligatorio')
        Email = self.normalize_email(Email)
        user = self.model(Email=Email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, Email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(Email, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True, db_column='Id_User')
    Nombre = models.CharField(max_length=100)
    Apellido = models.CharField(max_length=100)
    Email = models.EmailField(max_length=150, unique=True)
    Telefono = models.CharField(max_length=20, null=True)
    Address = models.CharField(max_length=40)
    City = models.CharField(max_length=40)
    BirthDate = models.DateField()
    FechaRegistro = models.DateTimeField(auto_now_add=True, db_column='FechaRegistro')
    
    # Campos requeridos por Django
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = UsuarioManager()

    USERNAME_FIELD = 'Email'
    REQUIRED_FIELDS = ['Nombre', 'Apellido', 'Address', 'City', 'BirthDate']

    class Meta:
        db_table = 'Users'  # Nombre exacto de la tabla en MySQL

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
