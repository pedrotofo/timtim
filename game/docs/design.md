# Timtim e os Brinquedos Perdidos — design em uma página

**Promessa:** 2 a 3 minutos de plataforma que parecem um curta de animação estrelado por um cachorro de verdade. Feito para mostrar aos amigos.

## Pilares
1. **É o Timtim.** Mancha preta, bandana de festa junina, lacinho. O varal de luzinhas do parque repete as cores da bandana.
2. **Fluidez antes de tudo.** Pulo variável, pulo duplo com pirueta, um instante de flutuação no topo do pulo, tolerância na borda (coyote time, 0,1s), pulo antecipado (buffer, 0,12s), câmera que olha à frente e acompanha a altura.
3. **Impacto.** Cada pisão congela o jogo por um instante (hitstop), treme a câmera e solta faíscas de luz. O golpe final é em câmera lenta.
4. **Piada interna.** Os chefões são cães e bichos da vizinhança, com cena de apresentação própria: o **Furtão** (cão marrom) na fase 1, o **lobo-guará** na fase 2, o **Corvo-Borrão** na fase 3. A **Zara** (chihuahua preta e branca) e o **Elvis** (chihuahua branco) esperam no caminho e dão biscoito. *(Corrigido em 28/11/2026: a linha dizia "os pugs da vizinha", da ideia original; não há pug no jogo, e "sprites dos pugs reais" segue fora do escopo, no fim deste documento.)*

## Direção de arte: cada fase tem uma cor e um sentimento

> Desde 28/11/2026 existe `design/art/art-bible.md`, que **manda** onde os dois documentos falarem
> da mesma coisa. Ele fecha as superfícies de marca (capa, logo, cards, tipografia), a linguagem de
> forma por arquétipo e o sistema de cor; aqui fica o detalhe de cada fase.
Regra (Pedro, 24/11/2026): cada fase tem **uma cor predominante e um sentimento próprio**, para ficar claro que mudou de fase. A paleta é da fase inteira, não muda ao longo do caminho (`dayLight` em `render3d.js`).

| Fase | Cor | Sentimento | O que compõe |
|---|---|---|---|
| 1 · O Parque | **azul** | noite soturna, misteriosa, "cara de pântano"; homenagem à linguagem visual de *Ori and the Will of the Wisps* | floresta noturna pintada com raios de luz, névoa em camadas e uma figueira anciã brilhando em ciano ao longe (`bg/floresta-azul.jpg`), o Timtim com luz própria fria e contorno ciano, silhuetas escuras de raízes, samambaias e galhos com borda ciano no primeiro plano (`props/frente-*.png`), flores de luz magenta como acento quente, figueiras com lanternas, varais de luzinhas, lajes de pedra com musgo luminoso e raízes, sebe escura com florzinhas acesas, plantas de pântano ao luar (samambaia, taboa, cogumelos com brilho ciano), esporos azuis e violeta |
| 2 · O Arraial | **laranja** | festa quente, aconchegante, iluminada por fogueiras; a mesma linguagem visual de Ori da fase 1, em dourado | um arraial escondido numa clareira da mata ao entardecer, com névoa dourada contra a luz, raios de sol, fumaça das fogueiras e casinhas sobre palafitas (`bg/arraial-mata.jpg`), lanternas de cabaça penduradas balançando, silhuetas com borda dourada no primeiro plano (`props/frente-arraial-*.png`, `props/galhos-arraial.png`), contorno dourado no Timtim, troncos gigantes da mata espaçados no meio do cenário (`props/troncos.png`), plataformas que são deques de madeira sobre palafitas (troncos com casca e amarração de corda), tábuas da quadrilha que são peneiras de palha trançada com fitas, tochas de bambu no lugar dos postes e no checkpoint, barracas, bandeirinhas, fogueiras, mastro de São João, tábuas penduradas, terra batida |
| 3 · O Quadro Encantado | **o quadro de Van Gogh** | entrar numa pintura: pincelada que ondula, céu em espiral, girassóis | o mundo do quadro depois que o Corvo-Borrão rouba o pincel do Van Gogh. Paleta em `VGP` (`render3d.js`): fundo `#0c1430`, névoa `#7088c8`, facho `#f6e08a`, ambiente `#fff2d8`. A sombra é quase neutra (`shade (.96, .97, 1.04)`), então aqui a hierarquia vem de **valor e direção de pincelada**, não de temperatura — e o piso tem de ficar mais reto que em qualquer outra fase (ver `design/art/art-bible.md`, Seção 3) |
| 4 · Dia de Chuva | (a definir) | | |
| 5 · O Covil do Furtão | (a definir) | | |

