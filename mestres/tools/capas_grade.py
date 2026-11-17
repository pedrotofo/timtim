"""Capas em grade (referências: Klara and the Sun; Mamíferos del pasado). Gera out/capas/grade-*.jpg e grade-comparacao.jpg.
Grade de 4 colunas x 6 linhas sobre 6 x 9.6 pol. Cada célula: (col, lin, larg, alt, tipo, conteúdo, cor)."""
import os, sys, subprocess, tempfile, random
sys.path.insert(0, '.')
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
import build
from weasyprint import HTML
W, H, M, G, C, R = 6.0, 9.6, .32, .1, 4, 6
CW, CH = (W - 2 * M - (C - 1) * G) / C, (H - 2 * M - (R - 1) * G) / R
PAPER, INK = '#F1ECE1', '#1E1913'
BLUES = ['#5B87A6', '#4A7699', '#3B6386', '#304F78', '#243B5E']
# detalhe: (obra, x do centro, y do centro, largura do recorte em fração da imagem)
D = {'pag': ('n1_paganini', .53, .17, .3), 'durer': ('n2_durer13', .55, .31, .42), 'girl': ('n4_girl', .45, .42, .5),
     'mother': ('n4_mother', .27, .38, .42), 'more': ('n2_more', .58, .45, .5), 'yeats': ('n3_yeats', .48, .3, .45),
     'pray': ('n3_hands', .45, .42, .85), 'pillow': ('n1_pillows', .74, .21, .45), 'cat': ('n1_cats', .75, .44, .28),
     'drap': ('n3_drapery', .4, .62, .5), 'sibyl': ('n4_sibyl', .5, .22, .45), 'boat': ('n1_boats', .3, .7, .35),
     'dancer': ('n2_dancer', .62, .42, .75), 'lhands': ('n2_hands', .55, .82, .55), 'ideal': ('n3_ideal', .3, .45, .45),
     'lady': ('n4_holbein_lady', .48, .36, .45), 'edith': ('n1_edith', .5, .2, .5), 'crau': ('n5_crau', .5, .45, .32),
     'cat2': ('n1_cats', .3, .57, .3), 'pag_eye': ('n1_paganini', .53, .155, .16), 'mother_eye': ('n4_mother', .3, .34, .2),
     'roulin': ('c_roulin', .5, .37, .62), 'rem': ('g_rembrandt', .47, .33, .5), 'vg': ('g_vangogh', .42, .42, .78), 'dancer2': ('n2_dancer', .66, .3, .62)}
TMP = 'img/_grade'
os.makedirs(TMP, exist_ok=True)

def src(k):
    return f'obras/hd/{k}.jpg' if os.path.exists(f'obras/hd/{k}.jpg') and k != 'n3_ideal' else f'img/{k}.jpg'

def det(name, w, h):
    k, cx, cy, fw = D[name]
    im = Image.open(src(k)).convert('RGB'); iw, ih = im.size
    cw = fw * iw; ch = cw * h / w
    if ch > ih: ch = ih; cw = ch * w / h
    x0 = max(0, min(iw - cw, cx * iw - cw / 2)); y0 = max(0, min(ih - ch, cy * ih - ch / 2))
    out = f'{TMP}/{name}-{round(w*100)}x{round(h*100)}.jpg'
    im.crop((round(x0), round(y0), round(x0 + cw), round(y0 + ch))).resize((round(w * 220), round(h * 220)), Image.LANCZOS).save(out, quality=90)
    return out

def fatias(k, cx, cy, fw, cells, seed=3, jit=.05):
    """Um rosto grande cortado pela grade, com cada fatia levemente deslocada."""
    im = Image.open(src(k)).convert('RGB'); iw, ih = im.size
    gw, gh = W - 2 * M, H - 2 * M
    sw = fw * iw; sh = sw * gh / gw
    x0 = cx * iw - sw / 2; y0 = cy * ih - sh * .4
    sc = sw / gw; rnd = random.Random(seed); out = {}
    for (c, r) in cells:
        dx, dy = rnd.uniform(-jit, jit) * CW, rnd.uniform(-jit, jit) * CH
        px = x0 + (c * (CW + G) + dx) * sc; py = y0 + (r * (CH + G) + dy) * sc
        f = f'{TMP}/{k}-{c}-{r}.jpg'
        im.crop((round(px), round(py), round(px + CW * sc), round(py + CH * sc))).resize((round(CW * 220), round(CH * 220)), Image.LANCZOS).save(f, quality=90)
        out[(c, r)] = f
    return out

