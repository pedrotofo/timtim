# Laudo do pente fino — Timtim, 28/11/2026

Revisão completa das três fases por **sete frentes**: progressão, arte, inimigos e chefes,
interface, áudio, render e textos, mais **evidência jogada** medida com o jogo rodando. A
**fase 1 é o controle**: ninguém reclamou dela, e ela é a régua.

Evidência: 60 capturas do jogo por dentro em três viewports (`production/fases*`), medição de
draw calls e textura por fase com instrumentação do contexto WebGL, e um bot que jogou as lutas
de chefe até o fim. **Nada foi consertado.** Este documento é a lista; o que entra é decisão do
Pedro.

---

## A resposta, em uma linha

**A fase 1 foi construída com uma regra. As fases 2 e 3 foram construídas por acumulação — e por
cima disso há um punhado de defeitos de uma a três linhas em lugares estruturais.**

As sete frentes trabalharam em paralelo, sem conversarem entre si, e convergiram. O próprio
código confessa a parte estrutural: `game.js:34` diz *"A fase 2 ensina uma única ação nova:
planar"* e ela entrega **seis**; `game.js:67` diz o mesmo da fase 3, que entrega **cinco**.

> As duas fases foram **escritas** com um currículo de uma frase e **montadas** com um currículo
> de seis.

Mas o achado que mais surpreendeu foi outro: **a maior parte da sensação de caos não vem de
desenho ruim.** Vem de cinco defeitos pequenos, em lugares que ninguém olhava.

---

## Parte 1 — Os defeitos de uma a três linhas

Estes vêm primeiro porque custam quase nada e explicam boa parte da queixa.

### 1.1 O fundo da fase 2 nunca recuou — `render3d.js:1379`

A linha tem **456 caracteres**. Um comentário `//` começa na coluna **175**. Os **281 caracteres
seguintes**, que incluem todo o `else if (ARR) { tint 0.74,0.6,0.52; hazeK 0.32 }`, estão dentro
do comentário. É código morto.

Medido no jogo: `tint [1,1,1]`, `hazeK 0`. Com `hazeK` zerado o shader do fundo não dessatura nem
mistura com a névoa, e o `bg/arraial-mata.jpg` vai para a tela **cru**. É um mato em contraluz: a
metade de baixo é escura, justamente onde fica o plano do jogo.

O comentário *"o fundo do Arraial recua: mais escuro, para o que se mexe aparecer"* descreve
exatamente o que nunca executou.

**O achado nº 1 do laudo de arte — "a fase 2 inverteu os três planos" — é um `//` mal colocado.**
Conserto: quebrar a linha em duas. Os valores já estão decididos no próprio código.

### 1.2 Todo o ensino do jogo some na primeira morte — `game.js:486`

`reset()` zera `warnedOnce`, `roarSeen`, `fruitSeen`, `peckSeen`, `bossSeen`.
**`TT.retry` não zera nenhum dos cinco.**

Quem morre e volta do checkpoint perde para sempre o aviso da debandada, o rótulo da fruta e a
única fala que ensina a vencer o chefe — exatamente no instante em que provou que precisava dela.

Pior: entrar na arena de novo dispara `rematch` (`game.js:733, 739`), e `rematch` **não emite** o
evento `cineEnd` de que a fala de estratégia depende. Morreu para o lobo-guará, voltou, entrou de
novo → **nenhuma instrução, nunca mais**.

### 1.3 Três mecânicas estreiam mudas — `ui.js:138-140`

`game.js` emite tutorial para `dance` (x>4380, **as tábuas da quadrilha**), `bounce` (x>4880) e
`blink` (x>6260). O objeto `TUT` de `ui.js` tem só `glide*`, `swirl` e `fire`. O guarda
`if (TUT[e.kind])` **descarta os três em silêncio**.

A mecânica mais perigosa da fase 2 — a tábua móvel estreando sobre o vão de 1380 px — tem uma
dica escrita no código que nunca chegou à tela. Idem as duas mecânicas novas da fase 3, incluindo
as estrelas que piscam, descritas como "o teste final antes do chefe".

