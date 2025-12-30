from django.urls import path
from .views import login_view, logout_view, cambiar_contrasena

urlpatterns = [
    path('', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('cambiar_contrasena/', cambiar_contrasena, name='cambiar_contrasena'),
]
