from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.servicios.empleados import *
from datetime import timedelta
from datetime import time
from django.utils import timezone

class BuscarEmpleadoAPI(APIView):

    def get(self, request):
        q = request.GET.get("q", "").strip()

        if q == "":
            empleados = EmpleadoServicio.listar_todos()

        elif q.isdigit():
            empleados = EmpleadoServicio.buscar_numempleado(q)

        else:
            empleados = EmpleadoServicio.buscar_empleado(q)

        return Response({"resultados": empleados}, status=200)
    
class BuscarFuncionarioAPI(APIView):

    def get(self, request):
        q = request.GET.get("q", "").strip()

        funcionarios = EmpleadoServicio.buscar_funcionario(q)

        return Response({"resultados": funcionarios}, status=200)
    
class BuscarPatrimonioAPI(APIView):

    def get(self, request):
        q = request.GET.get("q", "").strip()

        patrimonios = EmpleadoServicio.buscar_numpatrimonio(q)

        return Response({"resultados": patrimonios}, status=200)
    

from datetime import time, datetime, timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError


# ==============================
# CONFIGURACIÓN HORARIO LABORAL
# ==============================
WORKDAY_START_HOUR = 8
WORKDAY_END_HOUR = 15
# Duración de la jornada en minutos (7 horas = 420 min)
MINUTOS_POR_DIA = (WORKDAY_END_HOUR - WORKDAY_START_HOUR) * 60
WORKING_DAYS = [0, 1, 2, 3, 4]

# ==============================
# TABLA SLA (EN MINUTOS)
# ==============================

TIEMPOS = {
    'soporte_técnico': {
        'inmediata': 120,
        'urgente': 240,
        'normal': 1440,
        'minima': 4320
    },
    'redes': {
        'inmediata': 180,
        'urgente': 360,
        'normal': 1440,
        'minima': 4320
    },
    'servidores': {
        'inmediata': 240,
        'urgente': 360,
        'normal': 2880,
        'minima': 5760
    },
    'programadores': {
        'inmediata': 480,
        'urgente': 480,
        'normal': 2880,
        'minima': 10080
    }
}


# ==============================
# FUNCIONES AUXILIARES
# ==============================

def es_dia_laboral(fecha):
    return fecha.weekday() in WORKING_DAYS

def normalizar_a_inicio_jornada(fecha):
    """Lleva la fecha al inicio del horario laboral del mismo día."""
    return fecha.replace(hour=WORKDAY_START_HOUR, minute=0, second=0, microsecond=0)

def sumar_minutos_laborales(fecha_inicio, minutos_totales):
    # Asegurar que trabajamos con la hora local configurada en Django
    fecha_actual = timezone.localtime(fecha_inicio)
    minutos_restantes = minutos_totales

    while minutos_restantes > 0:
        # 1. Si no es día laboral, saltar al inicio del siguiente día hábil
        if not es_dia_laboral(fecha_actual):
            fecha_actual = normalizar_a_inicio_jornada(fecha_actual + timedelta(days=1))
            continue

        # 2. Si es antes de las 8:00 AM, ajustar a las 8:00 AM
        if fecha_actual.hour < WORKDAY_START_HOUR:
            fecha_actual = normalizar_a_inicio_jornada(fecha_actual)

        # 3. Si es después de las 3:00 PM, saltar al día siguiente a las 8:00 AM
        if fecha_actual.hour >= WORKDAY_END_HOUR:
            fecha_actual = normalizar_a_inicio_jornada(fecha_actual + timedelta(days=1))
            continue

        # 4. Calcular cuánto tiempo queda en el día actual hasta las 3:00 PM
        fin_jornada = fecha_actual.replace(hour=WORKDAY_END_HOUR, minute=0, second=0, microsecond=0)
        minutos_disponibles_hoy = int((fin_jornada - fecha_actual).total_seconds() / 60)

        if minutos_restantes <= minutos_disponibles_hoy:
            # El vencimiento es hoy mismo
            return fecha_actual + timedelta(minutes=minutos_restantes)
        else:
            # Agotar el día actual y saltar al día siguiente
            minutos_restantes -= minutos_disponibles_hoy
            fecha_actual = normalizar_a_inicio_jornada(fecha_actual + timedelta(days=1))

    return fecha_actual

# ==============================
# FUNCIÓN PRINCIPAL (Ajuste de validación)
# ==============================

def calcular_vencimiento(fecha_inicio, categoria, prioridad, fecha_manual=None):
    if prioridad == "programada":
        if not fecha_manual:
            raise ValidationError("Fecha manual requerida para prioridad programada")
        return fecha_manual

    if not fecha_inicio:
        raise ValidationError("Fecha de inicio requerida")

    # Validación de existencia en el diccionario
    cat_data = TIEMPOS.get(categoria)
    if not cat_data:
        raise ValidationError(f"Categoría '{categoria}' no válida")

    minutos = cat_data.get(prioridad)
    if minutos is None:
        raise ValidationError(f"Prioridad '{prioridad}' no válida para {categoria}")

    # Asegurar Timezone
    if timezone.is_naive(fecha_inicio):
        fecha_inicio = timezone.make_aware(fecha_inicio)

    return sumar_minutos_laborales(fecha_inicio, minutos)