// Teste de fumaça da fase 3 (o Quadro Encantado, no mundo de Van Gogh): o Van Gogh triste no começo, redemoinhos que giram e soltam,
// toldos do café que quicam, estrelas que piscam, corvos no trigal e a luta com o Corvo-Borrão (tubos de tinta, bicadas, pincel). Mesmo esquema do smoke-arraial.js: espera por condições.
// Uso: (servidor local na porta 8765 servindo a pasta game/) ; node game/tests/smoke-quadro.js [url]
const { chromium } = require('playwright');
(async () => {
  const url = (process.argv[2] || 'http://localhost:8765/') + '?fase=3&q=0';
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
  const put = (x, y, extra) => ev(([x, y, extra]) => { const p = __tintim.player; Object.assign(p, { x, y, vx: 0, vy: 0, onGround: false, inv: 0, hp: 3, orbit: null, swirlCd: 0, launchT: 0 }, extra || {}); }, [x, y, extra]);
  await pg.goto(url);
  check(await until(() => window.__tintim && __tintim.R.ready && __tintim.state === 'title'), 'abre o título na fase 3');
  check(await ev(() => document.querySelector('.logo img').alt === 'Timtim e os Brinquedos Perdidos' && document.querySelector('.logo img').naturalWidth > 0), 'a capa é a mesma do jogo todo');
  await pg.waitForTimeout(500); await pg.click('#btnStart'); // de parede: animação da capa (CSS/setTimeout)
  check(await until(() => TT.mapa.isOpen() && document.querySelector('#mapa canvas'), CINE), 'Jogar abre o mapa das fases');
  await pg.waitForTimeout(400); await pg.keyboard.press('Enter'); // de parede: o mapa tem laço de rAF próprio em performance.now() (mapa.js)
  check(await until(() => __tintim.storyScene === 2 && document.getElementById('storyLine').textContent.includes('pincel do Van Gogh'), CINE), 'antes da fase, o card do Van Gogh triste com o corvo');
  await pg.waitForTimeout(900); await pg.keyboard.press('Space'); // de parede: nextStory() só aceita o toque 800 ms depois, contados em performance.now() (ui.js)
  check(await until(() => __tintim.state === 'play' && __tintim.S.cine && __tintim.S.cine.type === 'arraial', CINE), 'depois do card, a fase começa com o cartão dela');
  check(await ev(() => document.body.innerText.includes('QUADRO ENCANTADO')), 'o cartão anuncia "O Quadro Encantado"');
  check(await until(() => !__tintim.S.cine, CINE), 'depois do cartão, o controle é liberado (o card já contou a história; o Van Gogh não repete)');
  check(await ev(() => { const m = __tintim.R.dbg.vg(); return m.visible && m.userData.name === 'vangogh-triste'; }), 'o Van Gogh aparece triste no começo');
  check(await ev(() => !document.getElementById('say').classList.contains('on')), 'sem balão de fala do Van Gogh no começo');
  check(await ev(() => !__tintim.S.thief && !__tintim.S.arena && __tintim.S.enemies.length > 0), 'sem Furtão nem chefão no começo, e há corvos no caminho');
  check(await ev(() => __tintim.S.enemies.every(e => { for (let x = e.a; x <= e.b + e.w; x += 5) if (!TT.C.grounds.some(([g0, gw]) => x >= g0 && x <= g0 + gw)) return false; return true; })), 'nenhum corvo anda por cima de buraco (o trajeto inteiro fica no chão)');

  // redemoinho: pula dentro, ele prende e gira; apertar o pulo solta com força
  const sw = await ev(() => TT.C.SWIRLS[0]);
  const pw = await ev(() => ({ w: __tintim.player.w, h: __tintim.player.h }));
  await put(sw.x - pw.w / 2 + 10, sw.y - pw.h / 2, { vy: 100 });
  check(await until(() => !!__tintim.player.orbit, CINE), 'pular dentro do redemoinho prende o Timtim');
  const a0 = await ev(() => __tintim.player.orbit.a);
  // condição, não 400 ms de parede: orbit.a só acumula (game.js:619), então dá para esperar os 0,8 rad de verdade
  const girou = await until(a => __tintim.player.orbit && Math.abs(__tintim.player.orbit.a - a) > 0.8, CINE, a0);
  const o = await ev(() => ({ a: __tintim.player.orbit && __tintim.player.orbit.a }));
  check(girou, `o redemoinho gira com ele (girou ${o.a == null ? '?' : (o.a - a0).toFixed(2)} rad)`);
  await ev(() => { window._swOut = null; TT.on('swirlOut', () => { const p = __tintim.player; window._swOut = window._swOut || { vx: p.vx, vy: p.vy }; }); });
  await pg.keyboard.press('Space');
  const soltou = await until(() => !!window._swOut, CINE); // era um until descartado
  const l = await ev(() => ({ orbit: !!__tintim.player.orbit, sp: window._swOut ? Math.hypot(window._swOut.vx, window._swOut.vy) : 0 }));
  check(soltou && !l.orbit && l.sp > 600, `apertar o pulo solta do redemoinho com impulso (${l.sp.toFixed(0)} px/s)`);
  const passou02 = await jogo(0.2); // tempo DE JOGO, e curto de propósito: a carência do redemoinho é 0,5 s de jogo (swirlCd, game.js:567)
  check(passou02 && await ev(() => !__tintim.player.orbit), 'logo depois de soltar, o mesmo redemoinho não prende de novo');

  // toldo do café: cair em cima dele joga o Timtim bem alto
  const tol = await ev(() => TT.C.plats.find(q => q[3]));
  await put(tol[0] + tol[2] / 2 - pw.w / 2, tol[1] - pw.h - 30, { vy: 300 });
  check(await until(() => __tintim.player.vy < -900, CINE), 'cair no toldo do café quica alto');
  // guarda o ponto mais alto do voo num amostrador por rAF (só registra; quem decide é a condição abaixo)
  await ev(() => { window.__minY = 1e9; const f = () => { window.__minY = Math.min(window.__minY, __tintim.player.y); if (__tintim.player.vy <= 0) requestAnimationFrame(f); }; requestAnimationFrame(f); });
  const alvo = tol[1] - pw.h - 200;
  const quicou = await until(y => __tintim.player.y < y, CINE, alvo); // condição, não 600 ms de parede amostrando
  const topY = await ev(() => window.__minY);
  check(quicou, `o quique sobe mais de 200 px (subiu ${(tol[1] - pw.h - topY).toFixed(0)})`);

  // estrelas que piscam: apagada, ele atravessa; acesa, segura
  const bl = await ev(() => TT.C.blinks[0]);
  await ev(() => { __tintim.S.clock = 1.6; }); // apagada por quase 1 s
  await put(bl.x + bl.w / 2 - pw.w / 2, bl.y - pw.h - 10, { vy: 120 });
  // prazo curto de propósito: a estrela volta a acender ~1 s DE JOGO depois, e a queda tem de acontecer antes disso
  check(await pg.waitForFunction(y => __tintim.player.y > y + 30, bl.y, { timeout: 900, polling: 50 }).then(() => true, () => false), 'estrela apagada: o Timtim cai através dela');
  await ev(() => { __tintim.S.clock = 0; });
  await put(bl.x + bl.w / 2 - pw.w / 2, bl.y - pw.h - 10, { vy: 120 });
  // prazo curto de propósito, como o de cima: a estrela apaga de novo depois de pouco mais de 1 s DE JOGO
  check(await pg.waitForFunction(y => __tintim.player.onGround && Math.abs(__tintim.player.y + __tintim.player.h - y) < 4, bl.y, { timeout: 900, polling: 50 }).then(() => true, () => false), 'estrela acesa: o Timtim fica em pé nela');

  // corvo do trigal: pisar em cima espanta ele
  const ei = await ev(() => { const S = __tintim.S; let k = -1; S.enemies.forEach((e, i) => { if (k < 0 && e.alive && e.x > 2650 && e.x < 4300) k = i; }); return k; });
  check(ei >= 0, 'há corvos andando no trigal');
  if (ei >= 0) {
    await ev(i => { const e = __tintim.S.enemies[i], p = __tintim.player; e.dir = 0; Object.assign(p, { x: e.x + e.w / 2 - p.w / 2, y: e.y - p.h - 6, vx: 0, vy: 250, onGround: false, inv: 0, hp: 3, orbit: null }); }, ei);
    check(await pg.waitForFunction(i => !__tintim.S.enemies[i].alive, ei, { timeout: CINE, polling: 50 }).then(() => true, () => false), 'pular em cima do corvo espanta ele');
    check(await ev(() => __tintim.player.hp === 3), 'o pisão no corvo não tira coração');
  }

  // a carta ao Theo usa o nome certo
  const nt = await ev(() => TT.C.NOTES[0]);
  await put(nt.x - pw.w / 2, nt.y - pw.h / 2, { vy: 0, inv: 99 });
  check(await until(() => document.querySelector('#note small').textContent.startsWith('Carta ao Theo'), CINE), 'o bilhete da fase 3 aparece como "Carta ao Theo"');
  await ev(() => TT.emit('banner', { text: 'TESTE-FAIXA' }));
  check(await ev(() => document.getElementById('banner').textContent !== 'TESTE-FAIXA'), 'com a carta aberta, uma faixa de texto nova não aparece por cima (um texto por vez)');
  await ev(() => { const n = document.getElementById('note'); if (n) n.classList.remove('on'); });

  // o Corvo-Borrão: chegar no morro começa a luta com a apresentação dele
  const ax = await ev(() => TT.C.ARENA_X);
  await ev(() => { __tintim.S.notes = __tintim.S.notes || 0; });
  await put(ax + 200, 452 - 50, { onGround: true, inv: 99 });
  check(await until(() => __tintim.S.arena && __tintim.S.cine && __tintim.S.cine.type === 'fox', CINE), 'chegar no morro apresenta o Corvo-Borrão');
  check(await ev(() => document.body.innerText.includes('CORVO-BORRÃO')), 'o cartão do chefão diz "O CORVO-BORRÃO"');
  check(await until(() => !__tintim.S.cine, CINE), 'depois da apresentação, a luta começa');
  const passou04 = await jogo(0.4); // afirmação negativa: alguns quadros DE JOGO depois da cinemática, não 400 ms de parede
  check(passou04 && await ev(() => { const m = __tintim.R.dbg.fox(), o = m.material.map.offset; return m.visible && Number.isFinite(o.x) && Number.isFinite(o.y); }), 'o Corvo-Borrão continua desenhado depois da apresentação');
  check(await ev(() => document.querySelector('.bossRow b').textContent === 'Corvo-Borrão'), 'a barra de vida mostra "Corvo-Borrão"');
  check(await ev(() => TT.C.SWIRLS.every(s => s.x < TT.C.ARENA_X)), 'o morro do chefão não tem redemoinhos');
  check(await until(() => __tintim.S.fox.state === 'fly', CINE), 'o Corvo-Borrão levanta voo');
  // tubo de tinta: aparece a marca vermelha, o tubo cai ali e machuca quem estiver embaixo
  await ev(() => { const p = __tintim.player; Object.assign(p, { x: TT.C.ARENA_X + 300, y: TT.C.GROUND - p.h, vx: 0, vy: 0, onGround: true, inv: 0, hp: 3, mega: 0, fast: 0 }); __tintim.S.fox.cd = 0; });
  check(await until(() => __tintim.S.fox.state === 'aim', CINE), 'ele mira antes de soltar o tubo (aviso)');
  const tx = await ev(() => __tintim.S.fox.tx);
  check(Math.abs(tx - (await ev(() => TT.C.ARENA_X + 300 + __tintim.player.w / 2))) < 40, 'a marca do tubo fica onde o Timtim está');
  check(await until(() => __tintim.S.tubes.length > 0, CINE), 'o corvo solta um tubo de tinta');
  check(await until(() => __tintim.player.hp === 2, CINE), 'o tubo de tinta machuca quem fica na marca'); 
  check(await until(() => __tintim.S.splats.length > 0 || !__tintim.S.tubes.length, CINE), 'o tubo vira mancha de tinta no chão');
  // no ar ele não leva dano
  await ev(() => { const f = __tintim.S.fox, p = __tintim.player; Object.assign(p, { x: f.x + f.w / 2 - p.w / 2, y: f.y - p.h - 20, vx: 0, vy: 200, onGround: false, inv: 99, hp: 3 }); });
  const passou05 = await jogo(0.5); // afirmação negativa (nada aconteceu): espera tempo DE JOGO em cima dele, não 500 ms de parede
  check(passou05 && await ev(() => __tintim.S.fox.hp === 3), 'voando, o corvo não perde vida');
  // acabados os tubos ele mergulha e fica bicando o chão: é a hora de pular nas costas
  const peck = async () => { await ev(() => { const f = __tintim.S.fox; if (f.state === 'fly') { f.drops = 0; f.cd = 0; } }); return until(() => __tintim.S.fox.state === 'peck', CINE); };
  const stomp = () => ev(() => { const f = __tintim.S.fox, p = __tintim.player; Object.assign(p, { x: f.x + f.w / 2 - p.w / 2, y: f.y - p.h - 30, vx: 0, vy: 250, onGround: false, inv: 99, hp: 3 }); });
  const voou1 = await until(() => __tintim.S.fox.state === 'fly', CINE); // era um until descartado
  check(voou1 && await peck(), 'sem tubos, ele mergulha e fica bicando o chão');
  check(await ev(() => __tintim.R.dbg.fox().userData.name === 'corvo-bica'), 'bicando, toca a animação da bicada (vídeo cortado em quadros)');
  await stomp();
  check(await until(() => __tintim.S.fox.hp === 2 && __tintim.S.fox.state === 'hurt', CINE), 'pular nas costas enquanto ele bica tira um coração');
  check(await until(() => __tintim.S.fox.state === 'fly', CINE), 'depois do golpe ele volta a voar');
  check(await ev(() => __tintim.S.fox.drops === 4), 'na segunda rodada ele joga mais tubos (4)');
  await peck(); await stomp();
  check(await until(() => __tintim.S.fox.hp === 1, CINE), 'segundo golpe nas costas');
  check(await ev(() => __tintim.S.fox.red), 'no último coração o corvo fica vermelho de raiva');
  const voou2 = await until(() => __tintim.S.fox.state === 'fly', CINE); // era um until descartado
  check(voou2 && await ev(() => __tintim.R.dbg.crowRed().visible && __tintim.S.fox.drops === 6), 'vermelho e mais bravo: 6 tubos na última rodada');
  await peck(); await stomp();
  check(await until(() => __tintim.S.fox.hp === 0, CINE), 'o terceiro golpe derrota o Corvo-Borrão');
  check(await ev(() => !!__tintim.S.brush), 'derrotado, ele solta o pincel do Van Gogh');
  check(await until(() => __tintim.S.vg && __tintim.S.vg.mood === 'run', CINE), 'o Van Gogh vem correndo buscar o pincel (não surge do nada)');
  check(await until(() => __tintim.S.vg && __tintim.S.vg.mood === 'happy' && !__tintim.S.brush, CINE), 'o Van Gogh aparece feliz com o pincel');
  check(await ev(() => __tintim.R.dbg.vg().visible && __tintim.R.dbg.vg().userData.name === 'vangogh-feliz'), 'o Van Gogh comemora (pose feliz)');
  check(await until(() => __tintim.player.won && __tintim.R.tintimMesh.userData.name === 'tintim-win', CINE), 'o Timtim comemora com a pose fiel à ficha (sem a animação de olho de panda)');
  check(await until(() => __tintim.state === 'winning' || __tintim.state === 'win', CINE), 'derrotar o Corvo-Borrão vence a fase');
  check(await until(() => document.getElementById('win').classList.contains('on'), CINE), 'tela de vitória aparece');
  check(await ev(() => document.getElementById('winTitle').textContent.includes('pincel') && document.getElementById('stNotes').textContent.includes('Cartas ao Theo')), 'vitória com o texto do pincel e a contagem das cartas ao Theo');
  check(await ev(() => document.querySelector('.winMonkey').src.includes('premio-bolinha') && document.getElementById('winText').textContent.includes('bolinha mordedora')), 'de presente, o Van Gogh dá a bolinha mordedora colorida');
  check(await ev(() => document.getElementById('btnNext').textContent === 'Ver o mapa'), 'na última fase pronta, o botão leva ao mapa');
  await pg.click('#btnNext');
  check(await until(() => TT.mapa.isOpen() && TT.mapa.state().fase === 3, CINE), 'o mapa abre com o Timtim na fase 3');
  await pg.waitForTimeout(700); await ev(() => TT.mapa.walk(4)); await pg.waitForTimeout(300); // de parede: o mapa anda no laço de rAF dele, em performance.now() (mapa.js)
  check(await ev(() => TT.mapa.state().fase === 3 && !TT.mapa.state().walking && TT.mapa.state().sign.includes('QUINTAL')), 'a fase 4 está trancada: o Timtim não anda até ela e a placa mostra o nome (em breve)');
  check(await ev(() => JSON.parse(localStorage.getItem('tintim-fases') || '{}')[3] === true), 'fase 3 fica marcada como vencida');
  check(errs.length === 0, 'sem erros no console' + (errs.length ? ': ' + errs.slice(0, 3).join(' | ') : ''));
  await b.close();
})();
