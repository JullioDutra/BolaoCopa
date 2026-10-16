# Checklist de deploy (PythonAnywhere)

Depois de `git pull` e `pip install -r requirements.txt`:

```bash
# 1) Tabelas novas e campos novos (as migrations de accounts/palpites/futebol são geradas aqui, como sempre)
python manage.py makemigrations accounts palpites futebol avisos melhores duelos setezero
python manage.py migrate

# 2) Bet dos Melhores do Ano (todos os participantes como candidatos; --incluir-2021 adiciona quem só votou em 2021)
python manage.py seed_melhores --ano 2026

# 3) Banco de futebol para pesquisa e comparativos (começa pelo que o site já tem)
python manage.py importar_futebol --fonte internos
python manage.py importar_futebol --fonte football-data      # opcional (precisa FOOTBALL_DATA_TOKEN)
python manage.py importar_futebol --fonte espn               # opcional (sem chave)

# 4) Notificações push: gere as chaves UMA vez e cole no .env
python manage.py gerar_vapid

# 5) Arquivos estáticos (o service worker mudou) 
python manage.py collectstatic --noinput
```

Depois, **Web → Reload**.

## Tarefas agendadas (aba Tasks)
| Frequência | Comando |
|---|---|
| de hora em hora | `python manage.py sincronizar_jogos --rodadas 2` |
| de hora em hora | `python manage.py enviar_lembretes` |

Conta gratuita tem só 1 tarefa diária: use `https://SEU-SITE/palpites/api/sincronizar/<SYNC_SECRET_TOKEN>/` em um cron externo (cron-job.org).

## Variáveis do `.env`
Veja `.env.example` (todas opcionais: sem chave, a função correspondente só fica desligada).

## Lista de sites liberados (conta gratuita)
Confirme em https://www.pythonanywhere.com/whitelist/ se estão liberados: `api.football-data.org`, `v3.football.api-sports.io`, `www.thesportsdb.com`, `site.api.espn.com`, `news.google.com`, e os servidores de push dos navegadores. O que estiver bloqueado fica vazio no site, sem quebrar nada.

## iPhone
Notificações push só funcionam com o app instalado na tela inicial (iOS 16.4+).


## Lote 5 (espaço, escudos, jogadores, staff, scout, 7 a 0)

```bash
# 0) Liberar espaço: o google-generativeai (~100 MB) saiu do requirements. Desinstale o que sobrou:
pip uninstall -y google-generativeai google-ai-generativelanguage google-api-core google-api-python-client \
  google-auth google-auth-httplib2 googleapis-common-protos grpcio grpcio-status proto-plus protobuf httplib2 uritemplate \
  pyparsing cachetools rsa pyasn1 pyasn1-modules tqdm
pip install -r requirements.txt            # (requirements-dev.txt é só para rodar scripts de imagem localmente)

# 1) Novas tabelas/campos (futebol: Escudo, FonteAtleta, EstatisticaAtleta; duelos: baralho do Trunfo; setezero)
python manage.py makemigrations futebol duelos setezero && python manage.py migrate

# 2) Escudos globais e banco único de jogadores (primeiro simule, depois aplique)
python manage.py consolidar_escudos && python manage.py consolidar_escudos --aplicar
python manage.py consolidar_jogadores && python manage.py consolidar_jogadores --aplicar

# 3) Scout "mitou ou bagre" (opcional)
python manage.py importar_estatisticas --csv estatisticas.csv
python manage.py importar_estatisticas --api-football --temporada 2023 --time Flamengo

python manage.py collectstatic --noinput   # inclui static/media/logo.png
```
Painel da staff: `/gestao/`. Jogo novo: `/setezero/`. O Super Trunfo completa o próprio baralho na 1ª mesa.

## Draft Copa do Brasil (7 a 0)
Nova tabela `DraftCopa7a0` e campos em `Partida7a0`: `python manage.py makemigrations setezero && python manage.py migrate`.
Entrada: `/setezero/` → "Draft Copa do Brasil". O retrospecto fica em `/setezero/r/<código>/` (público por link secreto, para colar no grupo).

