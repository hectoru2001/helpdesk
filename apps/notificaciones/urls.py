from django.urls import path
from .views import *

urlpatterns = [
    path('notificaciones/marcar-leidas/', marcar_notificaciones_leidas, name='marcar_notificaciones'),
    path('marcar_leida/<int:pk>/', marcar_notificacion_leida, name='marcar_notificacion_leida')
]
