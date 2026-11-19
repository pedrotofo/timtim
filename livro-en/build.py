"""Builds Van Gogh in Pencil (English edition of Van Gogh a Lápis) em PDF (WeasyPrint) e EPUB 3 a partir de src/*.md e data.json."""
import os, re, json, glob, html, uuid, zipfile, datetime
import markdown
from lxml import etree, html as lhtml

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
D = json.load(open('data.json'))
EX, PL, FI = D['ex'], D['pl'], D['fi']
# exercícios retirados na revisão de imagens (modelos fracos ou repetidos)
REMOVED = set('c15 a04 a09 a14 c23 p02 p05 c20 f12 f09 p01 p04 p06 a15 c13 c18 a10 b07 r18 f16'.split())
EX = [x for x in EX if x['id'] not in REMOVED]
NEX = len(EX)
NESS = sum(1 for x in EX if x['lv'] == 'e')
esc = html.escape

# ---------------------------------------------------------------- textos dos exercícios para o livro
FIX = {
 'r03': {'c': 'the tufts read as grass.'},
 'r09': {'d': 'Short hatching in one direction only. To darken, bring the lines closer and keep the same pressure.'},
 'r10': {'d': 'Sea and sand: dashes on one side, dots on the other. The border between them shows only through the change of mark, with no line at all.'},
 'f02': {'c': 'the clusters look like tongues of fire.'},
 'f14': {'c': 'the small cypress looks farther away, not only smaller.'},
 'c09': {'d': 'Before filling in, draw on a separate sheet only the flow lines of each zone, from the map in Chapter 4. Then fill in zone by zone.'},
 'c17': {'c': 'the brim looks round.'},
 'c20': {'d': 'Dashes that all point to the center of the head. This background pushes the eye inward.'},
 'c24': {'d': 'Study this model, then do the same from a photo of someone close to you, with side light and a plain background. Write the key in the corner: skin, hair, cloth, background.'},
 'a14': {'d': 'In the mirror, or from a photo of yourself. A background of rings, as in the model.'},
 'p02': {'d': 'Cover the whole sheet, with a different mark for each thing.'},
}
for x in EX:
    x.update(FIX.get(x['id'], {}))
for k, v in PL.items():
    for f in ('c', 'l', 't'):
        if f in v:
            v[f] = re.sub(r'(\d{2})(\d{2})–(\d{2})\b', lambda m: f'{m.group(1)}{m.group(2)} to {m.group(1)}{m.group(3)}', v[f]).replace('–', '-')
PL['sorrow']['l'] = 'The contour is one continuous, angular line. The weight shifts: thick under the thigh and at the foot, thin where the light falls.'
LEVELS = [('w', 'nivel1', 'Level 1', 'Foundations',
           'Short exercises, 8 to 20 minutes each, that train one mark or one part of the face at a time. Start here if you are new to drawing, and come back to them as a warm-up before each session.'),
          ('e', 'nivel2', 'Level 2', 'Essentials',
           f'The {NESS} exercises at the core of the method. Do only these and you will still learn the language: plains in bands, flow, cypresses, faces in directions, self-portraits and figures.'),
          ('d', 'nivel3', 'Level 3', 'Going Deeper',
           'Variations and harder cases, for when the essentials are solid: other background solutions, side light, larger and smaller marks, new landscapes.'),
          ('p', 'nivel4', 'Level 4', 'Master Studies',
           'Long studies of works by Van Gogh and a personal project, in which you take the language into your own world. Use the methods in Chapter 8.')]
CHAP = {'r': ('cap2', 'Chapter 2'), 'f': ('cap3', 'Chapter 3'), 'c': ('cap4', 'Chapter 4'), 'a': ('cap5', 'Chapter 5'), 'b': ('cap6', 'Chapter 6'), 'p': ('cap8', 'Chapter 8')}
STAGES = set('r13 r16 r19 f13 f17 c11 c12 c16 a01 a13 b04 b06'.split())
STN = ['Sketch', 'First ink', 'Nearly done', 'Finished']

def ex_html(x):
    cid, cname = CHAP[x['ch']]
    meta = esc(x['m'])
    out = [f'<section class="ex" id="ex-{x["id"]}">',
           f'<p class="exnum">{x["id"].upper()}</p>',
           f'<h3>{esc(x["t"])}</h3>',
           f'<figure class="model"><img src="img/{x["id"]}.jpg" alt="Model drawing for exercise {x["id"].upper()}"/></figure>',
           f'<p class="exmeta">{meta}</p>',
           f'<p>{esc(x["d"])}</p>',
           f'<p class="crit"><span class="sc">Done when</span> {esc(x["c"])}</p>']
    extra = [f'Theory in <a href="#{cid}">{cname}</a>.']
    if x.get('ref') and x['ref'] in PL:
        extra.append(f'Work to compare: <a href="#cat-{x["ref"]}"><i>{esc(PL[x["ref"]]["t"])}</i></a>, in the catalogue.')
    out.append(f'<p class="exref">{" ".join(extra)}</p>')
    if x['id'] in STAGES:
        imgs = ''.join(f'<figure><img src="img/{"st-"+x["id"]+"-"+str(k+1) if k < 3 else x["id"]}.jpg" alt="Stage {k+1}"/><figcaption>{k+1}. {STN[k]}</figcaption></figure>' for k in range(4))
        out.append(f'<div class="steps4 small">{imgs}</div>')
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
def md2html(s):
    MD.reset()
    h = MD.convert(s)
    return h.replace('src="ex/', 'src="img/')

def practice_list(chid):
    rev = {v[0]: k for k, v in CHAP.items()}
    if chid == 'cap7':
        items = [x for x in EX if x['id'] in STAGES]
        head = 'Exercises shown in stages'
    elif chid in rev:
        items = [x for x in EX if x['ch'] == rev[chid]]
        head = 'Practice'
    else:
        return ''
    lvn = {l[0]: l[2] for l in LEVELS}
    lis = ''.join(f'<li><a href="#ex-{x["id"]}">{x["id"].upper()}</a> {esc(x["t"])} <span class="lvl">{lvn[x["lv"]]}</span></li>' for x in items)
    return f'<div class="practice"><h4>{head}</h4><ul>{lis}</ul></div>'

def practice_line(chid):
    rev = {v[0]: k for k, v in CHAP.items()}
    if chid not in rev:
        return ''
    items = sorted((x for x in EX if x['ch'] == rev[chid]), key=lambda x: x['id'])
    first, last = items[0]['id'], items[-1]['id']
    ess = [x['id'] for x in items if x['lv'] == 'e']
    lk = lambda c: f'<a href="#ex-{c}">{c.upper()}</a>'
    pg = lambda c: f'<a class="pg" href="#ex-{c}"></a>'
    txt = (f'<b>Practice</b> {lk(first)} to {lk(last)} · pp. {pg(first)} to {pg(last)}' if first != last
           else f'<b>Practice</b> {lk(first)} · p. {pg(first)}')
    if ess:
        txt += ' · essentials ' + ', '.join(lk(c) for c in ess)
    return f'<p class="pline">{txt}</p>'

def build_sections():
    src = parse_src()
    S = []
    for s in src:
        h = md2html(s['md'])
        if s['id'] in ('como-usar', 'cap1'):
            h = add_icons(h)
        if s['id'] == 'vida':
            i = h.index('<h2>')
            h = h[:i] + '<!--MAPA-->' + h[i:] + tracos_html()
        if s['id'] in BALLOON_CHAPTERS:
            h = add_balloons(h)
        rev = {v[0]: k for k, v in CHAP.items()}
        if s['id'] in rev:
            fs = [x for x in EX if x['lv'] == 'w' and x['ch'] == rev[s['id']]]
            if fs:
                s = {**s, 'first_steps': fs,
                     'epub_extra': '<h2>First Steps</h2>' + '\n'.join(ex_html(x) for x in fs)}
        if s['kind'] == 'chapter':
            pl = practice_line(s['id'])
            t = h.rstrip()
            if '<div class="obra"' in t and re.fullmatch(r'(\s*</div>)+\s*', t[t.rfind('</figure>') + 9:]) and t.rfind('<div class="obra"') > t.rfind('</div>', 0, t.rfind('<div class="obra"') + 1) - 1:
                h = t[:-len('</div>')] + pl + '</div>'
            else:
                h += pl
        S.append({**s, 'html': h})
        if s['id'] == 'cap8':  # depois da Parte II vem a Parte III
            S.append({'id': 'parte3', 'title': 'Part III · Studies', 'kind': 'part', 'opener': 'ex/part3.jpg',
                      'html': '<h1>Part III</h1>\n<h2>Exercises</h2>'})
            for code, lid, ln, name, intro in LEVELS:
                if code == 'w':
                    continue
                items = [x for x in EX if x['lv'] == code]
                body = f'<h1><span class="lvnum">{ln}</span> {name}</h1>\n<p class="lead">{intro}</p>\n<p class="count">{len(items)} exercises</p>\n' + '\n'.join(ex_html(x) for x in items)
                S.append({'id': lid, 'title': f'{ln} · {name}', 'kind': 'level', 'html': body})
    return S

def catalogue():
    order = ['sorrow', 'wornout', 'orphan', 'yard', 'peasant', 'reaper', 'head85', 'hands', 'sower1', 'sower2', 'digger',
             'lacrau', 'arlesview', 'rock', 'boats', 'street', 'cottages2', 'garden', 'harvest', 'stacks', 'cafe',
             'roulin', 'roulin2', 'zouavepen', 'escalier', 'escalier2', 'mousme', 'mousme2', 'tanguy',
             'sp_chi', 'sp_close', 'sp_straw', 'sp_painter', 'sp_felt', 'sp_felteye', 'sp_gauguin', 'sp_ear', 'sp_orsay',
             'starry', 'cypress', 'wheatcyp', 'wheatcyp2', 'fountain', 'olivep', 'enclosed', 'pine', 'gachet']
    order += [k for k in PL if k not in order]
    rows = []
    for i, k in enumerate(order, 1):
        p = PL[k]; f = FI.get(k, {})
        inst = f.get('inst', '')
        if inst and inst.split(' (')[0].split(',')[0][:12] in p['c']:
            inst = ''
        ficha = ' · '.join(v for v in [f.get('cat'), f.get('dim'), inst] if v)
        rows.append(f'<div class="cat" id="cat-{k}"><img src="img/{k}.jpg" alt="{esc(p["t"])}"/><div><p class="ct"><span class="cn">{i}</span> <i>{esc(p["t"])}</i></p>'
                    f'<p class="cc">{esc(p["c"])}</p>' + (f'<p class="cf">{esc(ficha)}</p>' if ficha else '') + f'<p class="cl">{esc(p.get("l", ""))}</p></div></div>')
    intro = ('<p>The works by Van Gogh cited in the book and suggested in the exercises, in approximate order of date. Where available, '
             'the F (de la Faille) and JH (Hulsker) catalogue numbers follow, with dimensions (height by width) and the collection.</p>')
    return {'id': 'catalogo', 'title': 'Catalogue of Works', 'kind': 'back', 'html': '<h1>Catalogue of Works</h1>' + intro + ''.join(rows)}

def ex_index():
    lvn = {l[0]: l[2] for l in LEVELS}
    rows = ''.join(f'<tr><td><a href="#ex-{x["id"]}">{x["id"].upper()}</a></td><td>{esc(x["t"])}</td><td>{lvn[x["lv"]]}</td></tr>'
                   for x in sorted(EX, key=lambda x: ('rfcabp'.index(x['ch']), x['id'])))
    return {'id': 'indice', 'title': 'Index of Exercises', 'kind': 'back',
            'html': '<h1>Index of Exercises</h1><table class="idx"><tr><th>Code</th><th>Exercise</th><th>Level</th></tr>' + rows + '</table>'}

