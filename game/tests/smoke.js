// Teste de fumaça: joga o caminho crítico num navegador sem tela e falha se algo quebrar.
// Uso: (cd game && python3 -m http.server 8765 &) ; node game/tests/smoke.js [url]
// Espera por condições (e não por tempo fixo), então funciona mesmo em máquina lenta sem placa de vídeo.
const { chromium } = require('playwright');
(async () => {
  const url = process.argv[2] || 'http://localhost:8765/';
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'] });
  const pg = await b.newPage({ viewport: { width: 960, height: 540 } });
  const errs = []; pg.on('pageerror', e => errs.push(e.message + ' @ ' + String(e.stack || '').split(String.fromCharCode(10)).slice(1, 3).join(' '))); pg.on('console', m => m.type() === 'error' && errs.push(m.text()));
  pg.on('requestfailed', r => errs.push('falhou: ' + r.url()));
  const ev = f => pg.evaluate(f);
  const until = (f, ms = 20000) => pg.waitForFunction(f, null, { timeout: ms, polling: 50 }).then(() => true, () => false);
  const check = (ok, msg) => { console.log((ok ? 'ok   ' : 'FALHA') + ' ' + msg); if (!ok) process.exitCode = 1; };
  await pg.goto(url + '?q=0');
  check(await until(() => window.__tintim && __tintim.R.ready && __tintim.state === 'title'), 'abre na tela de título');
  check(await ev(() => __tintim.R.foe === 'pigeon'), 'os inimigos do Parque são pombos');
  check(await ev(() => { const l = document.querySelector('#msg .loadLogo'); return !!l && l.naturalWidth > 0 && getComputedStyle(l).animationName === 'logoPisca'; }), 'a tela de carregamento tem o logo piscando no canto');
  check(await ev(() => document.title === 'Timtim e os Brinquedos Perdidos' && document.querySelector('.logo img').alt === 'Timtim e os Brinquedos Perdidos' && document.querySelector('.logo img').naturalWidth > 0 && !document.querySelector('.tagline')), 'a capa mostra o logo do jogo, sem o convite embaixo');
  await pg.waitForTimeout(600);
  await pg.click('#btnShelf');
  check(await until(() => document.querySelector('#shelf').classList.contains('on') && document.querySelectorAll('#premioSlots .slot').length === 5 && document.querySelectorAll('#shelfSlots .slot').length === 5, 3000), 'a estante abre com os presentes das aventuras em cima e os escondidos embaixo');
  check(await ev(() => document.querySelector('#premioSlots .slot').textContent.includes('Vença a fase') && document.querySelectorAll('#shelfSlots .slot')[2].textContent.includes('Girassol') === false && document.querySelectorAll('#shelfSlots .slot')[2].textContent.includes('Quadro')), 'presente ainda não ganho aparece como "Vença a fase"');
  await pg.click('#btnShelfBack'); await until(() => !document.querySelector('#shelf').classList.contains('on'), 3000);
  check(await ev(() => document.getElementById('btnReset').hidden), 'sem progresso, não aparece "Recomeçar o jogo"');
  // com progresso salvo: o link aparece, o primeiro toque pede confirmação e o segundo apaga só o progresso
  await ev(() => { localStorage.setItem('tintim-fases', '{"1":true,"2":true}'); localStorage.setItem('tintim-toys', '{"patinho":true}'); localStorage.setItem('tintim-best', '{"stars":3,"time":72}'); localStorage.setItem('tintim-calmo', '1'); });
  await pg.reload(); await until(() => window.__tintim && __tintim.R.ready && __tintim.state === 'title' && document.getElementById('msg').classList.contains('hide'));
  check(await ev(() => document.getElementById('btnReset').hidden), 'na capa o botão de recomeçar não aparece (ele fica no mapa)');
  await pg.waitForTimeout(400); await pg.click('#btnStart'); await until(() => TT.mapa.isOpen(), 4000); await pg.waitForTimeout(200);
  check(await ev(() => !document.getElementById('btnReset').hidden && getComputedStyle(document.getElementById('btnReset')).borderTopStyle === 'solid'), 'com progresso salvo, o mapa mostra o botão "Recomeçar o jogo"');
  await pg.waitForTimeout(500); await pg.click('#btnReset');
  check(await ev(() => document.getElementById('btnReset').textContent.includes('Toque de novo') && localStorage.getItem('tintim-fases') !== null), 'o primeiro toque só pede confirmação');
  await Promise.all([pg.waitForNavigation({ timeout: 15000 }).catch(() => {}), pg.click('#btnReset')]);
  await until(() => window.__tintim && __tintim.R.ready && __tintim.state === 'title' && document.getElementById('msg').classList.contains('hide'));
  check(await ev(() => !localStorage.getItem('tintim-fases') && !localStorage.getItem('tintim-toys') && !localStorage.getItem('tintim-best') && localStorage.getItem('tintim-calmo') === '1' && document.getElementById('btnReset').hidden), 'o segundo toque apaga o progresso, guarda as preferências e o link some');
  await ev(() => localStorage.removeItem('tintim-calmo')); await pg.reload(); await until(() => window.__tintim && __tintim.R.ready && __tintim.state === 'title' && document.getElementById('msg').classList.contains('hide'));
  await pg.waitForTimeout(300); await pg.click('#btnStart');
  check(await until(() => TT.mapa.isOpen() && document.querySelector('#mapa canvas'), 4000), 'Jogar abre o mapa das fases');
  await pg.waitForTimeout(400); await pg.keyboard.press('Enter');
  check(await until(() => document.querySelector('#title').classList.contains('story') && __tintim.storyScene === 0), 'escolher a fase no mapa abre o card da história da fase 1');
  check(await ev(() => document.getElementById('storyLine').textContent.includes('roubou o Macaco Fedido')), 'o card conta que o Furtão roubou o Macaco Fedido');
  await pg.mouse.click(480, 270);
  check(await ev(() => __tintim.state) === 'title', 'o toque que abriu o card não pula o card');
  await pg.waitForTimeout(900); await pg.mouse.click(480, 270);
  check(await until(() => __tintim.state === 'play'), 'um toque no card começa a fase');
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
  await pg.click('#btnCalmo');
  check(await ev(() => TT.calmo === true && localStorage.getItem('tintim-calmo') === '1' && document.getElementById('btnCalmo').textContent.endsWith('sim')), 'a pausa liga "menos tremor e clarão" e guarda a escolha');
  await pg.click('#btnCalmo');
  check(await ev(() => TT.calmo === false && localStorage.getItem('tintim-calmo') === '0'), 'e desliga de novo');
  check(await ev(() => { const n = TT.audioNodes(); return !n.ctx || (n.comp.threshold.value === -6 && n.comp.ratio.value === 12); }), 'o som geral passa por um limitador que só age nos picos (não pelo compressor de fábrica)');
  // mixagem em camadas: nenhum efeito acima de -16 dB (a música fica por volta de -21) e, com uma revoada de sons do cenário,
  // no máximo 2 tocam juntos
  check(await ev(() => Object.values(TT.mixInfo().alvos).every(d => d <= -16)), 'nenhum efeito foi mixado acima de -16 dB (pancadas não estouram por cima da música)');
  check(await ev(async () => { for (let i = 0; i < 8; i++) TT.sfx(i % 2 ? 'henPanic' : 'pigeon'); await new Promise(r => setTimeout(r, 30)); return TT.mixInfo().camadas.mundo <= 2; }), 'muitos bichos de uma vez: só 2 sons do cenário tocam juntos');
  await pg.waitForTimeout(500); await pg.click('#btnResume');
  check(await until(() => __tintim.state === 'play', 3000), 'Continuar retoma');
  await ev(() => { const p = __tintim.player; p.x = 4200; p.y = 300; });
  check(await until(() => __tintim.S.checkpoint === 1, 5000), 'checkpoint ativado'); // (a bandeira 0 agora fica em 2600)
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
  check(await until(() => __tintim.S.prize && __tintim.S.prize.rest, 5000), 'o macaco cai no chão ao lado do Timtim');
  check(await until(() => __tintim.state === 'win', 40000), 'vitória depois do resgate');
  check(await pg.waitForSelector('#win.on', { timeout: 30000 }).then(() => true, () => false), 'tela de vitória aparece');
  check(await ev(() => document.querySelector('#stToy').classList.contains('ok')), 'vitória mostra o brinquedo achado');
  check(await ev(() => __tintim.S.items.every(i => ['cookie', 'gold', 'choco', 'toy'].includes(i.type))), 'na fase só há biscoitos, dourados, chocolates e o brinquedo perdido');
  check(errs.length === 0, 'sem erros no console' + (errs.length ? ': ' + errs.join(' | ') : ''));
  await b.close();
})();
