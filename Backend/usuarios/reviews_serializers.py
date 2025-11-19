from rest_framework import serializers

class CrearReviewSerializer(serializers.Serializer):
    Id_Products = serializers.IntegerField()
    Rating = serializers.IntegerField(min_value=1, max_value=5)
    Comentario = serializers.CharField(required=False, allow_blank=True, max_length=1000)

class ReviewSerializer(serializers.Serializer):
    Id_Review = serializers.IntegerField()
    Id_Products = serializers.IntegerField()
    Id_User = serializers.IntegerField()
    Rating = serializers.IntegerField()
    Comentario = serializers.CharField()
    Fecha = serializers.DateTimeField()
    usuario_nombre = serializers.CharField(required=False)
    usuario_apellido = serializers.CharField(required=False)

class ProductoConCalificacionSerializer(serializers.Serializer):
    Id_Products = serializers.IntegerField()
    Titulo = serializers.CharField()
    Total_Reviews = serializers.IntegerField()
    Rating_Promedio = serializers.FloatField()
    Reviews_5_Estrellas = serializers.IntegerField()
    Reviews_4_Estrellas = serializers.IntegerField()
    Reviews_3_Estrellas = serializers.IntegerField()
    Reviews_2_Estrellas = serializers.IntegerField()
    Reviews_1_Estrella = serializers.IntegerField()
