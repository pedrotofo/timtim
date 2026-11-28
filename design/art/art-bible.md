# Art Bible: Timtim e os Brinquedos Perdidos

> **Status**: Draft
> **Owned By**: art-director
> **Last Updated**: 2026-11-28
> **Art Director Sign-Off (AD-ART-BIBLE)**: [Not yet reviewed]

Escrito em 28/11/2026, retroativamente: o jogo já existe e já está publicado. As decisões de
arte que já estavam tomadas vêm de `game/docs/design.md`, datadas — este documento **consolida
e estreita**, não re-decide. Onde este documento e o `design.md` falarem da mesma coisa, **este
manda**, e o `design.md` fica com o detalhe de cada fase.

Existe porque a produção de 24 e 25/11/2026 refez a capa e os cards cerca de seis vezes cada
(20 commits) e trocou a Zara pelo Elvis apesar de haver ficha de personagem nos assets: a
direção de arte do mundo estava escrita, a das superfícies de marca não. Ver
`docs/equipe-de-agentes.md`.

## 1. Visual Identity Statement

### 1.1 A regra visual

> **Silhueta primeiro, luz depois: em qualquer quadro, o Timtim é a mancha mais clara da tela,
> pequeno dentro de um mundo grande feito de três planos de valor separados e de uma única cor
> de fase — e nada entra em cena que empate em valor, saturação ou brilho com ele ou com a
> borda da plataforma em que ele vai pisar.**

É a frase que decide. Toda dúvida visual nova — um prop, um efeito, um card, um ícone, um
pedido ao gerador de imagem — se resolve nesta ordem: (1) a silhueta do Timtim segue a mais
clara? (2) os três planos seguem separados? (3) a cor é a da fase? (4) a borda acesa do chão
segue visível? Qualquer "não" e o elemento recua ou sai.

Os três planos e o herói, nos valores que o jogo **já usa** (`compMat.uniforms`, em
`render3d.js:871` — estes números são a fonte, não uma meta a perseguir):

| | O que é | Onde está no código |
|---|---|---|
| Primeiro plano | quase preto, desfocado, emoldura em cima e embaixo, filete de borda na cor fria da fase | `props/frente-*.png` |
| Plano do jogo | z=0, nítido, saturação cheia da cor da fase | `expo` 1,25 · no Arraial 1,18 |
| Fundo | enevoado, sem contraste nem saturação | `hazeK` · névoa `(0.86, 0.66, 0.5)` |
| Timtim | pico local, com poça de luz própria em volta | `heroK` 0,45 · no Arraial 1,0 |
| Sombra | puxada para o frio contra a luz quente | `shade` `(0.80, 1.02, 1.16)` |
| Bloom | só o que já brilha vaza luz; menos no Arraial, que já é claro | `bloomK` 0,8 · no Arraial 0,5 |

Luz-chave quente e baixa, vinda do lado e não de cima; sombra fria complementar. Quem se mexe
ganha contorno de luz fria; o que está fixo não. O vilão fica um tom mais escuro que o plano do
jogo, silhueta contra a névoa, e **nunca** emite luz própria.

### 1.2 Princípios de apoio

#### A — A cor é da fase; a identidade é do Timtim

**Serve o pilar 1, "É o Timtim".**

A fantasia é o jogador ver um cachorro que ele conhece de verdade, dentro de um curta. A
graduação para a paleta da fase tinge o pelo, o ambiente e as sombras — mas **não** apaga os
três fatos de identidade: a mancha preta, a bandana de festa junina e o lacinho. Esses três
guardam matiz próprio e se leem como marca de silhueta, em forma e não em textura: a bandana
tem de ser reconhecível com o Timtim a 80 px de altura no desktop 960×540 e com os botões de
toque cobrindo parte da tela no iPhone. Detalhe de identidade que só aparece com zoom não existe.

Vale igual para os outros cães reais, e é o que faz a piada interna funcionar: Furtão marrom,
Zara preta e branca, Elvis branco. Identidade errada não é detalhe de arte, é a piada perdida —
foi o que custou o commit `a88f5a4`, que trocou a Zara pelo Elvis.

**Teste:** quando a graduação da fase sobre um personagem estiver ambígua, tinja só o pelo, o
ambiente e as sombras, preservando o matiz da bandana, do lacinho e da mancha preta.

#### B — Brilho é informação, não enfeite

**Serve o pilar 3, "Impacto".**

O hitstop, o tremor de câmera, as faíscas e a câmera lenta do golpe final só impressionam se o
brilho for raro. Onde tudo pulsa, o pisão não acende nada. O direito de emitir luz tem duas
portas, e só duas: **o que importa para jogar** (biscoito, brinquedo, chama, checkpoint, o
próprio Timtim) e **as luzes de verdade do mundo** (postes, varais, lanternas de cabaça,
fogueiras, tochas). Fora dessas listas, nada emite — reflete.

Exceção nomeada, para a fase 1 não se contradizer: **musgo luminoso e borda acesa podem
iluminar a superfície que se pisa; emissores pontuais no plano do jogo são só itens.** Assim as
lajes de pedra com musgo continuam acesas sem competir com um biscoito. A bioluminescência
restante (flores, cogumelos, esporos) mora no primeiro plano e no fundo. Magenta é acento:
pontual, pequeno, nunca uma massa.

**Teste:** na dúvida se um elemento pode brilhar, ele não brilha — a menos que seja luz física
do cenário ou algo com que o jogador interage.

#### C — A leitura do piso vem antes da pintura

**Serve o pilar 2, "Fluidez antes de tudo".**

Fluidez não é só física: é o jogador saber onde vai cair antes de pular. Pulo variável,
pirueta, tolerância na borda e pulo antecipado só se sentem bem se a borda de cada plataforma e
de cada vão estiver legível **no instante** em que a decisão é tomada. O filete de luz na quina
de cima do chão e de cada plataforma é elemento de jogabilidade, não enfeite: nunca é coberto,
nunca é interrompido por um prop, nunca compete com um brilho vizinho.

