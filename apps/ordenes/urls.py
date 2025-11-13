from django.urls import path
from . import views

urlpatterns = [
    path('crear/', views.formulario_nueva_orden, name='crear_orden'),
]
