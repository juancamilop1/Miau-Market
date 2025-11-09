from django.urls import path
from .views import (
    RegistroView, LoginView, UsuarioListView, UsuarioDetailView,
    ProductoListView, ProductoDetailView, CrearPedidoView, ActualizarPedidoView,
    MisPedidosView, NotificacionesView, MarcarNotificacionLeidaView, MarcarTodasLeidasView,
    VerificarProductosCaducadosView
)
from .ai_views import ChatbotView

urlpatterns = [
    path('registro/', RegistroView.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name='login'),
    path('', UsuarioListView.as_view(), name='usuario-list'),
    path('<int:pk>/', UsuarioDetailView.as_view(), name='usuario-detail'),
    # Endpoint único de chatbot inteligente
    path('chatbot/', ChatbotView.as_view(), name='chatbot'),
    # Endpoints de productos
    path('productos/', ProductoListView.as_view(), name='producto-list'),
    path('productos/<int:id>/', ProductoDetailView.as_view(), name='producto-detail'),
    # Endpoints de pedidos
    path('pedidos/', CrearPedidoView.as_view(), name='pedidos'),
    path('pedidos/<int:pk>/', ActualizarPedidoView.as_view(), name='actualizar-pedido'),
    path('mis-pedidos/', MisPedidosView.as_view(), name='mis-pedidos'),
    # Endpoints de notificaciones
    path('notificaciones/', NotificacionesView.as_view(), name='notificaciones'),
    path('notificaciones/<int:pk>/leer/', MarcarNotificacionLeidaView.as_view(), name='marcar-leida'),
    path('notificaciones/leer-todas/', MarcarTodasLeidasView.as_view(), name='marcar-todas-leidas'),
    path('notificaciones/verificar-caducados/', VerificarProductosCaducadosView.as_view(), name='verificar-caducados'),
]