Daí a **zona de leitura**: a faixa de tela onde o Timtim corre e pula. Props bonitos — troncos
gigantes, samambaias, bandeirinhas, galhos — vivem acima, abaixo ou atrás dela, no primeiro
plano quase preto ou no fundo enevoado. A beleza acontece nas bordas do quadro; o centro é
funcional. Isso dá ao `level-designer` uma restrição explícita de onde um prop pode morar, ao
lado da regra dos 70% em `docs/ritmo-das-fases.md`.

**Teste:** quando um prop e a borda acesa de uma plataforma disputarem o mesmo pixel, ganha a
borda acesa — o prop recua para o primeiro plano ou para o fundo.

### 1.3 O que esta seção já proíbe, sem nova discussão

- Mais de uma cor dominante numa fase, ou mudança de paleta ao longo do caminho.
- Qualquer elemento no plano do jogo mais claro que o Timtim.
- Brilho em decoração que não é luz física nem interativa (fora a exceção do musgo, em B).
- Detalhe de identidade que só se lê acima do tamanho de tela de jogo.
- Prop que atravessa a zona de leitura.
- Contorno grosso, na cena ou na interface — a interface é vidro escuro, filete fino de luz,
  serifada que brilha.
- Qualquer coisa de *Ori* que não seja linguagem visual: personagem, lugar, árvore-símbolo, música.
- Na fase 1, o reprovado em 24/11/2026: bandeirinhas, cenário colorido ou "feliz", vila ao
  entardecer, chafariz, coreto, carrinho de pipoca.

## 2. Mood & Atmosphere

A regra da Seção 1 não muda de estado para estado; o que muda é **quanto do quadro ela ocupa**.
Em exploração os três planos estão na tela; na apresentação do chefe o fundo some; na pausa o
quadro inteiro recua para trás de vidro. É esse o eixo que separa os estados — e é por isso que
**nenhum deles precisa de uma cor nova para se distinguir**.

Energia é de 0 a 10 e é **proposta**, não valor do código: serve para comparar estados, não para
ajustar nada.

| Estado | Alvo emocional | Luz | Energia | Elemento que carrega o humor | Distingue-se por |
|---|---|---|---|---|---|
| **Capa / título** | "esse cachorro é de alguém de verdade, e isso vai virar aventura" | quente, frontal, de pôster, sobre `#060a18` | 4 | o logo (`#3b1606` com gradiente `#fffbe0→#ff6a1f`) e os vaga-lumes `#ffe9a8` subindo por cima de arte imóvel | ser o único estado sem parallax e sem névoa |
| **Mapa das fases** | posse e escolha | luz de mesa, difusa, de cima, sobre `#0b1730` | 2 | o nó da fase atual é o **único** com poça de luz — eco de `heroK` fora do jogo | ser o único com luz vinda de cima |
| **Card de história** | "alguém está me contando isso"; intimidade | luz de página, chave quente lateral dentro de um quadro recortado | 3 | as barras de 12% fechando até o formato de curta; o título serifado com halo quente | ser o único com composição retangular centrada, sem zona de leitura |
| **Exploração** | curiosidade com segurança | o estado canônico da Seção 1 | 5, em dente de serra | o filete aceso na quina do chão mais as poças âmbar de postes, varais e tochas | ser o único com os três planos visíveis e em parallax ao mesmo tempo |
| **Aula do planar** (fase 2) | permissão para errar | o quadro mais aberto do jogo; contraste mais baixo (é o que `expo` 1,18 e `bloomK` 0,5 já fazem) | 4 | o vão inteiro dentro de um quadro, com o outro lado aceso por tocha: **o destino visível é o que ensina** | ser o único trecho em que o fundo clareia de propósito |
| **Debandada de galinhas** | susto cômico, bagunça de quintal, nunca ameaça | dois tempos: no aviso **nada muda** (é o aperto); na corrida o contraste sobe por acúmulo de silhuetas | 8 | a poeira rasante — a única massa de névoa autorizada na zona de leitura, e só porque atravessa e sai | ser o único estado em que algo opaco cruza a zona de leitura |
| **Apresentação do chefe** (3,2 s) | a piada e a ameaça no mesmo quadro | luz de palco: chave dura de lado, contraste máximo, fundo apagado | 7 de composição, não de movimento | o chefe um tom mais escuro e sem emitir luz; o nome em serifada, o maior texto do jogo | ser o único com fundo sem informação nenhuma |
| **Luta do chefe** | pressão legível: difícil, nunca confusa | arena fechada; o primeiro plano emoldura mais, o fundo recua mais | 9 | a borda acesa correndo de margem a margem **sem interrupção**; a crina do lobo-guará como único ponto claro no vilão | ser o único com borda acesa contínua |
| **Golpe final** | triunfo; um segundo de "eu fiz isso" | a única quebra autorizada do princípio B: um estouro para branco-quente que lava a cor da fase | 10, comprimida | as faíscas e o rastro de silhuetas de luz do Timtim, aqui como efeito principal | ser o único quadro em que algo é mais claro que o Timtim |
| **Vitória com presente** | alívio e vontade de mostrar a alguém | quente plena, frontal, contraste baixo; a névoa clareia e o fundo **sobe** de valor | 6 caindo a 3 | o presente como **único** emissor da tela, em `#ffd98a`. O brinquedo recuperado é a razão do jogo; ele é a luz | ser o único em que o fundo clareia em vez de recuar |
| **Derrota** ("Ah, não!") | "tenta de novo", nunca punição | a cor da fase **dessatura**, não escurece; o íris fecha para `#12070f` | 2 | o Timtim **continua a mancha mais clara**: a derrota tira cor do mundo, não luz do herói | ser o único estado dessaturado |
| **Estante de presentes** | coleção e posse; é a tela que se mostra ao amigo | luz de prateleira, difusa, quente neutra | 1 | a **silhueta** da estrela cheia contra a vazia já diz "tem / não tem" antes da cor | ser o único em grade, sem perspectiva |
| **Pausa** | interromper sem perder o lugar | nenhuma luz nova: congela, desfoca e recua para trás do vidro `rgba(44,18,40,.58)` | 0 | o quadro de jogo **continua visível** atrás do vidro: a pausa é camada, não tela nova | ser o único que não substitui o anterior |

