---
paths:
  - "game/src/**"
  - "game/tests/**"
  - "game/index.html"
  - "game/mapa.html"
---

# Regras do código do Timtim

Arquivo do projeto, não do framework. As 14 regras de `.claude/rules/` que vêm no Claude Code
Game Studios 1.3.0 têm globs de outros layouts (`src/ui/**`, `src/gameplay/**`, `tests/**`) e
nunca disparam aqui — este arquivo cobre os caminhos reais. Ele é aditivo: uma atualização do
framework não o sobrescreve.

Algumas regras genéricas do framework **não valem** neste projeto e não devem ser cobradas:
não há sistema de localização (os textos são em português, no código), não há suporte a
gamepad, e não há modo para daltônicos.

## Arquitetura — não mude sem pedir

- **`THREE` é global**, de `game/vendor/three.min.js`. Não introduza `import`/`export` nem
  etapa de build: o jogo tem de abrir servido como arquivo estático, sem empacotador.
- Os oito arquivos de `game/src/` entram por `<script src>` em ordem, e compartilham estado
  por `window.TT` (`game.js:4`). `window.__tintim` (`main.js:46`) é a janela que os testes
  usam para achar o estado — **não renomeie nem remova** nada que ele expõe.
- As regras do jogo andam em **passos fixos de `STEP = 1 / 240` s** (`main.js:29`). Isso existe
  porque o pulo dependia da taxa de quadros: 149 px a 30 fps contra 161 px a 144 fps. Nunca
  faça física ou lógica de jogo depender de `dt` variável.

## Celular é obrigatório, não é adaptação

- `matchMedia('(pointer: coarse)')` muda a câmera (`DESCE`, em `render3d.js`) e os botões de
  toque cobrem a parte de baixo da tela. O que lê bem no desktop pode esconder o Timtim.
- Toda mudança visual ou de interface se confere nos dois viewports: desktop 960×540 e um
  iPhone com safe-area. Um print só de desktop não é evidência.

## Testes

- Os smoke tests **esperam por condição, não por tempo fixo** (`until(...)`, não
  `waitForTimeout` como prova). Mantenha assim: eles rodam em máquina lenta sem placa de vídeo.
- Mexeu no pulo, no planar ou no desenho de uma fase: rode `node game/tests/metricas.js`. No
  caminho principal nenhum salto passa de **70%** do alcance do movimento que ele pede.
- Um teste que falha não se desliga nem se marca para pular. Conserte o jogo ou o teste.

## Render

- `render3d.js` tem shaders, bloom, profundidade de campo e três níveis de qualidade escritos
  à mão. Mudança ali sai do `technical-artist` e pede print nos dois viewports.
- Piso de 45 fps: abaixo disso `R.setQuality` baixa o nível sozinho. Qualidade caindo em cena
  é estouro de orçamento, não ajuste fino.
