from django.shortcuts import render
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect

from .forms import CambiarContraseñaForm

@login_required
def cambiar_contrasena(request):
    if request.method == 'POST':
        form = CambiarContraseñaForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Su contraseña ha sido actualizada con éxito.')
            return redirect('nombre_de_la_vista_donde_redirigir')
    else:
        form = CambiarContraseñaForm(user=request.user)
    return render(request, 'nueva_contrasena.html', {'form': form})
