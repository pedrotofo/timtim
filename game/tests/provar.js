// provar.js — a prova completa do Timtim, igual no Windows, no macOS e no Linux.
//
// Substitui o provar.sh, que só rodava no Linux: ele chamava python3 (no Windows é python ou py)
// e usava /dev/tcp, que o Git Bash não suporta. Aqui o servidor é Node, que os testes já exigem.
//
// Roda os três smoke tests, a evidência nos dois viewports obrigatórios e, se game.js mudou, as
// métricas (a regra dos 70%). Em caso de sucesso escreve production/evidencia/prova.ok — o recibo
// que .claude/hooks/gate-evidencia.sh confere.
//
// Uso: node game/tests/provar.js        (ou: npm run provar)
const http = require('http'), fs = require('fs'), path = require('path');
const { spawn, execFileSync } = require('child_process');

const RAIZ = path.join(__dirname, '..', '..');         // a raiz do repositório
const GAME = path.join(RAIZ, 'game');
const OUT = path.join(RAIZ, 'production', 'evidencia');
const RECIBO = path.join(OUT, 'prova.ok');
const TIPO = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.mp3': 'audio/mpeg',
  '.mp4': 'video/mp4', '.webmanifest': 'application/manifest+json', '.svg': 'image/svg+xml' };

function servidor() {
  return http.createServer((req, res) => {
    const rel = decodeURIComponent(req.url.split('?')[0]).replace(/^\/+/, '') || 'index.html';
    const alvo = path.join(GAME, rel);
    if (!path.resolve(alvo).startsWith(path.resolve(GAME))) { res.writeHead(403).end(); return; }
    fs.readFile(alvo, (e, b) => e
      ? res.writeHead(404).end()
      : res.writeHead(200, { 'Content-Type': TIPO[path.extname(alvo)] || 'application/octet-stream' }).end(b));
  });
}

// roda um teste e repassa a saída; devolve o código de saída
function rodar(arquivo, args = []) {
  return new Promise(ok => {
    const p = spawn(process.execPath, [path.join(__dirname, arquivo), ...args],
      { cwd: RAIZ, stdio: 'inherit' });
    p.on('close', c => ok(c === 0));
    p.on('error', e => { console.error('não deu para rodar ' + arquivo + ': ' + e.message); ok(false); });
  });
}

// game.js mudou? então as métricas entram (a regra dos 70%). Sem git, não arrisca: não roda.
function gameJsMudou() {
  try {
    execFileSync('git', ['diff', '--quiet', 'HEAD', '--', 'game/src/game.js'],
      { cwd: RAIZ, stdio: 'ignore' });
    return false;                       // saiu 0: sem mudança
  } catch (e) {
    return e.status === 1;              // saiu 1: mudou. Outro código: git indisponível
  }
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  fs.rmSync(RECIBO, { force: true });

  // Porta 0 = o sistema escolhe uma livre, e a URL vai por argumento para cada teste (todos
  // aceitam process.argv[2]). Com porta fixa, duas provas ao mesmo tempo colidiam.
  const srv = servidor();
  await new Promise((ok, erro) => {
    srv.once('error', e => erro(new Error(e.message)));
    srv.listen(0, '127.0.0.1', ok);
  });
  const url = `http://localhost:${srv.address().port}/`;

  let falhas = 0;
  for (const t of ['smoke.js', 'smoke-arraial.js', 'smoke-quadro.js']) {
    console.log(`\n=== ${t} ===`);
    if (!await rodar(t, [url])) falhas++;
  }

  console.log('\n=== evidência (desktop + iphone) ===');
  if (!await rodar('evidencia.js', [OUT])) falhas++;

  if (gameJsMudou()) {
    console.log('\n=== métricas (game.js mudou: a regra dos 70%) ===');
    if (!await rodar('metricas.js')) falhas++;
  }

  srv.close();

  if (falhas) {
    console.log(`\n${falhas} etapa(s) falharam — nenhum recibo escrito.`);
    process.exit(1);
  }
  fs.writeFileSync(RECIBO, new Date().toISOString() + '\n');
  console.log(`\nProva completa. Recibo: ${path.relative(RAIZ, RECIBO)}`);
})().catch(e => { console.error('provar.js quebrou: ' + e.message); process.exit(2); });
