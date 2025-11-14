from django.urls import path
from .views import *

urlpatterns = [
    path('lista/', ListaUsuarios.as_view(), name='lista_usuarios'),
]
