"""Páginas de abertura em grade (estilo da capa "Arquivo de Gabinete"): img/ab_<parte>.jpg em 6 x 9 pol.
Fragmentos das obras de cada nível (pelos balões de tools/detalhes.json) e uma célula na cor do nível com o número."""
import json, os, sys, subprocess, tempfile
sys.path.insert(0, '.'); sys.path.insert(0, 'tools')
from PIL import Image
import build
from weasyprint import HTML
W, H, M, G, C, R = 6.0, 9.0, .42, .1, 4, 6
CW, CH = (W - 2 * M - (C - 1) * G) / C, (H - 2 * M - (R - 1) * G) / R
PAPER = '#EEEAE0'
DET = json.load(open('tools/detalhes.json'))
os.makedirs('img/_ab', exist_ok=True)

def crop(k, cx, cy, fw, w, h, name):
    im = Image.open(f'img/{k}.jpg').convert('RGB'); iw, ih = im.size
    cw = fw * iw; ch = cw * h / w
    if ch > ih: ch = ih; cw = ch * w / h
    if cw > iw: cw = iw; ch = cw * h / w
    x0 = max(0, min(iw - cw, cx * iw - cw / 2)); y0 = max(0, min(ih - ch, cy * ih - ch / 2))
    out = f'img/_ab/{name}.jpg'
    im.crop((round(x0), round(y0), round(x0 + cw), round(y0 + ch))).resize((round(w * 200), round(h * 200)), Image.LANCZOS).save(out, quality=88)
    return out

# 16 posições: colunas 0 e 2 em linhas inteiras, 1 e 3 deslocadas meia célula
SLOTS = [(0, .2), (0, 1.2), (0, 2.2), (0, 3.2), (0, 4.2), (1, .7), (1, 1.7), (1, 2.7), (1, 3.7), (1, 4.7),
         (2, .2), (2, 1.2), (2, 2.2), (2, 3.2), (2, 4.2), (3, .7), (3, 1.7), (3, 2.7), (3, 3.7), (3, 4.7)]
def page(nome, crops, num, cor, vazios, azul):
    divs = []; it = iter(crops)
    for i, (c, r) in enumerate(SLOTS):
        x, y = M + c * (CW + G), M + r * (CH + G)
        st = f'left:{x:.3f}in;top:{y:.3f}in;width:{CW:.3f}in;height:{CH:.3f}in;'
        if i == azul:
            divs.append(f'<div class="c" style="{st}background:{cor}"><p>{num}</p></div>')
        elif i in vazios:
            continue
        else:
            k, cx, cy, fw = next(it)
            divs.append(f'<div class="c" style="{st}"><img src="{crop(k, cx, cy, fw, CW, CH, f"{nome}-{i}")}"/></div>')
    html = (f'<!doctype html><html><head><meta charset="utf-8"><style>{build.font_faces()}'
            f'@page{{size:{W}in {H}in;margin:0}}*{{margin:0;padding:0}}body{{background:{PAPER}}}'
            '.c{position:absolute;overflow:hidden}.c img{width:100%;height:100%;object-fit:cover;display:block}'
            '.c p{position:absolute;left:.12in;bottom:.06in;font:400 46pt/1 Disp;color:#F6EFE4}</style></head><body>' + ''.join(divs) + '</body></html>')
    with tempfile.TemporaryDirectory() as td:
        HTML(string=html, base_url=build.ROOT).write_pdf(f'{td}/p.pdf')
        subprocess.run(['pdftoppm', '-r', '200', '-jpeg', '-singlefile', f'{td}/p.pdf', f'{td}/p'], check=True)
        Image.open(f'{td}/p.jpg').save(f'img/ab_{nome}.jpg', quality=88)
    print(nome)

def crops_do_nivel(lv):
    ks = [x['ref'] for x in build.EX if x['lv'] == lv and x.get('ref')]
    ks = list(dict.fromkeys(ks)); out = []
    for k in ks:
        for (cx, cy, sz, *_ ) in DET.get(k, [k, []])[1][:3]:
            out.append((k, cx, cy, max(sz * 1.4, .32)))
    # alterna obras para não pôr dois recortes da mesma obra lado a lado
    a = out[0::2] + out[1::2]
    return a

for n, lid, lab, name, cor, code in build.LEVELS:
    cr = crops_do_nivel(n)
    azul = [7, 12, 2, 17, 6][n - 1]
    vazios = set([{0, 9, 15}, {5, 14, 19}, {0, 10, 19}, {4, 5, 15}, {9, 10, 14}][n - 1])
    borda = [0, 19, 4, 15, 5, 14, 9, 10, 18, 1]
    for b in borda:
        if len(SLOTS) - 1 - len(vazios) <= len(cr): break
        if b != azul: vazios.add(b)
    page(lid, cr, str(n), cor, vazios, azul)
# abertura: os dez retratos
g = [('g_leonardo', .5, .32, .55), ('g_durer', .45, .42, .6), ('g_michelangelo', .45, .4, .6), ('g_holbein', .45, .38, .6), ('g_rembrandt', .48, .35, .45),
     ('g_ingres', .5, .3, .55), ('g_degas', .45, .2, .55), ('g_vangogh', .55, .35, .55), ('g_sargent', .45, .25, .5), ('g_schiele', .45, .25, .6)]
page('parte1', g, '10', '#3B6386', {0, 4, 5, 9, 10, 14, 15, 19, 18}, 12)
