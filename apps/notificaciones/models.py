from django.db import models

class Notificacion(models.Model):
    titulo = models.CharField(max_length=150)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=20, default='info')
    creada = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)
    orden = models.CharField(blank=True, null=True)
    usuario = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.CASCADE, related_name='notificaciones')

class TelegramUser(models.Model):
    usuario = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    chat_id = models.CharField(max_length=50)
