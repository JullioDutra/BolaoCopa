from django.urls import path
from . import views

app_name = 'convocacao'
urlpatterns = [
    # Modo ativo: escalação 4-3-3 do Brasileirão
    path('selecao/', views.montar_selecao, name='montar_selecao'),
    path('selecao/ranking/', views.ranking_brasileirao, name='ranking_brasileirao'),

    # Modo Copa (encerrado) — agora só mural + cronômetro para 2030
    path('copa/', views.copa_mural, name='copa_mural'),
    path('copa/ranking/', views.ranking_convocacao, name='ranking_convocacao'),
    path('copa/mais-escalados/', views.estatisticas_convocacao, name='mais_escalados'),
]
