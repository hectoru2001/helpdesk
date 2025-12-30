from django.shortcuts import redirect
from django.urls import reverse


class ForzarCambioPasswordMiddleware:
    """
    Obliga al usuario a cambiar contraseña en el primer login
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:

            # Rutas permitidas sin restricción
            rutas_excluidas = [
                reverse('cambiar_contrasena'),
                reverse('logout'),
            ]

            # Evita loop infinito
            if request.path not in rutas_excluidas:

                extra = getattr(request.user, 'extra', None)

                if extra and not extra.cambio_contrasena:
                    return redirect('cambiar_contrasena')

        return self.get_response(request)
