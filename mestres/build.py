"""Monta o livro Grandes Artistas a Lápis em PDF (WeasyPrint) e EPUB 3 a partir de src/*.md e data.json."""
import os, re, json, glob, html, uuid, zipfile, datetime
import markdown
from lxml import etree, html as lhtml

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
D = json.load(open('data.json'))
EX, PL, FI = D['ex'], D['pl'], D['fi']
NEX = len(EX)
NMESTRES = 10
esc = html.escape

# ---------------------------------------------------------------- níveis e exercícios
# nível, id da parte, rótulo, nome, cor, código dos exercícios
LEVELS = [(1, 'nivel1', 'Nível 1', 'Linha e contorno', '#5B87A6', 'L'),
          (2, 'nivel2', 'Nível 2', 'Forma e proporção', '#4A7699', 'F'),
          (3, 'nivel3', 'Nível 3', 'Luz e sombra', '#3B6386', 'S'),
          (4, 'nivel4', 'Nível 4', 'Rosto e figura', '#304F78', 'R'),
          (5, 'nivel5', 'Nível 5', 'Composição', '#243B5E', 'C')]
LV = {l[0]: l for l in LEVELS}
STN = ['Esboço', 'Primeiras linhas', 'Tons', 'Acabado']
STAGES = {x['id'] for x in EX if x.get('st')}
AULA_LV = {}   # id do capítulo -> nível (preenchido em build_sections)

def ex_img(x):
    return x.get('img') or x['id'].lower()

def ex_html(x):
    out = [f'<section class="ex" id="ex-{x["id"]}">',
           f'<p class="exnum">{x["id"]}</p>',
           f'<h3>{esc(x["t"])}</h3>']
    if os.path.exists(f'img/{ex_img(x)}.jpg'):
        out.append(f'<figure class="model"><img src="img/{ex_img(x)}.jpg" alt="Modelo do exercício {x["id"]}"/></figure>')
    out += [f'<p class="exmeta">{esc(x["m"])}</p>', f'<p>{esc(x["d"])}</p>',
            f'<p class="crit"><span class="sc">Pronto quando</span> {esc(x["c"])}</p>']
    if x.get('ref') and x['ref'] in PL:
        out.append(f'<p class="exref">Obra: <a href="#cat-{x["ref"]}"><i>{esc(PL[x["ref"]]["t"])}</i></a>, {esc(PL[x["ref"]]["a"])}.</p>')
    out.append('</section>')
    return '\n'.join(out)

# ---------------------------------------------------------------- leitura das fontes
def parse_src():
    secs = []
    for f in sorted(glob.glob('src/*.md')):
        txt = open(f).read()
        parts = re.split(r'<!-- id: (.*?) -->', txt)
        for i in range(1, len(parts), 2):
            meta = [p.strip() for p in parts[i].split('|')]
            body = parts[i + 1].strip()
            secs.append({'id': meta[0], 'title': meta[1], 'kind': meta[2], 'opener': meta[3] if len(meta) > 3 else None, 'md': body})
    return secs

MD = markdown.Markdown(extensions=['md_in_html', 'tables'])
def obra_block(m):
    k = m.group(1); p = PL[k]
    return (f'<div class="obra"><figure><img src="img/{k}.jpg" alt="{esc(p["t"])}"/>'
            f'<figcaption><i>{esc(p["t"])}</i>, {esc(p["a"])}. {esc(p["l"])}</figcaption></figure></div>')

def md2html(s):
    MD.reset()
    s = re.sub(r'\{\{obra:([a-z0-9_]+)\}\}', obra_block, s)
    if '{{marcas}}' in s: s = s.replace('{{marcas}}', marcas_html())
    if '{{progresso}}' in s: s = s.replace('{{progresso}}', progresso_html())
    h = MD.convert(s)
    return h.replace('src="ex/', 'src="img/').replace('{NEX}', str(NEX)).replace('{NMESTRES}', str(NMESTRES))

def practice_line(chid):
    items = [x for x in EX if x['aula'] == chid]
    if not items:
        return ''
    first, last = items[0]['id'], items[-1]['id']
    lk = lambda c: f'<a href="#ex-{c}">{c}</a>'
    pg = lambda c: f'<a class="pg" href="#ex-{c}"></a>'
    txt = (f'<b>Para praticar</b> {lk(first)} a {lk(last)} · p. {pg(first)} a {pg(last)}' if first != last
           else f'<b>Para praticar</b> {lk(first)} · p. {pg(first)}')
    return f'<p class="pline">{txt}</p>'

def build_sections():
    src = parse_src()
    S = []
    lv = None
    for s in src:
        h = md2html(s['md'])
        if s['id'] in ('como-usar', 'cap1'):
            h = add_icons(h)
        if s['kind'] == 'part' and s['id'].startswith('nivel'):
            lv = int(s['id'][5:])
        if s['id'] == 'mestres':
            h = h + vidas_html() + tracos_html()
        if s['kind'] == 'chapter' and lv:
            AULA_LV[s['id']] = lv
            h = add_balloons(h)
            exs = [x for x in EX if x['aula'] == s['id']]
            if exs:
                s = {**s, 'exs': exs, 'epub_extra': '<h2>Para praticar</h2>' + '\n'.join(ex_html(x) for x in exs)}
            h += practice_line(s['id'])
        S.append({**s, 'html': h, 'lv': lv if s['kind'] in ('chapter', 'part') else None})
    return S

CAT_ORDER = list(PL)  # ordem do livro

def catalogue():
    order = [k for k in CAT_ORDER if k in PL] + [k for k in PL if k not in CAT_ORDER]
    rows = []
    for i, k in enumerate(order, 1):
        p = PL[k]; f = FI.get(k, {})
        ficha = ' · '.join(v for v in [f.get('tec'), f.get('dim')] if v)
        rows.append(f'<div class="cat" id="cat-{k}"><img src="img/{k}.jpg" alt="{esc(p["t"])}"/><div><p class="ct"><span class="cn">{i}</span> <i>{esc(p["t"])}</i> · {esc(p["a"])}</p>'
                    f'<p class="cc">{esc(p["c"])}</p>' + (f'<p class="cf">{esc(ficha)}</p>' if ficha else '') + f'<p class="cl">{esc(p.get("l", ""))}</p></div></div>')
    intro = ('<p>As obras dos mestres estudadas no livro, na ordem em que aparecem, com a técnica, '
             'as dimensões (altura por largura) e o acervo, quando disponíveis.</p>')
    return {'id': 'catalogo', 'title': 'Catálogo das obras', 'kind': 'back', 'html': '<h1>Catálogo das obras</h1>' + intro + ''.join(rows)}

CREDITS = {'id': 'creditos', 'title': 'Créditos', 'kind': 'back', 'html': md2html(
"""# Créditos

As reproduções das obras de Leonardo da Vinci, Albrecht Dürer, Michelangelo, Hans Holbein, o Jovem, Rembrandt van Rijn, Jean-Auguste-Dominique Ingres, Edgar Degas, Vincent van Gogh, John Singer Sargent e Egon Schiele, e os retratos feitos por Daniele da Volterra e Henri de Toulouse-Lautrec, são de domínio público e foram obtidas no Wikimedia Commons, a partir das imagens de acesso aberto dos museus indicados no catálogo. Os dados das obras vêm dos museus e do Wikimedia Commons. As citações são traduções livres do autor.

Os desenhos-modelo dos exercícios e as demonstrações em etapas foram criados para este livro com o auxílio de ferramentas de inteligência artificial, a partir de orientações do autor. São interpretações a lápis no espírito dos desenhos de cada mestre e não reproduzem obras deles. Os ícones foram desenhados para este livro.

Texto composto em EB Garamond e Archivo.""")}

# ---------------------------------------------------------------- detalhes das obras (balões logo depois de cada obra)
# obra: (imagem de origem, [(centro x, centro y, lado como fração da largura, título, texto)])
WORK_DETAILS = json.load(open('tools/detalhes.json')) if os.path.exists('tools/detalhes.json') else {}

def make_details():
    from PIL import Image
    for key, (src, items) in WORK_DETAILS.items():
        for i, (cx, cy, sz, *rest) in enumerate(items, 1):
            im = Image.open(f'img/{rest[2] if len(rest) > 2 else src}.jpg').convert('RGB')
            side = sz * im.width
            x0 = max(0, min(im.width - side, cx * im.width - side / 2))
            y0 = max(0, min(im.height - side, cy * im.height - side / 2))
            im.crop((round(x0), round(y0), round(x0 + side), round(y0 + side))).resize((520, 520), Image.LANCZOS).save(f'img/det-{key}-{i}.jpg', quality=90)

def balloons_html(key):
    src, items = WORK_DETAILS[key]
    cells = ''.join(f'<figure class="bal"><img src="img/det-{key}-{i}.jpg" alt="{esc(t)}"/>'
                    f'<figcaption><b>{esc(t)}</b> {esc(d)}</figcaption></figure>'
                    for i, (cx, cy, sz, t, d, *_) in enumerate(items, 1))
    return f'<div class="balrow n{len(items)}">{cells}</div>'

def add_balloons(h):
    done = set()
    def rep(m):
        key = m.group(1)
        if key not in WORK_DETAILS or key in done:
            return m.group(0)
        done.add(key)
        from PIL import Image
        w_, h_ = Image.open(f'img/{key}.jpg').size
        side = h_ > w_ * 1.05
        return f'<div class="figbal{" side" if side else ""}">{m.group(0)}{balloons_html(key)}</div>'
    h = re.sub(r'<div class="figbal side">(<figure>.*?</figure>)</div>', r'\1', h, flags=re.S)
    return re.sub(r'<figure[^>]*>\s*<img src="img/([a-z0-9_]+)\.jpg"[^>]*>.*?</figure>', rep, h, flags=re.S)

# ---------------------------------------------------------------- ícones e linha do tempo
ICONS_H2 = {'Por onde começar': 'comecar', 'Os desenhos-modelo': 'modelo', 'Material para desenhar por cima': 'imprimir',
            'As vozes': 'cartas', 'As aulas': 'moldura', 'O que eles usavam': 'junco', 'Como segurar o lápis': 'lapis', 'A pressão': 'giz',
            'O papel': 'papel', 'No tablet': 'tablet'}

