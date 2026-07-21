from django.urls import path
from . import views

app_name = 'palpites'
urlpatterns = [
    path('jogos/', views.listar_jogos, name='listar_jogos'),
    path('fazer-palpite/<int:jogo_id>/', views.fazer_palpite, name='fazer_palpite'),
    path('ranking/', views.ranking_geral, name='ranking_geral'),
    path('oscar/', views.indicar_oscar, name='indicar_oscar'),
    path('admin-resultados/', views.inserir_resultados_finais, name='inserir_resultados_finais'),
    path('longo-prazo/', views.meus_palpites_longo_prazo, name='meus_palpites_longo_prazo'),
    path('admin-painel/', views.painel_controle_admin, name='painel_controle_admin'),
]
