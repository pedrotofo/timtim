// Métricas das fases (skill level-design): mede o pulo de verdade do Timtim e confere cada buraco do caminho principal.
// Rode depois de mexer no pulo, no planar ou no desenho de uma fase.
//   1. O pulo é medido no jogo (passos fixos de 1/240 s): altura e tempo no ar do pulo cheio, do toque curto e do pulo duplo.
//   2. Para cada buraco do chão, procura a rota mais fácil (chão, tábuas, tábuas móveis, estrelas) e mede cada salto
//      contra o alcance do movimento: no caminho principal, nenhum salto pode passar de 70% do alcance.
//   3. Tábuas "no quase": uma tábua que só se alcança com o pulo simples não pode ficar a menos de 20 px do topo do pulo.
//   4. Chocolate (ou mancha de tinta) antes de um buraco: lento, o Timtim ainda tem de conseguir atravessar.
// Uso: (servidor local na porta 8765 servindo a pasta game/) ; node game/tests/metricas.js [url]
const { chromium } = require('playwright');
const GRAV = 2300, JV = -860, RUN = 310, SLOW = 175, DT = 1 / 240, LIMITE = 0.7, FOLGA = 20, SLOW_S = 5;

function traj(move, glideOk, speed) { // trajetória (x, altura) correndo, segurando o pulo (mesma conta do game.js)
  let vy = JV, y = 0, x = 0, djT = 0, used = !move.includes('duplo'), gliding = false; const pts = [];
  for (let n = 0; n < 240 * 8; n++) {
    if (!used && vy > -40) { vy = JV * 0.86; used = true; djT = 0.42; }
    djT = Math.max(0, djT - DT);
    const glide = glideOk && move.includes('planar') && djT <= 0 && (vy > -40 || gliding); gliding = glide;
    const hang = Math.abs(vy) < 130 ? 0.55 : 1;
    if (glide) { if (vy < 135) vy = Math.min(135, vy + GRAV * 0.3 * DT); else vy += (135 - vy) * Math.min(1, DT * 9); }
    else vy = Math.min(vy + GRAV * hang * DT, 1200);
    y += vy * DT; x += speed * DT; pts.push([x, -y, vy]); if (-y < -400) break; }
  return pts; }
const apexOf = pts => Math.max(...pts.map(p => p[1]));
const reach = (pts, dh) => { if (dh > apexOf(pts)) return -1; let best = -1; for (const [x, h, vy] of pts) if (vy > 0 && h >= dh) best = x; return best; };

function rotas(L, speed) { // para cada buraco do chão: a rota com o salto mais difícil o mais fácil possível
  const G = L.GROUND, pw = L.pw, moves = L.GLIDE ? ['planar', 'duplo+planar'] : ['simples', 'duplo'];
  const T = Object.fromEntries(moves.map(m => [m, traj(m, L.GLIDE, speed)]));
  const surf = [];
  L.grounds.forEach(([x, w]) => surf.push({ n: 'chão ' + x, a: x, b: x + w, h: 0 }));
  L.plats.forEach(([x, y, w, q]) => surf.push({ n: (q ? 'toldo ' : 'tábua ') + x, a: x, b: x + w, h: G - y }));
  (L.movers || []).forEach(m => surf.push({ n: 'tábua móvel ' + m.x, a: m.x - m.ax, b: m.x + m.w + m.ax, h: G - m.y + (m.ay || 0) }));
  (L.blinks || []).forEach(m => surf.push({ n: 'estrela ' + m.x, a: m.x, b: m.x + m.w, h: G - m.y }));
  const gs = L.grounds.map(([x, w]) => [x, x + w]).sort((p, q) => p[0] - q[0]), out = [];
  const hop = (A, B) => { const need = Math.max(0, B.a - A.b - pw), dh = B.h - A.h; let best = null;
    for (const m of moves) { const r = reach(T[m], dh); if (r <= 0) continue; const k = need / r; if (!best || (best.k > LIMITE && k < best.k)) best = { m, k, need, dh }; if (k <= LIMITE) break; }
    return best; };
  for (let i = 1; i < gs.length; i++) { const g0 = gs[i - 1][1], g1 = gs[i][0]; if (g1 <= g0) continue;
    const nodes = surf.filter(s => s.b > g0 - 400 && s.a < g1 + 400);
    const start = nodes.find(s => s.h === 0 && s.b === g0), end = nodes.find(s => s.h === 0 && s.a === g1); let best = null;
    const dfs = (A, path, worst) => { if (A === end) { if (!best || worst < best.worst) best = { path, worst }; return; } if (path.length > 6) return;
      for (const B of nodes) { if (B === A || B.a <= A.a || path.some(p => p.B === B)) continue; const hp = hop(A, B); if (!hp || hp.k > 1) continue; dfs(B, path.concat([{ A, B, ...hp }]), Math.max(worst, hp.k)); } };
    dfs(start, [], 0);
    const ajudas = [...(L.swirls || []), ...(L.fires || [])].some(s => s.x > g0 - 150 && s.x < g1 + 150) || L.plats.some(p => p[3] && p[0] > g0 - 600 && p[0] < g1);
    out.push({ g0, g1, best, ajudas }); }
  return { out, T, moves }; }