def add_icons(h):
    return re.sub(r'<h2>([^<]+)</h2>', lambda m: (f'<h2 class="ic"><img class="icon" src="img/icons/{ICONS_H2[m.group(1)]}.svg" alt=""/>{m.group(1)}</h2>'
                                                  if m.group(1) in ICONS_H2 else m.group(0)), h)

# ano, artista, imagem, centro x, centro y, largura (fração), obra, texto
TRACOS = json.load(open('tools/tracos.json')) if os.path.exists('tools/tracos.json') else []
XTR = json.load(open('tools/extras.json')) if os.path.exists('tools/extras.json') else {'cmp': {}, 'marcas': [], 'vidas': []}

def vidas_html():
    y0, y1 = 1440, 1930
    X = lambda y: (y - y0) / (y1 - y0) * 100
    ticks = ''.join(f'<span class="vt" style="left:{X(y):.2f}%"><i>{y}</i></span>' for y in range(1450, 1951, 50) if y <= 1925)
    rows = ''.join(f'<div class="vr"><p class="vn">{esc(n)}</p><div class="vb">{ticks if i == 0 else ""}'
                   f'<span class="bar" style="left:{X(a):.2f}%;width:{X(b) - X(a):.2f}%"></span>'
                   f'<span class="vy" style="left:{X(a):.2f}%">{a}</span><span class="vy e" style="left:{X(b):.2f}%">{b}</span></div></div>'
                   for i, (n, a, b) in enumerate(XTR['vidas']))
    grid = ''.join(f'<span class="vg" style="left:{X(y):.2f}%"></span>' for y in range(1450, 1951, 50) if y <= 1925)
    return ('<div class="vidas" id="toc-vidas"><h2>Dez vidas, quase cinco séculos</h2><p class="sub">Quem foi contemporâneo de quem. '
            'Leonardo, Dürer e Michelangelo viveram ao mesmo tempo. Degas, Van Gogh, Sargent e Schiele também.</p>'
            f'<div class="vgrid"><div class="vlines">{grid}</div>{rows}</div></div>')

def cmp_html(lv):
    d = XTR['cmp'].get(str(lv))
    if not d:
        return ''
    n, lid, lab, name, cor, code = LV[lv]
    it = ''.join(f'<div class="ci"><img src="img/cmp-{lv}-{i}.jpg" alt="Detalhe, {esc(m)}"/><div><p class="cm">{esc(m)}</p>'
                 f'<p class="co"><i>{esc(PL[k]["t"])}</i></p><p class="ct2">{esc(t)}</p></div></div>'
                 for i, (k, cx, cy, fw, m, t) in enumerate(d['it'], 1))
    return (f'<section class="cmp lv{lv}" id="cmp-{lv}" style="bookmark-level:2;bookmark-label:\'Três mestres · {esc(d["t"])}\'">'
            f'<span class="rh">Três mestres</span><p class="chlab">{lab} · {name}</p><p class="ck">O mesmo problema, três mestres</p>'
            f'<h1>{esc(d["t"])}</h1><p class="lead">{esc(d["i"])}</p>{it}</section>')

def marcas_html():
    cells = ''.join(f'<div class="mk"><img src="img/marca-{i:02d}.jpg" alt="Marca de {esc(n)}"/><div><p class="mn2">{esc(n)}</p>'
                    f'<p class="mm">{esc(m)}</p><p class="ma"><a href="#cap{a}">Aula {a}</a></p></div></div>'
                    for i, (n, m, k, cx, cy, fw, a) in enumerate(XTR['marcas'], 1))
    return f'<div class="marcas">{cells}</div>'

def progresso_html():
    out = ''
    for n, lid, lab, name, cor, code in LEVELS:
        bx = ''.join(f'<span class="pb" style="border-color:{cor}"><b>{x["id"]}</b></span>' for x in EX if x['lv'] == n)
        out += f'<div class="pl"><p style="color:{cor}">{lab} · {name}</p><div class="pbs">{bx}</div></div>'
    return f'<div class="prog">{out}</div>'


def make_tracos():
    from PIL import Image
    for i, (yy, pl, k, cx, cy, w, t, tx) in enumerate(TRACOS, 1):
        im = Image.open(f'img/{k}.jpg').convert('RGB'); W = w * im.width; H = W / 2.1
        x0 = max(0, min(im.width - W, cx * im.width - W / 2)); y0 = max(0, min(im.height - H, cy * im.height - H / 2))
        im.crop((round(x0), round(y0), round(x0 + W), round(y0 + H))).resize((840, 400), Image.LANCZOS).save(f'img/traco-{i:02d}.jpg', quality=90)

def map_html(inline=True):
    return ''

def tracos_html():
    if not TRACOS:
        return ''
    def row(i, x):
        yy, pl, k, cx, cy, w, t, tx = x
        return (f'<div class="tr"><img src="img/traco-{i:02d}.jpg" alt="Detalhe de {esc(t)}"/>'
                f'<div class="trt"><p class="ty">{yy}</p><p class="tp">{pl} · <i>{esc(t)}</i></p><p>{tx}</p></div></div>')
    rows = [row(i, x) for i, x in enumerate(TRACOS, 1)]
    return ('<div class="tracos" id="toc-tracos"><h2>Quatrocentos anos em dez traços</h2><p class="sub">Um desenho de cada mestre, do mais antigo ao mais recente.</p>'
            + ''.join(rows[:5]) + '<div class="tr2">' + ''.join(rows[5:]) + '</div></div>')

# ---------------------------------------------------------------- PDF (edição ilustrada)
FONTDIR = os.path.join(ROOT, 'fonts')
PARTS = {'parte1': ('10', 'Abertura', 'Os dez mestres', '<p>Quem foram os artistas deste livro, quando viveram e o que cada um tem a ensinar a quem desenha a lápis. Uma página para cada um, e no fim uma linha do tempo com um desenho de cada.</p>'),
         'nivel1': ('1', 'Nível 1', 'Linha e contorno', '<p>O material, a pressão da mão e os tipos de linha. Travesseiros, gatos, barcos e as primeiras pessoas, desenhados só com o contorno e quase nenhuma sombra.</p>'),
         'nivel2': ('2', 'Nível 2', 'Forma e proporção', '<p>Medir com o olho: onde ficam os olhos numa cabeça, o tamanho de uma mão, o peso de um corpo sentado. Ainda com pouca sombra, mas agora com as medidas no lugar.</p>'),
         'nivel3': ('3', 'Nível 3', 'Luz e sombra', '<p>A luz vem de um lado e a forma aparece. Panos, mãos, cabeças e uma pessoa dormindo, construídos com hachura, mancha e papel em branco.</p>'),
         'nivel4': ('4', 'Nível 4', 'Rosto e figura', '<p>Rostos de verdade, sem embelezar, e corpos em movimento. Tudo o que veio antes, a linha, a medida e a luz, junto no mesmo desenho.</p>'),
         'nivel5': ('5', 'Nível 5', 'Composição', '<p>A folha inteira: paisagens, um grupo de pessoas, uma figura sozinha num espaço vazio. Onde pôr as coisas, o que deixar em branco e quando parar. No fim, um projeto seu.</p>')}
LVCOL = {p: LV[int(p[5:])][4] for p in PARTS if p.startswith('nivel')}
END_ART = {}
def bleed_html(spec):
    key, img = spec
    from PIL import Image, ImageStat
    im = Image.open(f'img/{img}.jpg').convert('L')
    w, h = im.size
    lum = ImageStat.Stat(im.crop((0, int(h * .82), w, h))).mean[0]
    dark = lum < 150
    return (f'<section class="bleed{" dark" if dark else ""}"><img src="img/{img}.jpg" alt="{esc(PL[key]["t"])}"/>'
            f'<p class="bcap"><i>{esc(PL[key]["t"])}</i> · {esc(PL[key]["c"])}</p></section>')

PART_ART = json.load(open('tools/part_art.json')) if os.path.exists('tools/part_art.json') else {}

def font_faces(base='file://' + FONTDIR + '/'):
    css = ''
    for w in (400, 500, 600, 700):
        for st in ('normal', 'italic'):
            for sub in ('latin', 'latin-ext'):
                f = f'eb-garamond-{sub}-{w}-{st}.ttf'
                if os.path.exists(os.path.join(FONTDIR, f)):
                    css += f'@font-face{{font-family:"Serif";src:url("{base}{f}");font-weight:{w};font-style:{st}}}\n'
    for f in sorted(os.listdir(FONTDIR)):
        m = re.match(r'archivo-(black-)?latin(-ext)?-(\d+)-(normal|italic)\.woff$', f)
        if m:
            fam = 'Disp' if m.group(1) else 'Sans'
            css += f'@font-face{{font-family:"{fam}";src:url("{base}{f}");font-weight:{m.group(3)};font-style:{m.group(4)}}}\n'
    return css

