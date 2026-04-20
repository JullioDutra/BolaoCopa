from django.urls import path
from . import views

app_name = 'palpites'

urlpatterns = [
    path('jogos/', views.listar_jogos, name='listar_jogos'),
    path('fazer-palpite/<int:jogo_id>/', views.fazer_palpite, name='fazer_palpite'),
    path('ranking/', views.ranking_geral, name='ranking_geral'),
]