from rest_framework import serializers

class ChatbotSerializer(serializers.Serializer):
    """
    Serializador para el chatbot inteligente.
    Acepta preguntas y opcionalmente información del perro para personalizadas recomendaciones.
    """
    message = serializers.CharField(max_length=1000, help_text="Pregunta o mensaje del usuario")
    
    # Información del perro (opcional para personalizacion)
    dog_type = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text="Raza o tipo de perro (opcional)"
    )
    age = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Edad del perro en años (opcional)"
    )
    size = serializers.ChoiceField(
        choices=['pequeño', 'mediano', 'grande', 'extra grande'],
        required=False,
        allow_blank=True,
        help_text="Tamaño del perro (opcional)"
    )
    health_conditions = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        help_text="Condiciones de salud especiales (opcional)"
    )
    budget = serializers.ChoiceField(
        choices=['bajo', 'medio', 'alto'],
        required=False,
        allow_blank=True,
        help_text="Rango de presupuesto (opcional)"
    )
