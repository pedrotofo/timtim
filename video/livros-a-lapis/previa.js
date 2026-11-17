const { chromium } = require('playwright'); const path = require('path');
const ts = process.argv.slice(2).map(Number);
(async () => { const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  pg.on('pageerror', e => console.error('ERRO', e.message));
  await pg.goto('file://' + path.resolve('cena.html')); await pg.evaluate(() => document.fonts.ready);
  for (const t of ts) { await pg.evaluate(t => render(t), t); await pg.waitForFunction(() => [...document.images].every(i => i.complete && i.naturalWidth)); await pg.waitForTimeout(120);
    await pg.screenshot({ path: `prev2-${t}.png` }); }
  await b.close(); })();
