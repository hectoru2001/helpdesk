from django.db import models

class ExtraUsuarios(models.Model):
    usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    empleado = models.IntegerField()
    estatus = models.CharField(max_length=2)
    tipo = models.CharField(max_length=50)
    notificaciones = models.IntegerField()
    vacaciones = models.IntegerField()
    reportar = models.IntegerField()
    nivel_rep = models.IntegerField()
    acronimo = models.CharField(max_length=10)
    actualizado = models.IntegerField()
    fecha_nacimiento = models.DateField(null=True, blank=True)
    departamento = models.ForeignKey('Departamentos', on_delete=models.CASCADE)

class Departamentos(models.Model):
    nombre = models.CharField(max_length=100)
    estatus = models.CharField(max_length=2)
    fecha_creacion = models.DateTimeField(auto_now=True)
    fecha_baja = models.DateTimeField(null=True, blank=True)

