# Pente fino no Timtim — briefing para uma sessão nova

Escrito em 28/11/2026, no fim da sessão que ativou o estúdio de agentes. Serve para a **próxima**
sessão, que começa sem nenhum contexto desta. Cole o pedido do fim deste arquivo.

## Por que esta revisão só é possível agora

Até hoje o jogo não tinha contra o que ser revisado. O `game/docs/design.md` cobria o mundo
(cor por fase, luz, 2.5D) e nada mais; capa, logo, cards, linguagem de forma e sistema de cor não
tinham regra escrita — e foi exatamente ali que caíram 20 dos 50 commits de 24 e 25/11.

Agora existe `design/art/art-bible.md`, com nove seções e **cerca de 80 proibições explícitas**.
Nenhuma delas jamais foi conferida contra o jogo. É esse o pente fino: não "procure bugs", mas
**confira o jogo contra as regras que ele mesmo acabou de escrever.**

## O que uma sessão nova já tem de graça

| Arquivo | O que dá |
|---|---|
| `CLAUDE.md` | carrega sozinho: fatos de personagem, matriz de dispositivos, donos por arquivo, regra de evidência |
| `game/docs/design.md`, `docs/ritmo-das-fases.md` | importados pelo `CLAUDE.md` |
| `design/art/art-bible.md` | as 9 seções e as proibições. **Leia por seção** (`Grep '^## '` e `Read` com offset), não inteiro: são 843 linhas e há guarda de leitura em 40 KB |
| `project.yaml` | `review_mode: lean`, `automation: guided`, `performance.enforce: block`, `testing.strict.visual: true` |
| `.claude/rules/timtim-web.md` | dispara ao abrir qualquer arquivo de `game/` |
| `docs/equipe-de-agentes.md` | o estudo das refações e por que a equipe é assim |

**Confira que os hooks estão vivos:** o `settings.json` foi escrito no meio da sessão anterior, e
hooks costumam ser lidos na abertura. Se a sessão nova não mostrar o bloco de contexto do
`session-start.sh` na primeira resposta, feche e abra uma sessão de verdade em vez de só dar
`/clear` — sem os hooks, o Gate 1 não bloqueia nada.

## A regra que não se negocia

`bash game/tests/provar.sh` tem de terminar verde (173 verificações hoje) e escrever
`production/evidencia/prova.ok`. O hook `.claude/hooks/gate-evidencia.sh` sai com 2 e impede a
resposta de encerrar enquanto houver mudança em `game/src`, `game/assets`, `game/vendor`,
`index.html` ou `mapa.html` sem prova mais nova que ela. Um teste que falha é bug a consertar,
nunca teste a desligar.

A prova é lenta (WebGL por software, vários minutos). Rode em segundo plano.

## As regras novas que nada nunca verificou

Estas são as de maior retorno, porque são checáveis e ninguém olhou:

1. **Zona de leitura** (Seções 3 e 6). Nenhum prop pode atravessar a faixa de tela onde o Timtim
   corre e pula. Densidade zero ali; a beleza vive no primeiro plano quase preto e no fundo
   enevoado. **Isto é restrição nova** — as fases foram desenhadas antes dela existir.
2. **Teto de três formas-herói por quadro** (Seção 3). Timtim, borda acesa, item e ponto fraco do
   chefe. Na debandada de galinhas isso provavelmente estoura.
3. **Menta só no piso** (Seção 4). `PAL.mint` não pode estar em mais nada.
4. **Vermelho fora do cenário** (Seção 4). `#e8323c` e `--rose` só em vida e dano.
5. **Alvo de toque de 44 px** (Seção 7). Já se sabe de um com 31 px.
6. **Todo efeito definido nos três níveis de qualidade** (Seção 8). Um efeito sem comportamento no
   nível 0 desaparece sem aviso no celular, que começa no nível 1.
7. **Fichas de personagem** (`CLAUDE.md`). Zara preta e branca, Elvis branco, Furtão marrom, Timtim
   do mesmo tamanho em toda pose (`R.frame`: 77 a 82, e 69 ao farejar).

## A pergunta central desta revisão (Pedro, 28/11/2026)

