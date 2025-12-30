from .models import Notificacion
from apps.usuarios.models import ExtraUsuarios

def soporte_usuarios(request):
    tecnicos = ExtraUsuarios.objects.filter(tipo="T", estatus="A")
    programadores = ExtraUsuarios.objects.filter(tipo="P", estatus="A")

    return {
        "menu_tecnicos": tecnicos,
        "menu_programadores": programadores,
    }

def notificaciones_context(request):
    if not request.user.is_authenticated:
        return {}

    notifs = Notificacion.objects.filter(
        usuario=request.user,
        leida=False
    ).order_by('-creada')

    return {
        "notificaciones": notifs,
        "notificaciones_count": notifs.count()
    }

def tipo_usuario(request):
    if not request.user.is_authenticated:
        return {"tipo_usuario": None}
    try:
        extra = ExtraUsuarios.objects.get(usuario_id=request.user)
        tipo = extra.tipo
    except ExtraUsuarios.DoesNotExist:
        tipo = "T"

    return {"tipo_usuario": tipo}