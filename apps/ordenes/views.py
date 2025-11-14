from django.shortcuts import render
from .models import Orden
from .forms import OrdenForm, EquipoXOrdenForm
from .utils import equipos_form, post
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView

@method_decorator(csrf_exempt, name='dispatch')
class OrdenCreateTicket(CreateView):
    model = Orden
    form_class = OrdenForm
    template_name = 'nueva_orden.html'
    success_url = '/ordenes/'

    def get_context_data(self, **kwargs):
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
            else:
                print(form_equipo.errors)
        else:
            print(form_orden.errors)

            return redirect(self.success_url)

        return render(request, self.template_name, {
            'form': form_orden,
            'form_equipo': form_equipo
        })


class ListaOrdenes(ListView):
    model = Orden
    template_name = 'lista_ordenes.html'
    context_object_name = 'ordenes'
    paginate_by = 10

def formulario_nueva_orden(request):
     form_orden = OrdenForm()
     form_equipo = EquipoXOrdenForm()
     return render(request, 'nueva_orden.html', {'form': form_orden, 'form_equipo': form_equipo})

@csrf_exempt
def crear_orden(request):
    if request.method == 'POST':
        form = OrdenForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_ordenes')
        else:
            print(form.errors)
    else:
        form = OrdenForm()
    return render(request, 'nueva_orden.html', {'form': form})