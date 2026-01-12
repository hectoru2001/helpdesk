from django.urls import path
from .views import *

urlpatterns = [
    path('clasificaciones/', ListaClasificaciones.as_view(), name='lista_clasificaciones'),
    path('aplicaciones/', ListaAplicaciones.as_view(), name='lista_aplicaciones'),
    path('marcas/', ListaMarcas.as_view(), name='lista_marcas'),
    path('colores/', ListaColores.as_view(), name='lista_colores'),

    path('clasificaciones/nueva/', crear_clasificacion, name='crear_clasificacion'),
    path('clasificaciones/editar/<int:pk>/', editar_clasificacion, name='editar_clasificacion'),
    path('eliminar_clasificacion/<int:pk>/', eliminar_clasificacion, name='eliminar_clasificacion'),

    path('aplicaciones/nueva/', crear_aplicacion, name='crear_aplicacion'),
    path('aplicaciones/editar/<int:pk>/', editar_aplicacion, name='editar_aplicacion'),
    path('eliminar_aplicacion/<int:pk>/', eliminar_aplicacion, name='eliminar_aplicacion'),

    path('marcas/nueva/', crear_marca, name='crear_marca'),
    path('marcas/editar/<int:pk>/', editar_marca, name='editar_marca'),
    path('eliminar_marca/<int:pk>/', eliminar_marca, name='eliminar_marca'),

    path('colores/nuevo/', crear_color, name='crear_color'),
    path('colores/editar/<int:pk>/', editar_color, name='editar_color'),
    path('eliminar_color/<int:pk>/', eliminar_color, name='eliminar_color'),
]
