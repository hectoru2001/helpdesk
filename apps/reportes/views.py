from django.http import HttpResponse
from django.template.loader import get_template
from django.db.models import Count, Q, Avg, F, ExpressionWrapper, DurationField, Sum
from datetime import datetime
from xhtml2pdf import pisa
from apps.ordenes.models import UsuariosxOrden, SolicitantexOrden, Orden
from apps.usuarios.models import ExtraUsuarios
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from datetime import timedelta
from django.conf import settings
from core.decorators.permisos import administrador_required
from django.utils.decorators import method_decorator
from django.utils import timezone

USUARIOS_EXTRA_POR_CLASIFICACION = {
        'T': [554, 545],   # Técnicos (admins incluidos)
        'P': [549],       # Programadores (admins incluidos)
    }

class ReportesView(TemplateView):
    template_name = 'listado_reportes.html'

@method_decorator(administrador_required(True), name='dispatch')
class ReporteOrdenesPorUsuario(TemplateView):
    template_name = 'ordenes_usuario.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        fecha_inicio = self.request.GET.get('fecha_inicio')
        fecha_fin = self.request.GET.get('fecha_fin')
        usuario_id = self.request.GET.get('usuario')
        clasificacion = self.request.GET.get('clasificacion')

        qs = UsuariosxOrden.objects.select_related(
            'orden',
            'realiza',
            'realiza__extra'
        )

        if fecha_inicio:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            qs = qs.filter(orden__fecha_captura__gte=fecha_inicio)

        if fecha_fin:
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d') + timedelta(days=1)
            qs = qs.filter(orden__fecha_captura__lt=fecha_fin)

        if usuario_id:
            qs = qs.filter(realiza_id=usuario_id)

        if clasificacion:
            qs = qs.filter(
                Q(realiza__extra__tipo=clasificacion) |
                Q(realiza__id__in=USUARIOS_EXTRA_POR_CLASIFICACION.get(clasificacion, []))
            )


        context['reporte'] = (
            qs.values(
                'realiza__id',
                'realiza__username',
                'realiza__first_name',
                'realiza__last_name',
            )
            .annotate(
                total=Count('orden', distinct=True),
                en_proceso=Count('orden', filter=Q(estatus='E'), distinct=True),
                asignadas=Count('orden', filter=Q(estatus='A'), distinct=True),
                canceladas=Count('orden', filter=Q(estatus='C'), distinct=True),
                terminadas=Count('orden', filter=Q(estatus='T'), distinct=True),
            )
            .order_by('-total')
        )

        context['usuarios'] = User.objects.filter(
            id__in=qs.values_list('realiza_id', flat=True).distinct()
        )

        # Se conserva el valor para el formulario (no afecta CSS)
        context['clasificacion'] = clasificacion

        return context

def reporte_ordenes_por_usuario_pdf(request):
    qs = UsuariosxOrden.objects.select_related(
        'orden',
        'realiza',
        'realiza__extra'
    )

    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    usuario_id = request.GET.get('usuario')
    clasificacion = request.GET.get('clasificacion')

    if fecha_inicio:
        qs = qs.filter(orden__fecha_captura__date__gte=fecha_inicio)

    if fecha_fin:
        qs = qs.filter(orden__fecha_captura__date__lte=fecha_fin)

    if usuario_id:
        qs = qs.filter(realiza_id=usuario_id)

    if clasificacion:
                qs = qs.filter(
                    Q(realiza__extra__tipo=clasificacion) |
                    Q(realiza__id__in=USUARIOS_EXTRA_POR_CLASIFICACION.get(clasificacion, []))
            )

    reporte = (
        qs.values(
            'realiza__username',
            'realiza__first_name',
            'realiza__last_name',
            'realiza__extra__tipo', 
        )
        .annotate(
            total=Count('orden', distinct=True),
            asignadas=Count('orden', filter=Q(estatus='A'), distinct=True),
            en_proceso=Count('orden', filter=Q(estatus='E'), distinct=True),
            terminadas=Count('orden', filter=Q(estatus='T'), distinct=True),
            canceladas=Count('orden', filter=Q(estatus='C'), distinct=True),
        )
        .order_by('-total')
    )

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="ordenes_por_usuario.pdf"'

    template = get_template('plantillas/ordenes_usuario_pdf.html')
    html = template.render({
        'reporte': reporte,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'clasificacion': clasificacion,
    })

    pisa.CreatePDF(html, dest=response)
    return response

