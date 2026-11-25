# Revisão "hater" — 24/11/2026

Pedido do Pedro: jogar o jogo inteiro com olho de quem odeia o jogo, achar 50 erros e incoerências e resolver.
Fontes: os pontos que ele mandou (1 a 7), o jogo jogado e fotografado trecho a trecho (fases 1 e 2, título, história,
planada quadro a quadro) e uma leitura completa do código por um segundo revisor.

Legenda: ✅ corrigido · ➖ mantido de propósito (com o motivo) · ⏳ depende de algo de fora (arquivo ou aprovação)

## Os pontos do Pedro
1. ✅ **Abertura da fase 1 esquisita.** Quando o Furtão ria, o Timtim dava um pulinho e tocava a animação de *levar dano*; o tamanho mudava a cada quadro. Agora ele fica parado, encarando o ladrão, e leva um susto (estica e volta). Só se vira quando o Furtão aparece na tela.
2. ✅ **Movimentos guiados pelos chefões.** A queda e a planada agora usam os quadros de vídeo do próprio pulo, como os chefões (antes, no topo de todo pulo, trocava para um desenho parado de outro estilo). As patas do Furtão na abertura acompanham a velocidade real (antes patinavam enquanto ele freava).
3. ✅ **Planada com bug grave.** Eram três problemas juntos:
   - ao abrir, o Timtim virava outra figura, 1,7× mais larga, com outras manchas e duas bandanas;
   - no alto do ar quente a planada ligava e desligava 3 a 5 vezes por segundo (som de pirueta repetindo, capa abrindo e fechando);
   - ao sair da coluna pelo lado, subindo, a planada se desligava.
   Agora o corpo é o mesmo do pulo, só a bandana abre atrás como asa (um pano que ondula), e a planada tem memória: não pisca mais. Tem também um som próprio, de vento no pano.
4. ✅ **Fogueira cobria os personagens.** Ela foi para trás de todos (inclusive o lobo, as galinhas e os amigos).
5. ✅ **Erros gerais.** Ver a lista abaixo.
6. ✅ **Opção de jogar a fase 2 no começo.** O seletor de fases saiu do título. A fase 2 chega sozinha ao vencer a 1.
7. ✅ **Bug depois da frase da fase 2.** O cartão "O ARRAIAL" aparecia exatamente em cima do Timtim e o escondia. Agora fica no alto da tela. O carregador também avisava "tudo pronto" mais de uma vez, o que podia apertar "Jogar" de novo e cortar a história; agora só avisa uma vez.

## Fase 2 — Arraial
8. ✅ O título da fase 2 mostrava a floresta azul e o Furtão (vilão da fase 1). Agora mostra o fundo pintado do próprio arraial, sem personagens.
9. ✅ O cartão do Arraial repetia a mesma frase da história. Agora diz o que fazer: "Siga as galinhas assustadas até o galinheiro."
10. ✅ As galinhas da patrulha morriam de cabeça para baixo quando pisadas, numa fase sobre *salvar* galinhas. Agora o Timtim quica e ela foge assustada.
11. ✅ A galinha encurralada disparava para cima do Timtim e tirava coração. Disparando, ela passa sem bicar.
12. ✅ A primeira debandada vinha sem aviso nenhum. Agora tem cacarejo e a faixa "Galinhas em disparada! Pule por cima delas!".
13. ✅ O aviso da debandada era um clarão branco estourado na borda da tela. Agora é poeira de terra.
14. ✅ Havia uma debandada dentro da aula do planar (as galinhas cruzavam o primeiro vão tirando coração justo onde cair "não custa nada"). Saiu.
15. ✅ Só a partir da 9ª galinha correndo elas ficavam invisíveis (e ainda machucavam). Agora são desenhadas até 14.
16. ✅ O fundo dos buracos era azul-marinho chapado, da fase 1. Agora é terra escura.
17. ✅ As silhuetas da frente eram manchas quase pretas cortadas no canto da tela. Ficaram marrom-escuras e se leem como folhagem.
18. ✅ Voltar da aula do planar punha o Timtim *dentro* do palco de madeira (ele atravessava caindo). Agora volta em cima dele.
19. ✅ Do 3060 ao 6340 não havia ponto de controle (fogueiras e quadrilha inteiras). Novo ponto em 5900.
20. ✅ A Sanfoninha fica no alto da coluna de ar quente, mas era invisível e impossível de pegar sem farejar antes. Subir planando até ela agora revela o caminho.
21. ✅ O tanque da pescaria só funcionava caindo de cima. Entrando andando também solta os biscoitos.
22. ✅ O ovo dos amigos somava +3 biscoitos ao contador. O ovo não é biscoito; não soma mais.
23. ✅ O presente em voo curava e dava poder *depois* da derrota (o coração reacendia por trás do "Ah, não!"). Não cura mais.
24. ✅ A dica dizia "As tábuas dançam a quadrilha: pule no ritmo!", mas são peneiras e não há ritmo (a música do Arraial ainda não existe). Virou "As peneiras dançam a quadrilha: pule na hora certa!".
25. ✅ A dica do título no computador dizia "segure no ar: planar" sem dizer a tecla, e não falava do faro (que existe na fase 2). Corrigida.

