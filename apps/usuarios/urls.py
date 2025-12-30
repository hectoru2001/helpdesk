from django.urls import path
from .views import *

urlpatterns = [
    path('lista/', ListaUsuarios.as_view(), name='lista_usuarios'),
    path('detalle/<int:pk>/', DetalleUsuario.as_view(), name='detalle_usuario'),
    path('eliminar/<int:pk>/', eliminar_usuario, name='eliminar_usuario'),
    path('actualizar/<int:pk>/', ActualizarUsuario.as_view(), name='actualizar_usuario'),
    path('crear', CrearUsuario.as_view(), name="crear_usuario"),
    path("empleados/", ListaEmpleados.as_view(), name="lista_empleados"),

]