@method_decorator(administrador_required(True), name='dispatch')
class ReporteOrdenesPorDependencia(TemplateView):
    template_name = 'ordenes_dependencia.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        fecha_inicio = self.request.GET.get('fecha_inicio')
        fecha_fin = self.request.GET.get('fecha_fin')
        dependencia = self.request.GET.get('dependencia')

        qs = SolicitantexOrden.objects.select_related(
            'orden'
        )

        # 🔹 Filtros por fecha
        if fecha_inicio:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            qs = qs.filter(orden__fecha_captura__gte=fecha_inicio)

        if fecha_fin:
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d') + timedelta(days=1)
            qs = qs.filter(orden__fecha_captura__lt=fecha_fin)

        # 🔹 Filtro por dependencia beneficiada
        if dependencia:
            qs = qs.filter(dependencia_beneficiado=dependencia)

        # 🔹 Agrupación por dependencia beneficiada
        context['reporte'] = (
            qs.values(
                'dependencia_beneficiado',
            )
            .annotate(
                total=Count('orden', distinct=True),
                en_proceso=Count('orden', filter=Q(orden__estatus='E'), distinct=True),
                asignadas=Count('orden', filter=Q(orden__estatus='A'), distinct=True),
                canceladas=Count('orden', filter=Q(orden__estatus='C'), distinct=True),
                terminadas=Count('orden', filter=Q(orden__estatus='T'), distinct=True),
            )
            .order_by('-total')
        )

        # 🔹 Para el combo de dependencias (solo las que aparecen en el rango)
        context['dependencias'] = (
            qs.values_list('dependencia_beneficiado', flat=True)
            .distinct()
            .order_by('dependencia_beneficiado')
        )

        return context
    
def reporte_ordenes_por_dependencia_pdf(request):
    qs = SolicitantexOrden.objects.select_related(
        'orden'
    )

    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    dependencia = request.GET.get('dependencia')

    if fecha_inicio:
        qs = qs.filter(orden__fecha_captura__date__gte=fecha_inicio)

    if fecha_fin:
        qs = qs.filter(orden__fecha_captura__date__lte=fecha_fin)

    if dependencia:
        qs = qs.filter(dependencia_beneficiado=dependencia)

    reporte = (
        qs.values(
            'dependencia_beneficiado',
        )
        .annotate(
            total=Count('orden', distinct=True),
            asignadas=Count('orden', filter=Q(orden__estatus='A'), distinct=True),
            en_proceso=Count('orden', filter=Q(orden__estatus='E'), distinct=True),
            terminadas=Count('orden', filter=Q(orden__estatus='T'), distinct=True),
            canceladas=Count('orden', filter=Q(orden__estatus='C'), distinct=True),
        )
        .order_by('-total')
    )

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="ordenes_por_dependencia.pdf"'

    template = get_template('plantillas/ordenes_dependencia_pdf.html')
    html = template.render({
        'reporte': reporte,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'dependencia': dependencia,
        'STATIC_ROOT': settings.STATIC_ROOT,
    })

    pisa.CreatePDF(html, dest=response)
    return response