Some-se o banner morto *"O grasnado desliga os redemoinhos!"* (`ui.js:163`), cuja mecânica
`updateCrow` nunca dispara.

### 1.4 A fase 3 anuncia galinha para revoada de corvos — `ui.js:142`, `main.js:10`

> **Correção de um erro deste laudo.** As versões anteriores afirmavam que a fase 3 usa a galinha
> do Arraial como inimigo comum, porque `R.foe = ARR ? 'galinha' : 'pigeon'` e `ARR = FASE >= 2`.
> **É falso.** `render3d.js:67-71` faz substituição de textura por fase — *"os corvos entram no
> lugar das galinhas"* —, e `galinha: ['corvo', 1.2478]` carrega `sprites/vg/corvo.png` sob a
> chave `galinha`. O nome é chave, não arte: **o jogador vê corvos.** O mesmo vale para a carta no
> lugar do bilhete e a tampinha no lugar da fruta. O erro foi meu e do laudo de arte, que
> julgaram pelo nome da variável sem seguir a tabela de substituição.

O que **é** real nesse item é só o som e o texto. O aviso de debandada é o texto fixo *"Galinhas em disparada!"* com `sfx('henPanic')` — som de
galinha — para o que o próprio `game.js:86` chama de "revoadas de corvos rasantes". O
`main.js:10` também liga `henBounce` e `henJump` a `henFlap`, que disparam na fase 3.

### 1.5 A fase 1 nunca teve borda acesa de piso — `render3d.js:424, 448`

`litEdge` é chamado em dois lugares, **os dois dentro de `if (ARR)`**, e `ARR = FASE >= 2`.
Medido na cena: 10 filetes na fase 2, 16 na fase 3, **zero na fase 1**.

> **Correção de um erro deste laudo:** a primeira versão dizia o inverso, repassando o laudo de
> arte, que julgou a olho por captura. A medição do render ganha. O que a fase 1 tem é uma **poça
> de luz menta** difusa de 46 px (`:445`), não um filete — a cor está certa pela Seção 4, a forma
> não.

Nas fases 2 e 3 o filete **existe e some por contraste**: é âmbar `0xffe0b0` sobre um mundo
laranja. E pela Seção 4 âmbar é "recompensa e luz física"; "aqui se pisa" é menta.

Mais: `:448` tem `if (VG && VG_PLAT[x]) continue;` **antes** da chamada a `litEdge`, então as seis
plataformas que são móveis do quadro (cama, cadeira, duas mesas, dois toldos) ficam sem filete e
sem halo.

---

## Parte 2 — O relógio da música dirige a física

Dois defeitos distintos, mesma raiz. `beatClock()` (`game.js:439`) devolve o relógio do **áudio**
quando a trilha do Arraial toca; `moveMovers` deriva `dx` por diferença entre quadros
(`game.js:442`); e `game.js:537` soma esse `dx` ao jogador em cima.

### 2.1 Solavanco da pausa — **medido: 195,3 px num passo de 1/240 s**

Na pausa `S.clock` congela (`game.js:512`) e `ctx.currentTime` não para. Medido: em 5 s de pausa,
`S.clock` andou 0,033 s e `beatTime()` andou 5,25 s.

| Pausa | A tábua andou num passo |
|---|---|
| 600 ms | −161,0 px |
| 1500 ms | +155,2 px |
| **3700 ms** | **−195,3 px** (de 200 possíveis) |

Na tábua vertical, +115,4 px. Independente de máquina — acontece em qualquer computador. E
`ui.js:35-36` pausam em `blur` e `visibilitychange`: basta trocar de aba.

> **Correção de um erro deste laudo:** a primeira versão dizia que isso derruba o jogador no vão.
> **Não derruba.** Com o Timtim de pé na tábua, `p.x += p.on.dx` o move exatamente o mesmo tanto,
> e nas 15 rodadas medidas ele continuou em cima, com 3 corações. É teleporte lateral de 195 px —
> desorientador, não letal.

