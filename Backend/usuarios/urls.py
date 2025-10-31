from django.urls import path
from .views import RegistroView, LoginView, UsuarioListView, UsuarioDetailView
from .ai_views import ChatbotView

urlpatterns = [
    path('registro/', RegistroView.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name='login'),
    path('', UsuarioListView.as_view(), name='usuario-list'),
    path('<int:pk>/', UsuarioDetailView.as_view(), name='usuario-detail'),
    # Endpoint único de chatbot inteligente
    path('chatbot/', ChatbotView.as_view(), name='chatbot'),
]