CREDITS = {'id': 'creditos', 'title': 'Credits', 'kind': 'back', 'html': md2html(
"""# Credits

The reproductions of works by Vincent van Gogh are in the public domain and were obtained from Wikimedia Commons. The reproduction of the *Portrait of Joseph Roulin* used on the cover comes from the Open Content Program of the J. Paul Getty Museum, Los Angeles. Catalogue data comes from Wikidata and Wikimedia Commons. Quotations from the letters are the author's own translations; letter numbers follow the edition published by the Van Gogh Museum and the Huygens Institute at vangoghletters.org.

The model drawings for the exercises, the step-by-step demonstrations, the mark samples and the photographs of materials were made for this book with the help of artificial intelligence tools, following the author's directions. They are interpretations in the style of Van Gogh's drawings and do not reproduce his works. The icons and the map were drawn for this book.

Set in EB Garamond and Archivo. Translated from the Brazilian Portuguese edition, *Van Gogh a Lápis*.""")}

# ---------------------------------------------------------------- detalhes das obras (balões logo depois de cada obra)
# obra: (imagem de origem, [(centro x, centro y, lado como fração da largura, título, texto)])
WORK_DETAILS = {
 'lacrau': ('lacrau', [(.62, .14, .24, 'The horizon', 'Near the horizon the mark gets tiny and almost disappears.'),
                       (.45, .62, .22, 'Bands of dashes', 'Each field is a band of flat dashes.'),
                       (.25, .88, .22, 'The foreground', 'At the bottom the marks grow and darken. That is where the blacks go.')]),
 'boats': ('boats', [(.45, .66, .2, 'Firm contour', 'The hulls have the surest line on the sheet.'),
                     (.8, .86, .18, 'Sand in dots', 'The beach is only dots. The paper between them becomes light.')]),
 'garden': ('garden', [(.55, .12, .22, 'In the distance', 'The houses and trees at the back get much smaller marks.'),
                       (.3, .72, .2, 'One mark per flowerbed', 'Commas in one bed, dots in the next. There is no contour between them.')]),
 'cypress': ('cypress', [(.45, .18, .26, 'Clusters as flames', 'Each cluster is a C of two to four parallel strokes, always rising.'),
                         (.42, .55, .26, 'The dense core', 'In the core the clusters press together until they almost merge.'),
                         (.5, .9, .3, 'The ground in waves', 'Below, the ground repeats the movement in long waves.')]),
 'starry': ('starry', [(.885, .14, .2, 'The moon’s crown', 'The dashes turn in rings around the moon.'),
                       (.5, .42, .22, 'The currents of the sky', 'The sky runs in bands that curl.'),
                       (.25, .55, .26, 'The cypress', 'The only dense mass on the sheet, joining the ground to the sky.')]),
 'wheatcyp': ('wheatcyp', [(.5, .15, .24, 'The curling sky', 'The clouds run in curves that close into swirls.'),
                           (.82, .45, .2, 'The cypress', 'Brushstrokes that rise and twist like flames.'),
                           (.35, .86, .22, 'The wheat', 'Short slanted touches, all in the same direction.')]),
 'roulin': ('cover-roulin', [(.39, .385, .15, 'The eye as a swirl', 'Short rings around the eye socket. The upper eyelid is the thickest line.'),
                             (.5, .6, .24, 'The beard as a fan', 'Curves that fall and open out, instead of loose hairs.'),
                             (.25, .86, .26, 'The coat', 'Thick cross-hatching that follows the lapel.')]),
 'escalier2': ('escalier2', [(.55, .2, .3, 'The hat left white', 'The hat is almost all contour.'),
                             (.5, .44, .2, 'The face', 'Short dashes follow the wrinkles and the planes.'),
                             (.86, .16, .2, 'The dotted background', 'Dots in rows push the head forward.')]),
 'mousme': ('mousme', [(.47, .33, .26, 'Almost bare paper', 'Heavy contour only on the eyes, eyebrows, nostrils and mouth.'),
                       (.5, .72, .3, 'The striped blouse', 'Thick stripes that follow the folds of the clothes.')]),
 'sp_felt': ('sp_felt', [(.5, .5, .55, 'The eye', 'Each brushstroke is a separate dash. Together they form rings around the eye.', 'sp_felteye'),
                         (.5, .2, .3, 'The hat brim', 'Dashes that go all the way around the brim.'),
                         (.13, .42, .24, 'The halo of dashes', 'Short brushstrokes radiate from the head and set it apart.')]),
 'sp_chi': ('sp_chi', [(.5, .44, .2, 'Rays from the nose', 'The dashes of the face spread out from the nose like rays.'),
                       (.12, .2, .22, 'The dotted background', 'Dots larger than the marks on the face.')]),
 'sp_gauguin': ('sp_gauguin', [(.45, .4, .22, 'Firm planes', 'Shaved head, firm planes and a heavy contour.'),
                               (.85, .2, .25, 'The calm background', 'Almost flat. All the energy stays in the face.')]),
 'sp_orsay': ('sp_orsay', [(.14, .2, .26, 'The swirling background', 'The whole background turns in currents, like water.'),
                           (.5, .4, .2, 'The still face', 'Shorter, firmer marks than in the background.'),
                           (.62, .82, .26, 'The coat in the current', 'Wavy lines like those of the background.')]),
 'wornout': ('wornout', [(.55, .3, .45, 'The hidden face', 'The head in the hands. All the emotion is in the pose.')]),
 'peasant': ('peasant', [(.55, .3, .3, 'Two oval masses', 'Back and hips are two masses. The hatching changes direction in each.'),
                         (.3, .52, .24, 'Hatching in rings', 'On the arm, the hatching wraps around the form.')]),
 'cafe': ('cafe', [(.42, .42, .25, 'The lantern', 'A broken contour and short rays around the light.'),
                   (.3, .15, .35, 'The awning', 'Long parallel lines that follow the curve of the cloth.'),
                   (.5, .88, .35, 'The paving', 'Stones as small loops, smaller and smaller toward the back.')]),
 'mousme2': ('mousme2', [(.42, .2, .28, 'The face', 'Almost blank paper, with contour only on the features.'),
                         (.45, .45, .35, 'The striped blouse', 'Thick stripes that run down and follow the body.'),
                         (.5, .82, .35, 'The dotted skirt', 'Dots and rings in loose rows.')]),
 'roulin2': ('roulin2', [(.5, .2, .3, 'The face', 'A beard in curves and firm eyes: the sharpest area.'),
                         (.4, .5, .34, 'The coat', 'Bands of hatching that follow the buttons and the sleeves.')]),
 'sorrow': ('sorrow', [(.45, .66, .26, 'The weighted contour', 'The line thickens under the thigh and at the foot, and thins where the light falls.')]),
}
BALLOON_CHAPTERS = ('cap2', 'cap3', 'cap4', 'cap5', 'cap6')

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
    def rep(m):
        key = m.group(1)
        if key not in WORK_DETAILS:
            return m.group(0)
        from PIL import Image
        w_, h_ = Image.open(f'img/{key}.jpg').size
        side = h_ > w_ * 1.05
        return f'<div class="figbal{" side" if side else ""}">{m.group(0)}{balloons_html(key)}</div>'
    return re.sub(r'<figure[^>]*>\s*<img src="img/([a-z0-9_]+)\.jpg"[^>]*>.*?</figure>', rep, h, flags=re.S)

# ---------------------------------------------------------------- ícones e linha do tempo
ICONS_H2 = {'Where to Start': 'comecar', 'The Model Drawings': 'modelo', 'Drawing Over a Model': 'imprimir',
            'The Letters': 'cartas', 'The 6B Pencil': 'lapis', 'The Fineliner': 'junco', 'The Paper': 'papel', 'The Perspective Frame': 'moldura', 'On a Tablet': 'tablet'}

def add_icons(h):
    return re.sub(r'<h2>([^<]+)</h2>', lambda m: (f'<h2 class="ic"><img class="icon" src="img/icons/{ICONS_H2[m.group(1)]}.svg" alt=""/>{m.group(1)}</h2>'
                                                  if m.group(1) in ICONS_H2 else m.group(0)), h)

ENDERECOS = [('Borinage', '1879 to 1880', 'A preacher among the miners, he begins to draw them.'),
             ('Brussels', '1880 to 1881', 'Anatomy, perspective and the Bargue plates.'),
             ('Etten', '1881', 'At his parents’ house, he copies Millet and draws from life.'),
             ('The Hague', '1881 to 1883', 'The school of black and white.'),
             ('Drenthe', '1883', 'Three months among the peat bogs of the north.'),
             ('Nuenen', '1883 to 1885', 'Weavers, peasants and form built from masses.'),
             ('Antwerp', '1885 to 1886', 'A few months at the academy.'),
             ('Paris', '1886 to 1888', 'The palette brightens and the Japanese prints arrive.'),
             ('Arles', '1888 to 1889', 'The reed pen and the alphabet of marks.'),
             ('Saint-Rémy', '1889 to 1890', 'The short stroke stretches into curves.'),
             ('Auvers-sur-Oise', '1890', 'Seventy paintings in two months, and his only etching.')]
# ano, lugar, imagem, centro x, centro y, largura (fração), obra, texto
TRACOS = [('1881', 'Etten', 'sower2', .55, .22, .95, 'Sower in profile', 'Hard pencil and a continuous contour. He is still copying Millet.'),
          ('1882', 'The Hague', 'sorrow', .5, .62, .8, 'Sorrow', 'A single line, thicker under the forms.'),
          ('1882', 'The Hague', 'wornout', .5, .28, .85, 'Worn Out', 'Pencil on watercolor paper. The pose carries the emotion.'),
          ('1885', 'Nuenen', 'peasant', .5, .3, .85, 'Peasant woman stooping', 'Black chalk in rings over oval masses.'),
          ('1885', 'Nuenen', 'hands', .5, .5, .9, 'Three hands', 'Large, heavy hands, built from masses.'),
          ('1887', 'Paris', 'sp_chi', .5, .45, .7, 'Self-portrait', 'Separate dashes of color, in rays from the nose.'),
          ('1888', 'Arles', 'lacrau', .5, .62, .6, 'La Crau seen from Montmajour', 'Reed pen: one mark for each surface.'),
          ('1888', 'Arles', 'cover-roulin', .5, .58, .6, 'Portrait of Joseph Roulin', 'Four substances, four marks in one face.'),
          ('1889', 'Saint-Rémy', 'cypress', .45, .25, .8, 'Cypresses', 'Curves that rise and curl like flames.'),
          ('1890', 'Auvers', 'gachet', .5, .45, .85, 'Dr. Gachet', 'His only etching: quick, nervous hatching.')]

def make_tracos():
    from PIL import Image
    for i, (yy, pl, k, cx, cy, w, t, tx) in enumerate(TRACOS, 1):
        im = Image.open(f'img/{k}.jpg').convert('RGB'); W = w * im.width; H = W / 2.1
        x0 = max(0, min(im.width - W, cx * im.width - W / 2)); y0 = max(0, min(im.height - H, cy * im.height - H / 2))
        im.crop((round(x0), round(y0), round(x0 + W), round(y0 + H))).resize((840, 400), Image.LANCZOS).save(f'img/traco-{i:02d}.jpg', quality=90)

def map_html(inline=True):
    if inline:
        svg = open('img/mapa-caminho-en.svg').read()
        mp = f'<div class="mapa" id="toc-caminho">{svg}</div>'
    else:
        mp = '<figure class="mapa"><img src="img/mapa-caminho-en.svg" alt="Map of Van Gogh’s addresses between 1879 and 1890"/></figure>'
    rows = ''.join(f'<div class="end"><span class="en">{i}</span><div><p><b>{c}</b> <span class="ey">{y}</span></p><p>{t}</p></div></div>'
                   for i, (c, y, t) in enumerate(ENDERECOS, 1))
    return (mp + '<div class="enderecos"><h2>Eleven Addresses</h2><p class="sub">Each town left something in the line. '
            'Zundert, where he was born in 1853, and London, where he worked from 1873 to 1876, appear on the map as open circles.</p>' + rows + '</div>')

