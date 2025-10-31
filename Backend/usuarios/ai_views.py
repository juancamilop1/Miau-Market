from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .ai_serializers import ChatbotSerializer
from .ai_service import get_product_recommendations, chatbot_response


class ChatbotView(generics.GenericAPIView):
    """
    Chatbot inteligente para productos y cuidado de perros.
    
    POST:
    - message: La pregunta o mensaje del usuario
    - dog_type: (opcional) Raza o tipo de perro
    - age: (opcional) Edad del perro
    - size: (opcional) Tamaño (pequeño, mediano, grande, extra grande)
    - health_conditions: (opcional) Condiciones de salud especiales
    - budget: (opcional) Rango de presupuesto
    
    El endpoint detecta automáticamente si el usuario quiere:
    - Recomendaciones de productos específicas
    - Conversación general sobre cuidado de perros
    """
    serializer_class = ChatbotSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                message = serializer.validated_data.get('message', '')
                dog_type = serializer.validated_data.get('dog_type')
                age = serializer.validated_data.get('age')
                size = serializer.validated_data.get('size')
                health_conditions = serializer.validated_data.get('health_conditions')
                budget = serializer.validated_data.get('budget')
                
                # Detectar mensajes de saludo inicial
                greeting_keywords = ['hola', 'hello', 'hi', 'saludos', 'buenos', 'buenas', 'inicio', 'empezar']
                is_greeting = any(keyword in message.lower() for keyword in greeting_keywords) or len(message.strip()) < 10
                
                # Si es un saludo inicial, mostrar mensaje de bienvenida
                if is_greeting:
                    welcome_message = """¡Hola! 🐾 Bienvenido a MiauMarket.
Soy tu asistente para todo lo que tu perro necesita 🐕

Puedo ayudarte con:
• Productos recomendados
• Cuidado y alimentación
• Comportamiento y razas

¡Cuéntame sobre tu mascota y empecemos! 🦴"""
                    
                    return Response({
                        'success': True,
                        'response': welcome_message,
                        'status': 'Mensaje de bienvenida'
                    }, status=status.HTTP_200_OK)
                
                # Detectar si pide recomendaciones o solo conversación
                keywords = ['recomend', 'product', 'compr', 'qué', 'cual', 'mejor', 'need', 'want']
                is_recommendation_request = any(keyword in message.lower() for keyword in keywords)
                
                # Si tiene datos del perro y pide recomendaciones
                if is_recommendation_request and (dog_type or age or size):
                    response_data = get_product_recommendations(
                        dog_type=dog_type or 'Perro genérico',
                        age=age or 5,
                        size=size or 'mediano',
                        health_conditions=health_conditions,
                        budget=budget
                    )
                    return Response(response_data, status=status.HTTP_200_OK)
                
                # Si no, responder conversacionalmente
                else:
                    context = {
                        'dog_type': dog_type,
                        'age': age,
                        'size': size
                    }
                    response_data = chatbot_response(message, context)
                    return Response(response_data, status=status.HTTP_200_OK)
                    
            except Exception as e:
                return Response({
                    'success': False,
                    'error': str(e),
                    'status': 'Error al procesar el mensaje'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