PDF_CSS = """
@page part1{margin:0;background:#5B87A6;@bottom-left{content:none}@bottom-right{content:none}}\n.lv1 .chnum,.lv1 .pnum2{color:#5B87A6}.lv1 .exfoot .done{border-left-color:#5B87A6}.lv1 .pline a,.lv1 .exref a{border-bottom-color:#5B87A6}\n@page part2{margin:0;background:#4A7699;@bottom-left{content:none}@bottom-right{content:none}}\n.lv2 .chnum,.lv2 .pnum2{color:#4A7699}.lv2 .exfoot .done{border-left-color:#4A7699}.lv2 .pline a,.lv2 .exref a{border-bottom-color:#4A7699}\n@page part3{margin:0;background:#3B6386;@bottom-left{content:none}@bottom-right{content:none}}\n.lv3 .chnum,.lv3 .pnum2{color:#3B6386}.lv3 .exfoot .done{border-left-color:#3B6386}.lv3 .pline a,.lv3 .exref a{border-bottom-color:#3B6386}\n@page part4{margin:0;background:#304F78;@bottom-left{content:none}@bottom-right{content:none}}\n.lv4 .chnum,.lv4 .pnum2{color:#304F78}.lv4 .exfoot .done{border-left-color:#304F78}.lv4 .pline a,.lv4 .exref a{border-bottom-color:#304F78}\n@page part5{margin:0;background:#243B5E;@bottom-left{content:none}@bottom-right{content:none}}\n.lv5 .chnum,.lv5 .pnum2{color:#243B5E}.lv5 .exfoot .done{border-left-color:#243B5E}.lv5 .pline a,.lv5 .exref a{border-bottom-color:#243B5E}\n@page{size:6in 9in;margin:.62in .72in .82in .55in;background:#EEEAE0}
@page :left{margin-left:.55in;margin-right:.72in;
  @bottom-left{content:counter(page) "\\2003" string(sec);font:400 7.2pt Sans;color:#6E6253;vertical-align:top;padding-top:.3in}}
@page :right{margin-left:.72in;margin-right:.55in;
  @bottom-right{content:string(sec) "\\2003" counter(page);font:400 7.2pt Sans;color:#6E6253;vertical-align:top;padding-top:.3in}}
@page full{margin:0;@bottom-left{content:none}@bottom-right{content:none}}
@page part{margin:0;background:#3B6386;@bottom-left{content:none}@bottom-right{content:none}}
@page kraft{margin:0;background:#D6C7A8;@bottom-left{content:none}@bottom-right{content:none}}
@page bare{@bottom-left{content:none}@bottom-right{content:none}}
@page chap:first{@bottom-left{content:none}@bottom-right{content:none}}
:root{--ink:#1E1913;--mute:#6E6253;--soft:#A39682;--clay:#3B6386;--kraft:#D6C7A8;--paper:#EEEAE0}
html{font-family:Serif,serif;font-size:10.3pt;line-height:1.42;color:#1E1913;hyphens:auto}
body{margin:0}
*{bookmark-level:none}
p{margin:0 0 .55em;text-align:justify;orphans:2;widows:2}
a{color:inherit;text-decoration:none}
i,em{font-style:italic}
.rh{string-set:sec content();display:block;height:0;overflow:hidden;margin:0}
h1,h2,h3,h4{hyphens:manual}
h1{font:400 21pt/1.05 Disp;margin:0 0 .8em;letter-spacing:-.01em}
h2{font:400 12pt/1.2 Disp;margin:1.5em 0 .5em;break-after:avoid}
h3{font:700 10.5pt/1.25 Sans;margin:1.1em 0 .35em;break-after:avoid}
h4{font:700 7.6pt/1.3 Sans;margin:0 0 .4em;color:#1E1913}
figure{margin:1em 0;break-inside:avoid;text-align:center}
figure img{max-width:100%;max-height:4.1in}
figure.wide img{max-height:3.4in}
figcaption{font:400 8pt/1.42 Sans;color:#6E6253;text-align:left;margin-top:.45em}
figcaption i{color:#1E1913;font-weight:500}
table{border-collapse:collapse;width:100%;font-size:9.2pt;margin:.6em 0 1em}
th{font:700 7.2pt Sans;text-align:left;border-bottom:.6pt solid #1E1913;padding:.3em .4em .3em 0}
td{border-bottom:.4pt solid #CFC4B0;padding:.35em .5em .35em 0;vertical-align:top}
table.chrono td,table.letters td{vertical-align:baseline;line-height:1.38}
table.chrono tr,table.letters tr{break-inside:avoid}
table.chrono td:first-child{font:400 10pt Disp;width:.62in;white-space:nowrap}
table.letters td:first-child{font:400 9pt Disp;width:.82in;white-space:nowrap}
table.letters td:nth-child(2){font:400 7.6pt/1.4 Sans;color:#6E6253;width:1.4in}
ol.check li{margin:.35em 0}
dl.gloss dt{font:700 8.6pt Sans;margin-top:.7em;break-after:avoid}dl.gloss dd{margin:.1em 0 0 0}
.ref{padding-left:1.2em;text-indent:-1.2em;text-align:left}
.sign{text-align:right;font-style:italic;margin-top:1.2em}
.vida{background:#E3D9C6;padding:.14in .16in .1in;margin:0 0 1.3em}
.vida h4{margin-bottom:.3em}.vida p{text-align:left;font-size:9.4pt;line-height:1.4;margin:0}
.kit{background:#E3D9C6;padding:.14in .18in .1in;margin:.4em 0 1.3em}
.kit ul{margin:0;padding:0 0 0 1.1em}
.kit li{margin:0 0 .35em;font-size:9.6pt;line-height:1.38;text-align:left}
.kit li b{font-weight:600}
.marks{display:flex;gap:.16in;margin:.12in 0;break-inside:avoid}
.marks figure{margin:0;flex:1}.marks img{max-height:1.35in;width:100%;object-fit:cover}
.pair{display:flex;gap:.16in;break-inside:avoid;margin:.8em 0}.pair figure{margin:0;flex:1}
.pair img{max-height:2.3in}
.pair.small{margin:.4em 0}.pair.small img{max-height:1.45in}
figure.mid img{max-height:3in}
.keep{break-inside:avoid}
.steps4{display:grid;grid-template-columns:repeat(4,1fr);column-gap:.08in;break-inside:avoid;margin:.8em 0}.steps4 figure{margin:0}
.steps4 img{max-height:1.55in}.steps4 figcaption{font-size:6.8pt}
.practice{margin-top:1.6em;border-top:.6pt solid #1E1913;padding-top:.7em;break-inside:avoid}
.practice ul{margin:0;padding:0;list-style:none;font-size:9.2pt;columns:2;column-gap:.2in}
.practice li{margin:.1em 0;break-inside:avoid}.practice a{font:700 7.6pt Sans;margin-right:.35em}
.practice .lvl{font:400 6.8pt Sans;color:#6E6253;margin-left:.25em}
.lead{font-size:11pt;font-style:italic;text-align:left}


/* ícones, balões, linha do tempo */
h2.ic{display:flex;align-items:center;gap:.1in}
h2.ic .icon{width:.36in;height:.36in;flex:none}
figure.flow{break-inside:avoid}
figure.mat img{max-height:2.5in}
figure.flow img{max-height:4.2in}
figure.flow figcaption b{font-weight:700;color:#1E1913}
.figbal{break-inside:avoid;margin:1em 0 1.3em}
.figbal > figure{margin:0 0 .16in}
.figbal > figure img{max-height:3.25in}
.figbal.side{display:flex;gap:.22in;align-items:flex-start}
.figbal.side > figure{flex:none;width:3.05in;margin:0}
.figbal.side > figure img{max-height:4.1in;width:auto;max-width:3.05in}
.figbal.side .balrow{display:block;flex:1}
.figbal.side .bal{width:auto;display:block;margin:0 0 .14in}
.figbal.side .bal img{width:.92in;height:.92in}
.pline{break-before:avoid;margin-top:1.4em;border-top:.6pt solid #1E1913;padding-top:.08in;font:400 7.8pt/1.5 Sans;text-align:left}
.pline b{font-weight:700;margin-right:.3em}
.pline a.pg{border:0;font-weight:400}.pline a.pg::after{content:target-counter(attr(href), page)}
h2.newpage{break-before:page}
.obra{break-inside:avoid;margin:1em 0}
.obra > h2:first-child{margin-top:0}
.obra .figbal.side > figure img{max-height:3.05in;max-width:2.9in}
.obra .figbal.side > figure{width:2.9in}
.obra .figbal > figure img{max-height:2.05in}
.obra .figbal .bal img{width:.85in;height:.85in}.obra .figbal .balrow{gap:.16in}
.obra > figure img{max-height:4.3in}
.obra ol.laws ~ .figbal.side > figure img{max-height:2.6in}
.obra ol.laws ~ .figbal .bal img{width:.8in;height:.8in}
.obra ol.laws li{padding-top:.06in;padding-bottom:.06in}.pline a{font-weight:700;border-bottom:.5pt solid #3B6386}
.balrow{display:flex;gap:.22in;justify-content:center}
.bal{width:1.45in;flex:none;margin:0;text-align:left}
.bal img{width:1.1in;height:1.1in;border-radius:50%;display:block;margin:0 0 .08in}
.bal figcaption{margin:0;font-size:7.8pt;line-height:1.4}
.bal figcaption b{display:block;font-weight:700;color:#1E1913;margin-bottom:.02in}
.mapa{page:full;break-before:page;width:6in;height:9in}
.mapa svg{display:block;width:6in;height:9in}
.enderecos{break-before:page}
.enderecos h2,.tracos h2{font:400 17pt/1.1 Disp;margin:0 0 .05in}
.enderecos .sub,.tracos .sub{font:italic 10pt/1.35 Serif;margin:0 0 .2in;text-align:left}
.end{display:flex;gap:.12in;border-top:.6pt solid #CFC4B0;padding:.07in 0}
.end .en{flex:none;width:.2in;height:.2in;border-radius:50%;background:#1E1913;color:#F4EFE6;font:700 6.8pt/.2in Sans;text-align:center}
.end p{margin:0;text-align:left;font-size:9.2pt;line-height:1.32}.end b{font:700 8.4pt Sans}.end .ey{font:400 7.6pt Sans;color:#6E6253}
.tracos{break-before:page}
.tr{display:flex;gap:.16in;border-top:.6pt solid #CFC4B0;padding:.07in 0 .08in;break-inside:avoid}
.tr img{width:2.3in;height:1.1in;flex:none}
.trt p{margin:0;text-align:left;font-size:9pt;line-height:1.32}.trt .ty{font:400 16pt/1 Disp}
.trt .tp{font:700 7.6pt Sans;margin:.05in 0 .04in}.trt .tp i{font-weight:400}
.tr2{break-before:page;padding-top:.68in}
.lvhead .lvtag{position:absolute;left:0;bottom:.62in;font:400 30pt/1 Disp;color:#3B6386;margin:0}

/* blocos numerados e diagramas */
ol.laws{list-style:none;margin:.6em 0 1.2em;padding:0;counter-reset:law}
ol.laws li{counter-increment:law;position:relative;padding:.09in 0 .09in .46in;border-top:.6pt solid #CFC4B0;text-align:left;break-inside:avoid}
ol.laws li:last-child{border-bottom:.6pt solid #CFC4B0}
ol.laws li::before{content:counter(law);position:absolute;left:0;top:.06in;font:400 17pt/1 Disp;color:#1E1913}
ol.laws li b{display:block;font:700 8.8pt Sans;margin-bottom:.03in}
figure.diag img{width:100%;max-height:none}

/* final */
.fim{page:kraft;break-before:page;width:6in;height:9in;position:relative}
.fim img{position:absolute;left:.7in;top:.8in;width:4.6in;height:4.2in;object-fit:contain}
.fim .fq{position:absolute;left:.85in;right:.85in;top:5.45in;font:italic 400 15pt/1.35 Serif;text-align:left;color:#1E1913}
.fim .fs{position:absolute;left:.85in;right:.85in;top:7.25in;font:500 7.4pt/1.4 Sans;color:#4A4034;text-align:left}
.contra{page:full;break-before:page;width:6in;height:9in;background:#EEEAE0;color:#1E1913;text-align:center;position:relative}
.contra .ct1{position:absolute;left:0;right:0;top:3.7in;font:400 30pt/1 Serif;text-align:center}
.contra .ct2{position:absolute;left:0;right:0;top:4.35in;font:italic 400 11pt Serif;color:#6E6253;text-align:center}
.contra .ct3{position:absolute;left:0;right:0;bottom:.7in;font:500 8pt Sans;letter-spacing:.2em;text-align:center}
/* obra em página inteira */
.bleed{page:full;break-before:page;width:6in;height:9in;position:relative;overflow:hidden}
.bleed img{position:absolute;inset:0;width:6in;height:9in;object-fit:cover}
.bleed::after{content:"";position:absolute;left:0;right:0;bottom:0;height:2in;background:linear-gradient(to bottom,rgba(240,233,218,0),rgba(240,233,218,.92) 60%)}
.bleed.dark::after{content:"";position:absolute;left:0;right:0;bottom:0;height:2.2in;background:linear-gradient(to bottom,rgba(15,11,8,0),rgba(15,11,8,.8) 70%)}
.bleed .bcap{position:absolute;left:.4in;right:.4in;bottom:.4in;z-index:2;font:400 7pt/1.45 Sans;color:#1E1913;text-align:left;margin:0}
.bleed .bcap i{font:italic 400 9.6pt Serif}
.bleed.dark .bcap{color:#FBF8F1}
/* capa */
.cover{page:full;position:relative;width:6in;height:9in;background:#2A2119;color:#FBF8F1;break-after:page;bookmark-level:1;bookmark-label:"Capa"}
.cover .art{position:absolute;top:0;bottom:0;left:0;right:0;background:url("img/cover-art.jpg") 50% 0/cover no-repeat}
.cover .topsh{display:none}
.cover .shade{display:none}
.cover .spine{position:absolute;top:0;bottom:0;left:0;width:.13in;background:#F7F4EE}
.cover .ed{position:absolute;top:.38in;left:0;right:0;text-align:center;font:500 10.5pt Sans;letter-spacing:.2em}
.cover .t{position:absolute;left:0;right:0;top:6.12in;text-align:center;font:400 44pt/1.02 Serif;letter-spacing:-.012em;white-space:nowrap}
.cover .d{position:absolute;left:0;right:0;top:7.62in;text-align:center;font:italic 400 15pt Serif}
.cover .coll{position:absolute;bottom:.42in;left:0;right:0;text-align:center;font:italic 400 10.5pt Serif}

/* folha de rosto e créditos */
.titlepage{page:bare;break-before:page;text-align:center;padding-top:2.3in}
.titlepage .t{font:400 34pt/1 Serif;margin:0 0 .25em;text-align:center;letter-spacing:-.01em}
.titlepage .s{font:italic 400 12pt Serif;color:#6E6253;text-align:center;margin:0 0 3.2in}
.titlepage .a{font:500 9pt Sans;letter-spacing:.2em;text-align:center}
.copy{page:bare;break-before:page;padding-top:5.3in;font:400 7.6pt/1.5 Sans;color:#6E6253}.copy p{text-align:left;margin-bottom:.8em}

/* sumário */
.toc{page:bare;break-before:page;bookmark-level:1;bookmark-label:"Sumário"}
.toc h1{font:400 22pt/1 Disp;margin:0 0 .3in}
.toc a{color:#1E1913;text-decoration:none}
.toc .blk{display:flex;margin-bottom:.19in}
.toc .col{width:.5in;flex:none;font:400 10pt/1.6 Sans;color:#3B6386;padding-top:.01in}
.toc .body{flex:1}
.toc p{display:flex;justify-content:space-between;align-items:baseline;margin:0;text-align:left}
.toc .pt{font:400 11pt/1.6 Disp;margin-bottom:.04in;border-bottom:.5pt solid #1E1913;padding-bottom:.03in}
.toc .r{font:400 10.2pt/1.5 Serif}
.toc .pg::after{content:target-counter(attr(href),page);font:400 8.4pt Sans;color:#6E6253}
.toc .pt .pg::after{color:#1E1913}
/* páginas de parte */
.partimg{page:kraft;break-before:page;width:6in;height:9in;position:relative}
.partimg img{position:absolute;left:.55in;top:.55in;width:4.9in;height:7.4in;object-fit:contain}
.partimg .pcap{position:absolute;left:.55in;right:.55in;bottom:.45in;font:400 7pt/1.4 Sans;color:#4A4034;text-align:center}
.partimg .pcap i{color:#1E1913}
.part{page:part;break-before:page;position:relative;width:6in;height:9in;color:#F6EFE4}
.part .prule{border-top-color:#F6EFE4!important}
.part .plab{position:absolute;left:.55in;top:1.72in;font:500 7.4pt Sans;margin:0}
.part .prule{position:absolute;left:.55in;right:.55in;top:1.95in;border-top:.6pt solid #1E1913}
.part .pnum{position:absolute;left:.5in;top:2.1in;font:400 118pt/1 Disp;margin:0}
.part h1{position:absolute;left:.55in;top:3.85in;width:4.4in;font-size:23pt;margin:0}
.part .pintro{position:absolute;left:.55in;top:4.85in;width:3.9in;font-size:9.6pt;line-height:1.42}
.part .pintro p{text-align:left;margin:0 0 .55em}

/* capítulos */
section.chap{page:chap;break-before:page}
.chhead{position:relative;height:2.05in;margin-bottom:.12in}
.chhead .chlab{position:absolute;left:0;top:.05in;font:500 7.4pt/1.4 Sans;margin:0}
.chhead .chnum{position:absolute;right:-.06in;top:-.16in;font:400 104pt/1 Disp;color:#3B6386;margin:0}
.chhead h1{position:absolute;left:0;bottom:0;width:3.7in;margin:0;font-size:23pt}
.chhead.nonum{height:1.9in}
section.front{page:chap;break-before:page}
section.front h1{font:400 30pt/1.1 Serif;text-align:center;margin:.25in 0 .9em;letter-spacing:-.01em}
section.front .ini{font:400 38pt/.8 Serif;float:left;margin:.04in .07in 0 0}

/* níveis */
section.level{page:chap;break-before:page}
.lvhead{height:3.2in;position:relative}
.lvhead .chlab{position:absolute;left:0;top:.05in;font:500 7.4pt Sans;margin:0}
.lvhead .chnum{position:absolute;right:-.06in;top:-.2in;font:400 120pt/1 Disp;color:#3B6386;margin:0}
.lvhead h1{position:absolute;left:0;right:0;bottom:0;margin:0;font-size:23pt;white-space:nowrap}
.lvlist{columns:2;column-gap:.22in;margin-top:.9em;border-top:.6pt solid #1E1913;padding-top:.1in}
.lvlist p{font-size:8.8pt;line-height:1.3;text-align:left;margin:0 0 .3em;break-inside:avoid}
.lvlist b{font:700 7.4pt Sans;display:inline-block;width:.36in}

/* exercícios */
.ex{break-before:page;break-inside:avoid}
.ex.nobreak{break-before:auto}
.ex.half{break-before:auto;height:3.5in;margin-top:0;overflow:hidden}
.pair2{break-before:page}
.pshead{border-bottom:.6pt solid #1E1913;padding-bottom:.06in;margin-bottom:.12in}
.pshead .psl{font:400 13pt Disp;margin:0;white-space:nowrap}.pshead .pst{font:400 7.6pt Sans;color:#6E6253;margin:.03in 0 0;text-align:left}
.pair2.first .ex.half{height:3.14in}
.pair2 .ex.half + .ex.half{border-top:.6pt solid #CFC4B0;padding-top:.14in;margin-top:.14in}
.exh{position:relative;height:.62in}
.exh .code{position:absolute;left:0;top:0;font:400 30pt/1 Disp}
.exh .lv{position:absolute;left:1.25in;top:.07in;font:500 7.2pt/1.4 Sans;color:#1E1913}
.half .exh{height:.5in}.half .exh .code{font-size:23pt}.half .exh .lv{left:.95in;top:.02in}
.ex h3{font:400 13pt/1.12 Disp;margin:0 0 .12in}
.half h3{font-size:11pt;margin-bottom:.08in}
.meta{display:flex;border-top:.6pt solid #1E1913;border-bottom:.6pt solid #1E1913;margin-bottom:.14in;font:400 7.2pt/1.35 Sans}
.meta div{flex:1;padding:.05in 0}
.meta div+div{border-left:.6pt solid #1E1913;padding-left:.08in}
.meta b{display:block;font-weight:700;font-size:7.6pt;margin-top:.02in}
.exart{height:4.3in;position:relative;margin-bottom:.14in}
.exart .model{position:absolute;left:0;top:0;width:3.3in;height:4.3in;object-fit:cover}
.exart .steps{position:absolute;left:3.42in;right:0;top:0}
.exart .steps figure{margin:0 0 .09in;text-align:left}
.exart .steps img{width:100%;height:1.17in;object-fit:cover;display:block}
.exart .steps figcaption{margin-top:.03in;font-size:6.6pt;color:#1E1913}
.exsolo{text-align:center;margin-bottom:.14in}
.exsolo img{max-width:100%;max-height:4.7in}
.half .exsolo img{max-height:1.75in}
.half .exsolo{float:left;width:2.35in;margin:0 .18in .05in 0;text-align:left}.half .exsolo img{max-width:2.35in}
.exfoot{display:flex;gap:.18in}
.exfoot .desc{flex:1}
.exfoot .desc p{font-size:9.6pt;line-height:1.4;margin:0 0 .4em}
.exfoot .done{width:1.5in;border-left:1.3pt solid #3B6386;padding-left:.08in;font:400 7.4pt/1.4 Sans}
.exfoot .done b{font-weight:700}
.half .exfoot{display:block}.half .exfoot .done{width:auto;margin-top:.06in}
.exref{font:400 7.2pt/1.4 Sans;color:#6E6253;margin-top:.12in;text-align:left}
.exref a{border-bottom:.5pt solid #3B6386;color:#1E1913}

/* catálogo */
.iconimg{page:kraft;break-before:page;width:6in;height:9in;position:relative}
.iconimg img{position:absolute;left:.45in;top:.45in;width:5.1in;height:8.1in;object-fit:contain}
.iconinfo{page:bare;break-before:page;position:relative;height:7.5in}
.iconinfo .ptop{display:flex;justify-content:space-between;border-bottom:.6pt solid #1E1913;padding-bottom:.06in;font:500 7.2pt Sans;margin-bottom:.9in}
.iconinfo .no{font:400 36pt/1 Disp;margin:0 0 .1in}
.iconinfo h2{font:italic 400 17pt/1.2 Serif;margin:0 0 .18in}
.iconinfo .cc{font:400 7.8pt/1.45 Sans;color:#6E6253;text-align:left}
.iconinfo .cl{font-size:10.6pt;line-height:1.45;margin:.2in 0}
.ficha{width:100%;font:400 7.4pt Sans;margin-top:.15in}
.iconinfo .balrow{margin-top:.35in;justify-content:flex-start;gap:.18in}
.iconinfo .bal{width:1.5in}
.ficha td{border-top:.6pt solid #A39682;border-bottom:none;padding:.05in 0}
.ficha td:first-child{width:.95in;color:#6E6253}
.catlist{}
.cat{display:flex;gap:.16in;margin:0 0 .12in;break-inside:avoid;align-items:flex-start;border-top:.6pt solid #CFC4B0;padding-top:.1in}
.cat .im{width:1.15in;flex:none;text-align:left}
.cat img{max-width:1.15in;max-height:1.25in}
.cat p{text-align:left;margin:0 0 .18em}
.cat .ct{font:400 10.4pt/1.25 Serif}
.cat .cn{font:400 9pt Disp;margin-right:.35em}
.cat .cc{font:400 7.2pt/1.42 Sans;color:#6E6253}
.cat .cf{font:400 6.8pt/1.4 Sans;color:#6E6253}
.cat .cl{font-size:8.8pt;line-height:1.34}


/* galeria dos mestres */
.mestre{display:flex;gap:.2in;border-top:.6pt solid #CFC4B0;padding:.14in 0 .1in;break-inside:avoid}
.mestre figure{margin:0;width:1.3in;flex:none}
.mestre figure img{width:1.3in;height:1.7in;object-fit:cover;max-height:none}
.mestre p{text-align:left;font-size:9.3pt;line-height:1.38;margin:0 0 .4em}
.mestre .mn{font:400 12.5pt/1.15 Disp;margin:0 0 .03in}
.mestre .md{font:500 7.4pt Sans;color:#6E6253;margin:0 0 .1in}
.mestre .mx{font:400 7.6pt/1.45 Sans;color:#1E1913;margin-top:.06in}
.mestre .mx a{border-bottom:.5pt solid #3B6386}
.cat .ca{display:block;font:500 7.2pt Sans;color:#1E1913;margin-top:.02in}

/* aberturas em grade, vidas, comparações, marcas, progresso */
.abgrid{page:full;break-before:page;width:6in;height:9in;position:relative}
.abgrid img{position:absolute;inset:0;width:6in;height:9in}
.vidas{break-before:page}
.vidas h2{font:400 17pt/1.1 Disp;margin:0 0 .05in}.vidas .sub{font:italic 10pt/1.35 Serif;margin:0 0 .35in;text-align:left}
.vgrid{position:relative;padding-top:.25in}
.vlines{position:absolute;left:1.35in;right:0;top:.25in;bottom:0}
.vg{position:absolute;top:0;bottom:0;border-left:.4pt solid #CFC4B0}
.vr{display:flex;align-items:center;height:.48in;position:relative}
.vn{width:1.35in;flex:none;font:700 7.6pt Sans;margin:0;text-align:left}
.vb{position:relative;flex:1;height:.48in}
.vt{position:absolute;top:-.25in;font:400 6.4pt Sans;color:#6E6253}.vt i{font-style:normal;margin-left:-.12in}
.bar{position:absolute;top:.17in;height:.1in;background:#3B6386}
.vy{position:absolute;top:.3in;font:400 6.2pt Sans;color:#6E6253}.vy.e{margin-left:-.25in}
section.cmp{break-before:page;page:chap}
.cmp .chlab{font:500 7.4pt Sans;margin:0 0 .25in}
.cmp .ck{font:700 7.4pt Sans;letter-spacing:.14em;text-transform:uppercase;margin:0 0 .05in;color:#3B6386}
.cmp h1{font:400 22pt/1.1 Disp;margin:0 0 .1in}.cmp .lead{margin:0 0 .25in}
.ci{display:flex;gap:.2in;align-items:flex-start;border-top:.6pt solid #CFC4B0;padding:.12in 0;break-inside:avoid}
.ci img{width:1.75in;height:1.75in;flex:none}
.ci p{text-align:left;margin:0}.ci .cm{font:400 13pt/1.1 Disp;margin-bottom:.04in}.ci .co{font-size:9.6pt;color:#6E6253;margin-bottom:.1in}
.ci .ct2{font-size:10.2pt;line-height:1.4}
.lv1 .ck{color:#5B87A6}.lv2 .ck{color:#4A7699}.lv3 .ck{color:#3B6386}.lv4 .ck{color:#304F78}.lv5 .ck{color:#243B5E}
.marcas{display:flex;flex-wrap:wrap;justify-content:space-between}
.mk{display:flex;gap:.12in;width:2.28in;break-inside:avoid;border-top:.6pt solid #CFC4B0;padding:.07in 0 .07in}
.mk img{width:.82in;height:.82in;flex:none}
.mk p{margin:0;text-align:left}.mk .mn2{font:700 7.6pt/1.3 Sans}.mk .mm{font-size:9.6pt;line-height:1.3;margin:.03in 0}.mk .ma{font:400 7pt Sans;color:#6E6253}
.prog .pl{margin:0 0 .12in;break-inside:avoid}.prog .pl p{font:700 7.6pt Sans;margin:0 0 .08in;text-align:left}
.pbs{display:flex;flex-wrap:wrap;gap:.04in}
.pb{width:.38in;height:.38in;border:1pt solid;box-sizing:border-box;position:relative}
.pb b{position:absolute;left:.03in;top:.02in;font:700 5.6pt Sans;color:#1E1913}
/* índice */
.idx{columns:2;column-gap:.25in}
.idx p{font-size:8.3pt;line-height:1.2;margin:0 0 .16em;text-align:left;break-inside:avoid}
.idx b{font:700 7.2pt Sans;display:inline-block;width:.33in}
.idx span{font:400 6.6pt Sans;color:#6E6253}
.idx h4{column-span:none;margin:.8em 0 .3em}
"""

