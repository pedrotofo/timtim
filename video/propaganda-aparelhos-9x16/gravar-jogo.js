// Grava tomadas longas do jogo em TEMPO REAL: o relógio do navegador fica pausado e avança 1/30 s por quadro gravado.
// Uso: (cd game && python3 -m http.server 8765 &) ; node gravar.js f1|f2   → clips/<tomada>/NNN.jpg
const { chromium } = require('playwright');
const fs = require('fs');
const which = process.argv[2], OUT = __dirname + '/clips';
(async () => {
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const pg = await b.newPage({ viewport: { width: 1280, height: 720 } });
  pg.on('pageerror', e => console.log('ERR', e.message));
  await pg.clock.install({ time: new Date('2026-11-25T12:00:00') });
  // o laço do jogo mede o tempo pelo argumento do requestAnimationFrame: passa a ser o performance.now() do relógio falso
  await pg.addInitScript(() => { const r = window.requestAnimationFrame; window.requestAnimationFrame = cb => r(() => cb(performance.now())); });
  const ev = (f, a) => pg.evaluate(f, a);
  const ff = async (c, m = 60000) => { for (let t = 0; t < m; t += 100) { if (await ev(c)) return true; await pg.clock.runFor(100); await pg.waitForTimeout(3); } console.log('timeout', c.toString()); return false; };
  const keep = () => ev(() => { TT.demo.noHurt = true; const p = __tintim.player; if (p) { p.inv = 0; p.hp = 3; p.slow = 0; } if (__tintim.S.tut) __tintim.S.tut.learned = true; });
  const k = pg.keyboard;
  const rec = async (name, n, each) => { const d = `${OUT}/${name}`; fs.rmSync(d, { recursive: true, force: true }); fs.mkdirSync(d, { recursive: true }); const t0 = Date.now();
    for (let f = 0; f < n; f++) { if (each) await each(f); await keep(); await pg.clock.runFor(1000 / 30); await pg.screenshot({ path: `${d}/${String(f).padStart(3, '0')}.jpg`, quality: 92 }); }
    console.log(name, n, 'quadros', ((Date.now() - t0) / 1000).toFixed(0) + 's'); };
  await pg.goto('http://localhost:8765/?q=2' + (which === 'f2' ? '#fase2' : ''));
  await ff(() => window.__tintim && __tintim.R.ready && __tintim.state === 'title');
  // só para a gravação: sem faixas de dica, sem tela de vitória e sem pular sozinho para a fase seguinte
  await ev(() => { const st = document.createElement('style'); st.textContent = '#banner,#win{display:none!important}'; document.head.appendChild(st); document.getElementById('btnNext').onclick = () => {}; });
  { const now = await ev(() => Date.now()); await pg.clock.pauseAt(new Date(now + 200)); }
  await pg.clock.runFor(600); await pg.click('#btnStart');
  if (which === 'f1') {
    for (let s = 0; s < 3; s++) { await pg.clock.runFor(900); await pg.mouse.click(640, 360); }
    await ff(() => __tintim.state === 'play' && !!__tintim.S.thief && __tintim.S.cine);
    // tomada 1: o roubo e a corrida atrás do Furtão, com pulo duplo
    let free = -1, jumps = 0;
    await rec('parque', 210, async f => {
      const st = await ev(() => ({ cine: !!__tintim.S.cine, g: __tintim.player.onGround, vy: __tintim.player.vy }));
      if (free < 0 && !st.cine) { free = f; await k.down('ArrowRight'); }
      if (free >= 0) { const t = f - free;
        if (t === 14 || t === 62) await k.down('Space'); if (t === 22 || t === 70) await k.up('Space');
        if (t === 30 || t === 78) await k.down('Space'); if (t === 38 || t === 86) await k.up('Space'); }
    });
    await k.up('ArrowRight'); await k.up('Space');
    // tomada 3: o último golpe no Furtão e a comemoração com o macaco
    await ev(() => { const p = __tintim.player; p.x = 9400; p.y = 300; });
    await k.down('ArrowRight'); await ff(() => __tintim.S.cine && __tintim.S.cine.type === 'boss'); await k.up('ArrowRight');
    await ff(() => !__tintim.S.cine && __tintim.S.arena); await keep();
    await ev(() => { __tintim.boss.hp = 1; });
    await ff(() => __tintim.boss.state === 'chew'); await keep();
    await rec('resgate', 210, async f => { if (f === 0) await ev(() => { const b = __tintim.boss, p = __tintim.player; Object.assign(p, { x: b.x + b.w / 2 - p.w / 2, y: b.y - 230, vy: 0, vx: 0, onGround: false }); }); });
  } else {
    await ff(() => __tintim.state === 'play' && !__tintim.S.cine); await keep();
    // tomada 2: corre, plana sobre o primeiro vão, corre, plana sobre o segundo
    await ev(() => { Object.assign(__tintim.player, { x: 820, y: 300, vx: 0, vy: 0 }); });
    await ff(() => __tintim.player.onGround); await pg.clock.runFor(500);
    let holding = false, left = false;
    await rec('arraial', 210, async f => {
      const st = await ev(() => ({ x: __tintim.player.x, g: __tintim.player.onGround }));
      if (f === 0) await k.down('ArrowRight');
      const edge = (st.x > 1085 && st.x < 1200) || (st.x > 2300 && st.x < 2420);
      if (!holding && st.g && edge) { await k.down('Space'); holding = true; left = false; }
      if (holding && !st.g) left = true;
      if (holding && left && st.g) { await k.up('Space'); holding = false; }
    });
    await k.up('ArrowRight'); await k.up('Space');
    // tomada 4 (fundo): a luta com o lobo-guará
    const AX = await ev(() => TT.C.ARENA_X);
    await ev(x => { Object.assign(__tintim.player, { x: x - 300, y: 300, vx: 0, vy: 0 }); }, AX);
    await k.down('ArrowRight'); await ff(() => __tintim.S.arena && !__tintim.S.cine); await k.up('ArrowRight'); await keep();
    await pg.clock.runFor(800);
    await rec('lobo', 240, async f => { const t = f % 80;
      if (t === 5) await k.down('ArrowRight'); if (t === 25) await k.up('ArrowRight'); if (t === 10) await k.down('Space'); if (t === 34) await k.up('Space');
      if (t === 45) await k.down('ArrowLeft'); if (t === 65) await k.up('ArrowLeft'); if (t === 50) await k.down('Space'); if (t === 70) await k.up('Space'); });
  }
  await b.close();
})();
