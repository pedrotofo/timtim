# As três skills de Three.js — o que são e o que não se aplica aqui

Instaladas em 28/11/2026 de `majidmanzarpour/threejs-game-skills` (MIT), clone superficial do
`main`. **Os arquivos são do upstream, sem uma linha alterada**, para uma atualização do pacote
poder ser recopiada em cima. Esta nota é a única coisa local.

| Skill | Para que serve aqui |
|---|---|
| `threejs-debug-profiler` | tela preta, NaN no bloom HDR, realimentação de composer/depth, bugs de resize e de toque no celular, e orçamento medido de draw calls, triângulos, texturas e memória |
| `threejs-aaa-graphics-builder` | crítica de direção de arte com âncoras de calibração, materiais PBR, luz e sombra, shaders de superfície (`onBeforeCompile`), LOD e instanciamento, orçamento de render |
| `threejs-aaa-vfx-builder` | coreografia de 5 tempos, partículas suavizadas por `DepthTexture`, trilhas, relâmpago fractal, passes ópticos de impacto |

Por que estas três e não as dez: o framework Claude Code Game Studios tem 4 a 5 agentes
especialistas para Godot, Unity e Unreal, e **zero** para web/Three.js — o `render3d.js` (1.393
linhas, o maior churn do projeto) não tinha dono especializado. As outras sete skills do pacote
duplicam o que o estúdio já faz (direção, QA, interface, gameplay) ou pedem chaves de API
(Tripo, Gemini, ElevenLabs) para gerar assets que este projeto já tem.

## Como chamar

Elas não têm `user-invocable: true` no frontmatter, de propósito (é assim no upstream): não
viram comando de barra. Carregam quando o assunto bate com a descrição, ou **nomeando a skill no
pedido** — "usa a threejs-debug-profiler para achar por que a tela ficou preta no iPhone". É o
que o README do próprio pacote recomenda.

## O que NÃO se aplica ao Timtim

- **O kit de VFX é só referência.** `assets/vfx-kit/*.ts` é TypeScript estrito com módulos ES,
  escrito para um projeto Vite. O Timtim é `THREE` global por `<script src>`, sem etapa de
  build (ver `.claude/rules/timtim-web.md`). **Não copie esses arquivos para `game/src/`** — leia
  a matemática dos shaders e reescreva no estilo do `render3d.js`.
- **O `threejs-debug-profiler` foi escrito para ser chamado por um `threejs-game-director`**, que
  eu não instalei (duplicaria o estúdio). Onde ele diz "devolva ao lead", o lead aqui é o
  `technical-artist`, ou a conversa principal.
- **O scorecard e as âncoras de calibração** (`assets/scorecard-anchors/*.jpg`) foram pontuados
  para um estilo quase fotográfico. O Timtim é pintado, na linguagem visual de Ori: use o método
  (comparar contra uma âncora), não as notas.
- As três skills pressupõem uma versão recente do Three.js. O jogo subiu para **r186** em
  28/11/2026 (era r144, de 2022), com `ColorManagement` desligado para preservar a arte — ver o
  cabeçalho de `game/src/render3d.js`.
