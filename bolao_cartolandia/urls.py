from django.contrib import admin
from django.urls import path, include
from core.views import dashboard_view
from accounts import views as accounts_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard_view, name='dashboard'),
    
    # Rotas de Acesso
    path('login/', accounts_views.acesso_usuario, name='login'),
    path('logout/', accounts_views.sair, name='logout'),
    
    # Rotas dos seus aplicativos usando include
    path('bolao/', include('bolao.urls')), # <--- ATUALIZE ESTA LINHA
    path('convocacao/', include('convocacao.urls')),
    path('palpites/', include('palpites.urls')),
    path('pagamentos/', include('pagamentos.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)