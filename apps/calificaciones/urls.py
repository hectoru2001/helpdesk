from django.urls import path
from .views import comentario_orden

urlpatterns = [
    path("comentario/<str:token>/", comentario_orden, name="comentario_orden"),
]
