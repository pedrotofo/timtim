"""Variações de título e fade sobre o mosaico 1-seis-desenhos. Gera out/capas/variantes.jpg."""
import os, sys, subprocess, tempfile, json
sys.path.insert(0, '.'); sys.argv = ['x']
import numpy as np
from PIL import Image, ImageDraw
import importlib.util
spec = importlib.util.spec_from_file_location('cp', 'tools/capas.py')
src = open('tools/capas.py').read().split("if len(sys.argv) > 2 and sys.argv[1] == 'usar':")[0]
ns = {}; exec(src, ns)
face, W, H, GAP, INK, OPC = ns['face'], ns['W'], ns['H'], ns['GAP'], ns['INK'], ns['OPC']
import build
from weasyprint import HTML

def arte(top, f0, f1, amax, rows=3):
    o = OPC['1-seis-desenhos']; c = 2
    out = Image.new('RGB', (W, H), INK); mh = int(H * top)
    tw = (W - GAP * (c - 1)) // c; th = (mh - GAP * (rows - 1)) // rows
    for i, k in enumerate(o['faces'][:c * rows]):
        out.paste(face(k, tw, th), ((i % c) * (tw + GAP), (i // c) * (th + GAP)))
    a = np.asarray(out, float); yy = np.arange(H)[:, None, None] / H
    t1 = np.clip(1 - yy / .1, 0, 1) * .45
    t2 = np.clip((yy - f0) / (f1 - f0), 0, 1) * amax
    al = np.maximum(t1, t2)
    return Image.fromarray((a * (1 - al) + np.array(INK, float) * al).clip(0, 255).astype('uint8'))

V = [  # nome, (top, f0, f1, amax), título em 2 linhas?, tamanho, topo do título, topo do subtítulo
 ('A atual', (.64, .50, .64, 1), True, 48, 5.75, 7.5),
 ('B 2 linhas, fade curto', (.73, .66, .73, 1), True, 46, 6.55, 8.15),
 ('C 1 linha, fade curto', (.76, .70, .76, 1), False, 37, 7.55, 8.2),
 ('D 2 linhas, rostos até embaixo', (1.0, .52, .78, .72), True, 48, 5.95, 7.65),
 ('E 1 linha, rostos até embaixo', (1.0, .6, .82, .75), False, 37, 7.15, 7.85)]
base = build.COVER_EBOOK.format(fonts=build.font_faces(), nex=build.NEX)
outs = []
for nome, ap, two, sz, tt, dt in V:
    arte(*ap).save('img/_v.jpg', quality=90)
    h = base.replace('img/cover-art.jpg', 'img/_v.jpg')
    h = h.replace('top:5.75in;text-align:center;font:400 48pt/1.02 Serif', f'top:{tt}in;text-align:center;font:400 {sz}pt/1.02 Serif')
    h = h.replace('.d{{position:absolute;left:0;right:0;top:7.5in;'.replace('{{', '{'), f'.d{{position:absolute;left:0;right:0;top:{dt}in;')
    if not two:
        h = h.replace('Grandes Artistas<br>a Lápis', 'Grandes Artistas a Lápis')
    with tempfile.TemporaryDirectory() as td:
        HTML(string=h, base_url=build.ROOT).write_pdf(f'{td}/c.pdf')
        subprocess.run(['pdftoppm', '-r', '100', '-png', '-singlefile', f'{td}/c.pdf', f'{td}/c'], check=True)
        im = Image.open(f'{td}/c.png').convert('RGB').resize((500, 800))
    d = ImageDraw.Draw(im); outs.append((nome, im))
os.remove('img/_v.jpg')
cm = Image.new('RGB', (len(outs) * 520 - 20, 840), 'white'); d = ImageDraw.Draw(cm)
for i, (n, im) in enumerate(outs):
    cm.paste(im, (i * 520, 0)); d.text((i * 520 + 6, 812), n, fill='black')
cm.save('out/capas/variantes.jpg', quality=88)
print('ok')