def tracos_html():
    def row(i, x):
        yy, pl, k, cx, cy, w, t, tx = x
        return (f'<div class="tr"><img src="img/traco-{i:02d}.jpg" alt="Detail of {esc(t)}"/>'
                f'<div class="trt"><p class="ty">{yy}</p><p class="tp">{pl} · <i>{esc(t)}</i></p><p>{tx}</p></div></div>')
    rows = [row(i, x) for i, x in enumerate(TRACOS, 1)]
    return ('<div class="tracos" id="toc-tracos"><h2>Ten Years in Ten Lines</h2><p class="sub">The same draftsman, from 1881 to 1890, always seen up close.</p>'
            + ''.join(rows[:5]) + '<div class="tr2">' + ''.join(rows[5:]) + '</div></div>')

# ---------------------------------------------------------------- PDF (edição ilustrada)
FONTDIR = os.path.join(ROOT, 'fonts')
PARTS = {'parte1': ('01', 'Part I', 'Ten Years of Drawing', None),
         'parte2': ('02', 'Part II', 'The Language',
                    'The materials, the marks, the direction of the stroke, the face, the self-portraits, the body, the order in which he built a sheet and the way to copy a master. One chapter for each.'),
         'parte3': ('03', 'Part III', 'Studies', f'<p>The {NEX - sum(1 for x in EX if x["lv"] == "w")} studies of Levels 2 to 4. The short Level 1 exercises have already appeared at the end of each chapter, as First Steps. Here you draw whole pictures: landscapes, faces, figures and master copies. The code of each exercise tells you the subject: R for hatchings (from the Portuguese <i>ranhuras</i>), F for flow, C for faces, A for self-portraits, B for the body and P for the project.</p><p>Each page gives the model drawing, the suggested time and materials, the instruction and a criterion for knowing when the exercise is done. Twelve exercises also show the stages of construction, from sketch to finish.</p><p>To draw over a model, photocopy the page and use tracing paper, or photograph it, import it into a drawing app and work on a layer above. Most of the time, though, draw beside the book, looking at the model.</p>'),
         'parte4': ('04', 'Part IV', 'Practice',
                    'An eight-week study plan and a self-assessment to check the result.')}
END_ART = {'cap2': ('cafe', 'cafe'), 'cap4': ('tanguy', 'tanguy'), 'cap5': ('sp_painter', 'sp_painter-sem-moldura'), 'cap6': ('digger', 'digger')}

def bleed_html(spec):
    key, img = spec
    from PIL import Image, ImageStat
    im = Image.open(f'img/{img}.jpg').convert('L')
    w, h = im.size
    lum = ImageStat.Stat(im.crop((0, int(h * .82), w, h))).mean[0]
    dark = lum < 150
    return (f'<section class="bleed{" dark" if dark else ""}"><img src="img/{img}.jpg" alt="{esc(PL[key]["t"])}"/>'
            f'<p class="bcap"><i>{esc(PL[key]["t"])}</i> · {esc(PL[key]["c"])}</p></section>')

LEVEL_ART = {'e': 'stacks', 'd': 'street', 'p': 'enclosed'}
PART_ART = {'parte1': 'sower2', 'parte2': 'zouavepen', 'parte3': 'fountain', 'parte4': 'roulin2'}
ICONS = ['sorrow', 'cafe', 'roulin', 'mousme2', 'starry', 'cypress']
CAT_ORDER = ['sorrow', 'wornout', 'orphan', 'yard', 'peasant', 'reaper', 'head85', 'hands', 'sower1', 'sower2', 'digger',
             'lacrau', 'arlesview', 'rock', 'boats', 'street', 'cottages2', 'garden', 'harvest', 'stacks', 'cafe',
             'roulin', 'roulin2', 'zouavepen', 'escalier', 'escalier2', 'mousme', 'mousme2', 'tanguy',
             'sp_chi', 'sp_close', 'sp_straw', 'sp_painter', 'sp_felt', 'sp_felteye', 'sp_gauguin', 'sp_ear', 'sp_orsay',
             'starry', 'cypress', 'wheatcyp', 'wheatcyp2', 'fountain', 'olivep', 'enclosed', 'pine', 'gachet']

def font_faces(base='file://' + FONTDIR + '/'):
    css = ''
    for w in (400, 500, 600, 700):
        for st in ('normal', 'italic'):
            for sub in ('latin', 'latin-ext'):
                f = f'eb-garamond-{sub}-{w}-{st}.ttf'
                if os.path.exists(os.path.join(FONTDIR, f)):
                    css += f'@font-face{{font-family:"LivroSerif";src:url("{base}{f}");font-weight:{w};font-style:{st}}}\n'
    for f in sorted(os.listdir(FONTDIR)):
        m = re.match(r'archivo-(black-)?latin(-ext)?-(\d+)-(normal|italic)\.woff$', f)
        if m:
            fam = 'LivroDisp' if m.group(1) else 'LivroSans'
            css += f'@font-face{{font-family:"{fam}";src:url("{base}{f}");font-weight:{m.group(3)};font-style:{m.group(4)}}}\n'
    return css

