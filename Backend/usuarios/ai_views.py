from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .ai_serializers import ChatbotSerializer
from .ai_service import get_product_recommendations, chatbot_response
import logging

logger = logging.getLogger(__name__)


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
        print("\n" + "="*60)
        print("🤖 CHATBOT REQUEST RECIBIDO")
        print(f"📨 Datos recibidos: {request.data}")
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                message = serializer.validated_data.get('message', '')
                conversation_history = serializer.validated_data.get('conversation_history', [])
                dog_type = serializer.validated_data.get('dog_type')
                age = serializer.validated_data.get('age')
                size = serializer.validated_data.get('size')
                health_conditions = serializer.validated_data.get('health_conditions')
                budget = serializer.validated_data.get('budget')
                
                print(f"✅ Mensaje validado: '{message}'")
                print(f"   - Historial: {len(conversation_history)} mensajes anteriores")
                print(f"   - dog_type: {dog_type}")
                print(f"   - age: {age}")
                print(f"   - size: {size}")
                
                # Detectar si es SOLO un saludo sin contexto (evitar saludo doble)
                # Palabras que indican solo saludo
                only_greeting_keywords = ['hola', 'hello', 'hi', 'saludos', 'buenos', 'buenas', 'hey', 'ey', 'q tal', 'qué tal']
                message_lower = message.lower().strip()
                
                # Es saludo simple si contiene SOLO una palabra de saludo o es muy corto
                is_simple_greeting = (message_lower in only_greeting_keywords or 
                                     any(message_lower.startswith(kw) for kw in only_greeting_keywords) and len(message.strip()) < 15)
                
                print(f"🔍 ¿Es saludo simple? {is_simple_greeting}")
                
                # Si es solo un saludo simple, no responder (ya el chatbot saludó al abrir)
                # Solo continuar con la conversación
                if is_simple_greeting:
                    print(f"📤 Es solo un saludo - respondiendo mínimamente")
                    return Response({
                        'success': True,
                        'response': '¿En qué te puedo ayudar? 😊',
                        'status': 'Saludo confirmado'
                    }, status=status.HTTP_200_OK)
                
                # Detectar si pide recomendaciones o solo conversación
                keywords = ['recomend', 'product', 'compr', 'qué', 'cual', 'mejor', 'need', 'want']
                is_recommendation_request = any(keyword in message.lower() for keyword in keywords)
                
                print(f"🔍 ¿Pide recomendaciones? {is_recommendation_request}")
                
                # Si tiene datos del perro y pide recomendaciones
                if is_recommendation_request and (dog_type or age or size):
                    print(f"📝 Generando recomendaciones de productos...")
                    response_data = get_product_recommendations(
                        dog_type=dog_type or 'Gato genérico',
                        age=age or 5,
                        size=size or 'mediano',
                        health_conditions=health_conditions,
                        budget=budget,
                        user_message=message
                    )
                    print(f"✅ Recomendaciones generadas: {response_data['status']}")
                    return Response(response_data, status=status.HTTP_200_OK)
                
                # Si no, responder conversacionalmente
                else:
                    print(f"💬 Generando respuesta conversacional...")
                    context = {
                        'dog_type': dog_type,
                        'age': age,
                        'size': size,
                        'conversation_history': conversation_history
                    }
                    response_data = chatbot_response(message, context)
                    print(f"✅ Respuesta generada: {response_data['status']}")
                    return Response(response_data, status=status.HTTP_200_OK)
                    
            except Exception as e:
                print(f"❌ ERROR: {str(e)}")
                import traceback
                traceback.print_exc()
                return Response({
                    'success': False,
                    'error': str(e),
                    'status': 'Error al procesar el mensaje'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        print(f"❌ VALIDACION FALLIDA: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