> "Muitos objetos, artes de cenário, movimentos e afins foram criados no improviso, sem passar por
> um crivo minucioso. As fases 2 e 3 estão caóticas, sem progressão do jogador, sem linha de
> crescimento, movimentos esquisitos."

O diagnóstico está certo e tem prova documental: **não existe nenhum documento de design de fase.**
Os templates `level-design-document.md`, `difficulty-curve.md` e `player-journey.md` estão em
`.claude/docs/templates/` e nunca foram usados. O `docs/ritmo-das-fases.md` mede alcance de pulo,
rota de buraco e tensão por trecho de 800 px — ele **não** diz o que cada fase ensina, em que
ordem, nem como a dificuldade cresce. As fases foram montadas, não desenhadas.

**Esta revisão não conserta isso — ela produz o laudo que vai justificar a reconstrução.** O Pedro
quer recriar as fases 2 e 3 com os assets existentes. A ordem combinada é: (1) este pente fino,
(2) escrever o `level-design-document` de cada fase, (3) reconstruir contra ele, uma fase por vez,
com a prova verde entre cada. Recriar antes de (2) seria improvisar de novo, e invalidaria 115 das
171 verificações dos testes de uma vez.

### O que o `level-designer` tem de responder, fase por fase

Para a fase 1 (que serve de controle, porque ninguém reclamou dela), a 2 e a 3:

1. **Cada mecânica nova é ensinada num lugar seguro antes de ser exigida?** Existe a estrutura
   ensina → pratica → cobra, ou a mecânica aparece já valendo coração?
2. **A dificuldade sobe ou pula?** Use a tabela de tensão por 800 px do `ritmo-das-fases.md` e diga
   se aquilo é uma curva ou é ruído. Onde há salto sem aviso, nomeie o trecho em pixels.
3. **Há descanso entre picos?** Dois picos colados sem respiro leem como caos, mesmo que cada um
   isolado seja justo.
4. **O espaçamento de checkpoint acompanha a dificuldade?** Trecho difícil pede checkpoint perto.
   (Já houve um vão de 3060 a 6340 sem nenhum, corrigido na revisão hater — veja se o padrão voltou.)
5. **A fase 2 pressupõe o que a fase 1 ensinou? A 3 pressupõe a 2?** Ou cada uma começa do zero e
   ao mesmo tempo exige mais?
6. **O que cada fase ensina em uma frase.** Se não couber numa frase, é esse o problema.

Entregue como laudo com severidade, **não** como fase reconstruída. A reconstrução é o passo 3.

## Os três eixos de "movimento esquisito"

O Pedro foi específico: **o movimento do Timtim está FORA de escopo.** Pulo, planada, corrida,
pirueta, tolerância na borda e pulo antecipado ficam como estão — ele está satisfeito com eles.
Não meça, não ajuste, não "melhore". Isso tira o `gameplay-programmer` desta revisão.

O esquisito é o que está em volta:

| Eixo | O que olhar | Dono | Critério |
|---|---|---|---|
| **Inimigos e chefes** | como galinhas, pombos, o lobo-guará e o Corvo-Borrão se aproximam, esquivam, atacam e recuam. Telegrafia antes do golpe? A esquiva parece decisão ou sorteio? Um inimigo faz coisa diferente do que sua silhueta promete? | `ai-programmer` | a Seção 3 do art bible: a forma anuncia a mecânica ("vem de lado e machuca de lado") |
| **Animações (os quadros)** | ciclo tremendo, tamanho mudando entre quadros, pata de apoio escorregando no chão, pose parada no meio de um ciclo filmado | `art-director` | **Seção 9.4 do art bible**: altura constante contra `R.frame` (77 a 82, 69 ao farejar) e pata de apoio que não desliza. Ele vê imagens — passe os `.webp` de `game/assets/anim/` por caminho |
| **Plataformas e cenário** | tábuas da quadrilha, móveis do quadro como plataforma, coluna de ar quente: o que se move no mundo. Período, amplitude e fase legíveis? Dá para prever onde a plataforma vai estar? | `level-designer` | `TT.C.movers` em `game.js` tem `ax`, `ay`, `per` e `ph` por plataforma — leia os números, não só a sensação |

