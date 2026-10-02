from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from . import avatares
from .forms import (PerfilForm, PerguntaSecretaForm, RecuperarSenhaForm, RegistroSimplesForm)

# 1. IMPORTAMOS OS MODELS DE CARTEIRA E PARTICIPAÇÃO
from accounts.models import Carteira
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from . import dados, recuperacao
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
                if form_registro.cleaned_data.get('whatsapp'):
                    perfil = coins.obter_perfil(user)
                    perfil.telefone = form_registro.cleaned_data['whatsapp']
                    perfil.save(update_fields=['telefone'])
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
            from avisos import conquistas
            conquistas.checar(request.user)
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



BONUS_PERFIL_COMPLETO = 50


@login_required
def perfil(request):
    """ Perfil do participante: dados, segurança (senha + pergunta secreta) e preferências. """
    usuario = request.user
    perfil = coins.obter_perfil(usuario)
    aba = request.GET.get('aba', 'dados')

    form_dados = PerfilForm(initial={
        'nome': usuario.first_name, 'email': usuario.email or usuario.username,
        'telefone': dados.telefone_formatado(perfil.telefone), 'frase': perfil.frase,
        'avatar': avatares.normalizar(perfil.avatar),
        'avisos_whatsapp': perfil.avisos_whatsapp,
    }, usuario=usuario)
    form_senha = PasswordChangeForm(usuario)
    for campo in form_senha.fields.values():
        campo.widget.attrs['class'] = 'form-control form-control-lg'
    form_pergunta = PerguntaSecretaForm(initial={'pergunta': perfil.pergunta_secreta or 'craque'})

    if request.method == 'POST':
        acao = request.POST.get('acao')
        if acao == 'dados':
            aba = 'dados'
            form_dados = PerfilForm(request.POST, usuario=usuario)
            if form_dados.is_valid():
                d = form_dados.cleaned_data
                if usuario.username.lower() == (usuario.email or '').lower() or usuario.username == usuario.email:
                    usuario.username = d['email']          # o login é o e-mail
                usuario.first_name = d['nome']
                usuario.email = d['email']
                usuario.save()
                perfil.telefone, perfil.frase, perfil.avatar = d['telefone'], d['frase'], d['avatar']
                perfil.avisos_whatsapp = d['avisos_whatsapp']
                perfil.save()
                _bonus_perfil(request, perfil)
                messages.success(request, "Perfil atualizado!")
                return redirect(f"{reverse('conta:perfil')}?aba=dados")
        elif acao == 'senha':
            aba = 'seguranca'
            form_senha = PasswordChangeForm(usuario, request.POST)
            for campo in form_senha.fields.values():
                campo.widget.attrs['class'] = 'form-control form-control-lg'
            if form_senha.is_valid():
                usuario = form_senha.save()
                update_session_auth_hash(request, usuario)
                messages.success(request, "Senha alterada com sucesso!")
                return redirect(f"{reverse('conta:perfil')}?aba=seguranca")
        elif acao == 'pergunta':
            aba = 'seguranca'
            form_pergunta = PerguntaSecretaForm(request.POST)
            if form_pergunta.is_valid():
                perfil.pergunta_secreta = form_pergunta.cleaned_data['pergunta']
                perfil.resposta_secreta_hash = dados.hash_resposta(form_pergunta.cleaned_data['resposta'])
                perfil.save()
                _bonus_perfil(request, perfil)
                messages.success(request, "Pergunta secreta salva. Ela ajuda a recuperar sua senha.")
                return redirect(f"{reverse('conta:perfil')}?aba=seguranca")

    from avisos import conquistas
    from palpites.models import Palpite
    conquistas.checar(usuario)
    palpites = Palpite.objects.filter(usuario=usuario)
    return render(request, 'accounts/perfil.html', {
        'conquistas': conquistas.do_usuario(usuario),
        'perfil': perfil, 'aba': aba,
        'form_dados': form_dados, 'form_senha': form_senha, 'form_pergunta': form_pergunta,
        'avatares': avatares.do_usuario(usuario),
        'bonus_perfil': BONUS_PERFIL_COMPLETO,
        'saldo_coins': coins.saldo(usuario),
        'total_palpites': palpites.count(),
        'cravadas': palpites.filter(pontuacao_obtida=15).count(),
        'acertos': palpites.filter(pontuacao_obtida__gt=0).count(),
    })