def chapter_head(s, part):
    h = s['html']
    m = re.match(r'\s*<h1>(.*?)</h1>', h, re.S)
    title = m.group(1) if m else esc(s['title'])
    body = h[m.end():] if m else h
    n = re.match(r'(\d+)\.\s*(.*)', title)
    plab = f'{part[1]} · {part[2]}' if part else 'Consulta'
    short = re.sub(r':.*', '', n.group(2) if n else title)
    rh = f'<span class="rh">{short}</span>'
    if n:
        head = f'<div class="chhead"><p class="chlab">{plab}<br/>Aula {n.group(1)}</p><p class="chnum">{n.group(1)}</p><h1>{n.group(2)}</h1></div>'
    else:
        head = f'<div class="chhead nonum"><p class="chlab">{plab}</p><h1>{title}</h1></div>'
    return rh + head, body, (n.group(2) if n else title)

def ex_pdf(x, chapnames, half=False):
    n, lid, ln, lname, col, code = LV[x['lv']]
    cid = x['aula']
    cnum = re.match(r'(\d+)', SEC_TITLE.get(cid, '')).group(1) if re.match(r'(\d+)', SEC_TITLE.get(cid, '')) else ''
    tempo, _, mat = x['m'].partition(' · ')
    head = (f'<div class="exh"><span class="code">{x["id"]}</span>'
            f'<span class="lv">{ln} · {lname}<br/>Aula {cnum} · {esc(chapnames.get(cid, ""))}</span></div>'
            f'<h3>{esc(x["t"])}</h3>')
    meta = (f'<div class="meta"><div>Tempo<b>{esc(tempo)}</b></div><div>Material<b>{esc(mat)}</b></div>'
            f'<div>Teoria<b><a href="#{cid}">Aula {cnum}</a></b></div></div>')
    im = ex_img(x)
    if x['id'] in STAGES and not half:
        st = ''.join(f'<figure><img src="img/st-{im}-{k}.jpg" alt=""/><figcaption>{k} · {STN[k-1]}</figcaption></figure>' for k in (1, 2, 3))
        art = f'<div class="exart"><img class="model" src="img/{im}.jpg" alt=""/><div class="steps">{st}</div></div>'
    elif os.path.exists(f'img/{im}.jpg'):
        art = f'<div class="exsolo"><img src="img/{im}.jpg" alt=""/></div>'
    else:
        art = ''
    ref = ''
    if x.get('ref') and x['ref'] in PL:
        ref = f'<p class="exref">Obra: <a href="#cat-{x["ref"]}"><i>{esc(PL[x["ref"]]["t"])}</i></a>, {esc(PL[x["ref"]]["a"])}, no catálogo.</p>'
    foot = (f'<div class="exfoot"><div class="desc"><p>{esc(x["d"])}</p></div>'
            f'<div class="done"><b>Pronto quando</b> {esc(x["c"])}</div></div>')
    return f'<section class="ex lv{n}{" half" if half else ""}" id="ex-{x["id"]}">{head}{meta}{art}{foot}{ref}</section>'

