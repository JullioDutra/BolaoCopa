from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import RegistroSimplesForm

# 1. IMPORTAMOS OS MODELS DE CARTEIRA E PARTICIPAÇÃO
from accounts.models import Carteira
from django.contrib.auth.decorators import login_required
from palpites.models import Clube
from . import coins
from bolao.models import Participacao

def acesso_usuario(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form_login = AuthenticationForm()
    form_registro = RegistroSimplesForm()
    active_tab = 'login'

    if request.method == 'POST':
        action = request.POST.get('action')
        active_tab = 'registro' if action == 'registro' else 'login'

        if action == 'login':
            form_login = AuthenticationForm(request, data=request.POST)
            if form_login.is_valid():
                user = form_login.get_user()
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "E-mail ou senha incorretos.")

        elif action == 'registro':
            form_registro = RegistroSimplesForm(request.POST)
            if form_registro.is_valid():
                # Salva o usuário básico
                user = form_registro.save()
                
                # 2. MÁGICA AQUI: Cria automaticamente a Carteira e a Participação padrão
                Carteira.objects.get_or_create(usuario=user, defaults={'saldo': 0.00})
                Participacao.objects.get_or_create(usuario=user, defaults={'tipo': 'resenha', 'aprovado': True})
                
                # Faz o login automático
                login(request, user)
                messages.success(request, "Conta criada com sucesso! Bem-vindo(a) à Cartolândia.")
                return redirect('dashboard')
            else:
                messages.error(request, "Erro ao criar conta. Verifique os dados fornecidos.")

    context = {
        'form_login': form_login,
        'form_registro': form_registro,
        'active_tab': active_tab,
    }
    return render(request, 'accounts/login_registro.html', context)

def sair(request):
    logout(request)
    messages.info(request, "Você saiu da sua conta. Até logo!")
    return redirect('login')


RECOMPENSA_ESCOLHER_TIME = 100


@login_required
def escolher_time(request):
    """ Tela onde o usuário escolhe o time do coração (que define o tema do site). """
    perfil = coins.obter_perfil(request.user)

    if request.method == 'POST':
        clube = Clube.objects.filter(pk=request.POST.get('clube')).first()
        perfil.usar_tema_do_time = request.POST.get('usar_tema_do_time', 'on') == 'on'
        primeira_vez = perfil.time_coracao_id is None and clube is not None
        if clube:
            perfil.time_coracao = clube
        perfil.save()
        if primeira_vez:
            coins.creditar(request.user, RECOMPENSA_ESCOLHER_TIME, "❤️ Bônus por escolher o time do coração")
            messages.success(request, f"Time escolhido! +{RECOMPENSA_ESCOLHER_TIME} Cartola Coins pra você.")
        else:
            messages.success(request, "Preferências salvas!")
        return redirect('conta:escolher_time')

    return render(request, 'accounts/escolher_time.html', {
        'clubes': Clube.objects.all().order_by('competicao', 'nome'),
        'recompensa': RECOMPENSA_ESCOLHER_TIME,
        'perfil': perfil,
    })


@login_required
def extrato_coins(request):
    carteira = coins.obter_carteira(request.user)
    return render(request, 'accounts/extrato_coins.html', {
        'carteira': carteira,
        'movimentos': carteira.movimentos.all()[:100],
    })
