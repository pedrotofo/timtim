# Laudo do pente fino — Timtim, 28/11/2026

Revisão das três fases por três agentes em paralelo (`level-designer`, `art-director`,
`ai-programmer`), mais leitura própria e medição no jogo rodando. A **fase 1 é o controle**:
ninguém reclamou dela, e ela é a régua contra a qual as outras duas foram medidas.

Evidência: 24 capturas do jogo por dentro em desktop (`production/fases/`), 24 no celular em pé
(`production/fases-celular/`), 12 no celular deitado (`production/fases-deitado/`), geradas por
`node game/tests/capturar-fases.js`. **Nada foi consertado.** Este documento é a lista; o que
entra é decisão do Pedro.

---

## A resposta, em uma linha

**A fase 1 foi construída com uma regra. As fases 2 e 3 foram construídas por acumulação.**

As três revisões, feitas em paralelo e sem conversarem entre si, chegaram à mesma conclusão por
caminhos diferentes — progressão, arte e comportamento. É o que torna o diagnóstico confiável.

E o próprio código confessa. `game.js:34` diz *"A fase 2 ensina uma única ação nova: planar"*.
`game.js:67` diz *"ensina UMA ação nova: o redemoinho"*. A fase 2 entrega **seis** mecânicas
novas; a fase 3, **cinco**.

> As duas fases foram **escritas** com um currículo de uma frase no comentário e **montadas**
> com um currículo de seis.

É também a explicação da refação: sem documento que dissesse o que cada fase ensina e quanto ela
pode custar, cada sessão acrescentou sem orçamento, e o resultado teve de ser remendado — metade
dos 50 commits de 24 e 25/11.

---

## Por que a fase 1 funciona: três números

1. **Ordem de primeira aparição.** Cada perigo estreia sozinho, sobre chão sólido, com espaço
   reservado. O trecho 1400–2000 existe **só** para o primeiro pombo, e foi comprado empurrando a
   fase inteira 600 px para a direita (`game.js:26`). Alguém gastou 600 px de fase para dar a um
   pombo um lugar vazio. É a decisão mais cara e mais certa do projeto.
2. **Textura constante.** Uma plataforma a cada 337 px, um pombo a cada 1049 px. **Nunca há
   1000 px de nada.** Na fase 2 há uma plataforma a cada 1388 px — quatro vezes mais rala.
3. **O pico fica para o fim, e todo pico custa o mesmo.** O envelope de tensão sobe 4 → 6 → 8 → 8,
   e o custo de repetição nos picos é 600/1440/1520 px — razão de 2,5 para 1. Na fase 2 essa razão
   é de **47 para 1**; na fase 3, **41 para 1**.

E o que falta **nas três, inclusive na 1**: em lugar nenhum está escrito "esta fase ensina X". A
fase 1 acerta por ordem de apresentação, não por currículo — e por isso o acerto **não se
transferiu** para quem montou as fases 2 e 3 em dois dias.

---

## GRAVE — progressão

| Onde | O quê |
|---|---|
| Fase 2, x=4500–5880 | A primeira plataforma móvel do jogo estreia **sobre o vão mais fundo da fase** (1380 px). Não existe uma única tábua móvel sobre chão sólido em fase nenhuma. O jogador aprende a mecânica pagando coração, repetindo até 2820 px |
| Fase 2, x=1150–3000 | A aula do planar é seguida 700 px depois por um vão de 630 px que pede pulo duplo **mais** planar valendo coração. Entre os dois não há um único uso de planar sem risco: **ensina → cobra, sem praticar** |
| Fase 2, x=3060→5900 | Maior intervalo de checkpoint da fase (2840 px) cobre o trecho mais difícil; os dois checkpoints mais próximos (440 px) ficam no mais fácil. **A rede de segurança está onde ninguém cai** |
| Fase 2, envelope 9-6-10-9 | **Começa no teto.** O segundo trecho de 800 px já marca 9 de 10 |
| Fase 3, x=0–6940 | **Nenhuma** das cinco mecânicas novas é exigida no caminho principal. Os seis vãos medem 200–250 px e se atravessam com o repertório da fase 1 |
| Fase 3, x=1300–6600 | O terreno **não cresce**: 50 px de variação entre o primeiro e o último vão (200 → 250). A fase 1 vai de 120 a 230; a 2, de 140 a 1380 |
| Fase 3, x=6420 | As estrelas que piscam, descritas como "o teste final antes do chefe", ficam sobre um vão de 200 px que se pula direto. **O exame final é opcional** |
| Fase 3, picos 9-9-11-8 | A fase **descarrega no meio** (x=4000) e entrega o chefe na descida |
| Método | `ritmo-das-fases.md` atribui cada perigo ao trecho onde ele **começa**. Por isso o vão de 1380 px da fase 2 aparece como "descanso" nos trechos 4800 e 5600 — onde o jogador está no ar sobre o buraco. **O único instrumento de ritmo da produção marca descanso exatamente onde está a demanda mais longa do jogo** |

