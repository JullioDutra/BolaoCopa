from django.urls import path

from . import views

app_name = 'conta'

urlpatterns = [
    path('time/', views.escolher_time, name='escolher_time'),
    path('coins/', views.extrato_coins, name='extrato_coins'),
]
