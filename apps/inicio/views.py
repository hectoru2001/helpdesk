from django.views.generic import TemplateView, DetailView
from django.utils import timezone
from apps.ordenes.models import Orden
from apps.notificaciones.models import Notificacion
from apps.usuarios.models import ExtraUsuarios
from core.decorators.permisos import administrador_required
from django.utils.decorators import method_decorator

@method_decorator(administrador_required(False), name='dispatch')
class DashboardView(TemplateView):
    template_name = 'inicio.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Obtener tipo de usuario
        try:
            extra = ExtraUsuarios.objects.get(usuario_id=user)
            tipo = extra.tipo
        except ExtraUsuarios.DoesNotExist:
            tipo = "T"

        ordenes_qs = (
            Orden.objects.filter(usuarios_orden__realiza=user)
            .distinct()
        )

        context['ordenes'] = ordenes_qs.filter(estatus__in=['E', 'A']).order_by('-fecha_captura')[:5]

        hoy = timezone.now().date()
        print(hoy)

        context['estadisticas'] = {
            'ordenes_hoy': ordenes_qs.filter(fecha_captura__date=hoy).count(),
            'ordenes_completadas': ordenes_qs.filter(fecha_captura__date=hoy, estatus='T').count(),
            'ordenes_pendientes': ordenes_qs.filter(fecha_captura__date=hoy, estatus__in=['E', 'En Proceso']).count(),
            'ordenes_proceso': ordenes_qs.filter(fecha_captura__date=hoy, estatus__in=['A', 'Asignada']).count(),
        }

        queryset = Notificacion.objects.filter(usuario=user).order_by('-creada')

        context['notificaciones_count'] = queryset.filter(leida=False).count()
        context['notificaciones'] = queryset.filter(leida=False)[:5]

        return context
    
@method_decorator(administrador_required(False), name='dispatch')
class OrdenDetailView(DetailView):
    model = Orden
    template_name = 'detalle_orden.html'
    context_object_name = 'orden'