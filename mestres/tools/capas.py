"""Capas em mosaico de rostos (Grandes Artistas a Lápis).
Cada rosto: (arquivo em obras/hd ou obras, x dos olhos, y dos olhos, altura do recorte) em frações da imagem.
Cada opção: lista de rostos e grade (colunas, linhas). O mosaico ocupa a parte de cima da capa (proporção 6 x 9.6)
e a parte de baixo fica escura para o título. Gera out/capas/capa-opcao-*.jpg e uma comparação.
Para aplicar uma: python3 tools/capas.py usar NOME"""
import os, sys, json, subprocess, tempfile
sys.path.insert(0, '.')
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS = None
W, H = 1800, 2880          # 6 x 9.6 pol. a 300 dpi
GAP = 10
INK = (30, 25, 19)
ROSTOS = json.load(open('tools/rostos.json'))   # chave: [arquivo, x olhos, y olhos, altura do recorte]
OPC = json.load(open('tools/capas_opcoes.json'))  # nome: {"faces": [...], "cols": c, "rows": r, "top": fração da altura usada}

def face(k, w, h):
    f, cx, cy, fh = ROSTOS[k]
    p = f'img/{f}.jpg' if f in ('n3_ideal',) else (f'obras/hd/{f}.jpg' if os.path.exists(f'obras/hd/{f}.jpg') else f'obras/{f}.jpg')
    im = Image.open(p).convert('RGB'); iw, ih = im.size
    ch = fh * ih; cw = ch * w / h
    if cw > iw:
        cw = iw; ch = cw * h / w
    x0 = cx * iw - cw / 2; y0 = cy * ih - ch * .42   # olhos um pouco acima do meio
    x0 = max(0, min(iw - cw, x0)); y0 = max(0, min(ih - ch, y0))
    return im.crop((round(x0), round(y0), round(x0 + cw), round(y0 + ch))).resize((w, h), Image.LANCZOS)

def mosaico(nome):
    o = OPC[nome]; c, r = o['cols'], o['rows']; top = o.get('top', .6)
    out = Image.new('RGB', (W, H), INK)
    mh = int(H * top)
    tw = (W - GAP * (c - 1)) // c; th = (mh - GAP * (r - 1)) // r
    for i, k in enumerate(o['faces']):
        x, y = (i % c) * (tw + GAP), (i // c) * (th + GAP)
        out.paste(face(k, tw, th), (x, y))
    # sombra: topo (atrás do nome) e transição para a faixa escura
    import numpy as np
    a = np.asarray(out, float); yy = np.arange(H)[:, None, None] / H
    t1 = np.clip(1 - yy / .1, 0, 1) * .45
    t2 = np.clip((yy - (top - .14)) / .14, 0, 1)
    al = np.maximum(t1, t2)
    a = a * (1 - al) + np.array(INK, float) * al
    return Image.fromarray(a.clip(0, 255).astype('uint8'))

if len(sys.argv) > 2 and sys.argv[1] == 'usar':
    mosaico(sys.argv[2]).save('img/cover-art.jpg', quality=92); print('img/cover-art.jpg <-', sys.argv[2]); sys.exit()
import build
from weasyprint import HTML
os.makedirs('out/capas', exist_ok=True)
for f in os.listdir('out/capas'): os.remove(f'out/capas/{f}')
for nome in OPC:
    mosaico(nome).save('img/_capa_tmp.jpg', quality=92)
    html = build.COVER_EBOOK.format(fonts=build.font_faces(), nex=build.NEX).replace('img/cover-art.jpg', 'img/_capa_tmp.jpg')
    with tempfile.TemporaryDirectory() as td:
        HTML(string=html, base_url=build.ROOT).write_pdf(f'{td}/c.pdf')
        subprocess.run(['pdftoppm', '-r', '266.67', '-png', '-singlefile', f'{td}/c.pdf', f'{td}/c'], check=True)
        Image.open(f'{td}/c.png').convert('RGB').resize((1600, 2560), Image.LANCZOS).save(f'out/capas/capa-opcao-{nome}.jpg', quality=90)
    print(nome)
os.remove('img/_capa_tmp.jpg')
ims = [Image.open(f'out/capas/capa-opcao-{n}.jpg').resize((600, 960)) for n in OPC]
cm = Image.new('RGB', (len(ims) * 620 - 20, 960), 'white')
for i, im in enumerate(ims): cm.paste(im, (i * 620, 0))
cm.save('out/capas/comparacao.jpg', quality=88)