(async () => {
  const base = process.argv[2] || 'http://localhost:8765/';
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'] });
  const pg = await b.newPage({ viewport: { width: 960, height: 540 } });
  const check = (ok, msg) => { console.log((ok ? 'ok   ' : 'FALHA') + ' ' + msg); if (!ok) process.exitCode = 1; };
  const pulos = [];
  for (const f of [1, 2, 3]) {
    await pg.goto(base + '?fase=' + f + '&q=0&r=' + Date.now() + '#fase' + f + '-jogar');
    // vindo do mapa, a fase abre no card da história; aqui a medição pula o card
    await pg.waitForFunction(() => window.TT && TT.S && (TT.S.mode === 'play' || (window.__tintim && __tintim.storyScene >= 0)), null, { timeout: 30000 });
    await pg.evaluate(() => { if (TT.S.mode === 'title') TT.start(); });
    await pg.waitForFunction(() => TT.S.mode === 'play', null, { timeout: 10000 });
    const L = await pg.evaluate(() => { const C = TT.C, S = TT.S; TT.demo.noHurt = true; S.cine = null;
      const p = S.player, I = TT.input, settle = () => { for (let i = 0; i < 480; i++) TT.update(1 / 240); };
      const jump = mode => { Object.assign(p, { x: 200, vx: 0, vy: 0 }); I.left = I.right = I.jump = false; settle(); const y0 = p.y; let apex = 0, t = 0, n = 0, second = false;
        I.jump = true; I.jumpPressed = true;
        while (n < 2400) { n++; if (mode === 'toque' && n === 12) I.jump = false; if (mode === 'duplo' && !second && p.vy > -40 && n > 5) { I.jumpPressed = true; second = true; }
          TT.update(1 / 240); t += 1 / 240; apex = Math.max(apex, y0 - p.y); if (p.onGround && n > 5) break; }
        I.jump = false; return { altura: +apex.toFixed(1), noAr: +t.toFixed(2) }; };
      const pulo = { cheio: jump('cheio'), toque: jump('toque'), duplo: jump('duplo') };
      return { FASE: TT.FASE, pulo, pw: p.w, GROUND: C.GROUND, grounds: C.grounds, plats: C.plats, movers: C.movers, blinks: C.blinks, swirls: C.SWIRLS, fires: C.fires, GLIDE: C.GLIDE,
        chocos: S.items.filter(i => i.type === 'choco').map(i => i.x) }; });
    check(L.FASE === f, `fase ${f} carregada`);
    pulos.push(L.pulo.cheio.altura, L.pulo.duplo.altura);
    console.log(`     pulo na fase ${f}: cheio ${L.pulo.cheio.altura} px (${L.pulo.cheio.noAr} s no ar), toque ${L.pulo.toque.altura} px, duplo ${L.pulo.duplo.altura} px (${L.pulo.duplo.noAr} s)`);
    const { out, T, moves } = rotas(L, RUN);
    for (const g of out) {
      if (!g.best) { check(g.ajudas, `fase ${f}, buraco ${g.g0}-${g.g1}: sem rota só com pulo e planar${g.ajudas ? ' (atravessa com redemoinho, fogueira ou toldo)' : ''}`); continue; }
      const pior = g.best.path.reduce((a, p) => (p.k > a.k ? p : a));
      check(g.best.worst <= LIMITE, `fase ${f}, buraco ${g.g0}-${g.g1} (${g.g1 - g.g0} px): salto mais difícil a ${(g.best.worst * 100).toFixed(0)}% do alcance (${pior.A.n} → ${pior.B.n}, ${pior.m})`); }
    // tábuas no quase: altura acima do chão entre (topo do pulo simples - FOLGA) e o topo, sem outra tábua por perto para chegar por cima
    const ap = apexOf(T[moves[0]]);
    const quase = L.plats.filter(([x, y, w]) => { const h = L.GROUND - y; return h > ap - FOLGA && h <= ap; });
    check(quase.length === 0, `fase ${f}: nenhuma tábua a menos de ${FOLGA} px do topo do pulo (${Math.round(ap)} px)` + (quase.length ? ': ' + quase.map(p => p[0]).join(', ') : ''));
    // chocolate antes de buraco: com o Timtim lento (5 s), cada buraco ao alcance ainda tem rota
    const lento = rotas(L, SLOW).out;
    for (const cx of L.chocos) for (const g of lento) if (g.g0 > cx && g.g0 - cx < SLOW * SLOW_S) {
      check(g.best ? g.best.worst <= LIMITE : g.ajudas, `fase ${f}: lento pelo chocolate de ${cx}, o buraco ${g.g0}-${g.g1} ainda tem rota` + (g.best ? ` (salto mais difícil a ${(g.best.worst * 100).toFixed(0)}%)` : '')); }
  }
  check(Math.max(...pulos.filter((_, i) => i % 2 === 0)) - Math.min(...pulos.filter((_, i) => i % 2 === 0)) < 1, 'o pulo cheio tem a mesma altura nas 3 fases');
  // 5. o pulo pelo laço de verdade do jogo, com a tela a 30 e a 144 quadros por segundo: tem de sair com a mesma altura
  const alturas = [];
  for (const hz of [30, 144]) {
    const ctx = await b.newContext({ viewport: { width: 960, height: 540 } });
    await ctx.addInitScript(hz => { let t = 0; const q = []; // relógio falso: cada quadro anda 1/hz s, sem esperar o tempo real
      window.requestAnimationFrame = cb => { q.push(cb); if (q.length === 1) setTimeout(() => { t += 1000 / hz; const cbs = q.splice(0); cbs.forEach(c => c(t)); }, 1); return q.length; };
      const real = performance.now.bind(performance); performance.now = () => t; window.__realNow = real; }, hz);
    const p2 = await ctx.newPage();
    await p2.goto(base + '?fase=1&q=0&r=' + hz + '#fase1-jogar');
    await p2.waitForFunction(() => window.TT && TT.S && (TT.S.mode === 'play' || (window.__tintim && __tintim.storyScene >= 0)), null, { timeout: 60000 });
    await p2.evaluate(() => { if (TT.S.mode === 'title') TT.start(); });
    await p2.waitForFunction(() => TT.S.mode === 'play' && !TT.S.cine && TT.S.player.onGround, null, { timeout: 60000 });
    await p2.evaluate(() => { TT.demo.noHurt = true; Object.assign(TT.S.player, { x: 200, vx: 0 }); });
    await p2.waitForFunction(() => TT.S.player.onGround && TT.S.player.vy === 0, null, { timeout: 20000 });
    const h = await p2.evaluate(() => new Promise(res => { const p = TT.S.player, y0 = p.y, R = TT.R, frame = R.frame; let apex = 0, left = false;
      TT.input.jump = true; TT.input.jumpPressed = true;
      R.frame = dt => { apex = Math.max(apex, y0 - p.y); if (!p.onGround) left = true; if (left && p.onGround) { R.frame = frame; TT.input.jump = false; res(apex); } return frame(dt); }; }));
    alturas.push(h); console.log(`     pulo pelo laço do jogo a ${hz} quadros por segundo: ${h.toFixed(1)} px`);
    await ctx.close(); }
  check(Math.abs(alturas[0] - alturas[1]) < 2, `o pulo tem a mesma altura a 30 e a 144 quadros por segundo (diferença ${Math.abs(alturas[0] - alturas[1]).toFixed(1)} px)`);
  await b.close();
})();
