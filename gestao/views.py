import io
import os
import secrets

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.management import call_command
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from accounts import coins
from accounts.models import PerfilUsuario
from palpites.models import Clube

from . import auditoria

FILTROS = {
    'ativos': Q(is_active=True), 'inativos': Q(is_active=False), 'staff': Q(is_staff=True),
    'sem-telefone': Q(perfil__telefone='') | Q(perfil__isnull=True),
}


def _nome(u):
    return u.first_name or u.username


@staff_member_required
def hub(request):
    return render(request, 'gestao/hub.html', {
        'total_usuarios': User.objects.count(),
        'inativos': User.objects.filter(is_active=False).count(),
        'ultimas_acoes': auditoria.recentes(5),
    })


@staff_member_required
def usuarios(request):
    busca = (request.GET.get('q') or '').strip()
    filtro = request.GET.get('f') or ''
    qs = User.objects.select_related('perfil').order_by('first_name', 'username')
    if busca:
        qs = qs.filter(Q(first_name__icontains=busca) | Q(last_name__icontains=busca)
                       | Q(username__icontains=busca) | Q(email__icontains=busca))
    if filtro in FILTROS:
        qs = qs.filter(FILTROS[filtro])
    pagina = Paginator(qs, 30).get_page(request.GET.get('p'))
    return render(request, 'gestao/usuarios.html', {
        'pagina': pagina, 'busca': busca, 'filtro': filtro, 'filtros': FILTROS.keys()})


