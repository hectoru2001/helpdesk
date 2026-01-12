from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.login.urls')),
    path('ordenes/', include('apps.ordenes.urls')),
    path('usuarios/', include('apps.usuarios.urls')),
    path('calificaciones/', include('apps.calificaciones.urls')),
    path('catalogos', include('apps.catalogos.urls')),
    path('notificaciones/', include('apps.notificaciones.urls')),
    path('reportes/', include('apps.reportes.urls')),
    path('inicio/', include('apps.inicio.urls')),
    path('configuracion/', include('apps.configuracion.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)