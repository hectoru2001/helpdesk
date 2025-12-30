from django.db import models
from django.utils import timezone
from datetime import timedelta
from apps.ordenes.models import Orden

class TokenComentario(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name="comentario")
    token = models.CharField(max_length=255, unique=True)
    calificacion = models.IntegerField(null=True, blank=True)
    comentario = models.TextField(null=True, blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    usado = models.BooleanField(default=False)

    def expirado(self):
        return timezone.now() > self.creado + timedelta(hours=24)