SEC_TITLE = {}

def cat_numbers():
    order = CAT_ORDER + [k for k in PL if k not in CAT_ORDER]
    return {k: i for i, k in enumerate(order, 1)}, order


def catalogue_pdf():
    num, order = cat_numbers()
    cards = []
    for k in order:
        p = PL[k]; f = FI.get(k, {})
        fi = f.get('dim', '')
        cards.append(f'<div class="cat" id="cat-{k}"><div class="im"><img src="img/{k}.jpg" alt="{esc(p["t"])}"/></div><div>'
                     f'<p class="ct"><span class="cn">{num[k]}</span><i>{esc(p["t"])}</i><span class="ca">{esc(p["a"])}</span></p><p class="cc">{esc(p["c"])}</p>'
                     + (f'<p class="cf">{esc(fi)}</p>' if fi else '') + f'<p class="cl">{esc(p.get("l", ""))}</p></div></div>')
    return ('<section class="chap" id="catalogo"><span class="rh">Catálogo das obras</span>'
            '<div class="chhead nonum"><p class="chlab">Consulta</p><h1>Catálogo das obras</h1></div>'
            '<p>As obras dos mestres estudadas no livro, na ordem em que aparecem, com a técnica, '
            'as dimensões (altura por largura) e o acervo, quando disponíveis.</p>'
            + ''.join(cards) + '</section>')

