// Teste de fumaça da fase 2 (o Arraial): planar, ar quente da fogueira, chama que machuca, tábuas da quadrilha,
// faro revelando o caminho até a sanfoninha, galinhas agitadas, brincadeiras juninas e a luta com o lobo-guará. Mesmo esquema do smoke.js: espera por condições.
// Uso: (cd game && python3 -m http.server 8765 &) ; node game/tests/smoke-arraial.js [url]
const { chromium } = require('playwright');
(async () => {
  const url = (process.argv[2] || 'http://localhost:8765/') + '?fase=2&q=0';
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const pg = await b.newPage({ viewport: { width: 960, height: 540 } });
  const errs = []; pg.on('pageerror', e => errs.push(e.message)); pg.on('console', m => m.type() === 'error' && errs.push(m.text()));
  pg.on('requestfailed', r => errs.push('falhou: ' + r.url()));
  const ev = (f, a) => pg.evaluate(f, a);
  const until = (f, ms = 20000) => pg.waitForFunction(f, null, { timeout: ms, polling: 50 }).then(() => true, () => false);
  const check = (ok, msg) => { console.log((ok ? 'ok   ' : 'FALHA') + ' ' + msg); if (!ok) process.exitCode = 1; };
  const put = (x, y, extra) => ev(([x, y, extra]) => { const p = __tintim.player; Object.assign(p, { x, y, vx: 0, vy: 0, onGround: false, inv: 0, hp: 3 }, extra || {}); }, [x, y, extra]);
  await pg.goto(url);
  check(await until(() => window.__tintim && __tintim.R.ready && __tintim.state === 'title'), 'abre o título na fase 2');
  check(await ev(() => document.getElementById('faseTag').textContent.includes('ARRAIAL')), 'título mostra "Fase 2 · O Arraial"');
  await pg.waitForTimeout(500); await pg.click('#btnStart');
  check(await until(() => TT.mapa.isOpen() && document.querySelector('#mapa canvas'), 4000), 'Jogar abre o mapa das fases');
  await pg.waitForTimeout(400); await pg.keyboard.press('Enter');
  check(await until(() => __tintim.state === 'play' && __tintim.S.cine && __tintim.S.cine.type === 'arraial', 5000), 'Jogar começa direto, com o cartão do Arraial');
  check(await until(() => !__tintim.S.cine, 6000), 'cartão some e o controle é liberado');
  check(await ev(() => !__tintim.S.thief && !__tintim.S.arena), 'sem Furtão nem chefão no Arraial');
  check(await ev(() => __tintim.R.foe === 'galinha' && __tintim.S.enemies.length > 0), 'os inimigos do Arraial são galinhas caipiras, não pombos');

  // aula do planar: cair no primeiro vão (antes de aprender) volta para a beirada sem perder coração
  await put(1400, 300, { vy: 200 });
  check(await until(() => __tintim.player.x < TT.C.GLIDE_TUT.edge && __tintim.player.hp === 3 && __tintim.S.tut.tries >= 1, 6000), 'cair no primeiro vão durante a aula do planar não tira coração');
  await ev(() => { __tintim.S.tut.learned = true; __tintim.S.slowT = 0; });
  // planar: no ar, segurando o pulo, a queda fica lenta
  await put(1300, 100); await pg.keyboard.down('Space'); await pg.waitForTimeout(700);
  const g = await ev(() => ({ vy: __tintim.player.vy, gl: __tintim.player.gliding }));
  check(g.gl && g.vy > 0 && g.vy < 160, `planando, a queda fica lenta (vy=${g.vy.toFixed(0)})`);
  await pg.keyboard.up('Space'); await pg.waitForTimeout(300);
  check(await ev(() => !__tintim.player.gliding && __tintim.player.vy > 300), 'soltando o pulo, ele volta a cair normal');

  // ar quente: planando em cima da fogueira, ele sobe
  const fx = await ev(() => TT.C.fires[0].x);
  await put(fx - 27, 250, { vy: 50 }); await pg.keyboard.down('Space'); await pg.waitForTimeout(150);
  const y0 = await ev(() => __tintim.player.y); await pg.waitForTimeout(900); const y1 = await ev(() => __tintim.player.y);
  check(y1 < y0 - 60, `o ar quente da fogueira levanta quem plana (subiu ${(y0 - y1).toFixed(0)} px)`);
  await pg.keyboard.up('Space');
  // planada sem piscar: segurando o pulo dentro da coluna de ar quente por 2,5 s, ela nunca se desliga no ar
  const f0 = await ev(() => TT.C.fires[0].x);
  await ev(f0 => { const S = __tintim.S; S.arena = false; S.mode = 'play'; S.cine = null; S.fireOff = 0; Object.assign(__tintim.player, { x: f0 - 27, y: 300, vx: 0, vy: 0, onGround: false, inv: 99, hp: 3, noGlide: 0, djT: 0, hurtT: 0, dj: false }); }, f0); // sem pirueta guardada: o aperto no ar vai direto para a planada
  await pg.keyboard.down('Space');
  await ev(() => { window.__gl = []; const t0 = performance.now(); const f = () => { const p = __tintim.player; if (!p.onGround) __gl.push(p.gliding ? (__tintim.R.tintimMesh.userData.name === 'timtim-pulo' ? 1 : 2) : 0); if (performance.now() - t0 < 2500) requestAnimationFrame(f); }; requestAnimationFrame(f); });
  await pg.waitForTimeout(2700); await pg.keyboard.up('Space');
  const gl = await ev(() => __gl), drops = gl.slice(5).filter(v => !v).length;
  check(gl.length > 30 && drops === 0, `planando na coluna de ar quente a planada não pisca (${drops} quadros sem planar)`);
  check(gl.length > 30 && gl.every(v => v !== 2), 'planando, o Timtim usa o próprio desenho do pulo (não troca de figura)');
  // pisar numa galinha do Arraial faz quicar e ela foge; não morre
  const hen2 = await ev(() => { const e = __tintim.S.enemies.find(e => e.alive); return e && { x: e.x, y: e.y, w: e.w }; });
  if (hen2) { await ev(h => { const e = __tintim.S.enemies.find(e => e.alive); Object.assign(__tintim.player, { x: e.x + e.w / 2 - 27, y: e.y - 52, vx: 0, vy: 300, onGround: false, inv: 0, hp: 3, mega: 0 }); }, hen2);
    await pg.waitForTimeout(250);
    check(await ev(() => __tintim.S.enemies.every(e => e.alive) && __tintim.player.hp === 3), 'pisar numa galinha faz o Timtim quicar: ela foge e não morre' + (process.env.DBG ? await ev(() => JSON.stringify([__tintim.S.enemies.map(e => [e.alive, Math.round(e.x), Math.round(e.y)]), __tintim.player.hp, Math.round(__tintim.player.y), __tintim.player.vy])) : '')); }

  // a Zara não anda no ar: com o Timtim do outro lado do buraco, ela para na beirada
  await ev(() => { const f = __tintim.S.friends[0]; f.x = 4440; f.given = false; f.follow = 0; Object.assign(__tintim.player, { x: 4700, y: 60, vx: 0, vy: 0, onGround: false, inv: 99, hp: 3 }); });
  await ev(() => { window.__fx = 0; const t0 = performance.now(); const f = () => { __fx = Math.max(__fx, __tintim.S.friends[0].x); if (performance.now() - t0 < 700) requestAnimationFrame(f); }; requestAnimationFrame(f); });
  await pg.waitForTimeout(800);
  check(await ev(() => __fx <= 4500), `os amigos param na beirada do buraco (foi até ${Math.round(await ev(() => __fx))}, o chão acaba em 4500)`);

  // a chama não machuca: é ali que ele pula para subir no ar quente
  await put(fx - 27, 452 - 50, { onGround: true }); await pg.waitForTimeout(250);
  check(await ev(() => __tintim.player.hp === 3), 'encostar na fogueira não tira coração (ela é o trampolim do planar)');
  await until(() => __tintim.player.onGround, 3000);

  // tábuas da quadrilha se movem e levam o Timtim junto
  const m = await ev(() => { const s = TT.MOVERS[0]; return { x: s.x, y: s.y, w: s.w }; });
  // a tábua anda enquanto ele cai: põe o Timtim em cima dela na posição atual e espera ele estar mesmo apoiado nela.
  // Começa com a tábua perto do meio do caminho (andando rápido): perto das pontas ela quase para e 0,5 s não basta para medir
  await until(() => Math.abs(TT.MOVERS[0].x - TT.C.movers[0].x) < 45, 6000);
  await ev(() => { const s = TT.MOVERS[0], p = __tintim.player; Object.assign(p, { x: s.x + s.w / 2 - p.w / 2, y: s.y - p.h - 1, vx: 0, vy: 0, inv: 9, hp: 3, onGround: false }); });
  await until(() => __tintim.player.onGround && __tintim.player.on && !!__tintim.player.on.mover, 2000);
  const a0 = await ev(() => ({ px: __tintim.player.x, sx: TT.MOVERS[0].x })); await pg.waitForTimeout(500);
  const a1 = await ev(() => ({ px: __tintim.player.x, sx: TT.MOVERS[0].x, on: __tintim.player.onGround }));
  check(Math.abs(a1.sx - a0.sx) > 10 && a1.on && Math.abs((a1.px - a0.px) - (a1.sx - a0.sx)) < 4, 'a tábua da quadrilha anda e leva o Timtim junto' + (process.env.DBG ? JSON.stringify([a0, a1]) : ''));

  // faro: perto da terceira fogueira revela o caminho de cheiro até a sanfoninha
  const t = await ev(() => TT.C.trails[0].at);
  await put(t - 120, 452 - 50, { onGround: true, inv: 9 }); await until(() => __tintim.player.onGround, 2000);
  await pg.keyboard.down('ArrowDown'); check(await until(() => __tintim.S.revealed.sanfona, 3000), 'farejar perto da fogueira revela o caminho de cheiro'); await pg.keyboard.up('ArrowDown');
  await ev(() => { const it = __tintim.S.items.find(i => i.type === 'toy'), p = __tintim.player; p.x = it.x - 27; p.y = it.y - 25; p.vy = 0; });
  check(await until(() => __tintim.S.toy, 3000), 'pega a sanfoninha');
  check(await ev(() => JSON.parse(localStorage.getItem('tintim-toys') || '{}').sanfoninha === true), 'a sanfoninha fica salva na estante');

  // a Zara e o Elvis jogam ovo cozido: o primeiro dá o planar turbinado (queda bem mais lenta)
  check(await ev(() => TT.C.GIFT_ITEM === 'ovo' && TT.C.friends[0].power === 'egg'), 'no Arraial os amigos jogam ovo cozido');
  const fr = await ev(() => TT.C.friends[0].x);
  await put(fr - 260, 452 - 50, { onGround: true, inv: 9 }); await pg.keyboard.down('ArrowRight');
  check(await until(() => __tintim.player.egg > 0, 6000), 'pegar o ovo cozido dá o planar turbinado'); await pg.keyboard.up('ArrowRight');
  await put(fr, 60, { inv: 9 }); await pg.keyboard.down('Space'); await pg.waitForTimeout(700);
  const ge = await ev(() => ({ vy: __tintim.player.vy, gl: __tintim.player.gliding })); await pg.keyboard.up('Space');
  check(ge.gl && ge.vy > 0 && ge.vy <= 75, `com o ovo, a queda planando fica bem mais lenta (vy=${ge.vy.toFixed(0)})`);

  // galinha agitada: com o Timtim chegando perto, ela foge cacarejando
  const hen = await ev(() => { const i = __tintim.S.enemies.findIndex(e => e.alive && e.b - e.a > 200); const e = __tintim.S.enemies[i]; e.x = (e.a + e.b) / 2; return { i, x: e.x }; });
  await put(hen.x + 150, 452 - 50, { onGround: true, inv: 9 }); await pg.waitForTimeout(150);
  const scared = await ev(i => __tintim.S.enemies[i].scared, hen.i); await pg.waitForTimeout(250);
  const h1 = await ev(i => ({ x: __tintim.S.enemies[i].x }), hen.i);
  check(scared && h1.x < hen.x - 30, `a galinha fica agitada e foge quando o Timtim chega perto (andou ${(hen.x - h1.x).toFixed(0)} px)`);

  // brincadeiras juninas: pular dentro do tanque da pescaria solta biscoitos; atravessar a argola revela o dourado
  const tub = await ev(() => TT.C.TUB.x);
  await put(tub - 27, 340, { inv: 9 });
  check(await until(() => __tintim.S.revealed.pescaria, 3000), 'cair dentro do tanque da pescaria solta os biscoitos escondidos');
  const hp = await ev(() => TT.C.HOOP);
  await put(hp.x - 27, hp.y - 25, { inv: 9 });
  check(await until(() => __tintim.S.revealed.argola, 2000), 'passar pela argola revela o biscoito dourado');
  // correio elegante: pegar um bilhete abre a piada na tela
  const n0 = await ev(() => TT.C.NOTES[0]);
  await put(n0.x - 27, n0.y - 25, { inv: 9 });
  check(await until(() => __tintim.S.notes === 1 && document.getElementById('note').classList.contains('on'), 3000), 'pegar o bilhete do correio elegante mostra a piada');

  // galinhas em debandada: aviso de poeira, depois o bando corre da direita para a esquerda; encostar de lado machuca
  const st0 = await ev(() => TT.C.STAMPEDES.find(s => s.n === 4).at);
  await ev(() => { __tintim.S.runDone = {}; __tintim.S.runners = []; });
  await put(st0 + 20, 452 - 50, { onGround: true, inv: 9 });
  check(await until(() => !!__tintim.S.warn, 2000), 'passar do ponto da debandada levanta a poeira de aviso');
  check(await until(() => __tintim.S.runners.filter(r => r.kind === 'run').length === 4, 3000), 'depois do aviso, um bando de 4 galinhas aparece correndo');
  const r0 = await ev(() => __tintim.S.runners[0].x); await pg.waitForTimeout(200);
  check(await ev(x => __tintim.S.runners[0].x < x - 40, r0), 'as galinhas da debandada correm da direita para a esquerda');
  await ev(() => { const r = __tintim.S.runners[0], p = __tintim.player; Object.assign(p, { x: r.x - 70, y: 452 - p.h, vx: 0, vy: 0, onGround: true, inv: 0, hp: 3, mega: 0 }); });
  check(await until(() => __tintim.player.hp < 3, 2000), 'encostar de lado numa galinha da debandada tira um coração');
  await ev(() => { __tintim.player.inv = 9; __tintim.player.hp = 3; });

  // antes da luta, o lobo-guará está caçando galinhas no galinheiro; quando o Timtim chega, elas fogem para a esquerda
  const ax0 = await ev(() => TT.C.ARENA_X);
  await ev(() => { __tintim.S.chaseOn = false; __tintim.S.runners = []; }); await put(ax0 - 600, 452 - 50, { onGround: true, inv: 99 });
  check(await until(() => __tintim.S.chaseOn && __tintim.S.fox.state === 'chase' && __tintim.S.runners.filter(r => r.kind === 'arena').length === 3, 2000), 'chegando perto do fim, o lobo-guará aparece caçando três galinhas');
  // o lobo-guará: chegar na arena começa a luta com a apresentação dele
  const ax = ax0;
  await put(ax + 200, 452 - 50, { onGround: true, inv: 99 });
  check(await until(() => __tintim.S.arena && __tintim.S.cine && __tintim.S.cine.type === 'fox', 3000), 'chegar no fim do Arraial apresenta o lobo-guará');
  check(await ev(() => __tintim.S.runners.filter(r => r.kind === 'flee').length === 3 && __tintim.S.runners.every(r => r.kind !== 'flee' || r.vx < 0)), 'na apresentação, as galinhas caçadas fogem para a esquerda');
  check(await until(() => !__tintim.S.cine, 6000), 'depois da apresentação, a luta começa');
  await pg.waitForTimeout(400);
  check(await ev(() => { const m = __tintim.R.dbg.fox(), o = m.material.map.offset; return m.visible && Number.isFinite(o.x) && Number.isFinite(o.y) && Number.isFinite(m.userData.ph); }), 'depois da apresentação o lobo-guará continua desenhado (quadro da animação válido)');
  // pulo comum ela esquiva; caindo planando em cima dela, acerta
  const above = () => ev(() => { const f = __tintim.S.fox, p = __tintim.player; f.x = TT.C.ARENA_X + 400; f.y = TT.C.GROUND - f.h; f.vy = 0; f.state = 'idle'; f.t = 0; f.cd = 9; f.vx = 0; f.egg = 99; __tintim.S.fruit = null; Object.assign(p, { x: f.x + f.w / 2 - p.w / 2, y: f.y - p.h - 40, vx: 0, vy: 200, onGround: false, inv: 99, hp: 3, dj: false, buffer: 0, coyote: 0 }); });
  await above();
  check(await until(() => __tintim.S.fox.state === 'dodge', 2000) && await ev(() => __tintim.S.fox.hp === 3), 'pulo comum em cima do lobo-guará: ele esquiva e não perde vida');
  // o latido rouco apaga o ar quente e derruba quem está planando
  await ev(() => { const f = __tintim.S.fox, p = __tintim.player; f.egg = 99; __tintim.S.fruit = null; f.state = 'wind'; f.atk = 'roar'; f.t = 5; Object.assign(p, { x: TT.C.ARENA_X + 100, y: 200, vx: 0, vy: 50, onGround: false, inv: 99 }); TT.input.jump = true; }); // planando perto dele
  check(await until(() => __tintim.S.fox.state === 'roar' && __tintim.S.fireOff > 0 && __tintim.player.noGlide > 0, 2000), 'o latido do lobo-guará apaga o ar quente das fogueiras e derruba quem plana');
  await ev(() => { TT.input.jump = false; });
  await until(() => __tintim.player.onGround && __tintim.S.fox.state !== 'roar', 4000);
  // fruta-do-lobo: ele para para comer, de lombo baixo, e até o pulo comum acerta
  await ev(() => { const f = __tintim.S.fox; f.x = TT.C.ARENA_X + 400; f.state = 'idle'; f.cd = 9; f.egg = 99; __tintim.S.fruit = { x: TT.C.ARENA_X + 560, y: TT.C.GROUND - 22, vx: 0, vy: 0, rest: true }; });
  check(await until(() => __tintim.S.fox.state === 'eat' && !__tintim.S.fruit, 3000), 'o lobo-guará corre até a fruta-do-lobo e para para comer');
  await ev(() => { const f = __tintim.S.fox, p = __tintim.player; Object.assign(p, { x: f.x + f.w / 2 - p.w / 2, y: f.y - p.h - 40, vx: 0, vy: 200, onGround: false, inv: 99, hp: 3, dj: false, buffer: 0, coyote: 0 }); });
  check(await until(() => __tintim.S.fox.hp === 2, 2000), 'comendo a fruta, um pulo comum na crina acerta');
  for (let k = 1; k < 3; k++) {
    await until(() => ['idle', 'dodge', 'hurt'].includes(__tintim.S.fox.state) && __tintim.S.fox.state !== 'hurt' && __tintim.player.onGround, 4000);
    await above(); await pg.keyboard.down('Space'); await pg.waitForFunction(n => __tintim.S.fox.hp === n, 2 - k, { timeout: 3000, polling: 50 }).catch(() => {}); await pg.keyboard.up('Space');
  }
  check(await ev(() => __tintim.S.fox.hp === 0), 'mais duas quedas planando na crina derrotam o lobo-guará');
  check(await ev(() => __tintim.S.runners.filter(r => r.kind === 'chaser' && r.vx > 0).length === 5), 'no golpe final, as galinhas saem do galinheiro e correm atrás dele');
  check(await until(() => __tintim.state === 'winning' || __tintim.state === 'win', 3000), 'derrotar o lobo-guará vence a fase');
  check(await until(() => document.getElementById('win').classList.contains('on'), 9000), 'tela de vitória aparece');
  check(await ev(() => document.getElementById('winTitle').textContent.includes('Galinheiro') && document.getElementById('stNotes').textContent.includes('1/4')), 'vitória com o texto do galinheiro e a contagem do correio elegante');
  check(await ev(() => JSON.parse(localStorage.getItem('tintim-fases') || '{}')[2] === true), 'fase 2 fica marcada como vencida');
  // entre as fases: o mapa abre, o Timtim anda pelo caminho até a fase 3 e ela começa sozinha
  await pg.waitForTimeout(2200); await pg.click('#btnNext');
  check(await until(() => TT.mapa.isOpen() && TT.mapa.state().walking, 3000), 'Próxima fase abre o mapa e o Timtim anda até a fase seguinte');
  check(await pg.waitForURL(/fase3/, { timeout: 15000 }).then(() => true, () => false), 'chegando na placa, a fase 3 carrega');
  check(await until(() => window.TT && TT.FASE === 3 && window.__tintim && __tintim.state === 'play', 20000), 'a fase 3 começa direto, sem a tela de título');
  check(errs.length === 0, 'sem erros no console' + (errs.length ? ': ' + errs.slice(0, 3).join(' | ') : ''));
  await b.close();
})();
