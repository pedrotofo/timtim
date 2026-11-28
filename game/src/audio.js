// Som: efeitos gravados (Artlist, em assets/sfx) e trilha gravada (assets/music).
// Os efeitos e a trilha sintetizados abaixo continuam como reserva enquanto os arquivos carregam ou se algum faltar.
(() => {
'use strict';
const TT = window.TT;
let ctx = null, master, comp, musicBus, trackBus, sfxBus, noiseBuf;
let muted = false; const VOL = 1.0; // volume geral (era 0,9 com o compressor de fábrica, que somava ganho)
try { muted = localStorage.getItem('tintim-mute') === '1'; } catch (_) {}

function init() {
  if (ctx) { if (ctx.state === 'suspended') ctx.resume(); return true; }
  try {
    ctx = new (window.AudioContext || window.webkitAudioContext)();
    master = ctx.createGain(); master.gain.value = muted ? 0 : VOL;
    // proteção contra estouro: só age nos picos (acima de -6 dB). No ajuste de fábrica do navegador (-24 dB) ele apertava tudo,
    // e cada pancada ou latido abaixava a música uns 5 dB (a música "respirava")
    comp = ctx.createDynamicsCompressor(); comp.threshold.value = -6; comp.knee.value = 4; comp.ratio.value = 12; comp.attack.value = 0.003; comp.release.value = 0.25;
    master.connect(comp).connect(ctx.destination);
    musicBus = ctx.createGain(); musicBus.gain.value = 0.32; musicBus.connect(master);
    // sala grande: reverberação gerada (ruído que decai) para a trilha soar como orquestra num salão
    const len = ctx.sampleRate * 3.2, ir = ctx.createBuffer(2, len, ctx.sampleRate);
    for (let c = 0; c < 2; c++) { const d = ir.getChannelData(c); for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, 2.6); }
    const hall = ctx.createConvolver(); hall.buffer = ir; const wet = ctx.createGain(); wet.gain.value = 0.55; musicBus.connect(hall).connect(wet).connect(master);
    trackBus = ctx.createGain(); trackBus.gain.value = 0.62; trackBus.connect(master);
    sfxBus = ctx.createGain(); sfxBus.gain.value = 0.8; sfxBus.connect(master);
    noiseBuf = ctx.createBuffer(1, ctx.sampleRate * 0.5, ctx.sampleRate);
    const d = noiseBuf.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
    loadSamples(); loadVoices(); loadTrack(TRACKS.level); loadTrack(TRACKS.boss);
    return true;
  } catch (_) { ctx = null; return false; }
}

function tone(f, t, dur, { type = 'triangle', vol = 0.2, slide = 0, bus = sfxBus, attack = 0.005 } = {}) {
  const o = ctx.createOscillator(), g = ctx.createGain();
  o.type = type; o.frequency.setValueAtTime(f, t);
  if (slide) o.frequency.exponentialRampToValueAtTime(Math.max(30, f * slide), t + dur);
  g.gain.setValueAtTime(0.0001, t); g.gain.linearRampToValueAtTime(vol, t + attack);
  g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
  o.connect(g).connect(bus); o.start(t); o.stop(t + dur + 0.02);
}
// latido: serra com a altura caindo, passando por dois filtros de "boca" (formantes), com um sopro de ruído no começo.
// f0 = altura da voz; f1/f2 = formantes (cachorro grande = graves, chihuahua = agudos); growl = rosnado (tremolo).
function woof(t, { f0 = 300, dur = 0.16, f1 = 900, f2 = 2000, vol = 0.25, growl = 0 } = {}) {
  const o = ctx.createOscillator(), b1 = ctx.createBiquadFilter(), b2 = ctx.createBiquadFilter(), g = ctx.createGain(), mix = ctx.createGain();
  o.type = 'sawtooth'; o.frequency.setValueAtTime(f0 * 1.55, t); o.frequency.exponentialRampToValueAtTime(f0, t + dur * 0.35); o.frequency.exponentialRampToValueAtTime(f0 * 0.62, t + dur);
  b1.type = b2.type = 'bandpass'; b1.frequency.value = f1; b2.frequency.value = f2; b1.Q.value = 3; b2.Q.value = 4;
  g.gain.setValueAtTime(0.0001, t); g.gain.linearRampToValueAtTime(vol, t + 0.008); g.gain.exponentialRampToValueAtTime(vol * 0.5, t + dur * 0.45); g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
  o.connect(b1).connect(mix); o.connect(b2).connect(mix); mix.connect(g).connect(sfxBus);
  if (growl) { const l = ctx.createOscillator(), lg = ctx.createGain(); l.frequency.value = 34; lg.gain.value = growl; l.connect(lg).connect(mix.gain); l.start(t); l.stop(t + dur + 0.02); }
  o.start(t); o.stop(t + dur + 0.02);
  noise(t, 0.035, { vol: vol * 0.6, freq: f2, q: 1.2 });
}
function noise(t, dur, { vol = 0.2, freq = 2000, q = 1, type = 'bandpass', bus = sfxBus } = {}) {
  const s = ctx.createBufferSource(), f = ctx.createBiquadFilter(), g = ctx.createGain();
  s.buffer = noiseBuf; f.type = type; f.frequency.value = freq; f.Q.value = q;
  g.gain.setValueAtTime(vol, t); g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
  s.connect(f).connect(g).connect(bus); s.start(t); s.stop(t + dur + 0.02);
}

// cordas: três serras desafinadas atrás de um filtro que abre devagar
function strings(f, t, dur, vol = 0.05) {
  const lp = ctx.createBiquadFilter(), g = ctx.createGain(); lp.type = 'lowpass'; lp.Q.value = 0.4;
  lp.frequency.setValueAtTime(300, t); lp.frequency.linearRampToValueAtTime(1500, t + dur * 0.5); lp.frequency.linearRampToValueAtTime(500, t + dur);
  g.gain.setValueAtTime(0.0001, t); g.gain.linearRampToValueAtTime(vol, t + dur * 0.35); g.gain.linearRampToValueAtTime(0.0001, t + dur);
  [-7, 0, 8].forEach(c => { const o = ctx.createOscillator(); o.type = 'sawtooth'; o.frequency.value = f; o.detune.value = c; o.connect(lp); o.start(t); o.stop(t + dur + 0.05); });
  lp.connect(g).connect(musicBus);
}

const sfx = {
  glide: t => { noise(t, 0.32, { vol: 0.09, freq: 900, q: 0.8, type: 'lowpass' }); noise(t + 0.04, 0.22, { vol: 0.05, freq: 2600, q: 1.5 }); },
  jump: t => { tone(330, t, 0.16, { type: 'sine', vol: 0.22, slide: 2.1 }); noise(t, 0.06, { vol: 0.05, freq: 3000 }); },
  jump2: t => { tone(520, t, 0.22, { type: 'sine', vol: 0.16, slide: 2.4 }); tone(1040, t + 0.03, 0.3, { type: 'triangle', vol: 0.06, slide: 1.8 }); noise(t, 0.18, { vol: 0.04, freq: 5200, q: 2 }); },
  friend: t => { [0, 0.11].forEach(o => tone(760, t + o, 0.08, { type: 'triangle', vol: 0.13, slide: 1.35 })); },
  gift: t => [784, 988, 1175, 1568].forEach((f, i) => tone(f, t + i * 0.07, 0.4, { type: 'sine', vol: 0.13, attack: 0.01 })),
  land: t => { tone(120, t, 0.09, { type: 'sine', vol: 0.18, slide: 0.5 }); noise(t, 0.07, { vol: 0.07, freq: 700 }); },
  cookie: t => { tone(1175, t, 0.07, { vol: 0.16 }); tone(1568, t + 0.06, 0.12, { vol: 0.16 }); },
  power: t => [523, 659, 784, 1046, 1318].forEach((f, i) => tone(f, t + i * 0.06, 0.18, { vol: 0.16 })),
  stomp: t => { tone(180, t, 0.2, { type: 'sine', vol: 0.4, slide: 0.35 }); noise(t, 0.12, { vol: 0.2, freq: 900 }); tone(660, t + 0.02, 0.1, { type: 'square', vol: 0.06, slide: 1.6 }); },
  hurt: t => { tone(300, t, 0.28, { type: 'sawtooth', vol: 0.16, slide: 0.4 }); noise(t, 0.15, { vol: 0.12, freq: 500 }); },
  bark: t => { [0, 0.13].forEach(o => { tone(260, t + o, 0.09, { type: 'sawtooth', vol: 0.14, slide: 1.5 }); noise(t + o, 0.08, { vol: 0.1, freq: 1100, q: 2 }); }); },
  bonk: t => { tone(140, t, 0.3, { type: 'square', vol: 0.18, slide: 0.4 }); noise(t, 0.2, { vol: 0.2, freq: 400 }); tone(1200, t + 0.05, 0.25, { type: 'sine', vol: 0.08, slide: 0.6 }); },
  pound: t => { tone(55, t, 0.6, { type: 'sine', vol: 0.5, slide: 0.5 }); noise(t, 0.45, { vol: 0.3, freq: 250, type: 'lowpass' }); },
  throwBall: t => { tone(600, t, 0.12, { type: 'triangle', vol: 0.12, slide: 1.6 }); [0, 0.1].forEach(o => tone(900, t + 0.05 + o, 0.06, { type: 'triangle', vol: 0.1, slide: 1.3 })); },
  squeak: t => { tone(1400, t, 0.12, { type: 'sine', vol: 0.12, slide: 1.4 }); tone(1100, t + 0.14, 0.12, { type: 'sine', vol: 0.1, slide: 1.3 }); },
  boing: t => { tone(220, t, 0.25, { type: 'sine', vol: 0.22, slide: 2.4 }); },
  // Brutão: dois latidos graves e roucos, com um soco no peito
  bigBark: t => { woof(t, { f0: 150, dur: 0.32, f1: 520, f2: 1150, vol: 0.42, growl: 0.6 }); woof(t + 0.36, { f0: 135, dur: 0.38, f1: 480, f2: 1050, vol: 0.4, growl: 0.7 }); tone(70, t, 0.25, { type: 'sine', vol: 0.3, slide: 0.6 }); },
  // investida do Brutão: um latido grave só
  bossWoof: t => woof(t, { f0: 140, dur: 0.3, f1: 500, f2: 1100, vol: 0.38, growl: 0.5 }),
  // Zara: "iip-iip" bem agudo e curtinho
  yapZara: t => { woof(t, { f0: 780, dur: 0.09, f1: 1700, f2: 3200, vol: 0.2 }); woof(t + 0.12, { f0: 860, dur: 0.09, f1: 1800, f2: 3400, vol: 0.2 }); },
  // Elvis: "arf!" mais encorpado, com um "rrf" no fim
  yapElvis: t => { woof(t, { f0: 520, dur: 0.15, f1: 1150, f2: 2500, vol: 0.24 }); woof(t + 0.17, { f0: 430, dur: 0.11, f1: 1000, f2: 2200, vol: 0.16, growl: 0.4 }); },
  checkpoint: t => [659, 880, 1318].forEach((f, i) => tone(f, t + i * 0.09, 0.2, { vol: 0.14 })),
  boss: t => { tone(70, t, 1.2, { type: 'sawtooth', vol: 0.2, slide: 0.6 }); noise(t, 0.9, { vol: 0.12, freq: 200, type: 'lowpass' }); },
  final: t => { tone(90, t, 0.9, { type: 'sine', vol: 0.5, slide: 0.3 }); noise(t, 0.5, { vol: 0.25, freq: 600 }); },
  win: t => [523, 659, 784, 1046, 784, 1046, 1318].forEach((f, i) => tone(f, t + i * 0.13, 0.3, { vol: 0.18 })),
  lose: t => [392, 349, 311, 262].forEach((f, i) => tone(f, t + i * 0.18, 0.35, { vol: 0.16, type: 'sine' })),
  star: t => { tone(1318, t, 0.1, { vol: 0.16 }); tone(1976, t + 0.07, 0.25, { vol: 0.14 }); },
  ui: t => tone(880, t, 0.05, { vol: 0.1 }),
  // faro: três fungadas curtas e rápidas
  sniff: t => [0, 0.11, 0.2].forEach((o, i) => noise(t + o, 0.07, { vol: 0.16 - i * 0.03, freq: 2600 + i * 300, q: 1.4 })),
  // caminho de cheiro revelado: um brilho que sobe
  reveal: t => [392, 523, 659, 880, 1175].forEach((f, i) => tone(f, t + i * 0.05, 0.3, { type: 'sine', vol: 0.1, attack: 0.01 })),
  // brinquedo achado: "quá-quá" de patinho de borracha e um acorde
  toy: t => { [0, 0.16].forEach(o => tone(1250, t + o, 0.12, { type: 'square', vol: 0.06, slide: 0.7 })); [523, 659, 784, 1046].forEach((f, i) => tone(f, t + 0.32 + i * 0.07, 0.4, { type: 'sine', vol: 0.12, attack: 0.01 })); },
  // Furtão rindo com o macaco na boca: "he-he-he" grave, cada vez mais baixo (reserva do arquivo gravado)
  laugh: t => { [0, 0.16, 0.32, 0.5].forEach((o, i) => woof(t + o, { f0: 190 - i * 8, dur: 0.12, f1: 700, f2: 1500, vol: 0.3 - i * 0.05 })); },
  choco: t => { [330, 277, 233, 185].forEach((f, i) => tone(f, t + i * 0.12, 0.22, { type: 'sawtooth', vol: 0.1, slide: 0.85 })); tone(90, t + 0.5, 0.5, { type: 'sine', vol: 0.25, slide: 0.6 }); },
};
// ---- efeitos gravados, mixados em camadas (25/11/2026, skill audio-design) ----
// Cada som tem uma camada e um volume-alvo (db): o nível que ele deve ter na mixagem, medido como o pico de volume em 100 ms
// depois do barramento de efeitos. A música fica por volta de -21 dB; com isso nada passa por cima dela de surpresa.
//   heroi: o que o Timtim faz (pulo, biscoito, dano, poderes) - pequeno e claro, um pouco abaixo da música
//   golpe: chefões e pancadas - os mais fortes, mas no máximo uns 5 dB acima da música; quando tocam, o "mundo" abaixa um pouco
//   mundo: bichos do cenário (galinhas, corvos pequenos, pombos, latidinhos da turma) - atrás de tudo, mais escuros e com poucos ao mesmo tempo
//   ui: menus e jingles
// max = quantos sons da camada tocam juntos (no mundo, o que passar do limite não toca; nas outras, o mais antigo sai em fade).
// vary = quanto a altura muda a cada vez (repetições não soam iguais); gap = intervalo mínimo entre duas vezes do mesmo som.
// NIVEL = o volume medido de cada arquivo (scratchpad/medir_sfx.py); ao trocar um arquivo, medir de novo e atualizar aqui.
// 'vida' existe desde 28/11/2026 só para o dano: na camada 'heroi' um biscoito ou um pulo
// posterior EXPULSAVA o 'hurt' (a lista tira o mais antigo), então o som que informa a perda de
// um coração era descartável. Sozinho na camada, nada o expulsa.
const CAMADAS = { vida: { max: 1 }, heroi: { max: 4 }, golpe: { max: 2 }, mundo: { max: 2 }, ui: { max: 2 } };
const NIVEL = { bigBark: -8.2, boing: -8.5, bonk: -5.7, boss: -15.4, bossWoof: -11.7, checkpoint: -13.3, choco: -12.9, cluck1: -12.1, cluck2: -11.4, cookie: -21.4, crowCaw: -22.2, crowSmall: -8.7, crowWings: -17.0, diveWhistle: -7.8, eggCrack: -22.2, final: -4.1, gift: -10.8, henCoop: -11.6, henFlap: -13.4, henPanic: -11.3, hurt: -13.3, jump: -17.5, jump2: -16.1, land: -26.8, laugh: -14.9, lose: -9.2, pigeon: -19.1, pound: -6.3, power: -10.4, squeak: -14.4, star: -11.2, stomp: -13.3, swirl: -10.7, throwBall: -17.0, thud: -20.1, ui: -17.6, whimper: -11.7, win: -10.6, yapElvis: -12.1, yapZara: -10.4, yelp: -8.2 };
const SAMPLES = {
  // heroi
  jump: { c: 'heroi', db: -27, vary: 0.06 }, jump2: { c: 'heroi', db: -26, vary: 0.05 }, land: { c: 'heroi', db: -32, vary: 0.1 },
  cookie: { c: 'heroi', db: -31, vary: 0.12, gap: 0.09 }, power: { c: 'heroi', db: -21 }, gift: { c: 'heroi', db: -21 }, star: { c: 'heroi', db: -22 },
  checkpoint: { c: 'heroi', db: -23 }, hurt: { c: 'vida', db: -16, vary: 0.05 }, throwBall: { c: 'heroi', db: -27, vary: 0.06 }, squeak: { c: 'heroi', db: -26, vary: 0.08 },
  choco: { c: 'heroi', db: -22, vary: 0.06 }, eggCrack: { c: 'heroi', db: -24 }, swirl: { c: 'heroi', db: -26, gap: 0.4 }, swirlOut: { c: 'heroi', db: -24, gap: 0.12, vary: 0.04, arq: 'swirl', rate: 1.5 },
  // golpe (chefões)
  bossWoof: { c: 'golpe', db: -19, vary: 0.04 }, bigBark: { c: 'golpe', db: -18, vary: 0.03 }, stomp: { c: 'golpe', db: -19, vary: 0.07 },
  pound: { c: 'golpe', db: -18, vary: 0.04 }, bonk: { c: 'golpe', db: -22, vary: 0.06 }, final: { c: 'golpe', db: -16 }, boss: { c: 'golpe', db: -19 },
  thud: { c: 'golpe', db: -22, vary: 0.08, gap: 0.12 }, boing: { c: 'golpe', db: -22, vary: 0.06 }, laugh: { c: 'golpe', db: -21 },
  crowCaw: { c: 'golpe', db: -20, vary: 0.05, gap: 0.5 }, crowWings: { c: 'golpe', db: -24, vary: 0.08, gap: 0.45 }, diveWhistle: { c: 'golpe', db: -22 },
  yelp: { c: 'golpe', db: -21, vary: 0.04 }, whimper: { c: 'golpe', db: -21 },
  // mundo (bichos do cenário)
  cluck1: { c: 'mundo', db: -27, vary: 0.08, gap: 0.3 }, cluck2: { c: 'mundo', db: -27, vary: 0.08, gap: 0.3 }, henPanic: { c: 'mundo', db: -25 },
  henFlap: { c: 'mundo', db: -28, vary: 0.08, gap: 0.15 }, henCoop: { c: 'mundo', db: -23 }, pigeon: { c: 'mundo', db: -29, vary: 0.06 },
  crowSmall: { c: 'mundo', db: -28, vary: 0.1, gap: 0.3 }, yapZara: { c: 'mundo', db: -25, vary: 0.04 }, yapElvis: { c: 'mundo', db: -25, vary: 0.04 },
  // ui e jingles
  ui: { c: 'ui', db: -26 }, win: { c: 'ui', db: -18 }, lose: { c: 'ui', db: -18 },
};
const BUS_DB = 20 * Math.log10(0.8); // o barramento de efeitos (sfxBus = 0,8)
for (const n in SAMPLES) { const o = SAMPLES[n], lv = NIVEL[n] === undefined ? -12 : NIVEL[n]; o.v = Math.min(1.6, Math.pow(10, (o.db - lv - BUS_DB) / 20)); }
const sbufs = {}, lastAt = {}, ativos = { vida: [], heroi: [], golpe: [], mundo: [], ui: [] }, camadaBus = {};
function loadSamples() {
  // as camadas: o "mundo" passa por um filtro que tira um pouco do grave e do agudo (fica atrás, sem brigar com o Timtim e os golpes)
  for (const c in CAMADAS) { const g = ctx.createGain(); camadaBus[c] = g;
    if (c === 'mundo') { const hp = ctx.createBiquadFilter(), lp = ctx.createBiquadFilter(); hp.type = 'highpass'; hp.frequency.value = 140; lp.type = 'lowpass'; lp.frequency.value = 6500; g.connect(hp).connect(lp).connect(sfxBus); }
    else g.connect(sfxBus); }
  Object.keys(SAMPLES).forEach(n => fetch('assets/sfx/' + (SAMPLES[n].arq || n) + '.mp3').then(r => { if (!r.ok) throw 0; return r.arrayBuffer(); })
    .then(a => ctx.decodeAudioData(a)).then(b => { sbufs[n] = b; }).catch(() => {}));
}
function playSample(name, t) {
  const b = sbufs[name]; if (!b) return false;
  const o = SAMPLES[name], cam = o.c || 'heroi', lista = ativos[cam];
  let v = o.v;
  if (o.gap) { const dt = t - (lastAt[name] || -9); if (dt < o.gap) return true; if (dt < 0.6) v *= 0.65; lastAt[name] = t; }
  // limite de sons ao mesmo tempo na camada
  for (let i = lista.length - 1; i >= 0; i--) if (lista[i].fim <= t) lista.splice(i, 1);
  if (lista.length >= CAMADAS[cam].max) { if (cam === 'mundo') return true; const velho = lista.shift(); velho.g.gain.setTargetAtTime(0, t, 0.02); try { velho.src.stop(t + 0.12); } catch (_) {} }
  const src = ctx.createBufferSource(), g = ctx.createGain(), rate = (o.rate || 1) * (1 + (Math.random() * 2 - 1) * (o.vary || 0));
  src.buffer = b; src.playbackRate.value = rate; g.gain.value = v;
  src.connect(g).connect(camadaBus[cam]); src.start(t);
  lista.push({ src, g, fim: t + b.duration / rate });
  // golpe forte: o mundo abaixa uns 7 dB e volta em meio segundo (a pancada aparece sem precisar ser alta)
  if (cam === 'vida') for (const c of ['golpe', 'mundo']) { const d = camadaBus[c].gain;
    d.cancelScheduledValues(t); d.setTargetAtTime(0.5, t, 0.01); d.setTargetAtTime(1, t + 0.15, 0.1); }
  if (cam === 'golpe') { const m = camadaBus.mundo.gain; m.cancelScheduledValues(t); m.setTargetAtTime(0.45, t, 0.015); m.setTargetAtTime(1, t + 0.25, 0.2); }
  return true;
}
// para os testes: quantos sons tocam agora em cada camada e o volume-alvo de cada som
TT.mixInfo = () => { const now = ctx ? ctx.currentTime : 0, c = {}; for (const k in ativos) c[k] = ativos[k].filter(x => x.fim > now).length;
  const d = {}; for (const k in SAMPLES) d[k] = SAMPLES[k].db; return { camadas: c, alvos: d }; };
// ---- narração do card de cada fase (assets/voice/intro-fase1.mp3 a intro-fase3.mp3, gravadas pelo Pedro): a mesma frase do pergaminho.
// Se o arquivo da fase não existir, o card fica só com a imagem, a frase e a música.
// Enquanto ele fala, a música abaixa. Se a fala ainda não carregou quando o quadro começa, entra assim que chegar (até 1,2 s depois).
// fases que já têm a narração gravada (quando o arquivo da fase chegar, ponha o número dela aqui; sem isso o navegador acusaria arquivo faltando)
const NARRADAS = [1, 2, 3];
const vbufs = []; let voiceSrc = null, voiceWant = null;
function loadVoices() {
  [1, 2, 3].forEach((n, i) => NARRADAS.includes(n) && n === (TT.FASE || 1) && fetch('assets/voice/intro-fase' + n + '.mp3').then(r => { if (!r.ok) throw 0; return r.arrayBuffer(); })
    .then(a => ctx.decodeAudioData(a)).then(b => { vbufs[i] = b; if (voiceWant && voiceWant.i === i && performance.now() - voiceWant.at < 1200) playVoice(i); }).catch(() => {}));
}
function stopVoice() { if (voiceSrc) { try { voiceSrc.stop(); } catch (_) {} voiceSrc = null; } TT.audioDuck(false); }
function playVoice(i) {
  stopVoice(); voiceWant = null; const b = vbufs[i]; if (!b) return;
  const s = ctx.createBufferSource(), g = ctx.createGain(); s.buffer = b; g.gain.value = 0.48; s.connect(g).connect(master); // fala por volta de -21 dB e picos de -16 dB: clara, sem gritar (antes 1,1: uns 12 dB acima da música)
  s.start(ctx.currentTime + 0.3); voiceSrc = s; TT.audioDuck(true, 0.6);
  s.onended = () => { if (voiceSrc === s) { voiceSrc = null; TT.audioDuck(false); } };
}
TT.voice = i => { if (!init()) return; if (i < 0) { voiceWant = null; return stopVoice(); } voiceWant = { i, at: performance.now() }; if (vbufs[i]) playVoice(i); };

TT.audioNodes = () => ({ ctx, comp, master }); // para os testes medirem a mixagem
TT.sfx = name => { if (!init()) return; const t = ctx.currentTime; if (playSample(name, t)) return; if (sfx[name]) sfx[name](t); };

// ---- trilha: caixinha de música etérea para a fase e um baião tenso para a luta com o Brutão ----
const N = n => 440 * Math.pow(2, (n - 69) / 12);
const SONGS = {
  level: { bpm: 100, soft: true,
    lead: [74, 0, 78, 81, 0, 78, 81, 83, 81, 0, 78, 0, 76, 78, 74, 0,  76, 0, 79, 83, 0, 79, 83, 84, 83, 0, 79, 0, 78, 76, 74, 0,
           74, 0, 78, 81, 0, 78, 81, 83, 86, 0, 84, 0, 83, 81, 78, 0,  79, 0, 78, 76, 0, 74, 76, 78, 74, 0, 0, 0, 74, 0, 0, 0],
    bass: [50, 50, 55, 57], },
  boss: { bpm: 150,
    lead: [69, 0, 69, 72, 0, 69, 76, 0, 75, 0, 72, 0, 69, 0, 67, 0,  69, 0, 69, 72, 0, 69, 77, 0, 76, 0, 72, 0, 71, 0, 68, 0],
    bass: [45, 45, 41, 40], },
};
SONGS.title = { bpm: 58, soft: true, lead: SONGS.level.lead, bass: [50, 47, 43, 45] };
let song = null, step = 0, nextT = 0, timer = null;
function schedule() {
  if (!ctx || !song) return;
  const s = SONGS[song], st = 60 / s.bpm / 4;
  while (nextT < ctx.currentTime + 0.15) {
    const i = step % s.lead.length, bar = Math.floor(step / 16) % s.bass.length, b = step % 16;
    const n = s.lead[i];
    if (s.soft) { // fase: a mesma melodia, tocada como caixinha de música sobre um colchão de notas longas
      if (n) { tone(N(n), nextT, st * 4.5, { type: 'sine', vol: 0.11, attack: 0.012, bus: musicBus }); tone(N(n) * 2, nextT, st * 2.5, { type: 'triangle', vol: 0.028, bus: musicBus }); }
      if (b === 0) [0, 7, 12, 16].forEach((o, k) => tone(N(s.bass[bar] + o), nextT, st * 17, { type: 'sine', vol: k ? 0.035 : 0.09, attack: 0.5, bus: musicBus }));
      if (b === 0) [12, 19, 24, 28].forEach(o => strings(N(s.bass[bar] + o), nextT, st * 17, 0.03));
      if (b === 8) tone(N(s.bass[bar] + 12), nextT, st * 6, { type: 'triangle', vol: 0.05, attack: 0.05, bus: musicBus });
      if (b % 4 === 2) noise(nextT, 0.05, { vol: 0.012, freq: 6000, q: 3, bus: musicBus });
      step++; nextT += st; continue;
    }
    if (n) { tone(N(n), nextT, st * 1.8, { type: 'square', vol: 0.09, bus: musicBus }); tone(N(n) * 2, nextT, st, { type: 'triangle', vol: 0.05, bus: musicBus }); }
    // baixo no ritmo do baião: 1, "e" do 2, 3
    if (b === 0) [12, 19, 24].forEach(o => strings(N(s.bass[bar] + o), nextT, st * 16, 0.045));
    if (b === 0 || b === 6 || b === 8 || b === 14) tone(N(s.bass[bar] - (b === 6 || b === 14 ? 0 : 0)), nextT, st * 2.4, { type: 'triangle', vol: 0.26, bus: musicBus });
    if (b === 0 || b === 6 || b === 8) tone(110, nextT, 0.12, { type: 'sine', vol: 0.32, slide: 0.4, bus: musicBus }); // zabumba
    if (b % 2 === 0) noise(nextT, 0.03, { vol: b % 4 === 2 ? 0.07 : 0.035, freq: 7000, q: 3, bus: musicBus });         // triângulo
    step++; nextT += st;
  }
}
// ---- trilha gravada: cada fase tem a sua (fase e chefão); toca em laço com fusão entre o fim e o começo. A trilha sintetizada acima
// cobre se o arquivo faltar. Fase 1: theme/boss (do Pedro, Suno). Fase 2: arraial/arraial-boss. Fase 3: quadro/quadro-boss.
// A trilha do Arraial toca em laço exato de 64 compassos (sem fusão), para a batida nunca escorregar: TT.beatTime() diz em que
// ponto da música estamos, e o pulso visual (lanternas, brilho das tábuas) dança nesse relógio. Andamento e primeiro tempo
// medidos no arquivo. Desde 28/11/2026 este relógio NÃO move mais as tábuas da quadrilha: a física anda em S.clock (ver
// TT.beatClock em game.js). Som enfeita; nenhuma mecânica do jogo pode depender de ouvir.
const LOOPS = { arraial: { bpm: 97.98, beat0: 0.399, bars: 64 } };
const FASE_MUS = { 1: ['theme', 'boss'], 2: ['arraial', 'arraial-boss'], 3: ['quadro', 'quadro-boss'] }[TT.FASE] || ['theme', 'boss'];
const TRACKS = { title: FASE_MUS[0], level: FASE_MUS[0], boss: FASE_MUS[1] }, bufs = {};
let track = null;
function stopTrack() {
  if (!track) return; const t = track; track = null; t.alive = false;
  t.g.gain.setTargetAtTime(0, ctx.currentTime, 0.18);
  setTimeout(() => { t.srcs.forEach(s => { try { s.stop(); } catch (_) {} }); t.g.disconnect(); }, 900);
}
function playTrack(file) {
  const buf = bufs[file], XF = 1.2, g = ctx.createGain(); g.connect(trackBus);
  const t = track = { file, g, alive: true, srcs: [] };
  const L = LOOPS[file];
  if (L) { const s = ctx.createBufferSource(); s.buffer = buf; s.loop = true; s.loopStart = L.beat0; s.loopEnd = L.beat0 + L.bars * 4 * 60 / L.bpm;
    s.connect(g); t.start = ctx.currentTime + 0.05; t.beat0 = L.beat0; s.start(t.start); t.srcs.push(s); return; } // toca a introdução uma vez; o laço volta para o primeiro tempo
  const next = at => {
    if (!t.alive) return;
    const s = ctx.createBufferSource(), e = ctx.createGain(), end = at + buf.duration; s.buffer = buf;
    e.gain.setValueAtTime(0, at); e.gain.linearRampToValueAtTime(1, at + XF); e.gain.setValueAtTime(1, end - XF); e.gain.linearRampToValueAtTime(0, end);
    s.connect(e).connect(g); s.start(at); t.srcs.push(s); if (t.srcs.length > 3) t.srcs.shift();
    setTimeout(() => next(Math.max(end - XF, ctx.currentTime + 0.05)), Math.max(0, (end - XF - ctx.currentTime - 1.5) * 1000));
  };
  next(ctx.currentTime + 0.05);
}
function loadTrack(file) {
  if (file in bufs) return; bufs[file] = null;
  fetch('assets/music/' + file + '.mp3').then(r => { if (!r.ok) throw 0; return r.arrayBuffer(); }).then(a => ctx.decodeAudioData(a))
    .then(b => { bufs[file] = b; if (song && TRACKS[song] === file && !track) { clearInterval(timer); timer = null; playTrack(file); } })
    .catch(() => { bufs[file] = false;
      if (file !== 'theme' && file !== 'boss') { Object.keys(TRACKS).forEach(k => { if (TRACKS[k] === file) TRACKS[k] = k === 'boss' ? 'boss' : 'theme'; }); const s = song; song = null; if (s) TT.music(s); return; } // faltou a trilha da fase: volta para a da fase 1
      if (song && TRACKS[song] === file && !timer) { nextT = ctx.currentTime + 0.08; timer = setInterval(schedule, 40); } });
}
// segundos desde o primeiro tempo da trilha do Arraial (descontada a latência da saída de som); null quando ela não está tocando
TT.beatTime = () => (track && track.start != null && ctx) ? Math.max(0, ctx.currentTime - track.start - track.beat0 - (ctx.outputLatency || ctx.baseLatency || 0)) : null;
TT.BPM = LOOPS.arraial.bpm;
TT.music = name => {
  if (name === song) return;
  song = name; step = 0;
  const file = name && TRACKS[name];
  if (ctx && track && track.file !== file) stopTrack();
  clearInterval(timer); timer = null;
  if (!name || !init()) return;
  loadTrack(file);
  if (bufs[file]) { if (!track) playTrack(file); return; }
  // arquivo ainda carregando: espera em silêncio (loadTrack começa a música assim que chegar); a trilha sintetizada só entra se o arquivo falhar
  if (bufs[file] === false) { nextT = ctx.currentTime + 0.08; timer = setInterval(schedule, 40); }
};
TT.setMuted = m => {
  muted = m; try { localStorage.setItem('tintim-mute', m ? '1' : '0'); } catch (_) {}
  if (ctx) master.gain.setTargetAtTime(m ? 0 : VOL, ctx.currentTime, 0.03);
};
TT.isMuted = () => muted;
TT.audioDuck = (on, k = 0.32) => { if (ctx) { musicBus.gain.setTargetAtTime(on ? 0.32 * k : 0.32, ctx.currentTime, 0.1); trackBus.gain.setTargetAtTime(on ? 0.62 * k : 0.62, ctx.currentTime, 0.1); } };
TT.audioInit = init;
TT.audioState = () => ctx ? ctx.state : 'none'; // 'running' quando o navegador já deixa tocar som
})();
