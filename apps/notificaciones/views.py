import requests
from django.shortcuts import redirect
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from .models import Notificacion
from apps.usuarios.models import ExtraUsuarios
from apps.ordenes.models import SolicitantexOrden
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from smtplib import SMTPRecipientsRefused
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse


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
    def correo_html(destinatarios, asunto, template, contexto=None, cc=None):
        """
        Envía un correo usando un template HTML y captura errores SMTP.
        """
        if contexto is None:
            contexto = {}

        if isinstance(cc, str):
            cc = [cc]

        if isinstance(destinatarios, str):
            destinatarios = [destinatarios]

        cuerpo_html = render_to_string(template, contexto)

        correo = EmailMessage(
            subject=asunto,
            body=cuerpo_html,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=destinatarios,
            cc=cc or []
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

    def enviar_telegram(mensaje):
        token_id = "8209068064:AAESmEENLeqNs_os3gL2hvMDI5QTqCXE5CE"
        chat_id = "-1003775219374"

        if not token_id or not chat_id:
            print("Token de Telegram o chat ID no configurados.")
            return False
        
        url = f"https://api.telegram.org/bot{token_id}/sendMessage"

        try:
            r = requests.post(url, json={
                "chat_id": chat_id, 
                "text": mensaje,
                "parse_mode": "HTML"
            })
            return r.status_code == 200

        except Exception as e:
            print("Error al enviar mensaje a Telegram:", e)
            return False

def marcar_notificaciones_leidas(request):
    Notificacion.objects.filter(
        usuario=request.user,
        leida=False
    ).update(leida=True)

    return redirect(request.META.get('HTTP_REFERER', '/'))

def marcar_notificacion_leida(request, pk):
    notificacion = get_object_or_404(
        Notificacion,
        pk=pk,
        usuario=request.user
    )
    notificacion.leida = True
    notificacion.save()
    return JsonResponse({"success": True})


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