def pos(c, r, w=1, h=1):
    return M + c * (CW + G), M + r * (CH + G), w * CW + (w - 1) * G, h * CH + (h - 1) * G

def render(nome, bg, cells, extra_css=''):
    divs = []
    for c, r, w, h, kind, val, col in cells:
        x, y, ww, hh = pos(c, r, w, h)
        st = f'left:{x:.3f}in;top:{y:.3f}in;width:{ww:.3f}in;height:{hh:.3f}in;'
        if kind == 'img':
            divs.append(f'<div class="cell" style="{st}background:{col or PAPER}"><img src="{det(val, ww, hh)}"/></div>')
        elif kind == 'file':
            divs.append(f'<div class="cell" style="{st}"><img src="{val}"/></div>')
        elif kind == 'blank':
            divs.append(f'<div class="cell" style="{st}background:{col or PAPER}"></div>')
        else:
            divs.append(f'<div class="cell txt" style="{st}{"background:" + col + ";" if col else ""}">{val}</div>')
    html = (f'<!doctype html><html><head><meta charset="utf-8"><style>{build.font_faces()}'
            f'@page{{size:{W}in {H}in;margin:0}}*{{margin:0;padding:0}}body{{background:{bg}}}'
            '.cell{position:absolute;overflow:hidden}.cell img{width:100%;height:100%;object-fit:cover;display:block}'
            '.txt{color:#FBF8F1;font:400 30pt/1.02 Serif;padding:.1in .12in;box-sizing:border-box}.txt .ph:last-child{padding-bottom:0}'
            '.t{font:400 33pt/1 Serif;letter-spacing:-.01em}.s{font:italic 400 13pt/1.3 Serif}.a{font:500 9pt/1.4 Sans;letter-spacing:.2em}'
            '.ph{font:700 8.6pt/1.5 Sans;letter-spacing:.16em;margin-top:.22in}.n{font:400 40pt/1 Disp}.l{font:500 7.5pt/1.3 Sans;letter-spacing:.06em}.b{font:400 21pt/1.05 Disp;letter-spacing:.01em}'
            f'{extra_css}</style></head><body>{"".join(divs)}</body></html>')
    with tempfile.TemporaryDirectory() as td:
        HTML(string=html, base_url=build.ROOT).write_pdf(f'{td}/c.pdf')
        subprocess.run(['pdftoppm', '-r', '266.67', '-png', '-singlefile', f'{td}/c.pdf', f'{td}/c'], check=True)
        Image.open(f'{td}/c.png').convert('RGB').resize((1600, 2560), Image.LANCZOS).save(f'out/capas/grade-{nome}.jpg', quality=90)
    print(nome)

NEX = build.NEX
T2 = '<p class="t">Grandes<br/>Artistas<br/>a Lápis</p>'
SUB = '<p class="s">Cinco níveis com dez mestres</p>'
AUT = '<p class="a">PEDRO TORRES</p>'
EXS = f'<p class="s">{NEX} exercícios em cinco níveis</p>'
V = {}
# 1. Museu: fundo azul, uma bailarina de Degas fatiada pela grade, algumas células vazias, textos direto no azul
c1cells = [(c, r) for c in range(4) for r in range(6)]
fd = fatias('n2_dancer', .5, .4, .78, c1cells, seed=1, jit=0)
txt1 = {(0, 0): None, (1, 0): None, (0, 5): None, (1, 5): None, (0, 2): 'sub'}
vaz1 = {(3, 0), (2, 2), (0, 3), (3, 5), (1, 1)}
c1 = [(0, 0, 2, 1, 'txt', '<p class="b">GRANDES<br/>ARTISTAS<br/>A LÁPIS</p>', None),
      (0, 2, 1, 1, 'txt', '<p class="s" style="font-size:14pt">Cinco níveis com dez mestres</p>', None),
      (0, 5, 2, 1, 'txt', f'{AUT}<p class="s" style="margin-top:.12in">{NEX} exercícios<br/>em cinco níveis</p>', None)]
for (c, r), f in fd.items():
    if (c, r) in txt1: continue
    c1.append((c, r, 1, 1, 'blank', '', None) if (c, r) in vaz1 else (c, r, 1, 1, 'file', f, None))