Teto proposto para o estouro do golpe final: **0,08 s**. Ele existe justamente para o princípio B
continuar valendo no resto do jogo.

### O que esta seção já proíbe

- Inventar cor, hora do dia ou fonte de luz para distinguir um estado: a distinção vem de
  **quantos planos estão na tela**, não de paleta nova.
- Névoa ou massa opaca na zona de leitura — exceto a poeira da debandada, que atravessa e sai.
- Fundo com informação na apresentação do chefe.
- Escurecer ou dessaturar o Timtim na derrota.
- Mais de um emissor na tela de vitória.
- Estouro de branco fora do golpe final, e lá por mais de 0,08 s.
- Pausa ou card que **apague** o quadro de jogo em vez de cobri-lo.
- Borda acesa contínua de margem a margem fora da arena do chefe.

## 3. Shape Language

O Timtim tem 80 px de altura num desktop 960×540 — **15% da altura da tela**, e menos no iPhone,
onde a câmera desce e os botões cobrem parte da área. Nesse tamanho textura não existe e detalhe
interno não existe. **Só a borda existe.**

Daí o **teste dos três blobs** (proposta): toda silhueta do elenco tem de se ler com no máximo
três massas a 80 px, e continuar identificável reduzida a 24 px e desfocada. Se precisa de uma
quarta massa para ser reconhecível, a quarta massa não é identidade — é enfeite, e sai. É a
tradução de forma do princípio A. Serve o pilar 1.

### Um traço por arquétipo

Cada arquétipo tem **um** traço que o identifica na periferia da visão, e nenhum pode pegar o
traço de outro.

| Arquétipo | Traço único | Por quê |
|---|---|---|
| **Herói** (Timtim) | perfil arredondado com duas quebras duras: a ponta da orelha e o nó da bandana no peito. A bandana é a **única forma triangular clara** do elenco | pilar 1. As três massas são corpo claro, mancha preta e triângulo da bandana — exatamente três, o limite |
| **Amigo** (Zara, Elvis) | duas orelhas triangulares **para cima**, altas e grandes demais; a silhueta é dominada pelas pontas | pilar 4. "Amigo" se lê antes da cor; a cor então faz a piada — Zara em duas massas, Elvis numa massa clara inteira |
| **Inimigo comum** (pombo, galinha, corvo) | corpo em ovo com **uma ponta horizontal** (o bico), apontando para o lado, nunca para cima | é literalmente a regra do jogo: pisar por cima resolve, encostar de lado machuca. A forma anuncia a mecânica |
| **Chefe** (Furtão, lobo-guará, Corvo-Borrão) | **mais largo que alto**, ombro mais alto que a cabeça. Chefe é massa, não ponta | o chefe é a única coisa que não se resolve por cima; silhueta pesada e baixa diz isso sem texto |
| **Item** (biscoito, banana, estrela, presente) | convexo e **fechado**, sem apêndice nenhum | é o que impede item e inimigo de se confundirem na periferia. Serve o pilar 2: pegar não exige olhar |

Em revisão isto se cobra: um item novo com ponta é erro de arquétipo, não questão de gosto; uma
galinha mais alta que larga vira chefe aos olhos do jogador.

### Curva pinta, reta sustenta

**Domina a curva orgânica** — raízes, troncos, galhos, samambaias, fumaça, pincelada: é o que faz
o mundo parecer desenhado à mão. **Mas onde se pisa é reto e angular, sempre**: lajes da fase 1,
deques e peneiras da fase 2, tábuas da fase 3. A aresta de cima é reta e horizontal, sem exceção.

O contraste de gramática dá a leitura do piso **antes** da cor — serve o princípio C e o pilar 2.
Pulo variável, tolerância de 0,1 s e buffer de 0,12 s só se sentem bem se o olho identificar a
plataforma por forma, no instante da decisão, sem comparar brilhos.

**A fase 3 é o caso difícil:** no mundo de Van Gogh tudo é pincelada curva, então o piso tem de
ficar **mais** reto, não menos. Onde o cenário inteiro ondula, uma aresta reta é a coisa mais
estranha da tela — e estranha é o que ela precisa ser. É também a compensação para o `shade`
quase neutro da fase 3 (`(.96, .97, 1.04)`), que quase não separa planos por temperatura.

### Interface: linguagem própria, declarada

**A interface não ecoa o mundo.** É vidro escuro, filete fino de luz, serifada que brilha — e é a
única coisa no jogo com **raio de canto constante**. O mundo não tem raio constante em lugar nenhum.

A razão é de leitura: se a interface imitasse madeira, palha ou pincelada, entraria na mesma
família de formas do cenário e passaria a competir com ele pela atenção — e a verba de atenção do
quadro já está comprometida com o Timtim e a borda da plataforma. Interface que parece cenário é
interface que se perde no cenário. A fase pode chegar à interface como **luz atrás do vidro**,
nunca como material.

### Formas-herói contra formas de apoio

Quatro coisas são **forma-herói**, e só quatro: o Timtim, a borda acesa da plataforma, o item e o
ponto fraco do chefe. Elas têm direito a aresta nítida, contraste local alto e silhueta fechada.
Todo o resto é **apoio**: aresta amolecida, contraste baixo, silhueta aberta.

