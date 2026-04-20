from django.urls import path
from . import views

app_name = 'convocacao'

urlpatterns = [
    # A rota para a tela de escalar os 26 jogadores
    path('montar/', views.montar_selecao, name='montar_selecao'),
    path('resultado/', views.ranking_convocacao, name='ranking_convocacao'),
]