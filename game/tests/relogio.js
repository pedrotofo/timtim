// relogio.js — regressão do Grupo D do laudo (item 19): o relógio da música não dirige a física.
//
// O defeito: TT.beatClock() devolvia TT.beatTime() cru (ctx.currentTime), que não congela na pausa
// nem anda no passo fixo de 1/240 s, e era o relógio das tábuas da quadrilha. Medido no laudo de
// 28/11/2026: 195,3 px de teleporte lateral num só passo depois de 3,7 s de pausa, e 1,55× a
// velocidade de projeto sem pausa nenhuma, com picos de 16×.
//
// A fonte de som é falsificada de propósito (um relógio de música hostil: 10× o tempo real, com
// saltos para trás, como o laço da trilha). Sem essa fixture o teste passaria contra o próprio
// defeito, porque neste contêiner o áudio pode nem tocar e beatTime() devolver null.
//
// Uso: node game/tests/relogio.js [url-base]
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');

const RAIZ = path.join(__dirname, '..', '..');
const GAME = path.join(RAIZ, 'game');
const STEP = 1 / 240;
const TIPO = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.mp3': 'audio/mpeg',
  '.mp4': 'video/mp4', '.webmanifest': 'application/manifest+json', '.svg': 'image/svg+xml' };

const servidor = () => http.createServer((req, res) => {
  const rel = decodeURIComponent(req.url.split('?')[0]).replace(/^\/+/, '') || 'index.html';
  const alvo = path.join(GAME, rel);
  if (!path.resolve(alvo).startsWith(path.resolve(GAME))) { res.writeHead(403).end(); return; }
  fs.readFile(alvo, (e, b) => e
    ? res.writeHead(404).end()
    : res.writeHead(200, { 'Content-Type': TIPO[path.extname(alvo)] || 'application/octet-stream' }).end(b));
});

const falhas = [];
function confere(nome, ok, detalhe) {
  console.log(`${ok ? '  ok  ' : ' FALHA'} ${nome}${detalhe ? ' — ' + detalhe : ''}`);
  if (!ok) falhas.push(nome);
}

(async () => {
  let srv = null, base = process.argv[2];
  if (!base) { srv = servidor(); await new Promise(ok => srv.listen(0, '127.0.0.1', ok)); base = `http://localhost:${srv.address().port}/`; }
  const navegador = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader',
    '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'] });
  const ctx = await navegador.newContext({ viewport: { width: 960, height: 540 } });
  const pg = await ctx.newPage();
  const erros = [];
  pg.on('pageerror', e => erros.push(e.message));

  // fase 2: é a única com tábuas da quadrilha (C.movers), e a trilha do Arraial é a que tem relógio de batida
  await pg.goto(`${base}?fase=2&q=0`);
  await pg.waitForFunction(() => window.__tintim && __tintim.R.ready, null, { timeout: 60000, polling: 100 });
  await pg.waitForTimeout(600); await pg.click('#btnStart').catch(() => {});
  await pg.waitForTimeout(500); await pg.keyboard.press('Enter').catch(() => {});
  await pg.waitForTimeout(900); await pg.keyboard.press('Space').catch(() => {});
  const jogando = await pg.waitForFunction(() => __tintim.state === 'play', null, { timeout: 40000, polling: 50 })
    .then(() => true, () => false);
  if (!jogando) { console.log('FALHA: não entrou em jogo'); process.exitCode = 1; await navegador.close(); if (srv) srv.close(); return; }
  await pg.waitForFunction(() => !__tintim.S.cine, null, { timeout: 40000, polling: 50 }).catch(() => {});

  // ARRANJO — fonte de som hostil, e um observador de todo passo de 1/240 s
  await pg.evaluate(() => {
    let saltos = 0;
    TT.beatTime = () => {                            // 10× o tempo real, com um salto para trás a cada ~0,5 s
      const t = performance.now() / 1000 * 10;
      if (Math.floor(t / 5) > saltos) saltos = Math.floor(t / 5);
      return t - saltos * 3;                         // volta 3 s de vez em quando, como o laço da trilha
    };
    const orig = TT.update;
    window.__obs = { maxdx: 0, maxBeatSalto: 0, beatVoltou: false, prevBeat: TT.beatClock(), passos: 0 };
    TT.update = dt => {
      orig(dt);
      const o = window.__obs; o.passos++;
      for (const s of TT.MOVERS) o.maxdx = Math.max(o.maxdx, Math.abs(s.dx), Math.abs(s.dy));
      const b = TT.beatClock(), d = b - o.prevBeat; o.prevBeat = b;
      if (d < 0) o.beatVoltou = true;
      o.maxBeatSalto = Math.max(o.maxBeatSalto, d);
    };
  });
  await pg.waitForTimeout(1200);

  // AÇÃO 1 — as tábuas têm de estar onde o relógio da FASE manda, não onde o da música manda
  const pos = await pg.evaluate(() => ({
    clock: TT.S.clock,
    tabuas: TT.MOVERS.map(s => ({ x: s.x, y: s.y, m: { x: s.mover.x, y: s.mover.y, ax: s.mover.ax, ay: s.mover.ay, per: s.mover.per, ph: s.mover.ph } })),
  }));
  const erroMax = Math.max(...pos.tabuas.map(t => {
    const a = Math.PI * 2 * pos.clock / t.m.per + t.m.ph;
    return Math.max(Math.abs(t.x - (t.m.x + t.m.ax * Math.sin(a))), Math.abs(t.y - (t.m.y + t.m.ay * Math.sin(a))));
  }));
  confere('a tábua está na posição que S.clock manda, com a música fora do passo',
    erroMax < 0.5, `erro máximo ${erroMax.toFixed(2)} px`);

  // AÇÃO 2 — pausa de 3,7 s (o pior caso medido no laudo: basta trocar de aba) e volta
  await pg.evaluate(() => { window.__obs.maxdx = 0; TT.pause(); });
  await pg.waitForTimeout(3700);
  await pg.evaluate(() => TT.resume());
  await pg.waitForTimeout(900);

  const obs = await pg.evaluate(() => ({ ...window.__obs, limites: TT.MOVERS.map(s => Math.max(s.mover.ax, s.mover.ay) * Math.PI * 2 / s.mover.per) }));
  // o quanto uma tábua PODE andar num passo: ax · 2π/per · STEP (1,2 px na mais rápida da fase 2)
  const teto = Math.max(...obs.limites) * STEP * 1.5 + 0.2;
  confere('nenhum passo teleporta a tábua, nem ao voltar de 3,7 s de pausa',
    obs.maxdx <= teto, `maior passo ${obs.maxdx.toFixed(2)} px, teto ${teto.toFixed(2)} px`);

  confere('beatClock nunca volta atrás', !obs.beatVoltou);
  confere('beatClock nunca salta para frente num passo', obs.maxBeatSalto < 0.25,
    `maior salto ${obs.maxBeatSalto.toFixed(3)} s`);
  confere('o jogo continuou andando em passos de 1/240 s', obs.passos > 240, `${obs.passos} passos`);
  confere('sem erro de página', erros.length === 0, erros.join(' | '));

  await navegador.close(); if (srv) srv.close();
  console.log(falhas.length ? `\nrelogio.js: ${falhas.length} falha(s)` : '\nrelogio.js: verde');
  process.exitCode = falhas.length ? 1 : 0;
})();