Orçamento proposto: no máximo **três formas-herói no mesmo quadro**. Acima disso o olho escolhe
por conta própria e a Seção 1 deixa de valer na prática, mesmo que cada elemento passe nos quatro
testes. Caso concreto: na debandada, Timtim + borda + galinhas já estoura — por isso as galinhas
são apoio, não inimigo-herói.

### O que esta seção já proíbe

- Silhueta que precise de mais de três massas para ser reconhecida a 80 px.
- Item com ponta, bico ou apêndice.
- Inimigo comum mais alto que largo (vira chefe) ou com orelha triangular para cima (vira amigo).
- Chefe mais alto que largo.
- Aresta de cima de plataforma curva, ondulada ou interrompida — com mais rigor na fase 3.
- Interface com material do mundo: madeira, palha, pincelada, corda, peneira.
- Raio de canto variável na interface; aresta nítida em prop de apoio.
- Mais de três formas-herói no mesmo quadro.

## 4. Color System

Todos os valores abaixo são **os que o jogo já usa**, lidos de `game/src/render3d.js` e
`game/index.html`. O que é proposta está marcado.

### Paleta primária — sete cores e o papel de cada uma

| Cor | Valor | O que ela **é** neste mundo |
|---|---|---|
| **Quase-preto de moldura** | `#06202d` (near), `#010a0f` (front) | não é cor, é valor. O material de tudo que emoldura. É o que permite uma cor só dominar a fase |
| **Azul da distância** | `#14506a` (far), `#0b3447` (mid) | a distância. O fundo que **nunca** compete |
| **Ciano** | `0x6fe9ff` | "está vivo / está se mexendo". Contorno de quem se move, e a luz da fase 1. **Nunca é recompensa** |
| **Âmbar / dourado** | `0xffb866` (`PAL.warm`), `#ffd98a` (`--gold`) | "importa para jogar, e é bom": biscoito, chama, checkpoint, presente, poça de poste e tocha. É também a cor da luz **física**. As duas portas do princípio B têm a mesma cor, de propósito — o jogador aprende uma regra só |
| **Violeta** | `0xa98bff` (`PAL.violet`) | a sombra e o estranho. **Nunca é acionável** — é a cor do que você vê e não toca |
| **Menta** | `0x7dffd0` (`PAL.mint`) | "aqui se pisa". Proposta: o piso tem **direito exclusivo** ao menta |
| **Vermelho-rosa** | `#e8323c` (coração), `#ff7d9c` (`--rose`) | o seu corpo. Vida e dano, e nada mais. **Não existe no cenário** |

Acento fora da tabela: **magenta** `0xff5ad8`, a flor de luz da fase 1 — pontual e pequeno,
nunca massa (Seção 1).

### Uso semântico

- **Vermelho = você.** Se aparecer num tronco, numa fruta ou numa bandeirinha, o jogador vai
  checar a barra de vida. Por isso está fora do cenário em todas as fases.
- **Dourado = recompensa e luz de verdade.** As duas coisas que o princípio B autoriza a emitir.
  Quem vê dourado anda na direção dele.
- **Menta = piso.** A única cor que responde "posso pisar aí?".
- **Ciano = movimento.** Não quer dizer bom nem ruim; quer dizer "isso se move".
- **Violeta = cenário e sombra.** Bonito, inerte. É a cor que ensina a não tentar.
- **Branco = ruptura.** Só o golpe final e o nome do chefe. Nenhum dos dois é jogável.

### Temperatura por fase

| Fase | Cor | Regra | Valores reais |
|---|---|---|---|
| **1 · O Parque** | azul | mundo **frio**, luz quente pequena e rara; sombra puxa para o azul | `NIGHT_`: bg `#020a12`, amb `#6f9cc0`, sun `#a6dcff`, `shade (.80, 1.02, 1.16)`; `expo` 1,25 · `heroK` 0,45 · `bloomK` 0,8 |
| **2 · O Arraial** | laranja | mundo **quente**, sombra **roxa** complementar. O mundo já é claro, então o herói precisa de mais ajuda e o bloom de menos | `DUSK`: amb `#ffb27a`, sun `#ffc89a`, `shade (.8, .76, 1.08)`; `expo` 1,18 · `heroK` 1,0 · `bloomK` 0,5 |
| **3 · O Quadro Encantado** | Van Gogh | **a temperatura quase não separa planos aqui** — `shade` é quase neutro. A hierarquia vem de **valor e direção de pincelada**, não de cor | `VGP`: bg `#0c1430`, mist `#7088c8`, shaft `#f6e08a`, amb `#fff2d8`, `shade (.96, .97, 1.04)` |
| **4 · Dia de Chuva** | **proposta: verde-acinzentado frio**, família `#4d6b5e` | **proposta, não decidida.** "Cinza morno de quintal molhado, perto de casa": ar frio, janelas quentes — a inversão da fase 1. Único lugar com reflexo no chão, o que dá leitura de piso **e** chuva num só elemento | nada no código ainda |
| **5 · O Covil do Furtão** | **proposta: tijolo escuro / sépia**, família `#5a2a20` | **proposta, não decidida, e a mais arriscada:** inverteria os três planos (fundo escuro e fechado, por ser interior sem horizonte), o que contraria a leitura por profundidade do `design.md`. Precisa de teste. Se reprovar, a alternativa é fundo claro com luz de fresta | nada no código ainda |

**Risco cruzado da proposta da fase 4:** se a fase 4 for verde, o menta do piso perde o monopólio
de matiz ali e passa a depender só de forma (a aresta reta) e de valor. É aceitável, mas é custo
real — saiba dele antes de aprovar o verde.

### Paleta da interface — divergência declarada

