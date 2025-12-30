from django.db import models

TIPO_USUARIO = [
        ('P', 'Programador'),
        ('T', 'Técnico'),
        ('R', 'Jefe de Progrmación'),
        ('E', 'Jefe de Técnicos'),
        ('A', 'Administrador'),
    ]

ESTATUS_USUARIO = [
    ('A', 'Activo'),
    ('I', 'Inactivo'),
    ('B', 'Baja')
]

class ExtraUsuarios(models.Model):
    usuario = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name="extra")
    empleado = models.IntegerField(unique=True)
    estatus = models.CharField(choices=ESTATUS_USUARIO ,max_length=2, default="A")
    tipo = models.CharField(choices=TIPO_USUARIO, max_length=1)
    notificaciones = models.BooleanField(default=1)
    vacaciones = models.BooleanField(default=0)
    reportar = models.BooleanField(default=0)
    nivel_rep = models.IntegerField(default=0)
    acronimo = models.CharField(max_length=10, blank=True, null=True)
    actualizado = models.IntegerField(default=0)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    departamento = models.ForeignKey('Departamentos', on_delete=models.CASCADE, null=True, blank=True)
    cambio_contrasena = models.BooleanField(default=0)

class Departamentos(models.Model):
    nombre = models.CharField(max_length=100)
    estatus = models.CharField(max_length=2)
    fecha_creacion = models.DateTimeField(auto_now=True)
    fecha_baja = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.nombre