## Quem faz o quê

Um dono por arquivo; **nunca dois agentes no mesmo arquivo**; no máximo **3 em paralelo**.
`art-director`, `level-designer` e `ux-designer` **não têm Bash** — eles leem, julgam e escrevem,
mas não rodam o jogo nem tiram print. Quem produz evidência para eles é o `qa-tester`, ou a
conversa principal com `game/tests/evidencia.js`.

| Agente | O que revisar | Paraleliza? |
|---|---|---|
| `art-director` | `game/assets/` contra as proibições das Seções 1 a 6 e 9. Ele **vê imagens** — passe os prints e os assets por caminho | sim |
| `technical-artist` | `game/src/render3d.js` contra os valores da Seção 4 e a regra dos três níveis da Seção 8. Agora em **three r186**. Use a skill `threejs-debug-profiler` (nomeie-a no pedido; não é comando de barra) | sim |
| `level-designer` | zona de leitura e props nas três fases, mais a regra dos 70% (`node game/tests/metricas.js`) | sim |
| `ux-designer` | Seção 7: o defeito medido de 4,3 px no iPhone e o alvo de 31 px, mais fluxo de telas | depois |
| `ai-programmer` | comportamento de inimigo e de chefe nas três fases: telegrafia, esquiva, recuo | sim |
| `qa-tester` | lacunas de cobertura e os `waitForTimeout` que ainda medem movimento com tempo de parede | depois |

`game/src/ui.js` foi tocado em 31 dos 50 commits: é gargalo compartilhado e **nunca** entra em
paralelo com outra tarefa.

## Ordem sugerida

1. **Prova de linha de base** — `bash game/tests/provar.sh` em segundo plano, para saber que o
   ponto de partida é verde antes de culpar qualquer coisa.
2. **Três em paralelo** — `level-designer` (progressão, as 6 perguntas acima, mais plataformas
   móveis), `art-director` (as proibições do art bible, mais os ciclos de animação pela Seção 9.4)
   e `ai-programmer` (comportamento de inimigo e chefe). Passe os prints de
   `production/evidencia/` e os caminhos dos assets.
3. **`technical-artist`** — `render3d.js` contra a Seção 4 e a regra dos três níveis da Seção 8,
   agora em r186, com a skill `threejs-debug-profiler`.
4. **Sequenciais** — `ux-designer`, depois `qa-tester`.
5. **As skills do framework**, que não precisam de agente: `/consistency-check` (documentos entre
   si), `/content-audit` (especificado contra implementado), `/asset-audit`.
6. **Juntar num laudo** com severidade, e **não consertar nada no mesmo passo**: primeiro a lista,
   depois a decisão do Pedro sobre o que entra.

## Duas coisas que já se sabe, para não achar de novo

- **Fonte de 4,3 px e botão de 31 px no iPhone** (Seção 7, já medido e já com tarefa no painel).
- **`waitForTimeout` usados como medição** nos smoke tests, fora dos três já consertados — a causa
  é o relógio do jogo andar a 0,58× do tempo real em máquina sem placa de vídeo.

## Duas decisões abertas, que não são da revisão

Cor e sentimento das **fases 4 e 5** são proposta do `art-director`, marcadas como tal na Seção 4.
A da fase 5 inverteria os três planos de valor e contraria a leitura por profundidade do
`design.md`: precisa de teste antes de virar decisão. Não trate como regra.

---

## O pedido, para colar numa sessão nova

> Dá um pente fino no Timtim. Leia `docs/pente-fino.md` primeiro e siga o que está ali.
>
> Minha questão principal: sinto que muita coisa foi feita no improviso, e que as fases 2 e 3 estão
> caóticas, sem progressão do jogador nem linha de crescimento. Quero recriá-las com os assets que
> já existem — mas antes quero o laudo que diga o que de fato está quebrado. O movimento do Timtim
> está bom, não mexe nele; o esquisito é o comportamento dos inimigos e chefes, as animações e as
> plataformas que se movem.
>
> Laudo com severidade, sem consertar nada ainda — eu decido o que entra.