A interface **não segue a cor da fase**. É ameixa e quente, constante nas três fases, e isso é
deliberado: `--ink #020d14` · `--glass rgba(44,18,40,.58)` · `--line rgba(255,220,190,.34)` ·
`--glow #ffd9a8` · `--text #fff6ea` · `--gold #ffd98a` · `--warm #ffb866` · `--rose #ff7d9c` ·
`--violet #a98bff` · `--mint #7dffd0`. Telas: página `#12070f` · palco `#1a0c1c` · mapa `#0b1730`
· título `#060a18`.

**Por que diverge:** a Seção 1 proíbe mais de uma cor dominante por fase. Se a interface se
tingisse da fase, a tela teria **duas** fontes de cor dominante — a do mundo e a do sistema — e a
regra quebraria por fora, não por dentro. A interface constante também dá uma referência fixa de
"onde estou no sistema" que atravessa as fases. É o princípio A um nível acima: a cor é da fase,
a identidade é do jogo.

**Exceção autorizada:** mapa e cards podem usar a cor da fase como **luz atrás do vidro** — halo,
gradiente fraco, brilho de título. Nunca como material, nunca no texto.

`--gold`, `--warm`, `--rose`, `--violet` e `--mint` guardam os mesmos papéis semânticos de cima.
Isso não é divergência: é o que impede o ícone na interface de contradizer o objeto no mundo.

### Pares de cor que falham, e a pista de reserva de cada um

`.claude/rules/timtim-web.md` registra que este projeto **não tem modo para daltônicos**, e nada
aqui propõe um. O que segue é redundância em tempo de desenho: custa zero em execução e melhora a
leitura para todo mundo no iPhone, onde o Timtim tem muito menos de 80 px.

| Par que falha | Para quem | Pista de reserva obrigatória |
|---|---|---|
| **menta `#7dffd0` (piso) × ciano `#6fe9ff` (movimento)** | deuteranopia, protanopia — **e visão normal no iPhone**, onde são quase o mesmo pixel | **forma.** O piso é filete **reto, horizontal e contínuo**; o contorno de movimento é **fechado e acompanha a silhueta**. Logo: nunca pôr filete reto em algo que se mexe |
| **vermelho `#e8323c` (vida) × dourado `#ffd23f`/`#ffb866` (recompensa)** | protanopia os aproxima em matiz e valor | **forma, já existente, e som.** Coração × estrela × círculo do biscoito se distinguem em silhueta. Falta garantir que o coração nunca apareça reduzido a um ponto, e que o dano tenha marca sonora própria (o quê e como é do `audio-director`) |
| **violeta `#a98bff` (inerte) × ciano `#6fe9ff` (vivo)** | tritanopia | **contorno.** Só o acionável tem contorno; o violeta nunca tem. A ausência de contorno passa a ser a informação |
| **magenta `0xff5ad8` (flor) × rosa `#ff7d9c` (vida)** | praticamente todos, inclusive visão normal | **separação espacial, já exigida.** O princípio C manda a flor para fora da zona de leitura e o rosa de vida vive na interface. Regra nova: proibir rosa de vida em elemento de mundo |

**O que já está certo e deve ser preservado:** o vilão é "um tom mais escuro que o plano do jogo"
— diferença de **valor**, não de matiz, que segura em qualquer tipo de daltonismo, em qualquer
tela, com qualquer brilho. A mesma lógica vale para o Timtim ser a mancha mais clara: a regra
central da Seção 1 é a mais robusta possível em acessibilidade de cor. As três cores de
identidade também se distinguem por valor e forma antes de matiz.

### O que esta seção já proíbe

- Vermelho em qualquer elemento de cenário, em qualquer fase.
- Menta em qualquer coisa que não seja a borda acesa do piso.
- Ciano em recompensa; dourado em algo que não seja recompensa nem luz física.
- Violeta com contorno, ou violeta em algo acionável.
- Branco estourado fora do golpe final e do nome do chefe.
- Interface tingida pela cor da fase (fora halo e brilho de título no mapa e nos cards).
- Rosa de vida em elemento de mundo; magenta dentro da zona de leitura.
- Par semântico novo que se distinga **só** por matiz: todo par precisa de forma, posição ou
  contorno como reserva.
- Tratar `expo`, `heroK`, `bloomK`, `shade`, `PAL` ou `VGP` como meta a perseguir — são a fonte.
  Mudança ali é pedido ao `technical-artist`, com print nos dois viewports.

## 5. Character Design Direction

### O elenco, e o que é fato

| Personagem | Papel | Fato não-negociável |
|---|---|---|
| **Timtim** | herói | mancha preta, bandana de festa junina, lacinho. É um cachorro **real** |
| **Zara** | amiga, dá biscoito | chihuahua **preta e branca** |
| **Elvis** | amigo, dá biscoito | chihuahua **branco** |
| **Furtão** | chefe da fase 1 | cão **marrom** (nunca cinza-azulado) |
| **Lobo-guará** | chefe da fase 2 | a **crina** é o ponto fraco, e o único ponto claro nele |
| **Corvo-Borrão** | chefe da fase 3 | roubou o pincel; fica **vermelho de raiva** no último coração |
| **Macaco Fedido** | o brinquedo | dá invencibilidade |
| **Van Gogh** | figura da fase 3 | vem correndo buscar o pincel; não surge do nada |

Ficha visual: `game/assets/tintim-character-sheet.png`. Errar uma dessas linhas não é detalhe de
arte: no commit `a88f5a4` a Zara e o Elvis foram trocados e a piada se perdeu.

### O arquétipo do jogador

O Timtim é **um cachorro de verdade, não um mascote**. A diferença é operacional: mascote se
desenha para ser simpático em qualquer pose; um cachorro de verdade se desenha a partir de como
aquele cachorro se move. É por isso que as animações saem de **quadros de vídeo** e não de poses
desenhadas uma a uma (`design.md`, 24/11/2026) — quadros desenhados pela IA variam entre si e a
animação treme; os de vídeo são contínuos.