### 2.2 As tábuas correm fora do relógio do jogo — **1,55× medido, picos de 16×**

Sem pausa nenhuma, em 2400 passos: `S.clock` andou 0,65× o tempo real; `beatTime()` andou 1,00×.
As tábuas da quadrilha andam **55% mais rápido** do que o `ritmo-das-fases.md` supõe, com
solavancos de até **16,16× a velocidade de projeto** quando o laço engasga.

O vão de 1380 px — já grave por estrear a mecânica sobre o buraco mais fundo do jogo — é
atravessado por plataformas cuja velocidade **depende da máquina do jogador**.

**Política proposta, do laudo de áudio:** *nenhuma mecânica deste jogo pode depender de ouvir.* O
som confirma e antecipa; quem decide se dá para pisar é a imagem. O relógio da música pode
enfeitar a física, nunca ser a física.

---

## Parte 3 — O que é estrutural e pede redesenho

Estes três **não** são conserto de linha. São o que o `level-design-document` precisa resolver.

### 3.1 A fase 2 começa no teto

Envelope de tensão 9-6-10-9: o **segundo** trecho de 800 px já marca 9 de 10. A fase 1 sobe
4→6→8→8. A fase 2 são quatro set pieces separados por chão vazio, com uma plataforma fixa a cada
1388 px — **quatro vezes mais rala** que a fase 1 (337 px).

E os checkpoints estão invertidos: 2840 px de intervalo no trecho mais difícil, 440 px no mais
fácil. Custo de repetição no pico: **47:1** entre o pior e o melhor, contra 2,5:1 na fase 1.

A aula do planar é seguida 700 px depois por um vão de 630 px que pede pulo duplo **mais** planar
valendo coração, sem um único uso de planar sem risco entre os dois: **ensina → cobra, sem
praticar**.

### 3.2 A fase 3 não exige nada do que ensina

Cinco mecânicas novas (redemoinho, girassol móvel, toldo que quica, estrela que pisca, argola) e
**nenhuma é exigida no caminho principal**. Os seis vãos medem 200–250 px e se atravessam com o
repertório da fase 1. Variação entre o primeiro e o último vão: **50 px**.

As estrelas que piscam, "o teste final", ficam sobre um vão de 200 px que se pula direto. O pico
da fase está em x=4000 — **no meio** — e o chefe vem na descida.

### 3.3 Os chefes não pedem a ação da fase, e a escada desce

- O **Furtão** (fase 1) é o mais difícil de abrir: janela só quando a bolinha chega, a cada 5–7 s.
- O **lobo-guará** (fase 2) dá janela grátis depois de **todo** ataque; a luta acaba em 3 ataques.
- O **Corvo-Borrão** (fase 3) tem 2 ataques contra 3 dos outros.

E o lobo-guará escolhe o ataque por **sorteio puro** (`game.js:320`), sem anti-repetição e sem
olhar a distância — enquanto o Furtão da fase 1 **já filtra o último ataque** (`game.js:811`). O
padrão correto existe no projeto, numa fase só.

No último coração há 45% de chance de emendar bote com corrida usando **0,30 s de aviso**,
pousando onde o jogador estava.

> **Correção de um erro deste laudo:** a primeira versão levantou a hipótese de o Corvo-Borrão
> ser invencível, por a fase 3 não ter ar quente. **Ele é vencível.** Um bot venceu duas vezes, 3
> golpes em 3 janelas, **com e sem planar** — o dorso dele fica a 110 px do chão e o pulo cheio
> sobe 162 px. O que está errado é o **texto**: `FOXTXT.egg` manda planar, e planar não dá altura
> nenhuma. A instrução certa existe em `ui.js:289` — mas só aparece **depois de perder**.

---

## Parte 4 — Arte, contra as 80 proibições do art bible