def ex_index_pdf():
    body = ''
    for n, lid, lab, name, col, code in LEVELS:
        body += f'<h4>{lab} · {name}</h4>' + ''.join(f'<p><b><a href="#ex-{x["id"]}">{x["id"]}</a></b>{esc(x["t"])}</p>' for x in EX if x['lv'] == n)
    return ('<section class="chap" id="indice"><span class="rh">Índice dos exercícios</span>'
            '<div class="chhead nonum"><p class="chlab">Consulta</p><h1>Índice dos exercícios</h1></div>'
            f'<div class="idx">{body}</div></section>')

def pdf_html(S):
    chapnames = {}
    for s in S:
        SEC_TITLE[s['id']] = s['title']
        m = re.match(r'\s*<h1>\d+\.\s*(.*?)</h1>', s.get('html', ''))
        if m:
            chapnames[s['id']] = re.sub(r':.*', '', m.group(1))
    yr = datetime.date.today().year
    P = [f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Grandes Artistas a Lápis</title>'
         f'<meta name="author" content="Pedro Torres"><style>{font_faces()}{PDF_CSS}</style></head><body>']
    if os.path.exists('img/cover-pdf.jpg'):
        P.append('<div class="cover"><img src="img/cover-pdf.jpg" alt="Capa" style="position:absolute;inset:0;width:6in;height:9in"/></div>')
    else:
      P.append('<div class="cover"><div class="art"></div>'
             '<div class="ed">PEDRO TORRES</div><div class="t">Grandes Artistas<br/>a Lápis</div><div class="d">Cinco níveis com dez mestres</div>'
             f'<div class="coll">{NEX} exercícios em cinco níveis</div></div>')
    P.append('<div class="titlepage"><p class="t">Grandes Artistas a Lápis</p><p class="s">Cinco níveis com dez mestres</p><p class="a">PEDRO TORRES</p></div>')
    P.append(f'<div class="copy"><p>© {yr} Pedro Torres. Todos os direitos reservados.</p>'
             '<p>Nenhuma parte deste livro pode ser reproduzida sem autorização do autor, exceto as folhas de exercício destinadas ao uso pessoal do leitor.</p>'
             f'<p>Capa: {COVER_CREDIT}</p>'
             f'<p>Texto composto em EB Garamond e Archivo. Primeira edição, {yr}.</p></div>')
    def row(label, href):
        return f'<p class="r"><a href="#{href}">{label}</a><a class="pg" href="#{href}"></a></p>'
    def blk(num, inner, cls=''):
        return f'<div class="blk"><div class="col"{cls}>{num}</div><div class="body">{inner}</div></div>'
    def head(pid):
        return f'<p class="pt"><a href="#{pid}">{PARTS[pid][2]}</a><a class="pg" href="#{pid}"></a></p>'
    front = ''.join(row(esc(x['title']), x['id']) for x in S if x['kind'] == 'front')
    back = ''.join(row(esc(x['title']), x['id']) for x in S if x['kind'] == 'back') + row('Índice dos exercícios', 'indice')
    toc = ['<div class="toc"><h1>Sumário</h1>', blk('', front),
           blk('', head('parte1') + row('Os dez mestres, um a um', 'mestres') + row('Dez vidas, quase cinco séculos', 'toc-vidas') + row('Quatrocentos anos em dez traços', 'toc-tracos'))]
    for n, lid, lab, name, col, code in LEVELS:
        caps = ''.join(row(x['title'].replace('. ', '.&#8194;', 1), x['id']) for x in S if x['kind'] == 'chapter' and x.get('lv') == n)
        cmpr = row(f'Três mestres: {esc(XTR["cmp"][str(n)]["t"])}', f'cmp-{n}') if str(n) in XTR['cmp'] else ''
        toc.append(blk(str(n), head(lid) + caps + cmpr, f' style="color:{col}"'))
    toc += [blk('', back), '</div>']
    P.extend(toc)
    part = None
    global LASTCAP
    LASTCAP = {}
    for s in S:
        if s['kind'] == 'chapter' and s.get('lv'): LASTCAP[s['lv']] = s['id']
    for s in S:
        k = s['kind']
        if k == 'part':
            part = PARTS[s['id']]
            n, lab, name, intro = part
            art = PART_ART.get(s['id'])
            if art and art.startswith('ab_'):
                P.append(f'<section class="abgrid"><img src="img/{art}.jpg" alt=""/></section>')
            elif art:
                P.append(f'<section class="partimg"><img src="img/{art}.jpg" alt="{esc(PL[art]["t"])}"/>'
                         f'<p class="pcap"><i>{esc(PL[art]["t"])}</i>, {esc(PL[art]["a"])}. {esc(PL[art]["l"])}</p></section>')
            pg = f'part{s["lv"]}' if s.get('lv') else 'part'
            P.append(f'<section class="part" id="{s["id"]}" style="page:{pg};bookmark-level:1;bookmark-label:\'{lab} · {name}\'">'
                     f'<p class="plab">{lab}</p><div class="prule"></div><p class="pnum">{n}</p><h1>{name}</h1><div class="pintro">{intro}</div></section>')
        elif k == 'front':
            h = s['html']
            m = re.match(r'\s*<h1>(.*?)</h1>', h, re.S)
            body = h[m.end():]
            if s['id'] == 'prefacio':
                body = re.sub(r'<p>(\w)', r'<p><span class="ini">\1</span>', body, count=1)
            P.append(f'<section class="front" id="{s["id"]}" style="bookmark-level:1;bookmark-label:\'{s["title"]}\'"><span class="rh">{s["title"]}</span><h1>{m.group(1)}</h1>{body}</section>')
        elif s['id'] == 'catalogo':
            P.append(catalogue_pdf().replace('<section class="chap" id="catalogo">', '<section class="chap" id="catalogo" style="bookmark-level:1;bookmark-label:\'Catálogo das obras\'">', 1))
            P.append(ex_index_pdf().replace('<section class="chap" id="indice">', '<section class="chap" id="indice" style="bookmark-level:1;bookmark-label:\'Índice dos exercícios\'">', 1))
        else:
            head_, body, t = chapter_head(s, part if k == 'chapter' else None)
            lvl = 2 if k == 'chapter' else 1
            lab = s['title'].replace("'", "’")
            cls = f' lv{s["lv"]}' if s.get('lv') else ''
            P.append(f'<section class="chap{cls}" id="{s["id"]}" style="bookmark-level:{lvl};bookmark-label:\'{lab}\'">{head_}{body}</section>')
            exs = s.get('exs')
            if exs:
                i = 0; first = True
                while i < len(exs):
                    x = exs[i]
                    hd = (f'<div class="pshead"><span class="rh">Para praticar</span><p class="psl">Para praticar</p>'
                          f'<p class="pst">Aula {re.match(r"(\d+)", s["title"]).group(1)} · {esc(chapnames.get(s["id"], ""))}</p></div>') if first else ''
                    if x['id'] in STAGES:
                        P.append(hd.replace('<div class="pshead">', '<div class="pshead" style="break-before:page">') + ex_pdf(x, chapnames).replace('class="ex ', 'class="ex nobreak ', 1) if hd else ex_pdf(x, chapnames))
                        i += 1
                    else:
                        chunk = [x] + ([exs[i + 1]] if i + 1 < len(exs) and exs[i + 1]['id'] not in STAGES else [])
                        if len(chunk) == 1:
                            P.append(ex_pdf(x, chapnames))
                        else:
                            P.append(f'<div class="pair2{" first" if first else ""}">{hd}' + ''.join(ex_pdf(y, chapnames, half=True) for y in chunk) + '</div>')
                        i += len(chunk)
                    first = False
            if s['id'] in END_ART:
                P.append(bleed_html(END_ART[s['id']]))
            if s.get('lv') and s['id'] == LASTCAP.get(s['lv']):
                P.append(cmp_html(s['lv']))
    P.append(FIM_HTML)
    P.append('<section class="contra"><p class="ct1">Grandes Artistas a Lápis</p><p class="ct2">Cinco níveis com dez mestres</p>'
             '<p class="ct3">PEDRO TORRES</p></section>')
    P.append('</body></html>')
    html_ = '\n'.join(P)
    n = [0]
    def pg(m):
        n[0] += 1
        return f'{m.group(1)} style="page:pg{n[0]};'
    html_ = re.sub(r'(<section class="(?:chap[^"]*|front|level)" id="[^"]+") style="', pg, html_)
    extra = ''.join(f'@page :nth(1 of pg{i}){{@bottom-left{{content:none}}@bottom-right{{content:none}}}}' for i in range(1, n[0] + 1))
    return html_.replace('</style>', extra + '</style>', 1)

