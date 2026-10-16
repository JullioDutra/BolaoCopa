---
name: jogo-canvas-2d
description: Padrões para criar ou mexer em jogos/cenas 2D em <canvas> na Cartolândia (sem bibliotecas, dentro de templates Django). Use ao criar um jogo 2D novo, animar um lance, desenhar campo/jogadores/bola, ou ajustar o Campo2D do X1 Pênaltis.
---

# Jogos 2D em canvas na Cartolândia

Referência viva: `templates/minijogo/_campo2d.html` (X1 Pênaltis). Copie a estrutura dele, não reinvente.

## Regras de arquitetura

- **Sem bibliotecas de jogo** (nada de Phaser/Pixi/Three). Canvas 2D puro + JS inline no template. O site já carrega Bootstrap 5.3, Font Awesome 6.4 e as fontes Barlow Condensed / Inter / JetBrains Mono (`templates/base.html`).
- **A cena fica num partial** `templates/<app>/_<nome>2d.html` com `<canvas id="...">` + `<script>`, incluído na tela do jogo com `{% include %}`.
- **Módulo IIFE exposto em `window`** (ex.: `window.Campo2D = (function () { ... return { api } })();`). A página só fala com a cena por essa API pequena (`papeis()`, `cobranca(..., aoTerminar)`, `reset()`).
- **O servidor decide, o canvas só anima.** Resultado, pontuação, coins e ranking são calculados no Python (`engine.py` do app) e chegam por JSON. O cliente nunca manda "ganhei X pontos" — manda a *ação* (jogada, zona, tecla) e o servidor valida. Se o jogo for de reflexo/tempo real e local, o servidor ainda deve validar limites plausíveis (pontuação máxima por segundo, duração mínima da partida) antes de creditar qualquer coisa.
- **Alvos clicáveis em HTML, desenho no canvas.** Botões/zonas acessíveis ficam em elementos DOM posicionados sobre o canvas (como `#trave-botoes`); a cena mede esses elementos com `getBoundingClientRect()` para desenhar alinhado.

## Esqueleto obrigatório da cena

```js
window.MinhaCena = (function () {
    const cv = document.getElementById('minha-cena');
    const ctx = cv.getContext('2d');
    if (!ctx.roundRect) { /* polyfill Safari < 16 — copiar de _campo2d.html */ }
    const palco = cv.parentElement;
    let W = 0, H = 0, dpr = 1;

    function medir() {
        const r = palco.getBoundingClientRect();
        dpr = Math.min(window.devicePixelRatio || 1, 2);      // limita a 2x (celular)
        W = r.width; H = r.height;
        cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
        cv.style.width = W + 'px'; cv.style.height = H + 'px';
    }

    function quadro(t) {
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        ctx.clearRect(0, 0, W, H);
        // desenhar em coordenadas CSS (W x H), nunca em pixels físicos
        requestAnimationFrame(quadro);
    }

    window.addEventListener('resize', medir);
    medir();
    requestAnimationFrame(quadro);
    return { /* API mínima usada pela página */ };
})();
```

## Convenções

- **Tudo relativo ao tamanho** (`W`, `H` ou a caixa medida `G`): nada de coordenadas fixas em px — o público joga no celular (PWA).
- **Animação por tempo, não por frame**: use `t` do `requestAnimationFrame` e progresso `p = clamp((t - t0) / DURACAO)`, com os helpers `lerp`, `clamp`, `easeOut`, `easeIn`. Para física em tempo real use passo fixo (`dt` acumulado, ex.: 1/60 s) para não variar entre 60 Hz e 120 Hz.
- **Aleatoriedade visual determinística** (torcida, grama, partículas fixas): gerador com semente (`s = (s * 9301 + 49297) % 233280`) para não "piscar" a cada quadro.
- **Nomes em português**, como o resto do código (`cenario`, `goleiro`, `bola`, `quadro`, `medir`).
- **Cores**: azul `#2563eb` (j1), vermelho `#dc2626` (j2), amarelo `#facc15` (destaque/Cartolândia), gramado `#1f7a3a`/`#23873f`, fundo `#05070c`→`#142033`. Texto no canvas em `"Barlow Condensed"` peso 800.
- **Entrada**: suporte a toque e mouse com Pointer Events (`pointerdown/move/up`) e `touch-action: none` no canvas quando ele recebe gestos; teclado opcional. Nunca dependa só de teclado.
- **Desempenho**: pausar o loop quando `document.hidden` (evento `visibilitychange`); evitar criar gradientes/objetos dentro de laços quentes; pré-renderizar fundos estáticos num canvas fora da tela quando o cenário for pesado.
- **Fim de jogo**: usar o modal padronizado `templates/partials/modal_fim.html` (`window.abrirFimDeJogo(data)`) ou o estilo `sz-modal` / `partials/arena_css.html`, não um modal novo.
- `aria-hidden="true"` no canvas decorativo; o estado do jogo (placar, vez) também aparece em texto HTML.

## Testes

- Teste Django (no `tests.py` do app) garantindo que a tela renderiza o canvas e a API do módulo (`assertContains(resp, 'id="minha-cena"')`, `assertContains(resp, 'window.MinhaCena')`) e que a API de status devolve os dados que a animação consome. Ver `minijogo/tests.py`.
- Regras do jogo testadas no `engine.py`, com sementes fixas para resultados determinísticos.
- Para ver a cena de verdade: subir `python manage.py runserver` e usar o plugin **playwright** (navegar, logar, tirar screenshot do canvas, conferir console sem erros, testar em viewport de celular 390x844).
