// Correções do teste "jogador de 15 anos" (25/11/2026). Cada verificação foi vista falhando no código antigo.
//   1. Fase 2: a galinha que pula o buraco não machuca o Timtim no ar (antes acertava quem planava sobre o vão grande).
//   2. Espaço (o pulo) não pula as telas de vitória e derrota no primeiro 1,5 s.
//   3. "Carregando…" tem tempo-limite: se uma imagem travar, a tela sai mesmo assim.
//   4. Fase 3 sem a conversa repetida do Van Gogh dentro da fase; fase 1: o pulo encurta a cena do Furtão.
//   5. Vindo do mapa, a capa não aparece por baixo do card da fase.
//   6. A fala do Van Gogh tem letra maior.
// Uso: (servidor local na porta 8765 servindo a pasta game/) ; node game/tests/correcoes.js [url]
const { chromium } = require('playwright');
(async () => {
  const base = process.argv[2] || 'http://localhost:8765/';
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const check = (ok, msg) => { console.log((ok ? 'ok   ' : 'FALHA') + ' ' + msg); if (!ok) process.exitCode = 1; };
  const abre = async (hash, extra) => { const pg = await b.newPage({ viewport: { width: 960, height: 540 } }); if (extra) await extra(pg);
    await pg.goto(base + '?q=0&r=' + Math.random().toString(36).slice(2) + hash, { waitUntil: 'commit' }); return pg; };
  const ate = (pg, f, ms = 20000, a) => pg.waitForFunction(f, a, { timeout: ms, polling: 50 }).then(() => true, () => false);
  const joga = async (pg) => { await ate(pg, () => window.__tintim && __tintim.storyScene >= 0, 60000); await pg.waitForTimeout(1000); await pg.keyboard.press('Space');
    return ate(pg, () => TT.S.mode === 'play', 10000); };

  // 1. galinha pulando o buraco, no ar, encostando no Timtim que plana
  { const pg = await abre('#fase2-jogar'); await joga(pg); await ate(pg, () => !TT.S.cine, 15000);
    const r = await pg.evaluate(() => new Promise(res => { const S = TT.S, p = S.player, G = TT.C.GROUND;
      Object.assign(p, { x: 2500, y: 300, vx: 200, vy: -60, inv: 0, hp: 3, onGround: false, shrugT: 0 });
      S.runners.push({ kind: 'run', x: 2510, y: 300, w: 38, h: 30, vx: -420, t: 0, air: true, jv: -150, jy: 300 - (G - 30), boost: 1 });
      setTimeout(() => res({ hp: p.hp }), 250); }));
    check(r.hp === 3, 'fase 2: a galinha pulando o buraco não machuca o Timtim no ar (corações: ' + r.hp + ')');
    await pg.close(); }

  // 2. Espaço na vitória e na derrota
  { const pg = await abre('#fase1-jogar'); await joga(pg);
    await pg.evaluate(() => { TT.S.mode = 'winning'; TT.S.winT = 0; });
    await ate(pg, () => document.getElementById('win').classList.contains('on'), 20000);
    for (let i = 0; i < 5; i++) { await pg.keyboard.press('Space'); await pg.waitForTimeout(80); }
    await pg.waitForTimeout(300);
    check(await pg.evaluate(() => document.getElementById('win').classList.contains('on') && document.getElementById('mapa').hidden), 'vitória: Espaço logo que a tela aparece não pula a tela');
    await pg.waitForTimeout(1600); await pg.keyboard.press('Enter');
    check(await ate(pg, () => !document.getElementById('mapa').hidden, 3000), 'vitória: depois de 1,5 s, Enter segue para o mapa');
    await pg.close(); }
  { const pg = await abre('#fase1-jogar'); await joga(pg); await ate(pg, () => !TT.S.cine, 15000);
    await pg.evaluate(() => { const p = TT.S.player; p.hp = 1; p.inv = 0; p.x = 1300; p.y = 520; });
    await ate(pg, () => document.getElementById('lose').classList.contains('on'), 15000);
    for (let i = 0; i < 5; i++) { await pg.keyboard.press('Space'); await pg.waitForTimeout(80); }
    await pg.waitForTimeout(300);
    check(await pg.evaluate(() => TT.S.mode === 'lose' && document.getElementById('lose').classList.contains('on')), 'derrota: Espaço logo que a tela aparece não aperta "Tentar de novo"');
    await pg.close(); }

  // 3. uma imagem do cenário que nunca chega: o "Carregando…" sai mesmo assim
  { const pg = await abre('#fase2-jogar', p => p.route('**/assets/bg/arraial-mata.jpg', () => {}));
    check(await ate(pg, () => document.getElementById('msg') && document.getElementById('msg').classList.contains('hide'), 20000), '"Carregando…" sai mesmo com uma imagem travada');
    check(await ate(pg, () => window.__tintim && __tintim.storyScene === 1, 5000), 'e o card da fase aparece');
    await pg.close(); }

  // 4. fase 3: depois do cartão da fase, o jogo começa (sem o Van Gogh repetir a história); fase 1: o pulo encurta a cena do Furtão
  { const pg = await abre('#fase3-jogar'); await joga(pg);
    await ate(pg, () => TT.S.cine && TT.S.cine.type === 'arraial', 5000); await ate(pg, () => !TT.S.cine || TT.S.cine.type !== 'arraial', 8000);
    const c = await pg.evaluate(() => TT.S.cine && TT.S.cine.type);
    check(c !== 'vangogh', 'fase 3: o Van Gogh não conta de novo a história do card (cena: ' + c + ')');
    check(await pg.evaluate(() => { const m = __tintim.R.dbg.vg(); return m.visible && m.userData.name === 'vangogh-triste'; }), 'fase 3: o Van Gogh continua lá, triste, no começo');
    await pg.close(); }
  { const pg = await abre('#fase1-jogar'); await joga(pg); await ate(pg, () => TT.S.cine && TT.S.cine.type === 'steal', 5000);
    await pg.waitForTimeout(1000); const t0 = Date.now(); await pg.keyboard.press('Space');
    const ok = await ate(pg, () => !TT.S.cine, 1500);
    check(ok, 'fase 1: o pulo encerra a cena do Furtão (' + (ok ? ((Date.now() - t0) / 1000).toFixed(1) + ' s' : 'não encerrou') + ')');
    check(await pg.evaluate(() => TT.S.player.onGround && TT.S.player.vy === 0), 'o pulo que encerrou a cena não faz o Timtim pular sozinho');
    await pg.close(); }

  // 5. vindo do mapa (#faseN-jogar), a capa fica escondida enquanto o card aparece
  { const pg = await abre('#fase2-jogar'); await ate(pg, () => window.__tintim && __tintim.storyScene >= 0, 60000); await pg.waitForTimeout(300);
    const v = await pg.evaluate(() => getComputedStyle(document.querySelector('#title .tbg')).visibility);
    check(v === 'hidden', 'vindo do mapa, a capa não aparece por baixo do card (' + v + ')');
    await pg.close(); }

  // 6. fala do Van Gogh: letra maior que a dos amigos
  { const pg = await abre('#fase3-jogar'); await joga(pg); await ate(pg, () => !TT.S.cine, 15000);
    const fs = await pg.evaluate(() => { TT.emit('vgSay', { line: 'Meu pincel! Obrigado, Timtim!', dur: 2 }); const s = document.getElementById('say'); return { long: parseFloat(getComputedStyle(s).fontSize), cq: document.getElementById('stage').clientWidth }; });
    check(fs.long >= fs.cq * 0.019, 'a fala do Van Gogh tem letra de pelo menos 1,9% da largura da tela (' + fs.long.toFixed(1) + ' px em ' + fs.cq + ')');
    await pg.close(); }
  await b.close();
})();
