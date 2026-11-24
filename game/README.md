# Timtim e o Resgate do Macaco Fedido

Jogo de plataforma 2.5D curtinho: o Furtão, o valentão da vila, roubou o Macaco Fedido (o primeiro brinquedo do Timtim, fedido de tanto ser mordido), e o Timtim, a Zara e o Elvis partem para resgatá-lo. A abertura tem três quadros pintados com a frase escrita no pergaminho e a voz de um narrador; a fase começa com o Furtão passando com o macaco na boca, rindo e fugindo; no fim da luta o macaco pula dele e a turma comemora. Os dois amigos chihuahuas esperam no caminho e dão poderes (turbo e invencibilidade). Uma partida leva em torno de 2 minutos.

## Como jogar
- ← → / A D: andar · Espaço / ↑ / W: pular (segure para pular mais alto; aperte de novo no ar para a pirueta, um pulo duplo) · ↓ / S: farejar · P ou Esc: pausa · M: som
- Celular: botões na tela (👃 fareja). Controle (gamepad): direcional + botão A; direcional para baixo fareja.
- **Fases:** o jogo tem duas fases. A 1, o Parque, abre com a história; vencer o Parque libera a 2, o Arraial (botão "Próxima fase" na vitória e os botões de fase no título). A fase vem do endereço: `index.html?fase=2`.
- 🪁 Planar (fase 2): no ar, segure o pulo depois do topo e a bandana abre como asa-delta; a queda fica lenta. Em cima de uma fogueira, o ar quente levanta quem está planando. Encostar na chama tira um coração.
- 🥚 Ovo cozido (fase 2): a comida preferida do Timtim. No Arraial, a Zara e o Elvis jogam ovo cozido em vez de biscoito: o primeiro dá o planar turbinado por 12 s (queda bem mais lenta e o ar quente sobe mais), o segundo deixa invencível.
- 🐔 Galinhas caipiras (fase 2): no Arraial, o lugar dos pombos é delas. Mesma regra: pise por cima. Chegando perto, elas ficam agitadas como galinha de verdade: fogem cacarejando aos pulinhos, batendo as asas e soltando penas; encurraladas, disparam passando pelo Timtim. Em quatro pontos da fase vem uma debandada: poeira e cacarejo na beirada direita avisam, e um bando passa correndo da direita para a esquerda (fugindo do lobo-guará). Pule por cima: caindo em cima de uma, o Timtim quica; encostar de lado machuca.
- 🎣 Brincadeiras juninas (fase 2, segredos): pular dentro do tanque da pescaria solta 5 biscoitos; atravessar a argola pendurada sobre a quadrilha revela um biscoito dourado.
- 💌 Correio elegante (fase 2): 4 bilhetes escondidos, cada um com uma piada da turma (do Elvis, da Zara e dos cães da vila). A vitória mostra quantos você achou.
- 💃 Quadrilha (fase 2): as tábuas com bandeirinhas vão e voltam no ritmo da dança e levam o Timtim junto.
- 👃 Faro: segurando ↓, o Timtim para e fareja, e um rastro verde aponta o segredo mais próximo (biscoito dourado, moita falsa, caminho de cheiro). Sem segredo por perto, o rastro segue o cheiro do Macaco Fedido.
- Moita falsa: logo atrás do ponto de partida, um arbusto onde dá para entrar esconde 3 biscoitos.
- Caminho de cheiro: perto do primeiro checkpoint, lajes invisíveis que o faro revela levam ao brinquedo perdido da fase, o Patinho Quá-Quá. Os brinquedos achados ficam na estante "Brinquedos perdidos", na tela de título, e são salvos no navegador.
- 🍪 Biscoito: pontos (não há outros poderes soltos pela fase; só os presentes dos amigos)
- 🍫 Chocolate: dá dor de barriga e deixa o Timtim lento por 5s (pule por cima)
- 🐶 Amigos chihuahuas: os dois esperam no caminho e, quando o Timtim chega perto, jogam um biscoito de presente (+3 biscoitos e +1 coração; o primeiro dá turbo, o segundo deixa invencível). São os únicos poderes da fase.
- Pombos: pise por cima.
- Chefão do Arraial, o Lobo-guará: invadiu o galinheiro. Quando o Timtim chega, ele está caçando três galinhas, que fogem passando pelo Timtim (eram delas as debandadas da fase). Ponto fraco: o lombo, onde fica a crina. Ele é alto, então o pulo comum só bate na canela (ele dá um passo para trás e o Timtim quica); para acertar, suba no ar quente das fogueiras dos cantos e desça planando na crina. Com brilho dourado ele fica de lombo baixo e até o pulo comum acerta: fuçando o chão depois do bote, tonto depois de bater na cerca e comendo a fruta-do-lobo. Ataques, sempre com aviso vermelho: o bote (o salto alto de lobo-guará, com uma marca no chão de onde vai cair), a corrida (cava o chão e atravessa a arena; pule e plane por cima) e, do 2º coração em diante, o latido rouco (apaga o ar quente das fogueiras por 2 s e derruba quem estiver planando). No 3º coração ele fica mais rápido e às vezes emenda o bote com a corrida. A Zara e o Elvis se revezam: ovo cozido para o Timtim (planar turbinado) e fruta-do-lobo no chão (ele para para comer). No terceiro golpe, as galinhas saem do galinheiro e expulsam o lobo-guará para a mata.
- Chefão do Parque, o Furtão: 3 corações e um ataque novo a cada um (investida, latidão com onda no chão, pisão do terremoto). Pisar nele não adianta, ele sacode o Timtim para o alto. De tempos em tempos a Zara ou o Elvis jogam uma bolinha: ele corre atrás e fica mordendo, e só nessa hora o pisão na cabeça acerta.
- Estrelas: 1 por vencer, 1 por pegar 80% dos biscoitos, 1 por achar os 3 biscoitos dourados (só o pulo duplo alcança).

