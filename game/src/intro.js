// Card de introdução de cada fase: um quadro pintado com zoom lento e "vida" desenhada por cima —
// vento nos pelos (deformação suave só nas regiões marcadas), vaga-lumes, folhas e brilhos pulsando.
// Cada quadro tem um pergaminho pintado embaixo; a frase é escrita nele (no canvas, junto com a imagem).
// Tudo em canvas 2D, sem vídeo. Coordenadas das regiões no espaço de cada imagem (1672 × 941 na fase 1, 1376 × 768 nas outras).
(() => {
'use strict';
const TT = window.TT;
const cv = document.getElementById('introC'); if (!cv) return;
const ctx = cv.getContext('2d'), W = cv.width, H = cv.height;
const IW = 1672, IH = 941, FADE = 0.9;
const still = matchMedia('(prefers-reduced-motion: reduce)').matches;
const load = src => { const i = new Image(); i.src = src; return i; };

// zoom: escala inicial → final em torno de um ponto (embaixo no centro, para o pergaminho nunca sair do quadro);
// wind: regiões de pelo (ring = rosto parado, só a borda mexe); scroll: o pergaminho [x0, y0, x1, y1]; sky: até onde vaga-lumes e folhas descem
const SCENES = [
  // fase 1 · O Parque: o Furtão foge com o Macaco Fedido e a turma vai atrás
  { img: load('assets/intro/2-roubo.jpg'), dur: 9.0, zoom: [1.0, 1.04], at: [1200, 941], scroll: [50, 712, 1625, 900], sky: 620,
    wind: [ { x: 1340, y: 330, rx: 260, ry: 210, amp: 1.4, speed: 38, freq: 0.5, jitter: 1 },   // Furtão correndo treme
            { x: 1440, y: 420, rx: 120, ry: 110, amp: 3, speed: 6, freq: 0.07 },                 // macaco balançando na boca
            { x: 450, y: 330, rx: 200, ry: 180, amp: 3, speed: 3.4, freq: 0.04, ring: 1 },       // Timtim assustado
            { x: 170, y: 330, rx: 140, ry: 150, amp: 2.6, speed: 3.4, freq: 0.05, ring: 1 } ],   // Zara
    glow: [ { x: 300, y: 165, r: 70, c: '255,190,90', a: 0.4, pulse: 1.5, flicker: 1 }, { x: 420, y: 140, r: 70, c: '255,70,70', a: 0.4, pulse: 2.1 },
            { x: 585, y: 95, r: 65, c: '120,255,120', a: 0.35, pulse: 1.2 }, { x: 740, y: 35, r: 65, c: '255,70,70', a: 0.35, pulse: 1.8, flicker: 1 } ],
    flies: 16, leaves: 6, windX: 60 },
  // fase 2 · O Arraial: galinhas em pânico e um estranho de chapéu de pato atrás da barraca (imagem 1376 × 768)
  { img: load('assets/intro/fase2.jpg'), iw: 1376, ih: 768, dur: 9.0, zoom: [1.0, 1.04], at: [700, 768], scroll: [20, 578, 1360, 752], sky: 540,
    wind: [ { x: 350, y: 290, rx: 150, ry: 140, amp: 2.6, speed: 3.2, freq: 0.04, ring: 1 },   // Timtim
            { x: 160, y: 340, rx: 120, ry: 120, amp: 2.2, speed: 3.4, freq: 0.05, ring: 1 },   // Zara
            { x: 550, y: 300, rx: 100, ry: 110, amp: 2.2, speed: 3.0, freq: 0.05, ring: 1 },   // Elvis
            { x: 800, y: 420, rx: 110, ry: 110, amp: 1.6, speed: 30, freq: 0.4, jitter: 1 },   // galinhas tremendo de medo
            { x: 1000, y: 440, rx: 100, ry: 100, amp: 1.6, speed: 34, freq: 0.4, jitter: 1 },
            { x: 1160, y: 460, rx: 90, ry: 90, amp: 1.6, speed: 32, freq: 0.4, jitter: 1 } ],
    glow: [ { x: 482, y: 75, r: 70, c: '255,190,90', a: 0.4, pulse: 1.5, flicker: 1 }, { x: 607, y: 40, r: 70, c: '255,150,70', a: 0.4, pulse: 2.1 },
            { x: 350, y: 100, r: 60, c: '255,200,110', a: 0.35, pulse: 1.2 }, { x: 1290, y: 330, r: 220, c: '255,140,60', a: 0.28, pulse: 2.6, flicker: 1 } ],
    flies: 22, leaves: 0, windX: 40, rise: 1 },
  // fase 3 · O Quadro Encantado: o Van Gogh triste e o corvo fugindo com o pincel (imagem 1376 × 768)
  { img: load('assets/intro/fase3.jpg'), iw: 1376, ih: 768, dur: 9.0, zoom: [1.04, 1.0], at: [688, 768], scroll: [20, 640, 1360, 752], sky: 560,
    wind: [ { x: 680, y: 500, rx: 130, ry: 120, amp: 2.6, speed: 3.0, freq: 0.04, ring: 1 },   // Timtim
            { x: 875, y: 520, rx: 70, ry: 80, amp: 2, speed: 3.4, freq: 0.06, ring: 1 },       // Zara
            { x: 1015, y: 545, rx: 85, ry: 80, amp: 2, speed: 3.2, freq: 0.06, ring: 1 },      // Elvis
            { x: 780, y: 170, rx: 130, ry: 100, amp: 3, speed: 9, freq: 0.06 },                // corvo batendo as asas
            { x: 690, y: 330, rx: 700, ry: 330, amp: 1.2, speed: 1.2, freq: 0.012 } ],         // o céu pintado escorrendo devagar
    glow: [ { x: 960, y: 85, r: 150, c: '255,235,120', a: 0.25, pulse: 0.9 }, { x: 290, y: 95, r: 60, c: '255,240,150', a: 0.35, pulse: 1.6 },
            { x: 150, y: 20, r: 55, c: '255,240,150', a: 0.3, pulse: 2.1, flicker: 1 }, { x: 60, y: 265, r: 55, c: '255,240,150', a: 0.3, pulse: 1.3 },
            { x: 225, y: 300, r: 55, c: '255,240,150', a: 0.3, pulse: 1.8 } ],
    flies: 10, leaves: 0, windX: 20 },
];
SCENES.forEach(s => { s.windX = s.windX || 25; s.text = ''; s.iw = s.iw || IW; s.ih = s.ih || IH; });

// canvas de trabalho para o vento nos pelos
const off = document.createElement('canvas'), ox = off.getContext('2d');

// rajadas de vento: sempre um pouco, às vezes mais forte
const gust = t => 0.55 + 0.3 * Math.sin(t * 1.1) + 0.15 * Math.sin(t * 2.7 + 1.3);

function windPatch(img, w, t) {
  const bw = Math.ceil(w.rx * 2), bh = Math.ceil(w.ry * 2), x0 = Math.round(w.x - w.rx), y0 = Math.round(w.y - w.ry);
  if (off.width < bw) off.width = bw; if (off.height < bh) off.height = bh;
  ox.globalCompositeOperation = 'source-over'; ox.clearRect(0, 0, bw, bh);
  const g = w.jitter ? 1 : gust(t), step = 3;
  for (let y = 0; y < bh; y += step) {
    // deslocamento horizontal em onda que desce pelo pelo; nas pontas (baixo/lados) balança mais
    const dx = w.amp * g * Math.sin(y * w.freq + t * w.speed) + (w.jitter ? 0 : w.amp * 0.5 * g);
    ox.drawImage(img, x0, y0 + y, bw, step, dx, y, bw, step);
  }
  // máscara macia: elipse que some na borda; no "ring" o centro (olhos, focinho) fica parado
  ox.globalCompositeOperation = 'destination-in';
  ox.save(); ox.translate(bw / 2, bh / 2); ox.scale(1, w.ry / w.rx);
  const m = ox.createRadialGradient(0, 0, 0, 0, 0, w.rx);
  if (w.ring) { m.addColorStop(0, 'rgba(0,0,0,0)'); m.addColorStop(0.55, 'rgba(0,0,0,0)'); m.addColorStop(0.75, 'rgba(0,0,0,1)'); }
  else { m.addColorStop(0, 'rgba(0,0,0,1)'); m.addColorStop(0.6, 'rgba(0,0,0,1)'); }
  m.addColorStop(1, 'rgba(0,0,0,0)');
  ox.fillStyle = m; ox.fillRect(-w.rx, -w.rx, w.rx * 2, w.rx * 2); ox.restore();
  ctx.drawImage(off, 0, 0, bw, bh, x0, y0, bw, bh);
}

// a frase no pergaminho: tinta marrom, centralizada, que aparece palavra por palavra no ritmo da narração
const FONT = '"Marcellus", Georgia, serif';
function wrap(text, maxW) {
  const words = text.split(' '), lines = []; let cur = '';
  for (const w of words) { const t = cur ? cur + ' ' + w : w; if (ctx.measureText(t).width > maxW && cur) { lines.push(cur); cur = w; } else cur = t; }
  if (cur) lines.push(cur); return lines;
}
function writeScroll(s, t) {
  if (!s.text) return;
  const [x0, y0, x1, y1] = s.scroll, maxW = (x1 - x0) * 0.9;
  let size = 58, lines;
  do { ctx.font = `${size}px ${FONT}`; lines = wrap(s.text, maxW); size -= 2; } while ((lines.length * size * 1.3 > (y1 - y0) * 0.86 || lines.length > 2) && size > 30);
  size += 2; const lh = size * 1.28, cx = (x0 + x1) / 2, top = (y0 + y1) / 2 - (lines.length - 1) * lh / 2;
  // revelação: as palavras surgem ao longo da primeira metade da cena, cada uma num esmaecer rápido
  const total = s.text.split(' ').length, shown = still ? total : Math.max(0, (t - 0.3) / (s.dur * 0.5)) * total;
  ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; let k = 0; const base = ctx.globalAlpha;
  lines.forEach((ln, i) => {
    let x = cx - ctx.measureText(ln).width / 2; const y = top + i * lh;
    for (const w of ln.split(' ')) {
      const a = Math.max(0, Math.min(1, shown - k)); k++;
      if (a > 0) { ctx.globalAlpha = a * base; ctx.fillStyle = 'rgba(255,240,200,.55)'; ctx.fillText(w, x + 1.5, y + 2); ctx.fillStyle = '#4a2410'; ctx.fillText(w, x, y + (1 - a) * 8); }
      x += ctx.measureText(w + ' ').width;
    }
  });
  ctx.globalAlpha = base;
}

function makeParts(s) {
  const r = Math.random, p = [];
  for (let i = 0; i < s.flies; i++) p.push({ k: 'fly', x: r() * s.iw, y: 40 + r() * (s.sky - 40) + (s.rise ? 120 : 0), ph: r() * 9, sz: 2 + r() * 3, sp: 0.4 + r() * 0.8 });
  for (let i = 0; i < s.leaves; i++) p.push({ k: 'leaf', x: -r() * s.iw, y: r() * s.sky * 0.6, ph: r() * 9, sz: 9 + r() * 9, sp: 0.7 + r() * 0.6 });
  return p;
}

function drawScene(s, t, alpha, outgoing) {
  const img = s.img; if (!img.complete || !img.naturalWidth) return;
  const k = Math.min(1, t / s.dur), e = k * k * (3 - 2 * k) * 0.35 + k * 0.65; // zoom contínuo, levemente suavizado
  const IW = s.iw, IH = s.ih, sc = (s.zoom[0] + (s.zoom[1] - s.zoom[0]) * e) * Math.max(W / IW, H / IH);
  ctx.save(); ctx.globalAlpha = alpha;
  // zoom em torno de "at", sem deixar borda vazia
  let tx = W / 2 - s.at[0] * sc, ty = H / 2 - s.at[1] * sc;
  tx = Math.min(0, Math.max(W - IW * sc, tx)); ty = Math.min(0, Math.max(H - IH * sc, ty));
  ctx.setTransform(sc, 0, 0, sc, tx, ty);
  ctx.drawImage(img, 0, 0);
  if (!still) for (const w of s.wind) windPatch(img, w, t);
  ctx.globalCompositeOperation = 'lighter';
  for (const g of s.glow) {
    let a = g.a * (0.75 + 0.25 * Math.sin(t * g.pulse * 2));
    if (g.flicker) a *= 0.8 + 0.2 * Math.sin(t * 23) * Math.sin(t * 7.3);
    const gr = ctx.createRadialGradient(g.x, g.y, 0, g.x, g.y, g.r);
    gr.addColorStop(0, `rgba(${g.c},${a})`); gr.addColorStop(1, `rgba(${g.c},0)`); ctx.fillStyle = gr; ctx.fillRect(g.x - g.r, g.y - g.r, g.r * 2, g.r * 2);
  }
  for (const p of s.parts) {
    const gx = s.windX * gust(t + p.ph);
    if (p.k === 'fly') {
      const x = (p.x + t * gx * p.sp + Math.sin(t * 1.3 + p.ph) * 14) % IW, y = p.y - (s.rise ? t * 26 * p.sp : 0) + Math.sin(t * 0.9 + p.ph * 2) * 10;
      if (y > s.sky) continue;
      const a = 0.5 + 0.5 * Math.sin(t * 3 * p.sp + p.ph), R = p.sz * 4;
      const gr = ctx.createRadialGradient(x, y, 0, x, y, R);
      gr.addColorStop(0, `rgba(255,236,160,${0.9 * a})`); gr.addColorStop(0.25, `rgba(255,210,110,${0.45 * a})`); gr.addColorStop(1, 'rgba(255,200,100,0)');
      ctx.fillStyle = gr; ctx.fillRect(x - R, y - R, R * 2, R * 2);
    }
  }
  ctx.globalCompositeOperation = 'source-over';
  for (const p of s.parts) if (p.k === 'leaf') {
    const x = p.x + t * 260 * p.sp, y = p.y + t * 40 * p.sp + Math.sin(t * 2 + p.ph) * 24;
    if (x < -30 || x > IW + 30) continue;
    ctx.save(); ctx.translate(x, y); ctx.rotate(t * 3 * p.sp + p.ph); ctx.scale(1, 0.45 + 0.4 * Math.sin(t * 5 + p.ph));
    ctx.fillStyle = 'rgba(30,70,50,.85)'; ctx.beginPath(); ctx.ellipse(0, 0, p.sz, p.sz * 0.5, 0, 0, 7); ctx.fill(); ctx.restore();
  }
  if (!outgoing) writeScroll(s, t); // a frase do quadro que está saindo some na hora; o pergaminho novo cobre o antigo
  ctx.restore();
}

let cur = -1, prev = -1, t0 = 0, tp0 = 0, raf = 0;
function frame(now) {
  raf = requestAnimationFrame(frame);
  const t = (now - t0) / 1000;
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#060a18'; ctx.fillRect(0, 0, W, H);
  if (prev >= 0 && t < FADE) drawScene(SCENES[prev], (now - tp0) / 1000, 1, true);
  if (cur >= 0) drawScene(SCENES[cur], t, Math.min(1, t / FADE));
}
TT.intro = {
  durations: SCENES.map(s => s.dur),
  scene(i, text) { SCENES[i].text = text || ''; const now = performance.now(); prev = cur; tp0 = t0; cur = i; t0 = now; SCENES[i].parts = makeParts(SCENES[i]); if (!raf) raf = requestAnimationFrame(frame); },
  stop() { cancelAnimationFrame(raf); raf = 0; cur = prev = -1; },
};
})();
