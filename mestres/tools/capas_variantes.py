"""Variações de título e fade sobre o mosaico 1-seis-desenhos. Gera out/capas/variantes.jpg."""
import os, sys, subprocess, tempfile, json
sys.path.insert(0, '.'); OUT = sys.argv[1] if len(sys.argv) > 1 else 'out/capas/variantes.jpg'; sys.argv = ['x']
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
 ('B atual', (.73, .66, .73, 1), True, 46, 6.55, 8.15),
 ('B1 fade acaba 0,5 pol. acima', (.66, .59, .66, 1), True, 46, 6.85, 8.4),
 ('B2 idem, título 42 pt', (.68, .61, .68, 1), True, 42, 7.0, 8.4),
 ('B3 fade mais longo e suave', (.66, .5, .66, 1), True, 46, 6.85, 8.4),
 ('B4 fade acaba 0,8 pol. acima', (.62, .55, .62, 1), True, 46, 6.75, 8.3)]
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
cm.save(OUT, quality=88)
print('ok')
