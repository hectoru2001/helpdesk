from django.urls import path
from .views import  OrdenCreateTicket, ListaOrdenes

urlpatterns = [
    # path('crear/', views.formulario_nueva_orden, name='crear_orden'),
    path('crear/', OrdenCreateTicket.as_view(), name='crear_orden'),
    path('lista/', ListaOrdenes.as_view(), name='lista_ordenes'),

]