---

## GRAVE — arte

**Fase 1 cumpre a regra travada do art bible.** Fundo claro e enevoado, primeiro plano quase
preto, Timtim a mancha mais clara, borda acesa menta visível nas oito capturas.

**As duas outras quebram a mesma regra de formas opostas:**

- **Fase 2 inverteu os três planos.** O fundo é parede de troncos marrom-escuros, **mais escura
  que o plano do jogo**; não há moldura escura em cima; e o mais claro da tela é sempre fogo,
  nunca o herói. A Seção 9.1 chama isso de "o erro da maioria dos imitadores" e diz que é o item
  que vale mais que todos: *o fundo é claro e desbotado, não escuro*.
- **Fase 3 colapsou os três planos em um.** O fundo é claro — mas com contraste e saturação
  cheios e objetos legíveis (girassóis, casario, ciprestes), então **não recua**. Em `fase3-03` o
  fundo tem mais contraste local que o plano do jogo.

E as duas somam a mesma falta operacional:

> **Não existe borda acesa em nenhuma plataforma da fase 2 nem da fase 3.** O filete menta é
> elemento de jogabilidade, não enfeite (Seção 1.2-C): ele responde "posso pisar aí?". A fase 1
> tem nas oito capturas; as outras duas não têm em nenhuma.

Outros graves de arte:

- **A fase 3 troca de paleta no meio do caminho** — ouro de campo de trigo até x≈4000, azul-noite
  de *Noite Estrelada* depois. É a regra que o Pedro travou em 24/11 quebrada dentro de uma fase.
- **O Furtão está cinza-azulado com coleira de espinhos** nos `.webp`, não marrom. É o fato
  não-negociável mais repetido do projeto, errado no arquivo de origem.
- **A crina do lobo-guará é a faixa preta** — a parte mais escura do sprite. O ponto fraco, que
  deveria ser o único ponto claro nele, é invisível.
- **Risco real de confundir Timtim com Zara**: os dois são pretos e brancos, do mesmo porte, e o
  Timtim tem as duas orelhas triangulares para cima que a Seção 3 reservou para "amigo".
- **Teto de três formas-herói estourado em toda parte**: doze em `fase2-08`, treze em `fase3-03`.
- **Vermelho no cenário** (proibido pela Seção 4, porque vermelho é vida e dano): toldo listrado
  da barraca em cinco capturas da fase 2, cobertor da cama na fase 3.
- **Moldura de museu** na fase 3 (`fase3-01` e `fase3-05`), explicitamente proibida pela Seção 9.2.
- **A fase 3 é a fase 2 com outro papel de parede**: mesmo kit de piso (terra escalonada com
  filete de grama), mesma mesa de cavalete, e postes de rua da fase 1 espalhados pela fase 3.
- **Deriva de escala nos ciclos** de `elvis-parado`, `zara-parado` e `corvo-voa`: o animal encolhe
  e sobe da linha do chão ao longo da folha. É a deriva típica de vídeo de IA que a Seção 9.4
  manda cobrar.

---

## GRAVE — comportamento

**A fase 2 sorteia; a fase 1 decide.** É a causa mecânica do caos:

