from django.contrib import admin
from django.urls import path, include
from core.views import dashboard_view
from accounts import views as accounts_views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard_view, name='dashboard'),
    
    # Rotas de Acesso
    path('login/', accounts_views.acesso_usuario, name='login'),
    path('logout/', accounts_views.sair, name='logout'),
    # Rotas para Reset de Senha (Nativas do Django com templates customizados)
    path('reset-senha/', 
         auth_views.PasswordResetView.as_view(template_name='accounts/reset_senha.html'), 
         name='password_reset'),
    path('reset-senha/enviado/', 
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/reset_senha_enviado.html'), 
         name='password_reset_done'),
    path('reset-senha/confirmar/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/reset_senha_confirmar.html'), 
         name='password_reset_confirm'),
    path('reset-senha/concluido/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/reset_senha_concluido.html'), 
         name='password_reset_complete'),
    
    # Rotas dos seus aplicativos usando include
    path('bolao/', include('bolao.urls')), # <--- ATUALIZE ESTA LINHA
    path('convocacao/', include('convocacao.urls')),
    path('palpites/', include('palpites.urls')),
    path('pagamentos/', include('pagamentos.urls')),
    path('duelos/', include('duelos.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
