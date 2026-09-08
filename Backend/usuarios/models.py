from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator


class UsuarioManager(BaseUserManager):
    def create_user(self, Email, password=None, **extra_fields):
        if not Email:
            raise ValueError('El Email es obligatorio')
        Email = self.normalize_email(Email).lower()
        username = extra_fields.get('Username')
        if username:
            extra_fields['Username'] = username.strip().lower()
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
    Username = models.CharField(max_length=50, unique=True, db_column='Username')
    Nombre = models.CharField(max_length=100)
    Apellido = models.CharField(max_length=100)
    Email = models.EmailField(max_length=150, unique=True)
    Telefono = models.CharField(max_length=20)
    Address = models.CharField(max_length=40)
    City = models.CharField(max_length=40)
    BirthDate = models.DateField()
    FechaRegistro = models.DateTimeField(auto_now_add=True, db_column='FechaRegistro')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'Email'
    REQUIRED_FIELDS = ['Username', 'Nombre', 'Apellido', 'Telefono', 'Address', 'City', 'BirthDate']

    class Meta:
        db_table = 'Users'

    def set_password(self, raw_password):
        if raw_password:
            raw_password = raw_password.casefold()
        super().set_password(raw_password)

    def __str__(self):
        return f'{self.Nombre} {self.Apellido}'


class Producto(models.Model):
    id = models.AutoField(primary_key=True, db_column='Id_Products')
    Titulo = models.CharField(max_length=150)
    Descripcion = models.TextField(null=True, blank=True)
    Categoria = models.CharField(max_length=100, null=True, blank=True)
    Precio = models.IntegerField()
    Stock = models.IntegerField(default=0)
    Imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    Fecha_creacion = models.DateTimeField(auto_now_add=True, db_column='Fecha_creacion')
    Fecha_Caducidad = models.DateField(db_column='Fecha_Caducidad', default='2025-12-31')
    created_by = models.ForeignKey(
        Usuario, null=True, blank=True, on_delete=models.SET_NULL, db_column='created_by'
    )

    class Meta:
        db_table = 'Products'

    def __str__(self):
        return self.Titulo


class Pedido(models.Model):
    ESTADOS = ('Pendiente', 'Enviado', 'Entregado', 'Devuelto')

    id = models.AutoField(primary_key=True, db_column='Id_Factura')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='Id_User', related_name='pedidos')
    Fecha = models.DateTimeField(auto_now_add=True)
    Total = models.DecimalField(max_digits=10, decimal_places=2)
    Metodo_Pago = models.CharField(max_length=50, blank=True)
    Estado = models.CharField(max_length=50, default='Pendiente')
    Direccion_Envio = models.CharField(max_length=200, blank=True)
    Telefono_Envio = models.CharField(max_length=20, blank=True)

    class Meta:
        db_table = 'PaymentOrders'
        ordering = ['-Fecha']

    def __str__(self):
        return f'Pedido #{self.id}'


class DetallePedido(models.Model):
    id = models.AutoField(primary_key=True, db_column='Id_Detalle')
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, db_column='Id_Factura', related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, db_column='Id_Products')
    Cantidad = models.IntegerField()
    Precio_Unitario = models.DecimalField(max_digits=10, decimal_places=2)
    Subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'Orders_Details'

    def __str__(self):
        return f'Detalle #{self.id} pedido #{self.pedido_id}'


class ResenaProducto(models.Model):
    id = models.AutoField(primary_key=True, db_column='Id_Review')
    producto = models.ForeignKey(
        Producto, on_delete=models.CASCADE, db_column='Id_Products', related_name='resenas'
    )
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, db_column='Id_User', related_name='resenas'
    )
    Rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    Comentario = models.TextField(blank=True)
    Fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Product_Reviews'
        constraints = [
            models.UniqueConstraint(fields=['usuario', 'producto'], name='uk_reviews_user_product'),
        ]

    def __str__(self):
        return f'Resena {self.id} producto {self.producto_id}'


