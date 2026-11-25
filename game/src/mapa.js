// Mapa-múndi do Timtim: uma ilha em pixel art 16-bit onde ele anda de fase em fase, como nos mapas dos jogos clássicos.
// O caminho é um só (o rastro de cheiro que o Timtim fareja em todas as fases): sai do Parque e passa por cada fase, em fila.
// Tudo é desenhado num canvas de 458x256 pixels ampliado sem suavizar. O que se mexe, em laço:
// o mar (ondas no raso turquesa e no fundo azul, espuma nas pedras, brilhos), a cachoeira caindo, o céu do Van Gogh girando,
// a fogueira e as bandeirinhas do Arraial, os vaga-lumes e lampiões do Parque, a roupa no varal e a fumaça da chaminé
// do Quintal, as nuvens e os olhos do Furtão piscando no escuro da caverna.
// Uso: TT.mapa.open({ at, walkTo, done, onPlay(fase), onClose }) — at e walkTo são números de fase (1 a 5).
(() => {
  'use strict';
  const TT = window.TT = window.TT || {};
  const W = 458, H = 256;
  const FASES = [
    { x: 102, y: 176, nome: 'O PARQUE' },
    { x: 203, y: 211, nome: 'O ARRAIAL' },
    { x: 230, y: 122, nome: 'O QUADRO ENCANTADO' },
    { x: 323, y: 160, nome: 'O QUINTAL DA VIZINHA', breve: true },
    { x: 358, y: 79, nome: 'O COVIL DO FURTÃO', breve: true },
  ];
  // pontos de passagem de cada trecho (de uma fase para a seguinte): um caminho só, sem atalhos nem bifurcações.
  // Do Parque desce pela grama até o Arraial, atravessa a festa ao lado da fogueira, sobe ao quadro, contorna as moitas
  // até o Quintal e sobe pela beira do penhasco (à direita do varal) até a caverna do Furtão.
  const ROTA = [
    [[102, 176], [135, 192], [160, 207], [185, 215], [203, 211]],
    [[203, 211], [192, 195], [195, 170], [205, 150], [218, 135], [230, 122]],
    [[230, 122], [255, 130], [275, 140], [295, 152], [323, 160]],
    [[323, 160], [355, 158], [385, 156], [404, 142], [408, 115], [396, 96], [358, 79]],
  ];
  // ---------- fonte de pixel 5x7 (maiúsculas, números e acentos) ----------
  const GL = {
    A: '01110100011000111111100011000110001', B: '11110100011000111110100011000111110', C: '01111100001000010000100001000001111',
    D: '11110100011000110001100011000111110', E: '11111100001000011110100001000011111', F: '11111100001000011110100001000010000',
    G: '01111100001000010011100011000101111', H: '10001100011000111111100011000110001', I: '11111001000010000100001000010011111',
    J: '00111000100001000010100101001001100', L: '10000100001000010000100001000011111', M: '10001110111010110101100011000110001',
    N: '10001110011010110011100011000110001', O: '01110100011000110001100011000101110', P: '11110100011000111110100001000010000',
    Q: '01110100011000110001101011001001101', R: '11110100011000111110101001001010001', S: '01111100001000001110000010000111110',
    T: '11111001000010000100001000010000100', U: '10001100011000110001100011000101110', V: '10001100011000110001100010101000100',
    X: '10001100010101000100010101000110001', Z: '11111000010001000100010001000011111', Ã: '01101101100111010001111111000110001',
    Ç: '01111100001000010000011110010001100', '1': '00100011000010000100001000010001110', '2': '01110100010000100010001000100011111',
    '3': '11110000010000101110000010000111110', '4': '00010001100101010010111110001000010', '5': '11111100001111000001000011000101110',
    '·': '000000000010000000000', ' ': '000000000000000000000', '!': '1111101',
  };
  const glyph = ch => { const g = GL[ch] || GL[' ']; return { w: g.length / 7, bits: g }; };
  function textWidth(s) { let w = 0; for (const ch of s) w += glyph(ch).w + 1; return w - 1; }
  function drawText(ctx, s, x, y, color, shadow) {
    for (const pass of shadow ? [1, 0] : [0]) {
      ctx.fillStyle = pass ? shadow : color; let cx = x;
      for (const ch of s) { const g = glyph(ch);
        for (let r = 0; r < 7; r++) for (let c = 0; c < g.w; c++) if (g.bits[r * g.w + c] === '1') ctx.fillRect(cx + c + pass, y + r + pass, 1, 1);
        cx += g.w + 1; }
    }
  }
  // ---------- o caminho: curva suave pelos pontos de passagem, amostrada a cada pixel ----------
  function sampleRoute(pts) {
    const P = [pts[0], ...pts, pts[pts.length - 1]], out = [];
    for (let i = 1; i < P.length - 2; i++) {
      const [p0, p1, p2, p3] = [P[i - 1], P[i], P[i + 1], P[i + 2]];
      for (let t = 0; t < 1; t += 0.02) { const t2 = t * t, t3 = t2 * t;
        const f = (a, b, c, d) => 0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t2 + (-a + 3 * b - 3 * c + d) * t3);
        out.push([f(p0[0], p1[0], p2[0], p3[0]), f(p0[1], p1[1], p2[1], p3[1])]); }
    }
    out.push(pts[pts.length - 1]);
    const res = [out[0]]; let acc = 0;
    for (let i = 1; i < out.length; i++) { const d = Math.hypot(out[i][0] - out[i - 1][0], out[i][1] - out[i - 1][1]); acc += d; if (acc >= 1) { res.push(out[i]); acc = 0; } }
    res.push(pts[pts.length - 1]); return res;
  }
  const TRECHOS = ROTA.map(sampleRoute);

  // ---------- estado ----------
  let root, cv, ctx, base, baseData, frame, img = {}, ready = false, raf = 0, opts = {}, done = {};
  let seaMask, fallMask = [], swirl = [], waves = [], foam = [], fire = [], sparks = [], smoke = [], flies = [], clouds = [], glints = [], eyesT = 0;
  const me = { fase: 1, x: 0, y: 0, path: null, pi: 0, face: 1, walkT: 0, jumpT: 0, dir: 'front' };
  let sign = { t: 0, txt: '', sub: '' }, t0 = 0, last = 0, tick = 0;

  const load = src => new Promise((res, rej) => { const i = new Image(); i.onload = () => res(i); i.onerror = rej; i.src = src; });
  function prepare() {
    const c = document.createElement('canvas'); c.width = W; c.height = H; const x = c.getContext('2d');
    x.drawImage(img.mapa, 0, 0); baseData = x.getImageData(0, 0, W, H); base = baseData.data;
    const rgb = i => [base[i * 4], base[i * 4 + 1], base[i * 4 + 2]];
    // mar: tudo que é azul ou turquesa e encosta na borda da imagem (preenchimento a partir das bordas)
    seaMask = new Uint8Array(W * H);
    const water = i => { const [r, g, b] = rgb(i); return b > r + 40 && (b > 100 || g > 120); };
    const st = []; for (let xx = 0; xx < W; xx++) st.push(xx, (H - 1) * W + xx); for (let yy = 0; yy < H; yy++) st.push(yy * W, yy * W + W - 1);
    while (st.length) { const i = st.pop(); if (seaMask[i] || !water(i)) continue; seaMask[i] = 1; const xx = i % W, yy = (i / W) | 0;
      if (xx > 0) st.push(i - 1); if (xx < W - 1) st.push(i + 1); if (yy > 0) st.push(i - W); if (yy < H - 1) st.push(i + W); }
    // espuma: os pixels claros encostados no mar (beira da praia e volta das pedras)
    for (let i = W; i < W * (H - 1); i++) { if (seaMask[i]) continue; const [r, g, b] = rgb(i);
      if (r > 190 && g > 205 && b > 205 && (seaMask[i - 1] || seaMask[i + 1] || seaMask[i - W] || seaMask[i + W])) foam.push(i); }
    // cachoeira: o azul e o branco da queda d'água à direita
    for (let yy = 158; yy < 210; yy++) for (let xx = 368; xx < 402; xx++) { const i = yy * W + xx, [r, g, b] = rgb(i); if (b > r + 25 || (r > 200 && g > 215 && b > 220)) fallMask.push(i); }
    // céu do Van Gogh: os pixels azuis, brancos e amarelos do quadro do céu estrelado (sem o cipreste e sem a moldura dourada)
    for (let yy = 37; yy < 79; yy++) for (let xx = 186; xx < 274; xx++) { const i = yy * W + xx; if (seaMask[i]) continue;
      if (xx > 236 && yy > 66) continue; const [r, g, b] = rgb(i); if (b > r + 25 || (r > 190 && g > 170 && b > 110)) swirl.push(i); }
    // bandeirinhas do Arraial e roupa no varal do Quintal: pixels coloridos que balançam (o que fica atrás é a cor de cima)
    const wavy = (x0, x1, y0, y1, test) => { for (let xx = x0; xx < x1; xx++) for (let yy = y0; yy < y1; yy++) { const i = yy * W + xx, c = rgb(i); if (test(c)) waves.push({ i, x: xx, y: yy, c, under: rgb(i - W * 2) }); } };
    const vivid = ([r, g, b]) => Math.max(r, g, b) - Math.min(r, g, b) > 70 && !(g > r && g > b);
    wavy(168, 252, 141, 162, vivid);
    wavy(306, 328, 112, 123, ([r, g, b]) => (r > 180 && g > 180 && b > 180) || vivid([r, g, b]));
    flies = Array.from({ length: 14 }, () => ({ x: 52 + Math.random() * 100, y: 92 + Math.random() * 70, ph: Math.random() * 6, sp: 0.6 + Math.random() }));
    clouds = [{ x: 10, y: 10, s: 4 }, { x: 300, y: 232, s: 3 }];
    glints = Array.from({ length: 22 }, () => { let i; do { i = (Math.random() * W * H) | 0; } while (!seaMask[i]); return { i, ph: Math.random() * 9 }; });
    frame = ctx.createImageData(W, H);
  }

  // ---------- desenho ----------
  const LAMPS = [[82, 138], [124, 138]], FIRE = [210, 190], CHIMNEY = [356, 99], CAVE = [370, 52], SWIRLS = [[233, 58], [207, 52], [262, 50]];
  function shade(d, j, k, add = 0) { d[j] = Math.min(255, base[j] * k + add); d[j + 1] = Math.min(255, base[j + 1] * k + add); d[j + 2] = Math.min(255, base[j + 2] * k + add); }
  function paintBase(t) {
    const d = frame.data; d.set(base);
    // mar: ondas que correm em diagonal; nas cristas o azul clareia, nos vales escurece (pouco, como a água dos mapas 16-bit)
    for (let i = 0; i < W * H; i++) { if (!seaMask[i]) continue; const x = i % W, y = (i / W) | 0;
      const w = Math.sin(x * 0.19 + y * 0.55 - t * 1.6) + Math.sin(x * 0.07 - y * 0.27 + t * 1.1) + 0.6 * Math.sin(x * 0.45 - t * 2.2);
      if (w > 1.8) shade(d, i * 4, 1.12, 12); else if (w < -1.95) shade(d, i * 4, 0.9); }
    // brilhos do sol na água
    for (const g of glints) { const k = Math.sin(t * 2.2 + g.ph); if (k > 0.86) { const j = g.i * 4; d[j] = d[j + 1] = d[j + 2] = 255; } }
    // espuma respirando na beira
    for (const i of foam) { const x = i % W, y = (i / W) | 0; if (Math.sin(x * 0.9 + y * 0.7 + t * 2.6) > 0.55) shade(d, i * 4, 0.86); }
    // cachoeira: faixas claras descendo
    for (const i of fallMask) { const x = i % W, y = (i / W) | 0, w = Math.sin(y * 0.9 - t * 9 + Math.sin(x * 1.3) * 1.5);
      if (w > 0.6) shade(d, i * 4, 1.18, 18); else if (w < -0.7) shade(d, i * 4, 0.9); }
    // o céu do quadro gira: o brilho das pinceladas corre em volta dos centros dos redemoinhos
    for (const i of swirl) { const x = i % W, y = (i / W) | 0; let best = SWIRLS[0], bd = 1e9;
      for (const c of SWIRLS) { const dd = (x - c[0]) ** 2 + (y - c[1]) ** 2; if (dd < bd) { bd = dd; best = c; } }
      const a = Math.atan2(y - best[1], x - best[0]), r = Math.sqrt(bd), w = Math.sin(a * 2 + r * 0.5 - t * 2.4);
      if (w > 0.55) shade(d, i * 4, 1.2); else if (w < -0.7) shade(d, i * 4, 0.84); }
    // bandeirinhas e roupa no varal balançando (cada coluna sobe ou desce um pixel, em onda)
    for (const q of waves) { const j = q.i * 4; d[j] = q.under[0]; d[j + 1] = q.under[1]; d[j + 2] = q.under[2]; }
    for (const q of waves) { const off = Math.round(Math.sin(q.x * 0.45 - t * 4) * 0.9), k = ((q.y + off) * W + q.x) * 4; d[k] = q.c[0]; d[k + 1] = q.c[1]; d[k + 2] = q.c[2]; }
    ctx.putImageData(frame, 0, 0);
  }
  function px(x, y, c, a = 1) { ctx.globalAlpha = a; ctx.fillStyle = c; ctx.fillRect(x | 0, y | 0, 1, 1); ctx.globalAlpha = 1; }
  function glow(x, y, r, c, a) { for (let k = r; k > 0; k--) { ctx.globalAlpha = a * (1 - k / (r + 1)) * 0.5; ctx.fillStyle = c; ctx.beginPath(); ctx.arc(x, y, k, 0, 7); ctx.fill(); } ctx.globalAlpha = 1; }
  function drawLife(t) {
    // lampiões do Parque respirando e vaga-lumes piscando
    LAMPS.forEach(([x, y], k) => glow(x, y - 6, 8, '#9fd8ff', 0.5 + 0.25 * Math.sin(t * 2 + k)));
    for (const f of flies) { const on = Math.sin(t * 3 * f.sp + f.ph) > 0.2; if (!on) continue;
      px(f.x + Math.sin(t * 0.7 + f.ph) * 4, f.y + Math.cos(t * 0.5 + f.ph) * 3, '#eaff7a'); }
    // fogueira do Arraial: chama de pixels que muda a cada quadro, faíscas subindo
    glow(FIRE[0], FIRE[1] - 4, 12, '#ffb040', 0.55 + 0.15 * Math.sin(t * 9));
    if (tick % 2 === 0) fire = Array.from({ length: 9 }, (_, c) => 3 + Math.round(Math.random() * (c === 4 ? 8 : c === 3 || c === 5 ? 7 : c === 2 || c === 6 ? 5 : 3)));
    fire.forEach((h, c) => { for (let r = 0; r < h; r++) px(FIRE[0] - 4 + c, FIRE[1] - r, r > h - 2 ? '#fff3a0' : r > h - 4 ? '#ffc23a' : '#ff6a1a'); });
    if (Math.random() < 0.25) sparks.push({ x: FIRE[0] + (Math.random() - 0.5) * 5, y: FIRE[1] - 6, v: 8 + Math.random() * 10, life: 1 });
    sparks = sparks.filter(s => (s.life -= 0.03) > 0); sparks.forEach(s => { s.y -= s.v / 30; s.x += Math.sin(t * 6 + s.v) * 0.2; px(s.x, s.y, '#ffd25a', s.life); });
    // fumaça da chaminé do Quintal
    if (tick % 6 === 0) smoke.push({ x: CHIMNEY[0], y: CHIMNEY[1], life: 1 });
    smoke = smoke.filter(s => (s.life -= 0.012) > 0); smoke.forEach(s => { s.y -= 0.12; s.x += 0.05; const r = 1 + (1 - s.life) * 2.2;
      ctx.globalAlpha = s.life * 0.7; ctx.fillStyle = '#e8e4ee'; ctx.fillRect(Math.round(s.x - r), Math.round(s.y - r), Math.round(r * 2), Math.round(r * 2)); ctx.globalAlpha = 1; });
    // os olhos do Furtão no escuro da caverna: aparecem, piscam e somem
    eyesT += 1 / 30; const cyc = eyesT % 7;
    if (cyc > 2 && cyc < 5.5 && !(cyc > 3.6 && cyc < 3.75)) { [-3, 3].forEach(o => { px(CAVE[0] + o, CAVE[1], '#ffe14d'); px(CAVE[0] + o + 1, CAVE[1], '#ffe14d'); }); }
    // nuvens passando devagar (e dando a volta)
    for (const c of clouds) { c.x += 0.05 * c.s / 4; if (c.x > W + 30) c.x = -40; cloud(c.x, c.y); }
  }
  function cloud(x, y) {
    const rows = ['....xxxx......', '..xxxxxxxx.xx.', '.xxxxxxxxxxxxx', 'xxxxxxxxxxxxxx', '.ssssssssssss.'];
    rows.forEach((r, j) => { for (let i = 0; i < r.length; i++) if (r[i] !== '.') px(x + i, y + j, r[i] === 's' ? '#bcd6f2' : '#ffffff'); });
  }
  function drawRoute(t) {
    const liberadas = maxOpen();
    TRECHOS.forEach((pts, i) => {
      const aberto = i + 2 <= liberadas; // trecho até uma fase liberada: a trilha de terra inteira
      if (aberto) {
        ctx.fillStyle = '#6e4526'; for (const [x, y] of pts) ctx.fillRect(Math.round(x) - 3, Math.round(y) - 2, 7, 5);
        ctx.fillStyle = '#ad6c3e'; for (const [x, y] of pts) ctx.fillRect(Math.round(x) - 2, Math.round(y) - 1, 5, 3);
        ctx.fillStyle = '#cb8b4b'; for (const [x, y] of pts) ctx.fillRect(Math.round(x) - 2, Math.round(y) - 1, 5, 2);
      }
      // as pegadas do rastro de cheiro (nas fases ainda fechadas, só elas aparecem, bem de leve)
      for (let k = 6; k < pts.length - 6; k += 7) { const [x, y] = pts[k], [x2, y2] = pts[Math.min(pts.length - 1, k + 1)];
        const nx = -(y2 - y), ny = x2 - x, side = (k / 7) % 2 ? 1 : -1;
        const qx = Math.round(x + nx * side), qy = Math.round(y + ny * side);
        ctx.globalAlpha = aberto ? 1 : 0.5 + 0.25 * Math.sin(t * 2 - k * 0.2); ctx.fillStyle = aberto ? '#7a4a28' : '#fff1c6';
        ctx.fillRect(qx, qy, 1, 1); ctx.fillRect(qx - 1, qy - 1, 1, 1); ctx.fillRect(qx + 1, qy - 1, 1, 1); ctx.globalAlpha = 1; }
    });
  }
  function drawNodes(t) {
    const liberadas = maxOpen();
    FASES.forEach((f, i) => { const n = i + 1, x = f.x, y = f.y, open = n <= liberadas, ok = !!done[n];
      ctx.fillStyle = '#2a1e2c'; ctx.fillRect(x - 6, y - 3, 13, 7); ctx.fillRect(x - 5, y - 4, 11, 9);
      const c = !open ? ['#7d7688', '#a9a2b4'] : ok ? ['#d8a21c', '#ffe066'] : ['#d7303a', '#ff7a6e'];
      const pulse = open && !ok ? (Math.sin(t * 5) > 0 ? 1 : 0) : 0;
      ctx.fillStyle = c[0]; ctx.fillRect(x - 5, y - 2, 11, 5); ctx.fillRect(x - 4, y - 3, 9, 7);
      ctx.fillStyle = c[1]; ctx.fillRect(x - 3, y - 2 - pulse, 5, 2);
      if (!open && !f.breve) { // cadeado (fase liberável, ainda não alcançada)
        ctx.fillStyle = '#2a1e2c'; ctx.fillRect(x - 2, y - 9, 5, 1); ctx.fillRect(x - 3, y - 8, 1, 3); ctx.fillRect(x + 3, y - 8, 1, 3);
        ctx.fillRect(x - 4, y - 5, 9, 5); ctx.fillStyle = '#ffd34a'; ctx.fillRect(x - 3, y - 4, 7, 3); ctx.fillStyle = '#2a1e2c'; ctx.fillRect(x, y - 4, 1, 2); }
      if (f.breve) ribbon(x, y + 9, t, n);
      if (ok) { ctx.fillStyle = '#2a1e2c'; ctx.fillRect(x + 4, y - 12, 1, 10); ctx.fillStyle = Math.sin(t * 6) > 0 ? '#ff4a5a' : '#ff6a78'; ctx.fillRect(x + 5, y - 12, 5, 3); ctx.fillRect(x + 5, y - 11, 6, 1); } // bandeirinha: fase vencida
    });
  }
  // faixa de 'EM BREVE' com cadeado, embaixo de cada fase que ainda não existe; balança de leve e treme quando o Timtim tenta entrar
  const shake = {};
  function ribbon(cx, top, t, n) {
    const txt = 'EM BREVE', tw = textWidth(txt), w = tw + 21, h = 11, s = shake[n] > 0 ? Math.round(Math.sin(t * 60) * 2) : 0;
    const x = Math.round(cx - w / 2) + s, y = top + (Math.sin(t * 2 + n) > 0.7 ? 1 : 0), INK = '#2a1e2c';
    // pontas dobradas (rabo de andorinha) atrás, mais escuras
    ctx.fillStyle = INK; ctx.fillRect(x - 6, y + 2, 8, h); ctx.fillRect(x + w - 2, y + 2, 8, h);
    ctx.fillStyle = '#8e1f2a'; ctx.fillRect(x - 5, y + 3, 6, h - 2); ctx.fillRect(x + w - 1, y + 3, 6, h - 2);
    ctx.fillStyle = INK; ctx.fillRect(x - 6, y + 6, 2, 3); ctx.fillRect(x + w + 4, y + 6, 2, 3); // o corte em V das pontas
    // a faixa da frente
    ctx.fillStyle = INK; ctx.fillRect(x - 1, y - 1, w + 2, h + 2);
    ctx.fillStyle = '#d7303a'; ctx.fillRect(x, y, w, h); ctx.fillStyle = '#ff6a6e'; ctx.fillRect(x, y, w, 1); ctx.fillStyle = '#a8212c'; ctx.fillRect(x, y + h - 1, w, 1);
    // cadeado dourado
    const lx = x + 3, ly = y + 2;
    ctx.fillStyle = INK; ctx.fillRect(lx + 1, ly - 1, 4, 1); ctx.fillRect(lx, ly, 1, 3); ctx.fillRect(lx + 5, ly, 1, 3); ctx.fillRect(lx - 1, ly + 3, 8, 6);
    ctx.fillStyle = '#ffd34a'; ctx.fillRect(lx, ly + 4, 6, 4); ctx.fillStyle = '#fff1a0'; ctx.fillRect(lx, ly + 4, 6, 1); ctx.fillStyle = INK; ctx.fillRect(lx + 2, ly + 5, 2, 2);
    drawText(ctx, txt, x + 13, y + 2, '#fff1cc', '#5a121a');
  }
  function drawTimtim(t) {
    const S = img.tim, fw = S.width / 6, fh = S.height; let f = 0, bob = 0, flip = false;
    if (me.path) { const step = Math.floor(me.walkT * 8) % 2;
      if (me.dir === 'side') { f = 3 + step; flip = me.face < 0; } else f = 1 + step; }
    else if (me.jumpT > 0) { f = 5; bob = -Math.round(Math.sin(Math.min(1, me.jumpT / 0.7) * Math.PI) * 6); }
    else { f = 0; bob = Math.sin(t * 4) > 0.6 ? -1 : 0; }
    const x = Math.round(me.x - fw / 2), y = Math.round(me.y - fh + 3 + bob);
    ctx.fillStyle = 'rgba(30,20,40,.35)'; ctx.fillRect(Math.round(me.x) - 7, Math.round(me.y) + 1, 15, 2); // sombra
    ctx.save(); if (flip) { ctx.translate(x + fw, y); ctx.scale(-1, 1); ctx.drawImage(S, f * fw, 0, fw, fh, 0, 0, fw, fh); } else ctx.drawImage(S, f * fw, 0, fw, fh, x, y, fw, fh); ctx.restore();
  }
  function drawSign(t) {
    if (!sign.txt) return; sign.t = Math.min(1, sign.t + 1 / 12);
    const w = Math.max(textWidth(sign.txt), sign.sub ? textWidth(sign.sub) : 0) + 14, h = sign.sub ? 25 : 15;
    const x = Math.round(8 - (w + 10) * Math.pow(1 - sign.t, 3)), y = 8; // entra pela esquerda, no canto de cima, sobre o mar aberto
    ctx.fillStyle = '#2a1e2c'; ctx.fillRect(x - 1, y, w + 2, h); ctx.fillRect(x, y - 1, w, h + 2);
    ctx.fillStyle = '#9a5c2e'; ctx.fillRect(x, y, w, h); ctx.fillStyle = '#c07a40'; ctx.fillRect(x, y, w, 2); ctx.fillStyle = '#6e3e1e'; ctx.fillRect(x, y + h - 2, w, 2);
    [[x + 2, y + 2], [x + w - 3, y + 2], [x + 2, y + h - 3], [x + w - 3, y + h - 3]].forEach(([a, b]) => { ctx.fillStyle = '#e7c58a'; ctx.fillRect(a, b, 1, 1); }); // pregos
    drawText(ctx, sign.txt, x + 7, y + 4, '#fff1cc', '#3a2216');
    if (sign.sub) drawText(ctx, sign.sub, x + 7, y + 14, Math.sin(t * 4) > -0.3 ? '#ffe066' : '#c9a84c', '#3a2216');
  }

  // ---------- andar e escolher ----------
  // fases liberadas: a 1, cada uma depois de vencida a anterior, e no mínimo a fase da página aberta (quem chega direto nela pode jogar)
  const maxOpen = () => { let n = Math.max(1, opts.minOpen || 1); for (let f = n + 1; f <= 5; f++) if (done[f - 1] && !FASES[f - 1].breve) n = f; else break; return n; };
  function pathBetween(a, b) {
    let pts = []; if (a === b) return null;
    if (b > a) for (let i = a - 1; i < b - 1; i++) pts = pts.concat(TRECHOS[i]);
    else for (let i = a - 2; i >= b - 1; i--) pts = pts.concat(TRECHOS[i].slice().reverse());
    return pts;
  }
  function walk(to) {
    if (to < 1 || to > 5 || me.path) return;
    if (to > maxOpen()) { const f = FASES[to - 1]; shake[to] = 0.4; TT.sfx && TT.sfx('bonk'); sign.t = 0; sign.txt = `FASE ${to} · ${f.nome}`; sign.sub = f.breve ? 'EM BREVE' : ''; return; }
    const p = pathBetween(me.fase, to); if (!p) return;
    me.path = p; me.pi = 0; me.to = to; sign.txt = ''; TT.sfx && TT.sfx('jump');
  }
  function showSign() {
    const f = FASES[me.fase - 1]; sign.t = 0; sign.txt = `FASE ${me.fase} · ${f.nome}`;
    sign.sub = f.breve ? 'EM BREVE' : ''; // só o nome da fase, como nos mapas clássicos (Enter ou um toque na fase começa)
  }
  function update(dt, t) {
    if (me.path) { me.walkT += dt; me.pi += dt * 46;
      const i = Math.min(me.path.length - 1, Math.floor(me.pi)), [x, y] = me.path[i], [nx, ny] = me.path[Math.min(me.path.length - 1, i + 3)];
      me.x = x; me.y = y; const dx = nx - x, dy = ny - y; if (Math.abs(dx) > 0.2 || Math.abs(dy) > 0.2) { me.dir = Math.abs(dx) >= Math.abs(dy) * 0.8 ? 'side' : 'front'; if (Math.abs(dx) > 0.2) me.face = Math.sign(dx); }
      if (i >= me.path.length - 1) { me.path = null; me.fase = me.to; me.jumpT = 0.7; showSign(); TT.sfx && TT.sfx('checkpoint'); if (opts.onArrive) opts.onArrive(me.fase); } }
    me.jumpT = Math.max(0, me.jumpT - dt); for (const k in shake) shake[k] = Math.max(0, shake[k] - dt);
  }
  function loop(now) {
    raf = requestAnimationFrame(loop); if (!ready) return;
    const t = (now - t0) / 1000, dt = Math.min(0.05, (now - last) / 1000); last = now; tick++;
    update(dt, t); paintBase(t); drawRoute(t); drawLife(t); drawNodes(t); drawTimtim(t); drawSign(t);
  }
  function play() { const f = me.fase; if (me.path || FASES[f - 1].breve || f > maxOpen()) { TT.sfx && TT.sfx('bonk'); return; } TT.sfx && TT.sfx('ui'); if (opts.onPlay) opts.onPlay(f); }
  function key(e) {
    if (!root || root.hidden) return; const k = e.key;
    if (k === 'ArrowRight' || k === 'ArrowUp' || k === 'd' || k === 'w') { walk(Math.min(5, me.fase + 1)); e.preventDefault(); }
    else if (k === 'ArrowLeft' || k === 'ArrowDown' || k === 'a' || k === 's') { walk(Math.max(1, me.fase - 1)); e.preventDefault(); }
    else if (k === 'Enter' || k === ' ') { play(); e.preventDefault(); }
    else if (k === 'Escape' && opts.onClose) opts.onClose();
  }
  function click(e) {
    const r = cv.getBoundingClientRect(), x = (e.clientX - r.left) / r.width * W, y = (e.clientY - r.top) / r.height * H;
    const n = FASES.findIndex(f => Math.abs(f.x - x) < 12 && Math.abs(f.y - 4 - y) < 14) + 1;
    if (!n) return; if (n === me.fase) play(); else walk(n);
  }

  TT.mapa = {
    FASES, ROTA,
    async open(o = {}) {
      opts = o; done = o.done || {};
      if (!root) {
        root = o.root || document.body; cv = document.createElement('canvas'); cv.width = W; cv.height = H; cv.className = 'mapaCanvas'; cv.setAttribute('aria-label', 'Mapa das fases');
        root.appendChild(cv); ctx = cv.getContext('2d'); ctx.imageSmoothingEnabled = false;
        cv.addEventListener('pointerdown', click); addEventListener('keydown', key);
        const base = o.base || 'assets/mapa/';
        [img.mapa, img.tim] = await Promise.all([load(base + 'mapa.png'), load(base + 'timtim.png')]); prepare();
      }
      root.hidden = false; const at = o.at || 1; me.fase = at; me.x = FASES[at - 1].x; me.y = FASES[at - 1].y; me.path = null; me.dir = 'front';
      t0 = last = performance.now(); ready = true; cancelAnimationFrame(raf); raf = requestAnimationFrame(loop);
      if (o.walkTo && o.walkTo !== at) setTimeout(() => walk(o.walkTo), 700); else setTimeout(showSign, 300);
    },
    close() { ready = false; cancelAnimationFrame(raf); if (root) root.hidden = true; },
    isOpen: () => !!root && !root.hidden && ready, walk, play, state: () => ({ fase: me.fase, walking: !!me.path, x: me.x, y: me.y, sign: sign.txt, open: maxOpen() }),
  };
})();
