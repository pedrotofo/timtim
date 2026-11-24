# Timtim e o Resgate do Macaco Fedido

Jogo de plataforma 2.5D curtinho: o Furtão, o valentão da vila, roubou o Macaco Fedido (o primeiro brinquedo do Timtim, fedido de tanto ser mordido), e o Timtim, a Zara e o Elvis partem para resgatá-lo. A abertura tem três quadros pintados com a frase escrita no pergaminho e a voz de um narrador; a fase começa com o Furtão passando com o macaco na boca, rindo e fugindo; no fim da luta o macaco pula dele e a turma comemora. Os dois amigos chihuahuas esperam no caminho e dão poderes (turbo e invencibilidade). Uma partida leva em torno de 2 minutos.

## Como jogar
- ← → / A D: andar · Espaço / ↑ / W: pular (segure para pular mais alto; aperte de novo no ar para a pirueta, um pulo duplo) · ↓ / S: farejar · P ou Esc: pausa · M: som
- Celular: botões na tela (👃 fareja). Controle (gamepad): direcional + botão A; direcional para baixo fareja.
- **Fases:** o jogo tem duas fases. A 1, o Parque, abre com a história; vencer o Parque libera a 2, o Arraial (botão "Próxima fase" na vitória e os botões de fase no título). A fase vem do endereço: `index.html?fase=2`.
- 🪁 Planar (fase 2): no ar, segure o pulo depois do topo e a bandana abre como asa-delta; a queda fica lenta. Em cima de uma fogueira, o ar quente levanta quem está planando. Encostar na chama tira um coração.
- 💃 Quadrilha (fase 2): as tábuas com bandeirinhas vão e voltam no ritmo da dança e levam o Timtim junto.
- 👃 Faro: segurando ↓, o Timtim para e fareja, e um rastro verde aponta o segredo mais próximo (biscoito dourado, moita falsa, caminho de cheiro). Sem segredo por perto, o rastro segue o cheiro do Macaco Fedido.
- Moita falsa: logo atrás do ponto de partida, um arbusto onde dá para entrar esconde 3 biscoitos.
- Caminho de cheiro: perto do primeiro checkpoint, lajes invisíveis que o faro revela levam ao brinquedo perdido da fase, o Patinho Quá-Quá. Os brinquedos achados ficam na estante "Brinquedos perdidos", na tela de título, e são salvos no navegador.
- 🍪 Biscoito: pontos (não há outros poderes soltos pela fase; só os presentes dos amigos)
- 🍫 Chocolate: dá dor de barriga e deixa o Timtim lento por 5s (pule por cima)
- 🐶 Amigos chihuahuas: os dois esperam no caminho e, quando o Timtim chega perto, jogam um biscoito de presente (+3 biscoitos e +1 coração; o primeiro dá turbo, o segundo deixa invencível). São os únicos poderes da fase.
- Pombos: pise por cima.
- Chefão, o Furtão: 3 corações e um ataque novo a cada um (investida, latidão com onda no chão, pisão do terremoto). Pisar nele não adianta, ele sacode o Timtim para o alto. De tempos em tempos a Zara ou o Elvis jogam uma bolinha: ele corre atrás e fica mordendo, e só nessa hora o pisão na cabeça acerta.
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
| `tests/smoke-arraial.js` | Teste automático da fase 2: planar, ar quente, chama, tábuas da quadrilha, sanfoninha e mastro (`node game/tests/smoke-arraial.js`). |

Arte dos personagens gerada no Higgsfield a partir das fotos do Timtim; os chihuahuas foram recortados da folha de personagens. O Timtim farejando e planando, o Patinho Quá-Quá e o fundo da estante (`assets/bg/shelf.jpg`) foram gerados no Google Flow. Cada fase tem uma cor: a fase 1 é azul, em homenagem à linguagem visual de Ori (floresta noturna pintada `assets/bg/floresta-azul.jpg`, silhuetas de primeiro plano, plantas de pântano e flores de luz do Google Flow, o resto do pântano noturno desenhado por código) e a fase 2 é laranja (a vila em noite de fogueiras `assets/bg/vila-laranja.jpg`, barracas, fogueiras e mastro do Google Flow). Ver a tabela em `docs/design.md`. `vendor/three.min.js` é a three.js r149 (licença MIT).
