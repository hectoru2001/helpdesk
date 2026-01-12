from django.urls import path
from . import views

urlpatterns = [
    path('cambiar-contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),
]