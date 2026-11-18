"""Desenha linhas de corrente (setas em ocre) sobre uma obra. Gera img/flow-<obra>.jpg."""
import json, math, os, sys
from PIL import Image, ImageDraw
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLAY = (191, 110, 50)
TINTA = (20, 16, 12)   # versão para o impresso em preto e branco: o ocre viraria um cinza claro sobre o desenho

def draw(key, lines, centers=(), src=None, out=None, dim=.45, width=None, impresso=False):
    im = Image.open(os.path.join(ROOT, 'img', f'{src or key}.jpg')).convert('RGB')
    S = 1600 / max(im.size); im = im.resize((round(im.width * S), round(im.height * S)), Image.LANCZOS)
    W, H = im.size
    # esmaece a obra para as setas aparecerem
    im = Image.blend(im, Image.new('RGB', im.size, (245, 240, 230)), dim)
    d = ImageDraw.Draw(im)
    lw = width or max(5, round(W / 220))
    cor = TINTA if impresso else CLAY
    def P(p): return (p[0] / 100 * W, p[1] / 100 * H)
    for ln in lines:
        pts = [P(p) for p in ln]
        # curva suave (Catmull-Rom)
        sm = []
        for i in range(len(pts) - 1):
            p0 = pts[i - 1] if i else pts[i]; p1 = pts[i]; p2 = pts[i + 1]; p3 = pts[i + 2] if i + 2 < len(pts) else p2
            for t in [j / 12 for j in range(12)]:
                t2, t3 = t * t, t * t * t
                sm.append(tuple(.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2 + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3) for k in (0, 1)))
        sm.append(pts[-1])
        if impresso:  # contorno branco para a seta não se confundir com o traço da obra
            d.line(sm, fill=(255, 255, 255), width=lw * 2 + 4, joint='curve')
        d.line(sm, fill=cor, width=lw, joint='curve')
        (x0, y0), (x1, y1) = sm[-4], sm[-1]
        a = math.atan2(y1 - y0, x1 - x0); L = lw * 3.6
        d.polygon([(x1 + math.cos(a) * lw, y1 + math.sin(a) * lw),
                   (x1 - L * math.cos(a - .45), y1 - L * math.sin(a - .45)),
                   (x1 - L * math.cos(a + .45), y1 - L * math.sin(a + .45))], fill=cor, outline=(255, 255, 255) if impresso else None)
    for c in centers:
        x, y = P(c[:2]); r = c[2] / 100 * W
        if impresso:
            d.ellipse((x - r - lw / 2 - 2, y - r - lw / 2 - 2, x + r + lw / 2 + 2, y + r + lw / 2 + 2), outline=(255, 255, 255), width=lw * 2 + 4)
        d.ellipse((x - r, y - r, x + r, y + r), outline=cor, width=lw)
        d.ellipse((x - lw * 1.4, y - lw * 1.4, x + lw * 1.4, y + lw * 1.4), fill=cor)
    im.save(os.path.join(ROOT, 'img', 'hd' if impresso else '', out or f'flow-{key}.jpg'), quality=88)

if __name__ == '__main__':
    PL = json.load(open(os.path.join(ROOT, 'data.json')))['pl']
    imp = '--impresso' in sys.argv
    for k in [a for a in sys.argv[1:] if not a.startswith('--')]:
        draw(k, PL[k]['flow'], PL[k].get('centers', []), impresso=imp)
