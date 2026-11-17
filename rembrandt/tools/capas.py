"""Gera opções de capa (1600 x 2560) em out/capas/ com a mesma tipografia da capa do livro, trocando só a arte."""
import os, sys, subprocess, tempfile
sys.path.insert(0, '.')
import build
from weasyprint import HTML
from PIL import Image
# opção: (obra, centro x, topo y, base y) em frações da imagem original
OPC = {'A-autorretrato-de-boca-aberta': ('sp_shout', .465, .045, .955),
       'B-autorretrato-de-olhos-arregalados': ('sp_wide', .485, .055, .975),
       'C-hendrickje-dormindo': ('hendrickje', .42, .02, .98)}
os.makedirs('out/capas', exist_ok=True)
for nome, (k, cx, y0, y1) in OPC.items():
    im = Image.open(f'obras/{k}.jpg').convert('RGB'); w, h = im.size
    H = (y1 - y0) * h; W = H * .64
    x0 = max(0, min(w - W, cx * w - W / 2))
    im.crop((round(x0), round(y0 * h), round(x0 + W), round(y1 * h))).save(f'img/capa-{k}.jpg', quality=92)
    html = build.COVER_EBOOK.format(fonts=build.font_faces(), nex=build.NEX).replace('img/capa-gravura.jpg', f'img/capa-{k}.jpg')
    with tempfile.TemporaryDirectory() as td:
        HTML(string=html, base_url=build.ROOT).write_pdf(f'{td}/c.pdf')
        subprocess.run(['pdftoppm', '-r', '266.67', '-png', '-singlefile', f'{td}/c.pdf', f'{td}/c'], check=True)
        Image.open(f'{td}/c.png').convert('RGB').resize((1600, 2560), Image.LANCZOS).save(f'out/capas/capa-opcao-{nome}.jpg', quality=90)
    os.remove(f'img/capa-{k}.jpg')
    print(nome)
fs = ['out/capa-ebook-1600x2560.jpg'] + [f'out/capas/capa-opcao-{n}.jpg' for n in OPC]
ims = [Image.open(f).resize((600, 960)) for f in fs]
c = Image.new('RGB', (4 * 620 - 20, 960), 'white')
for i, im in enumerate(ims): c.paste(im, (i * 620, 0))
c.save('out/capas/comparacao-atual-A-B-C.jpg', quality=88)
