import json
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from django.db.models import Q

# Importação dos Modelos
from .models import (
    Avatar, Clube, ServidorConfig, PartidaMundo, EscalacaoPosicao, 
    PropostaJanela, ConflitoVestiario, RegistroHistoricoCampeao, 
    ConvocacaoSelecao, NoticiaJornal
)

# Importação dos Serviços (A Regra de Negócio)
from .services import (
    criar_avatar_peneira,
    processar_treino, checar_gatilho_dilema, gerar_dilema_ia, resolver_dilema,
    escalar_time_titular, processar_tique_partida, resolver_acao_jogador, encerrar_partida_e_processar_stats,
    calcular_valor_passe, gerar_propostas_mercado, processar_resposta_proposta,
    fazer_as_pazes, executar_virada_de_temporada,
    gerar_frases_narracao_ia, gerar_noticia_jornal_ia, gerar_calendario_liga
)

logger = logging.getLogger(__name__)

# ==========================================
# 1. CRIAÇÃO E PENEIRA
# ==========================================

@login_required
def tela_peneira(request):
    """ Renderiza a tela de criação do Avatar """
    if hasattr(request.user, 'avatar_carreira'):
        return redirect('modocarreira:dashboard')
        
    return render(request, 'carreira/criar_carreira.html')

@login_required
def api_assinar_contrato(request):
    """ Endpoint que processa o formulário de criação e devolve o clube sorteado """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nome_camisa = data.get('nome')
            arquetipo = data.get('arquetipo')

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


# ==========================================
# 2. DASHBOARD E ROTINA DE TREINOS
# ==========================================

