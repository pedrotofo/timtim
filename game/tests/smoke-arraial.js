// Teste de fumaça da fase 2 (o Arraial): planar, ar quente da fogueira, chama que machuca, tábuas da quadrilha,
// faro revelando o caminho até a sanfoninha, galinhas agitadas, brincadeiras juninas e a luta com o lobo-guará. Mesmo esquema do smoke.js: espera por condições.
// Uso: (cd game && python3 -m http.server 8765 &) ; node game/tests/smoke-arraial.js [url]
const { chromium } = require('playwright');
(async () => {
  const url = (process.argv[2] || 'http://localhost:8765/') + '?fase=2&q=0';
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'] });
  const pg = await b.newPage({ viewport: { width: 960, height: 540 } });
  const errs = []; pg.on('pageerror', e => errs.push(e.message)); pg.on('console', m => m.type() === 'error' && errs.push(m.text()));
  pg.on('requestfailed', r => errs.push('falhou: ' + r.url()));
  const ev = (f, a) => pg.evaluate(f, a);
  const until = (f, ms = 20000, a = null) => pg.waitForFunction(f, a, { timeout: ms, polling: 50 }).then(() => true, () => false);
  const check = (ok, msg) => { console.log((ok ? 'ok   ' : 'FALHA') + ' ' + msg); if (!ok) process.exitCode = 1; };
  // O relógio do jogo anda mais devagar que o relógio de parede: main.js:32 corta o quadro em 0,033 s e o laço de
  // passo fixo dá no máximo 10 passos de 1/240 s por quadro (main.js:37). Com WebGL por software medimos 0,58x do
  // tempo real em janelas curtas, e o quanto muda com a máquina. Então nenhuma espera de parede serve para MEDIR
  // movimento do jogo:
  //   - movimento com resultado visível -> until(condição)
  //   - "nada de ruim aconteceu"        -> jogo(s), que espera s segundos DE JOGO (S.clock)
  //   - entrada do jogador, animação da interface e amostragem por rAF -> waitForTimeout, que é de parede mesmo
  // Prazo de um until é orçamento de parede para um evento DE JOGO acontecer, então tem de ser generoso: um prazo
  // folgado nunca esconde regressão (a condição ainda precisa virar verdade), só deixa a falha demorar mais.
  const CINE = 20000; // fim de cinemática é o caso mais longo: 3,2 s de jogo, que a 0,58x já viram 5,5 s reais
  const jogo = async (s, ms = 20000) => { const t0 = await ev(() => __tintim.S.clock); return until(t => __tintim.S.clock >= t, ms, t0 + s); };
  const put = (x, y, extra) => ev(([x, y, extra]) => { const p = __tintim.player; Object.assign(p, { x, y, vx: 0, vy: 0, onGround: false, inv: 0, hp: 3 }, extra || {}); }, [x, y, extra]);
  await pg.goto(url);
  check(await until(() => window.__tintim && __tintim.R.ready && __tintim.state === 'title'), 'abre o título na fase 2');
  check(await ev(() => document.querySelector('.logo img').alt === 'Timtim e os Brinquedos Perdidos' && document.querySelector('.logo img').naturalWidth > 0), 'a capa é a mesma do jogo todo');
  await pg.waitForTimeout(500); await pg.click('#btnStart'); // de parede: animação da capa (CSS/setTimeout)
  check(await until(() => TT.mapa.isOpen() && document.querySelector('#mapa canvas'), CINE), 'Jogar abre o mapa das fases');
  await pg.waitForTimeout(400); await pg.keyboard.press('Enter'); // de parede: o mapa tem laço de rAF próprio em performance.now() (mapa.js)
  check(await until(() => __tintim.storyScene === 1 && document.getElementById('storyLine').textContent.includes('galinhas do arraial'), CINE), 'antes da fase, o card do Arraial (alguém assustando as galinhas)');
  await pg.waitForTimeout(900); await pg.keyboard.press('Space'); // de parede: nextStory() só aceita o toque 800 ms depois, contados em performance.now() (ui.js)
  check(await until(() => __tintim.state === 'play' && __tintim.S.cine && __tintim.S.cine.type === 'arraial', CINE), 'depois do card, a fase começa com o cartão do Arraial');
  check(await until(() => !__tintim.S.cine, CINE), 'cartão some e o controle é liberado');
  check(await ev(() => !__tintim.S.thief && !__tintim.S.arena), 'sem Furtão nem chefão no Arraial');
  check(await ev(() => __tintim.R.foe === 'galinha' && __tintim.S.enemies.length > 0), 'os inimigos do Arraial são galinhas caipiras, não pombos');

  // aula do planar: cair no primeiro vão (antes de aprender) volta para a beirada sem perder coração
  await put(1400, 300, { vy: 200 });
  check(await until(() => __tintim.player.x < TT.C.GLIDE_TUT.edge && __tintim.player.hp === 3 && __tintim.S.tut.tries >= 1, CINE), 'cair no primeiro vão durante a aula do planar não tira coração');
  await ev(() => { __tintim.S.tut.learned = true; __tintim.S.slowT = 0; });
  // planar: no ar, segurando o pulo, a queda fica lenta
  await put(1300, 100); await pg.keyboard.down('Space');
  const andou07 = await jogo(0.7); // tempo DE JOGO: a queda planando leva ~0,25 s de jogo para encostar no teto de 135 px/s (game.js:590)
  const g = await ev(() => ({ vy: __tintim.player.vy, gl: __tintim.player.gliding }));
  check(andou07 && g.gl && g.vy > 0 && g.vy < 160, `planando, a queda fica lenta (vy=${g.vy.toFixed(0)})`);
  await pg.keyboard.up('Space');
  check(await until(() => !__tintim.player.gliding && __tintim.player.vy > 300, CINE), 'soltando o pulo, ele volta a cair normal'); // condição, não 300 ms de parede

  // ar quente: planando em cima da fogueira, ele sobe
  const fx = await ev(() => TT.C.fires[0].x);
  await put(fx - 27, 250, { vy: 50 }); await pg.keyboard.down('Space');
  const planou = await until(() => __tintim.player.gliding, CINE);
  const y0 = await ev(() => __tintim.player.y);
  const subiu = await until(y => __tintim.player.y < y, CINE, y0 - 60); // condição, não 900 ms de parede: espera subir 60 px de verdade
  const y1 = await ev(() => __tintim.player.y);
  check(planou && subiu, `o ar quente da fogueira levanta quem plana (subiu ${(y0 - y1).toFixed(0)} px)`);
  await pg.keyboard.up('Space');
  // planada sem piscar: segurando o pulo dentro da coluna de ar quente por 2,5 s, ela nunca se desliga no ar
  const f0 = await ev(() => TT.C.fires[0].x);
  await ev(f0 => { const S = __tintim.S; S.arena = false; S.mode = 'play'; S.cine = null; S.fireOff = 0; Object.assign(__tintim.player, { x: f0 - 27, y: 300, vx: 0, vy: 0, onGround: false, inv: 99, hp: 3, noGlide: 0, djT: 0, hurtT: 0, dj: false }); }, f0); // sem pirueta guardada: o aperto no ar vai direto para a planada
  await pg.keyboard.down('Space');
  await ev(() => { window.__gl = []; const t0 = performance.now(); const f = () => { const p = __tintim.player; if (!p.onGround) __gl.push(p.gliding ? (__tintim.R.tintimMesh.userData.name === 'timtim-pulo' ? 1 : 2) : 0); if (performance.now() - t0 < 2500) requestAnimationFrame(f); }; requestAnimationFrame(f); });
  await pg.waitForTimeout(2700); await pg.keyboard.up('Space'); // de parede: o amostrador acima se mede em performance.now()
  const gl = await ev(() => __gl), drops = gl.slice(5).filter(v => !v).length;
  check(gl.length > 30 && drops === 0, `planando na coluna de ar quente a planada não pisca (${drops} quadros sem planar)`);
  check(gl.length > 30 && gl.every(v => v !== 2), 'planando, o Timtim usa o próprio desenho do pulo (não troca de figura)');
  // pisar numa galinha do Arraial faz quicar e ela foge; não morre
  const hen2 = await ev(() => { const e = __tintim.S.enemies.find(e => e.alive); return e && { x: e.x, y: e.y, w: e.w }; });
  if (hen2) { await ev(h => { const e = __tintim.S.enemies.find(e => e.alive); Object.assign(__tintim.player, { x: e.x + e.w / 2 - 27, y: e.y - 52, vx: 0, vy: 300, onGround: false, inv: 0, hp: 3, mega: 0 }); }, hen2);
    const quicou = await until(() => __tintim.player.vy < 0, CINE); // condição, não 250 ms de parede: o pisão joga o Timtim para cima (vy = -560, game.js:716)
    check(quicou && await ev(() => __tintim.S.enemies.every(e => e.alive) && __tintim.player.hp === 3), 'pisar numa galinha faz o Timtim quicar: ela foge e não morre' + (process.env.DBG ? await ev(() => JSON.stringify([__tintim.S.enemies.map(e => [e.alive, Math.round(e.x), Math.round(e.y)]), __tintim.player.hp, Math.round(__tintim.player.y), __tintim.player.vy])) : '')); }

  // a Zara não anda no ar: com o Timtim do outro lado do buraco, ela para na beirada
  await ev(() => { const f = __tintim.S.friends[0]; f.x = 4440; f.given = false; f.follow = 0; Object.assign(__tintim.player, { x: 4700, y: 60, vx: 0, vy: 0, onGround: false, inv: 99, hp: 3 }); });
  await ev(() => { window.__fx = 0; const t0 = performance.now(); const f = () => { __fx = Math.max(__fx, __tintim.S.friends[0].x); if (performance.now() - t0 < 700) requestAnimationFrame(f); }; requestAnimationFrame(f); });
  await pg.waitForTimeout(800); // de parede: o amostrador acima se mede em performance.now()
  check(await ev(() => __fx <= 4500), `os amigos param na beirada do buraco (foi até ${Math.round(await ev(() => __fx))}, o chão acaba em 4500)`);

  // a chama não machuca: é ali que ele pula para subir no ar quente
  await put(fx - 27, 452 - 50, { onGround: true });
  const naFogueira = await until(() => __tintim.player.onGround, CINE); // de pé na fogueira: era um until descartado
  const encostou = await jogo(0.3); // afirmação negativa (nada aconteceu): espera tempo DE JOGO encostado nela
  check(naFogueira && encostou && await ev(() => __tintim.player.hp === 3), 'encostar na fogueira não tira coração (ela é o trampolim do planar)');

  // tábuas da quadrilha se movem e levam o Timtim junto
  // a tábua anda enquanto ele cai: põe o Timtim em cima dela na posição atual e espera ele estar mesmo apoiado nela.
  // Começa com a tábua perto do meio do caminho, onde ela anda rápido: perto das pontas ela quase para.
  const noMeio = await until(() => Math.abs(TT.MOVERS[0].x - TT.C.movers[0].x) < 45, CINE);
  await ev(() => { const s = TT.MOVERS[0], p = __tintim.player; Object.assign(p, { x: s.x + s.w / 2 - p.w / 2, y: s.y - p.h - 1, vx: 0, vy: 0, inv: 9, hp: 3, onGround: false }); });
  const apoiado = await until(() => __tintim.player.onGround && __tintim.player.on && !!__tintim.player.on.mover, CINE);
  const a0 = await ev(() => ({ px: __tintim.player.x, sx: TT.MOVERS[0].x }));
  const andou = await until(s => Math.abs(TT.MOVERS[0].x - s) > 25, CINE, a0.sx); // condição, não 500 ms de parede: espera a tábua ter andado 25 px
  const a1 = await ev(() => ({ px: __tintim.player.x, sx: TT.MOVERS[0].x, on: __tintim.player.onGround }));
  check(noMeio && apoiado && andou && a1.on && Math.abs((a1.px - a0.px) - (a1.sx - a0.sx)) < 4, 'a tábua da quadrilha anda e leva o Timtim junto' + (process.env.DBG ? JSON.stringify([a0, a1]) : ''));

  // faro: perto da terceira fogueira revela o caminho de cheiro até a sanfoninha
  const t = await ev(() => TT.C.trails[0].at);
  await put(t - 120, 452 - 50, { onGround: true, inv: 9 });
  const dePe = await until(() => __tintim.player.onGround, CINE); // o faro só funciona no chão: era um until descartado
  await pg.keyboard.down('ArrowDown'); check(dePe && await until(() => __tintim.S.revealed.sanfona, CINE), 'farejar perto da fogueira revela o caminho de cheiro'); await pg.keyboard.up('ArrowDown');
  await ev(() => { const it = __tintim.S.items.find(i => i.type === 'toy'), p = __tintim.player; p.x = it.x - 27; p.y = it.y - 25; p.vy = 0; });
  check(await until(() => __tintim.S.toy, CINE), 'pega a sanfoninha');
  check(await ev(() => JSON.parse(localStorage.getItem('tintim-toys') || '{}').sanfoninha === true), 'a sanfoninha fica salva na estante');

  // a Zara e o Elvis jogam ovo cozido: o primeiro dá o planar turbinado (queda bem mais lenta)
  check(await ev(() => TT.C.GIFT_ITEM === 'ovo' && TT.C.friends[0].power === 'egg'), 'no Arraial os amigos jogam ovo cozido');
  const fr = await ev(() => TT.C.friends[0].x);
  await put(fr - 260, 452 - 50, { onGround: true, inv: 9 }); await pg.keyboard.down('ArrowRight');
  check(await until(() => __tintim.player.egg > 0, CINE), 'pegar o ovo cozido dá o planar turbinado'); await pg.keyboard.up('ArrowRight');
  await put(fr, 60, { inv: 9 }); await pg.keyboard.down('Space');
  const andouOvo = await jogo(0.7); // tempo DE JOGO: com o ovo o teto da queda é 70 px/s (C.EGG.fall, game.js:590)
  const ge = await ev(() => ({ vy: __tintim.player.vy, gl: __tintim.player.gliding })); await pg.keyboard.up('Space');
  check(andouOvo && ge.gl && ge.vy > 0 && ge.vy <= 75, `com o ovo, a queda planando fica bem mais lenta (vy=${ge.vy.toFixed(0)})`);

  // galinha agitada: com o Timtim chegando perto, ela foge cacarejando
  const hen = await ev(() => { const i = __tintim.S.enemies.findIndex(e => e.alive && e.b - e.a > 200); const e = __tintim.S.enemies[i]; e.x = (e.a + e.b) / 2; return { i, x: e.x }; });
  await put(hen.x + 150, 452 - 50, { onGround: true, inv: 9 });
  const scared = await until(i => __tintim.S.enemies[i].scared, CINE, hen.i); // condição, não 150 ms de parede
  const fugiu = await until(a => __tintim.S.enemies[a.i].x < a.x, CINE, { i: hen.i, x: hen.x - 30 }); // condição, não 250 ms de parede: espera andar 30 px
  const h1 = await ev(i => ({ x: __tintim.S.enemies[i].x }), hen.i);
  check(scared && fugiu, `a galinha fica agitada e foge quando o Timtim chega perto (andou ${(hen.x - h1.x).toFixed(0)} px)`);

  // brincadeiras juninas: pular dentro do tanque da pescaria solta biscoitos; atravessar a argola revela o dourado
  const tub = await ev(() => TT.C.TUB.x);
  await put(tub - 27, 340, { inv: 9 });
  check(await until(() => __tintim.S.revealed.pescaria, CINE), 'cair dentro do tanque da pescaria solta os biscoitos escondidos');
  const hp = await ev(() => TT.C.HOOP);
  await put(hp.x - 27, hp.y - 25, { inv: 9 });
  check(await until(() => __tintim.S.revealed.argola, CINE), 'passar pela argola revela o biscoito dourado');
  // correio elegante: pegar um bilhete abre a piada na tela
  const n0 = await ev(() => TT.C.NOTES[0]);
  await put(n0.x - 27, n0.y - 25, { inv: 9 });
  check(await until(() => __tintim.S.notes === 1 && document.getElementById('note').classList.contains('on'), CINE), 'pegar o bilhete da turma mostra a piada');

  // galinhas em debandada: aviso de poeira, depois o bando corre da direita para a esquerda; encostar de lado machuca
  const st0 = await ev(() => TT.C.STAMPEDES.find(s => s.n === 4).at);
  await ev(() => { __tintim.S.runDone = {}; __tintim.S.runners = []; });
  await put(st0 + 20, 452 - 50, { onGround: true, inv: 9 });
  check(await until(() => !!__tintim.S.warn, CINE), 'passar do ponto da debandada levanta a poeira de aviso');
  check(await until(() => __tintim.S.runners.filter(r => r.kind === 'run').length === 4, CINE), 'depois do aviso, um bando de 4 galinhas aparece correndo');
  const r0 = await ev(() => __tintim.S.runners[0].x);
  check(await until(x => __tintim.S.runners[0].x < x, CINE, r0 - 40), 'as galinhas da debandada correm da direita para a esquerda'); // condição, não 200 ms de parede
  await ev(() => { const r = __tintim.S.runners[0], p = __tintim.player; Object.assign(p, { x: r.x - 70, y: 452 - p.h, vx: 0, vy: 0, onGround: true, inv: 0, hp: 3, mega: 0 }); });
  check(await until(() => __tintim.player.hp < 3, CINE), 'encostar de lado numa galinha da debandada tira um coração');
  await ev(() => { __tintim.player.inv = 9; __tintim.player.hp = 3; });

  // antes da luta, o lobo-guará está caçando galinhas no galinheiro; quando o Timtim chega, elas fogem para a esquerda
  const ax0 = await ev(() => TT.C.ARENA_X);
  await ev(() => { __tintim.S.chaseOn = false; __tintim.S.runners = []; }); await put(ax0 - 600, 452 - 50, { onGround: true, inv: 99 });
  check(await until(() => __tintim.S.chaseOn && __tintim.S.fox.state === 'chase' && __tintim.S.runners.filter(r => r.kind === 'arena').length === 3, CINE), 'chegando perto do fim, o lobo-guará aparece caçando três galinhas');
  // o lobo-guará: chegar na arena começa a luta com a apresentação dele
  const ax = ax0;
  await ev(ax => { __tintim.S.fox.x = ax + 160; }, ax); // o pior caso: ele caçando bem na entrada da arena
  await put(ax + 200, 452 - 50, { onGround: true, inv: 99 });
  check(await until(() => __tintim.S.arena && __tintim.S.cine && __tintim.S.cine.type === 'fox', CINE), 'chegar no fim do Arraial apresenta o lobo-guará');
  check(await ev(() => __tintim.S.runners.filter(r => r.kind === 'flee').length === 3 && __tintim.S.runners.every(r => r.kind !== 'flee' || r.vx < 0)), 'na apresentação, as galinhas caçadas fogem para a esquerda');
  check(await until(() => !__tintim.S.cine, CINE), 'depois da apresentação, a luta começa');
  check(await ev(() => { const f = __tintim.S.fox, p = __tintim.player; return (f.x + f.w / 2) - (p.x + p.w / 2) > 280; }), 'na apresentação o lobo-guará se afasta: a luta não começa com o Timtim colado nele');
  const passou04 = await jogo(0.4); // afirmação negativa: alguns quadros DE JOGO depois da cinemática, não 400 ms de parede
  check(passou04 && await ev(() => { const m = __tintim.R.dbg.fox(), o = m.material.map.offset; return m.visible && Number.isFinite(o.x) && Number.isFinite(o.y) && Number.isFinite(m.userData.ph); }), 'depois da apresentação o lobo-guará continua desenhado (quadro da animação válido)');
  // pulo comum ela esquiva; caindo planando em cima dela, acerta
  const above = () => ev(() => { const f = __tintim.S.fox, p = __tintim.player; f.x = TT.C.ARENA_X + 400; f.y = TT.C.GROUND - f.h; f.vy = 0; f.state = 'idle'; f.t = 0; f.cd = 9; f.vx = 0; f.egg = 99; __tintim.S.fruit = null; Object.assign(p, { x: f.x + f.w / 2 - p.w / 2, y: f.y - p.h - 40, vx: 0, vy: 200, onGround: false, inv: 99, hp: 3, dj: false, buffer: 0, coyote: 0 }); });
  await above();
  check(await until(() => __tintim.S.fox.state === 'dodge', CINE) && await ev(() => __tintim.S.fox.hp === 3), 'pulo comum em cima do lobo-guará: ele esquiva e não perde vida');
  // o latido rouco apaga o ar quente e derruba quem está planando
  await ev(() => { const f = __tintim.S.fox, p = __tintim.player; f.egg = 99; __tintim.S.fruit = null; f.state = 'wind'; f.atk = 'roar'; f.t = 5; Object.assign(p, { x: TT.C.ARENA_X + 100, y: 200, vx: 0, vy: 50, onGround: false, inv: 99 }); TT.input.jump = true; }); // planando perto dele
  check(await until(() => __tintim.S.fox.state === 'roar' && __tintim.S.fireOff > 0 && __tintim.player.noGlide > 0, CINE), 'o latido do lobo-guará apaga o ar quente das fogueiras e derruba quem plana');
  await ev(() => { TT.input.jump = false; });
  const assentou = await until(() => __tintim.player.onGround && __tintim.S.fox.state !== 'roar', CINE); // era um until descartado
  // fruta-do-lobo: ele para para comer, de lombo baixo, e até o pulo comum acerta
  await ev(() => { const f = __tintim.S.fox; f.x = TT.C.ARENA_X + 400; f.state = 'idle'; f.cd = 9; f.egg = 99; __tintim.S.fruit = { x: TT.C.ARENA_X + 560, y: TT.C.GROUND - 22, vx: 0, vy: 0, rest: true }; });
  check(assentou && await until(() => __tintim.S.fox.state === 'eat' && !__tintim.S.fruit, CINE), 'o lobo-guará corre até a fruta-do-lobo e para para comer');
  await ev(() => { const f = __tintim.S.fox, p = __tintim.player; Object.assign(p, { x: f.x + f.w / 2 - p.w / 2, y: f.y - p.h - 40, vx: 0, vy: 200, onGround: false, inv: 99, hp: 3, dj: false, buffer: 0, coyote: 0 }); });
  check(await until(() => __tintim.S.fox.hp === 2, CINE), 'comendo a fruta, um pulo comum na crina acerta');
  let prontas = true; // os until de "pronto para o próximo golpe" eram descartados: um estouro em silêncio virava falha confusa aqui embaixo
  for (let k = 1; k < 3; k++) {
    prontas = prontas && await until(() => ['idle', 'dodge', 'hurt'].includes(__tintim.S.fox.state) && __tintim.S.fox.state !== 'hurt' && __tintim.player.onGround, CINE);
    await above(); await pg.keyboard.down('Space'); await pg.waitForFunction(n => __tintim.S.fox.hp === n, 2 - k, { timeout: CINE, polling: 50 }).catch(() => {}); await pg.keyboard.up('Space');
  }
  check(prontas && await ev(() => __tintim.S.fox.hp === 0), 'mais duas quedas planando na crina derrotam o lobo-guará');
  check(await ev(() => __tintim.S.runners.filter(r => r.kind === 'chaser' && r.vx > 0).length === 5), 'no golpe final, as galinhas saem do galinheiro e correm atrás dele');
  check(await until(() => __tintim.state === 'winning' || __tintim.state === 'win', CINE), 'derrotar o lobo-guará vence a fase');
  check(await until(() => document.getElementById('win').classList.contains('on'), CINE), 'tela de vitória aparece');
  check(await ev(() => document.querySelector('.winMonkey').src.includes('premio-chinela') && document.getElementById('winText').textContent.includes('chinela')), 'de presente, as galinhas dão a chinela amarela');
  check(await ev(() => document.getElementById('winTitle').textContent.includes('Galinheiro') && document.getElementById('stNotes').textContent.includes('1/4')), 'vitória com o texto do galinheiro e a contagem do correio elegante');
  check(await ev(() => JSON.parse(localStorage.getItem('tintim-fases') || '{}')[2] === true), 'fase 2 fica marcada como vencida');
  // entre as fases: o mapa abre, o Timtim anda pelo caminho até a fase 3 e ela começa sozinha
  await pg.waitForTimeout(2200); await pg.click('#btnNext'); // de parede: o botão só vira contagem 1900 ms depois, em setTimeout (ui.js)
  check(await until(() => TT.mapa.isOpen() && TT.mapa.state().walking, CINE), 'Próxima fase abre o mapa e o Timtim anda até a fase seguinte');
  check(await pg.waitForURL(/fase3/, { timeout: 15000 }).then(() => true, () => false), 'chegando na placa, a fase 3 carrega');
  check(await until(() => window.TT && TT.FASE === 3 && window.__tintim && __tintim.storyScene === 2 && document.getElementById('title').classList.contains('story'), CINE), 'a fase 3 abre direto no card dela (o Van Gogh), sem a capa');
  check(await ev(() => !/fase|corvo/i.test(document.getElementById('msg').textContent) || document.getElementById('msg').textContent === 'Carregando…'), 'na carga não aparece frase solta sem imagem');
  await pg.waitForTimeout(900); await pg.keyboard.press('Space'); // de parede: a trava de 800 ms do nextStory() (ui.js)
  check(await until(() => __tintim.state === 'play', CINE), 'um toque no card começa a fase 3');
  check(errs.length === 0, 'sem erros no console' + (errs.length ? ': ' + errs.slice(0, 3).join(' | ') : ''));
  await b.close();
})();
