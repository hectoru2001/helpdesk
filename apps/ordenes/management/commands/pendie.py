import time
import sys
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from apps.ordenes.models import Orden, UsuariosxOrden 
from apps.notificaciones.views import Notificar

class Command(BaseCommand):
    help = 'Daemon que vigila los vencimientos de órdenes en tiempo real'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('--- Daemon de Alertas Iniciado ---'))
        
        try:
            while True:
                self.revisar_vencimientos()
                # Espera 60 segundos antes de la siguiente revisión
                # Puedes bajarlo a 30 si quieres más velocidad
                time.sleep(60) 
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nDaemon detenido manualmente.'))
            sys.exit(0)

    def revisar_vencimientos(self):
        ahora = timezone.now()

        ordenes = Orden.objects.filter(
            estatus='E',
            fecha_vencimiento__isnull=False,
            fecha_inicio__isnull=False
        )

        for o in ordenes:
            try:
                duracion_total = (o.fecha_vencimiento - o.fecha_inicio).total_seconds()
                tiempo_restante = (o.fecha_vencimiento - ahora).total_seconds()

                if duracion_total <= 0:
                    continue

                porcentaje_restante = (tiempo_restante / duracion_total) * 100

                # 👥 USUARIOS ACTIVOS
                usuarios = o.usuarios_orden.select_related('realiza').filter(
                    estatus='E',
                    termina__isnull=True
                )

                nombres_usuarios = []
                correos_usuarios = []

                for u in usuarios:
                    user = u.realiza

                    nombre = f"{user.first_name} {user.last_name}".strip() or user.username
                    nombres_usuarios.append(nombre)

                    if user.email:
                        correos_usuarios.append(user.email)

                correos_usuarios = list(set(correos_usuarios))

                # Correos por categoría
                if o.categoria == "programadores":
                    correos_categoria = ["jaolague@juarez.gob.mx"]
                else:
                    correos_categoria = ["jesus.chavez@juarez.gob.mx"]

                # Base de destinatarios
                destinatarios_base = correos_usuarios + correos_categoria


                if 30 < porcentaje_restante <= 50 and o.nivel_alerta == 0:
                    if destinatarios_base:
                        self.enviar(o, "50%", destinatarios_base, nombres_usuarios)
                        o.nivel_alerta = 1
                        o.save(update_fields=["nivel_alerta"])

                elif 0 < porcentaje_restante <= 30 and o.nivel_alerta == 1:
                    destinatarios = destinatarios_base + ["dgic.direccion@juarez.gob.mx"]

                    self.enviar(o, "30%", destinatarios, nombres_usuarios)
                    o.nivel_alerta = 2
                    o.save(update_fields=["nivel_alerta"])

                elif porcentaje_restante <= 0:
                    hoy = timezone.localdate()

                    if o.ultima_alerta_vencido != hoy:

                        destinatarios = destinatarios_base + ["dgic.direccion@juarez.gob.mx"]

                        self.enviar(o, "VENCIDO", destinatarios, nombres_usuarios)

                        o.nivel_alerta = 3
                        o.ultima_alerta_vencido = hoy

                        o.save(update_fields=[
                            "nivel_alerta",
                            "ultima_alerta_vencido"
                        ])

            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"Error procesando orden {o.orden}: {e}"
                ))
                
    def enviar(self, orden, nivel, destino, nombres_usuarios=None):

        contexto = {
            'orden': orden,
            'nivel': nivel,
            'categoria': orden.get_categoria_display(),
            'fecha_vencimiento': orden.fecha_vencimiento,
            'usuarios': nombres_usuarios or [],
            'url_orden': "https://hlpdesk/gobjuarez.mpio/ordenes/ordenes/",
        }

        exito = Notificar.correo_html(
            destino,
            f"ALERTA {nivel}: Orden #{orden.orden}",
            'correos/recordatorios.html',
            contexto
        )

        if exito:
            self.stdout.write(self.style.SUCCESS(
                f"[OK] {nivel} | Orden {orden.orden} | Usuarios: {', '.join(nombres_usuarios or [])}"
            ))
        else:
            self.stdout.write(self.style.ERROR(
                f"[ERROR] {nivel} | Orden {orden.orden}"
        ))
