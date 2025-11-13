from django.shortcuts import render
from .models import Orden
from .forms import OrdenForm
from django.shortcuts import redirect

def formulario_nueva_orden(request):
    form = OrdenForm()
    return render(request, 'nueva_orden.html', {'form': form})

def crear_orden(request):
    if request.method == 'POST':
        form = OrdenForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ordenes:lista_ordenes')
    else:
        form = OrdenForm()
    return render(request, 'ordenes/crear_orden.html', {'form': form})