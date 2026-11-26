// Renderiza anim.html quadro a quadro (1080×1920, 30 fps). Uso: node render.js <pasta-de-trabalho> <segundos>
const { chromium } = require('playwright'); const path = require('path'), fs = require('fs');
const WORK = path.resolve(process.argv[2]), N = Math.round(+process.argv[3] * 30), OUT = path.join(WORK, 'vframes');
fs.rmSync(OUT, { recursive: true, force: true }); fs.mkdirSync(OUT);
(async () => { const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  pg.on('pageerror', e => { console.error('ERRO na página:', e.message); process.exitCode = 1; });
  await pg.goto('file://' + path.join(WORK, 'anim.html')); await pg.evaluate(() => document.fonts.ready);
  const t0 = Date.now();
  for (let i = 0; i < N; i++) {
    await pg.evaluate(t => render(t), i / 30);
    await pg.waitForFunction(() => [...document.images].every(im => im.complete && im.naturalWidth), null, { timeout: 15000 });
    await pg.screenshot({ path: path.join(OUT, String(i).padStart(4, '0') + '.png') });
    if (i % 60 === 0) console.log(`quadro ${i}/${N} · ${((Date.now() - t0) / (i + 1)).toFixed(0)} ms/quadro`);
  }
  console.log('render: ' + N + ' quadros em ' + ((Date.now() - t0) / 1000).toFixed(0) + ' s'); await b.close(); })();
