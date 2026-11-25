// Card de introdução de cada fase: um quadro pintado com zoom lento e um pouco de "vida" desenhada por cima (brilhos e vaga-lumes;
// o vento nos pelos e o tremor do Furtão saíram em 25/11/2026: ficavam bobos) —
// vento nos pelos (deformação suave só nas regiões marcadas), vaga-lumes, folhas e brilhos pulsando.
// Cada quadro tem um pergaminho pintado embaixo; a frase é escrita nele (no canvas, junto com a imagem).
// Desde 25/11/2026 cada quadro tem um vídeo curto em loop (Veo 3.1 Lite no Google Flow, com a mesma imagem no primeiro e no último quadro;
// na fase 1 só o trecho bom em vai e volta, na fase 3 o pintor parado igual à imagem),
// desenhado no canvas no lugar da imagem parada; o pergaminho continua vindo da imagem, para a frase não balançar.
// Sem vídeo (ainda carregando, ou com "reduzir movimento"), fica a imagem. Coordenadas no espaço de cada imagem (1672 × 941 na fase 1, 1376 × 768 nas outras).
(() => {
'use strict';
const TT = window.TT;
const cv = document.getElementById('introC'); if (!cv) return;
const ctx = cv.getContext('2d'), W = cv.width, H = cv.height;
const IW = 1672, IH = 941, FADE = 0.9;
const still = matchMedia('(prefers-reduced-motion: reduce)').matches;
const load = src => { const i = new Image(); i.src = src; return i; };
const loadV = src => { if (still) return null; const v = document.createElement('video'); v.muted = true; v.loop = true; v.playsInline = true; v.preload = 'auto'; v.setAttribute('playsinline', ''); v.src = src; return v; };

// zoom: escala inicial → final em torno de um ponto (embaixo no centro, para o pergaminho nunca sair do quadro);
// wind: regiões de pelo (ring = rosto parado, só a borda mexe); scroll: o pergaminho [x0, y0, x1, y1]; sky: até onde vaga-lumes e folhas descem
const SCENES = [
  // Cards de ação (25/11/2026, Google Flow no acabamento da capa, uma cor por fase; trio conferido com as fichas). Imagens 1376 × 768.
  // fase 1 · O Parque (azul): o Furtão foge com o Macaco Fedido e a turma corre atrás; o pergaminho fica à esquerda, o Furtão à direita
  { img: load('assets/intro/2-roubo.jpg'), vid: loadV('assets/intro/2-roubo.mp4'), iw: 1376, ih: 768, dur: 8.4, zoom: [1.065, 1.085], at: [1000, 0], scroll: [40, 612, 760, 742], sky: 560,
    wind: [], glow: [], flies: 12, leaves: 4, windX: 50 },
  // fase 2 · O Arraial (laranja): a turma procura o culpado, as galinhas fogem e o lobo-guará espia da barraca
  { img: load('assets/intro/fase2.jpg'), vid: loadV('assets/intro/fase2.mp4'), iw: 1376, ih: 768, dur: 7.4, zoom: [1.115, 1.14], at: [0, 0], scroll: [40, 588, 1340, 736], sky: 540,
    wind: [], glow: [], flies: 16, leaves: 0, windX: 40, rise: 1 },
  // fase 3 · O Quadro Encantado (azul e amarelo): o corvo foge com o pincel do Van Gogh e a turma dispara pelo trigal
  { img: load('assets/intro/fase3.jpg'), vid: loadV('assets/intro/fase3.mp4'), iw: 1376, ih: 768, dur: 7.0, zoom: [1.05, 1.015], at: [688, 0], scroll: [40, 645, 1345, 748], sky: 560,
    wind: [], glow: [], flies: 8, leaves: 0, windX: 20 },
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
// O pergaminho e a frase são desenhados pelo jogo, iguais nos três cards (25/11/2026): mesmo lugar, mesmo tamanho,
// mesma letra. Cada imagem veio com um pergaminho pintado de um jeito; ele fica escondido atrás deste (a imagem é
// aproximada e presa no topo em cada cena, ver "zoom" e "at" em SCENES).
const PERG = load('assets/intro/pergaminho.jpg');
const BAN = { x: 30, y: 752, w: W - 60, h: 128, r: 34 }, TXT = 44; // em pixels do canvas (1600 × 900)
function drawBanner(alpha) {
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = alpha;
  // faixa escura embaixo de tudo: o que sobra do pergaminho pintado em volta some nela
  const g = ctx.createLinearGradient(0, BAN.y - 40, 0, H); g.addColorStop(0, 'rgba(6,10,24,0)'); g.addColorStop(0.3, 'rgba(6,10,24,.92)'); g.addColorStop(1, 'rgba(6,10,24,1)');
  ctx.fillStyle = g; ctx.fillRect(0, BAN.y - 40, W, H - BAN.y + 40);
  ctx.beginPath(); ctx.roundRect(BAN.x, BAN.y, BAN.w, BAN.h, BAN.r);
  ctx.shadowColor = 'rgba(0,0,0,.55)'; ctx.shadowBlur = 18; ctx.shadowOffsetY = 4; ctx.fillStyle = '#e8c48c'; ctx.fill(); ctx.shadowColor = 'transparent';
  ctx.save(); ctx.clip(); if (PERG.complete && PERG.naturalWidth) ctx.drawImage(PERG, BAN.x, BAN.y, BAN.w, BAN.h);
  const e = ctx.createLinearGradient(0, BAN.y, 0, BAN.y + BAN.h); e.addColorStop(0, 'rgba(120,70,20,.22)'); e.addColorStop(0.18, 'rgba(120,70,20,0)'); e.addColorStop(0.82, 'rgba(120,70,20,0)'); e.addColorStop(1, 'rgba(120,70,20,.28)');
  ctx.fillStyle = e; ctx.fillRect(BAN.x, BAN.y, BAN.w, BAN.h); ctx.restore();
  ctx.lineWidth = 2; ctx.strokeStyle = 'rgba(110,62,22,.55)'; ctx.stroke();
  ctx.restore();
}
function writeScroll(s, t, alpha) {
  if (!s.text) return;
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = alpha;
  const maxW = BAN.w * 0.9; ctx.font = `${TXT}px ${FONT}`;
  let lines = wrap(s.text, maxW);
  // duas linhas: divide a frase ao meio, para não sobrar uma palavra sozinha embaixo
  if (lines.length === 2) { const even = wrap(s.text, Math.min(maxW, ctx.measureText(s.text).width / 2 + TXT * 1.5)); if (even.length === 2) lines = even; }
  const lh = TXT * 1.28, cx = BAN.x + BAN.w / 2, top = BAN.y + BAN.h / 2 - (lines.length - 1) * lh / 2;
  // revelação: as palavras surgem ao longo da primeira metade da cena, cada uma num esmaecer rápido
  const total = s.text.split(' ').length, shown = still ? total : Math.max(0, (t - 0.3) / (s.dur * 0.5)) * total;
  ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; let k = 0;
  lines.forEach((ln, i) => {
    let x = cx - ctx.measureText(ln).width / 2; const y = top + i * lh;
    for (const w of ln.split(' ')) {
      const a = Math.max(0, Math.min(1, shown - k)); k++;
      if (a > 0) { ctx.globalAlpha = a * alpha; ctx.fillStyle = 'rgba(255,240,200,.55)'; ctx.fillText(w, x + 1.5, y + 2); ctx.fillStyle = '#4a2410'; ctx.fillText(w, x, y + (1 - a) * 8); }
      x += ctx.measureText(w + ' ').width;
    }
  });
  ctx.restore();
}

function makeParts(s) {
  const r = Math.random, p = [];
  for (let i = 0; i < s.flies; i++) p.push({ k: 'fly', x: r() * s.iw, y: 40 + r() * (s.sky - 40) + (s.rise ? 120 : 0), ph: r() * 9, sz: 2 + r() * 3, sp: 0.4 + r() * 0.8 });
  for (let i = 0; i < s.leaves; i++) p.push({ k: 'leaf', x: -r() * s.iw, y: r() * s.sky * 0.6, ph: r() * 9, sz: 9 + r() * 9, sp: 0.7 + r() * 0.6 });
  return p;
}

const ENTRA = 0.9; // segundos do fade de entrada da imagem (a partir de quando ela fica pronta)
function drawScene(s, t, alpha, outgoing) {
  const img = s.img; if (!img.complete || !img.naturalWidth) return;
  if (!outgoing) { if (s.prontaEm == null) s.prontaEm = t; const f = Math.min(1, (t - s.prontaEm) / ENTRA); alpha *= f * f * (3 - 2 * f); }
  const k = Math.min(1, t / s.dur), e = k * k * (3 - 2 * k) * 0.35 + k * 0.65; // zoom contínuo, levemente suavizado
  const IW = s.iw, IH = s.ih, sc = (s.zoom[0] + (s.zoom[1] - s.zoom[0]) * e) * Math.max(W / IW, H / IH);
  ctx.save(); ctx.globalAlpha = alpha;
  // zoom em torno de "at", sem deixar borda vazia
  let tx = W / 2 - s.at[0] * sc, ty = H / 2 - s.at[1] * sc;
  tx = Math.min(0, Math.max(W - IW * sc, tx)); ty = Math.min(0, Math.max(H - IH * sc, ty));
  ctx.setTransform(sc, 0, 0, sc, tx, ty);
  const v = s.vid;
  if (v && v.readyState >= 2) ctx.drawImage(v, 0, 0, IW, IH); // o vídeo no lugar da imagem (o pergaminho padrão vai por cima, em frame())
  else ctx.drawImage(img, 0, 0);
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
  ctx.restore();
}

let cur = -1, prev = -1, t0 = 0, tp0 = 0, raf = 0;
function frame(now) {
  raf = requestAnimationFrame(frame);
  const t = (now - t0) / 1000;
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#060a18'; ctx.fillRect(0, 0, W, H);
  if (prev >= 0 && t < FADE) drawScene(SCENES[prev], (now - tp0) / 1000, 1, true);
  if (cur >= 0) drawScene(SCENES[cur], t, Math.min(1, t / FADE));
  // o pergaminho padrão e a frase do quadro atual, por cima de tudo (iguais nos três cards)
  if (cur >= 0) { const sc = SCENES[cur], pr = sc.prontaEm == null ? 0 : Math.min(1, (t - sc.prontaEm) / ENTRA), a = prev >= 0 ? 1 : pr * pr * (3 - 2 * pr);
    if (a > 0) { drawBanner(a); writeScroll(sc, sc.prontaEm == null ? 0 : t - sc.prontaEm, a); } }
}
TT.intro = {
  durations: SCENES.map(s => s.dur),
  scene(i, text) { SCENES[i].text = text || ''; const now = performance.now(); prev = cur; tp0 = t0; cur = i; t0 = now; SCENES[i].parts = makeParts(SCENES[i]); SCENES[i].prontaEm = null;
    const v = SCENES[i].vid; if (v) { try { v.currentTime = 0; } catch (_) {} v.play().catch(() => {}); }
    if (!raf) raf = requestAnimationFrame(frame); },
  stop() { cancelAnimationFrame(raf); raf = 0; cur = prev = -1; SCENES.forEach(s => s.vid && s.vid.pause()); },
};
})();