Homenagem a Ori (24/11/2026): vem da linguagem visual (silhueta primeiro e luz depois, herói pequeno e luminoso num mundo grande, camadas em movimento, raios de luz, bioluminescência, paleta por região), nunca de personagens, lugares, árvores-símbolo ou música do jogo. Tudo no cenário continua sendo do parque do Timtim.

Cada fase tem elementos próprios, não só cor (24/11/2026): plataformas, árvores do meio do cenário, iluminação e checkpoint mudam de uma fase para outra. Fase 1: lajes de pedra com musgo e raízes, figueiras com lanternas, postes, varais de luzinhas e lanterna no poste. Fase 2: deques sobre palafitas, peneiras de palha, troncos gigantes, tochas de bambu e lanternas de cabaça (sem varais de luzinhas, sem postes nem bancos de praça). Inimigo: pombo na fase 1, galinha caipira de chapéu de palha na fase 2 (mesma regra: pisar por cima tira ela do caminho, encostar de lado machuca; a galinha ainda foge agitada quando o Timtim chega perto). Chefe: o Furtão na fase 1 (cão), o Lobo-guará na fase 2 (salvar o galinheiro; as debandadas de galinhas pela fase são as que fugiram dele); cada chefe pede a ação da sua fase (no Arraial, cair planando).

O que **não** entra na fase 1: bandeirinhas, cenário colorido ou "feliz", vila ao entardecer, marcos coloridos da praça (chafariz, coreto, carrinho de pipoca: foram testados e reprovados em 24/11/2026).
- **Profundidade por valor.** Quanto mais longe, mais claro (rosado no entardecer, azulado à noite); quanto mais perto, mais escuro. O primeiro plano é quase preto e desfocado.
- **A luz conta a história.** Luz quente e baixa, sombras roxas. O que importa para jogar brilha: o Timtim tem um halo suave, os biscoitos são luzes douradas, os postes fazem poças de luz âmbar.
- **O mundo respira.** Fachos de sol, névoa, flores e cogumelos que pulsam, vaga-lumes, capim na frente dos pés.
- **Movimento elástico.** O corpo do Timtim estica e achata com uma mola, inclina com a velocidade, e deixa um rastro de silhuetas de luz na pirueta e no turbo.
- **O Timtim tem o mesmo tamanho em todas as poses.** As alturas em `R.frame` (parado 80, correndo 82, pulo 77, queda 82, farejando 69) foram acertadas para a cabeça dele não mudar de tamanho ao trocar de pose; antes ele encolhia uns 20% no pulo.
- **O Furtão é marrom**, como na abertura pintada (antes o jogo o deixava cinza-azulado).
- **Interface discreta.** Vidro escuro, contornos finos de luz, letras serifadas que brilham. Nada de contorno grosso.

## 2.5D
- O mundo é 3D de verdade: piso em blocos (os buracos são vãos), camadas de árvores a até 2.200 unidades de distância, céu no infinito. O parallax vem da perspectiva, não de truque.
- O cenário é desenhado por código (texturas de canvas): dá controle total da paleta e não depende de imagens.
- Personagens são sprites em pé no plano z=0 e projetam sombra recortada no chão.
- A câmera tem direção fixa e só desliza, aproxima e treme: nunca gira.
- Pós-processamento: profundidade de campo (plano do jogo nítido), bloom largo, sombras puxadas para o roxo, vinheta e grão.
- Animação de corrida avança conforme a distância percorrida, para as patas não patinarem.

