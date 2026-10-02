# Checklist de deploy (PythonAnywhere)

Depois de `git pull` e `pip install -r requirements.txt`:

```bash
# 1) Tabelas novas e campos novos (as migrations de accounts/palpites/futebol são geradas aqui, como sempre)
python manage.py makemigrations accounts palpites futebol avisos melhores
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