```js
// game.js:320 — lobo-guará
f.atk = (ph>=1 && !roarCd && rand<0.35 ? 'roar' : rand<0.55 ? 'pounce' : 'dash')
```

Sorteio puro: sem anti-repetição, sem olhar a distância. Três botes seguidos têm 17% de chance.
**E o Furtão da fase 1 já faz certo** (`game.js:811`): filtra o último ataque e o repertório
cresce por rodada. O padrão correto já existe no projeto, numa fase só.

- **Golpe inevitável**: no último coração, 45% de chance de emendar bote com corrida usando
  **0,30 s de aviso**, pousando onde o jogador estava (`game.js:333`).
- **A escada de dificuldade desce.** O Furtão é o chefe **mais difícil de abrir** (janela só
  quando a bolinha chega, a cada 5–7 s); o lobo-guará dá janela grátis depois de **todo** ataque e
  a luta acaba em 3 ataques; o corvo tem 2 ataques contra 3 dos outros.
- **Telegrafia falsa**: a esquiva do lobo é desenhada com a pose **do bote** (`render3d.js:1135`).
  O jogador recua de um movimento inofensivo.
- **Dois estados idênticos com consequências opostas**: `hurt` e `bonk` usam a mesma pose e as
  mesmas estrelinhas, mas num deles o pisão vale coração e no outro não.
- **Mecânica morta na fase 3**: o banner *"O grasnado desliga os redemoinhos!"* existe em
  `ui.js:163`, mas `updateCrow` nunca o dispara.
- **Nenhum chefe pede a ação da sua fase.** A arena do corvo não tem redemoinho nenhum.
- **A debandada não se resolve.** Pisar só quica; encostar de lado machuca; a galinha nunca sai.
  Não existe ação correta além de estar no ar na hora certa, e isso nunca é ensinado.

---

## Achados próprios, confirmados em código

1. **A fase 3 usa a galinha do Arraial como inimigo comum.** `render3d.js:746` faz
   `R.foe = ARR ? 'galinha' : 'pigeon'`, e `ARR = C.FASE >= 2`. Dentro do quadro de Van Gogh você
   enfrenta galinhas caipiras de chapéu de palha.
2. **A fase 3 anuncia "Galinhas em disparada!" com som de galinha** (`ui.js:142`) para o que o
   próprio código da fase 3 chama de "revoadas de corvos rasantes" (`game.js:86`).
3. **As revoadas de corvos usam o tipo das galinhas**: correm no chão e pulam buraco com gravidade
   de galinha, desenhadas como corvo voando.
4. **No celular em pé**, antes da tela cheia, o jogo é uma faixa de um terço da altura com os
   botões de toque por cima da área de jogo. O manifest pede `landscape` e o `ui.js:182` trava a
   orientação na tela cheia — então **é o que se vê ao abrir o link, não a experiência instalada**.

---

## Uma incerteza que eu resolvi, e que vira achado

O `art-director` disse não conseguir localizar o Timtim em várias capturas e pediu confirmação
antes de cobrar. Medi a posição dele na tela em todos os 24 pontos:

- **Fase 1:** em quadro em 7 de 8.
- **Fase 2:** **fora de quadro em 4 de 8** (a câmera não tinha alcançado o teleporte). Os achados
  de arte dessas quatro capturas valem para o cenário, não para o herói.
- **Fase 3:** **em quadro nas 8** — e o `art-director` não conseguiu achá-lo em cinco delas.

Essa última linha é o achado: **se ele está em quadro e um olho treinado não o encontra, a regra
travada da Seção 1 não se cumpre.** É a confirmação mais direta do problema da fase 3.

---

## Correção num documento meu

