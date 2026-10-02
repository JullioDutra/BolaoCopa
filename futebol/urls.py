from django.urls import path

from . import views

app_name = 'futebol'

urlpatterns = [
    path('', views.hub, name='hub'),
    path('buscar/', views.buscar, name='buscar'),
    path('api/buscar/', views.api_buscar, name='api_buscar'),
    path('api/ao-vivo/', views.api_ao_vivo, name='api_ao_vivo'),
    path('api/noticias/', views.api_noticias, name='api_noticias'),
    path('api/raio-x/<int:jogo_id>/', views.api_raio_x, name='api_raio_x'),
    path('time/<int:pk>/', views.time_detalhe, name='time'),
    path('jogador/<int:pk>/', views.jogador_detalhe, name='jogador'),
    path('tabela/', views.tabela, name='tabela'),
    path('artilharia/', views.artilharia, name='artilharia'),
    path('comparar/', views.comparar, name='comparar'),
    path('comparativo/novo/', views.comparativo_novo, name='comparativo_novo'),
    path('comparativos/', views.comparativo_lista, name='comparativo_lista'),
    path('comparativo/<int:pk>/', views.comparativo_detalhe, name='comparativo'),
    path('comparativo/<int:pk>/votar/', views.comparativo_votar, name='comparativo_votar'),
    path('comparativo/<int:pk>/encerrar/', views.comparativo_encerrar, name='comparativo_encerrar'),
]
