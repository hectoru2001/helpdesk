from django.utils.crypto import get_random_string
from django.conf import settings
from .models import TokenComentario
from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import get_object_or_404

def comentario_orden(request, token):
    token_obj = get_object_or_404(TokenComentario, token=token)

    context = {
        "orden": token_obj.orden,
        "token_usado": token_obj.usado,
    }

    if token_obj.usado:
        context["mensaje_error"] = "Este enlace ya fue utilizado y no puede volver a usarse."
        return render(request, "partials/comentario_orden.html", context)

    if request.method == "POST":
        comentario = request.POST.get("comentario", "").strip()
        calificacion = request.POST.get("calificacion")

        if not comentario or not calificacion:
            context["error_formulario"] = "Debes llenar todos los campos."
            return render(request, "partials/comentario_orden.html", context)

        token_obj.comentario = comentario
        token_obj.calificacion = int(calificacion)
        token_obj.usado = True
        token_obj.save()

        context["mensaje_exito"] = "Gracias, tu comentario fue registrado correctamente."
        context["token_usado"] = True  # 🔒 bloquear después de guardar
        return render(request, "partials/comentario_orden.html", context)

    return render(request, "partials/comentario_orden.html", context)

def generar_url_comentario(request, orden):
    token = get_random_string(48)

    TokenComentario.objects.create(
        orden=orden,
        token=token
    )

    url = request.build_absolute_uri(
        reverse("comentario_orden", args=[token])
    )

    return url
