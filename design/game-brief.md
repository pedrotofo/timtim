# Game Brief: Timtim e os Brinquedos Perdidos

> Brief retroativo, escrito em 28/11/2026. O jogo já existe e já está publicado: este
> documento não decide nada novo, ele põe no caminho que o framework espera
> (`design/game-brief.md`) o que já estava decidido em `game/docs/design.md`.
> **Detalhe de arte, fases e 2.5D continua no `design.md` — não duplicar aqui.**

## In your words

**Pitch:** 2 a 3 minutos de plataforma que parecem um curta de animação estrelado por um
cachorro de verdade.

**Genre:** plataforma 2.5D de ação, por fases

**Controls:** `←` `→` andar · `Espaço` pula (de novo no ar: pirueta) · segure `Espaço` no ar:
planar (fases 2 e 3) · `↓` fareja. No toque: `◀` `▶` `▲` e `👃`.

**Question:** já respondida — o jogo é jogável e está no ar. A pergunta aberta hoje é de
produção, não de conceito: cabe fazer mais fases sem a refação que custou metade dos commits
de 24 e 25/11 (ver `docs/equipe-de-agentes.md`).

**Hooks:** é o Timtim de verdade — cachorro real, mancha preta, bandana de festa junina. Os
chefões são os cães da vizinhança. Cada fase tem uma cor e um sentimento próprios.

## Who it's for / what they feel

Feito para mostrar aos amigos. Quem joga sente que está dentro de um curta de animação com um
cachorro que ele conhece — carinho e reconhecimento antes de desafio.

## Label

Arte quase realista graduada para a paleta de cada fase, na linguagem visual de *Ori* (silhueta
primeiro e luz depois, herói pequeno e luminoso num mundo grande). Áudio com trilha própria por
fase e narração nos cards.

## Core loop

Correr, pular e planar por uma fase pintada, juntando biscoitos e salvando quem precisa, até a
luta com o chefe da fase — que pede a ação daquela fase.

## Goal & fail state

Vencer as três fases e recuperar os brinquedos; cada fase dá um presente para a estante.
Perder: os corações acabam e volta ao último ponto de controle.

## Features

Três fases jogáveis (O Parque, O Arraial, O Quadro Encantado), mapa de fases, estante de
presentes, cards de história com narração, chefe por fase, qualidade adaptativa em três níveis.

## Keep

Fluidez antes de tudo: pulo variável, pulo duplo com pirueta, flutuação no topo do pulo,
tolerância na borda (0,1 s), pulo antecipado (0,12 s). Passos fixos de 1/240 s, para o pulo sair
igual em qualquer computador.

## Avoid

Ver `game/docs/design.md`, "O que **não** entra na fase 1" — bandeirinhas, cenário colorido ou
"feliz", vila ao entardecer, chafariz, coreto, carrinho de pipoca: testados e reprovados.

## Out of scope

Mais fases além da 3 (a 4 e a 5 aparecem no mapa como EM BREVE), animações próprias para os
chihuahuas, sprites dos pugs reais, placar online.

**Kill condition:** não se aplica — o jogo passou do protótipo e está publicado.
