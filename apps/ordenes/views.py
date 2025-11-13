from django.shortcuts import render
from .models import Orden
from .forms import OrdenForm, EquipoXOrdenForm
from django.shortcuts import redirect

def formulario_nueva_orden(request):
    form_orden = OrdenForm()
    form_equipo = EquipoXOrdenForm()
    return render(request, 'nueva_orden.html', {'form': form_orden, 'form_equipo': form_equipo})

def crear_orden(request):
    if request.method == 'POST':
        form = OrdenForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_ordenes')
    else:
        form = OrdenForm()
    return render(request, 'ordenes/crear_orden.html', {'form': form})