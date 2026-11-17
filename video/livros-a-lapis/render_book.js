// node render_book.js <saída-dir> <segundos> '<json>'
const { chromium } = require('playwright'); const path = require('path'), fs = require('fs');
const [out, secs, cfg] = [process.argv[2], +process.argv[3], process.argv[4]]; const N = Math.round(secs * 30);
fs.rmSync(out, { recursive: true, force: true }); fs.mkdirSync(out, { recursive: true });
(async () => { const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1280, height: 720 } });
  await pg.goto('file://' + path.resolve('book3d.html') + '?c=' + encodeURIComponent(cfg)); await pg.evaluate(() => document.fonts.ready);
  await pg.waitForFunction(() => [...document.images].every(i => i.complete && i.naturalWidth)); await pg.waitForTimeout(300);
  for (let i = 0; i < N; i++) { await pg.evaluate(([t, d]) => render(t, d), [i / 30, secs]);
    await pg.screenshot({ path: path.join(out, String(i).padStart(4, '0') + '.jpg'), type: 'jpeg', quality: 90 }); }
  await b.close(); })();
