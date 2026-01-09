from django.db import models

vacios = {
    'blank': True,
    'null': True,
}

ESTATUS = [
    ('A', 'Asignada'),
    ('E', 'En proceso'),
    ('C', 'Cancelada'),
    ('T', 'Terminada'),
    ('P', 'Aprobada'),
]

PRIORIDADES = [
    ('minima', 'Mínima'),
    ('inmediata', 'Inmediata'),
    ('urgente', 'Urgente'),
    ('programada', 'Programada'),
    ('normal', 'Normal'),
]

# Modelos para ordenes
class Orden(models.Model):
    orden = models.AutoField(primary_key=True)
    oficio = models.CharField(max_length=25, default='S/N', **vacios)
    usuario_solicita = models.IntegerField()
    usuario_beneficiado = models.IntegerField()
    telefono = models.CharField(max_length=15, **vacios)
    aplicacion = models.ForeignKey('Aplicaciones', on_delete=models.CASCADE)
    clasificacion = models.ForeignKey('Clasificaciones', on_delete=models.CASCADE)
    descripcion = models.TextField()
    solucion = models.TextField(**vacios)
    prioridad = models.CharField(choices=PRIORIDADES, max_length=12)
    equipo = models.BooleanField(default=False)
    captura = models.IntegerField(**vacios)
    estatus = models.CharField(choices=ESTATUS, max_length=2, default='A', **vacios)
    capacitacion = models.CharField(max_length=100, default='N', **vacios)
    capacitacion_descripcion = models.TextField(**vacios)
    fecha_captura = models.DateTimeField(auto_now_add=True, **vacios)
    fecha_inicio = models.DateTimeField(**vacios)
    fecha_terminado = models.DateTimeField(**vacios)

class OrdenxArchivo(models.Model):
    orden = models.ForeignKey('Orden', on_delete=models.CASCADE, related_name='archivos')
    archivo = models.FileField(upload_to='archivos_ordenes/')
    descripcion = models.CharField(max_length=100, **vacios)

    def save(self, *args, **kwargs):
        if not self.descripcion:
            self.descripcion = self.archivo.name
        super().save(*args, **kwargs)

    def __str__(self):
        return self.archivo or 'Archivo {self.id}'

class UsuariosxOrden(models.Model):
    orden = models.ForeignKey('Orden', on_delete=models.CASCADE, related_name='usuarios_orden')
    realiza = models.ForeignKey('auth.User', on_delete=models.CASCADE, **vacios)
    inicia = models.DateTimeField(**vacios)
    termina = models.DateTimeField(**vacios)
    asigna = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='asigna_usuario', **vacios)
    fecha_asigna = models.DateTimeField(auto_now_add=True)
    estatus_orden = models.CharField(choices=ESTATUS, **vacios)
    estatus = models.CharField(choices=ESTATUS, **vacios)
    causa = models.CharField(max_length=100, **vacios)
    etiquetas = models.CharField(max_length=100, **vacios)
    comentarios = models.TextField(**vacios)
    solucion = models.TextField(**vacios)
    
class EquipoXOrden(models.Model):
    orden = models.ForeignKey('Orden', on_delete=models.CASCADE, related_name='equipos')
    equipo = models.CharField(max_length=100, **vacios)
    patrimonio = models.CharField(max_length=50)
    serie = models.CharField(max_length=50)
    descripcion = models.TextField(**vacios)
    marca = models.ForeignKey('Marcas', on_delete=models.CASCADE)
    color = models.ForeignKey('Colores', on_delete=models.CASCADE)
    entregado_foraneo = models.IntegerField(choices=[(0, 'Dentro'), (1, 'Foraneo')])
    observaciones = models.TextField(**vacios)
    salida = models.IntegerField(**vacios)
    nombre_resguardante = models.CharField(max_length=100, **vacios)
    area_resguardante = models.CharField(max_length=100, **vacios)

class SolicitantexOrden(models.Model):
    orden = models.ForeignKey('Orden', on_delete=models.CASCADE, related_name='solicitantes')
    usuario_beneficiado = models.IntegerField()
    nombre_beneficiado = models.CharField(max_length=100, **vacios)
    puesto_beneficiado = models.CharField(max_length=100)
    dependencia_beneficiado = models.CharField(max_length=100, **vacios)
    correo_beneficiado = models.CharField(max_length=100, **vacios)
    telefono_beneficiado = models.CharField(max_length=50, **vacios) 
    usuario_solicita = models.IntegerField()
    nombre_solicitante = models.CharField(max_length=100, **vacios)
    puesto_solicitante = models.CharField(max_length=100, **vacios)
    dependencia_solicitante = models.CharField(max_length=100, **vacios)
    correo_solicitante = models.CharField(max_length=100, **vacios)
    telefono_solicitante = models.CharField(max_length=50, **vacios)  


# Modelos auxiliares
class Aplicaciones(models.Model):
    descripcion = models.CharField(max_length=100)
    estatus = models.IntegerField()

    def __str__(self):
        return self.descripcion
    
class Clasificaciones(models.Model):
    descripcion = models.CharField(max_length=100)
    estatus = models.IntegerField()

    def __str__(self):
        return self.descripcion
    
class Marcas(models.Model):
    marca = models.CharField(max_length=100)
    estatus = models.CharField(max_length=2)

    def __str__(self):
        return self.marca
    
class Colores(models.Model):
    color = models.CharField(max_length=100)
    estatus = models.CharField(max_length=2)

    def __str__(self):
        return self.color