**Fase 1 cumpre a regra travada.** Fundo claro e enevoado, primeiro plano quase preto, Timtim a
mancha mais clara.

**Fase 3 colapsou os três planos em um.** O fundo é claro, mas com contraste e saturação cheios e
objetos legíveis, então **não recua**. Medido: `hazeK` 0,16 na fase 3 contra 0,32 na fase 2 — a
dessaturação efetiva é de 8%, quase invisível sobre uma pintura de Van Gogh. **É parâmetro, não
asset:** subir `hazeK` e reavaliar. O valor novo é decisão do `art-director`.

Outros graves confirmados:

- **A fase 3 troca de paleta no meio** — ouro de campo de trigo até x≈4000, azul-noite depois.
- **O Furtão está cinza-azulado com coleira de espinhos** nos `.webp`, não marrom.
- **A crina do lobo-guará é a faixa preta** — a parte mais escura do sprite. O ponto fraco é
  invisível.
- **Risco real de confundir Timtim com Zara**: os dois pretos e brancos, do mesmo porte, e o
  Timtim tem as duas orelhas triangulares para cima que a Seção 3 reservou para "amigo".
- **Teto de três formas-herói estourado**: doze em `fase2-08`, treze em `fase3-03`.
- **Vermelho no cenário** (proibido, porque vermelho é vida e dano): toldo da barraca em cinco
  capturas da fase 2, cobertor da cama na fase 3.
- **Moldura de museu** na fase 3, proibida pela Seção 9.2.
- **A fase 3 é a fase 2 com outro papel de parede**: mesmo kit de piso, mesma mesa de cavalete, e
  postes de rua da fase 1 espalhados pela fase 3.

### Ciclos de animação — medido, e mais brando do que parecia

| Folha | Deriva de **escala** | Oscilação da caixa |
|---|---|---|
| `timtim-parado` | **4,81%** (3,85 px) | 12,17% — a diferença é **pose**, não escala |
| `timtim-pulo` | **3,44%** (2,65 px) | 4,37% |
| `elvis-parado`, `zara-parado`, `corvo-voa` | deriva visível a olho, não medida | reprovados pelo `art-director` |

> **Correção:** o `art-director` viu 12% de oscilação no `timtim-parado` e suspeitou de deriva de
> vídeo de IA. A medição separa as duas coisas: a escala real varia 4,81%, e o que oscila é a
> silhueta mudando de pose (a altura cai enquanto a largura sobe — sinal inequívoco de pose). As
> folhas do Timtim estão **bem melhores** que as três reprovadas.

---

## Parte 5 — Interface

- **Não existe nenhuma regra de orientação retrato.** Nada manda girar o aparelho. O manifest pede
  `landscape` e o `ui.js:182` trava a orientação, mas **os dois só valem depois da tela cheia, e
  tela cheia não existe no Safari do iPhone**. Quem abre o link no iPhone vê o jogo numa faixa de
  26% da altura, com os botões por cima — e não tem como saber que existe configuração melhor.
  **Girar não muda composição, só multiplica tudo por 1,78: o estado bom já existe e o jogo não
  conta ao jogador.**
- **O defeito de fonte não é só do retrato.** No **deitado** — a orientação que o jogo pede —
  nove estilos ficam abaixo de 12 px: dica de controles 9,0 px, textos da estante 7,6 px, fala do
  chefe 11,8 px.
- **Seis alvos de toque falham o piso de 44 px**, não um. Os dois piores: ❚❚ e ♪ a **14,8 px em
  pé**, e são a única saída de uma fase no celular.
- **`viewport-fit=cover` sem um único `env(safe-area-inset-*)`** no projeto. No iPhone deitado o
  notch pode cobrir o botão ◀ ou os corações. **Nenhuma das 60 capturas mostra recorte de
  sistema** — esse caso nunca foi visto.
- **"Jogar" não joga**: abre o mapa, que só desenha o nome da fase e **não tem botão de voltar no
  toque**.
