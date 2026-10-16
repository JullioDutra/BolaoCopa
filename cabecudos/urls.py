from django.urls import path

from . import views

app_name = 'cabecudos'

urlpatterns = [
    # --- Telas ---
    path('', views.hub, name='hub'),
    path('jogar/<int:fase>/', views.jogar, name='jogar'),

    # --- APIs (JSON) ---
    path('api/iniciar/', views.api_iniciar, name='api_iniciar'),
    path('api/finalizar/', views.api_finalizar, name='api_finalizar'),
]
