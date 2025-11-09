from rest_framework import serializers
from .models import Usuario, Producto

class DetallePedidoSerializer(serializers.Serializer):
    Id_Products = serializers.IntegerField()
    Cantidad = serializers.IntegerField()
    Precio_Unitario = serializers.DecimalField(max_digits=10, decimal_places=2)

class CrearPedidoSerializer(serializers.Serializer):
    Id_User = serializers.IntegerField()
    Total = serializers.DecimalField(max_digits=10, decimal_places=2)
    Metodo_Pago = serializers.CharField(max_length=50)
    productos = DetallePedidoSerializer(many=True)
    direccion_envio = serializers.CharField(max_length=200)
    telefono_envio = serializers.CharField(max_length=20)
