from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.login.urls')),
    path('ordenes/', include('apps.ordenes.urls')),
    path('usuarios/', include('apps.usuarios.urls')),
    path('calificaciones/', include('apps.calificaciones.urls')),
    path('notificaciones/', include('apps.notificaciones.urls')),
    path('reportes/', include('apps.reportes.urls')),
]