def _bonus_perfil(request, perfil):
    from avisos import conquistas
    conquistas.checar(request.user)
    if perfil.perfil_completo and not perfil.bonus_perfil_pago:
        perfil.bonus_perfil_pago = True
        perfil.save(update_fields=['bonus_perfil_pago'])
        coins.creditar(request.user, BONUS_PERFIL_COMPLETO, "🧾 Bônus por completar o perfil")
        messages.success(request, f"Perfil completo! +{BONUS_PERFIL_COMPLETO} Cartola Coins pra você.")


def _ip(request):
    return request.META.get('REMOTE_ADDR')


def recuperar_senha(request):
    """ Esqueci a senha: prova de identidade com WhatsApp ou pergunta secreta. """
    if request.user.is_authenticated:
        return redirect('conta:perfil')
    form = RecuperarSenhaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        d = form.cleaned_data
        if not d['telefone'] and not (d['pergunta'] and d['resposta']):
            messages.error(request, "Informe o WhatsApp cadastrado ou responda a pergunta secreta.")
        else:
            try:
                usuario = recuperacao.verificar(d['email'], d['telefone'], d['pergunta'], d['resposta'], ip=_ip(request))
            except recuperacao.Bloqueado as erro:
                messages.error(request, str(erro))
            else:
                if usuario:
                    return redirect('conta:nova_senha', token=recuperacao.gerar_token(usuario))
                messages.error(request, "Os dados não conferem. Confira o e-mail e tente de novo, ou peça um link à staff.")
    return render(request, 'accounts/recuperar.html', {'form': form})


def nova_senha(request, token):
    usuario = recuperacao.usuario_do_token(token)
    if usuario is None:
        messages.error(request, "Esse link expirou ou já foi usado. Refaça a verificação.")
        return redirect('conta:recuperar')
    form = SetPasswordForm(usuario, request.POST or None)
    for campo in form.fields.values():
        campo.widget.attrs['class'] = 'form-control form-control-lg'
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Senha nova salva! Agora é só entrar.")
        return redirect('login')
    return render(request, 'accounts/nova_senha.html', {'form': form, 'usuario': usuario})


@staff_member_required
def staff_links_senha(request):
    """ A staff gera um link de redefinição (valido por 3 dias) e manda pelo WhatsApp. """
    link = alvo = None
    if request.method == 'POST':
        alvo = User.objects.filter(pk=request.POST.get('usuario')).first()
        if alvo:
            uid = urlsafe_base64_encode(force_bytes(alvo.pk))
            link = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': default_token_generator.make_token(alvo)}))
    busca = (request.GET.get('q') or '').strip()
    usuarios = User.objects.filter(is_active=True).order_by('first_name', 'username')
    if busca:
        usuarios = usuarios.filter(first_name__icontains=busca) | usuarios.filter(username__icontains=busca)
    telefone = ''
    if alvo:
        from .models import PerfilUsuario
        p = PerfilUsuario.objects.filter(usuario=alvo).first()
        telefone = p.telefone if p else ''
    return render(request, 'accounts/staff_links.html', {
        'usuarios': usuarios[:40], 'link': link, 'alvo': alvo, 'busca': busca, 'telefone': telefone,
    })



@login_required
def perfil_publico(request, pk):
    """ Perfil que os outros participantes enxergam: avatar, frase, time, números e conquistas (sem dados de contato). """
    from avisos import conquistas
    from palpites.models import Palpite
    from . import npc
    alvo = get_object_or_404(User, pk=pk, is_active=True)
    if npc.eh_npc(alvo):
        raise Http404
    perfil = coins.obter_perfil(alvo)
    lista = conquistas.do_usuario(alvo)
    palpites = Palpite.objects.filter(usuario=alvo)
    try:
        from setezero.models import DraftCopa7a0
        drafts = DraftCopa7a0.objects.filter(usuario=alvo, status='campeao')
        copas = {'brasil': drafts.filter(torneio='brasil').count(), 'mundial': drafts.filter(torneio='mundial').count(),
                 'invictos': drafts.filter(invicto=True).count()}
    except Exception:
        copas = {'brasil': 0, 'mundial': 0, 'invictos': 0}
    return render(request, 'accounts/perfil_publico.html', {
        'alvo': alvo, 'perfil': perfil, 'nome': alvo.first_name or alvo.username.split('@')[0], 'conquistas': lista,
        'ganhas': sum(1 for c in lista if c['ganha']), 'total_conquistas': len(lista), 'copas': copas,
        'palpites': palpites.count(), 'cravadas': palpites.filter(pontuacao_obtida=15).count(),
        'acertos': palpites.filter(pontuacao_obtida__gt=0).count(), 'eu': alvo.pk == request.user.pk,
    })