## Luta do lobo-guará
26. ✅ Zara e Elvis ficavam dentro das fogueiras dos cantos da arena (e os ovos e a fruta "saíam do fogo"). Foram para mais perto do meio.
27. ✅ A luta podia começar com o lobo colado no Timtim, onde ele estava caçando as galinhas. Agora começa do outro lado da arena.
28. ✅ Subir no ar quente por dentro do lobo cansado empurrava o Timtim para fora, bem na hora de acertar a crina. Na hora certa, não empurra mais.
29. ✅ O latido derrubava qualquer um no ar, de qualquer distância (até um pulo comum do outro lado). Agora só derruba quem está planando perto dele.
30. ✅ O dano empurrava o Timtim para trás de onde ele olhava, às vezes para dentro do perigo. Agora o empurrão é para longe de quem bateu.
31. ✅ A luta tocava a música da fase, e a revanche, a música de chefão. As duas tocam a de chefão.
32. ✅ As dicas da estratégia ("1. Suba no ar quente…", "2. Plane…") apareciam depois de perder ou recomeçar. Agora são canceladas.
33. ✅ Os avisos de primeira vez ("O latido apaga o ar quente!", "Fruta-do-lobo!") nunca voltavam depois de recomeçar. Voltam.
34. ✅ Corrida do lobo, fuçada no chão, pulo do Furtão e biscoito dourado eram mudos. Ganharam som.
35. ➖ Antes da arena, o lobo e as galinhas caçadas passam pelo Timtim sem efeito. É a cena da perseguição e ninguém está atacando ainda; ficou assim.

## Planada e Timtim
36. ✅ Machucado, ele subia na coluna na pose de dor. Machucado não plana.
37. ✅ No quadro do pouso ficava um quadro de asa aberta no chão. Sumiu.
38. ✅ Os rastros de luz (pirueta, turbo) saíam espremidos, afundados e com outra arte. Usam o mesmo quadro do Timtim.
39. ✅ A pirueta girava em volta de um ponto 15 px fora do centro (o corpo fazia um arco). Gira no meio do corpo.
40. ✅ Ele nascia 10 px acima do chão: todo começo tinha pouso com poeira e som. Nasce no chão.
41. ➖ Primeiro aperto no ar = pirueta, segurar depois = planar. É a regra do jogo desde a fase 1 e está na dica.

## Fase 1
42. ✅ "Tentar de novo" antes do primeiro ponto de controle repetia a cena do roubo inteira (4,6 s) toda vez. Agora a cena só passa na primeira vez.
43. ✅ A pausa dizia "O Timtim está olhando o pôr do sol", numa fase que é noite azul. Agora: "parou para olhar os vaga-lumes".