@method_decorator(administrador_required(True), name='dispatch')
class ReporteCalificaciones(TemplateView):
    template_name = 'ordenes_comentarios.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # filtros GET
        fecha_inicio = self.request.GET.get('fecha_inicio')
        fecha_fin = self.request.GET.get('fecha_fin')
        calificacion = self.request.GET.get('calificacion')

        # queryset base
        ordenes = (
            Orden.objects
            .select_related('clasificacion')
            .prefetch_related(
                'usuarios_orden__realiza',
                'usuarios_orden__asigna',
                'comentario'
            )
        )

        # filtros por fecha de término
        if fecha_inicio:
            ordenes = ordenes.filter(
                fecha_terminado__date__gte=fecha_inicio
            )

        if fecha_fin:
            ordenes = ordenes.filter(
                fecha_terminado__date__lte=fecha_fin
            )

        # filtro por calificación
        if calificacion:
            ordenes = ordenes.filter(
                comentario__calificacion=calificacion
            ).distinct()

        # solo órdenes terminadas (tiene sentido para calificación)
        ordenes = ordenes.filter(estatus='T')

        # promedio de calificación por orden
        ordenes = ordenes.annotate(
            promedio_calificacion=Avg('comentario__calificacion')
        )

        # contexto
        context['ordenes'] = ordenes

        return context
      
from django.utils import timezone
from datetime import timedelta
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator

@method_decorator(administrador_required(True), name='dispatch')
class ReporteOrdenesTiempoView(TemplateView):
    template_name = "ordenes_ordenes_tiempos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ordenes = Orden.objects.all()

        # 🔍 FILTROS
        orden = self.request.GET.get('orden')
        fecha_inicio = self.request.GET.get('fecha_inicio')
        fecha_fin = self.request.GET.get('fecha_fin')

        if orden:
            ordenes = ordenes.filter(orden=orden)

        if fecha_inicio and fecha_fin:
            ordenes = ordenes.filter(
                fecha_captura__date__range=[fecha_inicio, fecha_fin]
            )

        reporte = []

        for orden in ordenes:

            inicio = orden.fecha_inicio
            fin = orden.fecha_terminado
            vencimiento = orden.fecha_vencimiento

            # -------------------------
            # ⏱️ TIEMPO TRABAJADO (suma de usuarios)
            # -------------------------
            trabajos = orden.usuarios_orden.exclude(
                inicia__isnull=True,
                termina__isnull=True
            )

            tiempo_trabajado = timedelta()

            for t in trabajos:
                if t.inicia and t.termina:
                    tiempo_trabajado += (t.termina - t.inicia)

            # 🔢 formateo horas/minutos
            total_segundos = int(tiempo_trabajado.total_seconds())
            horas = total_segundos // 3600
            minutos = (total_segundos % 3600) // 60

            if horas > 0:
                tiempo_formateado = f"{horas}h {minutos}m"
            else:
                tiempo_formateado = f"{minutos}m"

            # -------------------------
            # 📊 INDICADOR DE EFICIENCIA
            # -------------------------
            bandera = None

            if inicio and fin and vencimiento and orden.estatus == "T":

                tiempo_total = (vencimiento - inicio).total_seconds()
                tiempo_usado = (fin - inicio).total_seconds()

                if tiempo_total > 0:
                    porcentaje = (tiempo_usado / tiempo_total) * 100

                    if porcentaje <= 50:
                        bandera = "ok_50"
                    elif porcentaje <= 70:
                        bandera = "ok_30"
                    elif porcentaje <= 90:
                        bandera = "ok_10"
                    else:
                        bandera = "fuera"

            # -------------------------
            # 👥 USUARIOS
            # -------------------------
            usuarios = orden.usuarios_orden.select_related('realiza').all()

            usuarios_nombres = [
                f"{u.realiza.first_name} {u.realiza.last_name}".strip() or u.realiza.username
                for u in usuarios
            ]

            # -------------------------
            # 📦 ARMAR REPORTE
            # -------------------------
            reporte.append({
                "orden": orden.orden,
                "descripcion": orden.descripcion,
                "estatus": orden.estatus,
                "prioridad": orden.prioridad,

                "fecha_inicio": inicio,
                "fecha_vencimiento": vencimiento,
                "fecha_terminado": fin,

                "usuarios": usuarios_nombres,

                "tiempo_trabajado": tiempo_formateado,
                "bandera": bandera,
            })

        # 🔥 ORDENAR (más recientes primero)
        reporte = sorted(
            reporte,
            key=lambda x: x['orden'],
            reverse=True
        )

        context["reporte"] = reporte
        return context