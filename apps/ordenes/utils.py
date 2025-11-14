import pyodbc
from .models import Orden
from .forms import OrdenForm, EquipoXOrdenForm
from django.shortcuts import redirect
from django.shortcuts import render

def obtener_conexion():
    """String de conexión a Sybase"""

    conn_str = (
        "DRIVER={FreeTDS};"
        "SERVER=rhumanos;"
        "UID=internet;"
        "PWD=internetweb;"
        "TDS_Version=8.0;"
    )
    return pyodbc.connect(conn_str)

def ejecutar_consulta(query, params=None):
    """Ejectuta el query recibido como parámetro y devuelve los resultados."""

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        columnas = [column[0] for column in cursor.description]
        resultados = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
        return resultados
    
    finally:
        cursor.close()
        conexion.close()


def equipos_form(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_equipo'] = EquipoXOrdenForm()
        return context

def post(self, request, *args, **kwargs):
    form_orden = OrdenForm(request.POST)
    form_equipo = EquipoXOrdenForm(request.POST)

    if form_orden.is_valid():
        orden = form_orden.save()

        if form_equipo.is_valid():
            equipo = form_equipo.save(commit=False)
            equipo.orden = orden
            equipo.save()

        return redirect(self.success_url)

    return render(request, self.template_name, {
        'form': form_orden,
        'form_equipo': form_equipo
    })