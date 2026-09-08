from rest_framework import serializers
from .models import Notificacion


class NotificacionSerializer(serializers.ModelSerializer):
    Id_User = serializers.IntegerField(source='usuario_id', read_only=True)
    Id_Factura = serializers.IntegerField(source='pedido_id', read_only=True, allow_null=True)

    class Meta:
        model = Notificacion
        fields = ['id', 'Id_User', 'Titulo', 'Mensaje', 'Tipo', 'Leida', 'Fecha_Creacion', 'Id_Factura']
        read_only_fields = ['id', 'Fecha_Creacion']
