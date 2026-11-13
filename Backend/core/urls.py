from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def health(_request):
    return JsonResponse({'status': 'ok', 'app': 'miau-market'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health, name='health'),
    path('api/usuarios/', include('usuarios.urls')),
]

# Media: en free tier el disco de Render es efimero; OK para demo.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
