// Teste de fumaça da fase 3 (o Quadro Encantado, no mundo de Van Gogh): o Van Gogh pedindo ajuda, redemoinhos que giram e soltam,
// toldos do café que quicam, estrelas que piscam, corvos no trigal e a luta com o Corvo-Borrão (tubos de tinta, bicadas, pincel). Mesmo esquema do smoke-arraial.js: espera por condições.
// Uso: (servidor local na porta 8765 servindo a pasta game/) ; node game/tests/smoke-quadro.js [url]
const { chromium } = require('playwright');
(async () => {
  const url = (process.argv[2] || 'http://localhost:8765/') + '?fase=3&q=0';
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const pg = await b.newPage({ viewport: { width: 960, height: 540 } });
  const errs = []; pg.on('pageerror', e => errs.push(e.message)); pg.on('console', m => m.type() === 'error' && errs.push(m.text()));
  pg.on('requestfailed', r => errs.push('falhou: ' + r.url()));
  const ev = (f, a) => pg.evaluate(f, a);
  const until = (f, ms = 20000) => pg.waitForFunction(f, null, { timeout: ms, polling: 50 }).then(() => true, () => false);
  const check = (ok, msg) => { console.log((ok ? 'ok   ' : 'FALHA') + ' ' + msg); if (!ok) process.exitCode = 1; };
  const put = (x, y, extra) => ev(([x, y, extra]) => { const p = __tintim.player; Object.assign(p, { x, y, vx: 0, vy: 0, onGround: false, inv: 0, hp: 3, orbit: null, swirlCd: 0, launchT: 0 }, extra || {}); }, [x, y, extra]);
  await pg.goto(url);
  check(await until(() => window.__tintim && __tintim.R.ready && __tintim.state === 'title'), 'abre o título na fase 3');
  check(await ev(() => document.getElementById('faseTag').textContent.toUpperCase().includes('QUADRO') && document.querySelector('.logo i').textContent.includes('QUADRO ENCANTADO')), 'título mostra "O Quadro Encantado"');
  await pg.waitForTimeout(500); await pg.click('#btnStart');
  check(await until(() => __tintim.state === 'play' && __tintim.S.cine && __tintim.S.cine.type === 'arraial', 5000), 'Jogar começa direto, com o cartão da fase');
  check(await ev(() => document.body.innerText.includes('QUADRO ENCANTADO')), 'o cartão anuncia "O Quadro Encantado"');
  check(await until(() => __tintim.S.cine && __tintim.S.cine.type === 'vangogh', 6000), 'depois do cartão, o Van Gogh aparece pedindo ajuda');
  check(await until(() => document.getElementById('say').classList.contains('on') && document.getElementById('say').textContent.includes('corvo'), 2500), 'o Van Gogh conta que pintou um corvo que ganhou vida');
  check(await ev(() => { const m = __tintim.R.dbg.vg(); return m.visible && m.userData.name === 'vangogh-triste'; }), 'o Van Gogh aparece triste no começo');
  await pg.waitForTimeout(1200); await pg.keyboard.press('Space');
  check(await until(() => document.getElementById('say').textContent.includes('pincel'), 1500), 'o pulo adianta para a segunda fala (o pincel roubado)');
  await pg.waitForTimeout(300); await pg.keyboard.press('Space');
  check(await until(() => !__tintim.S.cine, 2000), 'mais um pulo encerra a conversa e libera o controle');
  check(await ev(() => __tintim.player.onGround && __tintim.player.vy === 0), 'o pulo que encerrou a conversa não faz o Timtim pular sozinho');
  check(await ev(() => !__tintim.S.thief && !__tintim.S.arena && __tintim.S.enemies.length > 0), 'sem Furtão nem chefão no começo, e há corvos no caminho');
  check(await ev(() => __tintim.S.enemies.every(e => { for (let x = e.a; x <= e.b + e.w; x += 5) if (!TT.C.grounds.some(([g0, gw]) => x >= g0 && x <= g0 + gw)) return false; return true; })), 'nenhum corvo anda por cima de buraco (o trajeto inteiro fica no chão)');

  // redemoinho: pula dentro, ele prende e gira; apertar o pulo solta com força
  const sw = await ev(() => TT.C.SWIRLS[0]);
  const pw = await ev(() => ({ w: __tintim.player.w, h: __tintim.player.h }));
  await put(sw.x - pw.w / 2 + 10, sw.y - pw.h / 2, { vy: 100 });
  check(await until(() => !!__tintim.player.orbit, 1500), 'pular dentro do redemoinho prende o Timtim');
  const a0 = await ev(() => __tintim.player.orbit.a); await pg.waitForTimeout(400);
  const o = await ev(() => ({ a: __tintim.player.orbit && __tintim.player.orbit.a, x: __tintim.player.x, y: __tintim.player.y }));
  check(o.a != null && Math.abs(o.a - a0) > 0.8, `o redemoinho gira com ele (girou ${(o.a - a0).toFixed(2)} rad)`);
  await ev(() => { window._swOut = null; TT.on('swirlOut', () => { const p = __tintim.player; window._swOut = window._swOut || { vx: p.vx, vy: p.vy }; }); });
  await pg.keyboard.press('Space'); await until(() => !!window._swOut, 1000);
  const l = await ev(() => ({ orbit: !!__tintim.player.orbit, sp: window._swOut ? Math.hypot(window._swOut.vx, window._swOut.vy) : 0 }));
  check(!l.orbit && l.sp > 600, `apertar o pulo solta do redemoinho com impulso (${l.sp.toFixed(0)} px/s)`);
  await pg.waitForTimeout(200);
  check(await ev(() => !__tintim.player.orbit), 'logo depois de soltar, o mesmo redemoinho não prende de novo');

  // toldo do café: cair em cima dele joga o Timtim bem alto
  const tol = await ev(() => TT.C.plats.find(q => q[3]));
  await put(tol[0] + tol[2] / 2 - pw.w / 2, tol[1] - pw.h - 30, { vy: 300 });
  check(await until(() => __tintim.player.vy < -900, 1500), 'cair no toldo do café quica alto');
  let topY = 1e9; for (let i = 0; i < 12; i++) { topY = Math.min(topY, await ev(() => __tintim.player.y)); await pg.waitForTimeout(50); }
  check(topY < tol[1] - pw.h - 200, `o quique sobe mais de 200 px (subiu ${(tol[1] - pw.h - topY).toFixed(0)})`);

  // estrelas que piscam: apagada, ele atravessa; acesa, segura
  const bl = await ev(() => TT.C.blinks[0]);
  await ev(() => { __tintim.S.clock = 1.6; }); // apagada por quase 1 s
  await put(bl.x + bl.w / 2 - pw.w / 2, bl.y - pw.h - 10, { vy: 120 });
  check(await pg.waitForFunction(y => __tintim.player.y > y + 30, bl.y, { timeout: 900, polling: 50 }).then(() => true, () => false), 'estrela apagada: o Timtim cai através dela');
  await ev(() => { __tintim.S.clock = 0; });
  await put(bl.x + bl.w / 2 - pw.w / 2, bl.y - pw.h - 10, { vy: 120 });
  check(await pg.waitForFunction(y => __tintim.player.onGround && Math.abs(__tintim.player.y + __tintim.player.h - y) < 4, bl.y, { timeout: 900, polling: 50 }).then(() => true, () => false), 'estrela acesa: o Timtim fica em pé nela');

  // corvo do trigal: pisar em cima espanta ele
  const ei = await ev(() => { const S = __tintim.S; let k = -1; S.enemies.forEach((e, i) => { if (k < 0 && e.alive && e.x > 2650 && e.x < 4300) k = i; }); return k; });
  check(ei >= 0, 'há corvos andando no trigal');
  if (ei >= 0) {
    await ev(i => { const e = __tintim.S.enemies[i], p = __tintim.player; e.dir = 0; Object.assign(p, { x: e.x + e.w / 2 - p.w / 2, y: e.y - p.h - 6, vx: 0, vy: 250, onGround: false, inv: 0, hp: 3, orbit: null }); }, ei);
    check(await pg.waitForFunction(i => !__tintim.S.enemies[i].alive, ei, { timeout: 1500, polling: 50 }).then(() => true, () => false), 'pular em cima do corvo espanta ele');
    check(await ev(() => __tintim.player.hp === 3), 'o pisão no corvo não tira coração');
  }

  // a carta ao Theo usa o nome certo
  const nt = await ev(() => TT.C.NOTES[0]);
  await put(nt.x - pw.w / 2, nt.y - pw.h / 2, { vy: 0, inv: 99 });
  check(await until(() => document.querySelector('#note small').textContent.startsWith('Carta ao Theo'), 2000), 'o bilhete da fase 3 aparece como "Carta ao Theo"');
  await ev(() => { const n = document.getElementById('note'); if (n) n.classList.remove('on'); });

  // o Corvo-Borrão: chegar no morro começa a luta com a apresentação dele
  const ax = await ev(() => TT.C.ARENA_X);
  await ev(() => { __tintim.S.notes = __tintim.S.notes || 0; });
  await put(ax + 200, 452 - 50, { onGround: true, inv: 99 });
  check(await until(() => __tintim.S.arena && __tintim.S.cine && __tintim.S.cine.type === 'fox', 3000), 'chegar no morro apresenta o Corvo-Borrão');
  check(await ev(() => document.body.innerText.includes('CORVO-BORRÃO')), 'o cartão do chefão diz "O CORVO-BORRÃO"');
  check(await until(() => !__tintim.S.cine, 6000), 'depois da apresentação, a luta começa');
  await pg.waitForTimeout(400);
  check(await ev(() => { const m = __tintim.R.dbg.fox(), o = m.material.map.offset; return m.visible && Number.isFinite(o.x) && Number.isFinite(o.y); }), 'o Corvo-Borrão continua desenhado depois da apresentação');
  check(await ev(() => document.querySelector('.bossRow b').textContent === 'Corvo-Borrão'), 'a barra de vida mostra "Corvo-Borrão"');
  check(await ev(() => TT.C.SWIRLS.every(s => s.x < TT.C.ARENA_X)), 'o morro do chefão não tem redemoinhos');
  check(await until(() => __tintim.S.fox.state === 'fly', 4000), 'o Corvo-Borrão levanta voo');
  // tubo de tinta: aparece a marca vermelha, o tubo cai ali e machuca quem estiver embaixo
  await ev(() => { const p = __tintim.player; Object.assign(p, { x: TT.C.ARENA_X + 300, y: TT.C.GROUND - p.h, vx: 0, vy: 0, onGround: true, inv: 0, hp: 3, mega: 0, fast: 0 }); __tintim.S.fox.cd = 0; });
  check(await until(() => __tintim.S.fox.state === 'aim', 2000), 'ele mira antes de soltar o tubo (aviso)');
  const tx = await ev(() => __tintim.S.fox.tx);
  check(Math.abs(tx - (await ev(() => TT.C.ARENA_X + 300 + __tintim.player.w / 2))) < 40, 'a marca do tubo fica onde o Timtim está');
  check(await until(() => __tintim.S.tubes.length > 0, 2000), 'o corvo solta um tubo de tinta');
  check(await until(() => __tintim.player.hp === 2, 2500), 'o tubo de tinta machuca quem fica na marca'); 
  check(await until(() => __tintim.S.splats.length > 0 || !__tintim.S.tubes.length, 2500), 'o tubo vira mancha de tinta no chão');
  // no ar ele não leva dano
  await ev(() => { const f = __tintim.S.fox, p = __tintim.player; Object.assign(p, { x: f.x + f.w / 2 - p.w / 2, y: f.y - p.h - 20, vx: 0, vy: 200, onGround: false, inv: 99, hp: 3 }); });
  await pg.waitForTimeout(500);
  check(await ev(() => __tintim.S.fox.hp === 3), 'voando, o corvo não perde vida');
  // acabados os tubos ele mergulha e fica bicando o chão: é a hora de pular nas costas
  const peck = async () => { await ev(() => { const f = __tintim.S.fox; if (f.state === 'fly') { f.drops = 0; f.cd = 0; } }); return until(() => __tintim.S.fox.state === 'peck', 9000); };
  const stomp = () => ev(() => { const f = __tintim.S.fox, p = __tintim.player; Object.assign(p, { x: f.x + f.w / 2 - p.w / 2, y: f.y - p.h - 30, vx: 0, vy: 250, onGround: false, inv: 99, hp: 3 }); });
  await until(() => __tintim.S.fox.state === 'fly', 6000);
  check(await peck(), 'sem tubos, ele mergulha e fica bicando o chão');
  check(await ev(() => __tintim.R.dbg.fox().userData.name === 'guara-agacha'), 'bicando, aparece a pose de cabeça baixa');
  await stomp();
  check(await until(() => __tintim.S.fox.hp === 2 && __tintim.S.fox.state === 'hurt', 1500), 'pular nas costas enquanto ele bica tira um coração');
  check(await until(() => __tintim.S.fox.state === 'fly', 6000), 'depois do golpe ele volta a voar');
  check(await ev(() => __tintim.S.fox.drops === 4), 'na segunda rodada ele joga mais tubos (4)');
  await peck(); await stomp();
  check(await until(() => __tintim.S.fox.hp === 1, 1500), 'segundo golpe nas costas');
  check(await ev(() => __tintim.S.fox.red), 'no último coração o corvo fica vermelho de raiva');
  await until(() => __tintim.S.fox.state === 'fly', 6000);
  check(await ev(() => __tintim.R.dbg.crowRed().visible && __tintim.S.fox.drops === 6), 'vermelho e mais bravo: 6 tubos na última rodada');
  await peck(); await stomp();
  check(await until(() => __tintim.S.fox.hp === 0, 1500), 'o terceiro golpe derrota o Corvo-Borrão');
  check(await ev(() => !!__tintim.S.brush), 'derrotado, ele solta o pincel do Van Gogh');
  check(await until(() => __tintim.S.vg && __tintim.S.vg.mood === 'happy' && !__tintim.S.brush, 5000), 'o Van Gogh aparece feliz com o pincel');
  check(await ev(() => __tintim.R.dbg.vg().visible && __tintim.R.dbg.vg().userData.name === 'vangogh-feliz'), 'o Van Gogh comemora (pose feliz)');
  check(await until(() => __tintim.state === 'winning' || __tintim.state === 'win', 3000), 'derrotar o Corvo-Borrão vence a fase');
  check(await until(() => document.getElementById('win').classList.contains('on'), 12000), 'tela de vitória aparece');
  check(await ev(() => document.getElementById('winTitle').textContent.includes('pincel') && document.getElementById('stNotes').textContent.includes('Cartas ao Theo')), 'vitória com o texto do pincel e a contagem das cartas ao Theo');
  check(await ev(() => !document.getElementById('btnNext').classList.contains('on')), 'na última fase não aparece "Próxima fase"');
  check(await ev(() => JSON.parse(localStorage.getItem('tintim-fases') || '{}')[3] === true), 'fase 3 fica marcada como vencida');
  check(errs.length === 0, 'sem erros no console' + (errs.length ? ': ' + errs.slice(0, 3).join(' | ') : ''));
  await b.close();
})();
