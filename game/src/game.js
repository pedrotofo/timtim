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
const FASE = TT.FASE = C.FASE = new URLSearchParams(location.search).get('fase') === '2' ? 2 : 1;
Object.assign(C, { BOSS: true, GLIDE: false, fires: [], movers: [], GOAL_X: C.ARENA_X, MASTRO_X: 0, GIFT_ITEM: 'cookie', EGG: { time: 12, fall: 70, lift: -470 } });
if (FASE === 2) Object.assign(C, {
  BOSS: false, GLIDE: true, LEVEL_END: 7900, ARENA_X: 7900 - W0, GOAL_X: 7480, MASTRO_X: 7580, START_X: 200,
  grounds: [[0, 1150], [1670, 700], [3000, 1500], [5880, 280], [6300, 1600]],
  plats: [[430, 250, 120], [700, 330, 450], [2150, 300, 200], [3500, 90, 170], [4120, 140, 150]],
  // tábuas da quadrilha: x e y da posição de descanso, ax/ay = quanto vão e voltam, per = período (s), ph = fase do passo
  movers: [{ x: 4580, y: 320, w: 150, ax: 100, ay: 0, per: 2.4, ph: 0 }, { x: 4950, y: 290, w: 140, ax: 0, ay: 70, per: 2.4, ph: Math.PI },
           { x: 5280, y: 320, w: 150, ax: 110, ay: 0, per: 2.4, ph: Math.PI / 2 }, { x: 5600, y: 280, w: 140, ax: 0, ay: 80, per: 2.4, ph: 0 }],
  fires: [{ x: 3410 }, { x: 4040 }, { x: 6610 }, { x: 7250 }],
  checkpoints: [1720, 3060, 6340],
  // a Zara e o Elvis ajudam jogando ovo cozido, a comida preferida do Timtim: o primeiro, antes da quadrilha, dá o planar
  // turbinado (cai bem devagar e o ar quente sobe mais); o segundo, antes do trecho final, deixa invencível
  friends: [{ x: 4380, kind: 'chi-pb', power: 'egg' }, { x: 5960, kind: 'chi-br', power: 'mega' }], GIFT_ITEM: 'ovo',
  hedges: [],
  trails: [{ id: 'sanfona', at: 6610, plats: [[6690, 120, 130], [6555, 10, 120]] }],
  TOY: { id: 'sanfoninha', x: 6615, y: -40 },
});
C.FIRE = { w: 64, h: 62, col: 64, top: -70, lift: -380 }; // chama que machuca; coluna de ar quente que sobe até y = top
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
function arraialItems() {
  const it = [], G = GROUND - 40, cookie = (x, y, trail) => it.push({ type: 'cookie', x, y, got: false, trail });
  [300, 360, 420].forEach(x => cookie(x, G)); cookie(490, 200); [780, 840, 1040, 1100].forEach(x => cookie(x, 280));
  [[1230, 290], [1330, 320], [1430, 350], [1530, 380], [1630, 405]].forEach(([x, y]) => cookie(x, y));
  for (let x = 1800; x <= 2100; x += 60) cookie(x, G); [2200, 2290].forEach(x => cookie(x, 250));
  [[2480, 250], [2600, 270], [2720, 290], [2840, 320], [2960, 350]].forEach(([x, y]) => cookie(x, y));
  [3120, 3180, 3240].forEach(x => cookie(x, G)); [330, 250, 170, 90].forEach(y => cookie(3410, y)); [3560, 3620].forEach(x => cookie(x, 40));
  [4170, 4230].forEach(x => cookie(x, 90)); [4290, 4340].forEach(x => cookie(x, G));
  [[4655, 250], [5020, 200], [5355, 250], [5670, 180]].forEach(([x, y]) => cookie(x, y));
  [5950, 6020, 6090].forEach(x => cookie(x, G)); [6400, 6460, 6880, 6940].forEach(x => cookie(x, G)); [7380, 7430].forEach(x => cookie(x, G));
  cookie(6750, 70, 'sanfona');
  [[900, 110], [3410, -10], [5440, 60]].forEach(([x, y]) => it.push({ type: 'gold', x, y, got: false }));
  [1950, 3880, 6820].forEach(x => it.push({ type: 'choco', x, y: GROUND - 34, got: false }));
  it.push({ type: 'toy', id: C.TOY.id, x: C.TOY.x, y: C.TOY.y, got: false, trail: 'sanfona' });
  for (const o of it) for (const [px, py, pw] of C.plats.concat(...C.trails.map(t => t.plats))) if (o.x > px - 20 && o.x < px + pw + 20 && o.y < py && o.y > py - 50) o.y = py - 50;
  return it;
}
function makeEnemies() {
  if (FASE === 2) return [[2050, 1760, 2340], [3720, 3540, 3900], [6900, 6760, 7120], [7420, 7330, 7470]]
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
function makeBoss() {
  return { name: 'Furtão', x: ARENA_X + 700, y: GROUND - 100, w: 150, h: 100, vx: 0, vy: 0, dir: -1, hp: 3,
    state: 'idle', atk: '', last: '', t: 0, cd: 1.8, hurt: 0, spin: 0, landT: 0, turnT: 0, tx: 0, ballT: 4, thrower: 0 };
}
function makePlayer(x) {
  return { x, y: GROUND - 60, w: 54, h: 50, vx: 0, vy: 0, onGround: false, face: 1, hp: 3, inv: 0, fast: 0, mega: 0, slow: 0,
    safeX: x, coyote: 0, buffer: 0, landT: 0, won: false, hurtT: 0, dj: true, djT: 0, sniff: 0, egg: 0 };
}

const SOLIDS = [];
for (const [x, w] of C.grounds) SOLIDS.push({ x, y: GROUND, w, h: 200, oneWay: false });
for (const [x, y, w] of C.plats) SOLIDS.push({ x, y, w, h: 18, oneWay: true });
for (const t of C.trails) for (const [x, y, w] of t.plats) SOLIDS.push({ x, y, w, h: 18, oneWay: true, trail: t.id }); // só existem depois de farejadas
// tábuas da quadrilha: sólidos que se movem; a posição é recalculada a cada quadro e quem está em cima vai junto
const MOVERS = C.movers.map(m => { const s = { x: m.x, y: m.y, w: m.w, h: 18, oneWay: true, mover: m, dx: 0, dy: 0 }; SOLIDS.push(s); return s; });
TT.MOVERS = MOVERS;
function moveMovers(clock) {
  for (const s of MOVERS) { const m = s.mover, a = Math.PI * 2 * clock / m.per + m.ph, nx = m.x + m.ax * Math.sin(a), ny = m.y + m.ay * Math.sin(a);
    s.dx = nx - s.x; s.dy = ny - s.y; s.x = nx; s.y = ny; }
}
moveMovers(0);
// fogueiras: a chama machuca quem encosta; a coluna de ar quente em cima levanta quem está planando
const fireBox = f => ({ x: f.x - C.FIRE.w / 2, y: GROUND - C.FIRE.h, w: C.FIRE.w, h: C.FIRE.h });
const inColumn = (p, f) => Math.abs(p.x + p.w / 2 - f.x) < C.FIRE.col && p.y > C.FIRE.top;
const solid = s => !s.trail || S.revealed[s.trail];
TT.SOLIDS = SOLIDS;
const overlap = (a, b) => a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;

const S = TT.S = { mode: 'title' };
function reset() {
  Object.assign(S, {
    player: makePlayer(C.START_X), items: makeItems(), enemies: makeEnemies(), boss: makeBoss(), ball: null, waves: [],
    cam: { x: 0, y: 0, look: 0 }, time: 0, clock: 0, cookies: 0, arena: false, trauma: 0, hitstop: 0,
    gold: 0, timeScale: 1, slowT: 0, cine: null, checkpoint: -1, bossSeen: false, hpLost: 0, winT: 0, dustT: 0,
    thief: null, prize: null, revealed: {}, toy: false, scent: null,
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
  if (FASE === 2) { S.cine = { type: 'arraial', t: 0, dur: 2.6 }; moveMovers(0); emit('start'); emit('arraialIntro'); return; } // cartão de abertura do Arraial
  S.thief = { x: -260, dir: 1, state: 'run', t: 0, laughed: false };
  S.cine = { type: 'steal', t: 0, dur: STEAL.dur }; emit('start'); emit('stealIntro'); };
TT.retry = () => {
  if (S.checkpoint < 0) return TT.start();
  const x = C.checkpoints[S.checkpoint];
  S.player = makePlayer(x); S.player.inv = 1.6; S.scent = null; S.boss = makeBoss(); S.ball = null; S.thief = null; S.prize = null; S.waves = []; S.arena = false; S.cine = null; S.timeScale = 1; S.slowT = 0; S.hitstop = 0; S.gifts = [];
  S.cam.x = Math.max(0, x - W * 0.4); S.cam.look = 0; S.mode = 'play';
  emit('start', { retry: true });
};
TT.pause = () => { if (S.mode === 'play') { S.mode = 'pause'; emit('pause'); } };
TT.resume = () => { if (S.mode === 'pause') { S.mode = 'play'; emit('resume'); } };

function stats() {
  const allCookies = S.cookies >= Math.ceil(S.totalCookies * 0.8), noHit = S.hpLost === 0, allGold = S.gold >= 3;
  return { cookies: S.cookies, total: S.totalCookies, time: S.time, hpLost: S.hpLost, gold: S.gold, toy: S.toy, allCookies, noHit, allGold, stars: 1 + (allCookies ? 1 : 0) + (allGold ? 1 : 0) };
}

// modo demonstração (só o script que grava o vídeo de apresentação liga): o Timtim não leva dano
TT.demo = { noHurt: false };
function hurt() {
  const p = S.player;
  if (p.inv > 0 || p.mega > 0 || S.mode !== 'play' || TT.demo.noHurt) return;
  p.hp--; S.hpLost++; p.inv = 1.6; p.hurtT = 0.5; S.trauma = Math.min(1, S.trauma + 0.6); S.hitstop = 0.08;
  p.vy = -500; p.vx = -p.face * 260;
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
    if (S.winT > 0.9 && S.player.onGround) S.player.won = true;
    if (S.winT > 3.2) { S.mode = 'win'; S.player.won = true; emit('win', stats()); }
  }

  const p = S.player, I = TT.input;
  if (MOVERS.length) { moveMovers(S.clock); if (p.on && p.on.mover && p.onGround) { p.x += p.on.dx; p.y += p.on.dy; } }
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
  if (p.vx < target) p.vx = Math.min(target, p.vx + accel * dt);
  else if (p.vx > target) p.vx = Math.max(target, p.vx - accel * dt);
  if (dir) p.face = dir;
  // dentro de uma moita falsa
  const pcx0 = p.x + p.w / 2; S.inHedge = C.hedges.findIndex(h => pcx0 > h.x && pcx0 < h.x + h.w && p.y + p.h > GROUND - 140);

  p.coyote = p.onGround ? 0.1 : Math.max(0, p.coyote - dt);
  const pressedNow = !locked && I.jumpPressed;
  p.buffer = pressedNow ? 0.12 : Math.max(0, p.buffer - dt);
  I.jumpPressed = false;
  if (p.onGround) p.dj = true;
  p.djT = Math.max(0, p.djT - dt);
  if (p.buffer > 0 && p.coyote > 0) { p.vy = JUMP_V; p.coyote = 0; p.buffer = 0; p.onGround = false; emit('jump', { x: p.x + p.w / 2, y: p.y + p.h }); }
  else if (pressedNow && !p.onGround && p.dj) { // pulo duplo: uma pirueta no ar
    p.dj = false; p.buffer = 0; p.vy = JUMP_V * 0.86; p.djT = 0.42; if (dir) p.vx = dir * Math.max(Math.abs(p.vx), speed * 0.8);
    emit('jump2', { x: p.x + p.w / 2, y: p.y + p.h / 2 });
  }
  if ((locked || !I.jump) && p.vy < -300) p.vy += GRAV * 1.4 * dt; // pulo variável
  const hang = !p.onGround && I.jump && !locked && Math.abs(p.vy) < 130 ? 0.55 : 1; // flutua um instante no topo do pulo
  // planar (fase 2 em diante): segurando o pulo no ar, depois do topo, a bandana abre como asa-delta e a queda fica lenta;
  // em cima de uma fogueira o ar quente levanta, até o topo da coluna
  const lifted = C.GLIDE && C.fires.some(f => inColumn(p, f));
  const gl = C.GLIDE && !p.onGround && !locked && I.jump && p.djT <= 0 && (p.vy > -40 || (lifted && p.gliding));
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
    if (s.oneWay) { if (p.vy >= 0 && prevBottom <= s.y + 2 + Math.max(0, -(s.dy || 0))) { p.y = s.y - p.h; p.vy = 0; p.onGround = true; p.on = s; } }
    else if (p.vy >= 0) { p.y = s.y - p.h; p.vy = 0; p.onGround = true; }
    else { p.y = s.y + s.h; p.vy = 0; }
  }
  if (p.onGround && !wasGround) { p.landT = 0.18; emit('land', { x: p.x + p.w / 2, y: p.y + p.h }); }
  p.landT = Math.max(0, p.landT - dt);
  if (p.onGround && p.y + p.h >= GROUND - 1) p.safeX = p.x;
  S.dustT -= dt;
  if (p.onGround && Math.abs(p.vx) > 160 && S.dustT <= 0) { S.dustT = 0.06; emit('dust', { x: p.x + p.w / 2 - p.face * 14, y: p.y + p.h, dir: -p.face }); }

  // buraco
  if (p.y > H + 80) {
    if (!playing) { p.y = H + 80; p.vy = 0; }
    else {
      p.hp--; S.hpLost++; S.trauma = 0.6; emit('hurt', { x: p.x, y: H });
      if (p.hp <= 0) { S.mode = 'lose'; emit('lose', stats()); }
      else Object.assign(p, { x: p.safeX - 40 * p.face, y: GROUND - 160, vx: 0, vy: 0, inv: 1.6 });
    }
  }

  if (playing && C.fires.length) {
    for (const f of C.fires) if (overlap(p, fireBox(f))) hurt(); // encostou na chama
    // dicas na hora certa: o planar antes do primeiro vão, o ar quente antes da primeira fogueira
    if (!S.tut.glide && p.x > 560) { S.tut.glide = true; emit('tutorial', { kind: 'glide' }); }
    if (!S.tut.fire && p.x > 3130) { S.tut.fire = true; emit('tutorial', { kind: 'fire' }); }
    if (!S.tut.dance && p.x > 4380) { S.tut.dance = true; emit('tutorial', { kind: 'dance' }); }
    // chegada: o mastro de São João
    if (p.x + p.w / 2 > C.GOAL_X) { S.mode = 'winning'; S.winT = 0; p.gliding = false; emit('goal', { x: C.MASTRO_X });
      S.friends.forEach((f, i) => { f.home = C.MASTRO_X - 150 + i * 260; f.given = true; f.follow = 0; }); }
  }
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
      if (it.type === 'toy') { S.toy = true; S.hitstop = 0.1; emit('toy', it); emit('banner', { text: 'Brinquedo perdido: o Patinho!' }); }
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
    f.vx += (want - f.vx) * Math.min(1, dt * 9); f.x += f.vx * dt;
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
      S.gifts.splice(i, 1); S.cookies += C.GIFT; p.hp = Math.min(3, p.hp + 1);
      const pw = S.friends[g.kind] && S.friends[g.kind].power;
      p.slow = 0; if (pw === 'none') { /* só o biscoito e o coração */ } else if (pw === 'egg') { p.egg = C.EGG.time; emit('egg', { x: g.x, y: g.y }); }
      else if (pw === 'fast' || (!pw && g.kind === 0)) p.fast = 8; else p.mega = 9;
      emit('gift', { x: g.x, y: g.y }); emit('power', g);
    }
  }

  // pombos
  for (const e of S.enemies) {
    if (!e.alive) { e.dy += GRAV * dt; e.y += e.dy * dt; continue; }
    e.t += dt; e.x += e.dir * 70 * dt;
    if (e.x < e.a) { e.x = e.a; e.dir = 1; } if (e.x > e.b) { e.x = e.b; e.dir = -1; }
    if (!playing || !overlap(p, e)) continue;
    if (p.mega > 0 || (p.vy > 0 && prevBottom <= e.y + 14)) {
      e.alive = false; e.dy = -400; S.hitstop = 0.05; S.trauma = Math.min(1, S.trauma + 0.25);
      if (p.mega <= 0) p.vy = -560;
      emit('stomp', { x: e.x + e.w / 2, y: e.y, boss: false });
    } else hurt();
  }

  // arena
  if (playing && C.BOSS && !S.arena && p.x > ARENA_X + 120) {
    S.arena = true;
    // os chihuahuas entram na arena e ficam um em cada canto, prontos para jogar a bolinha
    S.friends.forEach((f, i) => { f.home = i ? ARENA_X + W - 70 : ARENA_X + 50; f.x = i ? ARENA_X + W + 70 : ARENA_X - 70; f.given = true; f.follow = 0; f.vx = 0; });
    if (!S.bossSeen) { S.bossSeen = true; S.cine = { type: 'boss', t: 0, dur: 3.4, barks: 0 }; emit('bossIntro'); }
    else emit('rematch');
  }
  if (S.arena) updateBoss(dt, prevBottom, playing);

  // câmera
  const cam = S.cam;
  cam.look += (p.vx * 0.32 - cam.look) * Math.min(1, dt * 2.5);
  const want = S.arena ? ARENA_X : Math.max(0, Math.min(ARENA_X, p.x - W * 0.4 + cam.look));
  cam.x += (want - cam.x) * Math.min(1, dt * 5);
  const wantY = S.arena ? Math.max(-60, Math.min(0, (p.y + p.h - (GROUND - 150)) * 0.3)) : Math.max(-150, Math.min(0, (p.y + p.h - (GROUND - 70)) * 0.42));
  cam.y += (wantY - cam.y) * Math.min(1, dt * 3.4);
};

function updateThief(rdt) {
  const q = S.thief; if (!q) return; q.t += rdt;
  const p = S.player, stop = p.x + p.w / 2 + 330;
  if (q.t < STEAL.inT) { const k = q.t / STEAL.inT; q.state = 'run'; q.dir = 1; q.x = -260 + (stop + 260) * (1 - (1 - k) * (1 - k)); }
  else if (q.t < STEAL.laughT) { // vira para o Timtim e ri com o macaco na boca
    if (q.state !== 'laugh') { q.state = 'laugh'; q.dir = -1; q.x = stop; p.vy = -330; p.onGround = false; emit('laugh', { x: q.x, y: GROUND - 120 }); }
  } else { q.state = 'run'; q.dir = 1; q.x += 980 * rdt; if (q.x > S.cam.x + W + 400) S.thief = null; }
  if (S.thief) p.face = q.x > p.x ? 1 : -1;
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
