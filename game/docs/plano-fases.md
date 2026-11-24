# Plano: novas fases, truques e segredos

Regra: **cada fase nova ensina uma única ação nova**, e cada uma dura uns 2 minutos, que é a promessa do jogo.
Artes conceituais de tudo isto: `video/previa-novidades/` (página `index.html` e as imagens 0 a 9).

## A ideia central: o faro do Timtim
O Macaco Fedido é fedido, e isso vira mecânica. Segurando ↓, o Timtim fareja e aparece um rastro verde de cheiro.
Ele mostra o caminho e aponta segredos: paredes falsas, biscoitos escondidos e brinquedos perdidos.

## Fases da Vila de Reserva
Um mapinha da vila liga as fases, e o progresso fica salvo no navegador.

| # | Fase | Ação nova | Momento marcante |
|---|---|---|---|
| 1 | O Parque (a que já existe) | correr, pular, pirueta, **farejar** | a luta com o Furtão |
| 2 | O Arraial | planar com a bandana (segurar o pulo no ar) | o ar quente da fogueira levanta o Timtim; na quadrilha, as plataformas de bandeirinhas mexem no ritmo da música |
| 3 | O Quintal da Vizinha, à noite | se esconder atrás de arbustos | a luz da lanterna varre o quintal; o rastro de cheiro guia no escuro |
| 4 | Dia de Chuva | escorregar nas poças, por baixo dos bancos | fuga da hora do banho: a tela anda sozinha e o Timtim foge da banheira |
| 5 | O Covil do Furtão (ferro-velho) | tudo junto | revanche em duas etapas, com Zara e Elvis ajudando ao vivo |

## Truques para quem joga bem
- Quicada turbo: apertar pulo exatamente ao pisar num pombo faz o Timtim quicar bem mais alto.
- Combo no ar: pisar em vários pombos seguidos sem tocar o chão multiplica os biscoitos (×2, ×3…).
- Escorregão longo: pular no fim de um escorregão vai mais longe (fase 4).
- Latido (botão novo): espanta pombos, derruba caixas frágeis e faz o Furtão virar a cabeça por um instante.
- Fantasma do melhor tempo: uma silhueta corre o seu recorde junto com você.

## Segredos
- Brinquedos perdidos: um por fase, roubados pelo Furtão de outros cães da vila. Vão para a estante, cada um com uma piadinha sobre o dono.
- Fase secreta "O Sonho do Timtim": uma almofada escondida no Quintal leva a um sonho com nuvens de biscoito.
- Final alternativo: vencer o Furtão sem perder coração e com todos os brinquedos faz ele devolver tudo e virar amigo.
- Pombo dourado: raro (uma partida a cada vinte); pisar nele dá uma bandana nova.
- Detalhes: parado 10 s, o Timtim deita e coça a orelha; digitar TIMTIM no título destrava o Timtim de pijama; 3 estrelas em tudo destrava um modo "pôr do sol".

## Ordem de construção
1. **Feito:** faro, moita falsa e caminho de cheiro na fase atual, com o primeiro brinquedo (Patinho Quá-Quá) e a estante.
2. **Feito (24/11/2026):** fase 2, o Arraial, com o planar. Trechos: palco e primeiro vão (só planando) → vão maior → fogueiras (a chama machuca; o ar quente levanta quem plana) → quadrilha (quatro tábuas que dançam e levam o Timtim) → tudo junto, com a sanfoninha no alto da terceira fogueira (o faro revela o caminho) → mastro de São João. Dados em `game.js` (bloco `FASE === 2`), cenário em `render3d.js` (bloco `ARR`), teste em `tests/smoke-arraial.js`.
3. Mapa da vila com progresso salvo. Por enquanto as fases se escolhem por botões no título, liberados conforme a fase anterior é vencida (`tintim-fases` no navegador).
4. As outras fases, uma por vez.

## Artes
Geradas no Google Flow (Nano Banana Pro, 24/11/2026) com a folha de personagem e o `tintim-idle` como referência, sobre fundo cinza liso, e recortadas com alfa suave no pelo:
- **Feito:** `sprites/tintim-sniff.png`, o Timtim farejando de perfil, focinho no chão (entra quando `p.sniff > 0`).
- **Feito:** `sprites/toy-duck.png`, o Patinho Quá-Quá mordido no rabo e no bico (na fase e na estante).
- **Feito:** `bg/shelf.jpg`, a casinha de madeira à noite com 5 nichos, varal de luzes e bandeirinhas (fundo da estante).
- **Feito, ainda sem uso:** `sprites/tintim-glide.png`, o Timtim planando com a bandana aberta como asa-delta, para o Arraial.


- **Feito (24/11/2026):** cor por fase. Fase 1 azul: plantas de pântano ao luar (`props/pantano-*.png`). Fase 2 laranja: `bg/vila-laranja.jpg`, barracas, pescaria, fogueira, mastro, sanfoninha, texturas de terra e madeira, capim, hera, folhagem, plantas, banco e poste (`assets/props/`, `assets/tex/`).
- Testado e reprovado na fase 1 (24/11/2026): vila do entardecer à noite, bandeirinhas, chafariz, coreto, carrinho de pipoca, sebe florida, gramado e paralelepípedo realistas. Deixaram a fase genérica e colorida demais.

Ainda falta: uma trilha própria de forró para o Arraial (hoje ele usa a música da fase 1) e a arte de abertura pintada do Arraial (hoje é um cartão de texto).
