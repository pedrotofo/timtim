// Teste de fumaça da fase 2 (o Arraial): planar, ar quente da fogueira, chama que machuca, tábuas da quadrilha,
// faro revelando o caminho até a sanfoninha e a chegada ao mastro. Mesmo esquema do smoke.js: espera por condições.
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
  check(await until(() => __tintim.state === 'play' && __tintim.S.cine && __tintim.S.cine.type === 'arraial', 5000), 'Jogar começa direto, com o cartão do Arraial');
  check(await until(() => !__tintim.S.cine, 6000), 'cartão some e o controle é liberado');
  check(await ev(() => !__tintim.S.thief && !__tintim.S.arena), 'sem Furtão nem chefão no Arraial');

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

  // chama machuca quem encosta
  await put(fx - 27, 452 - 50, { onGround: true }); await pg.waitForTimeout(250);
  check(await ev(() => __tintim.player.hp < 3), 'encostar na fogueira tira um coração');
  await until(() => __tintim.player.onGround, 3000);

  // tábuas da quadrilha se movem e levam o Timtim junto
  const m = await ev(() => { const s = TT.MOVERS[0]; return { x: s.x, y: s.y, w: s.w }; });
  // a tábua anda enquanto ele cai: põe o Timtim em cima dela na posição atual e espera ele estar mesmo apoiado nela
  await ev(() => { const s = TT.MOVERS[0], p = __tintim.player; Object.assign(p, { x: s.x + s.w / 2 - p.w / 2, y: s.y - p.h - 1, vx: 0, vy: 0, inv: 9, hp: 3, onGround: false }); });
  await until(() => __tintim.player.onGround && __tintim.player.on && !!__tintim.player.on.mover, 2000);
  const a0 = await ev(() => ({ px: __tintim.player.x, sx: TT.MOVERS[0].x })); await pg.waitForTimeout(500);
  const a1 = await ev(() => ({ px: __tintim.player.x, sx: TT.MOVERS[0].x, on: __tintim.player.onGround }));
  check(Math.abs(a1.sx - a0.sx) > 10 && a1.on && Math.abs((a1.px - a0.px) - (a1.sx - a0.sx)) < 4, 'a tábua da quadrilha anda e leva o Timtim junto');

  // faro: perto da terceira fogueira revela o caminho de cheiro até a sanfoninha
  const t = await ev(() => TT.C.trails[0].at);
  await put(t - 120, 452 - 50, { onGround: true, inv: 9 }); await until(() => __tintim.player.onGround, 2000);
  await pg.keyboard.down('ArrowDown'); check(await until(() => __tintim.S.revealed.sanfona, 3000), 'farejar perto da fogueira revela o caminho de cheiro'); await pg.keyboard.up('ArrowDown');
  await ev(() => { const it = __tintim.S.items.find(i => i.type === 'toy'), p = __tintim.player; p.x = it.x - 27; p.y = it.y - 25; p.vy = 0; });
  check(await until(() => __tintim.S.toy, 3000), 'pega a sanfoninha');
  check(await ev(() => JSON.parse(localStorage.getItem('tintim-toys') || '{}').sanfoninha === true), 'a sanfoninha fica salva na estante');

  // chegada ao mastro
  await put(7300, 452 - 50, { onGround: true, inv: 9 }); await pg.keyboard.down('ArrowRight');
  check(await until(() => __tintim.state === 'winning' || __tintim.state === 'win', 6000), 'chegar ao mastro de São João vence a fase'); await pg.keyboard.up('ArrowRight');
  check(await until(() => document.getElementById('win').classList.contains('on'), 9000), 'tela de vitória aparece');
  check(await ev(() => document.getElementById('winTitle').textContent.includes('São João')), 'vitória com o texto do Arraial');
  check(await ev(() => JSON.parse(localStorage.getItem('tintim-fases') || '{}')[2] === true), 'fase 2 fica marcada como vencida');
  check(errs.length === 0, 'sem erros no console' + (errs.length ? ': ' + errs.slice(0, 3).join(' | ') : ''));
  await b.close();
})();
