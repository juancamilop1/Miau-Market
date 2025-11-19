from rest_framework import serializers

class ChatbotSerializer(serializers.Serializer):
    """
    Serializador para el chatbot inteligente.
    Acepta preguntas y opcionalmente información del gato para personalizadas recomendaciones.
    """
    message = serializers.CharField(max_length=1000, help_text="Pregunta o mensaje del usuario")
    
    # Historial de conversación (nuevo)
    conversation_history = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="Historial de conversación anterior"
    )
    
    # Información del gato (opcional para personalizacion)
    dog_type = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text="Raza o tipo de gato (opcional)"
    )
    age = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Edad del gato en años (opcional)"
    )
    size = serializers.ChoiceField(
        choices=['pequeño', 'mediano', 'grande', 'extra grande'],
        required=False,
        allow_blank=True,
        help_text="Tamaño del gato (opcional)"
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