- **A estratégia do chefe só existe num balão de 11,8 px, por 2,6 s, durante a luta.**
- **A dica de controles aparece uma vez, na capa** — e quem vai para a fase 2 pelo "Próxima fase"
  **não passa pela capa**.
- **O jogo não tem fecho**: vencida a fase 3, o jogador fica no mapa entre duas faixas "EM BREVE".

### A fila de banners explica o aviso atrasado

`showBanner` segura 2700 ms, `noteOpen` 4800 ms, e a fila só é consultada a cada 250 ms. A
310 px/s um aviso chega **até 840 px depois do gatilho — ou 2300 px se uma carta estiver aberta**.
É a explicação medida do "aviso da fogueira 974 px depois da fogueira": o gatilho em x=3130 está
**certo**; o banner ficou na fila atrás de "Galinhas em disparada!".

### O vão de 1150, medido no iPhone deitado

Os botões **não** cobrem a beirada (117 px de folga). O problema é outro e vale nos **dois**
viewports: **a plataforma de pouso em x=1670 está fora do quadro** no momento da decisão
(fx=1,081 no celular, 1,016 no desktop). E a beirada não tem borda acesa: lê como "o chão
continua, só mais escuro". **Não é defeito de celular.**

---

## Parte 6 — Render e desempenho

Medições reais (instrumentação do contexto WebGL, 8 pontos por fase, desktop e celular):

| | Fase 1 | Fase 2 | Fase 3 |
|---|---|---|---|
| Draw calls (pico) | **219** | 217 | 199 |
| Triângulos (pico) | 939 | 2 462 | 2 033 |
| Textura na GPU, desktop | 349,0 MB | **390,2 MB** | 185,8 MB |
| Textura na GPU, celular | 265,5 MB | 239,2 MB | 175,0 MB |

**A fase 2 custa 2,1× a fase 3 em textura** para o mesmo tipo de conteúdo. E o comentário do
`:51` ("passavam de 380 MB e o iPhone começava a jogar imagens fora") **ainda é verdade no desktop
da fase 2**.

O gargalo não é vértice nem CPU: é **preenchimento com sobreposição e memória de textura**. Na
fase 2, 823 malhas, **591 transparentes**, **470 aditivas**, e **646 materiais únicos** — cada
`glowMat()` cria material novo por instância, então nada batcha.

### O nível 0 não é "menos efeito", é outra gradação

`if (GL2 && R.quality > 0)` desliga a cadeia de pós **inteira**. Dentro dela moram `expo`
(tonemap), `heroK` (a poça de luz do herói), `shade` (as sombras roxas), `flash` (o acerto) e
`gray` (o cinza da derrota). **Três das cinco regras de contraste do `design.md` existem só
dentro desse passe.** O celular começa a um degrau disso.

**O pior cruzamento do laudo:** a única pista de borda da fase 1 é a poça menta, e ela está em
`pulses` sem `slow`, **que o nível 0 esconde**. No aparelho mais fraco, as plataformas da fase 1
ficam sem pista alguma.

### Os dois orçamentos que faltavam

- **`performance.draw_call_limit: 260`** — pico medido 219, 19% de folga.
- **`performance.memory_ceiling_mb: 320`** — **declara uma violação que já existe, de propósito**.
  A fase 2 no desktop está em 390 MB. Um teto de 400 abençoaria o problema.

### Código morto encontrado

- `:997` — `rim.visible = false` fixo, depois de o quadro recalcular geometria, mapa, posição,
  escala e opacidade. A regra 5 de Ori ("quem se mexe tem contorno de luz fria") está desligada.
- `:741-745` — `actorRims` nunca recebe nada; `updateRims()` itera array vazio todo quadro.
- `renderer.info` nunca é lido. Com `performance.enforce: block`, não há contador em cena.

---

## Parte 7 — Áudio

