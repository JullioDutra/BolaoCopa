from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('noticias/', views.feed_noticias, name='feed_noticias'),
    path('tabela/', views.feed_tabela, name='feed_tabela'),
]