COVER_CREDIT = json.load(open('tools/capa_credito.json')) if os.path.exists('tools/capa_credito.json') else ''
FIM_HTML = ('<section class="fim"><img src="img/g_ingres.jpg" alt="Autorretrato de Ingres, desenho a grafite"/>'
            '<p class="fq">“O desenho é a probidade da arte.”</p>'
            '<p class="fs">J.-A.-D. Ingres, segundo o biógrafo Henri Delaborde (1870)</p></section>')

# ---------------------------------------------------------------- EPUB
EPUB_FONTS = [('Serif', 'eb-garamond-latin-400-normal.ttf', 400, 'normal'), ('Serif', 'eb-garamond-latin-400-italic.ttf', 400, 'italic'),
              ('Serif', 'eb-garamond-latin-600-normal.ttf', 600, 'normal'), ('Disp', 'archivo-black-latin-400-normal.woff', 400, 'normal'),
              ('Sans', 'archivo-latin-400-normal.woff', 400, 'normal'), ('Sans', 'archivo-latin-700-normal.woff', 700, 'normal')]
EPUB_CSS = """
body{font-family:Serif,serif;line-height:1.5;margin:0;color:#1E1913}
h1{font-family:Disp,sans-serif;font-weight:400;font-size:1.65em;line-height:1.12;margin:1.4em 0 .9em;page-break-before:always}
h1 .lvnum{display:block;font-family:Sans,sans-serif;font-weight:700;font-size:.45em;color:#3B6386;margin-bottom:.4em}
h2{font-family:Disp,sans-serif;font-weight:400;font-size:1.15em;line-height:1.2;margin:1.6em 0 .5em}
h3{font-family:Sans,sans-serif;font-weight:700;font-size:1.05em;margin:.3em 0 .4em}
h4{font-family:Sans,sans-serif;font-weight:700;font-size:.78em;margin:0 0 .4em}
p{margin:0 0 .6em;text-indent:0}
a{color:#1E1913}
figure{display:block;margin:1.2em 0;text-align:center;page-break-inside:avoid}
img{max-width:100%;height:auto}
figcaption{font-family:Sans,sans-serif;font-size:.72em;line-height:1.45;color:#5F5446;text-align:left;margin-top:.4em}
.vida{background:#EFE8DB;padding:.7em .9em .5em;margin:0 0 1.3em;font-size:.92em}
.marks figure,.pair figure{margin:.8em 0}
.kgrid{width:100%;border-collapse:collapse;margin:.4em 0 1.2em;page-break-inside:avoid}
.kgrid td.kc{border:0;padding:.2em .4em .4em;vertical-align:top;text-align:center}
.kgrid td.kc img{width:100%;max-width:9em}
.kgrid p.kt{font-family:Sans,sans-serif;font-size:.68em;line-height:1.35;color:#5F5446;text-align:left;margin:.3em 0 0}
.kgrid p.kt b{display:block;color:#1E1913}
.practice{border-top:1px solid #1E1913;margin-top:1.6em;padding-top:.6em;font-size:.9em}
.practice ul{list-style:none;padding:0}.practice a{font-family:Sans,sans-serif;font-weight:700;font-size:.85em;margin-right:.3em}
.practice .lvl{font-family:Sans,sans-serif;color:#6E6253;font-size:.75em}
.exnum{font-family:Disp,sans-serif;font-size:1.9em;line-height:1;margin:1.2em 0 .1em}
section.ex{page-break-before:always}
.ex h3{font-family:Disp,sans-serif;font-weight:400;font-size:1.2em}
.exmeta{font-family:Sans,sans-serif;font-size:.78em;color:#5F5446;border-top:1px solid #1E1913;border-bottom:1px solid #1E1913;padding:.35em 0}
.exref{font-family:Sans,sans-serif;font-size:.78em;color:#5F5446}
.crit{border-left:3px solid #3B6386;padding-left:.6em}.crit .sc{font-family:Sans,sans-serif;font-weight:700;font-size:.85em}
.lead{font-style:italic}.count{font-family:Sans,sans-serif;font-size:.75em;color:#6E6253}
table{border-collapse:collapse;width:100%;font-size:.88em}th,td{border-bottom:1px solid #CFC4B0;padding:.3em .4em;text-align:left;vertical-align:top}
th{font-family:Sans,sans-serif;font-size:.8em;border-bottom:1px solid #1E1913}
dl.gloss dt{font-family:Sans,sans-serif;font-weight:700;font-size:.9em;margin-top:.7em}dl.gloss dd{margin-left:0}
.sign{text-align:right;font-style:italic}
.cat{margin:0 0 1.4em;page-break-inside:avoid;clear:both;overflow:hidden;border-top:1px solid #CFC4B0;padding-top:.6em}.cat img{display:block;width:34%;margin:0 0 .5em}.cat div{overflow:hidden}
.cat p{margin:0 0 .2em}.cc,.cf{font-family:Sans,sans-serif;font-size:.75em;color:#5F5446}.cn{font-family:Disp,sans-serif;margin-right:.35em}
.parttitle{margin-top:1.2em}.parttitle .pn{font-family:Disp,sans-serif;font-size:3.6em;line-height:1;color:#3B6386;margin:0}
.parttitle h1{page-break-before:avoid;font-family:Sans,sans-serif;font-weight:700;font-size:.8em;margin:.6em 0 .2em}
.parttitle h2{font-size:1.7em;margin:0 0 .6em}
h2.ic img.icon{width:1.6em;height:1.6em;vertical-align:middle;margin-right:.4em}
.balrow{text-align:center;margin:-.4em 0 1.2em}
.bal{display:inline-block;width:30%;margin:.4em 1.2% .8em;vertical-align:top;text-align:left}
.bal img{width:100%;border-radius:50%}
.bal figcaption b{display:block;font-weight:700}
.mapa{margin:0 0 1.2em;text-align:center}
.end{border-top:1px solid #CFC4B0;padding:.4em 0;overflow:hidden}.end .en{float:left;font-family:Sans,sans-serif;font-weight:700;width:1.6em}
.end p{margin:0 0 0 1.6em}.end .ey{font-family:Sans,sans-serif;font-size:.8em;color:#5F5446}
.tr{border-top:1px solid #CFC4B0;padding:.6em 0;page-break-inside:avoid}.tr img{width:100%}
.trt .ty{font-family:Disp,sans-serif;font-size:1.3em;margin:.3em 0 0}.trt .tp{font-family:Sans,sans-serif;font-size:.85em;font-weight:700;margin:0}
.tracos .sub,.enderecos .sub{font-style:italic}
ol.laws{list-style:none;padding:0}ol.laws li{border-top:1px solid #CFC4B0;padding:.5em 0}ol.laws li b{display:block;font-family:Sans,sans-serif}
figure.diag img{width:100%}
.titlepage{text-align:center;margin-top:25%}.titlepage .t{font-size:2.1em;line-height:1.1}.titlepage .s{font-style:italic;color:#5F5446}
.titlepage .a{font-family:Sans,sans-serif;font-size:.8em;letter-spacing:.2em;margin-top:3em}
"""

def xhtml(fragment):
    root = lhtml.fragment_fromstring(fragment, create_parent='div')
    s = ''.join(etree.tostring(c, method='xml', encoding='unicode') for c in root)
    if root.text and root.text.strip():
        s = esc(root.text) + s
    return s

def page(title, body):
    return ('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="pt-BR" xml:lang="pt-BR">'
            f'<head><meta charset="utf-8"/><title>{esc(title)}</title><link rel="stylesheet" type="text/css" href="style.css"/></head><body>{body}</body></html>')

def epub_assets():
    """Imagens extras para leitores (Kindle): balões em PNG com círculo transparente e o mapa em PNG."""
    from PIL import Image, ImageDraw
    import glob, subprocess, tempfile
    for f in glob.glob('img/det-*.jpg'):
        out = f[:-4] + '.png'
        if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(f):
            continue
        im = Image.open(f).convert('RGB').resize((360, 360), Image.LANCZOS)
        m = Image.new('L', (1440, 1440), 0); ImageDraw.Draw(m).ellipse((0, 0, 1439, 1439), fill=255)
        im.putalpha(m.resize((360, 360), Image.LANCZOS)); im.save(out, optimize=True)

def kindle_html(body):
    """Simplifica o HTML para leitores: sem imagens lado a lado por porcentagem, sem SVG, sem páginas do PDF."""
    body = re.sub(r'<img class="icon"[^>]*?/?>', '', body)
    body = body.replace('img/mapa-caminho.svg', 'img/mapa-caminho.png')
    body = re.sub(r' · p\. <a class="pg" href="[^"]*"></a>( a <a class="pg" href="[^"]*"></a>)?', '', body)
    def bal(m):
        cells = re.findall(r'<figure class="bal"><img src="img/(det-[^"]+)\.jpg" alt="([^"]*)"/><figcaption>(.*?)</figcaption></figure>', m.group(0), re.S)
        tds = ''.join(f'<td class="kc"><img src="img/{k}.png" alt="{a}"/><p class="kt">{c}</p></td>' for k, a, c in cells)
        return f'<table class="kgrid"><tr>{tds}</tr></table>'
    body = re.sub(r'<div class="balrow[^"]*">.*?</div>', bal, body, flags=re.S)
    def steps(m):
        figs = re.findall(r'<figure><img src="([^"]+)" alt="([^"]*)"/?>\s*<figcaption>(.*?)</figcaption></figure>', m.group(0), re.S)
        rows = ''
        for i in range(0, len(figs), 2):
            rows += '<tr>' + ''.join(f'<td class="kc"><img src="{s_}" alt="{a}"/><p class="kt">{c}</p></td>' for s_, a, c in figs[i:i + 2]) + '</tr>'
        return f'<table class="kgrid">{rows}</table>'
    body = re.sub(r'<div class="steps4[^"]*">.*?</div>', steps, body, flags=re.S)
    return body