@login_required
def dashboard_carreira(request):
    """ Renderiza o Hub Principal do Jogador """
    try:
        avatar = request.user.avatar_carreira
    except Avatar.DoesNotExist:
        return redirect('modocarreira:tela_peneira')

    clube = avatar.clube_atual
    proxima_partida = None
    
    if clube:
        # Busca o próximo jogo do clube do jogador (que ainda não acabou)
        proxima_partida = PartidaMundo.objects.filter(
            Q(clube_casa=clube) | Q(clube_fora=clube),
            status__in=['agendada', 'andamento']
        ).order_by('id').first()

    contexto = {
        'avatar': avatar,
        'clube': clube,
        'proxima_partida': proxima_partida,
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
            
            # CHANCE DE GERAR DILEMA APÓS O TREINO
            dilema = None
            if checar_gatilho_dilema():
                dilema = gerar_dilema_ia(avatar)
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
    """ Endpoint que recebe a escolha (A ou B) do dilema gerado pela IA """
    if request.method == 'POST':
        try:
            avatar = request.user.avatar_carreira
            data = json.loads(request.body)
            escolha = data.get('escolha')

            dilema = request.session.get('dilema_atual')
            if not dilema:
                return JsonResponse({'sucesso': False, 'mensagem': 'Nenhum dilema ativo.'})

            # Aceita tanto "A"/"B" quanto "opcao_A"/"opcao_B" vindos do front-end
            chave = escolha if escolha in dilema else f'opcao_{escolha}'
            if chave not in dilema:
                return JsonResponse({'sucesso': False, 'mensagem': f'Escolha inválida: {escolha}'})

            opcao_dict = dilema[chave]
            resolver_dilema(avatar, opcao_dict)

            del request.session['dilema_atual']
            return JsonResponse({'sucesso': True, 'mensagem': 'Decisão tomada e consequências aplicadas!'})

        except Exception as e:
            return JsonResponse({'sucesso': False, 'mensagem': str(e)})

    return JsonResponse({'sucesso': False, 'mensagem': 'Método inválido.'})


# ==========================================
# 3. VESTIÁRIO E PARTIDAS (MATCH DAY)
# ==========================================

@login_required
def tela_vestiario(request):
    """ Renderiza a prancheta tática e o elenco do clube """
    try:
        avatar = request.user.avatar_carreira
    except Avatar.DoesNotExist:
        return redirect('modocarreira:tela_peneira')

    clube = avatar.clube_atual
    if not clube:
        return redirect('modocarreira:dashboard')

    escalacao = EscalacaoPosicao.objects.filter(clube=clube)
    
    if not escalacao.exists():
        escalar_time_titular(clube)
        escalacao = EscalacaoPosicao.objects.filter(clube=clube)

    contexto = { 'avatar': avatar, 'clube': clube, 'escalacao': escalacao }
    return render(request, 'carreira/vestiario.html', contexto)

@login_required
def tela_match_day(request, partida_id):
    partida = get_object_or_404(PartidaMundo, id=partida_id)
    return render(request, 'carreira/match_day.html', {'partida': partida})

@login_required
def api_sync_partida(request, partida_id):
    """ Endpoint chamado via AJAX a cada 2 segundos no ecrã do jogo """
    partida = get_object_or_404(PartidaMundo, id=partida_id)
    avatar = getattr(request.user, 'avatar_carreira', None)
    
    if partida.status == 'andamento':
        processar_tique_partida(partida)
        partida.refresh_from_db()
        
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
    """ Recebe a decisão de chute/passe do jogador """
    if request.method == 'POST':
        partida = get_object_or_404(PartidaMundo, id=partida_id)
        avatar = getattr(request.user, 'avatar_carreira', None)
        
        if partida.jogador_esperado == avatar and partida.vencimento_lance and timezone.now() <= partida.vencimento_lance:
            data = json.loads(request.body)
            escolha = data.get('escolha')
            
            resolver_acao_jogador(partida, avatar, escolha)
            return JsonResponse({'sucesso': True})
            
        return JsonResponse({'sucesso': False, 'mensagem': 'Tempo esgotado ou ação inválida.'})

@login_required
def tela_resumo_partida(request, partida_id):
    partida = get_object_or_404(PartidaMundo, id=partida_id)
    avatar = getattr(request.user, 'avatar_carreira', None)
    
    if partida.status != 'finalizada':
        return redirect('modocarreira:tela_match_day', partida_id=partida.id)
        
    return render(request, 'carreira/resumo_partida.html', {'partida': partida, 'avatar': avatar})


# ==========================================
# 4. MERCADO E TRANSFERÊNCIAS
# ==========================================

@login_required
def tela_mercado(request):
    avatar = getattr(request.user, 'avatar_carreira', None)
    if not avatar: return redirect('modocarreira:tela_peneira')

    valor_mercado = calcular_valor_passe(avatar)
    propostas = PropostaJanela.objects.filter(avatar=avatar, status='analise')
    
    if request.method == 'POST' and 'buscar_ofertas' in request.POST:
        gerar_propostas_mercado(avatar)
        return redirect('modocarreira:tela_mercado')

    contexto = { 'avatar': avatar, 'valor_mercado': valor_mercado, 'propostas': propostas }
    return render(request, 'carreira/mercado.html', contexto)

@login_required
def api_responder_proposta(request, proposta_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        acao = data.get('acao')
        avatar = getattr(request.user, 'avatar_carreira', None)
        processar_resposta_proposta(proposta_id, avatar, acao)
        return JsonResponse({'sucesso': True})


# ==========================================
# 5. SOCIAL (VESTIÁRIO E TRETAS) E MUSEU
# ==========================================

@login_required
def tela_social(request):
    avatar = getattr(request.user, 'avatar_carreira', None)
    if not avatar or not avatar.clube_atual:
        return redirect('modocarreira:dashboard')

    colegas = Avatar.objects.filter(clube_atual=avatar.clube_atual).exclude(id=avatar.id)
    conflitos = ConflitoVestiario.objects.filter(Q(atleta_ofensor=avatar) | Q(atleta_ofendido=avatar), ativo=True)

    contexto = { 'avatar': avatar, 'colegas': colegas, 'conflitos': conflitos }
    return render(request, 'carreira/social.html', contexto)

@login_required
def api_fazer_pazes(request, conflito_id):
    if request.method == 'POST':
        try:
            avatar = getattr(request.user, 'avatar_carreira', None)
            fazer_as_pazes(avatar, conflito_id)
            return JsonResponse({'sucesso': True, 'mensagem': 'As pazes foram feitas. Entrosamento restaurado.'})
        except Exception as e:
            return JsonResponse({'sucesso': False, 'mensagem': str(e)})
    return JsonResponse({'sucesso': False})

@login_required
def tela_museu(request):
    temporadas = RegistroHistoricoCampeao.objects.values_list('temporada', flat=True).distinct().order_by('-temporada')
    temp_selecionada = request.GET.get('temporada')
    if not temp_selecionada and temporadas.exists():
        temp_selecionada = temporadas.first()
        
    registros = RegistroHistoricoCampeao.objects.filter(temporada=temp_selecionada)
    
    selecao_snapshot = []
    if registros.exists():
        registro_a = registros.filter(campeonato_nome__contains='Série A').first()
        if registro_a and registro_a.snapshot_elenco_selecao:
            try:
                dados_json = json.loads(registro_a.snapshot_elenco_selecao)
                selecao_snapshot = dados_json.get('selecao', [])
            except:
                pass

    contexto = {
        'temporadas_disponiveis': temporadas,
        'temp_selecionada': int(temp_selecionada) if temp_selecionada else None,
        'registros': registros,
        'selecao': selecao_snapshot
    }
    return render(request, 'carreira/museu.html', contexto)


# ==========================================
# 6. ENGINE DO SERVIDOR (CRONJOB)
# ==========================================

def api_cron_engine(request, token):
    """
    Webhook seguro para ser chamado pelo cron-job.org.
    Executa Automações e Inteligência Artificial.
    """
    if token != getattr(settings, 'CRON_SECRET_TOKEN', 'uma-chave-muito-secreta-cartolandia-2026'):
        return JsonResponse({'sucesso': False, 'mensagem': 'Acesso não autorizado.'}, status=403)

    agora = timezone.now()
    acoes_realizadas = []

    try:
        # ROTINA 1: RESET DIÁRIO DE ENERGIA (Meia-noite)
        if agora.hour == 0 and agora.minute < 10: 
            Avatar.objects.update(pontos_acao_diarios=1)
            acoes_realizadas.append("Reset Diário de AP concluído.")

        # ROTINA 2: IA DO TREINADOR (19h)
        if agora.hour == 19:
            clubes = Clube.objects.all()
            for clube in clubes:
                escalar_time_titular(clube)
            acoes_realizadas.append("IA de Escalação executada para todos os clubes.")

        # ROTINA 2.5: APITO INICIAL (20h)
        if agora.hour == 20:
            partidas = PartidaMundo.objects.filter(status='agendada')
            contagem = 0
            for partida in partidas:
                partida.status = 'andamento'
                
                # Chama a IA para gerar as frases únicas do jogo
                partida.frases_narracao_ia = gerar_frases_narracao_ia(partida.clube_casa.nome, partida.clube_fora.nome)
                partida.adicionar_log("BOLA ROLANDO! O árbitro autoriza o início da partida no metaverso.", destaque=True)
                partida.save()
                contagem += 1
                
            if contagem > 0:
                acoes_realizadas.append(f"{contagem} partidas iniciadas com narração de IA.")

        # ROTINA 3: APITO FINAL, CONSEQUÊNCIAS E JORNAL O CARTOLEIRO (21h)
        if agora.hour == 21:
            partidas_pendentes = PartidaMundo.objects.filter(status='andamento', minuto_atual__gte=90)
            
            for partida in partidas_pendentes:
                partida.status = 'finalizada'
                partida.save()
                encerrar_partida_e_processar_stats(partida) # Paga salários, lesões IA, tretas IA
                
            if partidas_pendentes.exists():
                acoes_realizadas.append(f"{partidas_pendentes.count()} partidas encerradas. Salários pagos.")
            
            # Geração da Notícia do Dia (IA Jornalista)
            if partidas_pendentes.exists():
                jogo_destaque = partidas_pendentes.order_by('-gols_casa').first()
                noticia = gerar_noticia_jornal_ia(
                    jogo_destaque.clube_casa.nome, jogo_destaque.gols_casa,
                    jogo_destaque.clube_fora.nome, jogo_destaque.gols_fora
                )
                
                config = ServidorConfig.objects.first()
                NoticiaJornal.objects.create(
                    temporada=config.temporada_atual if config else 1,
                    manchete=noticia['manchete'],
                    corpo_texto=noticia['corpo']
                )
                acoes_realizadas.append("Notícia do Jornal gerada pela IA.")

        # ==============================================================
        # ROTINA 4: INÍCIO DO MUNDO E VIRADA DE TEMPORADA (23h)
        # ==============================================================
        if agora.hour == 23:
            config = ServidorConfig.objects.first()
            if config:
                campeonatos_ativos = Campeonato.objects.filter(temporada=config.temporada_atual)
                todas_finalizadas = True
                
                for camp in campeonatos_ativos:
                    jogos_camp = PartidaMundo.objects.filter(campeonato=camp)
                    
                    # 1. INICIAR O MUNDO (Se o campeonato não tiver nenhum jogo ainda)
                    if not jogos_camp.exists():
                        gerar_calendario_liga(camp)
                        acoes_realizadas.append(f"Big Bang: Calendário gerado para {camp.nome} (Temporada {config.temporada_atual}).")
                        todas_finalizadas = False # O campeonato acabou de nascer
                    
                    # 2. VERIFICA SE O CAMPEONATO AINDA ESTÁ A ROLAR
                    elif jogos_camp.exclude(status='finalizada').exists():
                        todas_finalizadas = False
                
                # 3. VIRADA DE TEMPORADA GERAL
                # Se todos os campeonatos da temporada atual já tiveram todos os seus jogos finalizados
                if todas_finalizadas and campeonatos_ativos.exists():
                    config.temporada_atual += 1
                    config.rodada_atual = 1
                    config.save()
                    
                    # Clona os campeonatos para a nova temporada e gera os novos calendários
                    for camp_antigo in campeonatos_ativos:
                        novo_camp = Campeonato.objects.create(
                            nome=camp_antigo.nome,
                            temporada=config.temporada_atual,
                            tipo=camp_antigo.tipo,
                            divisao=camp_antigo.divisao
                        )
                        gerar_calendario_liga(novo_camp)
                        
                    acoes_realizadas.append(f"A TEMPORADA {config.temporada_atual} COMEÇOU! Novos calendários gerados automaticamente.")

        return JsonResponse({
            'sucesso': True, 
            'hora_servidor': agora.isoformat(),
            'acoes': acoes_realizadas if acoes_realizadas else ["Nenhuma ação agendada para esta hora."]
        })

    except Exception as e:
        logger.error(f"Erro no Cron Engine: {e}")
        return JsonResponse({'sucesso': False, 'erro': str(e)}, status=500)