PDF_CSS = """
@page{size:6in 9in;margin:.62in .72in .82in .55in;background:#EEEAE0}
@page :left{margin-left:.55in;margin-right:.72in;
  @bottom-left{content:counter(page) "\\2003" string(sec);font:400 7.2pt LivroSans;color:#6E6253;vertical-align:top;padding-top:.3in}}
@page :right{margin-left:.72in;margin-right:.55in;
  @bottom-right{content:string(sec) "\\2003" counter(page);font:400 7.2pt LivroSans;color:#6E6253;vertical-align:top;padding-top:.3in}}
@page full{margin:0;@bottom-left{content:none}@bottom-right{content:none}}
@page part{margin:0;background:#BF8A5A;@bottom-left{content:none}@bottom-right{content:none}}
@page kraft{margin:0;background:#D6C7A8;@bottom-left{content:none}@bottom-right{content:none}}
@page bare{@bottom-left{content:none}@bottom-right{content:none}}
@page chap:first{@bottom-left{content:none}@bottom-right{content:none}}
:root{--ink:#1E1913;--mute:#6E6253;--soft:#A39682;--clay:#BF8A5A;--kraft:#D6C7A8;--paper:#EEEAE0}
html{font-family:LivroSerif,serif;font-size:10.3pt;line-height:1.42;color:#1E1913;hyphens:auto;hyphenate-character:"-"}
body{margin:0}
*{bookmark-level:none}
p{margin:0 0 .55em;text-align:justify;orphans:2;widows:2}
a{color:inherit;text-decoration:none}
i,em{font-style:italic}
.rh{string-set:sec content();display:block;height:0;overflow:hidden;margin:0}
h1,h2,h3,h4{hyphens:manual}
h1{font:400 21pt/1.05 LivroDisp;margin:0 0 .8em;letter-spacing:-.01em}
h2{font:400 12pt/1.2 LivroDisp;margin:1.5em 0 .5em;break-after:avoid}
h3{font:700 10.5pt/1.25 LivroSans;margin:1.1em 0 .35em;break-after:avoid}
h4{font:700 7.6pt/1.3 LivroSans;margin:0 0 .4em;color:#1E1913}
figure{margin:1em 0;break-inside:avoid;text-align:center}
figure img{max-width:100%;max-height:4.1in}
figure.wide img{max-height:3.4in}
figcaption{font:400 8pt/1.42 LivroSans;color:#6E6253;text-align:left;margin-top:.45em}
figcaption i{color:#1E1913;font-weight:500}
table{border-collapse:collapse;width:100%;font-size:9.2pt;margin:.6em 0 1em}
th{font:700 7.2pt LivroSans;text-align:left;border-bottom:.6pt solid #1E1913;padding:.3em .4em .3em 0}
td{border-bottom:.4pt solid #CFC4B0;padding:.35em .5em .35em 0;vertical-align:top}
table.chrono td,table.letters td{vertical-align:baseline;line-height:1.38}
table.chrono tr,table.letters tr{break-inside:avoid}
table.chrono td:first-child{font:400 10pt LivroDisp;width:.62in;white-space:nowrap}
table.letters td:first-child{font:400 9pt LivroDisp;width:.82in;white-space:nowrap}
table.letters td:nth-child(2){font:400 7.6pt/1.4 LivroSans;color:#6E6253;width:1.4in}
ol.check li{margin:.35em 0}
dl.gloss dt{font:700 8.6pt LivroSans;margin-top:.7em}dl.gloss dd{margin:.1em 0 0 0}
.ref{padding-left:1.2em;text-indent:-1.2em;text-align:left}
.sign{text-align:right;font-style:italic;margin-top:1.2em}
.vida{background:#E3D9C6;padding:.14in .16in .1in;margin:0 0 1.3em}
.vida h4{margin-bottom:.3em}.vida p{text-align:left;font-size:9.4pt;line-height:1.4;margin:0}
.kit{background:#E3D9C6;padding:.14in .18in .1in;margin:.4em 0 1.3em}
.kit ul{margin:0;padding:0 0 0 1.1em}
.kit li{margin:0 0 .35em;font-size:9.6pt;line-height:1.38;text-align:left}
.kit li b{font-weight:600}
.marks{display:grid;grid-template-columns:1fr 1fr;column-gap:.16in;row-gap:.12in;margin:.6em 0 1em}
.marks figure{margin:0}.marks img{max-height:1.35in;width:100%;object-fit:cover}
.pair{display:grid;grid-template-columns:1fr 1fr;column-gap:.16in;break-inside:avoid;margin:.8em 0}.pair figure{margin:0}
.pair img{max-height:2.3in}
.steps4{display:grid;grid-template-columns:repeat(4,1fr);column-gap:.08in;break-inside:avoid;margin:.8em 0}.steps4 figure{margin:0}
.steps4 img{max-height:1.55in}.steps4 figcaption{font-size:6.8pt}
.practice{margin-top:1.6em;border-top:.6pt solid #1E1913;padding-top:.7em;break-inside:avoid}
.practice ul{margin:0;padding:0;list-style:none;font-size:9.2pt;columns:2;column-gap:.2in}
.practice li{margin:.1em 0;break-inside:avoid}.practice a{font:700 7.6pt LivroSans;margin-right:.35em}
.practice .lvl{font:400 6.8pt LivroSans;color:#6E6253;margin-left:.25em}
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
.pline{margin-top:1.4em;border-top:.6pt solid #1E1913;padding-top:.08in;font:400 7.8pt/1.5 LivroSans;text-align:left}
.pline b{font-weight:700;margin-right:.3em}
.pline a.pg{border:0;font-weight:400}.pline a.pg::after{content:target-counter(attr(href), page)}
h2.newpage{break-before:page}
.obra{break-before:page;break-inside:avoid}
.obra > h2:first-child{margin-top:0}
.obra .figbal.side > figure img{max-height:3.55in}
.obra .figbal > figure img{max-height:2.9in}
.obra ol.laws ~ .figbal.side > figure img{max-height:2.6in}
.obra ol.laws ~ .figbal .bal img{width:.8in;height:.8in}
.obra ol.laws li{padding-top:.06in;padding-bottom:.06in}.pline a{font-weight:700;border-bottom:.5pt solid #BF8A5A}
.balrow{display:flex;gap:.22in;justify-content:center}
.bal{width:1.45in;flex:none;margin:0;text-align:left}
.bal img{width:1.1in;height:1.1in;border-radius:50%;display:block;margin:0 0 .08in}
.bal figcaption{margin:0;font-size:7.8pt;line-height:1.4}
.bal figcaption b{display:block;font-weight:700;color:#1E1913;margin-bottom:.02in}
.mapa{page:full;break-before:page;width:6in;height:9in}
.mapa svg{display:block;width:6in;height:9in}
.enderecos{break-before:page}
.enderecos h2,.tracos h2{font:400 17pt/1.1 LivroDisp;margin:0 0 .05in}
.enderecos .sub,.tracos .sub{font:italic 10pt/1.35 LivroSerif;margin:0 0 .2in;text-align:left}
.end{display:flex;gap:.12in;border-top:.6pt solid #CFC4B0;padding:.07in 0}
.end .en{flex:none;width:.2in;height:.2in;border-radius:50%;background:#1E1913;color:#F4EFE6;font:700 6.8pt/.2in LivroSans;text-align:center}
.end p{margin:0;text-align:left;font-size:9.2pt;line-height:1.32}.end b{font:700 8.4pt LivroSans}.end .ey{font:400 7.6pt LivroSans;color:#6E6253}
.tracos{break-before:page}
.tr{display:flex;gap:.16in;border-top:.6pt solid #CFC4B0;padding:.07in 0 .08in;break-inside:avoid}
.tr img{width:2.3in;height:1.1in;flex:none}
.trt p{margin:0;text-align:left;font-size:9pt;line-height:1.32}.trt .ty{font:400 16pt/1 LivroDisp}
.trt .tp{font:700 7.6pt LivroSans;margin:.05in 0 .04in}.trt .tp i{font-weight:400}
.tr2{break-before:page;padding-top:.68in}
.lvhead .lvtag{position:absolute;left:0;bottom:.62in;font:400 30pt/1 LivroDisp;color:#BF8A5A;margin:0}

/* blocos numerados e diagramas */
ol.laws{list-style:none;margin:.6em 0 1.2em;padding:0;counter-reset:law}
ol.laws li{counter-increment:law;position:relative;padding:.09in 0 .09in .46in;border-top:.6pt solid #CFC4B0;text-align:left;break-inside:avoid}
ol.laws li:last-child{border-bottom:.6pt solid #CFC4B0}
ol.laws li::before{content:counter(law);position:absolute;left:0;top:.06in;font:400 17pt/1 LivroDisp;color:#1E1913}
ol.laws li b{display:block;font:700 8.8pt LivroSans;margin-bottom:.03in}
figure.diag img{width:100%;max-height:none}

/* final */
.fim{page:kraft;break-before:page;width:6in;height:9in;position:relative}
.fim img{position:absolute;left:.7in;top:.8in;width:4.6in;height:4.2in;object-fit:contain}
.fim .fq{position:absolute;left:.85in;right:.85in;top:5.45in;font:italic 400 15pt/1.35 LivroSerif;text-align:left;color:#1E1913}
.fim .fs{position:absolute;left:.85in;right:.85in;top:7.25in;font:500 7.4pt/1.4 LivroSans;color:#4A4034;text-align:left}
.contra{page:full;break-before:page;width:6in;height:9in;background:#2A2119;color:#EFE8DA;text-align:center;position:relative}
.contra .ct1{position:absolute;left:0;right:0;top:3.7in;font:400 30pt/1 LivroSerif;text-align:center}
.contra .ct2{position:absolute;left:0;right:0;top:4.35in;font:italic 400 11pt LivroSerif;color:#BDB09A;text-align:center}
.contra .ct3{position:absolute;left:0;right:0;bottom:.7in;font:500 8pt LivroSans;letter-spacing:.2em;text-align:center}
/* obra em página inteira */
.bleed{page:full;break-before:page;width:6in;height:9in;position:relative;overflow:hidden}
.bleed img{position:absolute;inset:0;width:6in;height:9in;object-fit:cover}
.bleed::after{content:"";position:absolute;left:0;right:0;bottom:0;height:2in;background:linear-gradient(to bottom,rgba(240,233,218,0),rgba(240,233,218,.92) 60%)}
.bleed.dark::after{content:"";position:absolute;left:0;right:0;bottom:0;height:2.2in;background:linear-gradient(to bottom,rgba(15,11,8,0),rgba(15,11,8,.8) 70%)}
.bleed .bcap{position:absolute;left:.4in;right:.4in;bottom:.45in;z-index:2;white-space:nowrap;font:400 7pt/1.45 LivroSans;color:#1E1913;text-align:left;margin:0}
.bleed .bcap i{font:italic 400 9.6pt LivroSerif}
.bleed.dark .bcap{color:#FBF8F1}
/* capa */
.cover{page:full;position:relative;width:6in;height:9in;background:#2A2119;color:#FBF8F1;break-after:page;bookmark-level:1;bookmark-label:"Capa"}
.cover .art{position:absolute;top:0;bottom:0;left:0;right:0;background:url("img/cover-roulin.jpg") 37% 0/122% auto no-repeat}
.cover .topsh{position:absolute;left:0;right:0;top:0;height:1.1in;background:linear-gradient(to bottom,rgba(20,15,10,.32),rgba(20,15,10,0))}
.cover .shade{position:absolute;left:0;right:0;bottom:0;height:5in;background:linear-gradient(to bottom,rgba(20,15,10,0),rgba(20,15,10,.55) 45%,rgba(20,15,10,.66))}
.cover .spine{position:absolute;top:0;bottom:0;left:0;width:.13in;background:#F7F4EE}
.cover .ed{position:absolute;top:.38in;left:0;right:0;text-align:center;font:500 10.5pt LivroSans;letter-spacing:.2em}
.cover .t{position:absolute;left:0;right:0;top:5.75in;text-align:center;font:400 50pt/1 LivroSerif;letter-spacing:-.012em;white-space:nowrap}
.cover .d{position:absolute;left:0;right:0;top:6.57in;text-align:center;font:italic 400 15pt LivroSerif}
.cover .coll{position:absolute;bottom:.42in;left:0;right:0;text-align:center;font:italic 400 10.5pt LivroSerif}

/* folha de rosto e créditos */
.titlepage{page:bare;break-before:page;text-align:center;padding-top:2.3in}
.titlepage .t{font:400 34pt/1 LivroSerif;margin:0 0 .25em;text-align:center;letter-spacing:-.01em}
.titlepage .s{font:italic 400 12pt LivroSerif;color:#6E6253;text-align:center;margin:0 0 3.2in}
.titlepage .a{font:500 9pt LivroSans;letter-spacing:.2em;text-align:center}
.copy{page:bare;break-before:page;padding-top:5.3in;font:400 7.6pt/1.5 LivroSans;color:#6E6253}.copy p{text-align:left;margin-bottom:.8em}

/* sumário */
.toc{page:bare;break-before:page;bookmark-level:1;bookmark-label:"Sumário"}
.toc h1{font:400 22pt/1 LivroDisp;margin:0 0 .3in}
.toc a{color:#1E1913;text-decoration:none}
.toc .blk{display:flex;margin-bottom:.19in}
.toc .col{width:.5in;flex:none;font:400 10pt/1.6 LivroSans;color:#BF8A5A;padding-top:.01in}
.toc .body{flex:1}
.toc p{display:flex;justify-content:space-between;align-items:baseline;margin:0;text-align:left}
.toc .pt{font:400 11pt/1.6 LivroDisp;margin-bottom:.04in;border-bottom:.5pt solid #1E1913;padding-bottom:.03in}
.toc .r{font:400 10.2pt/1.5 LivroSerif}
.toc .pg::after{content:target-counter(attr(href),page);font:400 8.4pt LivroSans;color:#6E6253}
.toc .pt .pg::after{color:#1E1913}
/* páginas de parte */
.partimg{page:kraft;break-before:page;width:6in;height:9in;position:relative}
.partimg img{position:absolute;left:.55in;top:.55in;width:4.9in;height:7.4in;object-fit:contain}
.partimg .pcap{position:absolute;left:.55in;right:.55in;bottom:.45in;font:400 7pt/1.4 LivroSans;color:#4A4034;text-align:center}
.partimg .pcap i{color:#1E1913}
.part{page:part;break-before:page;position:relative;width:6in;height:9in;color:#1E1913}
.part .plab{position:absolute;left:.55in;top:1.72in;font:500 7.4pt LivroSans;margin:0}
.part .prule{position:absolute;left:.55in;right:.55in;top:1.95in;border-top:.6pt solid #1E1913}
.part .pnum{position:absolute;left:.5in;top:2.1in;font:400 118pt/1 LivroDisp;margin:0}
.part h1{position:absolute;left:.55in;top:3.85in;width:4.4in;font-size:23pt;margin:0}
.part .pintro{position:absolute;left:.55in;top:4.85in;width:3.9in;font-size:9.6pt;line-height:1.42}
.part .pintro p{text-align:left;margin:0 0 .55em}

/* capítulos */
section.chap{page:chap;break-before:page}
.chhead{position:relative;height:2.95in;margin-bottom:.15in}
.chhead .chlab{position:absolute;left:0;top:.05in;font:500 7.4pt/1.4 LivroSans;margin:0}
.chhead .chnum{position:absolute;right:-.08in;top:-.2in;font:400 132pt/1 LivroDisp;color:#BF8A5A;margin:0}
.chhead h1{position:absolute;left:0;bottom:0;width:3.7in;margin:0;font-size:23pt}
.chhead.nonum{height:1.9in}
section.front{page:chap;break-before:page}
section.front h1{font:400 30pt/1.1 LivroSerif;text-align:center;margin:.25in 0 .9em;letter-spacing:-.01em}
section.front .ini{font:400 38pt/.8 LivroSerif;float:left;margin:.04in .07in 0 0}

/* níveis */
section.level{page:chap;break-before:page}
.lvhead{height:3.2in;position:relative}
.lvhead .chlab{position:absolute;left:0;top:.05in;font:500 7.4pt LivroSans;margin:0}
.lvhead .chnum{position:absolute;right:-.06in;top:-.2in;font:400 120pt/1 LivroDisp;color:#BF8A5A;margin:0}
.lvhead h1{position:absolute;left:0;right:0;bottom:0;margin:0;font-size:23pt;white-space:nowrap}
.lvlist{columns:2;column-gap:.22in;margin-top:.9em;border-top:.6pt solid #1E1913;padding-top:.1in}
.lvlist p{font-size:8.8pt;line-height:1.3;text-align:left;margin:0 0 .3em;break-inside:avoid}
.lvlist b{font:700 7.4pt LivroSans;display:inline-block;width:.36in}

/* exercícios */
.ex{break-before:page;break-inside:avoid}
.ex.half{break-before:auto;height:3.5in;margin-top:0;overflow:hidden}
.pair2{break-before:page}
.pshead{border-bottom:.6pt solid #1E1913;padding-bottom:.06in;margin-bottom:.12in}
.pshead .psl{font:400 13pt LivroDisp;margin:0;white-space:nowrap}.pshead .pst{font:400 7.6pt LivroSans;color:#6E6253;margin:.03in 0 0;text-align:left}
.pair2.first .ex.half{height:3.14in}
.pair2 .ex.half + .ex.half{border-top:.6pt solid #CFC4B0;padding-top:.14in;margin-top:.14in}
.exh{position:relative;height:.62in}
.exh .code{position:absolute;left:0;top:0;font:400 30pt/1 LivroDisp}
.exh .lv{position:absolute;left:1.25in;top:.07in;font:500 7.2pt/1.4 LivroSans;color:#1E1913}
.half .exh{height:.5in}.half .exh .code{font-size:23pt}.half .exh .lv{left:.95in;top:.02in}
.ex h3{font:400 13pt/1.12 LivroDisp;margin:0 0 .12in}
.half h3{font-size:11pt;margin-bottom:.08in}
.meta{display:flex;border-top:.6pt solid #1E1913;border-bottom:.6pt solid #1E1913;margin-bottom:.14in;font:400 7.2pt/1.35 LivroSans}
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
.exfoot .done{width:1.5in;border-left:1.3pt solid #BF8A5A;padding-left:.08in;font:400 7.4pt/1.4 LivroSans}
.exfoot .done b{font-weight:700}
.half .exfoot{display:block}.half .exfoot .done{width:auto;margin-top:.06in}
.exref{font:400 7.2pt/1.4 LivroSans;color:#6E6253;margin-top:.12in;text-align:left}
.exref a{border-bottom:.5pt solid #BF8A5A;color:#1E1913}

/* catálogo */
.iconimg{page:kraft;break-before:page;width:6in;height:9in;position:relative}
.iconimg img{position:absolute;left:.45in;top:.45in;width:5.1in;height:8.1in;object-fit:contain}
.iconinfo{page:bare;break-before:page;position:relative;height:7.5in}
.iconinfo .ptop{display:flex;justify-content:space-between;border-bottom:.6pt solid #1E1913;padding-bottom:.06in;font:500 7.2pt LivroSans;margin-bottom:.9in}
.iconinfo .no{font:400 36pt/1 LivroDisp;margin:0 0 .1in}
.iconinfo h2{font:italic 400 17pt/1.2 LivroSerif;margin:0 0 .18in}
.iconinfo .cc{font:400 7.8pt/1.45 LivroSans;color:#6E6253;text-align:left}
.iconinfo .cl{font-size:10.6pt;line-height:1.45;margin:.2in 0}
.ficha{width:100%;font:400 7.4pt LivroSans;margin-top:.15in}
.iconinfo .balrow{margin-top:.35in;justify-content:flex-start;gap:.18in}
.iconinfo .bal{width:1.5in}
.ficha td{border-top:.6pt solid #A39682;border-bottom:none;padding:.05in 0}
.ficha td:first-child{width:.95in;color:#6E6253}
.catlist{}
.cat{display:flex;gap:.16in;margin:0 0 .12in;break-inside:avoid;align-items:flex-start;border-top:.6pt solid #CFC4B0;padding-top:.1in}
.cat .im{width:1.15in;flex:none;text-align:left}
.cat img{max-width:1.15in;max-height:1.25in}
.cat p{text-align:left;margin:0 0 .18em}
.cat .ct{font:400 10.4pt/1.25 LivroSerif}
.cat .cn{font:400 9pt LivroDisp;margin-right:.35em}
.cat .cc{font:400 7.2pt/1.42 LivroSans;color:#6E6253}
.cat .cf{font:400 6.8pt/1.4 LivroSans;color:#6E6253}
.cat .cl{font-size:8.8pt;line-height:1.34}

/* índice */
.idx{columns:2;column-gap:.25in}
.idx p{font-size:8.6pt;line-height:1.28;margin:0 0 .16em;text-align:left;break-inside:avoid}
.idx b{font:700 7.2pt LivroSans;display:inline-block;width:.33in}
.idx span{font:400 6.6pt LivroSans;color:#6E6253}
.idx h4{column-span:none;margin:.8em 0 .3em}
"""