## Rodar
O jogo usa WebGL, então precisa de um servidor (abrir o arquivo direto não carrega as imagens):
```
cd game && python3 -m http.server 8765   # abrir http://localhost:8765
```
`?q=0`, `?q=1` ou `?q=2` na URL fixa a qualidade gráfica; sem isso ela se ajusta sozinha ao aparelho.

## Estrutura
| Arquivo | Papel |
|---|---|
| `src/game.js` | Regras: física, inimigos, chefão, checkpoints, fluxo. Avisa o resto por eventos. |
| `src/render3d.js` | Cenário 3D (three.js) desenhado por código, sprites, sombras, luzes, partículas, câmera e pós-processamento. |
| `src/ui.js` | Controles, placar, telas e transições (HTML/CSS). |
| `src/intro.js` | Abertura: três quadros pintados (`assets/intro`) com vento, vaga-lumes e a frase escrita no pergaminho. |
| `src/audio.js` | Narração da abertura (`assets/voice`, gerada no Artlist), efeitos gravados (`assets/sfx`) e trilhas gravadas (`assets/music`), tocadas em laço. Versões sintetizadas no navegador cobrem enquanto os arquivos carregam. |
| `src/main.js` | Laço principal e qualidade adaptativa. |
| `docs/design.md` | Decisões de design e de arte. |
| `docs/plano-fases.md` | Plano das próximas fases, truques e segredos, e o que já foi feito. |
| `tests/smoke.js` | Teste automático do caminho crítico da fase 1 (`node game/tests/smoke.js`). |
| `tests/smoke-arraial.js` | Teste automático da fase 2: planar, ar quente, chama, tábuas da quadrilha, sanfoninha, ovo, galinha agitada, pescaria, argola, correio elegante, debandada, a caçada e a luta com o lobo-guará (latido, fruta-do-lobo, golpe final) (`node game/tests/smoke-arraial.js`). |

Arte dos personagens gerada no Higgsfield a partir das fotos do Timtim; os chihuahuas foram recortados da folha de personagens. O Timtim farejando e planando, o Patinho Quá-Quá e o fundo da estante (`assets/bg/shelf.jpg`) foram gerados no Google Flow. Cada fase tem uma cor: a fase 1 é azul, em homenagem à linguagem visual de Ori (floresta noturna pintada `assets/bg/floresta-azul.jpg`, silhuetas de primeiro plano, plantas de pântano e flores de luz do Google Flow, o resto do pântano noturno desenhado por código) e a fase 2 é laranja, na mesma linguagem em dourado (arraial numa clareira da mata `assets/bg/arraial-mata.jpg`, lanternas de cabaça, barracas, fogueiras e mastro do Google Flow; o lobo-guará em seis poses, a fruta-do-lobo, o galinheiro e o bilhete do correio elegante também). Trilha do Arraial: 100 BPM; quando o arquivo `assets/music/arraial.mp3` existir, ligue `ARRAIAL_PRONTA` em `src/audio.js` e a quadrilha, as fitas e a argola passam a dançar no tempo da música. Ver a tabela em `docs/design.md`. `vendor/three.min.js` é a three.js r149 (licença MIT).
