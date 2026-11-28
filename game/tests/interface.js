// Pisos da interface: no celular, nenhum texto da interface abaixo de 12 px e nenhum alvo de toque abaixo de 44 px.
// Nasceu de uma medição: todos os tamanhos da interface são proporcionais ao container (cqw), e o que é confortável
// no desktop (container de 960 px) encolhe junto no iPhone (container de 390 px) — o texto chegava a 4,3 px e o
// botão de farejar a 31 px. A composição proporcional continua; o piso só impede que ela encolha o que não pode.
//   1. Mede o container do jogo (#stage) nos dois viewports obrigatórios: desktop 960x540 e iPhone 13.
//   2. Em cada tela (capa, pausa, derrota, vitória, estante, carregando) e no jogo rodando (placar, faixa, fala,
//      bilhete), lê getComputedStyle(...).fontSize de todo elemento de texto folha visível: nenhum abaixo de 12 px.
//   3. Lê getBoundingClientRect() dos quatro botões de toque: o menor lado de cada um, no mínimo 44 px
//      (piso usual da Apple e da WCAG). Errar o botão num jogo de plataforma custa um coração.
//   4. Confere que os botões de toque não se sobrepõem depois de crescerem, e que nada passa da borda do container.
//   5. Com o texto no piso, o espaço em volta é que cede: confere que o conteúdo de cada tela (o card, e na
//      capa o bloco do menu) ainda cabe dentro do container, no pior caso (vitória com o placar cheio).
// Uso: (cd game && python3 -m http.server 8765 &) ; node game/tests/interface.js [url]
const { chromium, devices } = require('playwright');
const PISO_TEXTO = 12, PISO_TOQUE = 44;

// mede, dentro da página, todo texto folha visível de cada tela e os alvos de toque
function medir() {
  const stage = document.getElementById('stage');
  const box = stage.getBoundingClientRect();
  const telas = ['title', 'pause', 'lose', 'win', 'shelf'];
  const antes = telas.map(id => document.getElementById(id).classList.contains('on'));
  const textos = [], vistos = new Set();

  // a capa é uma coluna que ocupa a tela toda; o que interessa é onde o conteúdo dela começa e termina
  const medeConteudo = el => {
    const fs = [...el.children].filter(c => c.className !== 'gap' && c.getBoundingClientRect().height);
    const rs = fs.map(c => c.getBoundingClientRect());
    return { top: Math.min(...rs.map(r => r.top)), bottom: Math.max(...rs.map(r => r.bottom)),
      left: Math.min(...rs.map(r => r.left)), right: Math.max(...rs.map(r => r.right)) }; };

  const folha = el => { // elemento de texto folha: tem texto próprio, não só o texto dos filhos
    for (const n of el.childNodes) if (n.nodeType === 3 && n.textContent.trim()) return true;
    return false; };

  const varrer = onde => {
    for (const el of stage.querySelectorAll('*')) {
      if (!folha(el) || el.id === 'storyLine') continue; // storyLine é só para leitores de tela (1 px, recortado)
      const s = getComputedStyle(el);
      const r = el.getBoundingClientRect();
      if (s.visibility === 'hidden' || s.display === 'none' || !r.width || !r.height) continue;
      const nome = (el.id ? '#' + el.id : el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/)[0] : ''));
      const chave = nome + '|' + s.fontSize;
      if (vistos.has(chave)) continue;
      vistos.add(chave);
      textos.push({ nome, onde, px: Math.round(parseFloat(s.fontSize) * 10) / 10, texto: el.textContent.trim().slice(0, 28) });
    } };

  varrer('jogo'); // o que está na tela agora (placar, faixa, fala, bilhete, botões de toque)
  const cards = [];
  for (const id of telas) { // cada tela, uma por vez
    telas.forEach(t => document.getElementById(t).classList.remove('on'));
    document.getElementById(id).classList.add('on');
    varrer(id);
    // o card de cada tela, e na capa o bloco do menu (que não tem card)
    const alvo = document.getElementById(id).querySelector('.card') || document.querySelector('#title .on-anim');
    if (alvo) { const c = (id === 'title' ? medeConteudo(alvo) : alvo.getBoundingClientRect());
      cards.push({ tela: id, cima: Math.round(c.top - box.top), baixo: Math.round(box.bottom - c.bottom),
        esq: Math.round(c.left - box.left), dir: Math.round(box.right - c.right) }); }
  }
  telas.forEach((t, i) => document.getElementById(t).classList.toggle('on', antes[i]));

  const toques = [...document.querySelectorAll('.tbtn')].map(b => {
    const r = b.getBoundingClientRect();
    return { nome: '#' + b.id, w: Math.round(r.width), h: Math.round(r.height), menor: Math.round(Math.min(r.width, r.height)),
      esq: Math.round(r.left - box.left), dir: Math.round(r.right - box.left), topo: Math.round(r.top - box.top), base: Math.round(r.bottom - box.top) };
  });
  return { container: { w: Math.round(box.width), h: Math.round(box.height) }, textos, toques, cards };
}