## Ritmo da fase
Início seguro com biscoitos no chão → primeiras lajes → primeiro buraco → **amigo preto e branco** (biscoito de presente) → banana (turbo) → checkpoint → macaco (invencível) → **amigo branco** → trecho final → parquinho → cena dos pugs → luta.

## Qualidade adaptativa
Três níveis. Se a média cair abaixo de 45 quadros por segundo: nível 1 desliga o desfoque e reduz a resolução; nível 0 desliga sombras, pós-processamento, névoa, parte dos fachos e dos halos.
Todas as imagens vão para a placa de vídeo ainda no carregamento (`warmUp`), para o primeiro segundo da fase não engasgar.

## Arte quase realista, sempre dentro da cor da fase (24/11/2026)
- Arte quase realista (Google Flow) é bem-vinda quando é graduada para a paleta da fase: as plantas de pântano da fase 1 já foram geradas ao luar azul; a arte do Arraial é tingida de laranja.
- Brilhos ficam para o que importa para jogar (biscoitos, brinquedo, chama, checkpoint) e para as luzes de verdade (postes, varais, fogueiras).
- Pular no Furtão nunca tira coração: cair por cima conta como pisão, e durante a sacudida que ele dá o contato não machuca.

## Contraste à moda de Ori (25/11/2026)

Uma cor dominante só funciona com planos de luz bem separados. Regras, tiradas de Ori and the Blind Forest:
1. três planos de valor: primeiro plano quase preto (emoldura em cima e embaixo), plano do jogo em tom médio, fundo claro e
   enevoado, sem contraste nem saturação (`hazeK` no fundo pintado);
2. o herói é o mais claro da tela e tem uma poça de luz em volta (`hero`/`heroK` na composição final);
3. luz quente contra sombra fria: no Arraial laranja, as sombras puxam para o roxo (`shade`);
4. borda acesa: um filete de luz na quina de cima do chão e de cada plataforma mostra onde se pisa;
5. quem se mexe tem contorno de luz fria; o vilão fica um tom mais escuro, como silhueta contra a névoa.

## Movimento quadro a quadro, tirado de vídeo (24/11/2026)

Personagens se movem com quadros de verdade, não com uma pose só deformada. O caminho que funciona: a arte do personagem
sobre cinza liso vira o primeiro quadro de um vídeo curto no Google Flow ("andando sem sair do lugar, câmera parada"); do
vídeo sai um ciclo completo (corrida, andar) ou um trecho que toca em vai e volta (parado, latindo, comendo, tonto). Quadros
desenhados um a um pela IA variam entre si e a animação treme; os do vídeo são contínuos. A deformação por código
(rabo, orelhas, respiração) fica só para as poses que ainda são paradas (bote, agachado, pulo duplo).

## O som não é física (28/11/2026)

Nenhuma mecânica deste jogo pode depender de ouvir. O som **confirma e antecipa**; quem decide se dá
para pisar é a imagem. O relógio da música (`TT.beatClock`) pode enfeitar — pulso das lanternas, brilho
das tábuas, uma batida que o cenário acompanha — e **nunca** ser a física: as regras do jogo andam todas
em `S.clock`, no passo fixo de 1/240 s.

Veio do pente fino: as tábuas da quadrilha andavam em `ctx.currentTime`, que não congela na pausa nem
anda no passo do jogo. Media 195,3 px de teleporte lateral num só passo depois de 3,7 s de pausa (basta
trocar de aba) e 1,55× a velocidade de projeto sem pausa nenhuma, com picos de 16× — ou seja, a
velocidade das plataformas do vão de 1380 px dependia da máquina de quem jogava. O `beatClock` que
sobrou é contínuo e monotónico: troca de trilha, laço da música ou aba escondida não fazem o enfeite
pular nem voltar.

## Fora do escopo (por enquanto)
Mais fases, mais quadros de animação (a corrida tem 4), animações próprias para os chihuahuas, sprites dos pugs reais, placar online.