class Notificacion(models.Model):
    id = models.AutoField(primary_key=True, db_column='Id_Notificacion')
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, db_column='Id_User', related_name='notificaciones'
    )
    Titulo = models.CharField(max_length=200)
    Mensaje = models.TextField()
    Tipo = models.CharField(max_length=50)
    pedido = models.ForeignKey(
        Pedido, null=True, blank=True, on_delete=models.SET_NULL, db_column='Id_Factura'
    )
    Leida = models.BooleanField(default=False)
    Fecha_Creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Notificaciones'
        ordering = ['-Fecha_Creacion']

    def __str__(self):
        return f'Notificacion {self.id} usuario {self.usuario_id}'


class MiauBotConfig(models.Model):
    """Configuracion y personalidad del chatbot (singleton activo)."""
    nombre_bot = models.CharField(max_length=50, default='MiauBot')
    prompt_sistema = models.TextField(
        help_text='Instrucciones internas de personalidad y tono del bot'
    )
    mensaje_bienvenida = models.TextField()
    mensaje_bienvenida_retorno = models.TextField(
        blank=True,
        help_text='Saludo cuando el usuario ya tiene sesion. Use {nombre} para personalizar.'
    )
    activo = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'MiauBot_Config'
        verbose_name = 'Configuracion MiauBot'

    def __str__(self):
        return self.nombre_bot


class MiauBotConocimiento(models.Model):
    """Base de conocimiento: consejos por animal y tema."""
    ANIMALES = (
        ('gato', 'Gato'),
        ('perro', 'Perro'),
        ('general', 'General'),
    )
    animal = models.CharField(max_length=20, choices=ANIMALES, default='gato')
    tema = models.CharField(max_length=50)
    palabras_clave = models.TextField(help_text='Palabras separadas por coma')
    respuesta = models.TextField()
    prioridad = models.PositiveSmallIntegerField(default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'MiauBot_Conocimiento'
        ordering = ['-prioridad', 'tema']
        verbose_name_plural = 'Conocimientos MiauBot'

    def __str__(self):
        return f'{self.animal} - {self.tema}'


class MiauBotFrase(models.Model):
    """Frases variadas para respuestas naturales."""
    TIPOS = (
        ('saludo', 'Saludo'),
        ('intro_producto', 'Intro productos'),
        ('cierre_producto', 'Cierre productos'),
        ('empatia', 'Empatia'),
        ('despedida', 'Despedida'),
    )
    tipo = models.CharField(max_length=30, choices=TIPOS)
    animal = models.CharField(max_length=20, default='general')
    texto = models.TextField()
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'MiauBot_Frases'

    def __str__(self):
        return f'{self.tipo}: {self.texto[:40]}'


class MiauBotAprendizaje(models.Model):
    """Preguntas de usuarios y respuestas — aprendizaje supervisado."""
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    )
    pregunta = models.TextField()
    respuesta = models.TextField()
    palabras_clave = models.TextField(blank=True, help_text='Auto-generadas desde la pregunta')
    animal = models.CharField(max_length=20, default='general')
    usuario_id = models.IntegerField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    veces_usada = models.PositiveIntegerField(default=0)
    Fecha_Creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'MiauBot_Aprendizaje'
        ordering = ['-Fecha_Creacion']
        verbose_name = 'Aprendizaje MiauBot'
        verbose_name_plural = 'Aprendizajes MiauBot'

    def __str__(self):
        return self.pregunta[:60]


class MiauBotMemoriaUsuario(models.Model):
    """Memoria persistente del chatbot por usuario: mascotas y temas de seguimiento."""
    usuario_id = models.IntegerField(unique=True)
    mascotas = models.JSONField(default=list, blank=True)
    seguimiento = models.JSONField(default=dict, blank=True)
    mascota_activa_idx = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'MiauBot_Memoria'
        verbose_name = 'Memoria MiauBot'
        verbose_name_plural = 'Memorias MiauBot'

    def __str__(self):
        return f'Memoria usuario {self.usuario_id}'