def build_epub(S, out, small=None):
    files = []  # (name, title, body, kind)
    files.append(('titulo.xhtml', 'Folha de rosto', '<div class="titlepage"><p class="t">Grandes Artistas a Lápis</p><p class="s">Cinco níveis com dez mestres</p><p class="a">PEDRO TORRES</p></div>'
                  f'<p style="margin-top:3em;font-size:.8em;color:#666">© {datetime.date.today().year} Pedro Torres. Todos os direitos reservados.</p>', 'front'))
    idfile = {}
    for i, s in enumerate(S):
        name = f'{i:02d}-{s["id"]}.xhtml'
        if s['kind'] == 'part':
            img = f'img/{PART_ART[s["id"]]}.jpg'
            n_, lab_, name_, intro_ = PARTS[s['id']]
            it = '' if intro_ is None else (intro_ if intro_.startswith('<p>') else f'<p>{intro_}</p>')
            body = (f'<section id="{s["id"]}"><figure><img src="{img}" alt=""/></figure><div class="parttitle"><p class="pn">{n_}</p>'
                    f'<h1>{lab_}</h1><h2>{name_}</h2>{it}</div></section>')
        else:
            body = f'<section id="{s["id"]}">{s["html"].replace("<!--MAPA-->", map_html(False))}{s.get("epub_extra", "")}</section>'
        body = kindle_html(body)
        files.append((name, s['title'], body, s['kind']))
        for m in re.finditer(r'id="([^"]+)"', body):
            idfile[m.group(1)] = name
    def fixlinks(body):
        return re.sub(r'href="#([^"]+)"', lambda m: f'href="{idfile.get(m.group(1), "")}#{m.group(1)}"', body)
    imgs = set()
    fonts_added = []
    bid = 'urn:uuid:' + str(uuid.uuid5(uuid.NAMESPACE_URL, 'grandes-artistas-a-lapis-pedro-torres'))
    with zipfile.ZipFile(out, 'w') as z:
        z.writestr(zipfile.ZipInfo('mimetype'), 'application/epub+zip', compress_type=zipfile.ZIP_STORED)
        z.writestr('META-INF/container.xml', '<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>', compress_type=zipfile.ZIP_DEFLATED)
        fcss = ''
        from fontTools.ttLib import TTFont
        import io
        for fam, f, w, st in EPUB_FONTS:
            ft = TTFont(os.path.join(FONTDIR, f)); ft.flavor = None
            buf = io.BytesIO(); ft.save(buf)
            name = re.sub(r'\.woff$', '.ttf', f)
            z.writestr('OEBPS/fonts/' + name, buf.getvalue(), compress_type=zipfile.ZIP_DEFLATED)
            fonts_added.append(name)
            fcss += f'@font-face{{font-family:"{fam}";src:url("fonts/{name}");font-weight:{w};font-style:{st}}}\n'
        z.writestr('OEBPS/style.css', fcss + EPUB_CSS, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr('OEBPS/cover.xhtml', page('Capa', '<figure style="margin:0;text-align:center"><img src="img/cover.jpg" alt="Capa" style="max-height:100%"/></figure>'), compress_type=zipfile.ZIP_DEFLATED)
        for name, title, body, kind in files:
            x = xhtml(fixlinks(body))
            imgs.update(re.findall(r'src="(img/[^"]+)"', x))
            z.writestr('OEBPS/' + name, page(title, x), compress_type=zipfile.ZIP_DEFLATED)
        imgs.add('img/cover.jpg')
        for im in sorted(imgs):
            if im.endswith('.png'):
                z.write(im, 'OEBPS/' + im, compress_type=zipfile.ZIP_STORED)
            elif im.endswith('.svg'):
                z.write(im, 'OEBPS/' + im, compress_type=zipfile.ZIP_DEFLATED)
            elif small:
                from PIL import Image
                import io
                pic = Image.open(im).convert('RGB')
                if im != 'img/cover.jpg':
                    pic.thumbnail((small, small))
                buf = io.BytesIO(); pic.save(buf, 'JPEG', quality=68, optimize=True, progressive=True)
                z.writestr('OEBPS/' + im, buf.getvalue(), compress_type=zipfile.ZIP_STORED)
            else:
                z.write(im, 'OEBPS/' + im, compress_type=zipfile.ZIP_STORED)
        nav = ['<nav epub:type="toc" id="toc"><h1>Sumário</h1><ol>']
        for name, title, body, kind in files[1:]:
            nav.append(f'<li><a href="{name}">{esc(title)}</a></li>')
        nav.append('</ol></nav><nav epub:type="landmarks" hidden=""><ol><li><a epub:type="cover" href="cover.xhtml">Capa</a></li>'
                   f'<li><a epub:type="toc" href="nav.xhtml">Sumário</a></li><li><a epub:type="bodymatter" href="{files[1][0]}">Início</a></li></ol></nav>')
        z.writestr('OEBPS/nav.xhtml', page('Sumário', ''.join(nav)), compress_type=zipfile.ZIP_DEFLATED)
        man = ['<item id="css" href="style.css" media-type="text/css"/>', '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
               '<item id="coverpage" href="cover.xhtml" media-type="application/xhtml+xml"/>']
        spine = ['<itemref idref="coverpage" linear="yes"/>', '<itemref idref="nav"/>']
        for i, (name, title, body, kind) in enumerate(files):
            man.append(f'<item id="p{i}" href="{name}" media-type="application/xhtml+xml"/>')
            spine.insert(-1 if i == 0 else len(spine), f'<itemref idref="p{i}"/>')
        for k, f in enumerate(fonts_added):
            man.append(f'<item id="f{k}" href="fonts/{f}" media-type="font/ttf"/>')
        for k, im in enumerate(sorted(imgs)):
            props = ' properties="cover-image"' if im == 'img/cover.jpg' else ''
            mt = 'image/svg+xml' if im.endswith('.svg') else 'image/png' if im.endswith('.png') else 'image/jpeg'
            man.append(f'<item id="i{k}" href="{im}" media-type="{mt}"{props}/>')
        now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        opf = ('<?xml version="1.0" encoding="utf-8"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bid" xml:lang="pt-BR">'
               '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
               f'<dc:identifier id="bid">{bid}</dc:identifier><dc:title>Grandes Artistas a Lápis</dc:title><dc:creator>Pedro Torres</dc:creator>'
               '<dc:language>pt-BR</dc:language><dc:subject>Desenho</dc:subject>'
               f'<dc:description>Um curso de desenho a lápis com dez mestres, de Leonardo a Schiele: linha, proporção, luz e sombra, rosto, figura e composição, com {NEX} exercícios em cinco níveis.</dc:description>'
               f'<meta property="dcterms:modified">{now}</meta><meta name="cover" content="i{sorted(imgs).index("img/cover.jpg")}"/></metadata>'
               f'<manifest>{"".join(man)}</manifest><spine>{"".join(spine)}</spine></package>')
        z.writestr('OEBPS/content.opf', opf, compress_type=zipfile.ZIP_DEFLATED)

COVER_EBOOK = """<!doctype html><html><head><meta charset="utf-8"><style>{fonts}
@page{{size:6in 9.6in;margin:0}}*{{margin:0;padding:0}}
.c{{position:relative;width:6in;height:9.6in;background:#2A2119;color:#FBF8F1;overflow:hidden}}
.art{{position:absolute;inset:0;background:url("img/cover-art.jpg") 50% 0/cover no-repeat}}
.topsh{{display:none}}
.shade{{display:none}}
.ed{{position:absolute;top:.42in;left:0;right:0;text-align:center;font:500 11.5pt Sans;letter-spacing:.2em}}
.t{{position:absolute;left:0;right:0;top:6.55in;text-align:center;font:400 46pt/1.02 Serif;letter-spacing:-.012em;white-space:nowrap}}
.d{{position:absolute;left:0;right:0;top:8.15in;text-align:center;font:italic 400 16pt Serif}}
.coll{{position:absolute;bottom:.5in;left:0;right:0;text-align:center;font:italic 400 11.5pt Serif}}
</style></head><body><div class="c"><div class="art"></div><div class="topsh"></div><div class="shade"></div>
<div class="ed">PEDRO TORRES</div><div class="t">Grandes Artistas<br>a Lápis</div><div class="d">Cinco níveis com dez mestres</div>
<div class="coll">{nex} exercícios em cinco níveis</div></div></body></html>"""

def make_cover():
    """Capa do e-book em 1600 × 2560 px (proporção pedida pela Amazon)."""
    if os.path.exists('img/cover-ebook.jpg'):
        from PIL import Image
        im = Image.open('img/cover-ebook.jpg').convert('RGB')
        im.save('img/cover.jpg', quality=92); im.save('out/capa-ebook-1600x2560.jpg', quality=92)
        return
    import subprocess, tempfile
    from weasyprint import HTML
    from PIL import Image
    with tempfile.TemporaryDirectory() as td:
        HTML(string=COVER_EBOOK.format(fonts=font_faces(), nex=NEX), base_url=ROOT).write_pdf(f'{td}/c.pdf')
        subprocess.run(['pdftoppm', '-r', '266.67', '-png', '-singlefile', f'{td}/c.pdf', f'{td}/c'], check=True)
        im = Image.open(f'{td}/c.png').convert('RGB').resize((1600, 2560), Image.LANCZOS)
    im.save('img/cover.jpg', quality=92)
    im.save('out/capa-ebook-1600x2560.jpg', quality=92)

if __name__ == '__main__':
    import sys
    S = build_sections()
    S += [catalogue(), CREDITS]
    os.makedirs('out', exist_ok=True)
    args = sys.argv[1:] or ['cover', 'pdf']  # EPUB só com: python3 build.py epub
    make_details(); make_tracos()
    if 'cover' in args:
        make_cover(); print('capa ok')
    if 'pdf' in args:
        open('out/livro.html', 'w').write(pdf_html(S))
        from weasyprint import HTML
        doc = HTML('out/livro.html', base_url=ROOT).render()
        print('páginas', len(doc.pages))
        doc.write_pdf('out/Grandes-Artistas-a-Lapis.pdf')
    if 'epub' in args:
        epub_assets()
        build_epub(S, 'out/Grandes-Artistas-a-Lapis.epub')
        build_epub(S, 'out/Grandes-Artistas-a-Lapis-loja-Amazon.epub', small=800)
        print('epub ok')
