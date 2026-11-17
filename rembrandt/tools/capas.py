"""Opções de capa no modelo da série (obra sangrando a página, como o Roulin no Van Gogh).
Cada opção: (arquivo em obras/hd, x dos olhos, topo, base) em frações da imagem. O recorte tem a proporção do e-book (6 x 9.6)
e fica centrado nos olhos. Gera out/capas/capa-opcao-*.jpg e uma comparação. Para aplicar uma: python3 tools/capas.py usar NOME"""
import os, sys, subprocess, tempfile, shutil
sys.path.insert(0, '.')
import build
from weasyprint import HTML
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
OPC = {'1-gorro-de-veludo-1638': ('velvet', .43, .18, .97),
       '2-desenhando-a-janela-1648': ('window', .49, .04, .96),
       '3-desenho-a-pena-1628': ('rijks', .40, .06, .95)}
def recorte(nome):
    k, cx, y0, y1 = OPC[nome]
    im = Image.open(f'obras/hd/{k}.jpg').convert('RGB'); w, h = im.size
    H = (y1 - y0) * h; W = H * 6 / 9.6
    x0 = max(0, min(w - W, cx * w - W / 2))
    x0 = max(x0, MARG.get(k, 0) * w)
    return sombra(im.crop((round(x0), round(y0 * h), round(x0 + W), round(y1 * h))))
MARG = {'rijks': .045}
def sombra(im):
    """Escurece o topo (atrás do nome) e a metade de baixo (atrás do título) direto na imagem."""
    import numpy as np
    a = np.asarray(im, float); H = a.shape[0]
    y = np.arange(H)[:, None, None] / H
    top = np.clip(1 - y / .14, 0, 1) * .35
    t = np.clip((y - .44) / .56, 0, 1)
    bot = np.where(t < .45, t / .45 * .55, .55 + (t - .45) / .55 * .15)
    al = np.maximum(top, bot)
    out = a * (1 - al) + np.array([20., 15., 10.]) * al
    return Image.fromarray(out.clip(0, 255).astype('uint8'))
if len(sys.argv) > 2 and sys.argv[1] == 'usar':
    recorte(sys.argv[2]).save('img/cover-art.jpg', quality=93); print('img/cover-art.jpg <-', sys.argv[2]); sys.exit()
os.makedirs('out/capas', exist_ok=True)
for f in os.listdir('out/capas'): os.remove(f'out/capas/{f}')
for nome in OPC:
    recorte(nome).save('img/_capa_tmp.jpg', quality=93)
    html = build.COVER_EBOOK.format(fonts=build.font_faces(), nex=build.NEX).replace('img/cover-art.jpg', 'img/_capa_tmp.jpg')
    with tempfile.TemporaryDirectory() as td:
        HTML(string=html, base_url=build.ROOT).write_pdf(f'{td}/c.pdf')
        subprocess.run(['pdftoppm', '-r', '266.67', '-png', '-singlefile', f'{td}/c.pdf', f'{td}/c'], check=True)
        Image.open(f'{td}/c.png').convert('RGB').resize((1600, 2560), Image.LANCZOS).save(f'out/capas/capa-opcao-{nome}.jpg', quality=90)
    print(nome)
os.remove('img/_capa_tmp.jpg')
ims = [Image.open(f'out/capas/capa-opcao-{n}.jpg').resize((600, 960)) for n in OPC]
c = Image.new('RGB', (len(ims) * 620 - 20, 960), 'white')
for i, im in enumerate(ims): c.paste(im, (i * 620, 0))
c.save('out/capas/comparacao.jpg', quality=88)
