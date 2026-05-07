from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView, TemplateView, View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from core.decorators.permisos import administrador_required
from django.utils.decorators import method_decorator

@method_decorator(administrador_required(False), name='dispatch')

class ConfiguracionesView(TemplateView):
    template_name = "configuraciones.html"

@login_required
def confirmar_cambio(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            user = form.save()

            # Evita que el usuario sea deslogueado
            update_session_auth_hash(request, user)

            messages.success(request, "Contraseña actualizada correctamente.")
            return redirect("login")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "confirmar_chansword.html", {
        "form": form
    })

def restablecer_contraseña(request):
    if request.method == "POST":
        correo = request.POST.get("correo")

        # Validar dominio institucional
        if not correo.endswith("@juarez.gob.mx"):
            messages.error(request, "Debes usar tu correo institucional.")
            return redirect("restablecer_contraseña")

        # Buscar usuario
        try:
            usuario = User.objects.get(email=correo)
        except User.DoesNotExist:
            messages.error(request, "No existe un usuario con ese correo.")
            return redirect("restablecer_contraseña")

        # Generar token seguro
        uid = urlsafe_base64_encode(force_bytes(usuario.pk))
        token = default_token_generator.make_token(usuario)

        domain = get_current_site(request).domain

        # Link de recuperación
        enlace = f"http://{domain}/configuracion/reset/{uid}/{token}/"

        # Renderizar plantilla del correo
        mensaje = render_to_string("correos/password_reset.html", {
            "usuario": usuario,
            "enlace": enlace
        })

        # Enviar correo
        send_mail(
            "Restablecer contraseña",
            "",  # texto plano vacío
            None,
            [correo],
            html_message=mensaje
        )


        messages.success(request, "Se envió un enlace a tu correo institucional.")
        return redirect("login")

    return render(request, "restablecer_contrasena.html")

def cambiar_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        usuario = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        usuario = None

    # Validar token
    if usuario is None or not default_token_generator.check_token(usuario, token):
        messages.error(request, "El enlace no es válido o expiró.")
        return redirect("login")

    # Si el token es válido → permitir cambio
    if request.method == "POST":
        nueva_password = request.POST.get("new_password")
        confirmar = request.POST.get("confirm_password")

        if nueva_password != confirmar:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, "cambiar_password.html")

        usuario.set_password(nueva_password)
        usuario.save()

        messages.success(request, "Contraseña actualizada correctamente.")
        return redirect("login")

    return render(request, "cambiar_password.html")