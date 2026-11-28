// Coletor de evidência do Gate 1: abre o jogo nos dois viewports obrigatórios e salva um print
// de cada. Sai diferente de zero se o jogo não chegar a desenhar — é o que o hook Stop lê.
//
// Os dois casos vêm do CLAUDE.md: desktop 960x540 e um iPhone com safe-area e botões de toque.
// Os seis últimos commits da produção de 24-25/11 foram conserto de celular descoberto no fim.
//
// Uso: node game/tests/evidencia.js [pasta-de-saida]
//   (sobe o próprio servidor estático; não precisa de servidor aberto nem de python)
const { chromium, devices } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');

const RAIZ = path.join(__dirname, '..');                       // game/
const SAIDA = process.argv[2] || path.join(RAIZ, '..', 'production', 'evidencia');
const TIPO = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.mp3': 'audio/mpeg',
  '.mp4': 'video/mp4', '.webmanifest': 'application/manifest+json', '.svg': 'image/svg+xml' };

const servidor = http.createServer((req, res) => {
  const rel = decodeURIComponent(req.url.split('?')[0]).replace(/^\/+/, '') || 'index.html';
  const alvo = path.join(RAIZ, rel);
  if (!alvo.startsWith(RAIZ)) { res.writeHead(403).end(); return; }          // sem subir de pasta
  fs.readFile(alvo, (e, b) => e
    ? res.writeHead(404).end()
    : res.writeHead(200, { 'Content-Type': TIPO[path.extname(alvo)] || 'application/octet-stream' }).end(b));
});

// Os dois viewports obrigatórios. O do iPhone leva toque de verdade (hasTouch), porque é
// `pointer: coarse` que muda a câmera (DESCE, em render3d.js) e põe os botões na tela.
// O iPhone entra DEITADO: é a orientação que o jogo pede (manifest landscape, ui.js trava a
// orientação na tela cheia), e desde 28/11/2026 em pé o palco é coberto pela tela de "gire o
// aparelho" — fotografar em pé passaria a registrar a cobertura, não o jogo.
const ip = devices['iPhone 13'];
const CASOS = [
  { nome: 'desktop', opcoes: { viewport: { width: 960, height: 540 } } },
  { nome: 'iphone', opcoes: { ...ip, viewport: { width: ip.viewport.height, height: ip.viewport.width }, isMobile: true, hasTouch: true } },
];

(async () => {
  fs.mkdirSync(SAIDA, { recursive: true });
  await new Promise(r => servidor.listen(0, r));
  const url = `http://localhost:${servidor.address().port}/`;
  const navegador = await chromium.launch({ args: ['--use-angle=swiftshader',
    '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'] });

  let falhas = 0;
  for (const { nome, opcoes } of CASOS) {
    const ctx = await navegador.newContext(opcoes);
    const pg = await ctx.newPage();
    const erros = [];
    pg.on('pageerror', e => erros.push(e.message));
    pg.on('console', m => m.type() === 'error' && erros.push(m.text()));
    let desenhou = false;
    try {
      await pg.goto(url + '?q=0');
      // espera por condição, não por tempo fixo (mesma regra dos smoke tests)
      await pg.waitForFunction(() => window.__tintim && __tintim.R.ready, null,
        { timeout: 30000, polling: 100 });
      desenhou = true;
    } catch (e) { erros.push('não chegou a desenhar: ' + e.message.split('\n')[0]); }
    const arquivo = path.join(SAIDA, `${nome}.png`);
    await pg.screenshot({ path: arquivo });
    const kb = Math.round(fs.statSync(arquivo).size / 1024);
    const ok = desenhou && erros.length === 0;
    if (!ok) falhas++;
    console.log(`${ok ? 'ok   ' : 'FALHA'} ${nome.padEnd(8)} ${String(kb).padStart(4)} KB  ${arquivo}`);
    for (const e of erros.slice(0, 5)) console.log(`        ! ${e}`);
    await ctx.close();
  }

  await navegador.close();
  servidor.close();
  if (falhas) { console.log(`\n${falhas} viewport(s) com problema — a evidência não passa.`); process.exit(1); }
  console.log('\nEvidência completa: os dois viewports obrigatórios desenharam sem erro.');
})().catch(e => { console.error('evidencia.js quebrou: ' + e.message); process.exit(2); });
