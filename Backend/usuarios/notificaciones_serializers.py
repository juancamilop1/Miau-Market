from rest_framework import serializers
from .models import Notificacion

class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = ['id', 'Id_User', 'Titulo', 'Mensaje', 'Tipo', 'Leida', 'Fecha_Creacion', 'Id_Factura']
        read_only_fields = ['id', 'Fecha_Creacion']