A Seção 3 do art bible afirma que o chefe "é a única coisa que não se resolve por cima", mas os
três chefes se resolvem exclusivamente por cima, e o `design.md` decidiu isso em 24/11 ("cair por
cima conta como pisão"). **A decisão datada manda; a linha do art bible é que está errada**, e eu
a escrevi ontem. Corrigir.

---

## O que fazer, em ordem

As três revisões concordam na ordem, e ela vai do mais barato ao mais caro:

1. **Devolver a borda acesa menta ao topo de toda plataforma das fases 2 e 3.** Um elemento, duas
   fases, e é elemento de jogabilidade. Hoje o jogador decide o pulo sem a pista que a fase 1 dá.
2. **Inverter os três planos da fase 2**: clarear e dessaturar o fundo, devolver a moldura quase
   preta. Destrava sozinho metade dos graves de arte da fase 2 sem mexer em prop nenhum — é
   parâmetro de render e uma imagem regraduada.
3. **Desentortar os checkpoints da fase 2**: mover o de 5900 para ~5100. Corta o custo de
   repetição do pico de 2820 para ~1400 px. É uma linha.
4. **Regerar o Furtão em marrom, sem coleira de espinhos.** Um asset, e é o fato não-negociável
   mais citado do projeto.
5. **Trocar o sorteio de ataque do lobo-guará por escolha de estado e distância, com
   anti-repetição**, e matar a emenda de 0,30 s. O padrão a copiar já está em `game.js:811`.
6. **Separar na tela os estados que colidem**: `hurt`/`bonk`, `wind`/`tired`, `dodge`/bote.
7. **Dar à fase 2 uma tábua móvel sobre chão sólido antes de 4500.** É o equivalente ao que a
   fase 1 fez com o primeiro pombo.
8. **Esvaziar a zona de leitura das fases 2 e 3.** O mais caro e o único que não é parâmetro: é
   repor prop por prop. Dá para fazer em fatias, começando pelos props colados em borda de vão.
9. **Fazer a fase 3 exigir o que ela ensina**: alargar dois vãos para além do pulo duplo. Depois
   do `level-design-document` da fase 3 estar escrito.

**Corrigir junto, custo quase zero:** a conta de tensão de `ritmo-das-fases.md`, para espalhar
cada perigo pelos trechos que ele **ocupa**. Enquanto a tabela disser que o interior do vão de
1380 px é descanso, nenhuma revisão enxerga o problema.

---

## O que o `level-design-document` precisa decidir, e hoje não está decidido em lugar nenhum

1. **A frase da fase**: qual é a única ação que ela ensina, e o que entra como variação em vez de
   mecânica nova.
2. **Os três x de cada mecânica**: onde estreia em segurança, onde se pratica sem risco, e a
   partir de que x vale coração. Hoje só o planar tem o primeiro.
3. **O que a fase pressupõe da anterior**, por escrito.
4. **Alvo de tamanho de vão por fase**, crescente, com mínimo e máximo.
5. **Distância máxima de repetição aceitável num pico.** A fase 1 pratica ~1500 px sem nunca ter
   declarado; a 2 chega a 2820.
6. **Onde mora o conteúdo opcional em relação ao risco.**
7. **Antecedência de aviso em px** antes do primeiro uso obrigatório. Hoje varia de 120 a 320 sem
   razão declarada.
8. **Onde fica o pico da fase**, e o que vem antes e depois dele.
9. **Se a mecânica da fase é exigida pelo chefe**, e em que x ela foi cobrada antes da arena.
10. **O conjunto próprio de marcos da fase, com consequência de rota** — não só de arte.
11. **Regra para plataforma móvel**: eixo, amplitude contra a largura da tábua, e uma regra única
    de fase para a sequência (hoje: 0, π, π/2, 0, com eixos alternados).
12. **Quanta precisão de temporização o jogo pode pedir.** O redemoinho pede **72 ms**; as folgas
    declaradas do próprio jogo são 100 ms (borda) e 120 ms (buffer). Ninguém comparou.

---

## O que ainda não foi verificado

- **Render e desempenho** (`technical-artist` com a skill `threejs-debug-profiler`) e **interface
  e fluxo** (`ux-designer`): não rodaram nesta leva.
- Três pontos pedem evidência **jogada**, não capturada: o aviso "Plane sobre o ar quente"
  aparecendo 974 px depois da fogueira; a legibilidade da beirada do vão de 1150 no iPhone com os
  botões na tela; e se o Corvo-Borrão exige altura que a fase 3 não oferece (`fires: []`).
- A deriva de escala de `timtim-parado` e `timtim-pulo` foi vista a olho, não medida em pixel.
