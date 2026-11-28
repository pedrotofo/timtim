# Testes do Timtim

## Preparar a máquina (uma vez)

Precisa de **Node 18 ou mais** e do Chromium do Playwright. **Não precisa de Python** — o
servidor local é Node, dentro do `provar.js`:

```sh
npm install          # instala o playwright
npm run preparar     # baixa o Chromium que ele usa
```

### Windows: o Git Bash não é opcional

A prova (`provar.js`) é Node e roda no PowerShell sem problema. **Os hooks são outra história.**
Sem o [Git para Windows](https://git-scm.com/downloads/win) instalado, o Claude Code roda os hooks
no PowerShell, e cada um **sai 0 sem executar** — o Gate 1 não bloqueia nada, em silêncio. O
`setup-requirements.md` do framework documenta isso. O Claude Code acha o Git Bash em
`C:\Program Files\Git` mesmo fora do PATH; se não achar, defina `CLAUDE_CODE_GIT_BASH_PATH`
apontando para o `bash.exe`.

No PowerShell 5.1 (o que vem no Windows) o `&&` não é operador válido: rode os comandos em linhas
separadas, ou use `;`.

## Rodar

```sh
npm run provar       # a prova completa: os 3 smoke tests + evidência nos 2 viewports
# ou, sem npm:  node game/tests/provar.js
```

É isto que o Gate 1 exige. Termina verde e escreve `production/evidencia/prova.ok`; o hook
`.claude/hooks/gate-evidencia.sh` lê o recibo e bloqueia o fim da resposta enquanto houver mudança
em `game/src`, `game/assets`, `game/vendor`, `index.html` ou `mapa.html` sem prova mais nova.

Avulsos, se precisar: `npm run smoke`, `smoke-arraial`, `smoke-quadro`, `evidencia`, `metricas`.

## Quanto tempo leva

Depende de haver placa de vídeo.

| Máquina | Prova completa | Por quê |
|---|---|---|
| Com GPU (seu PC) | segundos a pouco mais de um minuto | o jogo roda a ~1× o tempo real |
| Sem GPU (contêiner na nuvem) | vários minutos | WebGL em software; medimos o relógio do jogo a **0,58×** do tempo real |

Esse 0,58× não é defeito: `main.js` limita cada quadro a `dt = min(0.033, raw)` e a 10 passos de
1/240 s, de propósito, para a física não explodir num engasgo. A consequência é que **tempo de
parede não mede tempo de jogo** — foi a causa das três fragilidades consertadas em 28/11/2026. Se
você escrever um teste novo, espere por **condição** (`until(...)`), nunca por tempo fixo.

## Os arquivos

| Arquivo | O que faz |
|---|---|
| `provar.js` | a prova completa; sobe e derruba o servidor Node sozinho e escreve o recibo. Igual nos três sistemas |
| `provar.sh` | atalho de uma linha para o `provar.js`, para quem decorou o comando |
| `smoke.js` | fase 1 (o Parque), 56 verificações |
| `smoke-arraial.js` | fase 2 (o Arraial), 55 verificações |
| `smoke-quadro.js` | fase 3 (o Quadro Encantado), 60 verificações |
| `evidencia.js` | abre o jogo em desktop 960×540 e num iPhone com toque, e salva um print de cada |
| `metricas.js` | mede o pulo de verdade e confere cada buraco contra a regra dos 70% |
| `comparar-prints.js` | diferença numérica entre dois prints; use um controle (duas rodadas da mesma versão) antes de atribuir a diferença a uma mudança |