- **O dano não tem prioridade na mixagem.** `hurt` está na camada `heroi` sem reserva: um
  `cookie` ou um `jump` posterior **o expulsa**. Alvo −20 dB, com a música a −21 — 1 dB acima. E
  `bonk` (o chefe batendo na parede, **inofensivo**) está a −19, mais alto e em camada
  privilegiada. A Seção 4 cobra marca sonora própria para o dano, por escrito.
- **O redemoinho não tem som de saída.** `swirlIn` e `swirlOut` são **o mesmo arquivo** com
  intervalo mínimo de 0,4 s — e a soltura pede 72 ms de precisão. A ação mais exigente do jogo é
  a única sem confirmação sonora.
- **Capa, card e exploração tocam o mesmo arquivo.** Seis dos treze estados da Seção 2 não têm
  trilha nenhuma.
- **As duas trilhas da fase são baixadas e decodificadas no primeiro toque** — derivação: só
  `arraial.mp3` ocupa ~60 MB de PCM em RAM.
- **A fase 3 declara `BPM: 84` sem entrada em `LOOPS`**, então o pulso visual bate contra o
  relógio da fase, não contra a música. "O jogo pulsa na batida" só é verdade na fase 2.
- **Risco de licença, não de áudio:** o `CREDITOS.md` tem três linhas com ⚠️ em aberto — as
  trilhas das fases 2 e 3, as duas do Suno, e a locução.

### Correção à revisão de progressão

Ela concluiu que a previsibilidade das tábuas depende do som. **Não depende, e nunca dependeu:**
a música diz onde está o **compasso**, não onde está **aquela** tábua — cada uma tem fase própria
(0, π, π/2, 0). E o pulso visual é global e **quatro vezes mais rápido** que o ciclo que deveria
antecipar. As tábuas nunca foram previsíveis, nem pelo olho nem pelo ouvido.

---

## O que fazer, em ordem

**Grupo A — uma a três linhas, independentes entre si, nenhuma depende do documento de design:**

1. Quebrar `render3d.js:1379` em duas linhas. *(o fundo da fase 2 volta a recuar)*
2. Zerar os cinco sinalizadores didáticos em `TT.retry` e repetir a estratégia no `rematch`.
3. Escrever os três textos que faltam (`dance`, `bounce`, `blink`) e instruir a debandada por fase.
4. Trocar `henPanic`→`crowCaw` e `henFlap`→`crowWings` na fase 3. *(A arte do inimigo já estava
   certa — ver a correção em 1.4.)*
5. Dar faixa própria aos avisos de mecânica (`now: true`), para não ficarem na fila.
6. Corrigir o texto do Corvo-Borrão: a instrução certa já existe no `loseText`.
7. Camada `vida` protegida para o dano; `bonk` para −22 dB.
8. `swirlOut` com entrada própria, para a soltura do redemoinho ter som.

**Grupo B — parâmetro, pede decisão de direção de arte:**

9. Subir `hazeK` da fase 3 (0,16 → ~0,26–0,32) e reavaliar.
10. Acrescentar `litEdge` à fase 1 e trocar a cor do filete para menta nas três fases.
11. Mover o `continue` de `:448` para **depois** do `litEdge`, para as seis plataformas-móveis da
    fase 3 ganharem borda.
12. Fechar a cadeia de pós no nível 0 em vez de desligá-la (rodar só o `compMat` com `dof=0`,
    `bloomK=0`): mais barato que o nível 1 de hoje, e salva `expo`, `heroK`, `shade` e `flash`.
13. Regerar o Furtão em marrom, sem coleira de espinhos. Clarear a crina do lobo-guará.

**Grupo C — interface, mesma passada, mesmo dono:**

14. Tela de "gire o aparelho" em retrato, e caminho visível para tela cheia no iPhone.
15. `max(12px, …)` nos ~12 estilos abaixo do piso, e 44 px nos seis alvos que falham.
16. `env(safe-area-inset-*)` de verdade.
17. Repetir os controles na pausa; mover a estratégia do chefe do balão para o banner.
18. Dizer ao jogador o que fazer no mapa, e dar botão de voltar no toque.

