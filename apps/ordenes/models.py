from django.db import models

vacios = {
    'blank': True,
    'null': True,
}

# Modelos para ordenes
class Orden(models.Model):
    orden = models.AutoField(primary_key=True)
    oficio = models.CharField(max_length=20, default='S/N', blank=True, null=True)
    usuario_solicita = models.IntegerField()
    usuario_asigna = models.IntegerField()
    telefono = models.CharField(max_length=15, **vacios)
    aplicacion = models.ForeignKey('Aplicaciones', on_delete=models.CASCADE)
    clasificacion = models.ForeignKey('Clasificaciones', on_delete=models.CASCADE)
    problema = models.ForeignKey('Problemas', on_delete=models.CASCADE)
    descripcion = models.TextField()
    solucion = models.TextField(**vacios)
    prioridad = models.CharField(max_length=20)
    equipo = models.BooleanField(default=False)
    captura = models.IntegerField(**vacios)
    fecha_captura = models.DateTimeField(auto_now=True)
    estatus = models.CharField(max_length=2, default='A', **vacios)
    capacitacion = models.CharField(max_length=100, default='N', **vacios)
    capacitacion_descripcion = models.TextField(**vacios)
    fecha_terminado = models.DateTimeField(null=True, blank=True)

class UsuariosxOrden(models.Model):
    orden = models.ForeignKey('Orden', on_delete=models.CASCADE)
    realiza = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    inicia = models.DateTimeField(blank=True, null=True)
    termina = models.DateTimeField(blank=True, null=True)
    asigna = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='asigna_usuario')
    fecha_asigna = models.DateTimeField(auto_now=True)
    estatus_orden = models.CharField(max_length=2)
    estatus = models.CharField(max_length=2)
    causa = models.CharField(max_length=100)
    etiquetas = models.CharField(max_length=100)
    
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






# Modelos auxiliares
class Aplicaciones(models.Model):
    descripcion = models.CharField(max_length=100)
    estatus = models.IntegerField()

    def __str__(self):
        return self.descripcion

class Problemas(models.Model):
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