from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from apps.usuarios.models import ExtraUsuarios

def login_view(request):
    if request.user.is_authenticated:
        return redirect('inicio')

    if request.method == 'POST':
        username = request.POST.get('usuario')
        password = request.POST.get('contrasena')

        usuario = authenticate(request, username=username, password=password)

        if usuario is not None:
            login(request, usuario)

            extra = ExtraUsuarios.objects.filter(usuario=usuario).first()
            if extra and not extra.cambio_contrasena:
                return redirect('cambiar_contrasena')
            
            
            return redirect('inicio')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
            return redirect('login')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def main(request):
    return render(request, 'plantilla.html')


@login_required
def cambiar_contrasena(request):
    extra = ExtraUsuarios.objects.get(usuario=request.user)

    if extra.cambio_contrasena:
        return redirect('inicio')
    
    if request.method == 'POST':
        field1 = request.POST.get('password1')
        field2 = request.POST.get('password2')

        if field1 != field2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('cambiar_contrasena')
        
        request.user.set_password(field1)
        request.user.save()

        extra.cambio_contrasena = True
        extra.save()

        update_session_auth_hash(request, request.user)

        messages.success(request, 'Contraseña cambiada exitosamente.')
        return redirect('inicio')
    
    return render(request, 'cambiar_contrasena.html')