## Interface e fluxo
44. ✅ Na vitória, Enter/Espaço apertava "Jogar de novo" em vez de "Próxima fase". Quem apertava pulo no fim recomeçava a fase.
45. ✅ A contagem para a próxima fase começava antes de a tela aparecer (já surgia em 6). Agora começa em 8 quando a tela aparece.
46. ✅ No controle (gamepad), as telas de derrota, vitória e estante não tinham saída. Start ou A apertam o botão principal.
47. ✅ "toque para avançar" aparecia no computador. Agora: "clique ou Espaço para avançar".
48. ✅ Faixas longas podiam sair da tela (texto numa linha só). Agora quebram em duas no máximo e ficam centralizadas.
49. ✅ "Lobo-guará" não cabia no rótulo da barra do chefão.
50. ✅ A estante dizia "faro (↓)" também no celular, e contava "0 de 5" incluindo as fases "Em breve". Mostra 👃 no toque e conta só os brinquedos que existem.
51. ✅ "expulsarem ele" → "o expulsarem" no texto da vitória.
52. ✅ O comentário do código dizia que a chama machuca; não machuca. O código morto da caixa de fogo saiu.

## O que ficou de fora (precisa de algo seu)
53. ✅ A galinha cacarejava com o som do pombo. Agora tem sons do Artlist (aprovados): dois cacarejos de susto alternados, galinhas em disparada no aviso da debandada, bater de asas quando o Timtim quica nelas e o galinheiro em alvoroço quando expulsam o lobo.
54. ⏳ O Arraial ainda toca a música do Parque. Falta o arquivo da trilha do Suno (`assets/music/arraial.mp3`).
55. ⏳ A tela da história da fase 2 foi retirada: a imagem gerada no Artlist mostrava um cachorro que não é o Timtim (parecia um border collie). Ela volta só com uma arte nova, com o Timtim fiel ao personagem e aprovada antes.

## Segunda rodada (depois do retorno do Pedro, 24/11 à noite)
Desta vez as duas fases foram atravessadas de ponta a ponta, sem teleporte, com o Timtim correndo, pulando e planando, e uma foto a cada 0,6 s de jogo. Também gravei o Furtão quadro a quadro na abertura, na apresentação e na derrota.

56. ✅ **Aura em volta dos personagens.** O contorno de luz do Timtim (e, no Arraial, de todos os bichos) parecia uma aura recortada. Saiu.
57. ✅ **Zara andando no ar sobre o buraco.** Os amigos agora param na beirada.
58. ✅ **Correio elegante no meio da tela.** Virou um bilhete pequeno no canto esquerdo, logo abaixo dos corações (antes também cobria os botões de música e pausa).
59. ✅ **Defeito no Furtão.** O pelo claro do peito era parecido com o fundo cinza do vídeo e foi apagado junto, abrindo um buraco por onde apareciam os cogumelos de trás. O recorte agora deixa o miolo do corpo opaco, e todas as animações foram refeitas.
60. ✅ **Timtim comemorava dentro do corpo do Furtão derrotado.** Agora desce de cima dele e comemora do lado, virado para ele.
61. ✅ A tela de carregamento da fase 2 mostrava a frase da fase 1 ("Ajude Timtim a resgatar o Macaco Fedido…").
62. ✅ O balão de fala dos amigos saía cortado na borda da tela. Agora fica sempre dentro dela.
63. ✅ Planando alto (argola, ar quente), o Timtim ficava colado no topo, embaixo do placar. A câmera sobe junto, também na arena do lobo.
64. ✅ Um galho quase preto atravessava o meio da tela no Arraial. Os galhos ficaram num marrom quente, meio transparentes e mais altos.
65. ✅ As faixas de dica (texto branco com brilho claro) sumiam sobre o fundo claro do Arraial. Ganharam sombra escura.
66. ✅ Na fase 1, as raízes penduradas das plataformas cobriam o Timtim quando ele pulava por baixo. Ficaram atrás dele.
67. ✅ O ovo voando até o Timtim era tão grande e claro que cobria a cabeça dele. Ficou menor.