def _link_reset(request, alvo):
    uid = urlsafe_base64_encode(force_bytes(alvo.pk))
    return request.build_absolute_uri(
        reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': default_token_generator.make_token(alvo)}))


@staff_member_required
def usuario(request, pk):
    alvo = get_object_or_404(User, pk=pk)
    perfil = coins.obter_perfil(alvo)
    contexto_extra = {}
    eu = alvo.pk == request.user.pk

    if request.method == 'POST':
        acao = request.POST.get('acao')
        if acao == 'editar':
            alvo.first_name = request.POST.get('first_name', '').strip()[:150]
            alvo.last_name = request.POST.get('last_name', '').strip()[:150]
            alvo.email = request.POST.get('email', '').strip()[:254]
            alvo.save(update_fields=['first_name', 'last_name', 'email'])
            perfil.telefone = ''.join(c for c in request.POST.get('telefone', '') if c.isdigit())[:20]
            perfil.frase = request.POST.get('frase', '').strip()[:80]
            clube = Clube.objects.filter(pk=request.POST.get('time_coracao') or None).first()
            perfil.time_coracao = clube
            perfil.save()
            auditoria.registrar(request, f'editou o cadastro de {_nome(alvo)}', alvo)
            messages.success(request, 'Cadastro atualizado.')
        elif acao == 'link_senha':
            contexto_extra['link'] = _link_reset(request, alvo)
            auditoria.registrar(request, f'gerou link de senha para {_nome(alvo)}', alvo)
        elif acao == 'senha_temporaria':
            if not request.user.is_superuser:
                messages.error(request, 'Só superusuário define senha temporária.')
            else:
                senha = secrets.token_urlsafe(6)
                alvo.set_password(senha)
                alvo.save(update_fields=['password'])
                contexto_extra['senha_temporaria'] = senha
                auditoria.registrar(request, f'definiu senha temporária para {_nome(alvo)}', alvo)
        elif acao in ('ativar', 'desativar'):
            if eu:
                messages.error(request, 'Você não pode desativar a si mesmo.')
            else:
                alvo.is_active = acao == 'ativar'
                alvo.save(update_fields=['is_active'])
                auditoria.registrar(request, f"{'ativou' if alvo.is_active else 'desativou'} {_nome(alvo)}", alvo)
                messages.success(request, 'Conta ativada.' if alvo.is_active else 'Conta desativada.')
        elif acao == 'alternar_staff':
            if not request.user.is_superuser or eu:
                messages.error(request, 'Só outro superusuário pode alterar a equipe (e não em si mesmo).')
            else:
                alvo.is_staff = not alvo.is_staff
                alvo.save(update_fields=['is_staff'])
                auditoria.registrar(request, f"{'promoveu' if alvo.is_staff else 'removeu da staff'} {_nome(alvo)}", alvo)
                messages.success(request, 'Permissão de staff atualizada.')
        elif acao == 'coins':
            motivo = request.POST.get('motivo', '').strip()
            try:
                valor = int(request.POST.get('valor', '0'))
            except ValueError:
                valor = 0
            if not motivo or valor == 0:
                messages.error(request, 'Informe um valor diferente de zero e o motivo.')
            else:
                try:
                    if valor > 0:
                        coins.creditar(alvo, valor, f'🛠️ Ajuste da staff: {motivo}')
                    else:
                        coins.debitar(alvo, -valor, f'🛠️ Ajuste da staff: {motivo}')
                    auditoria.registrar(request, f'ajustou {valor:+d} coins de {_nome(alvo)} ({motivo})', alvo)
                    messages.success(request, f'Ajuste de {valor:+d} coins aplicado.')
                except coins.SaldoInsuficiente as e:
                    messages.error(request, str(e))
        elif acao == 'resetar_streak':
            perfil.streak_dias = 0
            perfil.save(update_fields=['streak_dias'])
            auditoria.registrar(request, f'zerou a sequência de {_nome(alvo)}', alvo)
            messages.success(request, 'Sequência zerada.')
        elif acao == 'limpar_pergunta':
            perfil.pergunta_secreta = ''
            perfil.resposta_secreta_hash = ''
            perfil.save(update_fields=['pergunta_secreta', 'resposta_secreta_hash'])
            auditoria.registrar(request, f'limpou a pergunta secreta de {_nome(alvo)}', alvo)
            messages.success(request, 'Pergunta secreta removida.')
        if 'link' not in contexto_extra and 'senha_temporaria' not in contexto_extra:
            return redirect('gestao:usuario', pk=alvo.pk)

    carteira = coins.obter_carteira(alvo)
    contexto = {
        'alvo': alvo, 'perfil': perfil, 'carteira': carteira, 'eu': eu,
        'movimentos': carteira.movimentos.order_by('-data')[:8],
        'clubes': Clube.objects.order_by('nome'),
    }
    contexto.update(contexto_extra)
    return render(request, 'gestao/usuario.html', contexto)


@staff_member_required
def auditoria_view(request):
    return render(request, 'gestao/auditoria.html', {'acoes': auditoria.recentes(150)})


def _tamanho_pasta(caminho):
    total = 0
    for raiz, _, arquivos in os.walk(caminho):
        for a in arquivos:
            try:
                total += os.path.getsize(os.path.join(raiz, a))
            except OSError:
                pass
    return total


def _integracoes():
    def ok(nome):
        return bool(getattr(settings, nome, None) or os.environ.get(nome))
    return [
        ('football-data.org (jogos/classificação)', ok('FOOTBALL_DATA_TOKEN')),
        ('API-Football (elencos/estatísticas)', ok('APIFOOTBALL_KEY')),
        ('Notificações push (VAPID)', ok('VAPID_PUBLIC_KEY') and ok('VAPID_PRIVATE_KEY')),
        ('Gemini (modo carreira com IA)', ok('GEMINI_API_KEY')),
        ('Token do agendador (SYNC_SECRET_TOKEN)', ok('SYNC_SECRET_TOKEN')),
        ('Grupo do WhatsApp (WHATSAPP_GRUPO_URL)', ok('WHATSAPP_GRUPO_URL')),
    ]


@staff_member_required
def sistema(request):
    saida = None
    if request.method == 'POST':
        acao = request.POST.get('acao')
        buffer = io.StringIO()
        try:
            if acao == 'sincronizar':
                call_command('sincronizar_jogos', stdout=buffer)
            elif acao == 'escudos':
                call_command('consolidar_escudos', '--aplicar', stdout=buffer)
            elif acao == 'jogadores':
                call_command('consolidar_jogadores', '--aplicar', stdout=buffer)
            elif acao == 'baralho':
                from duelos.baralho import garantir_cartas
                buffer.write(f'{garantir_cartas(40)} cartas criadas.')
            else:
                acao = None
            if acao:
                auditoria.registrar(request, f'rodou a tarefa "{acao}" no painel Sistema')
                messages.success(request, 'Tarefa concluída.')
        except Exception as e:  # mostra o erro para a staff em vez de 500
            buffer.write(f'Erro: {e}')
            messages.error(request, 'A tarefa falhou — veja os detalhes abaixo.')
        saida = buffer.getvalue()

    from duelos.models import CartaTrunfo
    from futebol.models import Atleta, Escudo, Time
    from palpites.models import Jogo
    media = getattr(settings, 'MEDIA_ROOT', None)
    return render(request, 'gestao/sistema.html', {
        'integracoes': _integracoes(), 'saida': saida,
        'contagens': [('Usuários', User.objects.count()), ('Jogos do bolão', Jogo.objects.count()),
                      ('Times (banco de futebol)', Time.objects.count()), ('Atletas (banco único)', Atleta.objects.count()),
                      ('Escudos no catálogo global', Escudo.objects.count()), ('Cartas do Super Trunfo', CartaTrunfo.objects.count())],
        'media_mb': round(_tamanho_pasta(media) / 1048576, 1) if media and os.path.isdir(media) else 0,
    })
