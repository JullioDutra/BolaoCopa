from django.urls import path

from . import views

app_name = 'avisos'

urlpatterns = [
    path('', views.central, name='central'),
    path('api/chave/', views.api_chave, name='api_chave'),
    path('api/inscrever/', views.api_inscrever, name='api_inscrever'),
    path('api/cancelar/', views.api_cancelar, name='api_cancelar'),
    path('testar/', views.testar, name='testar'),
    path('staff/', views.staff_painel, name='staff'),
    path('resenha/', views.resenha, name='resenha'),
]
