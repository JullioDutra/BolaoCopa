from django.urls import path

from . import views

app_name = 'quemsoueu'

urlpatterns = [
    # --- Telas ---
    path('', views.hub, name='hub'),
    path('desafio/', views.desafio, name='desafio'),
    path('treino/', views.treino, name='treino'),
    path('rodada/<int:pk>/', views.rodada, name='rodada'),

    # --- APIs (JSON) ---
    path('api/rodada/<int:pk>/', views.api_estado, name='api_estado'),
    path('api/rodada/<int:pk>/rapida/', views.api_rapida, name='api_rapida'),
    path('api/rodada/<int:pk>/perguntar/', views.api_perguntar, name='api_perguntar'),
    path('api/rodada/<int:pk>/dica/', views.api_dica, name='api_dica'),
    path('api/rodada/<int:pk>/palpite/', views.api_palpite, name='api_palpite'),
    path('api/rodada/<int:pk>/desistir/', views.api_desistir, name='api_desistir'),
]
