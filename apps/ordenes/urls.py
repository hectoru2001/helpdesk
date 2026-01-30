from django.urls import path
from .views import *
from .utils import BuscarEmpleadoAPI, BuscarFuncionarioAPI, BuscarPatrimonioAPI
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('crear/', OrdenCreateTicket.as_view(), name='crear_orden'),
    path('lista/', ListaOrdenes.as_view(), name='lista_ordenes'),
    path('editar/<str:pk>/', EditarOrden.as_view(), name='editar_orden'),
    path('eliminar/<str:pk>/', eliminar_orden, name='eliminar_orden'),
    path('detalles/<str:pk>/', DetallesOrdenes.as_view(), name='detalle_orden'),
    path('ordenes/', OrdenesView.as_view(), name='ordenes_lista'),
    path('imprimir/<int:orden_id>/', imprimir_orden, name='imprimir_orden'),

    path('agregar_equipos/<int:orden_id>/', Agregar_Equipo.as_view(), name='agregar_equipos'),
    path('orden/<int:orden_id>/archivos/', Agregar_Archivos.as_view(), name='agregar_archivos'),
    path('archivo/<int:pk>/eliminar/', EliminarArchivoOrden.as_view(), name='eliminar_archivo_orden'),
    path('ordenes_usuario/<int:user_id>/', EstadoUsuariosView.as_view(), name='ordenes_usuario'),
    path('estado_usuarios/<int:user_id>/', OrdenesPorUsuarioView.as_view(), name='detalle_usuario_ordenes'),
    path("duplicar_orden/", DuplicarOrden.as_view(), name='duplicar_orden'),


    # === Endpint órdenes asignadas === #
    path("actualizar_estatus/proceso/", actualizar_estatus_api),
    path("cargar_detalles/proceso/<int:pk>/", detalle_orden_api),
    path('usuarios_disponibles/<int:orden_id>/', usuarios_disponibles, name='usuarios_disponibles'),
    path('reasignar/', reasignar_orden, name='reasignar_orden'),
    path('entregar_equipo/<int:equipo_id>/', entregar_equipo, name='entregar_equipo'),
    path('guardar_comentario/', guardar_comentario, name='guardar_comentario'),

    # === Endpoint Empleados === #
    path("empleados/buscar/", BuscarEmpleadoAPI.as_view(), name="buscar_empleado"),
    path("funcionarios/buscar/", BuscarFuncionarioAPI.as_view(), name="buscar_funcionario"),
    path("patrimonio/buscar/", BuscarPatrimonioAPI.as_view()),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)