Serve o pilar 1 diretamente, e é o que o jogo tem de mais difícil de imitar.

### Tamanho igual em toda pose

As alturas em `R.frame` — **parado 80, correndo 82, pulo 77, queda 82, farejando 69** — foram
acertadas para a cabeça não mudar de tamanho ao trocar de pose. Antes o Timtim encolhia uns 20%
no pulo.

Regra: **uma pose nova entra com a altura medida contra essas, não escolhida.** A de farejar é 69
de propósito (ele abaixa a cabeça); qualquer outra que fuja da faixa 77–82 precisa de justificativa
escrita. Serve o pilar 2: o corpo mudar de tamanho durante o pulo quebra a leitura da trajetória.

### Como se distinguem num relance

A Seção 3 já dá o traço de silhueta por arquétipo. O que esta seção acrescenta é a ordem de
leitura, que vale para qualquer personagem novo:

1. **Silhueta** diz o arquétipo (herói, amigo, inimigo, chefe, item) — a 80 px, sem cor.
2. **Valor** diz a intenção: o herói é o mais claro, o chefe é mais escuro que o plano do jogo.
3. **Cor** diz **qual** indivíduo é (Zara contra Elvis), e só isso.

Cor nunca carrega a informação de arquétipo nem de ameaça. Se um personagem novo só se distingue
por cor, ele está errado na camada 1 e não se conserta repintando.

### Pose e expressão

Expressivo e elástico, nunca realista: o corpo estica e achata com uma mola, inclina com a
velocidade, e deixa rastro de silhuetas de luz na pirueta e no turbo. A deformação por código
(rabo, orelhas, respiração) fica **só** para as poses que ainda são paradas — bote, agachado,
pulo duplo. Onde há quadros de vídeo, a deformação sai: somar mola a um ciclo filmado é o que
produzia a tremida.

### Nível de detalhe à distância da câmera

A câmera tem direção fixa, só desliza, aproxima e treme — nunca gira. Isso significa que **todo
personagem é visto de perfil, a uma distância quase constante**, e o nível de detalhe se afina
para esse único caso. Não há orçamento a gastar com o que não se vê: nada de detalhe para
close-up, nada de costas, nada de três quartos, a não ser num card de história, que é ilustração
e não jogo.

Personagens são sprites em pé no plano z=0, com sombra recortada no chão.

### O que esta seção já proíbe

- Pose nova fora da faixa de altura 77–82 (69 só para farejar) sem justificativa escrita.
- Quadros de animação desenhados um a um pela IA onde um ciclo de vídeo é possível.
- Deformação por código somada a um ciclo de vídeo.
- Personagem que só se distinga por cor.
- Arte de personagem para ângulo que a câmera não mostra.
- Qualquer alteração nas linhas da tabela de fatos acima sem o Pedro decidir.

## 6. Environment Design Language

### O mundo é 3D de verdade

Piso em blocos (os buracos são vãos de verdade), camadas de árvores a até 2.200 unidades, céu no
infinito. **O parallax vem da perspectiva, não de truque** — e é essa decisão que faz a arte
parecer um curta em vez de um jogo de camadas deslizantes.

O cenário é desenhado **por código**, com texturas de canvas. Isso dá controle total da paleta e
não depende de imagem — e é por isso que a regra "uma cor por fase" é exequível: a cor é um
parâmetro, não uma repintura.

### Arquitetura por fase, e a cultura por trás

| Fase | O lugar | O que o constrói | O que ele conta sem texto |
|---|---|---|---|
| **1 · O Parque** | floresta noturna com cara de pântano | lajes de pedra com musgo luminoso e raízes, figueiras com lanternas, postes, varais de luzinhas, sebe escura, plantas de pântano ao luar, esporos | um parque de bairro à noite, habitado mas vazio agora. As luzinhas penduradas são de gente, não de magia: alguém mora perto |
| **2 · O Arraial** | festa junina escondida numa clareira da mata | deques de madeira sobre palafitas com casca e amarração de corda, peneiras de palha trançada com fitas, troncos gigantes espaçados, tochas de bambu, barracas, bandeirinhas, fogueiras, mastro de São João | a festa é improvisada e feita à mão: nada é industrial, tudo é amarrado, trançado ou fincado |
| **3 · O Quadro Encantado** | dentro de uma pintura de Van Gogh | móveis do próprio quadro como plataformas (cama, cadeira, mesas, toldo, moldura), ciprestes, girassóis, lampião, céu em espiral | o quadro é um lugar com mobília: você pisa nas coisas que o pintor pintou |

### Textura: pintado, nunca PBR

Arte quase realista é bem-vinda **quando é graduada para a paleta da fase** — as plantas de
pântano da fase 1 foram geradas ao luar azul; a arte do Arraial é tingida de laranja. O que não
entra é material fisicamente correto: metal com reflexo, especular, mapa de rugosidade. O jogo é
uma pintura iluminada, não uma cena renderizada.

A razão não é só gosto: `render3d.js` usa `ShaderMaterial` com GLSL próprio e não o pipeline de
material do Three.js. Pedir PBR é pedir outro renderizador.

### Densidade de prop: a zona de leitura manda

O princípio C já diz onde prop pode morar. Em números de composição (proposta):

- **Zona de leitura** (a faixa onde o Timtim corre e pula): densidade **zero**. Nada além do piso,
  da borda acesa, dos itens e dos personagens.
- **Primeiro plano** (quase preto, emoldura em cima e embaixo): densidade **alta** — é onde a
  beleza se gasta, porque ali ela não custa leitura.
- **Plano do jogo, fora da zona de leitura**: densidade **média**, caindo perto de um vão. Um vão
  precisa de ar à volta: é a hora da decisão.
