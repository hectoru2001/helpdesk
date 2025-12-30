from django.urls import path
from .views import *

urlpatterns = [
    path('notificaciones/marcar-leidas/', marcar_notificaciones_leidas, name='marcar_notificaciones'),
]
