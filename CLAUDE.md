# Timtim e os Brinquedos Perdidos

Jogo de plataforma 2.5D no navegador. Three.js com `THREE` global, JavaScript puro,
sem etapa de build: `game/index.html` carrega `game/vendor/three.min.js` e oito arquivos
em `game/src/` por `<script src>`. Publicado no Cloudflare Pages.

**Promessa (de `game/docs/design.md`):** 2 a 3 minutos de plataforma que parecem um curta de
animação estrelado por um cachorro de verdade. Feito para mostrar aos amigos.

## Fontes de verdade — leia antes de mexer em qualquer coisa

@game/docs/design.md
@docs/ritmo-das-fases.md

Decisões de arte e de jogo vivem no `design.md`, datadas. Medidas de fase e a regra dos 70%
vivem no `ritmo-das-fases.md`. **Nunca re-decida o que já está datado nesses arquivos** —
em 24 e 25/11/2026 a direção de arte "Ori" foi reaplicada quatro vezes por não ter sido lida.
Se você discorda de uma decisão datada, diga, não refaça.

## Fatos não-negociáveis

Errar qualquer um destes é refação garantida. Ficha visual: `game/assets/tintim-character-sheet.png`.

| Personagem | Fato |
|---|---|
| **Timtim** | o herói. Mancha preta, bandana de festa junina, lacinho. Tem o **mesmo tamanho em todas as poses** (alturas em `R.frame`: parado 80, correndo 82, pulo 77, queda 82, farejando 69) |
| **Zara** | chihuahua **preta e branca** |
| **Elvis** | chihuahua **branco** |
| **Furtão** | o ladrão da fase 1, **marrom** (nunca cinza-azulado) |
| **Lobo-guará** | chefe da fase 2. Crina é o ponto fraco |

Cor por fase, uma por fase e constante ao longo do caminho: **fase 1 azul** (noite soturna),
**fase 2 laranja** (festa quente), **fase 3** o quadro de Van Gogh.

"Ori" é **só linguagem visual** (silhueta primeiro e luz depois, herói pequeno e luminoso,
camadas, raios de luz, bioluminescência, paleta por região). Nunca personagens, lugares,
árvores-símbolo ou música.

**Reprovado em teste, não propor de novo:** na fase 1, bandeirinhas, cenário colorido ou
"feliz", vila ao entardecer, chafariz, coreto, carrinho de pipoca.

## Matriz de dispositivos — os dois casos obrigatórios

Nenhuma mudança visual ou de interface está pronta sem ter sido vista nos **dois**:

1. **Desktop** — 960×540
2. **Celular** — viewport de iPhone, com safe-area e os **botões de toque na tela**

Os seis últimos commits da produção foram conserto de celular descoberto no fim. O
`pointer: coarse` muda a câmera (`DESCE` em `render3d.js`) e os botões cobrem a área de jogo:
o que parece certo no desktop esconde o Timtim no iPhone.

## Evidência antes de "pronto"

Nada é pronto sem:

- `node game/tests/smoke.js`, `smoke-arraial.js` e `smoke-quadro.js` **verdes**; e
- print nos dois viewports acima (`bash .claude/scripts/page-shot.sh game/index.html <saida.png> --size WxH`).

Mexeu no pulo ou no desenho de uma fase? `node game/tests/metricas.js` também, e a regra dos
**70% do alcance** no caminho principal é bloqueante, não conselho.

Piso de desempenho: **45 fps**. Abaixo disso `R.setQuality` baixa o nível sozinho — se a
qualidade está caindo em cena, o problema é de orçamento, não de ajuste fino.

## Donos por arquivo

Um dono por arquivo, escolhidos pelo churn real da produção. **Nunca dois agentes no mesmo arquivo.**

| Agente | Arquivos |
|---|---|
| `art-director` | `game/assets/` (capa, logo, cards), paleta, fidelidade às fichas |
| `ui-programmer` | `game/src/ui.js`, `game/index.html`, viewport, toque, safe-area |
| `technical-artist` | `game/src/render3d.js`, shaders, pós-processamento, níveis de qualidade |
| `level-designer` | medidas e rota de fase, `docs/ritmo-das-fases.md` |
| `qa-tester` | `game/tests/`, achados, evidência |
| `ux-designer` | matriz de dispositivos, fluxo de telas, onboarding |

Para a camada Three.js, o `technical-artist` tem três skills de apoio instaladas em
`.claude/skills/threejs-*` (o framework não traz nenhum especialista web): `threejs-debug-profiler`
(tela preta, NaN no bloom, resize, toque, orçamento de draw calls), `threejs-aaa-graphics-builder`
(materiais, luz, shaders de superfície) e `threejs-aaa-vfx-builder` (partículas por `DepthTexture`,
trilhas, passes de impacto). Elas não são comando de barra: nomeie a skill no pedido. **O kit de
VFX delas é TypeScript com módulos ES — é referência, não código para copiar.** Ver
`.claude/skills/THREEJS-PACK.md`.

`art-director`, `level-designer` e `ux-designer` **não têm Bash** — eles leem, julgam e escrevem,
mas não rodam o jogo nem tiram print. Quem produz a evidência para eles é o `qa-tester`.

No máximo **3 agentes em paralelo**, e só em arquivos diferentes. `ui.js` foi tocado em 31 dos
50 commits: é gargalo compartilhado e nunca entra em paralelo com outra tarefa.

## Modo

`project.yaml` é a configuração: `review_mode: lean`, `automation: guided`,
`performance.enforce: block`, `testing.strict.visual: true`. Decisões grandes vêm ao Pedro;
as pequenas seguem declaradas. Não mude esses valores sem pedir.
