from django.views.generic import ListView
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from apps.ordenes.models import Aplicaciones, Clasificaciones
from core.decorators.permisos import administrador_required
from .forms import AplicacionForm, ClasificacionForm
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