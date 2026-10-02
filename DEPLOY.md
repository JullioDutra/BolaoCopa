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
