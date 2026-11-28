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

[To be designed] — for each major game state (exploration, combat, victory,
defeat, menus — whichever this game has): the emotional target, lighting
character (time of day, colour temperature, contrast), 3–5 atmospheric
descriptors, and energy level. Each state must look distinct from the others.

## 3. Shape Language

[To be designed] — character silhouette philosophy (readable at thumbnail
size, one distinguishing trait per archetype), environment geometry, UI shape
grammar, and hero versus supporting shapes.

## 4. Color System

[To be designed] — a primary palette of 5–7 colours with their meaning in this
world, semantic colour usage, per-area colour temperature rules, the UI palette
and where it diverges, and colourblind safety: which semantic colours need a
shape, icon or sound backup.

## 5. Character Design Direction

[To be designed] — the player character's visual archetype, how players tell
enemies, NPCs and allies apart at a glance, expression and pose style, and how
much detail survives at game camera distance (LOD philosophy).

## 6. Environment Design Language

[To be designed] — architectural style and its tie to the world's culture,
texture philosophy (painted, PBR or stylised, and why), prop density rules per
area type, and environmental storytelling guidelines.

## 7. UI/HUD Visual Direction

[To be designed] — diegetic versus screen-space HUD, typography (personality,
weight, size hierarchy, minimum readable size), iconography style, UI animation
feel, and any art-direction versus readability conflict and how it was decided.

## 8. Asset Standards

[To be designed] — file formats, naming convention, texture resolution tiers,
LOD levels, export settings, and the engine's hard limits (poly budgets per
asset category, texture memory, material slots). Where an art preference and a
technical limit disagree, record both and the trade-off chosen.

## 9. Reference Direction

[To be designed] — 3–5 references (games, films, art styles or artists). For
each: the specific element to take from it, and what to avoid so the result
does not read as a copy.
