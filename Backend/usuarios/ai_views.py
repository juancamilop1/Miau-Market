from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from .ai_serializers import ChatbotSerializer
from .models import MiauBotAprendizaje
from .services.miaubot_service import procesar_mensaje, obtener_mensaje_bienvenida
from .services.miaubot_aprendizaje import aprobar_aprendizaje
import logging

logger = logging.getLogger(__name__)


class ChatbotView(generics.GenericAPIView):
    """MiauBot 100% local — productos reales + conocimiento en BD."""
    serializer_class = ChatbotSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            message = serializer.validated_data.get('message', '')
            conversation_history = serializer.validated_data.get('conversation_history', [])

            user = request.user if request.user.is_authenticated else None
            context = {
                'user_name': user.Nombre if user else None,
                'user_id': user.id if user else None,
                'animal': serializer.validated_data.get('dog_type') or None,
                'conversation_history': conversation_history,
            }

            result = procesar_mensaje(message, conversation_history, context)
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception('Error en chatbot')
            return Response({
                'success': False,
                'error': str(e),
                'response': 'Hubo un problema. Intenta de nuevo en un momento.',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatbotConfigView(APIView):
    """Configuracion publica del bot (bienvenida, nombre, modo IA)."""
    permission_classes = [AllowAny]

    def get(self, request):
        from django.conf import settings
        user = request.user if request.user.is_authenticated else None
        nombre = user.Nombre if user else None
        user_id = user.id if user else None
        ia_activa = bool(getattr(settings, 'GEMINI_API_KEY', ''))
        return Response({
            'success': True,
            'nombre_bot': 'MiauBot',
            'mensaje_bienvenida': obtener_mensaje_bienvenida(nombre, user_id),
            'ia_activa': ia_activa,
        })


class MiauBotAprendizajeListView(APIView):
    """Lista propuestas de aprendizaje del chatbot (solo admin)."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        estado = request.query_params.get('estado', 'pendiente')
        qs = MiauBotAprendizaje.objects.all()
        if estado and estado != 'todos':
            qs = qs.filter(estado=estado)

        items = [{
            'id': i.id,
            'pregunta': i.pregunta,
            'respuesta': i.respuesta,
            'palabras_clave': i.palabras_clave,
            'animal': i.animal,
            'usuario_id': i.usuario_id,
            'estado': i.estado,
            'veces_usada': i.veces_usada,
            'Fecha_Creacion': i.Fecha_Creacion.isoformat(),
        } for i in qs[:200]]

        pendientes = MiauBotAprendizaje.objects.filter(estado='pendiente').count()
        return Response({
            'success': True,
            'total': len(items),
            'pendientes': pendientes,
            'items': items,
        })


class MiauBotAprendizajeDetailView(APIView):
    """Editar, aprobar o rechazar una propuesta de aprendizaje."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def _get_item(self, pk):
        try:
            return MiauBotAprendizaje.objects.get(pk=pk)
        except MiauBotAprendizaje.DoesNotExist:
            return None

    def put(self, request, pk):
        item = self._get_item(pk)
        if not item:
            return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)

        if 'respuesta' in request.data:
            item.respuesta = request.data['respuesta']
            item.save(update_fields=['respuesta'])
        if 'pregunta' in request.data:
            item.pregunta = request.data['pregunta']
            item.save(update_fields=['pregunta'])

        return Response({'success': True, 'message': 'Actualizado'})

    def post(self, request, pk):
        item = self._get_item(pk)
        if not item:
            return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)

        accion = request.data.get('accion', 'aprobar')
        if accion == 'aprobar':
            aprobar_aprendizaje(item)
            return Response({'success': True, 'message': 'Aprendizaje aprobado y agregado al conocimiento'})
        if accion == 'rechazar':
            item.estado = 'rechazado'
            item.save(update_fields=['estado'])
            return Response({'success': True, 'message': 'Aprendizaje rechazado'})

        return Response({'error': 'Accion invalida'}, status=status.HTTP_400_BAD_REQUEST)
