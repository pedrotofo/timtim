# game/vendor/three.min.js

| | |
|---|---|
| Biblioteca | [three.js](https://threejs.org) |
| Versão | **r186** (npm `three@0.186.1`) |
| Formato | IIFE com `THREE` global, minificado |
| Licença | MIT — ver `three.LICENSE` |
| Atualizado em | 28/11/2026 (era **r144**, de 2022) |

## Como este arquivo foi feito

O three.js é publicado só como módulos ES, e o Timtim carrega tudo por `<script src>` sem etapa de
build. O pacote global vem de:

```sh
npm install three@0.186.1 esbuild
echo 'export * from "three";' > entry.js
esbuild entry.js --bundle --format=iife --global-name=THREE --minify \
  --outfile=three.min.js --legal-comments=none
```

A mesma versão que o starter web do framework fixa (`.claude/engines/web/starters/three/`), para
um dia o `.claude/scripts/vendor-three.sh` poder refazer este arquivo sem mudar de versão.

## O que o upgrade exigiu do código

Duas linhas em `game/src/render3d.js`, e nada mais — o arquivo usa `ShaderMaterial` com GLSL
próprio e **nenhuma** das APIs removidas entre r144 e r186 (`outputEncoding`, `.encoding`,
`physicallyCorrectLights`, `onBeforeCompile`):

1. `THREE.ColorManagement.enabled = false` — ligado por padrão desde o r152, converteria os 433
   literais de cor do arquivo de sRGB para linear e repintaria o jogo inteiro.
2. `renderer.outputColorSpace = THREE.LinearSRGBColorSpace` — o r144 saía em linear; o padrão
   virou sRGB no r152.

## Como se verificou que a imagem não mudou

`node game/tests/provar.js` ficou verde (173 verificações). Depois, `comparar-prints.js` mediu a
diferença de pixel entre a linha de base r144 e o r186, **e também entre duas rodadas do próprio
r186**, como controle:

| Comparação | Diferença média | Máxima | Pixels fora de 8 níveis |
|---|---|---|---|
| r144 contra r186 (desktop) | 1,14 | 160 | 0,69% |
| **r186 contra r186** (controle, desktop) | **1,18** | **168** | **0,78%** |
| r144 contra r186 (iPhone) | 0,44 | 161 | 0,31% |
| **r186 contra r186** (controle, iPhone) | **0,36** | **153** | **0,21%** |

O controle tem diferença **igual ou maior** que a comparação entre versões: a diferença entre r144
e r186 é indistinguível do ruído de rodada a rodada (vaga-lumes em movimento, fase do sprite). O
upgrade é visualmente neutro.

## O que ficou de fora de propósito

Adotar o gerenciamento de cor de verdade (deixar `ColorManagement` ligado) é um passe de arte sobre
433 literais, não uma troca de biblioteca. Ver `design/art/art-bible.md`, Seção 4.
