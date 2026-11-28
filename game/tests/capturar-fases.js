// capturar-fases.js — fotografa o jogo por dentro, ao longo das três fases.
//
// Existe porque uma revisão de progressão ou de arte precisa VER a fase, e o evidencia.js só
// fotografa a tela de título. Os agentes que julgam (art-director, level-designer, ux-designer)
// não têm Bash: não rodam o jogo. Este script é quem produz a evidência para eles.
//
// Uso: node game/tests/capturar-fases.js [pasta-de-saida] [--mobile]
const { chromium, devices } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');

const RAIZ = path.join(__dirname, '..', '..');
const GAME = path.join(RAIZ, 'game');
const args = process.argv.slice(2);
const MOBILE = args.includes('--mobile');
const SAIDA = args.find(a => !a.startsWith('--')) ||
  path.join(RAIZ, 'production', 'fases' + (MOBILE ? '-celular' : ''));
const TIPO = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.mp3': 'audio/mpeg',
  '.mp4': 'video/mp4', '.webmanifest': 'application/manifest+json', '.svg': 'image/svg+xml' };

// Quantos pontos por fase, de START_X até a arena do chefe. Evita o trecho da arena, que é luta.
const PONTOS = 8;

const servidor = () => http.createServer((req, res) => {
  const rel = decodeURIComponent(req.url.split('?')[0]).replace(/^\/+/, '') || 'index.html';
  const alvo = path.join(GAME, rel);
  if (!path.resolve(alvo).startsWith(path.resolve(GAME))) { res.writeHead(403).end(); return; }
  fs.readFile(alvo, (e, b) => e
    ? res.writeHead(404).end()
    : res.writeHead(200, { 'Content-Type': TIPO[path.extname(alvo)] || 'application/octet-stream' }).end(b));
});

(async () => {
  fs.mkdirSync(SAIDA, { recursive: true });
  const srv = servidor();
  await new Promise(ok => srv.listen(0, '127.0.0.1', ok));
  const base = `http://localhost:${srv.address().port}/`;
  const navegador = await chromium.launch({ args: ['--use-angle=swiftshader',
    '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'] });

  const opcoes = MOBILE
    ? { ...devices['iPhone 13'], isMobile: true, hasTouch: true }
    : { viewport: { width: 960, height: 540 } };

  for (const fase of [1, 2, 3]) {
    const ctx = await navegador.newContext(opcoes);
    const pg = await ctx.newPage();
    const erros = [];
    pg.on('pageerror', e => erros.push(e.message));
    await pg.goto(`${base}?fase=${fase}&q=2`);           // q=2: qualidade cheia, para julgar a arte
    await pg.waitForFunction(() => window.__tintim && __tintim.R.ready, null, { timeout: 60000, polling: 100 });

    // começa a fase: capa -> mapa/card -> jogo
    await pg.waitForTimeout(600); await pg.click('#btnStart').catch(() => {});
    await pg.waitForTimeout(500); await pg.keyboard.press('Enter').catch(() => {});
    await pg.waitForTimeout(900); await pg.keyboard.press('Space').catch(() => {});
    const jogando = await pg.waitForFunction(() => __tintim.state === 'play', null,
      { timeout: 40000, polling: 50 }).then(() => true, () => false);
    if (!jogando) { console.log(`FALHA fase ${fase}: não entrou em jogo`); await ctx.close(); continue; }
    // deixa o cartão de abertura passar
    await pg.waitForFunction(() => !__tintim.S.cine, null, { timeout: 40000, polling: 50 }).catch(() => {});

    const { inicio, fim } = await pg.evaluate(() => ({ inicio: TT.C.START_X || 200, fim: TT.C.ARENA_X }));
    for (let i = 0; i < PONTOS; i++) {
      const x = Math.round(inicio + ((fim - inicio) * i) / (PONTOS - 1));
      // põe o Timtim no chão naquele x, invencível, e deixa a câmera e a cena assentarem
      await pg.evaluate(xx => {
        const p = __tintim.player;
        Object.assign(p, { x: xx, y: TT.C.GROUND - p.h - 1, vx: 0, vy: 0, onGround: true, inv: 999, hp: 3 });
      }, x);
      await pg.waitForTimeout(700);
      const arq = path.join(SAIDA, `fase${fase}-${String(i + 1).padStart(2, '0')}-x${x}.png`);
      await pg.screenshot({ path: arq });
      process.stdout.write(`fase ${fase}  ponto ${i + 1}/${PONTOS}  x=${String(x).padStart(5)}  ${path.basename(arq)}\n`);
    }
    if (erros.length) console.log(`  ! fase ${fase}: ${erros.length} erro(s) no console: ${erros[0].slice(0, 90)}`);
    await ctx.close();
  }

  await navegador.close();
  srv.close();
  const n = fs.readdirSync(SAIDA).filter(f => f.endsWith('.png')).length;
  console.log(`\n${n} capturas em ${path.relative(RAIZ, SAIDA)}`);
})().catch(e => { console.error('capturar-fases.js quebrou: ' + e.message); process.exit(2); });
