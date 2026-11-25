// Grava tomadas do jogo em TEMPO REAL (relógio pausado, 1/30 s por quadro). Uso: node gravar.js f3|mapa  → clips/<tomada>/NNN.jpg
const { chromium } = require('playwright');
const fs = require('fs');
const which = process.argv[2], OUT = __dirname + '/clips', DBG = !!process.env.DBG;
(async () => {
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const pg = await b.newPage({ viewport: { width: 1280, height: 720 } });
  pg.on('pageerror', e => console.log('ERR', e.message));
  await pg.clock.install({ time: new Date('2026-11-25T12:00:00') });
  await pg.addInitScript(() => { try { localStorage.setItem('tintim-fases', JSON.stringify({ 1: true, 2: true, 3: true })); } catch (_) {} });
  await pg.addInitScript(() => { const r = window.requestAnimationFrame; window.requestAnimationFrame = cb => r(() => cb(performance.now())); });
  const ev = (f, a) => pg.evaluate(f, a);
  const ff = async (c, m = 60000, each) => { for (let t = 0; t < m; t += 100) { if (await ev(c)) return true; if (each) await each(t); await pg.clock.runFor(100); await pg.waitForTimeout(3); } console.log('timeout', c.toString()); return false; };
  const keep = () => ev(() => { TT.demo.noHurt = true; const p = __tintim.player; if (p) { p.inv = 0; p.hp = 3; p.slow = 0; } if (__tintim.S.tut) __tintim.S.tut.learned = true; });
  const k = pg.keyboard;
  const rec = async (name, n, each) => { const d = `${OUT}/${name}`; if (!DBG) { fs.rmSync(d, { recursive: true, force: true }); fs.mkdirSync(d, { recursive: true }); } const t0 = Date.now();
    for (let f = 0; f < n; f++) { if (each) await each(f); if (which !== 'mapa') await keep(); await pg.clock.runFor(1000 / 30);
      if (DBG) { if (f % 10 === 0) console.log(name, f, JSON.stringify(await ev(() => { const p = __tintim.player; return [Math.round(p.x), Math.round(p.y), p.onGround]; }))); }
      else await pg.screenshot({ path: `${d}/${String(f).padStart(3, '0')}.jpg`, quality: 92 }); }
    console.log(name, n, 'quadros', ((Date.now() - t0) / 1000).toFixed(0) + 's'); };
  await pg.goto('http://localhost:8765/?q=2' + (which === 'f3' ? '&fase=3' : ''));
  await ff(() => window.__tintim && __tintim.R.ready && __tintim.state === 'title');
  await ev(() => { const st = document.createElement('style'); st.textContent = '#banner,#win,#iris{display:none!important}'; document.head.appendChild(st); const n = document.getElementById('btnNext'); if (n) n.onclick = () => {}; });
  { const now = await ev(() => Date.now()); await pg.clock.pauseAt(new Date(now + 200)); }
  await pg.clock.runFor(700); await pg.click('#btnStart');
  await ff(() => TT.mapa.isOpen() && !!document.querySelector('#mapa canvas'), 8000);
  if (which === 'mapa') { await pg.clock.runFor(1200); await rec('mapa', 150); await b.close(); return; }
  await pg.clock.runFor(500); await k.press('Enter');
  await ff(() => __tintim.storyScene === 2, 8000); await pg.clock.runFor(1000); await k.press('Space');
  // cartão da fase e as falas do Van Gogh: o pulo adianta
  await ff(() => __tintim.state === 'play' && !__tintim.S.cine, 60000, async t => { if (t % 700 === 0) await k.press('Space'); });
  await keep(); console.log('jogando');
  // tomada do aparelho: o terraço do café na noite estrelada, quicando nos toldos
  await ev(() => Object.assign(__tintim.player, { x: 4930, y: 300, vx: 0, vy: 0 }));
  await ff(() => __tintim.player.onGround, 5000); await pg.clock.runFor(400);
  let solta = -1;
  await rec('toldos', 150, async f => {
    if (f === 0) await k.down('ArrowRight');
    const st = await ev(() => ({ g: __tintim.player.onGround, x: __tintim.player.x }));
    if (solta < 0 && st.g && f > 4) { await k.down('Space'); solta = f + 10; }
    if (solta >= 0 && f >= solta) { await k.up('Space'); solta = -1; }
    if (st.x > 5800) await k.up('ArrowRight');
  });
  await k.up('ArrowRight'); await k.up('Space');
  // fundo: os girassóis que sobem e descem
  await ev(() => Object.assign(__tintim.player, { x: 1520, y: 300, vx: 0, vy: 0, orbit: null, swirlCd: 1, launchT: 0 }));
  await ff(() => __tintim.player.onGround, 5000); await pg.clock.runFor(400); solta = -1;
  await rec('girassois', 180, async f => {
    if (f === 0) await k.down('ArrowRight');
    const st = await ev(() => ({ g: __tintim.player.onGround }));
    if (solta < 0 && st.g && f % 24 === 6) { await k.down('Space'); solta = f + 12; }
    if (solta >= 0 && f >= solta) { await k.up('Space'); solta = -1; }
  });
  await k.up('ArrowRight'); await k.up('Space');
  // a luta com o Corvo-Borrão
  const AX = await ev(() => TT.C.ARENA_X);
  await ev(x => Object.assign(__tintim.player, { x: x + 200, y: 402, vx: 0, vy: 0, onGround: true, orbit: null, swirlCd: 1, launchT: 0 }), AX);
  await ff(() => __tintim.S.arena && !__tintim.S.cine, 60000, async t => { if (t % 700 === 0) await k.press('Space'); }); await keep();
  await pg.clock.runFor(600);
  await rec('corvo', 180, async f => { const t = f % 60;
    if (t === 3) await k.down('ArrowRight'); if (t === 22) await k.up('ArrowRight'); if (t === 8) await k.down('Space'); if (t === 26) await k.up('Space');
    if (t === 33) await k.down('ArrowLeft'); if (t === 52) await k.up('ArrowLeft'); if (t === 38) await k.down('Space'); if (t === 56) await k.up('Space'); });
  await b.close();
})();