## Busca pelo Mundial (7 a 0)
Novo campo `torneio` em `DraftCopa7a0`: `python manage.py makemigrations setezero && python manage.py migrate`.
Entrada: `/setezero/` → "Busca pelo Mundial". Hino: por padrão é sintetizado no navegador (fanfarra em ré maior inspirada em
"Zadok the Priest", de Handel, domínio público). Se quiser outro áudio (que você tenha direito de usar), coloque em
`static_files/audio/hino-mundial.mp3` e rode `collectstatic`: ele toca no lugar do sintetizado.

## Lote 6 (Mundial bloqueado, perfis, NPCs)
- **Busca pelo Mundial** agora só abre para quem foi campeão da Copa do Brasil (draft).
- **Perfis públicos**: `/conta/jogador/<id>/` (avatar, frase, time, conquistas, títulos do 7 a 0). **Avatares** viraram ícones: os livres + um por conquista.
  Os emojis antigos viram o ícone "Bola" automaticamente (sem migração).
- **NPCs do modo carreira**: os "jogadores reais" criados como usuários agora ficam inativos e marcados `[NPC]`. Para ajustar os que já existem:
  `python manage.py ajustar_npcs` (simula) e `python manage.py ajustar_npcs --aplicar` (ou o botão "Separar NPCs" em /gestao/sistema/).
  Só mexe em quem nunca entrou no site, não é staff e não tem participação nem palpites. Os scripts `popular_reais*` já criam NPCs do jeito novo.

## Apito Final (jogo do árbitro)
App novo `arbitro`: `python manage.py makemigrations arbitro && python manage.py migrate`. Sem seed, sem dependência nova.
Entrada: `/arbitro/` (card "Apito Final" na Arena X1). Ranking em `/arbitro/ranking/`, súmula de cada partida em `/arbitro/partida/<id>/sumula/`.
- 10 lances por partida: 4 lances reais de Copas (`arbitro/historicos.py`) e 6 gerados pela regra (impedimento, bola na linha,
  contato dentro/fora da área, falta e cartão, reinício). Gabarito e pontuação ficam só no servidor.
- Prêmio: 3 coins por acerto (+30 no 10/10), no máximo 5 partidas premiadas por dia. Conquistas novas: Apito Inicial, Árbitro FIFA e Apito de Ouro.

## Jogos com IA: Quem Sou Eu?, Vida de Craque, Cabeçudos e Narrador
```bash
pip install -r requirements.txt          # novo: anthropic (SDK oficial da Claude)
python manage.py makemigrations ia quemsoueu craque cabecudos arbitro && python manage.py migrate
```
No `.env` (opcional, veja `.env.example`): `ANTHROPIC_API_KEY=...` (chave em console.anthropic.com).
`api.anthropic.com` já está na lista liberada da conta gratuita do PythonAnywhere.
Sem a chave, tudo funciona com textos prontos: perguntas rápidas no Quem Sou Eu?, cenas, coletivas e narrações
prontas no Vida de Craque, crônicas prontas no 7 a 0 e no Apito Final.

- **IA**: modelo `claude-haiku-5-5` (o mais barato), respostas curtas em JSON e limite de 60 chamadas por usuário por
  dia (`IA_LIMITE_DIARIO`). O uso fica em Admin → "Uso de IA" (chamadas e tokens por usuário e dia).
  A IA nunca decide placar, pontos nem coins: escolhe só entre opções que o servidor valida.
- **Quem Sou Eu?** (`/quem-sou-eu/`): craque do dia (44 fichas em `quemsoueu/craques.py`), ranking diário e geral, até 10 coins.
- **Vida de Craque** (`/craque/`): carreira de 8 temporadas com jogos simulados, coletivas e propostas; até 50 coins por temporada (3 por dia).
- **Cabeçudos** (`/cabecudos/`): futebol de cabeção 2D, 8 fases contra bots; o servidor só aceita partidas com duração plausível.
- **Narrador**: voz do navegador (botão "Voz") no 7 a 0, Apito Final e nos jogos novos; crônica pós-jogo com IA no 7 a 0 e
  comentarista de arbitragem na súmula do Apito Final (campo novo `resenha` em `arbitro`, daí o `makemigrations arbitro`).
- 4 conquistas novas (Detetive, Faro Apurado, Craque Campeão, Rei dos Cabeçudos), cada uma com avatar.
