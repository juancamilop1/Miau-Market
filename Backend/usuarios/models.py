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
    Telefono = models.CharField(max_length=20)
    Address = models.CharField(max_length=40)
    City = models.CharField(max_length=40)
    BirthDate = models.DateField()
    FechaRegistro = models.DateTimeField(auto_now_add=True, db_column='FechaRegistro')
    
    # Campos requeridos por Django
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = UsuarioManager()

    USERNAME_FIELD = 'Email'
    REQUIRED_FIELDS = ['Nombre', 'Apellido', 'Telefono', 'Address', 'City', 'BirthDate']

    class Meta:
        db_table = 'Users'  # Nombre exacto de la tabla en MySQL

    def __str__(self):
        return f"{self.Nombre} {self.Apellido}"


class Producto(models.Model):
    id = models.AutoField(primary_key=True, db_column='Id_Products')
    Titulo = models.CharField(max_length=150)
    Descripcion = models.TextField(null=True, blank=True)
    Categoria = models.CharField(max_length=100, null=True, blank=True)
    Precio = models.IntegerField()
    Stock = models.IntegerField(default=0)
    Imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    Fecha_creacion = models.DateTimeField(auto_now_add=True, db_column='Fecha_creacion')
    Fecha_Caducidad = models.DateField(db_column='Fecha_Caducidad', default='2025-12-31')  # Campo obligatorio para fecha de caducidad
    created_by = models.ForeignKey(Usuario, null=True, blank=True, on_delete=models.SET_NULL, db_column='created_by')

    class Meta:
        db_table = 'Products'

    def __str__(self):
        return self.Titulo


class Notificacion(models.Model):
    id = models.AutoField(primary_key=True, db_column='Id_Notificacion')
    Id_User = models.IntegerField()  # ID del usuario que recibe la notificación
    Titulo = models.CharField(max_length=200)
    Mensaje = models.TextField()
    Tipo = models.CharField(max_length=50)  # 'pedido_confirmado', 'pedido_enviado', 'pedido_entregado', 'pedido_devuelto'
    Id_Factura = models.IntegerField(null=True, blank=True)  # ID del pedido relacionado
    Leida = models.BooleanField(default=False)
    Fecha_Creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Notificaciones'
        ordering = ['-Fecha_Creacion']

    def __str__(self):
        return f"Notificación {self.id} para usuario {self.Id_User}"
