import pytest
from apps.ordenes.forms import OrdenForm, EquipoXOrdenForm
from apps.ordenes.models import *

@pytest.mark.django_db
def test_crear_orden():

    # Datos necesarios para la orden
    aplicacion = Aplicaciones.objects.create(descripcion="App de prueba", estatus=1)
    clasificacion = Clasificaciones.objects.create(descripcion="Clasificacion de prueba", estatus=1)
    problema = Problemas.objects.create(descripcion="Problema de prueba", estatus=1)

    # Datos para equipo asociado a la orden
    marca = Marcas.objects.create(marca="Marca de prueba", estatus="A")
    color = Colores.objects.create(color="Color de prueba", estatus="A")


    datosOrden = {
        "oficio": "",
        "usuario_solicita": 1,
        "usuario_asigna": 1,
        "telefono": "1234567890",
        "aplicacion": aplicacion.id,
        "clasificacion": clasificacion.id,
        "problema": problema.id,
        "descripcion": "Descripcion de prueba",
        "solucion": "Solucion de prueba",
        "prioridad": "Alta",
        "equipo": True,
        "captura": 1,
        "estatus": "Abierta",
        "capacitacion": "Ninguna",
        "capacitacion_descripcion": "Ninguna",
    }

    formOrden = OrdenForm(data=datosOrden)

    datosEquipo = {
        "orden": formOrden.instance,
        "equipo": "Laptop Dell",
        "patrimonio": "12345",
        "serie": "ABCDE12345",
        "marca": marca.id,
        "color": color.id,
        "entregado_foraneo": 0,
    }

    if datosOrden.get("equipo") == True:
        formEquipo = EquipoXOrdenForm(data=datosEquipo)
        assert formEquipo.is_valid(), f" {formEquipo.errors}"


    assert formOrden.is_valid(), f" {formOrden.errors}"
