from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.servicios.empleados import *

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
    
class BuscarFuncionarioAPI(APIView):

    def get(self, request):
        q = request.GET.get("q", "").strip()

        funcionarios = EmpleadoServicio.buscar_funcionario(q)

        return Response({"resultados": funcionarios}, status=200)
    
class BuscarPatrimonioAPI(APIView):

    def get(self, request):
        q = request.GET.get("q", "").strip()

        patrimonios = EmpleadoServicio.buscar_numpatrimonio(q)

        return Response({"resultados": patrimonios}, status=200)