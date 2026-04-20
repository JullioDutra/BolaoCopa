from django.shortcuts import render
from bolao.decorators import acesso_liberado_required
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from palpites.models import Jogo
from django.utils import timezone

@acesso_liberado_required
def dashboard_view(request):
    """
    Tela principal. O usuário só chega aqui se estiver logado 
    e com a participação (resenha ou pix) devidamente aprovada.
    """

    proximo_jogo = Jogo.objects.filter(data_hora__gt=timezone.now()).order_by('data_hora').first()

    context = {
        'participacao': request.user.participacao,
        'proximo_jogo': proximo_jogo,
    }
    return render(request, 'core/dashboard.html', context)