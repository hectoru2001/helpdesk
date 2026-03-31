from django.urls import path
from .views import *

urlpatterns = [
    path('', ReportesView.as_view(), name='listado_reportes'),

    path('ordenes_por_usuario/', ReporteOrdenesPorUsuario.as_view(), name='ordenes_por_usuario'),
    path('ordenes_por_dependencia/', ReporteOrdenesPorDependencia.as_view(), name='ordenes_por_dependencia'),
    path('reporte_ordenes_usuario/', reporte_ordenes_por_usuario_pdf, name='reporte_ordenes_usuario'),
    path('reporte_ordenes_dependencia/', reporte_ordenes_por_dependencia_pdf, name='reporte_dependencia_usuario'),
    path('reporte_calificaciones', ReporteCalificaciones.as_view(), name='reporte_calificaciones'),
    path('reporte_ordenes_tiempo/', ReporteOrdenesTiempoView.as_view(), name='reporte_ordenes_tiempo'),
]
