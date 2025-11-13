from django.urls import path
from .views import login_view, logout_view, main

urlpatterns = [
    path('', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('inicio/', main, name='main'),
]
