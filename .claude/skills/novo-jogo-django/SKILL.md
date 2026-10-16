---
name: novo-jogo-django
description: Checklist para adicionar um jogo novo à Cartolândia (app Django, rotas, engine, telas, API JSON, coins/conquistas, testes e notas de deploy). Use ao começar qualquer jogo ou modo de jogo novo no site.
---

# Adicionar um jogo novo à Cartolândia

Projeto Django 6 (`bolao_cartolandia/settings.py`), templates em `templates/<app>/`, deploy no PythonAnywhere (`DEPLOY.md`). Jogos existentes para copiar padrões: `minijogo` (X1 Pênaltis), `duelos` (arena/trunfo), `setezero` (7 a 0).

## 1. Onde mora

- Jogo independente → app novo: `python manage.py startapp <nome>`, adicionar em `INSTALLED_APPS` (com comentário curto, como os outros) e `path('<nome>/', include('<nome>.urls'))` em `bolao_cartolandia/urls.py`.
- Variação de um jogo existente → dentro do app dele.
- `app_name = '<nome>'` no `urls.py`; telas em cima, APIs (`api/...`) embaixo, como `minijogo/urls.py`.

## 2. Camadas

- `engine.py`: regras puras do jogo (sem request), testáveis. Toda decisão de resultado fica aqui.
- `models.py`: partida/sessão, placar, ranking. Lembrar de gerar a migration e listá-la no `DEPLOY.md`.
- `views.py`: telas com `@login_required` + `render`; APIs com `@login_required`, `@require_POST` quando mudam estado, corpo `json.loads(request.body)`, resposta `JsonResponse`. Validar que o usuário pertence à partida (`get_object_or_404` + checagem de jogador).
- `templates/<nome>/`: `{% extends 'base.html' %}`, `{% block title %}`, `{% block content %}`; `fetch` com headers `'Content-Type': 'application/json', 'X-CSRFToken': csrfToken` (ver `templates/minijogo/tela_jogo.html`).
- Multijogador assíncrono: polling de uma API `api/partida/<id>/status/` (modelo de `minijogo.views.api_status_partida`).

## 3. Integrações do site

- **Cartola Coins**: só via `accounts/coins.py` (`creditar`, `debitar`, `saldo`) — nunca mexer em `CarteiraCoins.saldo` direto. Crédito sempre decidido no servidor.
- **Conquistas**: regras em `avisos/conquistas.py` (`checar(usuario)`) se o jogo destravar algo.
- **Fim de jogo**: `templates/partials/modal_fim.html`.
- **IA (Claude)**: só via `ia/cliente.py` (`gerar_json(usuario, system, mensagem, schema)`), que já usa Haiku, JSON estruturado,
  cota diária por usuário e devolve `None` sem chave/erro. Todo jogo precisa de texto pronto para o `None`. A IA escolhe entre
  opções que o servidor valida (enums, `ia.limitar`, `ia.cortar`); nunca decide placar, pontos ou coins. Texto do usuário vai
  delimitado (`<resposta>…</resposta>`) e o prompt manda tratá-lo como dado. Crônica pós-jogo: `ia/narrador.py`.
- **Voz**: `{% include 'partials/voz.html' %}` + `Voz.falar(texto, {animado})` e um botão `data-voz-toggle`.
- **Avatares**: toda conquista nova em `avisos/conquistas.py` precisa de um avatar em `accounts/avatares.POR_CONQUISTA` (código ≤ 8 letras).
- **Menu/hub**: adicionar o card/link onde os outros jogos aparecem (a arena de jogos é `templates/duelos/listar_desafios.html`; conferir também o menu em `templates/base.html`).
- Cena 2D → seguir a skill `jogo-canvas-2d`.

## 4. Testes e verificação

- `tests.py` do app: engine com semente fixa, telas retornam 200 para jogador logado e redirecionam anônimo, APIs recusam usuário de fora da partida e não creditam coins duas vezes.
- Rodar: `python manage.py test <app>` (e `python manage.py check`); antes de abrir PR, a suíte inteira. Confira a linha
  `OK`/`FAILED` da saída: em `... | tail`, o código de saída é o do `tail`, não o dos testes.
- As migrations não vão para o Git (são geradas no servidor): para testar localmente, gere e apague depois.
- Ver no navegador com o plugin **playwright** (desktop e viewport de celular).

## 5. Entrega

- Atualizar `DEPLOY.md` com uma seção do lote: `makemigrations <app>`, `migrate`, comandos de seed e `collectstatic` se mexer em `static_files/`.
- Nada de dependência nova pesada no `requirements.txt` (conta gratuita do PythonAnywhere tem pouco espaço).
- Textos da interface e commits em português, como o histórico do repositório.
