from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView, TemplateView
from django.db.models import Q
from .models import ExtraUsuarios
from .forms import UsuarioCompletoForm
from django.conf import settings
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.db import transaction, IntegrityError
from core.decorators.permisos import administrador_required
from django.utils.decorators import method_decorator

# Vistas para usuarios
@method_decorator(administrador_required(True), name='dispatch')
class ListaUsuarios(ListView):
    model = ExtraUsuarios
    template_name = 'lista_usuarios.html'
    context_object_name = 'usuarios'
    paginate_by = 10

    def get_queryset(self):
        qs = ExtraUsuarios.objects.select_related('usuario', 'departamento')

        q = self.request.GET.get('q', '').strip()
        estatus = self.request.GET.get('estatus', '').strip()
        clasificacion = self.request.GET.get('clasificacion', '').strip()

        if q:
            qs = qs.filter(
                Q(usuario__first_name__icontains=q) |
                Q(usuario__last_name__icontains=q) |
                Q(empleado__icontains=q)
            )

        if estatus:
            qs = qs.filter(estatus=estatus)

        if clasificacion:
            qs = qs.filter(tipo=clasificacion)

        qs = qs.order_by('empleado')
        return qs

@method_decorator(administrador_required(True), name='dispatch')
class CrearUsuario(CreateView):
    model = User
    form_class = UsuarioCompletoForm
    template_name = 'crear_usuario.html'
    success_url = reverse_lazy('lista_usuarios')

    def form_valid(self, form):
        try:
            with transaction.atomic():
                # Crear usuario
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                user.save()

                # Crear datos extra
                ExtraUsuarios.objects.create(
                    usuario=user,
                    tipo=form.cleaned_data['tipo'],
                    empleado=form.cleaned_data['empleado'],
                    estatus="A"
                )

            messages.success(self.request, "Usuario creado correctamente.")
            return redirect(self.success_url)

        except Exception as e:
            messages.error(self.request, "Ocurrió un error al crear el usuario.")
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.warning(self.request, f"{field.capitalize()}: {error}")
        return super().form_invalid(form)

@method_decorator(administrador_required(True), name='dispatch')
class DetalleUsuario(DetailView):
    model = ExtraUsuarios
    template_name = 'detalle_usuario.html'
    context_object_name = 'usuario'

    def get_queryset(self):
        return ExtraUsuarios.objects.select_related('usuario', 'departamento')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['MEDIA_URL'] = settings.MEDIA_URL
        return context


@method_decorator(administrador_required(True), name='dispatch')
class ActualizarUsuario(UpdateView):
    model = User
    form_class = UsuarioCompletoForm
    template_name = 'actualizar_usuario.html'
    success_url = reverse_lazy('lista_usuarios')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        try:
            kwargs['extrausuario'] = ExtraUsuarios.objects.get(usuario=self.object)
        except ExtraUsuarios.DoesNotExist:
            kwargs['extrausuario'] = None

        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        form.save_extra()

        if form.cleaned_data.get('password'):
            update_session_auth_hash(self.request, self.object)

        messages.success(self.request, "Usuario actualizado correctamente")
        return response

@method_decorator(administrador_required(True), name='dispatch')
class ListaEmpleados(TemplateView):
    template_name = "lista_empleados.html"

@administrador_required(True)
def eliminar_usuario(request, pk):
    """
    Elimina un usuario y sus dependientes de ExtraUsuarios.
    Todo se realiza dentro de una transacción para mayor seguridad.
    """
    usuario = get_object_or_404(User, pk=pk)

    try:
        with transaction.atomic():
            # Eliminar ExtraUsuarios relacionado
            ExtraUsuarios.objects.filter(usuario=usuario).delete()
            # Eliminar el usuario
            usuario.delete()

        messages.success(request, "Usuario eliminado correctamente.")
    except IntegrityError:
        messages.error(request, "No se pudo eliminar el usuario. Inténtelo de nuevo.")
    except Exception as e:
        messages.error(request, f"Error inesperado: {str(e)}")

    return redirect('lista_usuarios')