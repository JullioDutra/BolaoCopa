from django.urls import path

from . import views

app_name = 'conta'

urlpatterns = [
    path('time/', views.escolher_time, name='escolher_time'),
    path('coins/', views.extrato_coins, name='extrato_coins'),
    path('perfil/', views.perfil, name='perfil'),
    path('recuperar/', views.recuperar_senha, name='recuperar'),
    path('nova-senha/<str:token>/', views.nova_senha, name='nova_senha'),
    path('staff/links-senha/', views.staff_links_senha, name='staff_links_senha'),
]
