// Teste de fumaça: joga o caminho crítico num navegador sem tela e falha se algo quebrar.
// Uso: (cd game && python3 -m http.server 8765 &) ; node game/tests/smoke.js [url]
// Espera por condições (e não por tempo fixo), então funciona mesmo em máquina lenta sem placa de vídeo.
const { chromium } = require('playwright');
(async () => {
  const url = process.argv[2] || 'http://localhost:8765/';
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const pg = await b.newPage({ viewport: { width: 960, height: 540 } });
  const errs = []; pg.on('pageerror', e => errs.push(e.message)); pg.on('console', m => m.type() === 'error' && errs.push(m.text()));
  pg.on('requestfailed', r => errs.push('falhou: ' + r.url()));
  const ev = f => pg.evaluate(f);
  const until = (f, ms = 20000) => pg.waitForFunction(f, null, { timeout: ms, polling: 50 }).then(() => true, () => false);
  const check = (ok, msg) => { console.log((ok ? 'ok   ' : 'FALHA') + ' ' + msg); if (!ok) process.exitCode = 1; };
  await pg.goto(url + '?q=0');
  check(await until(() => window.__tintim && __tintim.R.ready && __tintim.state === 'title'), 'abre na tela de título');
  check(await ev(() => __tintim.R.foe === 'pigeon'), 'os inimigos do Parque são pombos');
  await pg.waitForTimeout(600);
  await pg.click('#btnShelf');
  check(await until(() => document.querySelector('#shelf').classList.contains('on') && document.querySelectorAll('#shelf .slot').length === 5, 3000), 'estante de brinquedos abre com 5 lugares');
  await pg.click('#btnShelfBack'); await until(() => !document.querySelector('#shelf').classList.contains('on'), 3000);
  await pg.waitForTimeout(300); await pg.click('#btnStart');
  check(await until(() => TT.mapa.isOpen() && document.querySelector('#mapa canvas'), 4000), 'Jogar abre o mapa das fases');
  await pg.waitForTimeout(400); await pg.keyboard.press('Enter');
  check(await until(() => document.querySelector('#title').classList.contains('story')), 'Jogar abre a introdução');
  const scene = () => ev(() => __tintim.storyScene);
  await pg.waitForTimeout(700); await pg.mouse.click(480, 270); // cada toque avança uma tela
  check(await until(() => __tintim.storyScene === 1, 3000) && await ev(() => __tintim.state) === 'title', 'toque avança só para a segunda tela');
  await pg.mouse.click(480, 270); await pg.waitForTimeout(100);
  check(await scene() === 1, 'dois toques seguidos não pulam duas telas');
  await pg.waitForTimeout(600); await pg.mouse.click(480, 270);
  check(await until(() => __tintim.storyScene === 2, 3000) && await ev(() => __tintim.state) === 'title', 'toque avança para a terceira tela');
  await pg.waitForTimeout(600); await pg.mouse.click(480, 270);
  check(await until(() => __tintim.state === 'play'), 'toque na última tela inicia a partida');
  check(await until(() => !!__tintim.S.thief && __tintim.S.cine && __tintim.S.cine.type === 'steal', 5000), 'Furtão aparece com o macaco na abertura');
  check(await until(() => !__tintim.S.cine && !__tintim.S.thief, 8000), 'Furtão foge e o controle é liberado');
  await pg.keyboard.down('ArrowRight');
  check(await until(() => __tintim.player.x > 300), 'Tintim anda para a direita');
  check(await until(() => __tintim.S.cookies > 0), 'coleta biscoitos');
  await pg.keyboard.up('ArrowRight');
  await pg.keyboard.down('Space'); await until(() => !__tintim.player.onGround && __tintim.player.vy > -500); await pg.keyboard.up('Space');
  await pg.waitForTimeout(80); await pg.keyboard.down('Space');
  check(await until(() => __tintim.player.dj === false, 3000), 'pulo duplo no ar'); await pg.keyboard.up('Space');
  await until(() => __tintim.player.onGround);
  // faro: no começo, o rastro aponta para a moita falsa à esquerda; entrando nela, os biscoitos escondidos aparecem
  await ev(() => { const p = __tintim.player; p.x = 300; p.vx = 0; });
  await until(() => __tintim.player.onGround);
  await pg.keyboard.down('ArrowDown');
  check(await until(() => __tintim.S.scent && __tintim.S.scent.kind === 'hedge' && Math.abs(__tintim.player.vx) < 1, 3000), 'segurar ↓ fareja e o rastro aponta a moita falsa');
  await pg.keyboard.up('ArrowDown');
  const c0 = await ev(() => __tintim.S.cookies);
  await pg.keyboard.down('ArrowLeft');
  check(await until(() => __tintim.S.inHedge === 0, 4000), 'dá para entrar na moita falsa');
  check(await pg.waitForFunction(c => __tintim.S.cookies >= c + 3, c0, { timeout: 4000, polling: 50 }).then(() => true, () => false), 'a moita esconde 3 biscoitos');
  await pg.keyboard.up('ArrowLeft');
  // caminho de cheiro: invisível e sem chão até farejar perto dele; depois leva ao patinho
  check(await ev(() => !__tintim.S.revealed.duck && __tintim.S.items.find(i => i.type === 'toy').trail === 'duck'), 'caminho de cheiro começa escondido');
  await ev(() => { const p = __tintim.player; p.x = 4100; p.y = 300; p.vx = 0; });
  await until(() => __tintim.player.onGround && __tintim.player.y > 380);
  await pg.keyboard.down('ArrowDown');
  check(await until(() => __tintim.S.revealed.duck, 3000), 'farejar perto revela o caminho de cheiro');
  await pg.keyboard.up('ArrowDown');
  await ev(() => { const p = __tintim.player; p.x = 4190; p.y = 0; p.vy = 0; });
  check(await until(() => __tintim.player.onGround && __tintim.player.y < 62, 3000), 'as lajes de cheiro sustentam o Timtim');
  check(await until(() => __tintim.S.toy, 3000) && await ev(() => JSON.parse(localStorage.getItem('tintim-toys') || '{}').patinho === true), 'pega o patinho e ele fica salvo na estante');
  const ck = await ev(() => { const p = __tintim.player; p.x = 2010; p.y = 380; return __tintim.S.cookies; });
  check(await until(() => __tintim.S.friends[0].given) && await until(() => __tintim.S.gifts.length === 0) && await ev(() => __tintim.S.cookies) === ck + 3, 'amigo chihuahua entrega o biscoito');
  await pg.keyboard.press('KeyP');
  check(await until(() => __tintim.state === 'pause', 3000), 'P pausa');
  await pg.waitForTimeout(500); await pg.click('#btnResume');
  check(await until(() => __tintim.state === 'play', 3000), 'Continuar retoma');
  await ev(() => { const p = __tintim.player; p.x = 4200; p.y = 300; });
  check(await until(() => __tintim.S.checkpoint === 0, 5000), 'checkpoint ativado');
  await ev(() => { __tintim.player.hp = 1; __tintim.player.x = 4000; __tintim.player.y = 700; });
  check(await until(() => __tintim.state === 'lose'), 'cair no buraco sem corações perde');
  await pg.waitForSelector('#lose.on', { timeout: 20000 }); await pg.waitForTimeout(700); await pg.click('#btnRetry');
  check(await until(() => __tintim.state === 'play' && __tintim.player.x > 4100 && __tintim.player.hp === 3), 'tentar de novo volta ao checkpoint com 3 corações');
  await ev(() => { const p = __tintim.player; p.x = 9400; p.y = 300; });
  await pg.keyboard.down('ArrowRight');
  check(await until(() => __tintim.S.cine && __tintim.S.cine.type === 'boss'), 'cena de apresentação do Furtão');
  await pg.keyboard.up('ArrowRight');
  check(await until(() => !__tintim.S.cine && __tintim.S.arena, 40000), 'luta começa depois da cena');
  // pisar fora da hora não tira coração do Brutão: ele sacode o Timtim
  const hp0 = await ev(() => { const b = __tintim.boss, p = __tintim.player; p.inv = 5; p.x = b.x + 50; p.y = b.y - 70; p.vy = 300; return b.hp; });
  await pg.waitForTimeout(600);
  check(await ev(() => __tintim.boss.hp) === hp0, 'pisar fora da hora não machuca o Furtão');
  // regressão (24/11/2026): cair nas costas do Furtão enquanto ele anda não pode tirar coração do Timtim.
  // O desenho dele é mais alto que o corpo de colisão; antes, encostar descendo abaixo do topo contava como esbarrão de lado.
  await until(() => __tintim.boss.state === 'idle', 15000);
  await ev(() => { const S = __tintim.S, b = S.boss, p = S.player; S.ball = null; S.waves.length = 0; b.cd = 99; b.ballT = 99;
    Object.assign(p, { inv: 0, mega: 0, hp: 3, vx: 0, vy: 150, onGround: false, x: b.x + 12 - p.w, y: b.y + 45 - p.h }); b.dir = -1; b.vx = -90; });
  await pg.waitForTimeout(250); // o contato acontece nos primeiros quadros; depois disso ele pode cair de novo ao lado e levar um esbarrão de verdade
  check(await ev(() => __tintim.player.hp) === 3, 'cair nas costas do Furtão andando não tira coração');
  await ev(() => { __tintim.S.boss.cd = 1; __tintim.S.boss.ballT = 3; });
  // a bolinha distrai o Brutão; pisar na cabeça enquanto ele morde acerta
  await ev(() => { window.__safe = setInterval(() => { __tintim.player.inv = 2; __tintim.player.hp = 3; }, 100); }); // o teste não desvia dos ataques
  for (let i = 0; i < 3; i++) {
    const ok = await until(() => __tintim.boss.state === 'chew' || __tintim.state !== 'play', 30000);
    if (!ok || await ev(() => __tintim.state) !== 'play') break;
    const hp = await ev(() => { const b = __tintim.boss, p = __tintim.player; p.inv = 5; p.x = b.x + b.w / 2 - p.w / 2; p.y = b.y - 70; p.vy = 300; return b.hp; });
    await pg.waitForFunction(h => __tintim.boss.hp < h || __tintim.state !== 'play', hp, { timeout: 4000, polling: 50 }).catch(() => {});
    if (i === 0) check(await ev(() => __tintim.boss.hp) === hp - 1, 'bolinha distrai o Furtão e o pisão acerta');
  }
  check(await until(() => __tintim.state !== 'play' && !!__tintim.S.prize, 40000), '3 pisões na hora certa soltam o Macaco Fedido');
  check(await until(() => __tintim.S.prize.rest, 5000), 'o macaco cai no chão ao lado do Timtim');
  check(await until(() => __tintim.state === 'win', 40000), 'vitória depois do resgate');
  check(await pg.waitForSelector('#win.on', { timeout: 30000 }).then(() => true, () => false), 'tela de vitória aparece');
  check(await ev(() => document.querySelector('#stToy').classList.contains('ok')), 'vitória mostra o brinquedo achado');
  check(await ev(() => __tintim.S.items.every(i => ['cookie', 'gold', 'choco', 'toy'].includes(i.type))), 'na fase só há biscoitos, dourados, chocolates e o brinquedo perdido');
  check(errs.length === 0, 'sem erros no console' + (errs.length ? ': ' + errs.join(' | ') : ''));
  await b.close();
})();