V['1-museu'] = ('#3B6386', c1)
# 2. Klara: um rosto grande cortado pela grade, algumas células trocadas por outros mestres, título numa célula azul
cells2 = [(c, r) for c in range(4) for r in range(1, 5)]
fl = fatias('n1_paganini', .53, .17, .5, cells2)
c2 = [(1, 0, 2, 1, 'txt', '<p class="t" style="font-size:25pt;text-align:center">Grandes Artistas<br/>a Lápis</p>', '#3B6386'),
      (0, 0, 1, 1, 'img', 'pillow', None), (3, 0, 1, 1, 'img', 'cat', None)]
swap = {(0, 3): 'pray', (3, 2): 'boat', (0, 1): 'sibyl'}
for (c, r), f in fl.items():
    c2.append((c, r, 1, 1, 'img', swap[(c, r)], None) if (c, r) in swap else (c, r, 1, 1, 'file', f, None))
c2 += [(0, 5, 4, 1, 'txt', f'<p class="s" style="text-align:center;color:{INK};font-size:15pt">Cinco níveis com dez mestres</p><p class="a" style="text-align:center;color:{INK};margin-top:.18in">PEDRO TORRES</p>', None)]
V['2-um-rosto'] = ('#CFC3AC', c2)
# 3. Dez rostos: todas as células com rostos, título num bloco azul de 2 x 2 no meio
faces = ['durer', 'girl', 'pag', 'mother', 'more', 'yeats', 'ideal', 'lady', 'edith', 'durer', 'girl', 'pag']
c3 = []
order = [(c, r) for r in range(6) for c in range(4) if not (c in (1, 2) and r in (2, 3)) and r < 5]
names = ['durer', 'girl', 'pag', 'mother', 'more', 'yeats', 'ideal', 'lady', 'edith', 'pray', 'cat', 'pillow', 'sibyl', 'boat', 'drap', 'lhands']
for (c, r), n in zip(order, names):
    c3.append((c, r, 1, 1, 'img', n, None))
c3 += [(1, 2, 2, 2, 'txt', f'{T2}<p class="s" style="margin-top:.2in">Cinco níveis<br/>com dez mestres</p>', '#3B6386'),
       (0, 5, 4, 1, 'txt', f'<p class="a" style="color:{INK};text-align:center;margin-top:.25in">PEDRO TORRES</p><p class="s" style="color:{INK};text-align:center;margin-top:.12in">{NEX} exercícios em cinco níveis</p>', None)]
V['3-dez-rostos'] = (PAPER, c3)
# 4. Cinco azuis: os cinco níveis como células de cor
lv = ['Linha e contorno', 'Forma e proporção', 'Luz e sombra', 'Rosto e figura', 'Composição']
c4 = [(0, 0, 4, 1, 'txt', f'<p class="t" style="color:{INK};font-size:30pt">Grandes Artistas a Lápis</p><p class="s" style="color:{INK};margin-top:.1in">Cinco níveis com dez mestres</p>', None)]
lvpos = [(0, 1), (2, 2), (1, 3), (3, 4), (0, 5)]
for i, (c, r) in enumerate(lvpos):
    c4.append((c, r, 1, 1, 'txt', f'<p class="n">{i + 1}</p><p class="l" style="margin-top:.32in">{lv[i]}</p>', BLUES[i]))
rest = [(c, r) for r in range(1, 6) for c in range(4) if (c, r) not in lvpos and (c, r) != (3, 5)]
for (c, r), n in zip(rest, ['durer', 'pillow', 'cat', 'girl', 'pag', 'boat', 'mother', 'pray', 'drap', 'ideal', 'sibyl', 'more', 'dancer', 'yeats', 'lady']):
    c4.append((c, r, 1, 1, 'img', n, None))
c4.append((3, 5, 1, 1, 'txt', f'<p class="a" style="color:{INK};font-size:7.5pt;margin-top:.5in">PEDRO<br/>TORRES</p>', None))
V['4-cinco-azuis'] = (PAPER, c4)
# 5. Papel: fundo creme, poucos fragmentos espalhados, título grande em tinta
c5 = [(0, 0, 3, 2, 'txt', f'<p class="t" style="color:{INK};font-size:44pt">Grandes<br/>Artistas<br/>a Lápis</p>', None),
      (3, 0, 1, 1, 'img', 'durer', None), (3, 1, 1, 1, 'img', 'pillow', None), (0, 2, 1, 1, 'img', 'cat', None), (1, 2, 1, 1, 'img', 'pag', None),
      (2, 2, 2, 1, 'txt', f'<p class="s" style="color:{INK};font-size:15pt;margin-top:.35in">Cinco níveis com dez mestres</p>', None),
      (1, 3, 1, 1, 'img', 'girl', None), (2, 3, 1, 1, 'img', 'mother', None), (0, 4, 1, 1, 'img', 'pray', None), (3, 3, 1, 1, 'img', 'boat', None),
      (2, 4, 1, 1, 'img', 'drap', None), (3, 4, 1, 1, 'img', 'yeats', None), (1, 5, 1, 1, 'img', 'sibyl', None),
      (2, 5, 2, 1, 'txt', f'<p class="a" style="color:{INK};margin-top:.35in">PEDRO TORRES</p><p class="s" style="color:{INK};margin-top:.1in;font-size:11pt">{NEX} exercícios em cinco níveis</p>', None)]
