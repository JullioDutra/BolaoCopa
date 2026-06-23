import json
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Avatar, Clube, EscalacaoPosicao
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.dateformat import format
from .models import PartidaMundo
from django.conf import settings
from django.utils import timezone
import logging
from .services import (
    escalar_time_titular, 
    encerrar_partida_e_processar_stats,
    executar_virada_de_temporada,
    criar_avatar_peneira,
    processar_treino,
    checar_gatilho_dilema,
    gerar_dilema_ia,
    resolver_dilema,
    processar_tique_partida,
    resolver_acao_jogador
)



@login_required
def tela_peneira(request):
    """ Renderiza a tela de criação do Avatar """
    # Se já tem avatar, redireciona pro Dashboard (faremos o dashboard depois)
    if hasattr(request.user, 'avatar_carreira'):
        pass # return redirect('carreira:dashboard')
        
    return render(request, 'carreira/criar_carreira.html')

@login_required
def api_assinar_contrato(request):
    """ Endpoint que processa o formulário de criação e devolve o clube sorteado """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nome_camisa = data.get('nome')
            arquetipo = data.get('arquetipo')

            # Cria o Avatar usando a regra de negócios
            avatar = criar_avatar_peneira(request.user, nome_camisa, arquetipo)

            return JsonResponse({
                'sucesso': True,
                'clube_nome': avatar.clube_atual.nome if avatar.clube_atual else 'Sem Clube',
                'ovr_calculado': avatar.ovr_calculado,
                'posicao': avatar.get_arquetipo_display()
            })
        except Exception as e:
            return JsonResponse({'sucesso': False, 'mensagem': str(e)})
            
    return JsonResponse({'sucesso': False, 'mensagem': 'Método inválido'})




@login_required
def dashboard_carreira(request):
    """ Renderiza o Hub Principal do Jogador """
    try:
        avatar = request.user.avatar_carreira
    except Avatar.DoesNotExist:
        return redirect('carreira:tela_peneira')

    contexto = {
        'avatar': avatar,
        'clube': avatar.clube_atual,
    }
    return render(request, 'carreira/dashboard.html', contexto)

@login_required
def api_treinar(request):
    """ Endpoint AJAX para executar a ação de treino diário """
    if request.method == 'POST':
        try:
            avatar = request.user.avatar_carreira
            data = json.loads(request.body)
            tipo_treino = data.get('tipo')

            resultado = processar_treino(avatar, tipo_treino)

            return JsonResponse({
                'sucesso': True,
                'mensagem': 'Treino executado com sucesso!',
                'dados': resultado
            })
        except Exception as e:
            return JsonResponse({'sucesso': False, 'mensagem': str(e)})

    return JsonResponse({'sucesso': False, 'mensagem': 'Método inválido.'})


@login_required
def api_treinar(request):
    """ Endpoint AJAX para executar a ação de treino diário """
    if request.method == 'POST':
        try:
            avatar = request.user.avatar_carreira
            data = json.loads(request.body)
            tipo_treino = data.get('tipo')

            resultado = processar_treino(avatar, tipo_treino)
            
            # CHANCE DE GERAR DILEMA APÓS O TREINO
            dilema = None
            if checar_gatilho_dilema():
                dilema = gerar_dilema_ia(avatar)
                # Salva o dilema temporariamente na sessão para validar depois
                request.session['dilema_atual'] = dilema

            return JsonResponse({
                'sucesso': True,
                'mensagem': 'Treino executado com sucesso!',
                'dados': resultado,
                'tem_dilema': dilema is not None,
                'dilema_dados': dilema
            })
        except Exception as e:
            return JsonResponse({'sucesso': False, 'mensagem': str(e)})

    return JsonResponse({'sucesso': False, 'mensagem': 'Método inválido.'})

@login_required
def api_resolver_dilema(request):
    """ Endpoint que recebe a escolha (A ou B) do dilema """
    if request.method == 'POST':
        try:
            avatar = request.user.avatar_carreira
            data = json.loads(request.body)
            escolha = data.get('escolha') # 'opcao_A' ou 'opcao_B'
            
            dilema = request.session.get('dilema_atual')
            if not dilema:
                return JsonResponse({'sucesso': False, 'mensagem': 'Nenhum dilema ativo.'})
                
            opcao_dict = dilema[escolha]
            resolver_dilema(avatar, opcao_dict)
            
            # Limpa a sessão
            del request.session['dilema_atual']
            
            return JsonResponse({'sucesso': True, 'mensagem': 'Decisão tomada e consequências aplicadas!'})
            
        except Exception as e:
            return JsonResponse({'sucesso': False, 'mensagem': str(e)})
            
    return JsonResponse({'sucesso': False, 'mensagem': 'Método inválido.'})


@login_required
def tela_vestiario(request):
    """ Renderiza a tela da prancheta tática e elenco do clube """
    try:
        avatar = request.user.avatar_carreira
    except Avatar.DoesNotExist:
        return redirect('carreira:tela_peneira')

    clube = avatar.clube_atual
    if not clube:
        return redirect('carreira:dashboard')

    # Busca a escalação atual do clube
    escalacao = EscalacaoPosicao.objects.filter(clube=clube)
    
    # Se não houver escalação, o treinador IA faz uma na hora (Gatilho automático)
    if not escalacao.exists():
        from .services import escalar_time_titular
        escalar_time_titular(clube)
        escalacao = EscalacaoPosicao.objects.filter(clube=clube)

    contexto = {
        'avatar': avatar,
        'clube': clube,
        'escalacao': escalacao
    }
    return render(request, 'carreira/vestiario.html', contexto)




