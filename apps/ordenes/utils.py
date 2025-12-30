from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.servicios.empleados import EmpleadoServicio

class BuscarEmpleadoAPI(APIView):

    def get(self, request):
        q = request.GET.get("q", "").strip()

        if q == "":
            empleados = EmpleadoServicio.listar_todos()

        elif q.isdigit():
            empleados = EmpleadoServicio.buscar_numempleado(q)

        else:
            empleados = EmpleadoServicio.buscar_empleado(q)

        return Response({"resultados": empleados}, status=200)