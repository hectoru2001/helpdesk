from django.shortcuts import render, redirect
from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Notificacion
from apps.usuarios.models import ExtraUsuarios
from apps.ordenes.models import SolicitantexOrden
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage, send_mail
from smtplib import SMTPRecipientsRefused

class Notificar:

    @staticmethod
    def crear(usuario, mensaje, tipo="info"):
        """
        Crea una notificación interna para un usuario.
        """
        return Notificacion.objects.create(
            usuario=usuario,
            mensaje=mensaje,
            tipo=tipo
        )

    @staticmethod
    def correo_html(destinatarios, asunto, template, contexto=None):
        """
        Envía un correo usando un template HTML y captura errores SMTP.
        """
        if contexto is None:
            contexto = {}

        if isinstance(destinatarios, str):
            destinatarios = [destinatarios]

        cuerpo_html = render_to_string(template, contexto)

        correo = EmailMessage(
            subject=asunto,
            body=cuerpo_html,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=destinatarios,
        )
        correo.content_subtype = "html"

        try:
            return correo.send()
        except SMTPRecipientsRefused as e:
            print("Destinatarios rechazados:", e.recipients)
            return 0
        except Exception as e:
            print("Error al enviar correo:", e)
            return 0


    @staticmethod
    def enviar_notificacion_orden(orden_id, correos, tipo, contexto=None):
        if not correos:
            return False

        asunto = f"Su orden ha sido {tipo}"
        template_html = "correos/orden_estatus.html"

        # Renderizar el HTML
        cuerpo_html = render_to_string(template_html, contexto)

        # Enviar correo a cada destinatario
        correo = EmailMessage(
            subject=asunto,
            body=cuerpo_html,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[correos],
        )
        correo.content_subtype = "html"
        correo.send(fail_silently=False)

        return True

def marcar_notificaciones_leidas(request):
    Notificacion.objects.filter(
        usuario=request.user,
        leida=False
    ).update(leida=True)

    return redirect(request.META.get('HTTP_REFERER', '/'))

def obtener_correos_orden(orden_id):
    try:
        registro = SolicitantexOrden.objects.get(orden=orden_id)

        correo_b = (registro.correo_beneficiado or "").strip()

        return correo_b  

    except ObjectDoesNotExist:
        return ""


def obtener_correo_usuario(user_id):
    try:
        usuario = User.objects.get(id=user_id)
        return usuario.email or None
    except ObjectDoesNotExist:
        return None
    
def notificaciones_activadas(user_id):
    try:
        usuario = ExtraUsuarios.objects.get(usuario_id=user_id)
        return usuario.notificaciones or True
    except ObjectDoesNotExist:
        return False