(async () => {
  const base = process.argv[2] || 'http://localhost:8765/';
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'] });
  const check = (ok, msg) => { console.log((ok ? 'ok   ' : 'FALHA') + ' ' + msg); if (!ok) process.exitCode = 1; };

  const alvos = [
    { nome: 'desktop 960x540', ctx: { viewport: { width: 960, height: 540 } }, toque: false },
    { nome: 'iPhone 13', ctx: { ...devices['iPhone 13'], isMobile: true, hasTouch: true }, toque: true },
  ];

  for (const alvo of alvos) {
    const ctx = await b.newContext(alvo.ctx);
    const pg = await ctx.newPage();
    await pg.goto(base + '?fase=1&q=0&r=' + Date.now() + '#fase1-jogar');
    await pg.waitForFunction(() => window.TT && TT.S, null, { timeout: 30000 });
    await pg.evaluate(() => { if (TT.S.mode === 'title') TT.start(); });
    await pg.waitForFunction(() => TT.S.mode === 'play', null, { timeout: 15000 });
    // põe texto na faixa, na fala e no bilhete: vazios, não medem nada
    await pg.evaluate(() => {
      const p = (id, t) => { const e = document.getElementById(id); e.textContent = t; e.style.opacity = 1; };
      p('banner', 'Fase 1 — o Parque'); p('say', 'Vai, Timtim!');
      const n = document.getElementById('note'); n.style.opacity = 1;
      n.querySelector('small').textContent = 'BILHETE DA TURMA'; n.querySelector('p').textContent = 'A Zara passou por aqui.';
      document.getElementById('hud').style.opacity = 1;
      document.getElementById('btnReset').hidden = false; document.getElementById('skip').style.opacity = 1;
      document.getElementById('msg').style.opacity = 1; document.getElementById('msg').style.visibility = 'visible';
      document.getElementById('faseTag').textContent = '1 · O Parque'; document.getElementById('best').textContent = 'melhor: 42 biscoitos';
      document.getElementById('fases').classList.add('on');
      document.getElementById('shelfCount').textContent = '2 de 5 brinquedos';
      document.getElementById('btnShelf').click(); // desenha os brinquedos de verdade nas prateleiras
      document.getElementById('shelf').classList.remove('on');
      // pior caso do card da vitória: placar cheio (com os bilhetes da turma) e o texto mais comprido
      document.getElementById('stNotes').style.display = '';
      document.getElementById('winText').textContent = 'Timtim, Zara e Elvis resgataram o macaco das patas do Furtão. Continua fedido, e mais amado do que nunca.';
    });
    const m = await pg.evaluate(medir);

    console.log('\n--- ' + alvo.nome + ' --- container ' + m.container.w + 'x' + m.container.h + ' px');
    const miudos = m.textos.filter(t => t.px < PISO_TEXTO).sort((a, b) => a.px - b.px);
    const menores = [...m.textos].sort((a, b) => a.px - b.px).slice(0, 4);
    console.log('menores fontes: ' + menores.map(t => t.px + ' px (' + t.nome + ')').join(', '));
    if (miudos.length) console.log('abaixo do piso: ' + miudos.map(t => t.nome + ' ' + t.px + ' px [' + t.onde + ']').join(', '));
    check(!miudos.length, alvo.nome + ': nenhum texto da interface abaixo de ' + PISO_TEXTO + ' px (' + m.textos.length + ' elementos medidos)');

    const estourou = m.cards.filter(c => c.cima < 0 || c.baixo < 0 || c.esq < 0 || c.dir < 0);
    check(!estourou.length, alvo.nome + ': o conteúdo de cada tela cabe dentro do container, com o placar cheio' +
      (estourou.length ? ' (' + estourou.map(c => c.tela + ' passa ' + Math.abs(Math.min(c.cima, c.baixo, c.esq, c.dir)) + ' px').join(', ') + ')'
        : ' (folga menor: ' + Math.min(...m.cards.map(c => Math.min(c.cima, c.baixo, c.esq, c.dir))) + ' px)'));

    if (alvo.toque) {
      console.log('alvos de toque: ' + m.toques.map(t => t.nome + ' ' + t.w + 'x' + t.h).join(', '));
      const curtos = m.toques.filter(t => t.menor < PISO_TOQUE);
      check(m.toques.length === 4, alvo.nome + ': os quatro botões de toque aparecem no celular');
      check(!curtos.length, alvo.nome + ': nenhum alvo de toque abaixo de ' + PISO_TOQUE + ' px (menor lado) — ' +
        (curtos.length ? curtos.map(t => t.nome + ' ' + t.menor + ' px').join(', ') : m.toques.map(t => t.nome + ' ' + t.menor).join(', ')));
      // crescer o botão não pode encavalar o vizinho nem passar da borda do container
      const ord = [...m.toques].sort((x, y) => x.esq - y.esq);
      const colados = ord.slice(1).map((t, i) => [ord[i], t]).filter(([a, c]) => c.esq < a.dir);
      check(!colados.length, alvo.nome + ': os botões de toque não se encavalam' +
        (colados.length ? ' (' + colados.map(([a, c]) => a.nome + '/' + c.nome).join(', ') + ')' : ''));
      const fora = m.toques.filter(t => t.esq < 0 || t.dir > m.container.w || t.topo < 0 || t.base > m.container.h);
      check(!fora.length, alvo.nome + ': os botões de toque ficam dentro do container' +
        (fora.length ? ' (' + fora.map(t => t.nome).join(', ') + ')' : ''));
    }
    await ctx.close();
  }
  await b.close();
})();
