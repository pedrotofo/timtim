// Interface: controles (teclado, toque, gamepad), placar, telas e transições.
(() => {
'use strict';
const TT = window.TT, S = TT.S, C = TT.C, I = TT.input;
const $ = id => document.getElementById(id);
const stage = $('stage');

// ---------------- controles ----------------
const mainBtn = () => ({ title: 'btnStart', pause: 'btnResume', lose: 'btnRetry', win: $('btnNext').classList.contains('on') ? 'btnNext' : 'btnAgain' })[S.mode];
const keyMap = { ArrowLeft: 'left', KeyA: 'left', ArrowRight: 'right', KeyD: 'right', Space: 'jump', ArrowUp: 'jump', KeyW: 'jump', ArrowDown: 'sniff', KeyS: 'sniff' };
const press = (k, on) => { if (k === 'jump' && on && !I.jump) I.jumpPressed = true; I[k] = on; };
addEventListener('keydown', e => {
  if (TT.mapa && TT.mapa.isOpen()) return; // no mapa, as teclas são do mapa (setas andam, Enter joga, Esc volta)
  if (e.code === 'KeyP' || e.code === 'Escape') { S.mode === 'pause' ? TT.resume() : TT.pause(); return; }
  if (e.code === 'KeyM') return toggleMute();
  if (e.code === 'Enter' || e.code === 'Space') {
    const b = mainBtn();
    if ($('shelf').classList.contains('on')) { e.preventDefault(); $('btnShelfBack').click(); return; }
    if (b && $(S.mode).classList.contains('on')) { e.preventDefault(); $(b).click(); return; }
  }
  const k = keyMap[e.code]; if (!k) return; e.preventDefault(); if (!e.repeat) press(k, true);
});
addEventListener('keyup', e => { const k = keyMap[e.code]; if (k) press(k, false); });
addEventListener('blur', () => { I.left = I.right = I.jump = I.sniff = false; TT.pause(); });
document.addEventListener('visibilitychange', () => { if (document.hidden) TT.pause(); });

const isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
$('skip').textContent = isTouch ? 'toque para começar' : 'clique ou Espaço para começar';
if (isTouch) { $('touch').classList.add('on'); $('hint').textContent = '◀ ▶ andar · ▲ pula · no ar, de novo: pirueta · 👃 fareja'; }
document.querySelectorAll('.tbtn').forEach(b => {
  const k = b.dataset.k;
  const set = on => { press(k, on); b.classList.toggle('down', on); };
  b.addEventListener('pointerdown', e => { e.preventDefault(); b.setPointerCapture(e.pointerId); set(true); });
  ['pointerup', 'pointercancel', 'lostpointercapture'].forEach(ev => b.addEventListener(ev, () => set(false)));
  b.addEventListener('contextmenu', e => e.preventDefault());
});
let padPrev = {};
TT.pollPad = () => {
  const gp = navigator.getGamepads && [...navigator.getGamepads()].find(g => g);
  if (!gp) return;
  const ax = gp.axes[0] || 0, b = i => !!(gp.buttons[i] && gp.buttons[i].pressed);
  const now = { left: ax < -0.35 || b(14), right: ax > 0.35 || b(15), jump: b(0) || b(1), sniff: (gp.axes[1] || 0) > 0.6 || b(13) || b(2), start: b(9) };
  for (const k of ['left', 'right', 'jump', 'sniff']) if (now[k] !== !!padPrev[k]) press(k, now[k]);
  const okNow = now.start || b(0);
  if (now.start && !padPrev.start && S.mode === 'play') TT.pause();
  else if (okNow && !padPrev.ok && S.mode !== 'play') { if ($('shelf').classList.contains('on')) $('btnShelfBack').click(); else { const id = mainBtn(); if (id && $(S.mode) && $(S.mode).classList.contains('on')) $(id).click(); } }
  now.ok = okNow;
  padPrev = now;
};

// ---------------- telas ----------------
const screens = ['title', 'pause', 'lose', 'win'];
const show = name => screens.forEach(s => $(s).classList.toggle('on', s === name));
const iris = $('iris');
function irisTo(closed, at) {
  if (at) { iris.style.setProperty('--x', (at.x * 100).toFixed(1) + '%'); iris.style.setProperty('--y', (at.y * 100).toFixed(1) + '%'); }
  iris.classList.toggle('closed', closed);
}
function irisOpenFromBlack() { iris.style.transition = 'none'; irisTo(true, { x: 0.3, y: 0.7 }); void iris.offsetWidth; iris.style.transition = ''; requestAnimationFrame(() => irisTo(false)); }

function begin(fn) { TT.audioInit(); TT.sfx('ui'); irisTo(true, { x: 0.5, y: 0.5 }); setTimeout(() => { fn(); }, 520); }
// card de introdução: antes de cada fase, um quadro pintado (src/intro.js) com zoom lento e a frase escrita no pergaminho.
// Se existir a narração da fase (assets/voice/intro-faseN.mp3), ela toca junto. Um toque (ou Enter/Espaço) começa a fase.
const titleEl = $('title'), STORY = [
  'O Furtão roubou o Macaco Fedido! Ajude Timtim, Zara e Elvis a trazê-lo de volta.',
  'Festa de São João! Mas alguém está assustando as galinhas do arraial.',
  'O corvo do quadro fugiu com o pincel do Van Gogh! Vamos recuperá-lo?'];
const DUR = (TT.intro && TT.intro.durations) || [7, 7, 7];
let storyTimer = null, storyAt = 0, storyI = -1;
// a frase vai desenhada no pergaminho (canvas); #storyLine guarda o mesmo texto para leitores de tela
function storyLine() { const i = (TT.FASE || 1) - 1; clearTimeout(storyTimer); storyI = i; storyAt = performance.now(); if (TT.intro) TT.intro.scene(i, STORY[i]); $('storyLine').textContent = STORY[i]; TT.voice(i); storyTimer = setTimeout(endStory, DUR[i] * 1000); }
function endStory() { if (!titleEl.classList.contains('story') || titleEl.classList.contains('leaving')) return; clearTimeout(storyTimer); TT.voice(-1); titleEl.classList.add('leaving'); begin(TT.start); }
// um toque começa a fase (menos de 0,8 s depois do card aparecer não conta: é o mesmo toque que abriu o card)
TT.storyScene = () => storyI;
const nextStory = () => { if (performance.now() - storyAt > 800) endStory(); };
// ---------------- fases ----------------
// A fase atual vem do endereço (?fase=2). Vencer o Parque libera o Arraial; o progresso fica salvo no navegador.
const FASE = TT.FASE || 1, FASES = ['O Parque', 'O Arraial', 'O Quadro Encantado'];
let done = {}; try { done = JSON.parse(localStorage.getItem('tintim-fases') || '{}') || {}; } catch (_) {}
const goFase = (f, jogar) => { TT.sfx('ui'); irisTo(true, { x: 0.5, y: 0.5 }); setTimeout(() => { const h = (f > 1 ? 'fase' + f : 'fase1') + (jogar ? '-jogar' : '');
  if (location.search) location.href = location.pathname + '#' + h; else { location.hash = h; location.reload(); } }, 480); };
// chegou de "Próxima fase": começa a fase direto, sem a tela inicial
if (/-jogar/.test(location.hash)) { try { history.replaceState(null, '', location.pathname + location.search + '#fase' + FASE); } catch (_) { location.hash = 'fase' + FASE; } // vindo do mapa: a capa nem aparece, entra o card da fase
  titleEl.classList.add('story');
  let auto = false; TT.on('assetsReady', () => { if (auto) return; auto = true; if (S.mode === 'title') historia(); }); }
document.querySelectorAll('#fases .chip').forEach(b => { const f = +b.dataset.f; b.classList.toggle('cur', f === FASE); b.disabled = f > 1 && !done[f - 1];
  b.onclick = () => { if (f !== FASE) goFase(f); }; });
$('fases').classList.remove('on'); // a fase 2 chega sozinha ao vencer o Parque; o título não oferece atalho
if (FASE === 2) $('hint').textContent = isTouch ? '◀ ▶ andar · ▲ pula · segure ▲ no ar: planar · 👃 fareja' : '← → andar · Espaço pula · segure Espaço no ar: planar · ↓ fareja';
if (FASE === 3) $('hint').textContent = isTouch ? '◀ ▶ andar · ▲ pula · no redemoinho, ▲ solta · 👃 fareja' : '← → andar · Espaço pula · no redemoinho, Espaço solta · ↓ fareja';
if (FASE > 1) { $('pauseText').textContent = 'O Timtim parou para comer uma pipoca.'; $('progEnd').textContent = '🎉'; }
// mapa das fases: aparece depois do título (escolher a fase) e entre as fases (o Timtim anda pelo caminho até a seguinte)
const mapaEl = $('mapa');
function abrirMapa(o) { TT.audioInit(); mapaEl.hidden = false; TT.mapa.open(Object.assign({ root: mapaEl, done, minOpen: FASE, onClose: () => TT.mapa.close() }, o)); }
let nextT = 0; $('btnNext').onclick = () => { clearInterval(nextT); const prox = FASE < FASES.length ? FASE + 1 : 0;
  abrirMapa({ at: FASE, walkTo: prox || undefined,
    onArrive: f => { if (f === prox) setTimeout(() => { if (TT.mapa.isOpen() && TT.mapa.state().fase === f) goFase(f, true); }, 1400); }, // chegou na placa da fase nova: ela começa
    onPlay: f => { if (f === FASE) { TT.mapa.close(); begin(TT.start); } else goFase(f, true); } }); };
$('btnAgain').addEventListener('click', () => clearInterval(nextT), true);
let contando = false;
const historia = () => { if (contando) return; contando = true; TT.audioInit(); TT.sfx('ui'); TT.music('title'); titleEl.classList.add('story'); storyLine(); };
// no mapa, o Timtim começa na fase mais nova já liberada (ou na desta página)
const ultima = () => { let n = 1; while (n < FASES.length && done[n]) n++; return Math.max(FASE, n); };
// Jogar abre o mapa; no mapa, a fase desta página mostra o card aqui mesmo e as outras carregam a página delas
$('btnStart').onclick = () => { if (titleEl.classList.contains('story')) return nextStory(); if (TT.mapa.isOpen()) return;
  abrirMapa({ at: ultima(), onPlay: f => { TT.mapa.close(); if (f === FASE) historia(); else goFase(f, true); } }); };
titleEl.addEventListener('pointerdown', () => { if (titleEl.classList.contains('story')) nextStory(); });
const firstTouch = () => { if (S.mode === 'title') { TT.audioInit(); TT.music('title'); } removeEventListener('pointerdown', firstTouch); removeEventListener('keydown', firstTouch); };
addEventListener('pointerdown', firstTouch); addEventListener('keydown', firstTouch);
TT.on('start', () => setTimeout(() => { titleEl.classList.remove('story', 'leaving'); contando = false; if (TT.intro) TT.intro.stop(); }, 600));
// dicas do Arraial, na hora em que cada coisa aparece
const HOLD = isTouch ? 'segure ▲' : 'segure Espaço';
const TUT = { glide: isTouch ? 'Segure ▲ no ar para planar' : 'Segure Espaço no ar para planar', glideEdge: `Pule e ${HOLD} para planar!`,
  glideHold: HOLD[0].toUpperCase() + HOLD.slice(1) + '!', glideRetry: `Quase! Pule e ${HOLD} para planar`, glideOk: 'Isso! O Timtim sabe planar', swirl: isTouch ? '▲ solta do redemoinho' : 'Espaço solta do redemoinho', fire: 'Plane sobre o ar quente' };
TT.on('tutorial', e => { if (TUT[e.kind]) TT.emit('banner', { text: TUT[e.kind], important: true, now: e.kind.startsWith('glide') }); }); // a aula de planar troca a dica no meio do pulo: substitui na hora
// a primeira debandada é anunciada: sem isso, as galinhas atropelavam o jogador sem aviso nenhum
TT.on('stampedeWarn', e => { TT.sfx('henPanic'); if (e.first) TT.emit('banner', { text: 'Galinhas em disparada!', important: true }); });
TT.on('egg', () => TT.emit('banner', { text: 'Planar turbinado!' }));
// cartão de abertura do Arraial (o mesmo cartão da apresentação do chefão, com outro texto)
TT.on('arraialIntro', () => { stage.classList.add('cine'); const c = $('bossCard'); c.classList.add('top'); c.querySelector('small').textContent = 'FASE ' + FASE; c.querySelector('h2').textContent = FASE === 3 ? 'O QUADRO ENCANTADO' : 'O ARRAIAL';
  c.querySelector('p').textContent = FASE === 3 ? 'O Van Gogh precisa da sua ajuda.' : 'Siga as galinhas assustadas até o galinheiro.'; setTimeout(() => c.classList.add('show'), 350); });
// o chefão do Arraial: o lobo-guará
if (FASE === 2) document.querySelector('.bossRow b').textContent = 'Lobo-guará';
if (FASE === 3) document.querySelector('.bossRow b').textContent = 'Corvo-Borrão';
TT.on('foxIntro', () => { stage.classList.add('cine'); const c = $('bossCard'); c.classList.remove('top'); c.querySelector('small').textContent = 'CHEFÃO'; c.querySelector('h2').textContent = FASE === 3 ? 'O CORVO-BORRÃO' : 'O LOBO-GUARÁ';
  c.querySelector('p').textContent = FASE === 3 ? 'fugiu com o pincel favorito do Van Gogh' : 'invadiu o galinheiro do arraial'; setTimeout(() => c.classList.add('show'), 600); });
// a estratégia, contada pela Zara e pelo Elvis no começo da luta
const tipT = [];
TT.on('cineEnd', e => { if (e.type !== 'fox') return;
  const fala = (i, line) => { const f = S.friends[i]; if (f && S.mode === 'play') TT.emit('friend', { x: f.x, y: C.GROUND - 70, kind: f.kind, line }); };
  const ok = () => S.mode === 'play' && S.arena;
  if (FASE === 3) { tipT.push(setTimeout(() => { if (ok()) fala(1, 'Cuidado com os tubos de tinta!'); }, 300)); return; }
  tipT.push(setTimeout(() => { if (ok()) fala(1, 'Sobe no ar quente da fogueira!'); }, 300));
  tipT.push(setTimeout(() => { if (ok()) fala(0, 'E cai planando na crina dele!'); }, 3300)); });
// o Corvo-Borrão: a hora de atacar é quando ele desce e fica bicando o chão
TT.on('crowPeck', e => { if (!e.first) return; const f = S.friends[0]; if (f) TT.emit('friend', { x: f.x, y: C.GROUND - 70, kind: f.kind, line: 'Desceu! Pula nas costas dele!' }); });
TT.on('vgIntro', () => stage.classList.add('cine'));
TT.on('start', () => { tipT.forEach(clearTimeout); tipT.length = 0; }); TT.on('lose', () => { tipT.forEach(clearTimeout); tipT.length = 0; });
TT.on('foxRoar', e => { if (e.first) TT.emit('banner', { text: FASE === 3 ? 'O grasnado desliga os redemoinhos!' : 'O latido apaga o ar quente!' }); });
TT.on('fruitLand', e => { if (e.first) TT.emit('banner', { text: 'Fruta-do-lobo!' }); });
TT.on('henRevenge', () => setTimeout(() => TT.emit('banner', { text: 'As galinhas expulsaram o lobo-guará!' }), 500));
let dodgeTip = false; TT.on('foxDodge', () => { if (dodgeTip) return; dodgeTip = true; TT.emit('banner', { text: 'Pulo comum não basta: plane!', important: true }); });
TT.on('start', e => { if (!e.retry) dodgeTip = false; });
// correio elegante: o bilhete abre na tela com a piada
let noteT = 0; TT.on('note', e => { const n = $('note'); n.querySelector('small').textContent = `${FASE === 3 ? 'Carta ao Theo' : 'Correio elegante'} ${e.n}/${e.total}`; n.querySelector('p').textContent = e.text;
  n.classList.remove('on'); void n.offsetWidth; n.classList.add('on'); clearTimeout(noteT); noteT = setTimeout(() => n.classList.remove('on'), 4800); });
TT.on('start', () => { clearTimeout(noteT); $('note').classList.remove('on'); });
$('btnAgain').onclick = () => begin(TT.start);
$('btnRestart').onclick = () => begin(TT.start);
$('btnLoseRestart').onclick = () => begin(TT.start);
$('btnRetry').onclick = () => begin(TT.retry);
$('btnResume').onclick = () => TT.resume();
// opção de acessibilidade: a tela treme bem menos e os clarões ficam fracos (para quem se incomoda com isso); fica salva
try { TT.calmo = localStorage.getItem('tintim-calmo') === '1'; } catch (_) { TT.calmo = false; }
const showCalmo = () => { $('btnCalmo').textContent = 'Menos tremor e clarão: ' + (TT.calmo ? 'sim' : 'não'); $('btnCalmo').setAttribute('aria-pressed', TT.calmo ? 'true' : 'false'); };
$('btnCalmo').onclick = () => { TT.calmo = !TT.calmo; try { localStorage.setItem('tintim-calmo', TT.calmo ? '1' : '0'); } catch (_) {} TT.sfx('ui'); showCalmo(); }; showCalmo();
$('btnPause').onclick = () => TT.pause();
const toggleMute = () => { TT.setMuted(!TT.isMuted()); $('btnMute').classList.toggle('muted', TT.isMuted()); };
$('btnMute').onclick = toggleMute; $('btnMute').classList.toggle('muted', TT.isMuted());

// ---------------- estante de brinquedos perdidos ----------------
// Em cima, o presente que cada aventura dá ao vencer (fica salvo junto com as fases vencidas).
// Embaixo, os escondidos: um por fase, achados com o faro; são brinquedos que o Furtão roubou de outros cães da vila.
const PREMIOS = [
  { fase: 1, nome: 'O Parque', name: 'Macaco Fedido', img: 'assets/sprites/monkey-joy.png', joke: 'De volta para casa! Continua fedido, e mais amado do que nunca.' },
  { fase: 2, nome: 'O Arraial', name: 'Chinela Amarela', img: 'assets/sprites/premio-chinela.png', joke: 'Presente das galinhas do arraial: amarela como milho de São João, e boa de morder.' },
  { fase: 3, nome: 'O Quadro Encantado', name: 'Bolinha Mordedora', img: 'assets/sprites/premio-bolinha.png', joke: 'Presente do Van Gogh: roxa de um lado, verde do outro. "As cores que faltavam no meu quadro."' },
  { nome: 'O Quintal da Vizinha' }, { nome: 'O Covil do Furtão' }];
const TOYS = [
  { id: 'patinho', fase: 'O Parque', name: 'Patinho Quá-Quá', joke: 'É do Pipoca, o salsicha da padaria. O Furtão levou porque ele faz "quá" toda vez que é mordido.' },
  { id: 'sanfoninha', fase: 'O Arraial', name: 'Sanfoninha', joke: 'É do Bolota, o vira-lata do sanfoneiro. Cada vez que o Furtão apertava, ela tocava um forró desafinado.' },
  { id: 'girassol', fase: 'O Quadro Encantado', name: 'Girassol de Apito', joke: 'É da Tinta, a cachorrinha da pintora. Apita toda vez que alguém aperta, e o Furtão não parava de apertar.' },
  { fase: 'O Quintal da Vizinha' }, { fase: 'O Covil do Furtão' }];
const TOY_IMG = { patinho: 'assets/sprites/toy-duck.png', sanfoninha: 'assets/sprites/toy-sanfona.png', girassol: 'assets/sprites/toy-girassol.png' };
let found = {};
try { found = JSON.parse(localStorage.getItem('tintim-toys') || '{}') || {}; } catch (_) {}
function drawShelf() {
  $('premioSlots').innerHTML = PREMIOS.map(t => { const got = t.fase && done[t.fase], soon = !t.fase;
    const img = t.img ? `<img src="${t.img}" alt="">` : '<b>?</b>';
    return `<div class="slot${got ? ' got' : ''}${soon ? ' soon' : ''}"><div class="pic">${img}</div><small>${t.nome}</small>` +
      `<strong>${got ? t.name : soon ? 'Em breve' : 'Vença a fase'}</strong>${got ? `<p>${t.joke}</p>` : ''}</div>`; }).join('');
  $('shelfSlots').innerHTML = TOYS.map(t => { const got = t.id && found[t.id], soon = !t.id;
    const img = TOY_IMG[t.id] ? `<img src="${TOY_IMG[t.id]}" alt="">` : '<b>?</b>';
    return `<div class="slot${got ? ' got' : ''}${soon ? ' soon' : ''}"><div class="pic">${img}</div><small>${t.fase}</small>` +
      `<strong>${got ? t.name : soon ? 'Em breve' : 'Ainda perdido'}</strong>${got ? `<p>${t.joke}</p>` : t.id ? `<p>Dica: o faro (${isTouch ? '👃' : '↓'}) mostra o caminho.</p>` : ''}</div>`; }).join('');
  $('shelfCount').textContent = `${PREMIOS.filter(t => t.fase && done[t.fase]).length} de ${PREMIOS.filter(t => t.fase).length} presentes · ${TOYS.filter(t => t.id && found[t.id]).length} de ${TOYS.filter(t => t.id).length} escondidos achados`;
}
$('btnShelf').onclick = () => { TT.audioInit(); TT.sfx('ui'); drawShelf(); $('shelf').classList.add('on'); };
$('btnShelfBack').onclick = () => { TT.sfx('ui'); $('shelf').classList.remove('on'); };
TT.on('toy', e => { found[e.id] = true; try { localStorage.setItem('tintim-toys', JSON.stringify(found)); } catch (_) {} });
// dica do faro: aparece quando o controle é liberado, enquanto o brinquedo da fase não tiver sido achado
TT.on('cineEnd', e => { if (e.type === 'steal' && !found.patinho) setTimeout(() => { if (S.mode === 'play') TT.emit('banner', { text: isTouch ? 'Segure 👃 para farejar' : 'Segure ↓ para farejar' }); }, 400); });

let best = null;
const BEST_KEY = FASE > 1 ? 'tintim-best-' + FASE : 'tintim-best';
try { best = JSON.parse(localStorage.getItem(BEST_KEY) || 'null'); } catch (_) {}
const showBest = () => { $('best').textContent = best ? `Seu recorde: ${'★'.repeat(best.stars)}${'☆'.repeat(3 - best.stars)} em ${best.time.toFixed(1)}s` : ''; };
showBest();

// ---------------- placar ----------------
const hearts = [...document.querySelectorAll('.heart')], segs = [...document.querySelectorAll('.bossRow')].map(r => [...r.querySelectorAll('.seg')]);
const last = {};
const setIf = (key, val, fn) => { if (last[key] !== val) { last[key] = val; fn(val); } };
TT.uiFrame = () => {
  const p = S.player;
  setIf('hp', p.hp, v => hearts.forEach((h, i) => h.classList.toggle('off', i >= v)));
  setIf('ck', S.cookies, v => { const n = $('cookieN'); n.textContent = v; n.classList.remove('bump'); void n.offsetWidth; n.classList.add('bump'); });
  setIf('boss', S.arena, v => $('hr').classList.toggle('boss', v));
  if (!S.arena) setIf('prog', Math.round(Math.min(1, p.x / C.GOAL_X) * 200) / 2, v => { $('progFill').style.width = v + '%'; $('progDog').style.left = v + '%'; });
  else setIf('bossHp', C.FOX ? S.fox.hp : S.boss.hp, v => segs[0].forEach((s, k) => s.classList.toggle('off', k >= v)));
};

const banner = $('banner');
let bannerUntil = 0, bannerQ = null;
const noteOpen = () => $('note').classList.contains('on'), textBusy = () => performance.now() < bannerUntil || noteOpen();
const showBanner = e => { banner.textContent = e.text; banner.classList.remove('show'); void banner.offsetWidth; banner.classList.add('show'); bannerUntil = performance.now() + 2700; };
TT.on('banner', e => { if (textBusy() && !e.now) { if (e.important) bannerQ = e; return; } showBanner(e); });
setInterval(() => { if (bannerQ && !textBusy() && S.mode === 'play') { const q = bannerQ; bannerQ = null; showBanner(q); } }, 250);
TT.on('start', () => { bannerQ = null; bannerUntil = 0; });
TT.on('hurt', () => { const h = hearts[Math.max(0, S.player.hp)]; if (h) { h.classList.remove('hit'); void h.offsetWidth; h.classList.add('hit'); } });
TT.on('start', () => { show(null); $('hud').classList.add('on'); stage.classList.remove('cine'); $('bossCard').classList.remove('show'); $('cookieT').textContent = '/' + S.totalCookies; irisOpenFromBlack(); });
// balão dos amigos
const say = $('say'), LINES = TT.FASE === 3 ? ['Toma tinta amarela, Timtim! Dá força pra planar!', 'Mais um tubo: agora nada te machuca!'] : TT.FASE === 2 ? ['Toma um ovo cozido, Timtim! Dá força pra planar!', 'Mais um ovinho: agora nada te machuca!'] : ['Toma um turbo, Timtim!', 'Fica invencível, Timtim!']; let sayF = null, sayEnd = 0;
TT.on('friend', e => { if (noteOpen() && !S.arena) return; sayF = S.friends.reduce((a, f) => Math.abs(f.x - e.x) < Math.abs(a.x - e.x) ? f : a); say.textContent = e.line || LINES[S.friends.indexOf(sayF) % 2]; sayEnd = performance.now() + 2600; say.classList.remove('long'); say.classList.add('on'); });
// o Van Gogh fala no mesmo balão, mais alto (ele é bem maior que os cachorros) e com a fala quebrada em linhas
TT.on('vgSay', e => { if (!S.vg) return; sayF = S.vg; say.textContent = e.line; sayEnd = performance.now() + (e.dur || 3.4) * 1000; say.classList.add('long', 'on'); });
const uiFrame0 = TT.uiFrame;
TT.uiFrame = () => { uiFrame0(); if (!sayF) return;
  if (performance.now() > sayEnd || S.mode === 'lose') { say.classList.remove('on'); sayF = null; return; }
  const at = TT.R.toScreen(sayF.x, C.GROUND - (sayF === S.vg ? 232 : 118)), half = say.offsetWidth / 2 / Math.max(1, stage.clientWidth) + 0.01; // o balão nunca sai da tela
  say.style.left = (Math.max(half, Math.min(1 - half, at.x)) * 100).toFixed(2) + '%'; say.style.top = (Math.max(0.12, at.y) * 100).toFixed(2) + '%'; };
TT.on('pause', () => show('pause'));
TT.on('resume', () => show(null));
TT.on('stealIntro', () => stage.classList.add('cine'));
TT.on('bossIntro', () => { stage.classList.add('cine'); setTimeout(() => $('bossCard').classList.add('show'), 650); });
TT.on('cineEnd', () => { stage.classList.remove('cine'); $('bossCard').classList.remove('show'); });
TT.on('lose', () => {
  $('loseText').textContent = FASE === 3 && S.arena ? 'Fuja das marcas vermelhas no chão e, quando o corvo descer para bicar, pule nas costas dele.' : S.checkpoint >= 0 ? 'Você volta do último checkpoint com os corações cheios.' : FASE === 3 ? 'Cuidado com os buracos: entre no redemoinho e aperte o pulo para se soltar na direção certa.' : FASE === 2 ? 'Cuidado com os buracos: segure o pulo no ar para planar, e use o ar quente das fogueiras para subir.' : 'Cuidado com os buracos e pise nos pombos por cima.';
  setTimeout(() => { if (S.mode === 'lose') show('lose'); }, 1100);
});
TT.on('win', st => {
  if (!best || st.stars > best.stars || (st.stars === best.stars && st.time < best.time)) { best = { stars: st.stars, time: st.time }; try { localStorage.setItem(BEST_KEY, JSON.stringify(best)); } catch (_) {} }
  done[FASE] = true; try { localStorage.setItem('tintim-fases', JSON.stringify(done)); } catch (_) {}
  $('btnNext').classList.add('on'); if (FASE >= FASES.length) $('btnNext').textContent = 'Ver o mapa'; // na última fase pronta, o botão leva ao mapa (com as próximas em breve)
  if (FASE < FASES.length) { let n = 8; const lab = 'Próxima fase: ' + FASES[FASE]; $('btnNext').textContent = `${lab} (${n})`; clearInterval(nextT);
    setTimeout(() => { if (S.mode !== 'win') return; clearInterval(nextT); nextT = setInterval(() => { n--; $('btnNext').textContent = `${lab} (${n})`; if (n <= 0) { clearInterval(nextT); $('btnNext').click(); } }, 1000); }, 1900); }
  if (FASE === 3) { document.querySelector('.winMonkey').src = 'assets/sprites/premio-bolinha.png'; $('winTitle').textContent = 'O pincel voltou!'; $('winText').textContent = 'Timtim pulou nas costas do Corvo-Borrão e devolveu o pincel do Van Gogh. De presente, ganhou uma bolinha mordedora colorida, roxa e verde!'; $('stMain').textContent = 'Pincel de volta';
    document.querySelector('.winMonkey').style.width = '8cqw'; $('stNotes').lastChild.textContent = 'Cartas ao Theo';
    $('stNotes').style.display = ''; $('stNotes').firstElementChild.textContent = `${st.notes}/${st.notesTotal}`; $('stNotes').classList.toggle('ok', st.notes >= st.notesTotal); }
  else if (FASE === 2) { document.querySelector('.winMonkey').src = 'assets/sprites/premio-chinela.png'; document.querySelector('.winMonkey').style.width = '8.5cqw'; $('winTitle').textContent = 'Galinheiro salvo!'; $('winText').textContent = 'As galinhas expulsaram o lobo-guará para a mata e, de presente, deram ao Timtim uma chinela amarela mordedora!'; $('stMain').textContent = 'Galinheiro salvo';
    $('stNotes').style.display = ''; $('stNotes').firstElementChild.textContent = `${st.notes}/${st.notesTotal}`; $('stNotes').classList.toggle('ok', st.notes >= st.notesTotal); }
  showBest();
  $('stCookies').firstElementChild.textContent = `${st.cookies}/${st.total}`; $('stCookies').classList.toggle('ok', st.allCookies);
  $('stHearts').firstElementChild.textContent = st.gold + '/3'; $('stHearts').classList.toggle('ok', st.allGold);
  $('stTime').firstElementChild.textContent = st.time.toFixed(1) + 's';
  $('stToy').firstElementChild.textContent = st.toy ? '✓' : '?'; $('stToy').classList.toggle('ok', st.toy);
  const stars = [...document.querySelectorAll('.star')]; stars.forEach(s => s.classList.remove('got'));
  const p = S.player, at = TT.R && TT.R.toScreen ? TT.R.toScreen(p.x + p.w / 2, p.y + 10) : { x: 0.5, y: 0.6 };
  setTimeout(() => irisTo(true, at), 900);
  setTimeout(() => { if (S.mode !== 'win') return; show('win'); $('hud').classList.remove('on'); irisTo(false);
    // estrelas na ordem: vencer, biscoitos, os três dourados
    [true, st.allCookies, st.allGold].forEach((ok, i) => { if (ok) setTimeout(() => { stars[i].style.animationDelay = '0s'; stars[i].classList.add('got'); TT.sfx('star'); }, 500 + i * 380); });
  }, 1900);
});
TT.on('assetsReady', () => $('msg').classList.add('hide'));
if (TT.noWebGL) $('msgTxt').textContent = 'Este navegador não conseguiu ligar o modo 3D (WebGL). Tente no Chrome ou Safari atualizados.';
})();