V['5-papel'] = (PAPER, c5)

# --- segunda rodada: bases 5 e 3, título grande no alto, frase dos artistas, nome em duas linhas, uma célula azul
TIT = (f'<p class="t" style="color:{INK};font-size:44pt">Grandes<br/>Artistas<br/>a Lápis</p>'
       f'<p class="ph" style="color:{INK}">DE LEONARDO DA VINCI<br/>A VAN GOGH</p>')
AUT2 = f'<p class="a" style="color:{INK}">PEDRO<br/>TORRES</p><p class="s" style="color:{INK};font-size:10.5pt;margin-top:.12in">{NEX} exercícios<br/>em cinco níveis</p>'
SUBB = '<p class="s" style="font-size:14pt;margin-top:.12in">Cinco níveis<br/>com dez mestres</p>'
V['6-base5'] = (PAPER, [
    (0, 0, 3, 2, 'txt', TIT, None),
    (3, 0, 1, 1, 'img', 'durer', None), (3, 1, 1, 1, 'img', 'pillow', None), (0, 2, 1, 1, 'img', 'cat', None), (1, 2, 1, 1, 'img', 'pag', None),
    (2, 2, 2, 1, 'txt', SUBB, '#3B6386'),
    (1, 3, 1, 1, 'img', 'girl', None), (2, 3, 1, 1, 'img', 'mother', None), (0, 4, 1, 1, 'img', 'pray', None), (3, 3, 1, 1, 'img', 'boat', None),
    (2, 4, 1, 1, 'img', 'drap', None), (3, 4, 1, 1, 'img', 'yeats', None), (1, 5, 1, 1, 'img', 'sibyl', None),
    (2, 5, 2, 1, 'txt', AUT2, None)])
V['7-base3-solta'] = (PAPER, [
    (0, 0, 3, 2, 'txt', TIT, None),
    (3, 0, 1, 1, 'img', 'durer', None), (3, 1, 1, 1, 'img', 'girl', None),
    (0, 2, 1, 1, 'img', 'pag', None), (0, 3, 1, 1, 'img', 'pray', None), (0, 4, 1, 1, 'img', 'cat', None), (0, 5, 1, 1, 'txt', AUT2, None),
    (1, 2.5, 1, 1, 'img', 'mother', None), (1, 3.5, 1, 1, 'img', 'ideal', None), (1, 4.5, 1, 1, 'img', 'sibyl', None),
    (2, 2, 1, 1, 'txt', SUBB.replace('14pt', '12.5pt'), '#3B6386'), (2, 3, 1, 1, 'img', 'drap', None), (2, 4, 1, 1, 'img', 'yeats', None), (2, 5, 1, 1, 'img', 'boat', None),
    (3, 2.5, 1, 1, 'img', 'more', None), (3, 3.5, 1, 1, 'img', 'lady', None), (3, 4.5, 1, 1, 'img', 'edith', None)])
# --- terceira rodada: um rosto por mestre, nome assentado na margem de baixo, sem a linha dos exercícios
TIT3 = (f'<p class="t" style="color:{INK};font-size:44pt">Grandes<br/>Artistas<br/>a Lápis</p>'
        f'<p class="ph" style="color:{INK};font-weight:500">DE LEONARDO DA VINCI<br/>A VAN GOGH</p>')
