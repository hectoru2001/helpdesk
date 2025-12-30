from django.urls import path
from .views import DashboardView

urlpatterns = [
    # Otras rutas de la aplicación 'inicio'...
    path('', DashboardView.as_view(), name='inicio'),  # Página principal
]