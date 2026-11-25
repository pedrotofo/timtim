// Grava os trechos do jogo para a propaganda, quadro a quadro com relógio virtual.
// Uso: (cd game && python3 -m http.server 8765 &) ; node video/propaganda-9x16/gravar-jogo.js f1|f1v|f2   → clips/<tomada>/NNN.jpg
// Grava trechos do jogo quadro a quadro (relógio virtual) em clips/<nome>/NNN.jpg
const { chromium } = require('playwright');
const fs = require('fs');
const which = process.argv[2]; // 'f1' ou 'f2'
const OUT = __dirname + '/clips';
(async () => {
  const b = await chromium.launch({ args: ['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'] });
  const pg = await b.newPage({ viewport: { width: 1280, height: 720 } });
  pg.on('pageerror', e => console.log('ERR', e.message));
  const ev = (f, a) => pg.evaluate(f, a);
  const ff = async (cond, maxMs = 30000, step = 100) => { for (let t = 0; t < maxMs; t += step) { if (await ev(cond)) return true; await pg.clock.runFor(step); await pg.waitForTimeout(5); } console.log('timeout', cond.toString()); return false; };
  const keep = () => ev(() => { TT.demo.noHurt = true; const p = __tintim.player; if (p) { p.inv = 0; p.hp = 3; p.slow = 0; } if (__tintim.S.tut) __tintim.S.tut.learned = true; });
  const rec = async (name, n, each) => { const d = `${OUT}/${name}`; fs.mkdirSync(d, { recursive: true }); const t0 = Date.now();
    for (let f = 0; f < n; f++) { if (each) await each(f); await keep(); await pg.clock.runFor(1000 / 30); await pg.screenshot({ path: `${d}/${String(f).padStart(3, '0')}.jpg`, quality: 92 }); }
    console.log(name, n, 'quadros', ((Date.now() - t0) / 1000).toFixed(0) + 's'); };
  await pg.clock.install({ time: new Date('2026-11-25T12:00:00') });
  console.log('goto'); await pg.goto('http://localhost:8765/?q=2' + (which === 'f2' ? '#fase2' : ''));
  await ff(() => window.__tintim && __tintim.R.ready && __tintim.state === 'title');
  console.log('title'); await pg.clock.runFor(600); await pg.click('#btnStart'); console.log('started');
  if (which === 'f1v') {
    for (let s = 0; s < 3; s++) { await pg.clock.runFor(900); await pg.mouse.click(640, 360); }
    await ff(() => __tintim.state === 'play' && !!__tintim.S.thief);
    await ff(() => !__tintim.S.cine && !__tintim.S.thief);
    console.log('jogando');
    await ev(() => { const p = __tintim.player; p.x = 9400; p.y = 300; });
    await pg.keyboard.down('ArrowRight'); await ff(() => __tintim.S.cine && __tintim.S.cine.type === 'boss'); await pg.keyboard.up('ArrowRight');
    await ff(() => !__tintim.S.cine && __tintim.S.arena, 60000);
    console.log('arena');
    await ev(() => { document.getElementById('btnNext').onclick = () => {}; const st = document.createElement('style'); st.textContent = '#win{display:none!important}'; document.head.appendChild(st); }); // a gravação não pode pular para o Arraial
    await keep();
    for (let i = 0; i < 12; i++) {
      await ff(() => __tintim.boss.state === 'chew' || __tintim.state !== 'play', 40000); await keep();
      await ev(() => { const b = __tintim.boss, p = __tintim.player; p.x = b.x + b.w / 2 - p.w / 2; p.y = b.y - 70; p.vy = 300; });
      for (let k = 0; k < 8; k++) { await pg.clock.runFor(1000 / 30); }
      const st = await ev(() => [__tintim.boss.hp, __tintim.state]); console.log('golpe', i, st);
      if (st[0] <= 0 || st[1] !== 'play') { await rec('vitoria', 150); break; }
      await pg.clock.runFor(1200);
    }
  } else
  if (which === 'f1') {
    for (let s = 0; s < 3; s++) { await pg.clock.runFor(900); await pg.mouse.click(640, 360); }
    await ff(() => __tintim.state === 'play' && !!__tintim.S.thief);
    await rec('roubo', 60);
    await ff(() => !__tintim.S.cine && !__tintim.S.thief);
    await pg.clock.runFor(300);
    await rec('corre', 42, async f => { const k = pg.keyboard;
      if (f === 0) await k.down('ArrowRight'); if (f === 8) await k.down('Space'); if (f === 16) await k.up('Space');
      if (f === 19) await k.down('Space'); if (f === 27) await k.up('Space'); });
    await pg.keyboard.up('ArrowRight');
    await ev(() => { const p = __tintim.player; p.x = 4060; p.y = 300; p.vx = 0; }); await ff(() => __tintim.player.onGround); await pg.clock.runFor(600);
    await rec('fareja', 40, async f => { if (f === 2) await pg.keyboard.down('ArrowDown'); });
    await pg.keyboard.up('ArrowDown');
    await ev(() => { const p = __tintim.player; p.x = 9400; p.y = 300; });
    await pg.keyboard.down('ArrowRight'); await ff(() => __tintim.S.cine && __tintim.S.cine.type === 'boss'); await pg.keyboard.up('ArrowRight');
    await ff(() => !__tintim.S.cine && __tintim.S.arena, 60000);
    await ff(() => __tintim.boss.state === 'chew', 40000);
    await rec('furtao', 45, async f => { if (f === 2) await ev(() => { const b = __tintim.boss, p = __tintim.player; p.x = b.x + b.w / 2 - p.w / 2; p.y = b.y - 260; p.vy = 0; p.vx = 0; p.onGround = false; }); });
    for (let i = 0; i < 3 && await ev(() => __tintim.state === 'play' && __tintim.boss.hp > 0); i++) {
      if (!await ff(() => __tintim.boss.state === 'chew' || __tintim.state !== 'play', 40000)) break;
      if (await ev(() => __tintim.state !== 'play')) break;
      await ev(() => { const b = __tintim.boss, p = __tintim.player; p.x = b.x + b.w / 2 - p.w / 2; p.y = b.y - 70; p.vy = 300; });
      await pg.clock.runFor(1500);
    }
    await ff(() => !!__tintim.S.prize && __tintim.S.prize.rest, 40000);
    await rec('vitoria', 80);
  } else {
    await ff(() => __tintim.state === 'play' && !__tintim.S.cine);
    await keep();
    await ev(() => { const p = __tintim.player; Object.assign(p, { x: 880, y: 300, vx: 0, vy: 0 }); });
    await ff(() => __tintim.player.onGround); await pg.clock.runFor(700);
    await rec('planar', 60, async f => { const k = pg.keyboard;
      if (f === 0) await k.down('ArrowRight'); if (f === 8) await k.down('Space'); if (f === 56) await k.up('Space'); });
    await pg.keyboard.up('Space'); await pg.keyboard.up('ArrowRight');
    const fx = await ev(() => TT.C.fires[0].x);
    await ev(x => { const p = __tintim.player; Object.assign(p, { x: x - 300, y: 300, vx: 0, vy: 0 }); }, fx);
    await ff(() => __tintim.player.onGround); await pg.clock.runFor(700);
    await rec('arquente', 54, async f => { const k = pg.keyboard;
      if (f === 0) await k.down('ArrowRight'); if (f === 6) await k.down('Space'); if (f === 18) await k.up('ArrowRight'); if (f === 30) await k.up('Space'); if (f === 34) await k.down('ArrowRight'); });
    await pg.keyboard.up('Space'); await pg.keyboard.up('ArrowRight');
    await ev(() => { const p = __tintim.player; Object.assign(p, { x: 3010, y: 300, vx: 0, vy: 0 }); });
    await ff(() => __tintim.player.onGround); await pg.clock.runFor(700);
    let jt = -1, walking = false;
    await rec('debandada', 100, async f => { const k = pg.keyboard;
      if (f === 0) { await k.down('ArrowRight'); walking = true; }
      const st = await ev(() => { const p = __tintim.player; const near = __tintim.S.runners.some(r => r.kind === 'run' && r.x - (p.x + p.w) < 150 && r.x + r.w > p.x - 10); return { x: p.x, g: p.onGround, near }; });
      if (walking && st.x > 3140) { await k.up('ArrowRight'); walking = false; }
      if (jt < 0 && st.near && st.g) { await k.down('Space'); jt = f; }
      if (jt >= 0 && f - jt === 10) { await k.up('Space'); jt = -1; }
    });
    await pg.keyboard.up('Space');
    const AX = await ev(() => TT.C.ARENA_X);
    await ev(x => { const p = __tintim.player; Object.assign(p, { x: x - 520, y: 300, vx: 0, vy: 0 }); }, AX);
    await ff(() => __tintim.player.onGround); await pg.clock.runFor(400);
    await rec('lobo-caca', 60, async f => { if (f === 0) await pg.keyboard.down('ArrowRight'); });
    await ff(() => __tintim.S.arena && !__tintim.S.cine, 60000); await pg.keyboard.up('ArrowRight');
    await pg.clock.runFor(1500);
    await rec('lobo-luta', 66, async f => { const k = pg.keyboard;
      if (f === 10) await k.down('Space'); if (f === 30) await k.up('Space'); if (f === 40) await k.down('ArrowLeft'); if (f === 50) await k.up('ArrowLeft'); });
  }
  await b.close();
})();