BOT = 'display:flex;flex-direction:column;justify-content:flex-end;'
V['8-um-por-mestre'] = (PAPER, [
    (0, 0, 3, 2, 'txt', TIT3, None),
    (3, 0, 1, 1, 'img', 'durer', None), (3, 1, 1, 1, 'img', 'girl', None),
    (0, 2, 1, 1, 'img', 'pag', None), (0, 3, 1, 1, 'img', 'pray', None), (0, 4, 1, 1, 'img', 'cat', None),
    (0, 5, 1, 1, 'txt', f'<div style="{BOT}height:100%"><p class="a" style="color:{INK}">PEDRO<br/>TORRES</p></div>', None),
    (1, 2.5, 1, 1, 'img', 'mother', None), (1, 3.5, 1, 1, 'img', 'ideal', None), (1, 4.5, 1, 1, 'img', 'sibyl', None),
    (2, 2, 1, 1, 'txt', f'<div style="{BOT}height:100%"><p class="s" style="font-size:12.5pt">Cinco níveis<br/>com dez mestres</p></div>', '#3B6386'),
    (2, 3, 1, 1, 'img', 'dancer2', None), (2, 4, 1, 1, 'img', 'yeats', None), (2, 5, 1, 1, 'img', 'vg', None),
    (3, 2.5, 1, 1, 'img', 'edith', None), (3, 3.5, 1, 1, 'img', 'rem', None), (3, 4.5, 1, 1, 'img', 'lady', None)])
# --- quarta rodada (canvas-design, "Arquivo de Gabinete"): nome no canto inferior direito, diagonal título-assinatura
RIGHT = 'display:flex;flex-direction:column;justify-content:flex-end;align-items:flex-end;text-align:right;'
V['9-gabinete'] = (PAPER, [
    (0, 0, 3, 2, 'txt', TIT3, None),
    (3, 0, 1, 1, 'img', 'durer', None), (3, 1, 1, 1, 'img', 'girl', None),
    (0, 2, 1, 1, 'img', 'pag', None), (0, 3, 1, 1, 'img', 'pray', None), (0, 4, 1, 1, 'img', 'cat', None), (0, 5, 1, 1, 'img', 'drap', None),
    (1, 2.5, 1, 1, 'img', 'mother', None), (1, 3.5, 1, 1, 'img', 'ideal', None), (1, 4.5, 1, 1, 'img', 'sibyl', None),
    (2, 2, 1, 1, 'txt', f'<div style="{BOT}height:100%"><p class="s" style="font-size:12.5pt">Cinco níveis<br/>com dez mestres</p></div>', '#3B6386'),
    (2, 3, 1, 1, 'img', 'dancer2', None), (2, 4, 1, 1, 'img', 'yeats', None), (2, 5, 1, 1, 'img', 'roulin', None),
    (3, 2.5, 1, 1, 'img', 'edith', None), (3, 3.5, 1, 1, 'img', 'rem', None), (3, 4.5, 1, 1, 'img', 'lady', None),
    (3, 5.5, 1, .5, 'txt', f'<div style="{RIGHT}height:100%;padding:0"><p class="a" style="color:{INK}">PEDRO<br/>TORRES</p></div>', None)])
TIT4 = (f'<p class="t" style="color:{INK};font-size:39pt;white-space:nowrap">Grandes Artistas<br/>a Lápis</p>'
        f'<p class="ph" style="color:{INK};font-weight:500;margin-top:.26in">DE LEONARDO DA VINCI A VAN GOGH</p>')
TIT4b = (f'<div style="display:flex;flex-direction:column;justify-content:space-between;height:100%">'
         f'<p class="t" style="color:{INK};font-size:39pt;white-space:nowrap">Grandes Artistas<br/>a Lápis</p>'
         f'<p class="ph" style="color:{INK};font-weight:500;margin:0">DE LEONARDO DA VINCI A VAN GOGH</p></div>')
V['10-gabinete-2linhas'] = (PAPER, [(0, 0, 3, 2, 'txt', TIT4b, None)] + V['9-gabinete'][1][1:])
if len(sys.argv) > 1:
    V = {k: v for k, v in V.items() if k in sys.argv[1:]}
for nome, (bg, cells) in V.items():
    render(nome, bg, cells)
ims = [Image.open(f'out/capas/grade-{n}.jpg').resize((500, 800)) for n in (sys.argv[1:] or ['1-museu', '2-um-rosto', '3-dez-rostos', '4-cinco-azuis', '5-papel']) if os.path.exists(f'out/capas/grade-{n}.jpg')]
cm = Image.new('RGB', (len(ims) * 520 - 20, 800), 'white')
for i, im in enumerate(ims): cm.paste(im, (i * 520, 0))
cm.save('out/capas/grade-comparacao' + ('-' + '-'.join(sys.argv[1:]) if len(sys.argv) > 1 else '') + '.jpg', quality=88)
