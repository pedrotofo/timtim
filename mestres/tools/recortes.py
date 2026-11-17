"""Recortes das cópias (img/cp-<obra>.jpg), balões de detalhe (tools/detalhes.json), linha do tempo (tools/tracos.json)
e imagens das aberturas de nível (tools/part_art.json). Coordenadas em fração da imagem em img/."""
import json
from PIL import Image
CP = {'n1_pillows': (.5, .06, .99, .4), 'n1_cats': (.25, .3, .97, .62), 'n1_boats': (0, .45, .62, .97), 'n1_paganini': (.28, .03, .78, .36),
      'n1_edith': (0, 0, 1, 1), 'n2_durer13': (.08, .08, .78, .62), 'n2_more': (.05, .05, .95, .78), 'n2_hands': (.18, 0, .72, .48),
      'n2_worn': (.04, 0, .96, .93), 'n2_dancer': (0, 0, 1, 1), 'n3_drapery': (0, .38, 1, 1), 'n3_hands': (.05, .05, .95, .95),
      'n3_ideal': (.05, .12, .7, .78), 'n3_sleeping': (0, .15, 1, .95), 'n3_yeats': (.12, .03, .88, .62), 'n4_mother': (.04, .12, .7, .68),
      'n4_girl': (.15, .15, .8, .78), 'n4_holbein_lady': (.08, .04, .88, .62), 'n4_schiele_man': (0, 0, 1, 1), 'n4_sibyl': (0, .55, .48, .87),
      'n4_dancers': (0, 0, .52, 1), 'n4_digger': (0, 0, 1, 1), 'n5_arno': (0, 0, 1, 1), 'n5_rembrandt_land': (0, 0, 1, 1),
      'n5_crau': (.33, 0, .78, 1), 'n5_stamaty': (0, 0, 1, 1), 'n5_sargent': (.05, 0, .95, 1)}
for k, (x0, y0, x1, y1) in CP.items():
    im = Image.open(f'img/{k}.jpg'); w, h = im.size
    im.crop((round(x0 * w), round(y0 * h), round(x1 * w), round(y1 * h))).save(f'img/cp-{k}.jpg', quality=88)
