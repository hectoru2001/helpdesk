from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from apps.usuarios.models import ExtraUsuarios

def administrador_required(solo_admin=True):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user

            if not user.is_authenticated:
                return redirect('login')

            try:
                extra = ExtraUsuarios.objects.get(usuario=user)
            except ExtraUsuarios.DoesNotExist:
                extra = None

            if solo_admin:
                if not extra or extra.tipo != 'A':
                    messages.warning(
                        request,
                        "No tienes permisos para acceder a esta sección."
                    )
                    return redirect('inicio')

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator
