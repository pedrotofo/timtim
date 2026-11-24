# Timtim e o Resgate do Macaco Fedido

Jogo de plataforma 2.5D curtinho: o Furtão, o valentão da vila, roubou o Macaco Fedido (o primeiro brinquedo do Timtim, fedido de tanto ser mordido), e o Timtim, a Zara e o Elvis partem para resgatá-lo. A abertura tem três quadros pintados com a frase escrita no pergaminho e a voz de um narrador; a fase começa com o Furtão passando com o macaco na boca, rindo e fugindo; no fim da luta o macaco pula dele e a turma comemora. Os dois amigos chihuahuas esperam no caminho e dão poderes (turbo e invencibilidade). Uma partida leva em torno de 2 minutos.

## Como jogar
- ← → / A D: andar · Espaço / ↑ / W: pular (segure para pular mais alto; aperte de novo no ar para a pirueta, um pulo duplo) · ↓ / S: farejar · P ou Esc: pausa · M: som
- Celular: botões na tela (👃 fareja). Controle (gamepad): direcional + botão A; direcional para baixo fareja.
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
| `tests/smoke.js` | Teste automático do caminho crítico (`node game/tests/smoke.js`). |

Arte dos personagens gerada no Higgsfield a partir das fotos do Timtim; os chihuahuas foram recortados da folha de personagens. O cenário inteiro é desenhado por código em `render3d.js`, sem imagens de fundo. `vendor/three.min.js` é a three.js r149 (licença MIT).
