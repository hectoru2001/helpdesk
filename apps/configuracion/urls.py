from django.urls import path
from .views import restablecer_contraseña, cambiar_password, ConfiguracionesView, confirmar_cambio

urlpatterns = [
    path('opciones/', ConfiguracionesView.as_view(), name='configuraciones'),

    path('restablecer_contraseña/', restablecer_contraseña, name='restablecer_contraseña'),
    path("reset/<uidb64>/<token>/", cambiar_password, name="cambiar_password"),
    path("confirmar_cambio/", confirmar_cambio, name="confirmar_cambio"),
]