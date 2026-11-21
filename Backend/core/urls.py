from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.http import JsonResponse
from django.views.static import serve


def health(_request):
    return JsonResponse({'status': 'ok', 'app': 'miau-market'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health, name='health'),
    path('api/usuarios/', include('usuarios.urls')),
    # Media: en free tier el disco de Render es efimero; sirve subidas incluso con DEBUG=False.
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