**Grupo D — relógio, pede cuidado:**

19. Fazer `beatClock()` ser contínuo e monotônico em qualquer troca de fonte, e declarar que a
    física não depende do áudio.

**Grupo E — estrutural, só depois do `level-design-document`:**

20. Desentortar os checkpoints da fase 2.
21. Dar à fase 2 uma tábua móvel sobre chão sólido antes de 4500.
22. Fazer a fase 3 exigir o que ensina: alargar dois vãos para além do pulo duplo.
23. Trocar o sorteio de ataque do lobo-guará por escolha de estado e distância; matar a emenda de
    0,30 s.
24. Separar na tela `hurt`/`bonk`, `wind`/`tired` e `dodge`/bote.
25. Esvaziar a zona de leitura das fases 2 e 3.
26. Levar o fio do Furtão aos três cards, e dar fecho à fase 3.

**Corrigir junto, custo quase zero:** a conta de tensão de `ritmo-das-fases.md`, para espalhar
cada perigo pelos trechos que ele **ocupa**. Enquanto a tabela disser que o interior do vão de
1380 px é descanso, nenhuma revisão enxerga o problema.

---

## O que o `level-design-document` precisa decidir

1. **A frase da fase**: a única ação que ela ensina, e o que entra como variação.
2. **Os três x de cada mecânica**: estreia segura, prática sem risco, e a partir de onde vale
   coração.
3. **O que a fase pressupõe da anterior**, por escrito.
4. **Alvo de tamanho de vão por fase**, crescente, com mínimo e máximo.
5. **Distância máxima de repetição num pico.** A fase 1 pratica ~1500 px sem nunca ter declarado.
6. **Onde mora o conteúdo opcional em relação ao risco.**
7. **Antecedência de aviso**, medida em px **e** no tempo de leitura do banner (2700 ms × 310 px/s
   ≈ **840 px**, contra os 120–320 px de hoje).
8. **Onde fica o pico da fase**, e o que vem antes e depois.
9. **Se a mecânica da fase é exigida pelo chefe**, e em que x foi cobrada antes da arena.
10. **O conjunto próprio de marcos da fase, com consequência de rota.**
11. **Regra para plataforma móvel**: eixo, amplitude contra a largura, e uma regra única de fase.
12. **Quanta precisão de temporização o jogo pode pedir.** O redemoinho pede **72 ms**; as folgas
    do próprio jogo são 100 ms (borda) e 120 ms (buffer).

---

## O que ficou sem resposta

1. **O portão de áudio entre fases no iPhone.** Não se conseguiu forçar o `AudioContext`
   suspenso depois do `reload`; a pergunta não foi exercitada. A captura `q6-2` mostra que, com o
   contexto já liberado, o card monta normal e o portão vira um rótulo discreto no canto.
2. **Se a dica do ar quente chega atrasada em partida real** (não só no teleporte).
3. **Contraste medido da beirada do vão de 1150** contra a fase 1 como controle.
4. **Quantas tentativas uma criança leva** no Corvo-Borrão. O bot tem reflexo perfeito.
5. **O piso de 45 fps** — não verificável neste contêiner, que roda WebGL por software.
6. **Por que o Timtim não aparece** num print de desktop embora `R.toScreen` o coloque em quadro.

---

## Onde paramos (28/11/2026)

Aplicado e empurrado nos dois branches:

| Grupo | O quê | Commit |
|---|---|---|
| **A** | 8 consertos de 1 a 3 linhas | `cdad4ac` |
| **C** | interface no celular (itens 14 a 18) | `4def2f8` |
| **B** | borda, névoa e nível de emergência (itens 9 a 12) | `e89468a` |
| **D** | o relógio do áudio (item 19) | *este commit* |

**Falta do laudo:** Grupo **E** (itens 20 a 26, só depois do `level-design-document`) e o item
**13** do Grupo B (regerar o Furtão e clarear a crina — gasta crédito, pede o "pode" do Pedro).