def chapter_head(s, part):
    h = s['html']
    m = re.match(r'\s*<h1>(.*?)</h1>', h, re.S)
    title = m.group(1) if m else esc(s['title'])
    body = h[m.end():] if m else h
    n = re.match(r'(\d+)\.\s*(.*)', title)
    plab = f'{part[1]} · {part[2]}' if part else 'Reference'
    short = re.sub(r':.*', '', n.group(2) if n else title)
    rh = f'<span class="rh">{short}</span>'
    if n:
        head = f'<div class="chhead"><p class="chlab">{plab}<br/>Chapter {n.group(1)}</p><p class="chnum">{n.group(1)}</p><h1>{n.group(2)}</h1></div>'
    else:
        head = f'<div class="chhead nonum"><p class="chlab">{plab}</p><h1>{title}</h1></div>'
    return rh + head, body, (n.group(2) if n else title)

def ex_pdf(x, chapnames, half=False):
    cid, cname = CHAP[x['ch']]
    lvn = {l[0]: (l[2], l[3]) for l in LEVELS}
    tempo, _, mat = x['m'].partition(' · ')
    ln, lname = lvn[x['lv']]
    head = (f'<div class="exh"><span class="code">{x["id"].upper()}</span>'
            f'<span class="lv">{ln} · {lname}<br/>{cname} · {esc(chapnames.get(cid, ""))}</span></div>'
            f'<h3>{esc(x["t"])}</h3>')
    meta = (f'<div class="meta"><div>Time<b>{esc(tempo)}</b></div><div>Materials<b>{esc(mat)}</b></div>'
            f'<div>Theory<b><a href="#{cid}">{cname}</a></b></div></div>')
    if x['id'] in STAGES and not half:
        st = ''.join(f'<figure><img src="img/st-{x["id"]}-{k}.jpg" alt="Stage {k} of exercise {x['id'].upper()}: {STN[k-1].lower()}"/><figcaption>{k} · {STN[k-1]}</figcaption></figure>' for k in (1, 2, 3))
        art = f'<div class="exart"><img class="model" src="img/{x["id"]}.jpg" alt="Model drawing for exercise {x['id'].upper()}"/><div class="steps">{st}</div></div>'
    else:
        art = f'<div class="exsolo"><img src="img/{x["id"]}.jpg" alt="Model drawing for exercise {x['id'].upper()}"/></div>'
    ref = ''
    if x.get('ref') and x['ref'] in PL:
        ref = f'<p class="exref">Work to compare: <a href="#cat-{x["ref"]}"><i>{esc(PL[x["ref"]]["t"])}</i></a>, in the catalogue.</p>'
    foot = (f'<div class="exfoot"><div class="desc"><p>{esc(x["d"])}</p></div>'
            f'<div class="done"><b>Done when</b> {esc(x["c"])}</div></div>')
    return f'<section class="ex{" half" if half else ""}" id="ex-{x["id"]}">{head}{meta}{art}{foot}{ref}</section>'

def level_pdf(code, lid, ln, name, intro, chapnames):
    items = [x for x in EX if x['lv'] == code]
    lst = ''.join(f'<p><b><a href="#ex-{x["id"]}">{x["id"].upper()}</a></b>{esc(x["t"])}</p>' for x in items)
    out = [f'<section class="level" id="{lid}"><span class="rh">Studies · {ln}</span>'
           f'<div class="lvhead"><p class="chlab">Part III · Studies</p><p class="lvtag">{ln}</p><h1>{name}</h1></div>'
           f'<p class="lead">{intro}</p><div class="lvlist">{lst}</div></section>']
    if code == 'w':
        for i in range(0, len(items), 2):
            out.append('<div class="pair2">' + ''.join(ex_pdf(x, chapnames, half=True) for x in items[i:i + 2]) + '</div>')
    else:
        out += [ex_pdf(x, chapnames) for x in items]
    return ''.join(out)

def cat_numbers():
    order = CAT_ORDER + [k for k in PL if k not in CAT_ORDER]
    return {k: i for i, k in enumerate(order, 1)}, order

def ficha(k):
    p = PL[k]; f = FI.get(k, {})
    inst = f.get('inst', '')
    if inst and inst.split(' (')[0].split(',')[0][:12] in p['c']:
        inst = ''
    return f, inst

def catalogue_pdf():
    num, order = cat_numbers()
    cards = []
    for k in order:
        p = PL[k]; f, inst = ficha(k)
        fi = ' · '.join(v for v in [f.get('cat'), f.get('dim'), inst] if v)
        cards.append(f'<div class="cat" id="cat-{k}"><div class="im"><img src="img/{k}.jpg" alt="{esc(p["t"])}"/></div><div>'
                     f'<p class="ct"><span class="cn">{num[k]}</span><i>{esc(p["t"])}</i></p><p class="cc">{esc(p["c"])}</p>'
                     + (f'<p class="cf">{esc(fi)}</p>' if fi else '') + f'<p class="cl">{esc(p.get("l", ""))}</p></div></div>')
    return ('<section class="chap" id="catalogo"><span class="rh">Catalogue of Works</span>'
            '<div class="chhead nonum"><p class="chlab">Reference</p><h1>Catalogue of Works</h1></div>'
            '<p>The works by Van Gogh cited in the book and suggested in the exercises, in approximate order of date. Where available, '
            'the F (de la Faille) and JH (Hulsker) catalogue numbers follow, with dimensions (height by width) and the collection.</p>'
            + ''.join(cards) + '</section>')

def ex_index_pdf():
    lvn = {l[0]: l[2] for l in LEVELS}
    groups = [('r', 'Hatchings'), ('f', 'Flow'), ('c', 'Faces'), ('a', 'Self-Portraits'), ('b', 'Body'), ('p', 'Project')]
    body = ''
    for ch, nm in groups:
        body += f'<h4>{nm}</h4>' + ''.join(f'<p><b><a href="#ex-{x["id"]}">{x["id"].upper()}</a></b>{esc(x["t"])} <span>{lvn[x["lv"]]}</span></p>'
                                         for x in sorted(EX, key=lambda x: x['id']) if x['ch'] == ch)
    return ('<section class="chap" id="indice"><span class="rh">Index of Exercises</span>'
            '<div class="chhead nonum"><p class="chlab">Reference</p><h1>Index of Exercises</h1></div>'
            f'<div class="idx">{body}</div></section>')

