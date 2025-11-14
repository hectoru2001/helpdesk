from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.models import User
from .models import ExtraUsuarios


# Vistas para usuarios
class ListaUsuarios(ListView):
    model = ExtraUsuarios
    template_name = 'lista_usuarios.html'
    context_object_name = 'usuarios'
    paginate_by = 10

    def get_queryset(self):
        return ExtraUsuarios.objects.select_related('usuario', 'departamento')