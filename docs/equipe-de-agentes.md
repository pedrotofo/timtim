# Equipe de agentes para o Timtim — diagnóstico das refações e formato proposto

Estudo pedido pelo Pedro em 28/11/2026: por que houve tanta refação na produção do Timtim e qual
formato de equipe de agentes resolve isso. Fontes: os 50 commits do repositório, o `revisao-hater.md`,
o `ritmo-das-fases.md`, o `game/docs/design.md`, o framework instalado em `.claude/` e a documentação
oficial de subagentes, hooks e skills do Claude Code.

---

## 1. O diagnóstico: medindo a refação

As refações não estão no git — estão dentro das conversas. Os 50 commits são só os sobreviventes.
Mas eles deixam a marca:

| Medida | Valor | O que significa |
|---|---|---|
| Commits totais | 50 em 2 dias (24–25/11) | produção muito rápida |
| Arquivos por commit | 59,3 em média | commits em lote, não unidade de trabalho |
| `game/src/ui.js` | tocado em **31 dos 50** commits | o gargalo real da produção |
| `game/src/render3d.js` | 33 commits | segundo gargalo |
| Capa e logo | **9 commits** | refeitos ~6 vezes |
| Cards de história | **11 commits** | refeitos ~6 vezes |
| Celular / iPhone | **6 commits**, todos nos últimos 80 min | plataforma descoberta no fim |
| Achados do `revisao-hater.md` | **71 de uma vez** | o QA rodava tarde |
| Revisões em lote | 4 (`#14` "50 correções", `#16`, `#25`, `#32`) | retrabalho concentrado |

Somando os clusters, **mais da metade dos commits é refação, não conteúdo novo.**

### Os quatro padrões de refação

**a) Decisão re-tomada.** A direção de arte "linguagem visual de Ori" foi aplicada quatro vezes
(`#2`, `#3`, `#12`, `#31`). A Zara e o Elvis tiveram os nomes trocados (`#33`) *apesar de existirem
fichas de personagem em `game/assets/tintim-character-sheet.png`*. O inimigo da fase 2 virou galinha
(`#5`), depois raposa (`#7`), depois lobo-guará (`#8`).

**b) Superfície de marca sem especificação.** Capa, logo e cards somam 20 commits de refação. O
`design.md` é uma boa fonte de verdade para o *mundo* (cor por fase, luz, contraste, 2.5D) — mas não
diz nada sobre capa, logo, tipografia ou pergaminho. Onde não havia especificação, houve refação.

**c) Plataforma descoberta no fim.** Os seis últimos commits (`#44`–`#50`) são todos conserto de
celular: viewport cortado, botões de toque cobrindo o Timtim, iPhone piscando. O jogo foi feito para
desktop e adaptado depois.

**d) QA como evento, não como passo.** O `revisao-hater.md` é um documento excelente — e é a prova do
problema: 71 achados numa única passada, encontrados por alguém jogando o jogo e fotografando trecho a
trecho. O único controle de qualidade que funcionava de verdade na produção era **o Pedro jogando e se
incomodando.** Um gate humano que dispara tarde encontra tudo de uma vez.

---

## 2. A causa raiz: o framework está instalado e desligado

O `.claude/` deste projeto tem um estúdio inteiro: **49 agentes, ~100 skills, 28 gates de diretor,
18 hooks, 14 arquivos de regras, 62 templates.** Nada disso roda. Faltam três arquivos:

| Arquivo | Existe? | Consequência de faltar |
|---|---|---|
| `CLAUDE.md` (raiz) | **não** (nunca existiu no git) | `game/docs/design.md` não é carregado sozinho. Toda sessão começa cega → padrão (a) |
| `project.yaml` (raiz) | **não** | `rigor` cai no padrão `minimal`, que resolve `review_mode: solo` = **zero gates de diretor** |
| `.claude/settings.json` | **não** | os 18 hooks são scripts inertes; nada é validado |