- **Fundo**: densidade alta, mas **em silhueta e sem contraste** — massa, não objeto.

### Marcos, e por que importam

Cada fase tem elementos próprios, não só cor: plataformas, árvores do meio do cenário, iluminação
e checkpoint mudam de uma para outra. Fase 1: lajes, figueiras com lanternas, postes, varais.
Fase 2: deques, peneiras, troncos, tochas de bambu, lanternas de cabaça — **sem** varais de
luzinhas, **sem** postes nem bancos de praça.

É o que impede as fases de serem a mesma fase repintada. Uma fase nova precisa de um conjunto
próprio de plataforma, árvore, luz e checkpoint, não de uma paleta nova.

### O que esta seção já proíbe

- Material fisicamente correto: metal, especular, rugosidade, reflexo.
- Qualquer prop dentro da zona de leitura.
- Prop no plano do jogo perto da borda de um vão.
- Objeto legível (com contraste próprio) no fundo: o fundo é massa em silhueta.
- Reaproveitar o conjunto de plataforma, árvore, luz ou checkpoint de outra fase.
- Na fase 1, o reprovado em 24/11/2026: bandeirinhas, cenário colorido ou "feliz", vila ao
  entardecer, chafariz, coreto, carrinho de pipoca.
- Parallax por deslizamento de camada em vez de perspectiva.

## 7. UI/HUD Visual Direction

### Visão de arte

**Interface em tela, não diegética.** O jogo é 2.5D com câmera de direção fixa; não há superfície
no mundo onde pôr informação sem competir com a zona de leitura. A interface mora na frente,
atrás de vidro, e assume isso.

**Material:** vidro escuro (`--glass rgba(44,18,40,.58)`), filete fino de luz
(`--line rgba(255,220,190,.34)`), halo quente (`--glow #ffd9a8`). **Nada de contorno grosso** — a
proibição já está travada na Seção 1.

**Tipografia, duas famílias e um papel para cada:**

| Família | Valor | Papel |
|---|---|---|
| **Display** | `Marcellus`, Georgia, serif | título, nome de chefe, nome de fase, frase de card. É a voz do curta: serifada, com brilho |
| **Texto** | `Nunito`, Trebuchet MS, sans | dica, contador, botão, rótulo. É a voz do sistema: redonda, legível, sem personalidade própria |

A hierarquia é por tamanho e por família, nunca por peso só. O maior texto do jogo é o nome do
chefe (5,6cqw); o menor é o rótulo de sistema (1,05cqw).

**Ícones:** pictograma cheio, silhueta fechada, sem traço externo — mesma gramática dos itens na
Seção 3 (convexo e fechado). O ícone na interface tem de ser a **mesma silhueta** do objeto no
mundo: o biscoito da interface é o biscoito do chão.

**Animação de interface:** entra por opacidade e por um deslocamento curto, nunca por escala
grande nem por rotação. O card não trepida (foi corrigido em `050675e`). A interface não chama
atenção para si — ela aparece e fica.

**A cor da fase chega à interface como luz atrás do vidro, nunca como material** (Seção 4).

### Visão de UX — e um defeito medido

Medi a interface nos dois viewports obrigatórios, no navegador, com o jogo carregado:

| | container | menores fontes | alvos de toque (menor lado) |
|---|---|---|---|
| **Desktop 960×540** | 960 px | **10,6 px** (`SMALL`), 11,0 (`btnTela`), 12,5 (`btnReset`), 12,5 (`hint`) | — |
| **iPhone 13** | 390 px | **4,3 px** (`SMALL`), 4,5 (`btnTela`), 5,1 (`btnReset`), 5,1 (`hint`) | **31 px**, 37, 37, 47 |

**O defeito:** todos os tamanhos da interface estão em `cqw` (1% da largura do container, 119
usos em `index.html`). No desktop o container tem 960 px e 1,05cqw dá 10,6 px — pequeno, legível.
No iPhone o container tem 390 px e o **mesmo** 1,05cqw dá **4,3 px**, que ninguém lê. A escolha
proporcional, que é correta para manter a composição, aplica-se também ao que não pode encolher.

**Segundo achado:** um dos botões de toque tem **31 px** no menor lado. O piso usual para alvo de
toque é 44 px — abaixo disso o dedo erra, e este é um jogo de plataforma em que errar o botão
custa um coração.

**O conflito, sem eu resolver:** a visão de arte quer tipo proporcional, porque é o que mantém a
composição idêntica em qualquer tela — e é também o que faz o jogo caber na janela de artefato.
A visão de UX quer um piso absoluto em pixels para texto de sistema e alvo de toque. As duas não
cabem juntas no mesmo `cqw`.

As saídas possíveis, para o Pedro decidir:

1. **Piso com `max()`** — `font-size: max(12px, 1.05cqw)`. O texto de sistema para de encolher
   abaixo do legível e a composição continua proporcional acima disso. É a mudança mais pequena e
   não mexe em layout no desktop. **É a que eu recomendaria.**
2. **Duas escalas** — display em `cqw` (composição) e texto de sistema em `px` ou `rem`
   (legibilidade). Mais correto conceitualmente, mais trabalho, e muda o desktop.
3. **Aceitar** — registrar que no celular o texto de sistema é decorativo e garantir que nenhuma
   informação necessária viva só ali. Nesse caso a dica de controles precisa de outro lugar.

Para o alvo de 31 px não há conflito: 44 px é piso, e crescer o botão não custa composição —
ele está sobre o jogo, não dentro dele.

**O que já está certo:** nenhuma informação da interface depende só de cor (Seção 4 cobra a pista
de reserva); o card de vitória e de derrota não aceita tecla nos primeiros 1,5 s, o que impede
quem vinha apertando o pulo de passar a tela sem ver o presente (`ui.js:64`) — isso é feedback
cuidado, e deve ficar.