### O que o Grupo D fechou (28/11/2026)

A física não depende mais de ouvir. `moveMovers` anda em `S.clock`; `TT.beatClock()` sobrou só como
enfeite e virou contínuo e monotónico (descarta qualquer salto de fonte). A política está declarada
em `game/docs/design.md` ("O som não é física") e cobrada em `.claude/rules/timtim-web.md`.

A regressão é `game/tests/relogio.js`, que entra no `provar.js`. Ela falsifica a fonte de som de
propósito (relógio de música a 10×, com saltos para trás), porque neste contêiner o áudio pode nem
tocar e o teste passaria contra o próprio defeito. **Vista falhar contra o código sem o conserto:**
211 px de teleporte num só passo (o laudo media 195,3) e 82,6 px de erro de posição sem pausa
nenhuma. Com o conserto: 1,16 px por passo, teto de 1,96; erro de posição 0,00 px.

As métricas confirmam de fora: o vão de 1380 px agora mede **21%** do alcance pelas tábuas móveis,
exatamente o que o `ritmo-das-fases.md` dizia e não era verdade.

**O que isso custou de propósito:** as tábuas não estão mais travadas no compasso da trilha. Pelo
laudo de áudio elas nunca foram previsíveis pelo ouvido (cada uma tem fase própria e o pulso visual
é 4× mais rápido que o ciclo), então o que se perde é a intenção escrita no `audio.js`, não um
efeito que o jogador sentia. O pulso visual (lanternas, brilho) continua na batida.

### Três coisas achadas durante o Grupo B, ainda abertas

1. **Item 13 não foi feito** (regerar o Furtão em marrom sem coleira de espinhos, clarear a crina do
   lobo-guará). É gerar sprite novo, e gerar imagem gasta crédito do Pedro: **pede o "pode" dele**.
2. **A corrida do Timtim está 10% maior do que o fato não-negociável manda.** `CLAUDE.md` e
   `design.md` dizem que a altura da corrida é **82**; `render3d.js`, em `R.frame`, usa **88**
   (`name = 'tintim-run'; h = 88`). Não foi mexido: pode ter sido proposital quando a corrida virou
   tira desenhada de 8 quadros, e "mesmo tamanho em todas as poses" é fato não-negociável — quem
   decide é o Pedro, depois de olhar o histórico. As outras batem (parado 80, pulo 77, queda 82,
   farejando 69); `win` 92 e `glide` 78 também não estão na tabela.
3. **A borda da fase 3 ficou discreta de propósito** (linha de contato escura, não filete aceso,
   porque numa cena clara a luz aditiva satura em branco e vira um risco em cima da pintura).
   Está esperando o Pedro dizer se ficou discreta demais. Mexe em `litEdge`, no ramo `if (VG)`.

### Duas perguntas antigas, ainda sem resposta do Pedro

- As três linhas ⚠️ de `CREDITOS.md` (música e voz geradas por IA — risco de licença se o jogo for
  mostrado em público).
- Encurtar `arraial.mp3` de 64 para 32 compassos.

### Armadilhas que já custaram tempo, para não cair de novo

- **Medir diferença de print entre duas versões não funciona aqui.** A cena anima (névoa,
  vaga-lumes, pincelada), então `comparar-prints.js` acusa 60–79% dos pixels mesmo onde quase nada
  mudou. Para julgar arte, olhe as imagens.
- **Esperar `R.ready` não quer dizer que a fase começou** — na tela de título ele já é verdadeiro.
  Quem sabe entrar na fase é `game/tests/capturar-fases.js`.
- **Os testes rodam com `q=0`**, então mudança no nível 0 do render muda o tempo dos testes.
- **O relógio do jogo corre a cerca de metade do tempo de parede** nesta máquina (WebGL por
  software). Orçamento de espera para cinemática é `CINE`, nunca um número à mão.