def pdf_html(S):
    chapnames = {}
    for s in S:
        m = re.match(r'\s*<h1>\d+\.\s*(.*?)</h1>', s.get('html', ''))
        if m:
            chapnames[s['id']] = re.sub(r':.*', '', m.group(1))
    yr = datetime.date.today().year
    P = [f'<!doctype html><html lang="en-US"><head><meta charset="utf-8"><title>Van Gogh in Pencil</title>'
         f'<meta name="author" content="Pedro Torres"><style>{font_faces()}{PDF_CSS}</style></head><body>']
    P.append('<div class="cover"><div class="art"></div><div class="topsh"></div><div class="shade"></div>'
             '<div class="ed">PEDRO TORRES</div><div class="t">Van Gogh in Pencil</div><div class="d">Theory and Practice for Drawing Like Vincent</div>'
             f'<div class="coll">{NEX} exercises in four levels</div></div>')
    P.append('<div class="titlepage"><p class="t">Van Gogh in Pencil</p><p class="s">Theory and Practice for Drawing Like Vincent</p><p class="a">PEDRO TORRES</p></div>')
    P.append(f'<div class="copy"><p>© {yr} Pedro Torres. All rights reserved.</p>'
             '<p>No part of this book may be reproduced without the author’s permission, except the exercise pages, for the reader’s personal use.</p>'
             '<p>Cover: <i>Portrait of Joseph Roulin</i>, Arles, August 1888. Reed pen and quill, ink and black chalk. J. Paul Getty Museum, Los Angeles (85.GA.299), Open Content Program.</p>'
             '<p>Originally published in Brazilian Portuguese as <i>Van Gogh a Lápis</i>.</p>'
             f'<p>Set in EB Garamond and Archivo. First English edition, {yr}.</p></div>')
    # sumário
    def row(label, href):
        return f'<p class="r"><a href="#{href}">{label}</a><a class="pg" href="#{href}"></a></p>'
    def blk(num, inner):
        return f'<div class="blk"><div class="col">{num}</div><div class="body">{inner}</div></div>'
    def head(pid):
        return f'<p class="pt"><a href="#{pid}">{PARTS[pid][2]}</a><a class="pg" href="#{pid}"></a></p>'
    caps = ''.join(row(t.replace('. ', '.&#8194;', 1), i) for i, t in ((x['id'], x['title']) for x in S if x['kind'] == 'chapter' and re.match(r'\d+\.', x['title'])))
    lv = row('Level 1&#8194;Foundations, at the end of chapters 2 to 6', 'primeiros-passos') + ''.join(row(f'{l[2]}&#8194;{l[3]}', l[1]) for l in LEVELS if l[0] != 'w')
    front = ''.join(row(esc(x['title']), x['id']) for x in S if x['kind'] == 'front')
    back = ''.join(row(esc(x['title']), x['id']) for x in S if x['kind'] == 'back')
    toc = ['<div class="toc"><h1>Contents</h1>', blk('', front),
           blk('01', head('parte1') + row('Vincent’s Path', 'toc-caminho') + row('From Zundert to Auvers', 'toc-periodos') + row('Ten Years in Ten Lines', 'toc-tracos')),
           blk('02', head('parte2') + caps), blk('03', head('parte3') + lv), blk('', back), '</div>']
    P.extend(toc)
    part = None
    vida_intro = ''
    for s in S:
        if s['id'] == 'vida':
            m = re.match(r'\s*<h1>.*?</h1>(.*?)<!--MAPA-->', s['html'], re.S)
            vida_intro = m.group(1).strip()
    for s in S:
        k = s['kind']
        if k == 'part':
            part = PARTS[s['id']]
            n, lab, name, intro = part
            if intro is None:
                intro = vida_intro
            art = PART_ART[s['id']]
            P.append(f'<section class="partimg"><img src="img/{art}.jpg" alt="{esc(PL[art]["t"])}"/>'
                     f'<p class="pcap"><i>{esc(PL[art]["t"])}</i>. {esc(PL[art]["c"])}</p></section>')
            P.append(f'<section class="part" id="{s["id"]}" style="bookmark-level:1;bookmark-label:\'{lab} · {name}\'">'
                     f'<p class="plab">{lab}</p><div class="prule"></div><p class="pnum">{n}</p><h1>{name}</h1><div class="pintro">{intro if intro.startswith('<p>') else '<p>' + intro + '</p>'}</div></section>')
        elif k == 'front':
            h = s['html']
            m = re.match(r'\s*<h1>(.*?)</h1>', h, re.S)
            body = h[m.end():]
            if s['id'] == 'prefacio':
                body = re.sub(r'<p>(\w)', r'<p><span class="ini">\1</span>', body, count=1)
            P.append(f'<section class="front" id="{s["id"]}" style="bookmark-level:1;bookmark-label:\'{s["title"]}\'"><span class="rh">{s["title"]}</span><h1>{m.group(1)}</h1>{body}</section>')
        elif k == 'level':
            code, lid, ln, name, intro = next(l for l in LEVELS if l[1] == s['id'])
            art = LEVEL_ART.get(code)
            if art:
                P.append(f'<section class="partimg"><img src="img/{art}.jpg" alt="{esc(PL[art]["t"])}"/>'
                         f'<p class="pcap"><i>{esc(PL[art]["t"])}</i>. {esc(PL[art]["c"])}</p></section>')
            P.append(level_pdf(code, lid, ln, name, intro, chapnames).replace(
                f'<section class="level" id="{lid}">', f'<section class="level" id="{lid}" style="bookmark-level:2;bookmark-label:\'{ln} · {name}\'">', 1))
        elif s['id'] == 'catalogo':
            P.append(catalogue_pdf().replace('<section class="chap" id="catalogo">', '<section class="chap" id="catalogo" style="bookmark-level:1;bookmark-label:\'Catálogo das obras\'">', 1))
        elif s['id'] == 'indice':
            P.append(ex_index_pdf().replace('<section class="chap" id="indice">', '<section class="chap" id="indice" style="bookmark-level:1;bookmark-label:\'Índice dos exercícios\'">', 1))
        elif s['id'] == 'vida':
            body = s['html'][s['html'].index('<!--MAPA-->'):].replace('<h2>', '<h2 id="toc-periodos">', 1)
            body = body.replace('<!--MAPA-->', '<!--MAPA--><span class="rh">Ten Years of Drawing</span>', 1)
            P.append(f'<section id="vida">{body}</section>')
        else:
            head, body, t = chapter_head(s, part if k == 'chapter' else None)
            lvl = 2 if k == 'chapter' else 1
            lab = s['title'].replace("'", "’")
            P.append(f'<section class="chap" id="{s["id"]}" style="bookmark-level:{lvl};bookmark-label:\'{lab}\'">{head}{body}</section>')
            fs = s.get('first_steps')
            if fs:
                for i in range(0, len(fs), 2):
                    hd = ('<div class="pshead"><span class="rh">First Steps</span><p class="psl">First Steps</p>'
                          f'<p class="pst">Short exercises for {CHAP[fs[0]["ch"]][1]}, 8 to 20 minutes each.</p></div>') if i == 0 else ''
                    anchor = ' id="primeiros-passos"' if (i == 0 and fs[0]['ch'] == 'r') else ''
                    chunk = fs[i:i + 2]
                    if len(chunk) == 1 and i > 0:
                        P.append(ex_pdf(chunk[0], chapnames))
                    else:
                        P.append(f'<div class="pair2{" first" if i == 0 else ""}"{anchor}>{hd}' + ''.join(ex_pdf(x, chapnames, half=True) for x in chunk) + '</div>')
            if s['id'] in END_ART:
                P.append(bleed_html(END_ART[s['id']]))
    P.append('<section class="fim"><img src="img/harvest.jpg" alt="The Harvest, pen drawing by Van Gogh"/>'
             '<p class="fq">“What is drawing? How do you get there? It is working your way through an invisible iron wall '
             'that seems to stand between what you feel and what you are able to do.”</p>'
             '<p class="fs">Vincent van Gogh to Theo, The Hague, October 1882 (letter 274)</p></section>')
    P.append('<section class="contra"><p class="ct1">Van Gogh in Pencil</p><p class="ct2">Theory and Practice for Drawing Like Vincent</p>'
             '<p class="ct3">PEDRO TORRES</p></section>')
    P.append('</body></html>')
    html_ = '\n'.join(P).replace('<!--MAPA-->', map_html(True))
    # cada capítulo ganha um nome de página próprio, para a primeira página sair sem rodapé
    n = [0]
    def pg(m):
        n[0] += 1
        return f'{m.group(1)} style="page:pg{n[0]};'
    html_ = re.sub(r'(<section class="(?:chap|front|level)" id="[^"]+") style="', pg, html_)
    extra = ''.join(f'@page :nth(1 of pg{i}){{@bottom-left{{content:none}}@bottom-right{{content:none}}}}' for i in range(1, n[0] + 1))
    return html_.replace('</style>', extra + '</style>', 1)

# ---------------------------------------------------------------- impresso (KDP Paperback)
# Miolo 6 × 9 pol. com sangria: o WeasyPrint gera 6,25 × 9,25 (0,125 pol. em volta) e depois se corta
# o lado da lombada de cada página, chegando aos 6,125 × 9,25 que a KDP pede. Sem capa nem contracapa,
# sem o fundo bege (o papel creme faz esse papel) e com as obras de página inteira em alta resolução (img/hd).
SANGRIA = .125
PAPEL_ESPESSURA = {'branco': 0.002252, 'creme': 0.0025}
PRINT_CSS = """
@page{bleed:.125in;background:none}
@page mapa{margin:0;background:#E8E2D4;@bottom-left{content:none}@bottom-right{content:none}}
.mapa{page:mapa}
.mapa svg{width:5.2in;height:7.8in;margin:.6in auto 0}  /* texto do mapa a mais de 0,375 pol. do corte (exigência da KDP) */
.bleed{overflow:visible}
.bleed img{left:-.125in;top:-.125in;width:6.25in;height:9.25in}
.bleed::after,.bleed.dark::after{left:-.125in;right:-.125in;bottom:-.125in}
"""
CREDITO_HD = ('<p>The reproduction of <i>Self-Portrait as a Painter</i> in this print edition is a photograph by the Van Gogh Museum, '
              'Amsterdam (Vincent van Gogh Foundation), published on Wikimedia Commons under the CC BY 4.0 license.</p>')

def print_html(S):
    h = pdf_html(S)
    h = re.sub(r'<div class="cover">.*?</div></div>', '', h, count=1, flags=re.S)
    h = re.sub(r'<section class="contra">.*?</section>', '', h, count=1, flags=re.S)
    # sem a capa, todas as páginas trocariam de lado (aberturas de parte deixariam de ser páginas espelhadas):
    # uma prancha com o desenho da capa na p. 3 devolve a ordem do PDF de leitura
    prancha = ('<section class="partimg"><img src="img/cover-roulin.jpg" alt="Portrait of Joseph Roulin, drawing by Van Gogh"/>'
               '<p class="pcap"><i>Portrait of Joseph Roulin</i>. Arles, August 1888. Reed pen and quill, ink and black chalk. '
               'J. Paul Getty Museum, Los Angeles.</p></section>')
    h = re.sub(r'(<div class="copy">.*?</div>)', lambda m: m.group(1) + prancha, h, count=1, flags=re.S)
    for f in glob.glob('img/hd/*.jpg'):
        h = h.replace(f'img/{os.path.basename(f)}"', f'img/hd/{os.path.basename(f)}"')
    if os.path.exists('img/hd/sp_painter-sem-moldura.jpg'):
        h = re.sub(r'(<section class="chap" id="creditos"[^>]*>.*?)(</section>)', lambda m: m.group(1) + CREDITO_HD + m.group(2), h, count=1, flags=re.S)
    return h.replace('</style>', PRINT_CSS + '</style>', 1)

def corta_lombada(src, dst):
    """Tira a sangria do lado da lombada: página ímpar (direita) perde a faixa da esquerda, a par perde a da direita."""
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import RectangleObject
    r = PdfReader(src); w = PdfWriter(); s = SANGRIA * 72
    for i, p in enumerate(r.pages):
        x0, y0, x1, y1 = [float(v) for v in p.mediabox]
        box = RectangleObject([x0 + s, y0, x1, y1] if i % 2 == 0 else [x0, y0, x1 - s, y1])
        p.mediabox = box; p.cropbox = box; p.bleedbox = box
        p.trimbox = RectangleObject([x0 + s, y0 + s, x1 - s, y1 - s])
        w.add_page(p)
    w.add_metadata({'/Title': 'Van Gogh in Pencil', '/Author': 'Pedro Torres'})
    w.write(dst)

SINOPSE = ('<p>Van Gogh drew far more than he painted. It was on paper, with a carpenter’s pencil and a reed pen, that he invented '
           'the way of seeing he later took to the canvas: dots, dashes, commas and swirls, each with a job to do.</p>'
           '<p>This book teaches that language. It follows Vincent’s ten years of drawing, takes the method apart in eight chapters '
           '(the marks, the flow, the face, the self-portraits, the body, how a sheet is built, the master copy) and offers '
           f'{NEX} exercises in four levels, each with a model drawing, a time, materials and a clear sign of when it is done.</p>'
           '<p>For people who have never drawn and want a clear path, and for those who already draw and want to learn to look the way Vincent looked.</p>')

CAPA_IMPRESSA = """<!doctype html><html lang="en-US"><head><meta charset="utf-8"><style>{fonts}
@page{{size:{W}in {H}in;margin:0}}*{{margin:0;padding:0}}body{{width:{W}in;height:{H}in;position:relative;background:#2A2119;overflow:hidden}}
.back{{position:absolute;left:0;top:0;width:{BW}in;height:{H}in;background:#2A2119;color:#EFE8DA}}
.back .in{{position:absolute;left:{BX}in;top:{BY}in;width:{BTW}in}}
.back .k{{font:500 8pt LivroSans;letter-spacing:.2em;color:#BDB09A;margin-bottom:.32in}}
.back .q{{font:italic 400 15.5pt/1.32 LivroSerif;margin-bottom:.35in}}
.back .q span{{display:block;font:500 7.2pt/1.4 LivroSans;font-style:normal;color:#BDB09A;margin-top:.12in}}
.back p.s{{font:400 10.4pt/1.45 LivroSerif;margin:0 0 .13in;text-align:left;hyphens:auto}}
.back .n{{font:500 8pt LivroSans;letter-spacing:.12em;color:#BDB09A;margin-top:.25in}}
.spine{{position:absolute;left:{SX}in;top:0;width:{SW}in;height:{H}in;background:#2A2119}}
.spine .t{{position:absolute;left:50%;top:50%;width:{H}in;transform:translate(-50%,-50%) rotate(90deg);text-align:center;white-space:nowrap;
  color:#FBF8F1;font:400 {SF}pt/1 LivroSerif}}
.spine .t b{{font:500 {SF2}pt LivroSans;letter-spacing:.18em;margin-left:.35in;font-weight:500}}
.front{{position:absolute;left:{FX}in;top:0;width:{FW}in;height:{H}in;overflow:hidden;background:#2A2119;color:#FBF8F1}}
.front .art{{position:absolute;inset:0;background:url("img/cover-roulin.jpg") {AX}in {AY}in/{AW}in auto no-repeat}}
.front .tr{{position:absolute;left:0;top:{S}in;width:6in;height:9in}}
.front .topsh{{position:absolute;left:0;right:0;top:0;height:1.1in;background:linear-gradient(to bottom,rgba(20,15,10,.32),rgba(20,15,10,0))}}
.front .shade{{position:absolute;left:0;right:-{S}in;bottom:-{S}in;height:5.125in;background:linear-gradient(to bottom,rgba(20,15,10,0),rgba(20,15,10,.55) 45%,rgba(20,15,10,.66))}}
.front .ed{{position:absolute;top:.38in;left:0;right:0;text-align:center;font:500 10.5pt LivroSans;letter-spacing:.2em}}
.front .ti{{position:absolute;left:0;right:0;top:5.75in;text-align:center;font:400 50pt/1 LivroSerif;letter-spacing:-.012em;white-space:nowrap}}
.front .d{{position:absolute;left:0;right:0;top:6.57in;text-align:center;font:italic 400 15pt LivroSerif}}
.front .coll{{position:absolute;bottom:.42in;left:0;right:0;text-align:center;font:italic 400 10.5pt LivroSerif}}
</style></head><body>
<div class="back"><div class="in"><p class="k">PEDRO TORRES</p>
<p class="q">“What is drawing? It is working your way through an invisible iron wall that seems to stand between what you feel and what you are able to do.”<span>VINCENT VAN GOGH TO THEO, 1882</span></p>
{sinopse}<p class="n">{nex} EXERCISES IN FOUR LEVELS</p></div></div>
<div class="spine"><p class="t">Van Gogh in Pencil<b>PEDRO TORRES</b></p></div>
<div class="front"><div class="art"></div><div class="tr"><div class="topsh"></div></div><div class="shade"></div><div class="tr">
<div class="ed">PEDRO TORRES</div><div class="ti">Van Gogh in Pencil</div><div class="d">Theory and Practice for Drawing Like Vincent</div>
<div class="coll">{nex} exercises in four levels</div></div></div>
</body></html>"""

