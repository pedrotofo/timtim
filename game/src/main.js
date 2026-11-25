// Laço principal, trilha/efeitos ligados aos eventos, e qualidade adaptativa.
(() => {
'use strict';
const TT = window.TT, S = TT.S, R = TT.R;

const sfxOn = (ev, name) => TT.on(ev, () => TT.sfx(name));
sfxOn('sniff', 'sniff'); sfxOn('reveal', 'reveal'); sfxOn('toy', 'toy'); sfxOn('jump', 'jump'); sfxOn('jump2', 'jump2'); TT.on('friend', e => TT.sfx(e.kind === 'chi-br' ? 'yapZara' : 'yapElvis')); sfxOn('gift', 'gift'); sfxOn('land', 'land'); sfxOn('cookie', 'cookie'); sfxOn('power', 'power'); TT.on('stomp', e => { TT.sfx('thud'); TT.sfx(e.boss ? 'stomp' : 'pigeon'); }); sfxOn('hurt', 'hurt');
sfxOn('bark', 'bossWoof'); sfxOn('bigBark', 'bigBark'); sfxOn('bonk', 'bonk'); sfxOn('pound', 'pound'); TT.on('throw', e => { TT.sfx('throwBall'); TT.sfx(e.kind === 'chi-br' ? 'yapZara' : 'yapElvis'); }); sfxOn('chew', 'squeak'); sfxOn('shrug', 'boing'); sfxOn('choco', 'choco'); sfxOn('checkpoint', 'checkpoint'); sfxOn('bossIntro', 'boss'); sfxOn('finalBlow', 'final'); sfxOn('laugh', 'laugh'); sfxOn('goal', 'final'); { let gAt = 0; TT.on('glide', () => { const n = performance.now(); if (n - gAt > 600) TT.sfx('glide'); gAt = n; }); } sfxOn('monkeyFree', 'squeak'); sfxOn('monkeyLand', 'gift');
// Arraial: raposa, galinhas assustadas e as brincadeiras
sfxOn('foxIntro', 'boss'); sfxOn('foxRoar', 'bigBark'); sfxOn('foxEat', 'squeak'); sfxOn('fruitLand', 'land'); sfxOn('henRevenge', 'henCoop'); sfxOn('foxPounce', 'jump2'); sfxOn('foxDodge', 'boing'); { let ck = 0; TT.on('cluck', () => TT.sfx(++ck % 2 ? 'cluck1' : 'cluck2')); } sfxOn('splash', 'gift'); sfxOn('hoop', 'star'); sfxOn('note', 'ui'); sfxOn('foxDash', 'bossWoof'); sfxOn('foxSniff', 'squeak'); sfxOn('bossJump', 'jump2'); sfxOn('gold', 'star'); sfxOn('henBounce', 'henFlap'); sfxOn('henJump', 'henFlap');
// fase 3: o Corvo-Borrão (bater de asas, tubo caindo, tinta espirrando, bicadas) e o Van Gogh comemorando
sfxOn('crowFly', 'henFlap'); sfxOn('crowDrop', 'throwBall'); sfxOn('tubeSplat', 'choco'); sfxOn('crowPeck', 'pound'); sfxOn('crowRed', 'pound'); sfxOn('brushLand', 'land'); sfxOn('vgHappy', 'gift');
TT.on('start', () => { TT.music(S.arena ? 'boss' : 'level'); TT.audioDuck(false); });
TT.on('bossIntro', () => TT.music(null)); TT.on('foxIntro', () => TT.music(null));
TT.on('cineEnd', e => { if (e.type === 'boss' || e.type === 'fox') TT.music('boss'); });
TT.on('rematch', () => TT.music('boss'));
TT.on('finalBlow', () => TT.music(null));
TT.on('win', () => TT.sfx('win'));
TT.on('lose', () => { TT.music(null); TT.sfx('lose'); });
TT.on('pause', () => TT.audioDuck(true)); TT.on('resume', () => TT.audioDuck(false));


if (TT.noWebGL || !R || !R.frame) return;
const qp = new URLSearchParams(location.search).get('q'); // ?q=0..2 fixa a qualidade (para testes)
if (qp !== null) R.setQuality(+qp);
let last = performance.now(), acc = 0, n = 0, warm = 0, step = 0;
const STEP = 1 / 240;
TT.on('start', () => { warm = 2; acc = 0; n = 0; });
function loop(now) {
  const raw = (now - last) / 1000, dt = Math.min(0.033, raw); last = now;
  TT.pollPad();
  // as regras andam em passos fixos de 1/240 s: o pulo sai com a mesma altura em qualquer computador e em qualquer tela
  // (antes o passo era o tempo do quadro e o pulo ia de 149 px a 30 quadros por segundo a 161 px a 144)
  step += dt; let k = 0;
  while (step >= STEP && k < 10) { TT.update(STEP); step -= STEP; k++; }
  R.frame(dt);
  TT.uiFrame();
  // qualidade adaptativa: abaixo de ~45 quadros por segundo, simplifica (sem desfoque → sem sombras/pós)
  warm -= raw;
  if (qp === null && warm < 0 && S.mode === 'play' && raw < 0.5) { acc += raw; n++; if (acc > 2.5) { if (n / acc < 45 && R.quality > 0) R.setQuality(R.quality - 1); acc = 0; n = 0; } }
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);
window.__tintim = { get state() { return S.mode; }, get player() { return S.player; }, get boss() { return S.boss; }, get storyScene() { return TT.storyScene ? TT.storyScene() : -1; }, S, R };
})();
