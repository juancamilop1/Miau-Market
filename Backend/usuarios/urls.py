from django.urls import path
from .views import RegistroView, LoginView, UsuarioListView, UsuarioDetailView

urlpatterns = [
    path('registro/', RegistroView.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name='login'),
    path('', UsuarioListView.as_view(), name='usuario-list'),
    path('<int:pk>/', UsuarioDetailView.as_view(), name='usuario-detail'),
]