def make_print_cover(paginas, papel='creme'):
    """Capa inteira (contracapa + lombada + capa) com 0,125 pol. de sangria em volta, para a KDP."""
    from weasyprint import HTML
    s = SANGRIA; lomb = paginas * PAPEL_ESPESSURA[papel]
    W, H = 2 * s + 12 + lomb, 9 + 2 * s
    # a obra da capa mede como na capa do PDF (122 % da largura de 6 pol., deslocada a 37 %), presa ao corte
    aw = 6 * 1.22; ax = .37 * (6 - aw)
    html_ = CAPA_IMPRESSA.format(fonts=font_faces(), W=f'{W:.4f}', H=f'{H:.4f}', S=s,
                                 BW=f'{s + 6:.4f}', BX=s + .55, BY=s + .75, BTW=6 - 1.1,
                                 SX=f'{s + 6:.4f}', SW=f'{lomb:.4f}', SF=min(13, lomb * 72 * .5), SF2=min(7.5, lomb * 72 * .3),
                                 FX=f'{s + 6 + lomb:.4f}', FW=f'{6 + s:.4f}', AX=f'{ax:.4f}', AY=0, AW=f'{aw:.4f}',
                                 sinopse=SINOPSE.replace('<p>', '<p class="s">'), nex=NEX)
    HTML(string=html_, base_url=ROOT).write_pdf('out/Van-Gogh-in-Pencil-capa-impressa.pdf')
    return W, H, lomb

# ---------------------------------------------------------------- EPUB
EPUB_FONTS =[('LivroSerif', 'eb-garamond-latin-400-normal.ttf', 400, 'normal'), ('LivroSerif', 'eb-garamond-latin-400-italic.ttf', 400, 'italic'),
              ('LivroSerif', 'eb-garamond-latin-600-normal.ttf', 600, 'normal'), ('LivroDisp', 'archivo-black-latin-400-normal.woff', 400, 'normal'),
              ('LivroSans', 'archivo-latin-400-normal.woff', 400, 'normal'), ('LivroSans', 'archivo-latin-700-normal.woff', 700, 'normal')]
EPUB_CSS = """
body{font-family:LivroSerif,serif;line-height:1.5;margin:0}
h1{font-family:LivroDisp,sans-serif;font-weight:400;font-size:1.65em;line-height:1.12;margin:1.4em 0 .9em;page-break-before:always}
h1 .lvnum{display:block;font-family:LivroSans,sans-serif;font-weight:700;font-size:.45em;color:#8C5A2E;margin-bottom:.4em}
h2{font-family:LivroDisp,sans-serif;font-weight:400;font-size:1.15em;line-height:1.2;margin:1.6em 0 .5em}
h3{font-family:LivroSans,sans-serif;font-weight:700;font-size:1.05em;margin:.3em 0 .4em}
h4{font-family:LivroSans,sans-serif;font-weight:700;font-size:.78em;margin:0 0 .4em}
p{margin:0 0 .6em;text-indent:0}
a{color:inherit}
figure{display:block;margin:1.2em 0;text-align:center;page-break-inside:avoid}
img{max-width:100%;height:auto}
figcaption{font-family:LivroSans,sans-serif;font-size:.72em;line-height:1.45;color:#5F5446;text-align:left;margin-top:.4em}
.vida{border-left:3px solid #BF8A5A;padding:.1em 0 .1em .8em;margin:0 0 1.3em;font-size:.92em}
.marks figure,.pair figure{margin:.8em 0}
.kgrid{width:100%;border-collapse:collapse;margin:.4em 0 1.2em;page-break-inside:avoid}
.kgrid td.kc{border:0;padding:.2em .4em .4em;vertical-align:top;text-align:center}
.kgrid td.kc img{width:100%;max-width:9em}
.kgrid p.kt{font-family:LivroSans,sans-serif;font-size:.68em;line-height:1.35;color:#5F5446;text-align:left;margin:.3em 0 0}
.kgrid p.kt b{display:block;color:#1E1913}
.practice{border-top:1px solid #1E1913;margin-top:1.6em;padding-top:.6em;font-size:.9em}
.practice ul{list-style:none;padding:0}.practice a{font-family:LivroSans,sans-serif;font-weight:700;font-size:.85em;margin-right:.3em}
.practice .lvl{font-family:LivroSans,sans-serif;color:#6E6253;font-size:.75em}
.exnum{font-family:LivroDisp,sans-serif;font-size:1.9em;line-height:1;margin:1.2em 0 .1em}
section.ex{page-break-before:always}
.ex h3{font-family:LivroDisp,sans-serif;font-weight:400;font-size:1.2em}
.exmeta{font-family:LivroSans,sans-serif;font-size:.78em;color:#5F5446;border-top:1px solid #1E1913;border-bottom:1px solid #1E1913;padding:.35em 0}
.exref{font-family:LivroSans,sans-serif;font-size:.78em;color:#5F5446}
.crit{border-left:3px solid #BF8A5A;padding-left:.6em}.crit .sc{font-family:LivroSans,sans-serif;font-weight:700;font-size:.85em}
.lead{font-style:italic}.count{font-family:LivroSans,sans-serif;font-size:.75em;color:#6E6253}
table{border-collapse:collapse;width:100%;font-size:.88em}th,td{border-bottom:1px solid #CFC4B0;padding:.3em .4em;text-align:left;vertical-align:top}
th{font-family:LivroSans,sans-serif;font-size:.8em;border-bottom:1px solid #1E1913}
dl.gloss dt{font-family:LivroSans,sans-serif;font-weight:700;font-size:.9em;margin-top:.7em}dl.gloss dd{margin-left:0}
.sign{text-align:right;font-style:italic}
.cat{margin:0 0 1.4em;page-break-inside:avoid;clear:both;overflow:hidden;border-top:1px solid #CFC4B0;padding-top:.6em}.cat img{display:block;width:34%;margin:0 0 .5em}.cat div{overflow:hidden}
.cat p{margin:0 0 .2em}.cc,.cf{font-family:LivroSans,sans-serif;font-size:.75em;color:#5F5446}.cn{font-family:LivroDisp,sans-serif;margin-right:.35em}
.parttitle{margin-top:1.2em}.parttitle .pn{font-family:LivroDisp,sans-serif;font-size:3.6em;line-height:1;color:#BF8A5A;margin:0}
.parttitle h1{page-break-before:avoid;font-family:LivroSans,sans-serif;font-weight:700;font-size:.8em;margin:.6em 0 .2em}
.parttitle h2{font-size:1.7em;margin:0 0 .6em}
h2.ic img.icon{width:1.6em;height:1.6em;vertical-align:middle;margin-right:.4em}
.balrow{text-align:center;margin:-.4em 0 1.2em}
.bal{display:inline-block;width:30%;margin:.4em 1.2% .8em;vertical-align:top;text-align:left}
.bal img{width:100%;border-radius:50%}
.bal figcaption b{display:block;font-weight:700}
.mapa{margin:0 0 1.2em;text-align:center}
.end{border-top:1px solid #CFC4B0;padding:.4em 0;overflow:hidden}.end .en{float:left;font-family:LivroSans,sans-serif;font-weight:700;width:1.6em}
.end p{margin:0 0 0 1.6em}.end .ey{font-family:LivroSans,sans-serif;font-size:.8em;color:#5F5446}
.tr{border-top:1px solid #CFC4B0;padding:.6em 0;page-break-inside:avoid}.tr img{width:100%}
.trt .ty{font-family:LivroDisp,sans-serif;font-size:1.3em;margin:.3em 0 0}.trt .tp{font-family:LivroSans,sans-serif;font-size:.85em;font-weight:700;margin:0}
.tracos .sub,.enderecos .sub{font-style:italic}
ol.laws{list-style:none;padding:0}ol.laws li{border-top:1px solid #CFC4B0;padding:.5em 0}ol.laws li b{display:block;font-family:LivroSans,sans-serif}
figure.diag img{width:100%}
.titlepage{text-align:center;margin-top:25%}.titlepage .t{font-size:2.1em;line-height:1.1}.titlepage .s{font-style:italic;color:#5F5446}
.titlepage .a{font-family:LivroSans,sans-serif;font-size:.8em;letter-spacing:.2em;margin-top:3em}
.capa{margin:0;padding:0;height:100%;text-align:center}.capa svg{width:100%;height:100%}
"""

def xhtml(fragment):
    root = lhtml.fragment_fromstring(fragment, create_parent='div')
    s = ''.join(etree.tostring(c, method='xml', encoding='unicode') for c in root)
    if root.text and root.text.strip():
        s = esc(root.text) + s
    return s