# balões: obra -> [obra, [[cx, cy, lado, título, texto], ...]]
B = {
 'n1_pillows': [(.3, .18, .3, 'O contorno', 'Firme e contínuo, mais grosso onde o pano dobra.'), (.43, .23, .16, 'A dobra', 'Um gancho escuro onde a costura puxa.'), (.28, .55, .3, 'O volume', 'Linhas curvas que seguem o pano.')],
 'n1_cats': [(.73, .44, .22, 'As costas', 'Uma curva só dá o gesto inteiro.'), (.33, .57, .25, 'Linhas refeitas', 'O movimento certo desenhado por cima.')],
 'n1_boats': [(.3, .82, .22, 'A areia', 'Só pontos e traços curtos.'), (.88, .62, .22, 'O mar', 'Linhas longas e deitadas.'), (.32, .74, .2, 'As cores', 'O nome da cor escrito no casco.')],
 'n1_paganini': [(.53, .17, .2, 'O rosto', 'A única parte acabada.'), (.42, .5, .3, 'O casaco', 'Poucas linhas claras.')],
 'n1_edith': [(.47, .13, .2, 'O rosto', 'Detalhe e cor só aqui.'), (.25, .55, .3, 'O cotovelo', 'Um ângulo onde caberia uma curva.'), (.6, .6, .22, 'As mãos', 'Dedos longos e angulosos.')],
 'n2_durer13': [(.55, .3, .2, 'O rosto', 'Três quartos, com o olho do fundo menor.'), (.75, .6, .18, 'O dedo', 'Aponta para fora da folha.'), (.75, .07, .35, 'A inscrição', 'Acrescentada por ele anos depois.')],
 'n2_more': [(.58, .42, .25, 'Os olhos', 'Na metade da altura da cabeça.'), (.4, .2, .35, 'O chapéu', 'Só contorno e um pouco de cor.')],
 'n2_hands': [(.6, .82, .3, 'As mãos cruzadas', 'O dedo médio quase do tamanho da palma.'), (.5, .15, .3, 'A mão levantada', 'Hachura de canhoto, do alto à esquerda para baixo.')],
 'n2_worn': [(.35, .25, .25, 'A cabeça', 'Os punhos fechados contra os olhos.'), (.55, .45, .3, 'O bloco', 'O corpo inteiro inclinado numa massa.'), (.55, .88, .25, 'As botas', 'Pesadas, plantadas no chão.')],
 'n2_dancer': [(.75, .12, .22, 'A cabeça', 'Pequena, no alto da curva das costas.'), (.6, .72, .3, 'A grade', 'Linhas para ampliar o desenho na tela.')],
 'n3_drapery': [(.3, .48, .25, 'A luz', 'Branco puro no alto das dobras.'), (.5, .72, .25, 'O fundo da dobra', 'O escuro mais forte da folha.')],
 'n3_hands': [(.25, .15, .22, 'As pontas dos dedos', 'Realce branco do lado da luz.'), (.7, .72, .25, 'A manga', 'Hachura branca que segue as dobras.')],
 'n3_ideal': [(.25, .45, .22, 'O perfil', 'Quase papel, do lado da luz.'), (.7, .6, .25, 'A nuca', 'A sombra em hachura miúda.'), (.6, .2, .3, 'O penteado', 'Detalhe que vai sumindo para trás.')],
 'n3_sleeping': [(.2, .25, .25, 'A cabeça', 'Meia dúzia de toques.'), (.5, .45, .35, 'O corpo', 'Pinceladas largas, sem contorno fechado.')],
 'n3_yeats': [(.45, .12, .3, 'O cabelo', 'Uma massa escura, sem fios.'), (.48, .4, .22, 'O rosto', 'Quase papel, com poucos planos.'), (.3, .8, .3, 'O casaco', 'Carvão largo e rápido.')],
 'n4_mother': [(.2, .3, .2, 'O olho', 'Saltado, desenhado sem piedade.'), (.25, .45, .2, 'A maçã do rosto', 'O osso logo abaixo da pele.'), (.45, .65, .25, 'O pescoço', 'Tendões em linhas duras.')],
 'n4_girl': [(.43, .37, .3, 'Os olhos', 'O olhar volta para quem olha.'), (.78, .55, .3, 'A hachura', 'Paralela, numa só direção.')],
 'n4_holbein_lady': [(.48, .33, .3, 'O rosto', 'Contorno exato e sombra leve.'), (.25, .2, .3, 'A touca', 'Só linha.')],
 'n4_schiele_man': [(.42, .07, .2, 'O rosto', 'Virado por cima do ombro.'), (.3, .73, .18, 'As mãos', 'Grandes, ossudas, tensas.')],
 'n4_sibyl': [(.5, .25, .35, 'As costas', 'A hachura segue cada músculo.'), (.2, .72, .28, 'A cabeça', 'Estudada de novo, em outro ângulo.'), (.43, .7, .18, 'A mão', 'Repetida para acertar os dedos.')],
 'n4_dancers': [(.3, .2, .25, 'O braço na cabeça', 'Contorno repassado várias vezes.'), (.62, .55, .22, 'A mão no joelho', 'O peso do corpo apoiado.')],
 'n4_digger': [(.55, .38, .3, 'As costas', 'Curvadas sobre a pá.'), (.6, .75, .3, 'O pé de apoio', 'O esforço chega até o chão.')],
 'n5_arno': [(.13, .3, .2, 'O castelo', 'Um ponto fixo à esquerda.'), (.55, .4, .3, 'O vale', 'Traços miúdos e deitados ao longe.'), (.18, .06, .3, 'A data', 'Escrita da direita para a esquerda.')],
 'n5_rembrandt_land': [(.48, .5, .25, 'A cabana', 'No centro, quase só contorno.'), (.5, .9, .3, 'A estrada', 'Papel em branco.')],
 'n5_crau': [(.3, .8, .25, 'O primeiro plano', 'Árvores e marcas grandes.'), (.6, .2, .25, 'O horizonte', 'Marcas miúdas, quase pontos.')],
 'n5_stamaty': [(.58, .38, .2, 'Os rostos', 'A única parte modelada.'), (.12, .9, .2, 'O carrinho', 'Um brinquedo esquecido no chão.')],
 'n5_sargent': [(.5, .15, .25, 'A cabeça', 'O único lugar com detalhe.'), (.45, .55, .35, 'O vestido', 'Traços longos com o lápis deitado.'), (.8, .3, .3, 'O fundo', 'Riscos horizontais que recortam a figura.')],
}
json.dump({k: [k, v] for k, v in B.items()}, open('tools/detalhes.json', 'w'), ensure_ascii=False, indent=0)
# linha do tempo: um desenho de cada mestre
T = [('1473', 'Leonardo', 'n5_arno', .5, .45, .7, 'Paisagem do vale do Arno', 'Pena. A primeira paisagem desenhada com data.'),
     ('1484', 'Dürer', 'n2_durer13', .5, .3, .8, 'Autorretrato aos treze anos', 'Ponta de prata. Um menino no espelho.'),
     ('c. 1511', 'Michelangelo', 'n4_sibyl', .5, .25, .8, 'Estudos para a Sibila Líbia', 'Giz vermelho. O volume em hachura.'),
     ('c. 1527', 'Holbein', 'n2_more', .55, .42, .8, 'Sir Thomas More', 'Giz. O rosto medido de uma vez.'),
     ('c. 1654', 'Rembrandt', 'n3_sleeping', .45, .4, .9, 'Jovem dormindo', 'Pincel. Nenhum contorno fechado.'),
     ('1819', 'Ingres', 'n1_paganini', .5, .17, .8, 'Niccolò Paganini', 'Grafite. Rosto acabado, roupa em linha.'),
     ('1873', 'Degas', 'n2_dancer', .55, .25, .9, 'Bailarina ajustando a sapatilha', 'Grafite e giz. Linhas refeitas por cima.'),
     ('1888', 'Van Gogh', 'n5_crau', .5, .5, .6, 'A planície de La Crau', 'Pena de junco. Só marcas.'),
     ('1908', 'Sargent', 'n3_yeats', .5, .25, .8, 'W. B. Yeats', 'Carvão. Massas escuras e papel.'),
     ('1917', 'Schiele', 'n1_edith', .5, .15, .9, 'A mulher do artista', 'Lápis e cor. O contorno anguloso.')]
json.dump(T, open('tools/tracos.json', 'w'), ensure_ascii=False, indent=0)
json.dump({k: 'ab_' + k for k in ['parte1', 'nivel1', 'nivel2', 'nivel3', 'nivel4', 'nivel5']}, open('tools/part_art.json', 'w'))
print('ok')
