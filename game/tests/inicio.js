// Teste do começo do jogo como o jogador vê: navegador que ainda não deixa tocar som (o normal na primeira visita),
// "aperte para começar" na tela de carregamento, música liberada pelo toque, e a passagem mapa → card sem a capa piscar no meio.
// Uso: (servidor local na porta 8765 servindo a pasta game/) ; node game/tests/inicio.js [url]
const { chromium } = require('playwright');
(async () => {
  const url = (process.argv[2] || 'http://localhost:8765/') + '?q=0';
  // sem --autoplay-policy: o som começa travado, como num navegador de verdade
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const pg = await b.newPage({ viewport: { width: 960, height: 540 } });
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  const ev = (f, a) => pg.evaluate(f, a);
  const until = (f, ms = 30000) => pg.waitForFunction(f, null, { timeout: ms, polling: 50 }).then(() => true, () => false);
  const check = (ok, msg) => { console.log((ok ? 'ok   ' : 'FALHA') + ' ' + msg); if (!ok) process.exitCode = 1; };
  await pg.goto(url);
  check(await until(() => document.getElementById('msg').classList.contains('gate')), 'com o som travado, o carregamento termina em "aperte para começar"');
  check(await ev(() => /começar/.test(document.getElementById('msgTxt').textContent) && TT.audioState() !== 'running'), 'o aviso diz para começar e o som ainda está travado');
  await pg.keyboard.press('Space');
  check(await until(() => document.getElementById('msg').classList.contains('hide'), 4000), 'uma tecla fecha o aviso e mostra a capa');
  check(await until(() => TT.audioState() === 'running', 3000), 'a tecla libera o som (a música da capa pode tocar)');
  check(await ev(() => !TT.mapa.isOpen() && __tintim.state === 'title'), 'a tecla que liberou o som não aperta Jogar sozinha');
  // mapa → card: a capa não pode aparecer entre os dois
  await pg.waitForTimeout(500); await pg.click('#btnStart');
  await until(() => TT.mapa.isOpen(), 4000); await pg.waitForTimeout(500);
  // a narração só pode entrar depois que o card aparece (não no clique, com o mapa ainda na tela)
  await ev(() => { window._vozEm = null; const v0 = TT.voice; TT.voice = i => { if (i >= 0 && window._vozEm === null) window._vozEm = performance.now(); return v0(i); }; window._enterEm = performance.now(); });
  await pg.keyboard.press('Enter');
  const viu = await ev(() => new Promise(res => { const t0 = performance.now(), log = [];
    const tick = () => { const capa = getComputedStyle(document.querySelector('#title .tbg')).visibility !== 'hidden' && !TT.mapa.isOpen() && getComputedStyle(document.getElementById('introC')).opacity < 0.5;
      if (capa) log.push(Math.round(performance.now() - t0)); if (performance.now() - t0 < 2500) requestAnimationFrame(tick); else res(log); };
    tick(); }));
  check(viu.length === 0, 'entre o mapa e o card a capa não aparece' + (viu.length ? ' (apareceu em ' + viu.slice(0, 5).join(', ') + ' ms)' : ''));
  check(await until(() => !TT.mapa.isOpen() && document.getElementById('title').classList.contains('story'), 3000), 'o mapa fecha depois que o card já entrou');
  check(await until(() => window._vozEm !== null, 4000) && await ev(() => window._vozEm - window._enterEm >= 1100), 'a narração começa só depois que o card aparece (não junto com o clique)');
  check(errs.length === 0, 'sem erros na página' + (errs.length ? ': ' + errs.join(' | ') : ''));
  await b.close();
})();
