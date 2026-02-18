from django.shortcuts import render
from .services import obtener_correos


def bandeja_correos(request):
    correos = []
    error = None

    try:
        correos = obtener_correos(limit=20)
    except Exception as e:
        error = str(e)

    return render(request, "bandeja.html", {
        "correos": correos,
        "error": error
    })
