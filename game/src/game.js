// Timtim e o Resgate do Macaco Fedido — regras do jogo (física, inimigos, chefão, fluxo). Sem nada de desenho aqui.
(() => {
'use strict';
const TT = window.TT = window.TT || {};

const C = TT.C = {
  W: 960, H: 540, GROUND: 452, GRAV: 2300, JUMP_V: -860, RUN: 310, FAST: 440, SLOW: 175,
  LEVEL_END: 9800, ARENA_X: 8840,
  grounds: [[0, 1250], [1400, 600], [1400, 1000], [2520, 820], [3480, 1100], [4740, 900], [5830, 760], [6820, 700], [7680, 2120]],
  plats: [
    [520, 340, 160], [820, 270, 140], [1180, 330, 150], [1700, 330, 180], [1960, 250, 140],
    [2380, 330, 160], [2850, 320, 140], [3100, 240, 160], [3330, 330, 120], [3800, 320, 200],
    [4150, 250, 160], [4400, 330, 150], [4620, 300, 120], [5150, 320, 180], [5480, 250, 140],
    [5700, 300, 110], [5950, 320, 170], [6230, 230, 150], [6470, 140, 130], [6660, 300, 110], [6950, 320, 160], [7200, 235, 140],
    [7420, 150, 130], [7560, 300, 100], [7900, 320, 180], [8200, 250, 140],
  ],
  checkpoints: [3560, 5880, 8660],
  // amigos chihuahuas que esperam no caminho e entregam biscoito
  friends: [{ x: 1452, kind: 'chi-pb' }, { x: 4792, kind: 'chi-br' }], GIFT: 3,
};
// A fase ensina uma coisa de cada vez: começo só com biscoitos e plataformas, depois um pombo sozinho,
// depois um chocolate sozinho, e só então tudo junto. Para caber o trecho de aprendizado (1400–2000),
// tudo o que ficava de 1400 em diante foi empurrado STRETCH px para a direita — sx() faz essa conta.
const GAP_AT = 1400, STRETCH = 600, sx = x => x >= GAP_AT ? x + STRETCH : x;
C.LEVEL_END = sx(C.LEVEL_END); C.ARENA_X = sx(C.ARENA_X);
C.grounds = C.grounds.map(([x, w], i) => [i === 1 ? x : sx(x), w]);
C.plats = C.plats.map(([x, y, w]) => [sx(x), y, w]).concat([[1560, 330, 140], [1820, 260, 120]]);
C.checkpoints = C.checkpoints.map(sx); C.friends.forEach(f => { f.x = sx(f.x); });
const W0 = C.W;
// ---- fase 2: o Arraial ----
// As fases são escolhidas pelo endereço (index.html?fase=2): cada uma carrega só o que é dela, e a fase 1 fica intacta.
// A fase 2 ensina uma única ação nova: planar com a bandana aberta (segurar o pulo no ar). Ordem:
// palco + primeiro vão (só planando) → vão maior → fogueiras (o ar quente levanta quem plana) → quadrilha
// (tábuas de bandeirinhas que dançam no ritmo) → tudo junto, com o brinquedo perdido no alto de uma fogueira → mastro de São João.
const FASE = TT.FASE = C.FASE = (() => { const q = new URLSearchParams(location.search).get('fase'), h = (location.hash.match(/fase(\d)/) || [])[1]; return +(h || q || 1) === 3 ? 3 : +(h || q || 1) === 2 ? 2 : 1; })();
Object.assign(C, { BOSS: true, FOX: false, GLIDE: false, PREFIGHT: false, SWIRLS: [], blinks: [], fires: [], movers: [], FOXTXT: { egg: 'Ovo cozido! Plana na crina dele!', fruit: 'Ó a fruta-do-lobo, lobão!' }, GOAL_X: C.ARENA_X, MASTRO_X: 0, GIFT_ITEM: 'cookie', NOTES: [], TUB: null, HOOP: null, STAMPEDES: [], GLIDE_TUT: null, EGG: { time: 12, fall: 70, lift: -470 } });
if (FASE === 2) Object.assign(C, {
  BOSS: false, FOX: true, GLIDE: true, PREFIGHT: true, LEVEL_END: 7900, ARENA_X: 7900 - W0, GOAL_X: 7900 - W0 + 120, MASTRO_X: 7580, START_X: 200, BPM: 100,
  grounds: [[0, 1150], [1670, 700], [3000, 1500], [5880, 280], [6300, 1600]],
  plats: [[430, 250, 120], [700, 330, 450], [2150, 300, 200], [3500, 90, 170], [4120, 140, 150]],
  // tábuas da quadrilha: x e y da posição de descanso, ax/ay = quanto vão e voltam, per = período (s), ph = fase do passo
  movers: [{ x: 4580, y: 320, w: 150, ax: 100, ay: 0, per: 2.4, ph: 0 }, { x: 4950, y: 290, w: 140, ax: 0, ay: 70, per: 2.4, ph: Math.PI },
           { x: 5280, y: 320, w: 150, ax: 110, ay: 0, per: 2.4, ph: Math.PI / 2 }, { x: 5600, y: 280, w: 140, ax: 0, ay: 80, per: 2.4, ph: 0 }],
  fires: [{ x: 3410 }, { x: 4040 }, { x: 6610 }, { x: 7040 }, { x: 7810 }], // as duas últimas ficam nos cantos da arena do lobo-guará
  // brincadeiras juninas: cair dentro do tanque da pescaria solta biscoitos; atravessar a argola revela um biscoito dourado
  // aula do planar: o primeiro vão (de 1150 a 1670) só se atravessa planando; cair nele não custa coração até aprender
  GLIDE_TUT: { edge: 1150, land: 1670 },
  TUB: { x: 2120, w: 96 }, HOOP: { x: 5440, y: 130, r: 44 },
  // galinhas em debandada: quando o Timtim passa de 'at', um bando de n galinhas vem correndo da direita
  STAMPEDES: [{ at: 1840, n: 3 }, { at: 3120, n: 4 }, { at: 6360, n: 3 }],
  // correio elegante: bilhetes escondidos, cada um com uma piada dos personagens
  NOTES: [{ x: 640, y: 300, text: 'Para o Timtim: seu faro é o mais charmoso do arraial. Ass.: um admirador secreto (é o Elvis).' },
    { x: 2700, y: 170, text: 'Para o Furtão: devolve os brinquedos ou ninguém dança quadrilha com você. Ass.: a Zara.' },
    { x: 3650, y: 20, text: 'Para a Zara: guardei o último pé de moleque pra você. Ass.: o Elvis (comi metade).' },
    { x: 6040, y: 300, text: 'Para o Lobo-guará: galinha não é brinquedo! Vai comer fruta-do-lobo. Ass.: todos os cães da vila.' }],
  checkpoints: [1720, 3060, 5900, 6340],
  // a Zara e o Elvis ajudam jogando ovo cozido, a comida preferida do Timtim: o primeiro, antes da quadrilha, dá o planar
  // turbinado (cai bem devagar e o ar quente sobe mais); o segundo, antes do trecho final, deixa invencível
  friends: [{ x: 4380, kind: 'chi-pb', power: 'egg' }, { x: 5960, kind: 'chi-br', power: 'mega' }], GIFT_ITEM: 'ovo',
  hedges: [],
  trails: [{ id: 'sanfona', at: 6610, plats: [[6690, 120, 130], [6555, 10, 120]] }],
  TOY: { id: 'sanfoninha', x: 6615, y: -40 },
});
// ---- fase 3: o Quadro Encantado (dentro dos quadros do Van Gogh) ----
// Reaproveita a espinha do Arraial (planar, chefão em três rodadas) e ensina UMA ação nova: o redemoinho.
// Trechos: o Quarto (cama e cadeira, primeiro redemoinho) → os Girassóis (cabeças que sobem e descem, o vaso)
// → o Trigal com Corvos (corvos andando, revoadas) → o Terraço do Café (toldos que quicam, manchas de tinta)
// → a Noite Estrelada (estrelas que piscam, o cipreste) → o morro do Corvo-Borrão (o mesmo motor da luta do lobo-guará).
if (FASE === 3) Object.assign(C, {
  BOSS: false, FOX: true, GLIDE: true, LEVEL_END: 7900, ARENA_X: 7900 - W0, GOAL_X: 7900 - W0 + 120, MASTRO_X: 7900 - W0 + 300, START_X: 200, BPM: 84,
  grounds: [[0, 1300], [1500, 900], [2650, 700], [3550, 1150], [4900, 900], [6050, 350], [6600, 1300]],
  // [x, y, largura, quica]: a cama, a cadeira e a estante do quarto; tábuas pintadas; os toldos do café quicam; as mesas
  plats: [[380, 352, 230], [700, 330, 80], [1000, 150, 160], [2250, 300, 140], [2750, 330, 150], [3000, 320, 160], [3250, 250, 150],
          [3750, 320, 170], [4000, 240, 150], [4300, 320, 160], [5000, 340, 200, 1], [5280, 372, 80], [5500, 340, 200, 1], [5730, 372, 80], [6150, 300, 120]],
  // cabeças de girassol que sobem e descem devagar
  movers: [{ x: 1650, y: 330, w: 120, ax: 0, ay: 50, per: 2.6, ph: 0 }, { x: 1900, y: 270, w: 120, ax: 0, ay: 60, per: 2.6, ph: 2 }, { x: 2150, y: 320, w: 120, ax: 0, ay: 50, per: 2.6, ph: 4 }],
  // redemoinhos: pegam o Timtim no ar e giram com ele; apertar o pulo solta na direção em que ele está indo (d = sentido do giro)
  SWIRLS: [{ x: 880, y: 230, r: 70, d: 1 }, { x: 2520, y: 250, r: 70, d: 1 }, { x: 3450, y: 230, r: 70, d: 1 }, { x: 4800, y: 240, r: 70, d: 1 },
           { x: 5930, y: 230, r: 70, d: 1 }, { x: 6230, y: 100, r: 64, d: -1 }, { x: 7900 - W0 + 150, y: 250, r: 70, d: 1 }, { x: 7900 - 150, y: 250, r: 70, d: -1 }],
  // estrelas que piscam: só seguram enquanto estão acesas
  blinks: [{ x: 6420, y: 260, w: 100, per: 2.4, ph: 0 }, { x: 6520, y: 180, w: 100, per: 2.4, ph: 1.2 }],
  fires: [], GLIDE_TUT: null, TUB: null, HOOP: { x: 4150, y: 120, r: 46 },
  STAMPEDES: [{ at: 3600, n: 3 }, { at: 4320, n: 4 }], // revoadas de corvos rasantes
  NOTES: [{ x: 1060, y: 100, text: 'Para o Theo, o gato do museu: entramos no quadro! Se o Furtão perguntar, a gente não está aqui. Ass.: a Zara.' },
    { x: 2210, y: 240, text: 'Theo, este trigo faz cócegas na barriga. Já mordi três girassóis achando que eram biscoito. Ass.: o Elvis.' },
    { x: 4060, y: 180, text: 'Theo, o céu daqui gira mais que o Timtim correndo atrás do rabo. Ass.: a Zara (tonta).' },
    { x: 5560, y: 150, text: 'Para o Corvo-Borrão: devolve o girassol da Tinta e a gente te dá uma tampinha. Ass.: todos os cães da vila.' }],
  checkpoints: [1560, 3600, 4950, 6080],
  friends: [{ x: 2800, kind: 'chi-pb', power: 'egg' }, { x: 5150, kind: 'chi-br', power: 'mega' }], GIFT_ITEM: 'tubo',
  hedges: [],
  trails: [{ id: 'girassol', at: 6200, plats: [[6260, 20, 110], [6120, -80, 110]] }],
  TOY: { id: 'girassol', x: 6175, y: -130 },
  FOXTXT: { egg: 'Tinta amarela! Plana nas costas dele!', fruit: 'Ó a tampinha dourada, corvão!' },
});
C.SWIRL = { w: Math.PI * 2 / 1.3, speed: 820 }; // uma volta a cada 1,3 s; a soltura sai a 820 px/s
C.FIRE = { w: 64, h: 62, col: 64, top: -70, lift: -380 }; // a chama não machuca; a coluna de ar quente sobe até y = top
const { W, H, GROUND, GRAV, JUMP_V, RUN, FAST, LEVEL_END, ARENA_X } = C; // (já com o trecho novo e a fase escolhida)
// ---- segredos (em coordenadas finais) ----
// O faro: segurando ↓ o Timtim para e fareja, e um rastro verde de cheiro aponta o segredo mais próximo.
// - moita falsa: parece um arbusto qualquer, mas dá para entrar nela; esconde biscoitos (a primeira fica logo atrás do
//   ponto de partida, para quem farejar ou andar para a esquerda no começo).
// - caminho de cheiro: plataformas invisíveis que o faro revela. Elas levam ao brinquedo perdido da fase.
if (FASE === 1) {
  C.START_X = 250;
  C.hedges = [{ x: 0, w: 200 }];
  C.trails = [{ id: 'duck', at: 4230, plats: [[4170, 312, 110], [4300, 182, 100], [4150, 62, 130]] }];
  C.TOY = { id: 'patinho', x: 4215, y: 12 }; // o brinquedo perdido do Parque, no alto do caminho de cheiro
}
C.SNIFF = { reveal: 0.35, range: 700 }; // farejando por 0,35 s revela o caminho de cheiro a até 700 px

// ---- eventos (o jogo avisa; som, tela e interface reagem) ----
const handlers = {};
TT.on = (n, f) => { (handlers[n] = handlers[n] || []).push(f); };
const emit = TT.emit = (n, d) => { (handlers[n] || []).forEach(f => f(d || {})); };

TT.input = { left: false, right: false, jump: false, jumpPressed: false, sniff: false };

function makeItems() {
  if (FASE === 2) return arraialItems();
  if (FASE === 3) return quadroItems();
  const it = [];
  const cookie = (x, y) => it.push({ type: 'cookie', x, y, got: false });
  [300, 360, 420].forEach(x => cookie(x, GROUND - 40));
  [560, 600, 640].forEach(x => cookie(x, 300));
  cookie(890, 230); cookie(1225, 290);
  cookie(1352, 288); cookie(1388, 300); // arco do salto sobre o buraco, logo depois da plataforma
  [1740, 1790, 1840].forEach(x => cookie(x, 290));
  cookie(2030, 210); cookie(2430, 290);
  for (let x = 2620; x <= 2820; x += 50) cookie(x, GROUND - 40);
  [3140, 3190, 3240].forEach(x => cookie(x, 200));
  [3870, 3920, 3970].forEach(x => cookie(x, 280));
  cookie(4220, 210); cookie(4680, 260);
  for (let x = 4850; x <= 5050; x += 50) cookie(x, GROUND - 40);
  [5520, 5570].forEach(x => cookie(x, 210));
  cookie(5755, 260); [5990, 6040, 6090].forEach(x => cookie(x, 280)); cookie(6300, 190); cookie(6535, 100); cookie(6715, 260);
  [6860, 6905].forEach(x => cookie(x, GROUND - 40)); [6995, 7035, 7075].forEach(x => cookie(x, 280)); // em cima da plataforma, não embaixo das raízes
  cookie(7270, 195); cookie(7485, 110); [7950, 8000, 8050].forEach(x => cookie(x, 280)); cookie(8270, 210);
  for (let x = 8350; x <= 8550; x += 50) cookie(x, GROUND - 40);
  // biscoitos dourados: só o pulo duplo alcança
  [[1325, 165], [3410, 70], [7610, 40]].forEach(([x, y]) => it.push({ type: 'gold', x, y, got: false }));
  // chocolates no chão: cachorro não pode! Dá dor de barriga e ele anda devagar por um tempo. Dá para pular por cima.
  // O primeiro aparece sozinho, depois do pombo de treino e do primeiro amigo.
  [2240, 3900, 5370, 6330, 7830].forEach(x => it.push({ type: 'choco', x, y: GROUND - 34, got: false }));
  // sem poderes soltos pela fase: turbo e invencibilidade vêm só dos presentes dos chihuahuas
  it.forEach(o => { o.x = sx(o.x); });
  // trecho de aprendizado (já em coordenadas finais): poucos biscoitos e o pombo de treino
  [1600, 1640, 1680].forEach(x => cookie(x, 290)); cookie(1860, 220);
  // segredos: biscoitos atrás da moita falsa do começo, dois no meio do caminho de cheiro e o brinquedo perdido no topo
  [45, 95, 145].forEach(x => cookie(x, GROUND - 40));
  [[4335, 130], [4375, 130]].forEach(([x, y]) => it.push({ type: 'cookie', x, y, got: false, trail: 'duck' }));
  it.push({ type: 'toy', id: C.TOY.id, x: C.TOY.x, y: C.TOY.y, got: false, trail: 'duck' });
  // nada encosta no tampo de musgo: o que está sobre uma plataforma fica no mínimo 50px acima dela
  // (o tampo é desenhado em perspectiva e o item flutua, então a 40px ele parecia entrar no bloco)
  for (const o of it) for (const [px, py, pw] of C.plats.concat(...C.trails.map(t => t.plats))) if (o.x > px - 20 && o.x < px + pw + 20 && o.y < py && o.y > py - 50) o.y = py - 50;
  return it;
}
// itens do Arraial: os biscoitos desenham o caminho (o arco do primeiro vão ensina a descer planando; a fila na coluna
// de ar quente ensina a subir); os dourados ficam no alto do palco, no topo da primeira fogueira e entre duas tábuas da quadrilha
function quadroItems() {
  const it = [], G = GROUND - 40, cookie = (x, y, trail) => it.push({ type: 'cookie', x, y, got: false, trail });
  [300, 360].forEach(x => cookie(x, G)); [430, 490, 550].forEach(x => cookie(x, 300)); cookie(740, 280); [1030, 1090].forEach(x => cookie(x, 100));
  [[780, 200], [880, 140], [980, 200]].forEach(([x, y]) => cookie(x, y)); // em volta do primeiro redemoinho
  [1600, 1660].forEach(x => cookie(x, G)); [1710, 1960, 2210].forEach(x => cookie(x, 180)); [2300, 2350].forEach(x => cookie(x, 250));
  [[2460, 180], [2520, 160], [2580, 180]].forEach(([x, y]) => cookie(x, y)); [2700, 2760].forEach(x => cookie(x, G)); [2800, 2860].forEach(x => cookie(x, 280));
  [3050, 3110].forEach(x => cookie(x, 270)); [3300, 3360].forEach(x => cookie(x, 200)); [[3400, 160], [3450, 140], [3500, 160]].forEach(([x, y]) => cookie(x, y));
  for (let x = 3600; x <= 3720; x += 60) cookie(x, G); [3800, 3860, 4050, 4110, 4350, 4410].forEach((x, i) => cookie(x, i < 2 ? 270 : i < 4 ? 190 : 270));
  [4550, 4610].forEach(x => cookie(x, G)); [[4750, 170], [4800, 150], [4850, 170]].forEach(([x, y]) => cookie(x, y));
  [5060, 5120].forEach(x => cookie(x, 170)); [5560, 5620].forEach(x => cookie(x, 170)); [5300, 5750].forEach(x => cookie(x, 320));
  [[5880, 170], [5930, 150], [5980, 170]].forEach(([x, y]) => cookie(x, y)); [6120, 6180].forEach(x => cookie(x, 250));
  [6440, 6540].forEach((x, i) => cookie(x, i ? 130 : 210)); [6700, 6760, 6820].forEach(x => cookie(x, G));
  cookie(6290, -30, 'girassol');
  [[1060, 60], [3300, 170], [5520, 60]].forEach(([x, y]) => it.push({ type: 'gold', x, y, got: false })); // os três tubos de tinta dourados
  it.push({ type: 'gold', x: 4150, y: 60, got: false, trail: 'argola' }); // a moldura dourada revela mais um
  C.NOTES.forEach((n, i) => it.push({ type: 'bilhete', x: n.x, y: n.y, got: false, idx: i })); // cartas ao Theo
  [3900, 5150, 5650].forEach(x => it.push({ type: 'choco', x, y: GROUND - 34, got: false })); // manchas de tinta preta: deixam o Timtim lento
  it.push({ type: 'toy', id: C.TOY.id, x: C.TOY.x, y: C.TOY.y, got: false, trail: 'girassol' });
  for (const o of it) for (const [px, py, pw] of C.plats.concat(...C.trails.map(t => t.plats))) if (o.x > px - 20 && o.x < px + pw + 20 && o.y < py && o.y > py - 50) o.y = py - 50;
  return it;
}
function arraialItems() {
  const it = [], G = GROUND - 40, cookie = (x, y, trail) => it.push({ type: 'cookie', x, y, got: false, trail });
  [300, 360, 420].forEach(x => cookie(x, G)); cookie(490, 200); [780, 840, 1040, 1100].forEach(x => cookie(x, 280));
  [[1230, 290], [1330, 320], [1430, 350], [1530, 380], [1630, 405]].forEach(([x, y]) => cookie(x, y));
  for (let x = 1800; x <= 2100; x += 60) cookie(x, G); [2200, 2290].forEach(x => cookie(x, 250));
  [[2480, 250], [2600, 270], [2720, 290], [2840, 320], [2960, 350]].forEach(([x, y]) => cookie(x, y));
  [3120, 3180, 3240].forEach(x => cookie(x, G)); [330, 250, 170, 90].forEach(y => cookie(3410, y)); [3560, 3620].forEach(x => cookie(x, 40));
  [4170, 4230].forEach(x => cookie(x, 90)); [4290, 4340].forEach(x => cookie(x, G));
  [[4655, 250], [5020, 200], [5355, 250], [5670, 180]].forEach(([x, y]) => cookie(x, y));
  [5950, 6020, 6090].forEach(x => cookie(x, G)); [6400, 6460, 6860, 6910].forEach(x => cookie(x, G));
  cookie(6750, 70, 'sanfona');
  [[900, 110], [3410, -10]].forEach(([x, y]) => it.push({ type: 'gold', x, y, got: false }));
  it.push({ type: 'gold', x: 5505, y: 140, got: false, trail: 'argola' }); // só aparece depois de atravessar a argola
  [[2075, 340], [2100, 300], [2125, 280], [2150, 300], [2175, 340]].forEach(([x, y]) => cookie(x, y, 'pescaria')); // saem do tanque da pescaria
  C.NOTES.forEach((n, i) => it.push({ type: 'bilhete', x: n.x, y: n.y, got: false, idx: i }));
  [1950, 3880, 6820].forEach(x => it.push({ type: 'choco', x, y: GROUND - 34, got: false }));
  it.push({ type: 'toy', id: C.TOY.id, x: C.TOY.x, y: C.TOY.y, got: false, trail: 'sanfona' });
  for (const o of it) for (const [px, py, pw] of C.plats.concat(...C.trails.map(t => t.plats))) if (o.x > px - 20 && o.x < px + pw + 20 && o.y < py && o.y > py - 50) o.y = py - 50;
  return it;
}
function makeEnemies() {
  if (FASE === 3) return [[3100, 3000, 3340], [3800, 3600, 4100], [4400, 4300, 4650], [1750, 1520, 2380]]
    .map(([x, a, b]) => ({ x, y: GROUND - 30, w: 38, h: 30, a, b, dir: -1, alive: true, t: Math.random() * 6, dy: 0 }));
  if (FASE === 2) return [[2050, 1760, 2340], [3720, 3540, 3900], [6460, 6330, 6560], [6790, 6700, 6900]]
    .map(([x, a, b]) => ({ x, y: GROUND - 30, w: 38, h: 30, a, b, dir: -1, alive: true, t: Math.random() * 6, dy: 0 }));
  // sem pombo no começo; o primeiro anda sozinho no trecho de aprendizado
  return [[1750, 1480, 1960], ...[[1700, 1570, 1980], [2700, 2560, 3300], [3700, 3520, 4500], [4300, 4150, 4300], [5100, 4930, 5600], [6100, 5860, 6560], [7100, 6840, 7500], [8100, 7700, 8700]].map(e => e.map(sx))]
    .map(([x, a, b]) => ({ x, y: GROUND - 30, w: 38, h: 30, a, b, dir: -1, alive: true, t: Math.random() * 6, dy: 0 }));
}
// ---- Furtão, o chefão (no código ainda "boss"/"brute") ----
// Três corações = três fases, e cada fase traz um ataque novo: investida, latidão (onda no chão) e pisão do terremoto.
// O ponto fraco é a bolinha: de tempos em tempos a Zara ou o Elvis jogam uma, o Brutão não resiste, vai buscar e fica
// mordendo. Só nessa hora um pisão na cabeça acerta. Fora disso ele sacode o Timtim para o alto, sem dano para ninguém.
const BOSS = { ballEvery: [5, 6, 7], chew: [3.0, 2.5, 2.1], charge: [520, 590, 660], wind: { charge: 0.75, bark: 0.6, pound: 0.5 } };
// ---- o Lobo-guará, chefão do Arraial (no código ainda "fox") ----
// Ele invadiu o galinheiro. É alto: o pulo comum só bate na canela dele, que dá um passo para trás, e o Timtim quica.
// O ponto fraco é o lombo, onde fica a crina: para alcançar, o Timtim sobe no ar quente das fogueiras dos cantos e desce
// PLANANDO em cima dele. Há também janelas em que ele fica de lombo baixo e qualquer pisão acerta (brilho dourado):
// fuçando o chão depois do bote, tonto depois de bater na cerca e comendo a fruta-do-lobo.
// Ataques, sempre com aviso vermelho:
//  - bote: agacha e dá o salto alto de lobo-guará; a marca no chão mostra onde ele vai cair; depois fica fuçando o chão;
//  - corrida: cava o chão e atravessa a arena com as pernas compridas; se bater na cerca, fica tonto;
//  - latido rouco (a partir do 2º coração): apaga o ar quente das fogueiras por 2 s e derruba quem estiver planando.
// Rodadas: 1º coração devagar, com janelas longas; 2º entra o latido; 3º mais rápido, emendando o bote com a corrida.
// A Zara e o Elvis se revezam: ovo cozido para o Timtim (planar turbinado) e fruta-do-lobo no chão da arena (ele para
// para comer). No terceiro golpe, as galinhas criam coragem, saem do galinheiro e expulsam o lobo-guará para a mata.
const FOXC = { prowl: [100, 130, 160], wind: [0.75, 0.6, 0.48], dash: [560, 640, 720], sniff: [1.5, 1.25, 1.0], bonk: [1.3, 1.1, 0.9], eat: [2.3, 2.0, 1.7],
  roarWind: 0.7, roarOff: 2.0, throwEvery: 7 };
function makeFox() { return { x: ARENA_X + 640, y: GROUND - 110, w: 120, h: 110, vx: 0, vy: 0, dir: -1, hp: 3, state: 'idle', t: 0, cd: 1.6, atk: '', tx: 0, egg: 5, hurt: 0, roarCd: 0, throws: 0 }; }
function updateFox(dt, prevBottom, playing) {
  const p = S.player, f = S.fox, ph = Math.max(0, Math.min(2, 3 - f.hp)), cine = S.cine && S.cine.type === 'fox';
  f.t += dt; f.hurt = Math.max(0, f.hurt - dt); f.roarCd = Math.max(0, f.roarCd - dt);
  S.fireOff = Math.max(0, (S.fireOff || 0) - dt); p.noGlide = Math.max(0, (p.noGlide || 0) - dt);
  const fx = f.x + f.w / 2, pcx = p.x + p.w / 2, onGround = f.y + f.h >= GROUND - 0.5;
  const go = st => { f.state = st; f.t = 0; };
  // fruta-do-lobo jogada pelos amigos: voa em arco e fica no chão até ele comer
  const fr = S.fruit;
  if (fr && !fr.rest) { fr.vy += GRAV * dt; fr.x += fr.vx * dt; fr.y += fr.vy * dt; if (fr.y >= GROUND - 22) { fr.y = GROUND - 22; fr.rest = true; emit('fruitLand', { x: fr.x, y: GROUND, first: !S.fruitSeen }); S.fruitSeen = true; } }
  if (f.state === 'flee') { f.dir = 1; f.vx = 600; f.x += f.vx * dt; return; } // foge para a mata, sem parede que o segure
  if (cine) f.vx *= 0.9;
  else if (playing) switch (f.state) {
    case 'idle': { if (fr && fr.rest && onGround) { go('toFruit'); break; }
      const d = Math.sign(pcx - fx) || f.dir; f.dir = d; f.vx += (d * FOXC.prowl[ph] - f.vx) * Math.min(1, dt * 3);
      f.cd -= dt; if (f.cd <= 0 && onGround) {
        f.atk = ph >= 1 && !f.roarCd && Math.random() < 0.35 ? 'roar' : Math.random() < 0.55 ? 'pounce' : 'dash'; go('wind'); }
      break; }
    case 'toFruit': { if (!fr) { go('idle'); f.cd = 0.6; break; } const d = Math.sign(fr.x - fx) || f.dir; f.dir = d; f.vx = d * 330;
      if (Math.abs(fr.x - fx) < 26) { S.fruit = null; f.vx = 0; go('eat'); emit('foxEat', { x: fx, y: GROUND - 40 }); } break; }
    case 'wind': { f.vx *= 0.8; f.dir = Math.sign(pcx - fx) || f.dir; // aviso: agacha (bote), cava o chão (corrida) ou enche o peito (latido)
      const w = f.atk === 'roar' ? FOXC.roarWind : f.combo ? 0.3 : FOXC.wind[ph];
      if (f.t >= w) { f.combo = false;
        if (f.atk === 'pounce') { go('air'); f.tx = Math.max(ARENA_X + 80, Math.min(ARENA_X + W - 80, pcx)); f.vy = -900; f.vx = (f.tx - fx) / (2 * 900 / GRAV); emit('foxPounce', { x: fx, y: GROUND }); }
        else if (f.atk === 'roar') { go('roar'); f.roarCd = 6; S.fireOff = FOXC.roarOff; emit('foxRoar', { x: fx - f.dir * 40, y: f.y + 20, first: !S.roarSeen }); S.roarSeen = true;
          if (p.gliding && Math.abs(pcx - fx) < 460) { p.vy = Math.max(p.vy, 520); p.noGlide = 0.7; p.gliding = false; } } // o latido derruba quem está planando perto
        else { go('dash'); f.vx = f.dir * FOXC.dash[ph]; emit('foxDash', { x: fx, y: GROUND }); } }
      break; }
    case 'air': if (onGround && f.t > 0.2) { f.vx = 0; S.trauma = Math.min(1, S.trauma + 0.35); emit('land', { x: fx, y: GROUND });
      if (ph === 2 && Math.random() < 0.45) { f.atk = 'dash'; f.combo = true; go('wind'); } else { go('tired'); emit('foxSniff', { x: fx, y: GROUND }); } } break; // no 3º coração, às vezes emenda o bote com a corrida
    case 'dash': if ((f.dir < 0 && f.x <= ARENA_X + 14) || (f.dir > 0 && f.x + f.w >= ARENA_X + W - 14)) { f.vx = 0; go('bonk'); S.trauma = Math.min(1, S.trauma + 0.4); emit('bonk', { x: f.dir < 0 ? f.x : f.x + f.w, y: GROUND - 50 }); } break;
    case 'tired': f.vx *= 0.8; if (f.t > FOXC.sniff[ph]) { go('idle'); f.cd = 1.1 - ph * 0.2; } break; // fuçando o chão, de lombo baixo
    case 'bonk': f.vx *= 0.8; if (f.t > FOXC.bonk[ph]) { go('idle'); f.cd = 1.0; } break;
    case 'eat': f.vx *= 0.8; if (f.t > FOXC.eat[ph]) { go('idle'); f.cd = 0.8; } break;
    case 'roar': f.vx *= 0.8; if (f.t > 1.0) { go('idle'); f.cd = 0.9; } break;
    case 'dodge': if (onGround && f.t > 0.25) { f.vx = 0; go('idle'); f.cd = 0.6; } break;
    case 'hurt': f.vx *= 0.85; if (f.t > 1.1) { go('idle'); f.cd = 0.9; } break;
  }
  f.vy += GRAV * dt; f.x += f.vx * dt; f.y += f.vy * dt;
  if (f.y + f.h > GROUND) { f.y = GROUND - f.h; f.vy = 0; }
  f.x = Math.max(ARENA_X + 10, Math.min(ARENA_X + W - 10 - f.w, f.x));
  // a Zara e o Elvis se revezam, um de cada canto: ovo cozido para o Timtim, fruta-do-lobo para distrair o lobo-guará
  if (playing && !cine) { f.egg -= dt; if (f.egg <= 0 && !S.gifts.length && !S.fruit) { f.egg = FOXC.throwEvery; f.throws++; const q = S.friends[f.throws % 2];
    if (f.throws % 2) { S.gifts.push({ sx: q.x + q.face * 18, sy: GROUND - 58, x: q.x, y: GROUND - 58, t: 0, kind: 0, fight: true }); emit('friend', { x: q.x, y: GROUND - 70, kind: q.kind, line: C.FOXTXT.egg }); }
    else { const tx = Math.max(ARENA_X + 160, Math.min(ARENA_X + W - 160, ARENA_X + W / 2 + (Math.random() - 0.5) * 360)), T = 2 * 650 / GRAV;
      S.fruit = { x: q.x, y: GROUND - 58, vx: (tx - q.x) / T, vy: -650, rest: false }; emit('friend', { x: q.x, y: GROUND - 70, kind: q.kind, line: C.FOXTXT.fruit }); }
    q.hop = 0.9; } }
  if (!playing || cine) return;
  const hb = { x: f.x + 14, y: f.y + 12, w: f.w - 28, h: f.h - 12 };
  if (!overlap(p, hb)) return;
  const fromAbove = p.vy > 0 && (prevBottom <= f.y + 30 || p.y + p.h < f.y + f.h * 0.55), low = ['tired', 'bonk', 'eat'].includes(f.state);
  if (fromAbove) {
    if (f.state === 'hurt') { p.vy = -520; p.shrugT = 0.45; return; }
    if (p.gliding || low) { // acertou a crina!
      f.hp--; f.hurt = 0.4; go('hurt'); p.vy = -720; p.shrugT = 0.5; S.hitstop = 0.12; S.trauma = Math.min(1, S.trauma + 0.55);
      emit('stomp', { x: fx, y: f.y, boss: true }); emit('foxHit', { x: fx, y: f.y, hp: f.hp });
      if (f.hp <= 0) { go('flee'); S.mode = 'winning'; S.winT = 0; S.slowT = 0.6; S.fruit = null;
        S.friends.forEach((q, i) => { q.home = Math.max(ARENA_X + 60, p.x - 120 - i * 85) + (p.x < ARENA_X + 300 ? 330 : 0); q.vx = 0; });
        // as galinhas criam coragem: saem do galinheiro e correm atrás dele até a mata
        if (FASE === 2) for (let i = 0; i < 5; i++) S.runners.push({ kind: 'chaser', x: ARENA_X + 260 - i * 55, y: GROUND - 30, w: 38, h: 30, vx: 470 + i * 12, t: i * 0.7 });
        emit('finalBlow', { x: fx, y: f.y }); emit('foxDefeated', { x: fx, y: f.y }); if (FASE === 2) emit('henRevenge', { x: ARENA_X + 300, y: GROUND - 40 }); }
    } else { // pulo comum: só bate na canela; ele dá um passo para trás e o Timtim quica
      go('dodge'); f.vy = -380; f.vx = (fx < pcx ? -1 : 1) * 280; p.vy = -600; p.shrugT = 0.45; emit('foxDodge', { x: fx, y: f.y }); }
  } else if ((f.state === 'dash' || (f.state === 'air' && f.vy > 0)) && p.mega <= 0 && !(p.shrugT > 0)) hurt(fx); // só machucam os ataques avisados: a corrida e a queda do bote
  else if (f.state !== 'hurt' && f.state !== 'dodge' && !(low && p.vy < 0)) { // encostou fora de um ataque: o lobo-guará empurra, sem tirar coração
    const d = Math.sign(pcx - fx) || 1; p.vx = d * 380; p.vy = Math.min(p.vy, -300); p.shrugT = 0.3; emit('foxBump', { x: (pcx + fx) / 2, y: p.y + p.h / 2 }); }
}
// ---- galinhas em debandada (Arraial) ----
// De vez em quando um bando vem correndo da direita para a esquerda, fugindo do lobo-guará: o Timtim tem de pular por
// cima (ou planar). Antes de elas aparecerem, poeira e cacarejo na beirada direita da tela avisam. Encostar de lado machuca;
// caindo em cima de uma, ele quica (ela não some, só está fugindo). No fim, na arena, o lobo-guará aparece caçando três delas.
const groundAt = x => C.grounds.some(([g0, gw]) => x >= g0 && x <= g0 + gw);
function updateRunners(dt, prevBottom, playing) {
  const p = S.player, cam = S.cam;
  for (const st of C.STAMPEDES) {
    if (!playing || S.runDone[st.at] || p.x < st.at || p.x > st.at + 500) continue;
    S.runDone[st.at] = true; S.warn = { t: 0, n: st.n };
    emit('stampedeWarn', { x: cam.x + W, y: GROUND, first: !S.warnedOnce }); S.warnedOnce = true;
  }
  if (S.warn) { S.warn.t += dt; if (S.warn.t >= 0.9) { for (let i = 0; i < S.warn.n; i++) {
      let x = cam.x + W + 40 + i * 85; if (!groundAt(x + 19)) { const g = C.grounds.find(([g0]) => g0 > x); if (!g) continue; x = g[0] + 40 + i * 85; }
      S.runners.push({ kind: 'run', x, y: GROUND - 30, w: 38, h: 30, vx: -(390 + Math.random() * 70), t: Math.random() * 3 }); }
    S.warn = null; emit('stampede', { x: cam.x + W, y: GROUND }); } }
  for (let i = S.runners.length - 1; i >= 0; i--) {
    const r = S.runners[i]; r.t += dt;
    if (r.kind === 'arena') { // perseguida pelo lobo-guará dentro da arena, de um lado para o outro
      r.x += r.vx * dt; if (r.x < ARENA_X + 30) { r.x = ARENA_X + 30; r.vx = Math.abs(r.vx); } if (r.x > ARENA_X + 430) { r.x = ARENA_X + 430; r.vx = -Math.abs(r.vx); } } // fica na parte da arena que já aparece para quem chega
    else r.x += r.vx * dt;
    // na beirada de um buraco ela dá um pulo batendo as asas e cai do outro lado (antes atravessava flutuando)
    if (r.air) { r.jv += 1500 * dt; r.jy += r.jv * dt; r.x += r.vx * (r.boost - 1) * dt;
      if (r.jy >= 0 && groundAt(r.x + r.w / 2)) { r.jy = 0; r.jv = 0; r.air = false; emit('henLand', { x: r.x + r.w / 2, y: GROUND }); } }
    else { const dir = Math.sign(r.vx) || -1, cx = r.x + r.w / 2;
      if (groundAt(cx) && !groundAt(cx + dir * 22)) {
        const segs = C.grounds.filter(([g0, gw]) => dir < 0 ? g0 + gw < cx : g0 > cx);
        const land = segs.length ? (dir < 0 ? segs.reduce((a, s) => s[0] + s[1] > a[0] + a[1] ? s : a) : segs.reduce((a, s) => s[0] < a[0] ? s : a)) : null;
        if (land) { const edge = dir < 0 ? land[0] + land[1] - 30 : land[0] + 30, d = Math.abs(edge - cx), T = Math.min(0.85, d / Math.abs(r.vx));
          r.boost = d / T / Math.abs(r.vx); r.jv = -1500 * T / 2; r.jy = 0; r.air = true; emit('henJump', { x: cx, y: GROUND - 20 }); } } }
    r.y = GROUND - 30 + (r.air ? r.jy : -Math.abs(Math.sin(r.t * 14)) * 16);
    if ((r.x < cam.x - 200 && r.kind !== 'arena') || r.x > C.LEVEL_END + 400 || r.jy > 500) { S.runners.splice(i, 1); continue; }
    if (r.kind !== 'run' || !playing || S.cine || !overlap(p, r)) continue;
    if (p.vy > 0 && prevBottom <= r.y + 16) { p.vy = -640; p.shrugT = 0.3; emit('cluck', { x: r.x + r.w / 2, y: r.y }); emit('henBounce', { x: r.x + r.w / 2, y: r.y }); }
    else if (!(p.shrugT > 0)) hurt(r.x + r.w / 2);
  }
}
// antes da luta: o lobo-guará caça três galinhas na arena; quando o Timtim chega, elas fogem para a esquerda passando por ele
function preFight(dt) {
  const p = S.player, f = S.fox;
  if (S.bossSeen || p.x < ARENA_X - 900) return;
  if (!S.chaseOn) { S.chaseOn = true; for (let i = 0; i < 3; i++) S.runners.push({ kind: 'arena', x: ARENA_X + 220 + i * 60, y: GROUND - 30, w: 38, h: 30, vx: -270 - i * 25, t: i }); f.state = 'chase'; f.x = ARENA_X + 480; }
  const hens = S.runners.filter(r => r.kind === 'arena'); if (!hens.length) return;
  const tx = hens.reduce((a, r) => a + r.x, 0) / hens.length - Math.sign(hens[0].vx) * 140;
  const d = Math.sign(tx - (f.x + f.w / 2)) || f.dir; f.dir = d; f.vx += (d * 330 - f.vx) * Math.min(1, dt * 4);
  if (Math.abs(tx - (f.x + f.w / 2)) < 40) f.vx *= 0.8;
  f.x = Math.max(ARENA_X + 10, Math.min(ARENA_X + 560, f.x + f.vx * dt));
}
function scatterHens() { S.runners.forEach(r => { if (r.kind === 'arena') { r.kind = 'flee'; r.vx = -(470 + Math.random() * 80); } }); if (S.chaseOn) emit('cluck', { x: ARENA_X + 300, y: GROUND - 40 }); }
function makeBoss() {
  return { name: 'Furtão', x: ARENA_X + 700, y: GROUND - 100, w: 150, h: 100, vx: 0, vy: 0, dir: -1, hp: 3,
    state: 'idle', atk: '', last: '', t: 0, cd: 1.8, hurt: 0, spin: 0, landT: 0, turnT: 0, tx: 0, ballT: 4, thrower: 0 };
}
function makePlayer(x) {
  return { x, y: GROUND - 50, w: 54, h: 50, vx: 0, vy: 0, onGround: true, face: 1, hp: 3, inv: 0, fast: 0, mega: 0, slow: 0,
    safeX: x, coyote: 0, buffer: 0, landT: 0, won: false, hurtT: 0, dj: true, djT: 0, sniff: 0, egg: 0 };
}

const SOLIDS = [];
for (const [x, w] of C.grounds) SOLIDS.push({ x, y: GROUND, w, h: 200, oneWay: false });
for (const [x, y, w, b] of C.plats) SOLIDS.push({ x, y, w, h: 18, oneWay: true, bounce: !!b });
for (const b of C.blinks) SOLIDS.push({ x: b.x, y: b.y, w: b.w, h: 18, oneWay: true, blink: b });
TT.blinkOn = b => (((TT.S.clock || 0) + b.ph) % b.per) < b.per * 0.62; // acesa 62% do tempo
for (const t of C.trails) for (const [x, y, w] of t.plats) SOLIDS.push({ x, y, w, h: 18, oneWay: true, trail: t.id }); // só existem depois de farejadas
// tábuas da quadrilha: sólidos que se movem; a posição é recalculada a cada quadro e quem está em cima vai junto
const MOVERS = C.movers.map(m => { const s = { x: m.x, y: m.y, w: m.w, h: 18, oneWay: true, mover: m, dx: 0, dy: 0 }; SOLIDS.push(s); return s; });
TT.MOVERS = MOVERS;
TT.beatClock = () => { const b = TT.beatTime && TT.beatTime(); return b != null ? b : S.clock; }; // tempo da música quando há trilha do Arraial; senão o relógio da fase
function moveMovers(clock) {
  for (const s of MOVERS) { const m = s.mover, a = Math.PI * 2 * clock / m.per + m.ph, nx = m.x + m.ax * Math.sin(a), ny = m.y + m.ay * Math.sin(a);
    s.dx = nx - s.x; s.dy = ny - s.y; s.x = nx; s.y = ny; }
}
moveMovers(0);
// fogueiras: a chama machuca quem encosta; a coluna de ar quente em cima levanta quem está planando
const inColumn = (p, f) => Math.abs(p.x + p.w / 2 - f.x) < C.FIRE.col && p.y > C.FIRE.top;
const solid = s => (!s.trail || S.revealed[s.trail]) && (!s.blink || TT.blinkOn(s.blink));
TT.SOLIDS = SOLIDS;
const overlap = (a, b) => a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;

const S = TT.S = { mode: 'title' };
function reset() {
  Object.assign(S, {
    player: makePlayer(C.START_X), items: makeItems(), enemies: makeEnemies(), boss: makeBoss(), ball: null, waves: [],
    cam: { x: 0, y: 0, look: 0 }, time: 0, clock: 0, cookies: 0, arena: false, trauma: 0, hitstop: 0,
    gold: 0, timeScale: 1, slowT: 0, cine: null, checkpoint: -1, bossSeen: false, hpLost: 0, winT: 0, dustT: 0,
    thief: null, prize: null, revealed: {}, toy: false, scent: null, fox: makeFox(), fruit: null, fireOff: 0, notes: 0, runners: [], runDone: {}, warn: null, chaseOn: false, warnedOnce: false, roarSeen: false, fruitSeen: false,
    friends: C.friends.map(f => ({ x: f.x, home: f.x, vx: 0, follow: 0, kind: f.kind, power: f.power, given: false, hop: 0, face: -1, t: 0 })), gifts: [], tut: {},
  });
  S.totalCookies = S.items.filter(i => i.type === 'cookie').length + C.friends.length * C.GIFT;
}
// para onde o faro aponta: o segredo ainda não achado mais perto (biscoito dourado, moita falsa, caminho de cheiro);
// se não houver nenhum por perto, o rastro segue o cheiro do Macaco Fedido, para a direita.
function scentTarget(p) {
  const px = p.x + p.w / 2; let best = null, bd = 1500;
  const consider = (x, y, kind) => { const d = Math.abs(x - px); if (d < bd) { bd = d; best = { x, y, kind }; } };
  for (const it of S.items) if (!it.got && (it.type === 'gold' || it.type === 'toy')) consider(it.x, it.y, it.type);
  for (const h of C.hedges) if (S.items.some(it => !it.got && it.type === 'cookie' && it.x > h.x && it.x < h.x + h.w)) consider(h.x + h.w / 2, GROUND - 50, 'hedge');
  for (const t of C.trails) if (!S.revealed[t.id]) consider(t.at, t.plats[0][1] - 20, 'trail');
  return best || { x: Math.min(C.BOSS ? ARENA_X + 600 : C.MASTRO_X, px + 700), y: GROUND - 60, kind: 'monkey' };
}
reset();

// a fase abre com o roubo: o Timtim fica parado e o Furtão passa correndo com o Macaco Fedido na boca,
// para na frente dele, ri e foge para a direita (para onde a fase vai). Só então o controle é liberado.
const STEAL = { inT: 1.0, laughT: 3.3, dur: 4.6 }; // a risada gravada dura ~2,2 s: ele fica parado rindo até ela acabar
TT.start = () => { reset(); S.mode = 'play';
  if (FASE >= 2) { S.cine = { type: 'arraial', t: 0, dur: 3.6 }; moveMovers(0); emit('start'); emit('arraialIntro'); return; } // cartão de abertura do Arraial
  if (TT.stealSeen) { emit('start'); return; }
  TT.stealSeen = true; S.thief = { x: -260, dir: 1, state: 'run', t: 0, laughed: false };
  S.cine = { type: 'steal', t: 0, dur: STEAL.dur }; emit('start'); emit('stealIntro'); };
TT.retry = () => {
  if (S.checkpoint < 0) return TT.start();
  const x = C.checkpoints[S.checkpoint];
  S.player = makePlayer(x); S.player.inv = 1.6; S.scent = null; S.boss = makeBoss(); S.fox = makeFox(); S.fruit = null; S.fireOff = 0; S.runners = []; S.runDone = {}; S.warn = null; S.chaseOn = false; S.ball = null; S.thief = null; S.prize = null; S.waves = []; S.arena = false; S.cine = null; S.timeScale = 1; S.slowT = 0; S.hitstop = 0; S.gifts = [];
  S.cam.x = Math.max(0, x - W * 0.4); S.cam.look = 0; S.mode = 'play';
  emit('start', { retry: true });
};
TT.pause = () => { if (S.mode === 'play') { S.mode = 'pause'; emit('pause'); } };
TT.resume = () => { if (S.mode === 'pause') { S.mode = 'play'; emit('resume'); } };

function stats() {
  const allCookies = S.cookies >= Math.ceil(S.totalCookies * 0.8), noHit = S.hpLost === 0, allGold = S.gold >= 3;
  return { notes: S.notes, notesTotal: C.NOTES.length, cookies: S.cookies, total: S.totalCookies, time: S.time, hpLost: S.hpLost, gold: S.gold, toy: S.toy, allCookies, noHit, allGold, stars: 1 + (allCookies ? 1 : 0) + (allGold ? 1 : 0) };
}

// modo demonstração (só o script que grava o vídeo de apresentação liga): o Timtim não leva dano
TT.demo = { noHurt: false };
function hurt(fromX) {
  const p = S.player;
  if (p.inv > 0 || p.mega > 0 || S.mode !== 'play' || TT.demo.noHurt) return;
  p.hp--; S.hpLost++; p.inv = 1.6; p.hurtT = 0.5; S.trauma = Math.min(1, S.trauma + 0.6); S.hitstop = 0.08;
  p.vy = -500; p.vx = (fromX != null ? (Math.sign(p.x + p.w / 2 - fromX) || -p.face) : -p.face) * 260;
  emit('hurt', { x: p.x + p.w / 2, y: p.y });
  if (p.hp <= 0) { S.mode = 'lose'; emit('lose', stats()); }
}

// ---------------- atualização ----------------
TT.update = (rdt) => {
  S.trauma = Math.max(0, S.trauma - rdt * 1.4);
  if (!['play', 'winning', 'win', 'lose'].includes(S.mode)) return;
  if (S.hitstop > 0) { S.hitstop -= rdt; return; } // congela um instante no impacto
  if (S.slowT > 0) { S.slowT -= rdt; S.timeScale = S.slowT > 0 ? 0.2 : 1; }
  const dt = rdt * S.timeScale;
  S.clock += dt;
  if (S.cine) { S.cine.t += rdt; if (S.cine.t >= S.cine.dur) { const type = S.cine.type; S.cine = null; emit('cineEnd', { type }); } }
  updateThief(rdt); updatePrize(rdt);
  const playing = S.mode === 'play', locked = !playing || !!S.cine;
  if (playing && !S.cine) S.time += dt;
  if (S.mode === 'winning') {
    S.winT += rdt;
    // vencido o Furtão, o Timtim desce de cima dele e comemora do lado (antes comemorava em pé dentro do corpo do bulldog)
    const bb = S.boss, pp = S.player, onBoss = C.BOSS && bb.hp <= 0 && Math.abs(pp.x + pp.w / 2 - (bb.x + bb.w / 2)) < bb.w * 0.8;
    if (onBoss && pp.onGround && !pp.won) { pp.vx = (Math.sign(pp.x + pp.w / 2 - (bb.x + bb.w / 2)) || 1) * 240; pp.face = Math.sign(pp.vx); }
    if (S.winT > 0.9 && S.player.onGround && !onBoss) { if (C.BOSS && !S.player.won) S.player.face = Math.sign(bb.x + bb.w / 2 - pp.x) || 1; S.player.won = true; }
    if (S.winT > 3.2) { S.mode = 'win'; S.player.won = true; emit('win', stats()); }
  }

  const p = S.player, I = TT.input;
  if (MOVERS.length) { moveMovers(TT.beatClock()); if (p.on && p.on.mover && p.onGround) { p.x += p.on.dx; p.y += p.on.dy; } }
  p.inv = Math.max(0, p.inv - dt); p.fast = Math.max(0, p.fast - dt); p.mega = Math.max(0, p.mega - dt); p.slow = Math.max(0, p.slow - dt);
  p.hurtT = Math.max(0, p.hurtT - dt); p.shrugT = Math.max(0, (p.shrugT || 0) - dt); p.egg = Math.max(0, (p.egg || 0) - dt);

  const speed = p.fast > 0 || p.mega > 0 ? FAST : p.slow > 0 ? C.SLOW : RUN;
  // faro: no chão, segurando ↓, ele para e fareja; o rastro aparece e, com um instante de faro, o caminho de cheiro se revela
  const sniffing = !locked && I.sniff && p.onGround && playing;
  p.sniff = sniffing ? p.sniff + dt : 0;
  if (sniffing) {
    if (!S.scent || p.sniff === dt) emit('sniff', { x: p.x + p.w / 2 + p.face * 26, y: p.y + p.h - 12 });
    S.scent = Object.assign(scentTarget(p), { t: (S.scent && S.scent.t) || 0, fade: 1 }); S.scent.t += dt;
    if (S.scent.x !== p.x + p.w / 2) p.face = Math.sign(S.scent.x - (p.x + p.w / 2)) || p.face;
    if (p.sniff > C.SNIFF.reveal) for (const t of C.trails) if (!S.revealed[t.id] && Math.abs(t.at - (p.x + p.w / 2)) < C.SNIFF.range) {
      S.revealed[t.id] = true; emit('reveal', { id: t.id, x: t.at, y: t.plats[0][1] }); emit('banner', { text: 'Caminho de cheiro!' }); }
  } else if (S.scent) { S.scent.fade -= dt / 1.2; if (S.scent.fade <= 0) S.scent = null; } // o rastro some devagar
  const dir = locked || sniffing ? 0 : (I.right ? 1 : 0) - (I.left ? 1 : 0);
  const target = dir * speed, accel = p.onGround ? 2600 : 1900;
  if (p.launchT > 0) { /* solto do redemoinho: mantém o impulso um instante */ }
  else if (p.vx < target) p.vx = Math.min(target, p.vx + accel * dt);
  else if (p.vx > target) p.vx = Math.max(target, p.vx - accel * dt);
  if (dir) p.face = dir;
  // dentro de uma moita falsa
  const pcx0 = p.x + p.w / 2; S.inHedge = C.hedges.findIndex(h => pcx0 > h.x && pcx0 < h.x + h.w && p.y + p.h > GROUND - 140);

  // redemoinho (fase 3): pega o Timtim no ar e gira com ele; apertar o pulo solta na direção em que ele está indo.
  // O latido/grasnado do chefão desliga os redemoinhos (S.fireOff), como desligava o ar quente.
  if (C.SWIRLS.length) { p.swirlCd = Math.max(0, (p.swirlCd || 0) - dt); p.launchT = Math.max(0, (p.launchT || 0) - dt);
    if (!p.orbit && playing && !p.onGround && !(p.swirlCd > 0) && !(S.fireOff > 0)) for (let i = 0; i < C.SWIRLS.length; i++) { const s = C.SWIRLS[i], dx = p.x + p.w / 2 - s.x, dy = p.y + p.h / 2 - s.y;
      if (dx * dx + dy * dy < (s.r * 0.8) ** 2) { p.orbit = { i, a: Math.atan2(dy, dx) }; p.gliding = false; emit('swirlIn', { x: s.x, y: s.y }); break; } }
    if (p.orbit && ((I.jumpPressed && !locked) || S.fireOff > 0 || !playing)) { const s = C.SWIRLS[p.orbit.i], a = p.orbit.a, d = s.d || 1, sp = C.SWIRL.speed;
      p.vx = -Math.sin(a) * d * sp; p.vy = Math.cos(a) * d * sp - 120; p.orbit = null; p.swirlCd = 0.5; p.launchT = 0.45; p.boostT = 0.6; p.dj = true; I.jumpPressed = false; p.buffer = 0;
      if (p.vx) p.face = Math.sign(p.vx); emit('swirlOut', { x: p.x + p.w / 2, y: p.y + p.h / 2 }); } }
  p.coyote = p.onGround ? 0.1 : Math.max(0, p.coyote - dt);
  const pressedNow = !locked && I.jumpPressed;
  p.buffer = pressedNow ? 0.12 : Math.max(0, p.buffer - dt);
  I.jumpPressed = false;
  if (p.onGround) p.dj = true;
  p.djT = Math.max(0, p.djT - dt); p.boostT = Math.max(0, (p.boostT || 0) - dt);
  if (p.buffer > 0 && p.coyote > 0) { p.vy = JUMP_V; p.coyote = 0; p.buffer = 0; p.onGround = false; emit('jump', { x: p.x + p.w / 2, y: p.y + p.h }); }
  else if (pressedNow && !p.onGround && p.dj) { // pulo duplo: uma pirueta no ar
    p.dj = false; p.buffer = 0; p.vy = JUMP_V * 0.86; p.djT = 0.42; if (dir) p.vx = dir * Math.max(Math.abs(p.vx), speed * 0.8);
    emit('jump2', { x: p.x + p.w / 2, y: p.y + p.h / 2 });
  }
  // pulo variável (soltar o pulo corta a subida); o impulso do redemoinho e do toldo não é cortado, senão o quique morre no meio
  if ((locked || !I.jump) && p.vy < -300 && !(p.boostT > 0)) p.vy += GRAV * 1.4 * dt;
  const hang = !p.onGround && I.jump && !locked && Math.abs(p.vy) < 130 ? 0.55 : 1; // flutua um instante no topo do pulo
  // planar (fase 2 em diante): segurando o pulo no ar, depois do topo, a bandana abre como asa-delta e a queda fica lenta;
  // em cima de uma fogueira o ar quente levanta, até o topo da coluna
  const lifted = C.GLIDE && !(S.fireOff > 0) && C.fires.some(f => inColumn(p, f));
  const gl = C.GLIDE && !p.onGround && !locked && I.jump && p.djT <= 0 && !(p.noGlide > 0) && !(p.hurtT > 0) && (p.vy > -40 || p.gliding);
  if (gl && !p.gliding) emit('glide', { x: p.x + p.w / 2, y: p.y });
  p.gliding = gl;
  // com o ovo cozido (planar turbinado) a queda é mais lenta e o ar quente levanta mais forte
  const fall = p.egg > 0 ? C.EGG.fall : 135, lift = p.egg > 0 ? C.EGG.lift : C.FIRE.lift;
  if (gl && lifted) p.vy += (lift - p.vy) * Math.min(1, dt * 2.6);
  // planando a queda chega a 135 px/s e para aí (antes a conta deixava ~190 e mudava com a taxa de quadros);
  // vindo de uma queda rápida, ele freia suave até 135
  else if (gl) { if (p.vy < fall) p.vy = Math.min(fall, p.vy + GRAV * 0.3 * dt); else p.vy += (fall - p.vy) * Math.min(1, dt * 9); }
  else p.vy = Math.min(p.vy + GRAV * hang * dt, 1200);
  if (gl && lifted && p.y < C.FIRE.top + 20) p.vy = Math.max(p.vy, -60); // no alto da coluna ele fica pairando

  p.x += p.vx * dt;
  p.x = Math.max(S.arena ? ARENA_X + 4 : 0, Math.min(LEVEL_END - p.w - 4, p.x));
  for (const s of SOLIDS) if (!s.oneWay && solid(s) && overlap(p, s)) { if (p.vx > 0) p.x = s.x - p.w; else if (p.vx < 0) p.x = s.x + s.w; }
  const prevBottom = p.y + p.h;
  p.y += p.vy * dt;
  const wasGround = p.onGround; p.onGround = false; p.on = null;
  for (const s of SOLIDS) {
    if (!solid(s) || !overlap(p, s)) continue;
    if (s.oneWay) { if (p.vy >= 0 && prevBottom <= s.y + 2 + Math.max(0, -(s.dy || 0))) { p.y = s.y - p.h; p.vy = 0; p.onGround = true; p.on = s;
      if (s.bounce) { p.vy = -1080; p.boostT = 0.8; p.onGround = false; p.on = null; p.dj = true; emit('bounce', { x: p.x + p.w / 2, y: s.y }); } } } // toldo: cama elástica
    else if (p.vy >= 0) { p.y = s.y - p.h; p.vy = 0; p.onGround = true; }
    else { p.y = s.y + s.h; p.vy = 0; }
  }
  if (p.onGround) p.gliding = false;
  if (p.onGround && !wasGround) { p.landT = 0.18; emit('land', { x: p.x + p.w / 2, y: p.y + p.h }); }
  { if (C.TUB && playing && !S.revealed.pescaria && Math.abs(p.x + p.w / 2 - C.TUB.x) < C.TUB.w / 2 && p.y + p.h >= GROUND - 2) { S.revealed.pescaria = true; emit('splash', { x: C.TUB.x, y: GROUND }); emit('banner', { text: 'Pescaria! Caíram biscoitos do tanque!' }); } }
  p.landT = Math.max(0, p.landT - dt);
  if (p.onGround && p.y + p.h >= GROUND - 1) p.safeX = p.x;
  S.dustT -= dt;
  if (p.onGround && Math.abs(p.vx) > 160 && S.dustT <= 0) { S.dustT = 0.06; emit('dust', { x: p.x + p.w / 2 - p.face * 14, y: p.y + p.h, dir: -p.face }); }

  if (p.orbit) { const s = C.SWIRLS[p.orbit.i], d = s.d || 1, R = s.r * 0.62; p.orbit.a += d * C.SWIRL.w * dt;
    p.x = s.x + Math.cos(p.orbit.a) * R - p.w / 2; p.y = s.y + Math.sin(p.orbit.a) * R - p.h / 2; p.vx = 0; p.vy = 0; p.onGround = false; p.gliding = false;
    p.face = -Math.sin(p.orbit.a) * d >= 0 ? 1 : -1; }
  // buraco
  if (p.y > H + 80) {
    if (!playing) { p.y = H + 80; p.vy = 0; }
    else if (C.GLIDE_TUT && !S.tut.learned && p.x + p.w / 2 > C.GLIDE_TUT.edge - 60 && p.x < C.GLIDE_TUT.land + 40) { // aula do planar: volta para a beirada, sem perder coração
      Object.assign(p, { x: C.GLIDE_TUT.edge - 110, y: 330 - p.h - 40, vx: 0, vy: 0, inv: 0.6, gliding: false }); S.tut.tries = (S.tut.tries || 0) + 1; S.tut.slowed = false; emit('tutorial', { kind: 'glideRetry' }); }
    else {
      p.hp--; S.hpLost++; S.trauma = 0.6; emit('hurt', { x: p.x, y: H });
      if (p.hp <= 0) { S.mode = 'lose'; emit('lose', stats()); }
      else Object.assign(p, { x: p.safeX - 40 * p.face, y: GROUND - 160, vx: 0, vy: 0, inv: 1.6 });
    }
  }

  if (playing && C.GLIDE) {
    // a fogueira não machuca: é nela que o Timtim pula para subir no ar quente (machucar ali só atrapalhava)
    // dicas na hora certa: o planar antes do primeiro vão, o ar quente antes da primeira fogueira
    const GT = C.GLIDE_TUT;
    if (GT && !S.tut.glide && p.x + p.w > GT.edge - 240) { S.tut.glide = true; emit('tutorial', { kind: 'glideEdge' }); }
    // pulou o vão sem planar: o tempo desacelera um instante e a dica volta, para dar tempo de segurar o pulo
    if (GT && !S.tut.learned && !S.tut.slowed && !p.onGround && !p.gliding && p.vy > 60 && p.x > GT.edge - 20 && p.x < GT.land - 80) { S.tut.slowed = true; S.slowT = 0.9; emit('tutorial', { kind: 'glideHold' }); }
    if (GT && !S.tut.learned && p.onGround && p.x > GT.land) { S.tut.learned = true; emit('tutorial', { kind: 'glideOk' }); }
    if (FASE === 2 && !S.tut.fire && p.x > 3130) { S.tut.fire = true; emit('tutorial', { kind: 'fire' }); }
    if (FASE === 2 && !S.tut.dance && p.x > 4380) { S.tut.dance = true; emit('tutorial', { kind: 'dance' }); }
    // fase 3: as três coisas novas, cada uma na hora em que aparece pela primeira vez
    if (FASE === 3 && !S.tut.swirl && p.x > 560) { S.tut.swirl = true; emit('tutorial', { kind: 'swirl' }); }
    if (FASE === 3 && !S.tut.bounce && p.x > 4880) { S.tut.bounce = true; emit('tutorial', { kind: 'bounce' }); }
    if (FASE === 3 && !S.tut.blink && p.x > 6260) { S.tut.blink = true; emit('tutorial', { kind: 'blink' }); }
    if (C.HOOP && !S.revealed.argola && Math.hypot(p.x + p.w / 2 - C.HOOP.x, p.y + p.h / 2 - C.HOOP.y) < C.HOOP.r) { S.revealed.argola = true; emit('hoop', C.HOOP); emit('banner', { text: FASE === 3 ? 'Passou pela moldura: tubo de tinta dourado!' : 'Passou pela argola: biscoito dourado!' }); }
    // chegada: o mastro de São João (só sem chefe; no Arraial a vitória é derrotar o lobo-guará)
    if (!C.FOX && p.x + p.w / 2 > C.GOAL_X) { S.mode = 'winning'; S.winT = 0; p.gliding = false; emit('goal', { x: C.MASTRO_X });
      S.friends.forEach((f, i) => { f.home = C.MASTRO_X - 150 + i * 260; f.given = true; f.follow = 0; }); }
  }
  if (playing) for (const t of C.trails) if (!S.revealed[t.id] && C.TOY && Math.hypot(p.x + p.w / 2 - C.TOY.x, p.y - C.TOY.y) < 150) { S.revealed[t.id] = true; emit('reveal', { id: t.id, x: t.at, y: t.plats[0][1] }); }
  if (playing) {
    // checkpoints
    C.checkpoints.forEach((cx, i) => { if (i > S.checkpoint && p.x > cx) { S.checkpoint = i; emit('checkpoint', { index: i, x: cx }); } });
    // itens
    for (const it of S.items) {
      if (it.got || (it.trail && !S.revealed[it.trail])) continue;
      const box = { x: it.x - 20, y: it.y - 20, w: 40, h: 40 };
      if (!overlap(p, box)) continue;
      it.got = true;
      if (it.type === 'cookie') { S.cookies++; emit('cookie', it); }
      if (it.type === 'gold') { S.gold++; emit('power', it); emit('gold', it); }
      if (it.type === 'choco') { if (p.mega <= 0) { p.slow = 5; p.fast = 0; emit('choco', it); } }
      if (it.type === 'toy') { S.toy = true; S.hitstop = 0.1; emit('toy', it); emit('banner', { text: FASE === 3 ? 'Brinquedo perdido: o Girassol de Apito!' : FASE === 2 ? 'Brinquedo perdido: a Sanfoninha!' : 'Brinquedo perdido: o Patinho!' }); }
      if (it.type === 'bilhete') { S.notes++; emit('note', { x: it.x, y: it.y, text: C.NOTES[it.idx].text, n: S.notes, total: C.NOTES.length }); }
    }
  }

  // amigos: quando o Timtim chega perto, dão um pulinho e jogam um biscoito de presente
  const pcx = p.x + p.w / 2;
  for (const f of S.friends) {
    f.t += dt; f.hop = Math.max(0, f.hop - dt); f.follow = Math.max(0, f.follow - dt);
    // corre ao encontro do Timtim, acompanha uns passos depois do presente e volta para o seu lugar
    const seen = playing && Math.abs(pcx - f.home) < 460, chase = seen && (!f.given || f.follow > 0);
    const goal = Math.max(f.home - 20, Math.min(f.home + 280, chase ? pcx - Math.sign(pcx - f.x) * 70 : f.home));
    const want = f.hop > 0.35 || Math.abs(goal - f.x) < 10 ? 0 : Math.sign(goal - f.x) * (chase || !playing ? 260 : 130);
    f.vx += (want - f.vx) * Math.min(1, dt * 9);
    // amigos não andam no ar: se o próximo passo sai do chão (beirada de um buraco), param na beirada
    { const nx = f.x + f.vx * dt, edge = nx + Math.sign(f.vx) * 16; if (groundAt(f.x) && !groundAt(edge)) f.vx = 0; else f.x = nx; }
    if (Math.abs(f.vx) > 30) f.face = Math.sign(f.vx); else if (seen || !playing) f.face = pcx < f.x ? -1 : 1;
    if (playing && !f.given && Math.abs(pcx - f.x) < 120) {
      f.given = true; f.hop = 0.9; f.follow = 3.2; S.gifts.push({ sx: f.x + f.face * 18, sy: GROUND - 58, x: f.x, y: GROUND - 58, t: 0, kind: S.friends.indexOf(f) });
      emit('friend', { x: f.x, y: GROUND - 70, kind: f.kind });
    }
  }
  for (let i = S.gifts.length - 1; i >= 0; i--) {
    const g = S.gifts[i]; g.t += dt / 0.8; const k = Math.min(1, g.t), e = k * k * (3 - 2 * k);
    g.x = g.sx + (pcx - g.sx) * e; g.y = g.sy + (p.y + p.h / 2 - g.sy) * e - Math.sin(k * Math.PI) * 110;
    if (k >= 1) {
      S.gifts.splice(i, 1); if (S.mode !== 'play' && S.mode !== 'winning') continue; if (!g.fight && C.GIFT_ITEM !== 'ovo') S.cookies += C.GIFT; p.hp = Math.min(3, p.hp + 1);
      const pw = S.friends[g.kind] && S.friends[g.kind].power;
      p.slow = 0; if (pw === 'none') { /* só o biscoito e o coração */ } else if (pw === 'egg') { p.egg = C.EGG.time; emit('egg', { x: g.x, y: g.y }); }
      else if (pw === 'fast' || (!pw && g.kind === 0)) p.fast = 8; else p.mega = 9;
      emit('gift', { x: g.x, y: g.y }); emit('power', g);
    }
  }

  // pombos
  for (const e of S.enemies) {
    if (!e.alive) { if (FASE === 3) { e.y -= 300 * dt; e.x -= 180 * dt; } else { e.dy += GRAV * dt; e.y += e.dy * dt; } continue; } // corvo pisado sai voando
    e.t += dt;
    if (FASE === 2) { const d = (p.x + p.w / 2) - (e.x + e.w / 2), near = playing && Math.abs(d) < 230 && Math.abs(p.y - e.y) < 220;
      e.bolt = Math.max(0, (e.bolt || 0) - dt);
      if (near && !e.bolt) e.dir = d > 0 ? -1 : 1; // foge para longe do Timtim
      if (near && !e.scared) emit('cluck', { x: e.x + e.w / 2, y: e.y });
      e.scared = near || e.bolt > 0; const sp = e.bolt > 0 ? 250 : near ? 185 : 70; e.x += e.dir * sp * dt;
      const hop = e.scared ? Math.abs(Math.sin(e.t * (e.bolt > 0 ? 13 : 10))) * (e.bolt > 0 ? 40 : 22) : 0; e.y = GROUND - 30 - hop; // pulinhos de susto
      if (e.x < e.a || e.x > e.b) { e.x = Math.max(e.a, Math.min(e.b, e.x)); if (near && !e.bolt) { e.bolt = 0.6; e.dir = d > 0 ? 1 : -1; emit('cluck', { x: e.x + e.w / 2, y: e.y }); } else if (!e.bolt) e.dir = e.x <= e.a ? 1 : -1; } // encurralada: dispara passando por ele
    } else { e.x += e.dir * 70 * dt; if (e.x < e.a) { e.x = e.a; e.dir = 1; } if (e.x > e.b) { e.x = e.b; e.dir = -1; } }
    if (!playing || !overlap(p, e)) continue;
    // caindo por cima (mesmo com ela dando pulinhos de susto): quica e ela foge
    if (FASE === 2 && (p.mega > 0 || (p.vy > 0 && (prevBottom <= e.y + 18 || p.y + p.h / 2 < e.y + e.h / 2)))) { if (p.mega <= 0) p.vy = -560; e.bolt = 0.8; e.dir = (e.x + e.w / 2) < p.x + p.w / 2 ? -1 : 1; e.scared = true; S.hitstop = 0.04;
      emit('cluck', { x: e.x + e.w / 2, y: e.y }); emit('henBounce', { x: e.x + e.w / 2, y: e.y }); continue; }
    if (FASE === 2 && (e.bolt > 0 || p.shrugT > 0)) continue;
    if (p.mega > 0 || (p.vy > 0 && prevBottom <= e.y + 14)) {
      e.alive = false; e.dy = -400; S.hitstop = 0.05; S.trauma = Math.min(1, S.trauma + 0.25);
      if (p.mega <= 0) p.vy = -560;
      emit('stomp', { x: e.x + e.w / 2, y: e.y, boss: false });
    } else hurt(e.x + e.w / 2);
  }

  // arena
  if (playing && C.BOSS && !S.arena && p.x > ARENA_X + 120) {
    S.arena = true;
    // os chihuahuas entram na arena e ficam um em cada canto, prontos para jogar a bolinha
    S.friends.forEach((f, i) => { f.home = i ? ARENA_X + W - 70 : ARENA_X + 50; f.x = i ? ARENA_X + W + 70 : ARENA_X - 70; f.given = true; f.follow = 0; f.vx = 0; });
    if (!S.bossSeen) { S.bossSeen = true; S.cine = { type: 'boss', t: 0, dur: 3.4, barks: 0 }; emit('bossIntro'); }
    else emit('rematch');
  }
  if (S.arena && C.BOSS) updateBoss(dt, prevBottom, playing);
  if (playing && C.FOX && !S.arena && p.x > ARENA_X + 120) { S.arena = true;
    S.friends.forEach((f, i) => { f.home = i ? ARENA_X + W - 210 : ARENA_X + 190; f.x = i ? ARENA_X + W + 70 : ARENA_X - 70; f.given = true; f.follow = 0; f.vx = 0; });
    scatterHens(); S.fox.state = 'idle'; S.fox.vx = 0; S.fox.dir = -1; S.fox.cd = Math.max(S.fox.cd || 0, 1.6); // sem teleporte: ele continua de onde estava caçando (antes sumia e reaparecia do outro lado)
    if (!S.bossSeen) { S.bossSeen = true; S.cine = { type: 'fox', t: 0, dur: 3.2 }; emit('foxIntro'); } else emit('rematch'); }
  if (C.FOX && C.PREFIGHT && !S.arena) preFight(dt);
  if (C.FOX) updateRunners(dt, prevBottom, playing);
  if (S.arena && C.FOX) updateFox(dt, prevBottom, playing);

  // câmera
  const cam = S.cam;
  cam.look += (p.vx * 0.32 - cam.look) * Math.min(1, dt * 2.5);
  const want = S.arena ? ARENA_X : Math.max(0, Math.min(ARENA_X, p.x - W * 0.4 + cam.look));
  cam.x += (want - cam.x) * Math.min(1, dt * 5);
  const wantY = S.arena ? Math.max(C.FOX ? -170 : -60, Math.min(0, (p.y + p.h - (GROUND - 150)) * (C.FOX ? 0.45 : 0.3))) : Math.max(-260, Math.min(0, (p.y + p.h - (GROUND - 70)) * 0.6)); // sobe junto quando ele vai alto (planando, a argola): não fica colado no placar
  cam.y += (wantY - cam.y) * Math.min(1, dt * 3.4);
};

function updateThief(rdt) {
  const q = S.thief; if (!q) return; q.t += rdt;
  const p = S.player, stop = p.x + p.w / 2 + 330;
  if (q.t < STEAL.inT) { const k = q.t / STEAL.inT; q.state = 'run'; q.dir = 1; q.x = -260 + (stop + 260) * (1 - (1 - k) * (1 - k)); }
  else if (q.t < STEAL.laughT) { // vira para o Timtim e ri com o macaco na boca
    if (q.state !== 'laugh') { q.state = 'laugh'; q.dir = -1; q.x = stop; emit('laugh', { x: q.x, y: GROUND - 120 }); }
  } else { q.state = 'run'; q.dir = 1; q.x += 980 * rdt; if (q.x > S.cam.x + W + 400) S.thief = null; }
  if (S.thief && q.x > S.cam.x - 60) p.face = q.x > p.x ? 1 : -1; // só se vira quando o ladrão aparece na tela
}
function updatePrize(rdt) {
  const m = S.prize; if (!m) return; m.t += rdt;
  if (!m.rest) { const dt = rdt * S.timeScale; m.vy += GRAV * dt; m.x += m.vx * dt; m.y += m.vy * dt; m.spin += dt * 9;
    if (m.y >= GROUND - 30 && m.vy > 0) { m.y = GROUND - 30; m.rest = true; m.t = 0; m.spin = 0; emit('monkeyLand', { x: m.x, y: GROUND }); } }
}
function throwBall() {
  const b = S.boss, f = S.friends[b.thrower++ % 2], fromLeft = f.home < ARENA_X + W / 2;
  // cai do lado oposto ao do Brutão, para ele precisar atravessar a arena (e o Timtim ter tempo de chegar)
  const bx = b.x + b.w / 2, tx = bx > ARENA_X + W / 2 ? ARENA_X + 170 + Math.random() * 220 : ARENA_X + W - 390 + Math.random() * 220;
  S.ball = { x: f.x, y: GROUND - 56, vx: (tx - f.x) / 1.15, vy: -620, rest: false, held: false };
  f.hop = 0.7; f.face = fromLeft ? 1 : -1;
  emit('throw', { x: f.x, y: GROUND - 60, kind: f.kind });
}
function updateBall(dt) {
  const q = S.ball; if (!q || q.held) return;
  if (q.rest) return;
  q.vy += GRAV * 0.75 * dt; q.x += q.vx * dt; q.y += q.vy * dt;
  if (q.x < ARENA_X + 20) { q.x = ARENA_X + 20; q.vx = Math.abs(q.vx) * 0.6; }
  if (q.x > ARENA_X + W - 20) { q.x = ARENA_X + W - 20; q.vx = -Math.abs(q.vx) * 0.6; }
  if (q.y > GROUND - 14) { q.y = GROUND - 14; if (q.vy > 140) emit('ballBounce', { x: q.x, y: GROUND }); q.vy = -q.vy * 0.48; q.vx *= 0.72; if (Math.abs(q.vy) < 90) { q.vy = 0; q.vx = 0; q.rest = true; } }
}
function updateBoss(dt, prevBottom, playing) {
  const p = S.player, b = S.boss, ph = Math.max(0, Math.min(2, 3 - b.hp));
  const cine = S.cine && S.cine.type === 'boss' ? S.cine : null;
  if (cine) { // apresentação: o Brutão late duas vezes para a câmera
    const n = cine.t > 1.7 ? 2 : cine.t > 1.0 ? 1 : 0;
    if (n > cine.barks) { cine.barks = n; b.state = 'bark'; b.t = 0; emit('bigBark', { x: b.x + b.w / 2, y: b.y }); S.trauma = Math.min(1, S.trauma + 0.3); }
  }
  b.hurt = Math.max(0, b.hurt - dt); b.landT = Math.max(0, b.landT - dt); b.turnT = Math.max(0, b.turnT - dt); b.t += dt;
  const bx = b.x + b.w / 2, pcx = p.x + p.w / 2, onGround = b.y + b.h >= GROUND - 0.5;
  if (b.hp <= 0) { b.vy += GRAV * dt; b.y = Math.min(GROUND - b.h, b.y + b.vy * dt); b.x += b.vx * dt; b.vx *= 0.97; return; }
  const face = d => { if (d && d !== b.dir) { b.dir = d; b.turnT = 0.25; } };
  const go = (st) => { b.state = st; b.t = 0; };
  const idle = cd => { go('idle'); b.cd = cd; };

  updateBall(dt);
  // a bolinha: chega de tempos em tempos, quando ele não está no meio de um ataque
  // (o relógio corre sempre; se ele estiver no meio de uma investida ou salto, a bolinha espera ele terminar)
  if (!cine && playing && !S.ball && !['alert', 'fetch', 'chew', 'hurt'].includes(b.state)) { b.ballT -= dt; if (b.ballT <= 0 && ['idle', 'bark', 'bonk', 'land'].includes(b.state)) { throwBall(); go('alert'); } }

  if (cine || !playing) b.vx *= 0.9;
  else switch (b.state) {
    case 'idle': { // anda devagar na direção do Timtim e escolhe o próximo ataque
      face(Math.sign(pcx - bx)); b.vx += (b.dir * (70 + ph * 25) - b.vx) * Math.min(1, dt * 3);
      b.cd -= dt;
      if (b.cd <= 0 && onGround) {
        const pool = ['charge'].concat(ph >= 1 ? ['bark'] : [], ph >= 2 ? ['pound'] : []);
        const pick = pool.length > 1 ? pool.filter(a => a !== b.last) : pool;
        b.atk = b.last = pick[Math.floor(Math.random() * pick.length)]; go('wind');
      }
      break; }
    case 'wind': { // aviso do ataque: cava o chão, enche o peito ou se agacha — dá para ler o que vem
      b.vx *= 0.8; face(Math.sign(pcx - bx));
      if (b.atk === 'charge' && Math.random() < dt * 14) emit('dig', { x: bx - b.dir * 50, y: GROUND });
      if (b.t >= BOSS.wind[b.atk] * (ph === 2 ? 0.8 : 1)) {
        if (b.atk === 'charge') { go('charge'); b.vx = b.dir * BOSS.charge[ph]; emit('bark'); }
        else if (b.atk === 'bark') { go('bark'); S.waves.push({ x: bx + b.dir * 70, dir: b.dir, v: 430 + ph * 70, t: 0 }); if (ph >= 2) S.waves.push({ x: bx - b.dir * 70, dir: -b.dir, v: 380, t: 0 }); emit('bigBark', { x: bx, y: b.y }); S.trauma = Math.min(1, S.trauma + 0.3); }
        else { go('jump'); b.tx = Math.max(ARENA_X + 90, Math.min(ARENA_X + W - 90, pcx)); b.vy = -1050; b.vx = (b.tx - bx) / (2 * 1050 / GRAV); emit('bossJump', { x: bx, y: GROUND }); }
      }
      break; }
    case 'charge': // atravessa a arena até dar com a cara na parede
      if ((b.dir < 0 && b.x <= ARENA_X + 12) || (b.dir > 0 && b.x + b.w >= ARENA_X + W - 12)) { b.vx = 0; go('bonk'); S.trauma = Math.min(1, S.trauma + 0.4); emit('bonk', { x: b.dir < 0 ? b.x : b.x + b.w, y: GROUND - 50 }); }
      break;
    case 'bonk': b.vx *= 0.8; if (b.t > 0.7) idle(1.1 - ph * 0.2); break;
    case 'bark': b.vx *= 0.8; if (b.t > 0.75) idle(1.2 - ph * 0.25); break;
    case 'jump': if (onGround && b.t > 0.2) { b.vx = 0; go('land'); S.trauma = Math.min(1, S.trauma + 0.65); emit('pound', { x: bx, y: GROUND });
        S.waves.push({ x: bx + 80, dir: 1, v: 330, t: 0, small: true }, { x: bx - 80, dir: -1, v: 330, t: 0, small: true }); } break;
    case 'land': if (b.t > 0.55) idle(1.0); break;
    case 'alert': b.vx *= 0.7; face(Math.sign((S.ball ? S.ball.x : pcx) - bx)); if (b.t > 0.35) go('fetch'); break; // orelhas em pé: bolinha!
    case 'fetch': { // corre atrás da bolinha
      const q = S.ball; if (!q) { idle(0.5); break; }
      face(Math.sign(q.x - bx)); const d = q.x - (bx + b.dir * 55);
      b.vx += ((Math.abs(d) > 10 ? Math.sign(d) * 430 : 0) - b.vx) * Math.min(1, dt * 6);
      if (q.rest && Math.abs(d) < 26) { b.vx = 0; q.held = true; go('chew'); emit('chew', { x: q.x, y: GROUND }); }
      break; }
    case 'chew': b.vx = 0; if (S.ball) { S.ball.x = bx + b.dir * 58; S.ball.y = GROUND - 16; }
      if (b.t > BOSS.chew[ph]) { S.ball = null; b.ballT = BOSS.ballEvery[ph]; idle(0.5); emit('bark'); } break;
    case 'hurt': b.vx *= 0.85; if (b.t > 1.1) { b.ballT = BOSS.ballEvery[ph]; idle(0.7); emit('bigBark', { x: bx, y: b.y }); } break;
  }
  b.vy += GRAV * dt; b.x += b.vx * dt; b.y += b.vy * dt;
  if (b.y + b.h > GROUND) { if (b.vy > 350) b.landT = 0.24; b.y = GROUND - b.h; b.vy = 0; }
  b.x = Math.max(ARENA_X + 10, Math.min(ARENA_X + W - 10 - b.w, b.x));

  // ondas de choque do latido: correm pelo chão; é preciso pular
  for (let i = S.waves.length - 1; i >= 0; i--) {
    const w = S.waves[i]; w.t += dt; w.x += w.dir * w.v * dt;
    if (w.x < ARENA_X - 40 || w.x > ARENA_X + W + 40) { S.waves.splice(i, 1); continue; }
    const hh = w.small ? 22 : 34;
    if (playing && !cine && p.y + p.h > GROUND - hh && Math.abs(pcx - w.x) < 20 + p.w / 2 && p.mega <= 0) hurt();
  }

  if (!playing || cine) return;
  const hb = { x: b.x + 12, y: b.y + 10, w: b.w - 24, h: b.h - 10 };
  if (!overlap(p, hb)) return;
  // pular nele nunca tira coração: caindo por cima (mesmo nas costas, com ele andando ou investindo) conta como pisão.
  // O desenho do Furtão é mais alto que o corpo de colisão, então "por cima" é qualquer contato com o Timtim descendo
  // e com os pés acima da metade do corpo dele. Só esbarrar de lado, no chão, machuca.
  if (p.vy > 0 && (prevBottom <= b.y + 28 || p.y + p.h < b.y + b.h * 0.6)) {
    if (b.state === 'chew') { // pisão na cabeça enquanto ele está distraído: acerta!
      b.hp--; b.hurt = 0.4; go('hurt'); S.ball = null; p.vy = -760;
      S.hitstop = 0.12; S.trauma = Math.min(1, S.trauma + 0.55);
      emit('stomp', { x: bx, y: b.y, boss: true });
      if (b.hp <= 0) {
        b.vy = -500; b.vx = -b.dir * 180; S.waves.length = 0;
        S.mode = 'winning'; S.winT = 0; S.slowT = 0.75;
        S.friends.forEach((f, i) => { f.home = Math.max(ARENA_X + 60, p.x - 120 - i * 85) + (p.x < ARENA_X + 300 ? 330 : 0); f.vx = 0; });
        // o Macaco Fedido pula do Furtão e cai bem do lado do Timtim
        const land = Math.max(ARENA_X + 60, Math.min(ARENA_X + W - 60, pcx + (bx > pcx ? 70 : -70))), vy = -980, T = 2 * -vy / GRAV;
        S.prize = { x: bx + b.dir * 50, y: b.y + 20, vx: (land - (bx + b.dir * 50)) / T, vy, rest: false, t: 0, spin: 0 };
        emit('finalBlow', { x: bx, y: b.y }); emit('monkeyFree', { x: bx, y: b.y });
      }
    } else { p.vy = -720; p.vx = (pcx < bx ? -1 : 1) * 280; p.dj = true; p.shrugT = 0.45; emit('shrug', { x: bx, y: b.y }); } // ele sacode o Timtim para o alto
  // depois da sacudida o Timtim ainda passa por dentro do corpo dele subindo: isso não é esbarrão, não tira coração
  } else if (!['chew', 'hurt', 'bonk'].includes(b.state) && p.mega <= 0 && !(p.shrugT > 0)) hurt();
}
})();
