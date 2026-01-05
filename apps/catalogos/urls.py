from django.urls import path
from .views import *

urlpatterns = [
    path('clasificaciones/', ListaClasificaciones.as_view(), name='lista_clasificaciones'),
    path('aplicaciones/', ListaAplicaciones.as_view(), name='lista_aplicaciones'),

    path('clasificaciones/nueva/', crear_clasificacion, name='crear_clasificacion'),
    path('clasificaciones/editar/<int:pk>/', editar_clasificacion, name='editar_clasificacion'),
    path('eliminar_clasificacion/<int:pk>/', eliminar_clasificacion, name='eliminar_clasificacion'),

    path('aplicaciones/nueva/', crear_aplicacion, name='crear_aplicacion'),
    path('aplicaciones/editar/<int:pk>/', editar_aplicacion, name='editar_aplicacion'),
    path('eliminar_aplicacion/<int:pk>/', eliminar_aplicacion, name='eliminar_aplicacion'),
]