Ou seja: a resposta que você está pedindo já está no projeto, desenergizada. O `review_mode: solo`
é literalmente o modo "game jam, velocidade máxima, sem revisão" — e foi nele que a produção rodou.

**Ressalva honesta:** ligar os 18 hooks não resolveria sozinho. Lendo o
`.claude/docs/hooks-reference.md`, a maioria deles **avisa e nunca bloqueia** ("Warns, and never
blocks"). Eles são consultivos. O gate que de fato impede refação tem de ser construído — ver §4.

---

## 3. O formato de equipe proposto

O erro a não cometer é "adicionar mais agentes". Já há 49 agentes e ~100 skills — e a documentação
oficial dá um orçamento de contexto para descoberta de skills (da ordem de 1% da janela só para as
descrições). Com uma centena de skills, escolher a certa já é ruído. O formato correto aqui é
**poucos agentes, donos claros, gates duros.**

### 3.1 Os cinco agentes que importam neste projeto

Escolhidos pelo churn, não pelo organograma. Cada um é dono de arquivos, não de assuntos:

| Agente | Dono de | Justificativa nos dados |
|---|---|---|
| `art-director` | capa, logo, cards, paleta por fase, fidelidade às fichas | 20 commits de refação; Ori reaplicado 4×; Zara/Elvis trocados |
| `ui-programmer` | `ui.js`, `index.html`, viewport, toque, safe-area | `ui.js` em 31 de 50 commits; 6 commits de iPhone no fim |
| `technical-artist` | `render3d.js`, pós-processamento, níveis de qualidade | `render3d.js` com o maior churn (33) |
| `level-designer` | medidas de fase, rota, ritmo, `metricas.js` | já funcionou: `ritmo-das-fases.md` + regra dos 70% |
| `qa-tester` | smoke tests, achados, evidência | o `revisao-hater.md` prova que o papel existe, mas rodava tarde |

Os quatro diretores e as 44 outras especialidades continuam disponíveis para chamada pontual —
`performance-analyst` quando cair o fps, `audio-director` na mixagem. Não entram no fluxo padrão.

### 3.2 Como paralelizar

A documentação da Anthropic sobre o sistema multi-agente deles usa **3 a 5 subagentes em paralelo**
como faixa prática (o limite técnico de concorrência é bem maior, ~20, mas o custo de handoff cresce
e a qualidade do briefing cai). Para o Timtim:

- **Paralelizam bem:** `art-director` + `level-designer` + `technical-artist`. Tocam arquivos
  diferentes (assets, dados de fase, `render3d.js`).
- **São sequenciais:** `ui-programmer` e `qa-tester`. O `ui.js` é o arquivo compartilhado — dois
  agentes nele ao mesmo tempo é conflito garantido. E o QA só faz sentido depois.

Regra: **nunca dois agentes no mesmo arquivo.** Com `ui.js` em 31 de 50 commits, isso significa que
na prática a paralelização útil aqui é de 3 agentes, não 5.

### 3.3 Briefing: o que todo agente recebe

O custo de handoff é real — o que o subagente não recebe, ele não sabe, e o que ele devolve é só o
relatório. Todo briefing leva quatro campos:

1. **Objetivo** — o resultado, não a tarefa ("a capa lê o título em 3 s num celular", não "mexa na capa")
2. **Fronteira** — quais arquivos ele pode tocar, nominalmente
3. **Fonte de verdade** — os caminhos a ler primeiro (`design.md`, art bible, fichas)
4. **Evidência de pronto** — o que ele tem de anexar (ver §4)

---

## 4. Os gates: o que de fato mata a refação

Esta é a parte que muda o resultado. As três camadas, em ordem de retorno:

### Gate 1 — Evidência antes de "pronto" (o de maior retorno)

Um hook no evento `Stop` que **bloqueia** o agente de encerrar sem:

- `node game/tests/smoke.js`, `smoke-arraial.js` e `smoke-quadro.js` verdes; e
- captura de tela em **dois** viewports: desktop 960×540 e celular (`pointer: coarse`, com os botões
  de toque na tela).

Isso sozinho teria pego os 6 commits de iPhone e uma fatia grande dos 71 achados do `revisao-hater`.
Diferente dos 18 hooks instalados, este **bloqueia** em vez de avisar.

**Limite honesto:** esse gate prova que alguém *olhou*, não que está bonito. É a mesma limitação do
`check_evidence.py` do pacote threejs, que confere cobertura de capturas e não qualidade. Gosto é o
que o Gate 2 cobre.

### Gate 2 — AD-VISUAL contra um art bible (custa uma linha para ligar)

O gate `AD-VISUAL` já existe em `.claude/docs/director-gates/ad-visual.md`. Ele manda o
`art-director` julgar uma decisão visual contra o art bible e devolver **APPROVE / CONCERNS /
REJECT**. Falta o art bible: existe a skill `/art-bible`, o template e o gate — e nenhum documento.

Escopo do art bible do Timtim (exatamente onde a refação bateu): capa, logo, cards de história,
pergaminho, tipografia, e as fichas de Zara, Elvis, Timtim, Furtão e lobo-guará como fatos
não-negociáveis.

Regra: **toda mudança em capa, logo, card ou paleta passa pelo AD-VISUAL antes de gerar o asset.**
Gerar primeiro e julgar depois é o que produziu 20 commits.

### Gate 3 — Medida bloqueante de fase

Mudou o pulo ou o desenho de uma fase → roda `node game/tests/metricas.js`, e a regra dos **70% do
alcance** é bloqueante, não consultiva. Isto já existe e já funciona; só não é obrigatório.

### E o interruptor geral

`review_mode: lean` no `project.yaml` em vez do `solo` atual. `lean` roda os gates de fase sem
encarecer cada passo. `full` é provavelmente demais para este projeto.

---

## 5. Ordem de execução

A ordem importa: vários hooks do framework usam `project.yaml` como marcador de raiz, então ele vem
antes do `settings.json`.

1. **`project.yaml`** — `rigor: standard`, `review_mode: lean`, `automation: guided`, mais a matriz de
   dispositivos (desktop 960×540, iPhone com safe-area, janela de artefato) e o orçamento de
   performance (piso de 45 fps, os três níveis de qualidade)
2. **`CLAUDE.md`** — ~40 linhas, importando `game/docs/design.md` e `docs/ritmo-das-fases.md`, mais os
   fatos de personagem. Isto mata o padrão (a) na raiz
3. **`/art-bible`** — fecha as superfícies de marca. Mata o padrão (b)
4. **`.claude/settings.json`** — liga os hooks consultivos existentes
5. **Gate 1** — o hook `Stop` de evidência, construído. Mata os padrões (c) e (d)
6. **Gates 2 e 3** — ligados nos pontos de decisão

Passos 1 a 3 são de documento e já valem sozinhos. O passo 5 é o que exige código novo.

---

## 6. O que este estudo não verificou

- Não rodei nenhum dos 18 hooks. Alguns podem depender do `project.yaml` para funcionar; a ordem do
  §5 assume isso mas não foi testada.
- A documentação oficial de subagentes e hooks foi lida parcialmente pela pesquisa. O número de 3 a 5
  paralelos e o mecanismo de bloqueio no `Stop` vêm do blog de engenharia da Anthropic e da doc de
  hooks; o JSON exato do hook deve ser conferido contra o `.claude/docs/hooks-reference.md`, que é
  local e é a autoridade para este framework, antes de escrever o `settings.json`.
- Não medi quanto custa em tokens rodar 3 agentes em paralelo neste projeto. O `session-stop.sh`
  escreve a conta em `production/session-logs/session-cost.md` quando ligado — vale medir uma semana
  antes de decidir a faixa.