### O que esta seção já proíbe

- Interface diegética (informação em superfície do mundo).
- Contorno grosso; raio de canto variável; material do mundo na interface (Seção 3).
- Hierarquia por peso de fonte sem mudar tamanho ou família.
- Ícone cuja silhueta não seja a do objeto no mundo.
- Animação de interface por escala grande ou rotação.
- Informação necessária apenas em texto de sistema **enquanto** o defeito de 4,3 px no celular
  não estiver resolvido.
- Alvo de toque com menos de 44 px no menor lado.

## 8. Asset Standards

### Visão de arte

**Formatos em uso** (contagem real em `game/assets`, 60 MB no total):

| Formato | Quantos | Para que |
|---|---|---|
| `png` | 97 | sprites e props com transparência |
| `mp3` | 50 | música, locução, efeitos |
| `webp` | 32 | folhas de animação (com o `json` do ciclo ao lado) |
| `json` | 30 | dados de animação, um por `webp` |
| `jpg` | 17 | fundos pintados e texturas, onde não há transparência |
| `mp4` | 4 | vídeo de capa e de abertura de fase |

**Regra de formato:** transparência pede `png`; folha de animação pede `webp` com `json` irmão de
mesmo nome; fundo e textura sem transparência pedem `jpg`. Não introduzir formato novo sem
necessidade demonstrada — cada um a mais é uma via de decodificação a aquecer no carregamento.

**Nomes.** A convenção real do projeto é `kebab-case`, por pasta, com o padrão
`<sujeito>-<ação ou variante>.<ext>`: `corvo-bica.webp` + `corvo-bica.json`, `guara-corre.webp`,
`frente-arraial-1.png`, `vg-girassol.png`. Prefixo de fase quando o asset é de uma fase só
(`vg-` para o quadro, `arraial-` para a fase 2).

É **diferente** da convenção `[categoria]_[nome]_[variante]_[tamanho]` que o framework sugere, e
fica como está: 183 arquivos já seguem a do projeto, e a pasta já faz o papel da categoria.

**Animação:** o ciclo sai de **quadros de vídeo**, não de desenhos um a um (Seção 5). Um ciclo
completo para corrida e andar; um trecho que toca em vai e volta para parado, latindo, comendo,
tonto.

**Exportação:** a arte entra graduada para a paleta da fase (Seção 4). Graduar depois, por código,
não é opção — `render3d.js` tinge, mas não conserta uma arte gerada na cor errada.

### Visão técnica

Os orçamentos declarados em `project.yaml` são:

| Chave | Valor |
|---|---|
| `performance.target_framerate` | 60 |
| `performance.frame_budget_ms` | 16,67 |
| `performance.enforce` | `block` |
| `performance.draw_call_limit` | **não definido** |
| `performance.memory_ceiling_mb` | **não definido** |
| `platform.targets` | `[Web, Mobile]` |
| `engine.name` / `version` | Web / three r144 |

**Dois orçamentos não estão definidos, e eu não vou inventá-los.** Sem limite de draw call e sem
teto de memória, esta seção não pode dizer quantos triângulos ou quantos megabytes de textura um
asset novo pode custar. O que existe é o piso de **45 fps**, abaixo do qual `R.setQuality` baixa o
nível sozinho — um mecanismo de defesa, não um orçamento. Para medir e propor os dois números
faltantes, a skill instalada é `threejs-debug-profiler`.

**Limites que valem desde já, do que o projeto é:**

- **Sem etapa de build.** `THREE` é global, por `<script src>`. Asset novo entra por caminho
  relativo, não por `import` (`.claude/rules/timtim-web.md`).
- **Tudo vai para a placa de vídeo no carregamento** (`warmUp`), para o primeiro segundo da fase
  não engasgar. Cada textura nova soma ao tempo de carregamento, que já tem um vigia de 10 s sem
  arquivo novo antes de desistir (`render3d.js`).
- **Três níveis de qualidade.** Nível 1 desliga desfoque e reduz resolução; nível 0 desliga sombra,
  pós-processamento, névoa e parte dos fachos. **Celular começa no nível 1.** Um efeito novo tem de
  ter um comportamento definido nos três níveis, ou ele some sem aviso no celular.
- **O peso está no áudio, não na arte.** As seis músicas somam cerca de 17 MB dos 60 MB — mais que
  todos os sprites, props, fundos e texturas juntos. Se o carregamento no celular virar problema,
  é ali que se corta, e a decisão é do `audio-director`.

**Onde a arte e o limite se chocam:** a Seção 6 pede densidade alta de prop no primeiro plano, e o
primeiro plano é justamente o que está desfocado e mais perto da câmera — ou seja, o que custa
mais em preenchimento de pixel. No nível 0 o desfoque sai, e a densidade que era bonita passa a
ser ruído nítido. **Não resolvo isto aqui:** ou o primeiro plano tem uma versão mais rala para o
nível 0, ou a densidade alta fica limitada ao que ainda lê sem desfoque. É decisão do
`technical-artist` com o `art-director`, e pede print nos dois viewports.

### O que esta seção já proíbe

- Formato novo sem necessidade demonstrada.
- Folha de animação sem o `json` irmão de mesmo nome.
- Asset com transparência em `jpg`; fundo sem transparência em `png`.
- Nome fora do `kebab-case` `<sujeito>-<ação>` da pasta.
- Arte entregue fora da paleta da fase, para "graduar depois".
- Efeito novo sem comportamento definido nos três níveis de qualidade.
- Afirmar orçamento de draw call ou de memória enquanto `project.yaml` não os tiver — medir
  primeiro, com `threejs-debug-profiler`.

## 9. Reference Direction

[To be designed] — 3–5 references (games, films, art styles or artists). For
each: the specific element to take from it, and what to avoid so the result
does not read as a copy.