@login_required
def tela_match_day(request, partida_id):
    """ Renderiza o layout principal do estádio """
    partida = get_object_or_404(PartidaMundo, id=partida_id)
    return render(request, 'carreira/match_day.html', {'partida': partida})

@login_required
def api_sync_partida(request, partida_id):
    """ Endpoint chamado via AJAX a cada 2 segundos """
    partida = get_object_or_404(PartidaMundo, id=partida_id)
    avatar = getattr(request.user, 'avatar_carreira', None)
    
    # Só processa a engine se a partida estiver em andamento
    if partida.status == 'andamento':
        processar_tique_partida(partida)
        partida.refresh_from_db()
        
    # Verifica se é a vez de quem está chamando a API
    minha_vez = False
    segundos_restantes = 0
    opcoes = None
    
    if partida.jogador_esperado == avatar and partida.vencimento_lance:
        minha_vez = True
        opcoes = partida.opcoes_lance
        diferenca = partida.vencimento_lance - timezone.now()
        segundos_restantes = int(diferenca.total_seconds())
        if segundos_restantes < 0: segundos_restantes = 0

    return JsonResponse({
        'status': partida.status,
        'minuto': partida.minuto_atual,
        'placar_casa': partida.gols_casa,
        'placar_fora': partida.gols_fora,
        'log': partida.log_narracao,
        'minha_vez': minha_vez,
        'opcoes': opcoes,
        'segundos_restantes': segundos_restantes
    })

@login_required
def api_acao_lance(request, partida_id):
    """ Endpoint que recebe o clique do botão do jogador """
    if request.method == 'POST':
        partida = get_object_or_404(PartidaMundo, id=partida_id)
        avatar = getattr(request.user, 'avatar_carreira', None)
        
        # Valida se realmente era a vez dele e se o tempo não esgotou
        if partida.jogador_esperado == avatar and partida.vencimento_lance and timezone.now() <= partida.vencimento_lance:
            data = json.loads(request.body)
            escolha = data.get('escolha')
            
            resolver_acao_jogador(partida, avatar, escolha)
            return JsonResponse({'sucesso': True})
            
        return JsonResponse({'sucesso': False, 'mensagem': 'Tempo esgotado ou ação inválida.'})


logger = logging.getLogger(__name__)

def api_cron_engine(request, token):
    """
    Webhook seguro para ser chamado por um serviço externo (ex: cron-job.org).
    Gere todas as automações do jogo baseado na hora do dia.
    """
    if token != settings.CRON_SECRET_TOKEN:
        return JsonResponse({'sucesso': False, 'mensagem': 'Acesso não autorizado.'}, status=403)

    agora = timezone.now()
    acoes_realizadas = []

    try:
        # ==========================================
        # ROTINA 1: RESET DIÁRIO (Meia-noite)
        # ==========================================
        if agora.hour == 0 and agora.minute < 10: 
            Avatar.objects.update(pontos_acao_diarios=1)
            acoes_realizadas.append("Reset Diário de AP concluído.")

        # ==========================================
        # ROTINA 2: IA DO TREINADOR (Pré-Jogo às 19h)
        # ==========================================
        if agora.hour == 19:
            clubes = Clube.objects.all()
            for clube in clubes:
                escalar_time_titular(clube)
            acoes_realizadas.append("IA de Escalação executada para todos os clubes.")

        # ==========================================
        # ROTINA 2.5: O APITO INICIAL (Começa os jogos às 20h)
        # ==========================================
        if agora.hour == 20:
            # Pega todos os jogos que foram agendados mas ainda não começaram
            partidas = PartidaMundo.objects.filter(status='agendada')
            
            contagem = 0
            for partida in partidas:
                partida.status = 'andamento'
                # Insere a primeira linha na tela do Match Day
                partida.adicionar_log("BOLA ROLANDO! O árbitro autoriza o início da partida no metaverso.", destaque=True)
                partida.save()
                contagem += 1
                
            if contagem > 0:
                acoes_realizadas.append(f"{contagem} partidas iniciadas com sucesso (Apito Inicial).")

        # ==========================================
        # ROTINA 3: APITO FINAL E CONSEQUÊNCIAS (Pós-Jogo às 21h)
        # ==========================================
        if agora.hour == 21:
            partidas_pendentes = PartidaMundo.objects.filter(status='andamento', minuto_atual__gte=90)
            for partida in partidas_pendentes:
                partida.status = 'finalizada'
                partida.save()
                encerrar_partida_e_processar_stats(partida)
            acoes_realizadas.append(f"{partidas_pendentes.count()} partidas encerradas. XP e lesões calculados.")

        return JsonResponse({
            'sucesso': True, 
            'hora_servidor': agora.isoformat(),
            'acoes': acoes_realizadas if acoes_realizadas else ["Nenhuma ação agendada para esta hora."]
        })

    except Exception as e:
        logger.error(f"Erro no Cron Engine: {e}")
        return JsonResponse({'sucesso': False, 'erro': str(e)}, status=500)
