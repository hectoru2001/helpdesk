from django.views.generic import ListView
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from apps.ordenes.models import Aplicaciones, Clasificaciones, Marcas, Colores
from core.decorators.permisos import administrador_required
from .forms import AplicacionForm, ClasificacionForm, MarcaForm, ColorForm
from django.shortcuts import render

@method_decorator(administrador_required(True), name='dispatch')
class ListaClasificaciones(ListView):
    model = Clasificaciones
    template_name = 'lista_clasificaciones.html'
    context_object_name = 'clasificaciones'
    paginate_by = 10

    def get_queryset(self):
        qs = Clasificaciones.objects.all().order_by('id')

        q = self.request.GET.get('q')
        estatus = self.request.GET.get('estatus')

        if q:
            qs = qs.filter(descripcion__icontains=q)

        if estatus not in ("", None):
            qs = qs.filter(estatus=estatus)

        return qs


@method_decorator(administrador_required(True), name='dispatch')
class ListaAplicaciones(ListView):
    model = Aplicaciones
    template_name = 'lista_aplicaciones.html'
    context_object_name = 'aplicaciones'
    paginate_by = 10

    def get_queryset(self):
        qs = Aplicaciones.objects.all().order_by('id')

        q = self.request.GET.get('q')
        estatus = self.request.GET.get('estatus')

        if q:
            qs = qs.filter(descripcion__icontains=q)

        if estatus not in ("", None):
            qs = qs.filter(estatus=estatus)

        return qs

class ListaMarcas(ListView):
    model = Marcas
    template_name = 'lista_marcas.html'
    context_object_name = 'marcas'
    paginate_by = 10

    def get_queryset(self):
        qs = Marcas.objects.all().order_by('id')

        q = self.request.GET.get('q')
        estatus = self.request.GET.get('estatus')

        if q:
            qs = qs.filter(marca__icontains=q)

        if estatus not in ("", None):
            qs = qs.filter(estatus=estatus)

        return qs
    
class ListaColores(ListView):
    model = Colores
    template_name = 'lista_colores.html'
    context_object_name = 'colores'
    paginate_by = 10

    def get_queryset(self):
        qs = Colores.objects.all().order_by('id')

        q = self.request.GET.get('q')
        estatus = self.request.GET.get('estatus')

        if q:
            qs = qs.filter(color__icontains=q)

        if estatus not in ("", None):
            qs = qs.filter(estatus=estatus)

        return qs

@administrador_required(True)
def crear_aplicacion(request):
    form = AplicacionForm(request.POST or None)

    if form.is_valid():
        form.save()
        messages.success(request, "Aplicación creada correctamente")
        return redirect('lista_aplicaciones')

    return render(request, 'form_aplicacion.html', {
        'form': form,
        'titulo': 'Nueva aplicación'
    })

@administrador_required(True)
def crear_marca(request):
    form = MarcaForm(request.POST or None)

    if form.is_valid():
        form.save()
        messages.success(request, "Marca creada correctamente")
        return redirect('lista_marcas')

    return render(request, 'form_marca.html', {
        'form': form,
        'titulo': 'Nueva marca'
    })

@administrador_required(True)
def crear_color(request):
    form = ColorForm(request.POST or None)

    if form.is_valid():
        form.save()
        messages.success(request, "Color creado correctamente")
        return redirect('lista_colores')

    return render(request, 'form_color.html', {
        'form': form,
        'titulo': 'Nuevo color'
    })

@administrador_required(True)
def crear_clasificacion(request):
    form = ClasificacionForm(request.POST or None)

    if form.is_valid():
        form.save()
        messages.success(request, "Clasificación creada correctamente")
        return redirect('lista_clasificaciones')

    return render(request, 'form_clasificacion.html', {
        'form': form,
        'titulo': 'Nueva clasificación'
    })


@administrador_required(True)
def editar_aplicacion(request, pk):
    aplicacion = get_object_or_404(Aplicaciones, pk=pk)
    form = AplicacionForm(request.POST or None, instance=aplicacion)

    if form.is_valid():
        form.save()
        messages.success(request, "Aplicación actualizada correctamente")
        return redirect('lista_aplicaciones')

    return render(request, 'form_aplicacion.html', {
        'form': form,
        'titulo': 'Editar aplicación'
    })

@administrador_required(True)
def editar_clasificacion(request, pk):
    clasificacion = get_object_or_404(Clasificaciones, pk=pk)
    form = ClasificacionForm(request.POST or None, instance=clasificacion)

    if form.is_valid():
        form.save()
        messages.success(request, "Clasificación actualizada correctamente")
        return redirect('lista_clasificaciones')

    return render(request, 'form_clasificacion.html', {
        'form': form,
        'titulo': 'Editar clasificación'
    })

@administrador_required(True)
def editar_marca(request, pk):
    marca = get_object_or_404(Marcas, pk=pk)
    form = MarcaForm(request.POST or None, instance=marca)

    if form.is_valid():
        form.save()
        messages.success(request, "Marca actualizada correctamente")
        return redirect('lista_marcas')

    return render(request, 'form_marca.html', {
        'form': form,
        'titulo': 'Editar marca'
    })

def editar_color(request, pk):
    color = get_object_or_404(Colores, pk=pk)
    form = ColorForm(request.POST or None, instance=color)

    if form.is_valid():
        form.save()
        messages.success(request, "Color actualizado correctamente")
        return redirect('lista_colores')

    return render(request, 'form_color.html', {
        'form': form,
        'titulo': 'Editar color'
    })

@administrador_required(True)
def eliminar_aplicacion(request, pk):
    aplicacion = get_object_or_404(Aplicaciones, pk=pk)
    aplicacion.delete()
    messages.success(request, "Aplicación eliminada correctamente")
    return redirect('lista_aplicaciones')


@administrador_required(True)
def eliminar_clasificacion(request, pk):
    clasificacion = get_object_or_404(Clasificaciones, pk=pk)
    clasificacion.delete()
    messages.success(request, "Clasificación eliminada correctamente")
    return redirect('lista_clasificaciones')

@administrador_required(True)
def eliminar_marca(request, pk):
    marca = get_object_or_404(Marcas, pk=pk)
    marca.delete()
    messages.success(request, "Marca eliminada correctamente")
    return redirect('lista_marcas')

@administrador_required(True)
def eliminar_color(request, pk):
    color = get_object_or_404(Colores, pk=pk)
    color.delete()
    messages.success(request, "Color eliminado correctamente")
    return redirect('lista_colores')