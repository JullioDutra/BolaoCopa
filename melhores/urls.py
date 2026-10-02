from django.urls import path

from . import views

app_name = 'melhores'

urlpatterns = [
    path('', views.home, name='home'),
    path('apostar/<int:categoria_id>/', views.apostar, name='apostar'),
    path('cupom/', views.apostar_cupom, name='apostar_cupom'),
    path('cancelar/<int:categoria_id>/', views.cancelar, name='cancelar'),
    path('minhas-apostas/', views.minhas_apostas, name='minhas'),
    path('ranking/', views.ranking, name='ranking'),
    path('api/odds/', views.api_odds, name='api_odds'),
    path('staff/', views.staff_painel, name='staff'),
    path('staff/<int:categoria_id>/', views.staff_acao, name='staff_acao'),
]