def page(title, body):
    return ('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en-US" xml:lang="en-US">'
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
        im.putalpha(m.resize((360, 360), Image.LANCZOS))
        im.quantize(256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.FLOYDSTEINBERG).save(out, optimize=True)
    if not os.path.exists('img/mapa-caminho-en.png') or os.path.getmtime('img/mapa-caminho-en.png') < os.path.getmtime('img/mapa-caminho-en.svg'):
        from weasyprint import HTML
        with tempfile.TemporaryDirectory() as td:
            HTML(string=f'<style>{font_faces()}@page{{size:6in 9in;margin:0}}body{{margin:0}}</style>' + open('img/mapa-caminho-en.svg').read(),
                 base_url=ROOT).write_pdf(f'{td}/m.pdf')
            subprocess.run(['pdftoppm', '-r', '200', '-jpeg', '-singlefile', f'{td}/m.pdf', f'{td}/m'], check=True)
            Image.open(f'{td}/m.jpg').convert('RGB').save('img/mapa-caminho-en.png', optimize=True)

def kindle_html(body):
    """Simplifica o HTML para leitores: sem imagens lado a lado por porcentagem, sem SVG, sem páginas do PDF."""
    body = re.sub(r'<img class="icon"[^>]*?/?>', '', body)
    body = body.replace('img/mapa-caminho-en.svg', 'img/mapa-caminho-en.png')
    body = body.replace('print the exercise page and work on top of it with tracing paper, or open the page in an app',
                        'take a screenshot of the exercise and open it in an app')
    body = body.replace('To draw over a model, photocopy the page and use tracing paper, or photograph it, import it into a drawing app and work on a layer above.',
                        'To draw over a model, take a screenshot of it and open it in a drawing app, working on a layer above.')
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

def build_epub(S, out, small=None, kindle=False):
    files = []  # (name, title, body, kind)
    files.append(('titulo.xhtml', 'Title Page', '<div class="titlepage"><p class="t">Van Gogh in Pencil</p><p class="s">Theory and Practice for Drawing Like Vincent</p><p class="a">PEDRO TORRES</p></div>'
                  f'<p style="margin-top:3em;font-size:.8em">© {datetime.date.today().year} Pedro Torres. All rights reserved.</p>', 'front'))
    idfile = {}
    for i, s in enumerate(S):
        name = f'{i:02d}-{s["id"]}.xhtml'
        if s['kind'] == 'part':
            img = f'img/{PART_ART[s["id"]]}.jpg'
            n_, lab_, name_, intro_ = PARTS[s['id']]
            it = '' if intro_ is None else (intro_ if intro_.startswith('<p>') else f'<p>{intro_}</p>')
            body = (f'<section id="{s["id"]}"><figure><img src="{img}" alt="{esc(PL[PART_ART[s['id']]]['t'])}, drawing by Van Gogh"/></figure><div class="parttitle"><p class="pn">{n_}</p>'
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
    bid = 'urn:uuid:' + str(uuid.uuid5(uuid.NAMESPACE_URL, 'van-gogh-in-pencil-pedro-torres'))
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
        if not kindle:  # a capa como página: SVG que se ajusta a qualquer tela sem cortar nem esticar
            capa_svg = ('<div class="capa"><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" '
                        'width="100%" height="100%" viewBox="0 0 1500 2400" preserveAspectRatio="xMidYMid meet">'
                        '<image width="1500" height="2400" xlink:href="img/cover-en.jpg"/></svg></div>')
            z.writestr('OEBPS/cover.xhtml', page('Cover', capa_svg), compress_type=zipfile.ZIP_DEFLATED)
        for name, title, body, kind in files:
            x = xhtml(fixlinks(body))
            imgs.update(re.findall(r'src="(img/[^"]+)"', x))
            z.writestr('OEBPS/' + name, page(title, x), compress_type=zipfile.ZIP_DEFLATED)
        imgs.add('img/cover-en.jpg')
        for im in sorted(imgs):
            if im.endswith('.png'):
                z.write(im, 'OEBPS/' + im, compress_type=zipfile.ZIP_STORED)
            elif im.endswith('.svg'):
                z.write(im, 'OEBPS/' + im, compress_type=zipfile.ZIP_DEFLATED)
            elif im == 'img/cover-en.jpg':  # a Apple Books recusa imagem acima de 4 milhões de pixels
                from PIL import Image
                import io
                buf = io.BytesIO(); Image.open(im).convert('RGB').resize((1500, 2400), Image.LANCZOS).save(buf, 'JPEG', quality=90, optimize=True)
                z.writestr('OEBPS/' + im, buf.getvalue(), compress_type=zipfile.ZIP_STORED)
            elif small:
                from PIL import Image
                import io
                pic = Image.open(im).convert('RGB')
                # cada imagem no tamanho em que aparece: etapas ficam duas por linha, modelos de exercício em largura de tela
                base = os.path.basename(im)
                lado, q = (560, 72) if base.startswith('st-') else (800, 70) if re.match(r'[a-z]\d\d\.jpg$', base) else (small, 72)
                pic.thumbnail((lado, lado), Image.LANCZOS)
                buf = io.BytesIO(); pic.save(buf, 'JPEG', quality=q, optimize=True, progressive=True)
                z.writestr('OEBPS/' + im, buf.getvalue(), compress_type=zipfile.ZIP_STORED)
            else:
                z.write(im, 'OEBPS/' + im, compress_type=zipfile.ZIP_STORED)
        nav = ['<nav epub:type="toc" id="toc"><h1>Contents</h1><ol>']
        for name, title, body, kind in files[1:]:
            nav.append(f'<li><a href="{name}">{esc(title)}</a></li>')
        nav.append('</ol></nav><nav epub:type="landmarks" hidden=""><ol>' + ('' if kindle else '<li><a epub:type="cover" href="cover.xhtml">Cover</a></li>') +
                   f'<li><a epub:type="toc" href="nav.xhtml">Contents</a></li><li><a epub:type="bodymatter" href="{files[1][0]}">Start</a></li></ol></nav>')
        z.writestr('OEBPS/nav.xhtml', page('Contents', ''.join(nav)), compress_type=zipfile.ZIP_DEFLATED)
        man = ['<item id="css" href="style.css" media-type="text/css"/>', '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
               ]
        spine = ['<itemref idref="nav"/>']
        if not kindle:
            man.append('<item id="coverpage" href="cover.xhtml" media-type="application/xhtml+xml" properties="svg"/>')
            spine.insert(0, '<itemref idref="coverpage" linear="yes"/>')
        for i, (name, title, body, kind) in enumerate(files):
            man.append(f'<item id="p{i}" href="{name}" media-type="application/xhtml+xml"/>')
            spine.insert(-1 if i == 0 else len(spine), f'<itemref idref="p{i}"/>')
        for k, f in enumerate(fonts_added):
            man.append(f'<item id="f{k}" href="fonts/{f}" media-type="font/ttf"/>')
        for k, im in enumerate(sorted(imgs)):
            props = ' properties="cover-image"' if im == 'img/cover-en.jpg' else ''
            mt = 'image/svg+xml' if im.endswith('.svg') else 'image/png' if im.endswith('.png') else 'image/jpeg'
            man.append(f'<item id="i{k}" href="{im}" media-type="{mt}"{props}/>')
        now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        opf = ('<?xml version="1.0" encoding="utf-8"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bid" xml:lang="en-US">'
               '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
               f'<dc:identifier id="bid">{bid}</dc:identifier><dc:title>Van Gogh in Pencil</dc:title><dc:creator>Pedro Torres</dc:creator>'
               '<dc:language>en-US</dc:language><dc:subject>Drawing</dc:subject>'
               f'<dc:description>A drawing course in the language of Vincent van Gogh: hatchings, flow, faces and self-portraits, with {NEX} exercises in four levels.</dc:description>'
               f'<meta property="dcterms:modified">{now}</meta>'
               '<meta property="schema:accessMode">textual</meta><meta property="schema:accessMode">visual</meta>'
               '<meta property="schema:accessModeSufficient">textual,visual</meta>'
               '<meta property="schema:accessibilityFeature">alternativeText</meta><meta property="schema:accessibilityFeature">structuralNavigation</meta>'
               '<meta property="schema:accessibilityFeature">tableOfContents</meta><meta property="schema:accessibilityFeature">readingOrder</meta>'
               '<meta property="schema:accessibilityFeature">displayTransformability</meta>'
               '<meta property="schema:accessibilityHazard">none</meta>'
               '<meta property="schema:accessibilitySummary">Reflowable book with a navigable table of contents, ordered headings and alternative text for the works and drawings. The lessons depend on seeing the images: the text describes each work, but the exercises ask the reader to look at the drawing.</meta>'
               f'<meta name="cover" content="i{sorted(imgs).index("img/cover-en.jpg")}"/></metadata>'
               f'<manifest>{"".join(man)}</manifest><spine>{"".join(spine)}</spine></package>')
        z.writestr('OEBPS/content.opf', opf, compress_type=zipfile.ZIP_DEFLATED)

COVER_EBOOK = """<!doctype html><html><head><meta charset="utf-8"><style>{fonts}
@page{{size:6in 9.6in;margin:0}}*{{margin:0;padding:0}}
.c{{position:relative;width:6in;height:9.6in;background:#2A2119;color:#FBF8F1;overflow:hidden}}
.art{{position:absolute;inset:0;background:url("img/cover-roulin.jpg") 38% 0/126% auto no-repeat}}
.topsh{{position:absolute;left:0;right:0;top:0;height:1.2in;background:linear-gradient(to bottom,rgba(20,15,10,.35),rgba(20,15,10,0))}}
.shade{{position:absolute;left:0;right:0;bottom:0;height:5.4in;background:linear-gradient(to bottom,rgba(20,15,10,0),rgba(20,15,10,.55) 45%,rgba(20,15,10,.7))}}
.ed{{position:absolute;top:.42in;left:0;right:0;text-align:center;font:500 11.5pt LivroSans;letter-spacing:.2em}}
.t{{position:absolute;left:0;right:0;top:6.05in;text-align:center;font:400 51pt/1 LivroSerif;letter-spacing:-.012em;white-space:nowrap}}
.d{{position:absolute;left:0;right:0;top:6.9in;text-align:center;font:italic 400 16pt LivroSerif}}
.coll{{position:absolute;bottom:.5in;left:0;right:0;text-align:center;font:italic 400 11.5pt LivroSerif}}
</style></head><body><div class="c"><div class="art"></div><div class="topsh"></div><div class="shade"></div>
<div class="ed">PEDRO TORRES</div><div class="t">Van Gogh in Pencil</div><div class="d">Theory and Practice for Drawing Like Vincent</div>
<div class="coll">{nex} exercises in four levels</div></div></body></html>"""

def make_cover():
    """Capa do e-book em 1600 × 2560 px (proporção pedida pela Amazon)."""
    import subprocess, tempfile
    from weasyprint import HTML
    from PIL import Image
    with tempfile.TemporaryDirectory() as td:
        HTML(string=COVER_EBOOK.format(fonts=font_faces(), nex=NEX), base_url=ROOT).write_pdf(f'{td}/c.pdf')
        subprocess.run(['pdftoppm', '-r', '266.67', '-png', '-singlefile', f'{td}/c.pdf', f'{td}/c'], check=True)
        im = Image.open(f'{td}/c.png').convert('RGB').resize((1600, 2560), Image.LANCZOS)
    im.save('img/cover-en.jpg', quality=92)
    im.save('out/capa-ebook-1600x2560.jpg', quality=92)

if __name__ == '__main__':
    import sys
    S = build_sections()
    S += [catalogue(), CREDITS]
    os.makedirs('out', exist_ok=True)
    args = sys.argv[1:] or ['cover', 'pdf']  # EPUB só com: python3 build.py epub
    make_details(); make_tracos()
    import subprocess; subprocess.run(['python3', 'tools/flow.py', 'roulin', 'starry'], check=True)
    if 'cover' in args:
        make_cover(); print('capa ok')
    if 'pdf' in args:
        open('out/livro.html', 'w').write(pdf_html(S))
        from weasyprint import HTML
        doc = HTML('out/livro.html', base_url=ROOT).render()
        print('páginas', len(doc.pages))
        doc.write_pdf('out/Van-Gogh-in-Pencil.pdf')
    if 'impresso' in args:  # KDP Paperback: miolo com sangria e capa inteira (papel creme, miolo preto e branco)
        import tempfile
        from weasyprint import HTML
        subprocess.run(['python3', 'tools/flow.py', '--impresso', 'roulin', 'starry'], check=True)
        open('out/livro-impresso.html', 'w').write(print_html(S))
        doc = HTML('out/livro-impresso.html', base_url=ROOT).render()
        if len(doc.pages) % 2:  # número par de páginas: a KDP acrescentaria uma branca no fim e a lombada sairia diferente
            h = open('out/livro-impresso.html').read().replace('</body>', '<div class="titlepage"></div></body>')
            open('out/livro-impresso.html', 'w').write(h)
            doc = HTML('out/livro-impresso.html', base_url=ROOT).render()
        with tempfile.TemporaryDirectory() as td:
            doc.write_pdf(f'{td}/m.pdf')
            corta_lombada(f'{td}/m.pdf', 'out/Van-Gogh-in-Pencil-miolo-impresso.pdf')
        W, H, lomb = make_print_cover(len(doc.pages), 'creme')
        print('impresso: páginas', len(doc.pages), f'· capa {W:.3f} × {H:.3f} pol. · lombada {lomb:.3f} pol.')
    if 'epub' in args:
        epub_assets()
        build_epub(S, 'out/Van-Gogh-in-Pencil.epub')
        build_epub(S, 'out/Van-Gogh-in-Pencil-loja-Amazon.epub', small=1000, kindle=True)
        print('epub ok')
