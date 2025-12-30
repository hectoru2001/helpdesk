import os
import django
import csv
import unicodedata
import re

# 🔴 AJUSTA EL NOMBRE DEL PROYECTO
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "helpdesk.settings")
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from apps.usuarios.models import ExtraUsuarios

RUTA_CSV = "Lista_Empleados_Helpdesks.csv"

MAPA_TIPOS = {
    "Administrador": "A",
    "Programador": "P",
    "Técnico": "T",
    "Jefe Técnicos": "A",
    "Jefe Programadores": "A",
}

PASSWORD_INICIAL = "123"

def limpiar_texto(texto):
    texto = texto.strip().lower()
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"\s+", " ", texto)
    return texto

def formatear_usuario(nombre, apellido):
    nombre = limpiar_texto(nombre)
    apellido = limpiar_texto(apellido)

    primer_nombre = nombre.split(" ")[0]
    primer_apellido = apellido.split(" ")[0]

    return f"{primer_nombre[0]}.{primer_apellido}"

def importar_usuarios():
    with open(RUTA_CSV, newline="", encoding="utf-8") as archivo:
        lector = csv.DictReader(archivo)

        for fila in lector:
            numero = fila.get("Numero", "").strip()
            nombres = fila.get("Nombres", "").strip()
            apellidos = fila.get("Apellidos", "").strip()
            correo = fila.get("Correo", "").strip()
            tipo_texto = fila.get("Tipo", "").strip()

            tipo = MAPA_TIPOS.get(tipo_texto, "T")

            user, creado = User.objects.get_or_create(
                username=numero,
                defaults={
                    "first_name": nombres.title(),
                    "last_name": apellidos.title(),
                    "username": formatear_usuario(nombres, apellidos),
                    "email": correo.lower(),
                    "password": make_password(PASSWORD_INICIAL),
                    "is_active": True,
                }
            )

            if not creado:
                user.first_name = nombres.title()
                user.last_name = apellidos.title()
                user.email = correo.lower()
                user.save()

            ExtraUsuarios.objects.get_or_create(
                usuario=user,
                defaults={
                    "tipo": tipo,
                    "cambio_contrasena": False,
                    "empleado": numero,
                }
            )

            print(f"✔ {numero} - {user.get_full_name()} [{tipo}]")

if __name__ == "__main__":
    importar_usuarios()
    print("✔ Importación finalizada correctamente")


