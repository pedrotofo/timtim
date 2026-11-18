#!/usr/bin/env python3
"""Os 50 Maiores Pintores (Pedro Torres): monta as páginas de cada pintor a partir de artistas/NN-chave.json.

python3 build.py                 -> out/Os-50-Maiores-Pintores.pdf com todos os pintores que já têm ficha
python3 build.py amostra 19      -> out/amostra-19.pdf e as prévias em duas páginas (out/amostra-19-spread-*.png)

Cada pintor ocupa 4 páginas, sempre começando numa página da esquerda:
1 abertura (número, obra-símbolo, retrato, ficha, por que está no ranking) · 2 a vida e a linha do tempo
3 obra em foco com marcas numeradas · 4 técnica, principais obras, você sabia, para pensar."""
import glob, html, json, os, re, subprocess, sys
from PIL import Image

def aspas(t):
    return re.sub(r'"([^"]*)"', '“\\1”', t)

ROOT = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(ROOT, 'fonts')
esc = lambda t: html.escape(aspas(str(t)), quote=False)

def font_faces():
    css = ''
    for f in sorted(os.listdir(FONTS)):
        m = re.match(r'eb-garamond-latin(-ext)?-(\d+)-(normal|italic)\.ttf$', f)
        if m: css += f'@font-face{{font-family:"LivroSerif{"X" if m.group(1) else ""}";src:url("file://{FONTS}/{f}");font-weight:{m.group(2)};font-style:{m.group(3)}}}\n'
        m = re.match(r'archivo-(black-)?latin(-ext)?-(\d+)-(normal|italic)\.woff$', f)
        if m: css += f'@font-face{{font-family:"{"LivroDisp" if m.group(1) else "LivroSans"}{"X" if m.group(2) else ""}";src:url("file://{FONTS}/{f}");font-weight:{m.group(3)};font-style:{m.group(4)}}}\n'
    return css

def img(rel, larg=1800):
    """Copia a obra de obras/ para img/ no tamanho de uso (o PDF não precisa do original)."""
    src = os.path.join(ROOT, 'obras', rel); dst = os.path.join(ROOT, 'img', rel)
    if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        im = Image.open(src).convert('RGB'); im.thumbnail((larg, larg), Image.LANCZOS); im.save(dst, quality=90)
    return 'file://' + dst

PESQ = os.path.join(ROOT, 'pesquisa')
RANK = {k: dict(v, pos_nota=i) for i, (k, v) in enumerate(json.load(open(os.path.join(PESQ, 'ranking.json'))), 1)}
EXTRA = json.load(open(os.path.join(PESQ, 'extra.json')))
LISTA = {x['pos']: x for x in json.load(open(os.path.join(PESQ, 'lista-final.json')))}
_wk = sorted([v['wikis'] for v in RANK.values()], reverse=True)

def ranking(a):
    """Números do quadro 'Por que está no ranking', tirados da pesquisa (pesquisa/ranking.md)."""
    ref = LISTA[a['pos']]['chave']; v = RANK.get(ref) or EXTRA.get(ref) or {}
    w = v.get('wikis') or LISTA[a['pos']].get('wikis') or 0
    return {'wikis': w, 'wikis_pos': 1 + sum(x > w for x in _wk), 'influencia': v.get('influenciou'), 'nota': v.get('nota'),
            'mundo': LISTA[a['pos']]['grupo'] == 'volta ao mundo', 'regiao': LISTA[a['pos']].get('regiao', '')}

def regiao_com(reg):
    """'Coreia' -> 'na Coreia', 'Japão' -> 'no Japão'."""
    r = reg.split(' (')[0]
    masc = ('Japão', 'Brasil', 'Império Otomano', 'Sudeste Asiático', 'México')
    return ('no ' if r in masc else 'na ') + r

def cor_ok(c):
    """Escurece a cor do pintor até o texto branco ficar legível (contraste 4,5:1)."""
    def lum(rgb):
        f = lambda x: x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4
        r, g, b = (f(x / 255) for x in rgb); return .2126 * r + .7152 * g + .0722 * b
    rgb = [int(c[i:i + 2], 16) for i in (1, 3, 5)]
    while 1.05 / (lum(rgb) + .05) < 4.5: rgb = [int(x * .92) for x in rgb]
    return '#%02X%02X%02X' % tuple(rgb)

def razao(rel):
    w, h = Image.open(os.path.join(ROOT, 'obras', rel)).size
    return h / w

CSS = """
@page{size:8.5in 11in;margin:0}
html{hyphens:auto;hyphenate-character:"-"}
body{margin:0;font-family:LivroSerif;color:#1E1913}
.pg{width:8.5in;height:11in;position:relative;box-sizing:border-box;break-after:page;overflow:hidden;background:#FBF8F2}
.esq{padding:.6in .8in .8in .6in}.dir{padding:.6in .6in .8in .8in}
.folio{position:absolute;bottom:.38in;font:700 7.5pt LivroSans;letter-spacing:.08em;text-transform:uppercase;color:#7A6F60}
.esq .folio{left:.6in}.dir .folio{right:.6in;text-align:right}
.folio b{display:inline-block;min-width:.32in;padding:.03in .06in;margin:0 .08in;background:var(--c);color:#fff;text-align:center;border-radius:.04in}
.chip{display:inline-block;font:700 7.6pt LivroSans;letter-spacing:.14em;text-transform:uppercase;color:#fff;background:var(--c);padding:.05in .12in;border-radius:.2in}
h2{font:400 25pt/1.02 LivroDisp;margin:.1in 0 .14in;color:#1E1913}
p{margin:0}
/* 1 abertura */
.ab{padding:0}
.ab .heroi{height:4.55in;background-size:cover;background-position:center 40%;position:relative}
.ab .heroi:after{content:"";position:absolute;left:0;right:0;bottom:0;height:2.2in;background:linear-gradient(rgba(0,0,0,0),rgba(0,0,0,.55))}
.ab .num{position:absolute;left:.55in;bottom:.18in;z-index:2;font:400 150pt/0.8 LivroDisp;color:#fff;letter-spacing:-.04em}
.ab .num small{display:block;font:700 9pt LivroSans;letter-spacing:.24em;margin:0 0 .12in .06in}
.ab .serie{position:absolute;top:.38in;right:.6in;z-index:2;font:700 7.6pt LivroSans;letter-spacing:.2em;text-transform:uppercase;color:#fff;background:rgba(0,0,0,.55);padding:.05in .12in;border-radius:.2in}
.ab .hcap{position:absolute;left:.6in;top:4.62in;width:4.2in;font:400 6.8pt/1.3 LivroSans;color:#7A6F60}
.ab .ret{position:absolute;right:.75in;top:3.55in;z-index:3;width:1.85in;height:1.85in;border-radius:50%;border:.07in solid #FBF8F2;background-size:cover;background-position:center 20%;box-shadow:0 .03in .1in rgba(0,0,0,.25)}
.ab .corpo{padding:.42in .8in 0 .6in}
.ab h1{font:400 33pt/1 LivroDisp;margin:0;width:4.6in}
.ab .orig{font:400 15pt LivroSerif;color:var(--c);margin:.05in 0 0}
.ab .dt{font:700 9pt LivroSans;letter-spacing:.12em;text-transform:uppercase;color:#7A6F60;margin:.08in 0 0}
.ab .frase{font:italic 400 15.5pt/1.3 LivroSerif;margin:.24in 0 .26in;padding-left:.18in;border-left:.05in solid var(--c);width:6.6in}
.ab .retcap{position:absolute;right:.6in;top:5.64in;width:2.15in;text-align:center;font:400 6.6pt/1.3 LivroSans;color:#7A6F60}
.duas{display:flex;gap:.3in}
.ficha{flex:1.05;border-collapse:collapse;font:400 8.6pt/1.3 LivroSans}
.ficha td{padding:.055in 0;border-bottom:.6pt solid #DDD3C2;vertical-align:top}
.ficha td.k{width:.85in;font-weight:700;font-size:7pt;letter-spacing:.1em;text-transform:uppercase;color:var(--c);padding-top:.07in}
.porque{flex:.95;background:#EFE8DA;border-radius:.1in;padding:.16in .18in}
.porque h4{font:700 7.6pt LivroSans;letter-spacing:.14em;text-transform:uppercase;margin:0 0 .1in;color:var(--c)}
.barra{margin:0 0 .12in;font:400 7.6pt/1.3 LivroSans}
.barra .t{height:.09in;background:#DDD3C2;border-radius:.05in;margin:.04in 0 .03in}
.barra .t i{display:block;height:100%;background:var(--c);border-radius:.05in}
.barra b{font-weight:700}
.porque .nota{font:400 30pt/1 LivroDisp;color:var(--c)}
.porque .nota span{font:700 7.4pt LivroSans;color:#7A6F60;letter-spacing:.06em}
/* 2 a vida */
.vida .cols{column-count:2;column-gap:.3in;font:400 10.2pt/1.4 LivroSerif;text-align:justify;height:6.05in}
.vida h3{font:700 8.4pt LivroSans;letter-spacing:.08em;text-transform:uppercase;color:var(--c);margin:.13in 0 .04in;break-after:avoid}
.vida h3:first-child{margin-top:0}
.cit{break-inside:avoid;background:var(--c);color:#fff;border-radius:.1in;padding:.16in .18in;margin:.16in 0 .05in;font:italic 400 11pt/1.35 LivroSerif;text-align:left}
.cit small{display:block;margin-top:.08in;font:400 6.8pt/1.3 LivroSans;font-style:normal;opacity:.85}
.vfig{margin:.1in 0 .02in;break-inside:avoid;text-align:center}.vfig img{max-width:100%;max-height:1.95in;display:inline-block;box-shadow:0 .02in .06in rgba(0,0,0,.15)}
.vfig figcaption{font:400 6.8pt/1.3 LivroSans;color:#7A6F60;margin-top:.04in;text-align:left}
.linha{position:absolute;left:.8in;right:.6in;bottom:.85in;height:2.2in}
.linha h4{font:700 7.6pt LivroSans;letter-spacing:.14em;text-transform:uppercase;margin:0;color:#7A6F60}
.linha h4 .pt{display:inline-block;width:.09in;height:.09in;border-radius:50%;margin:0 .06in -.005in 0;box-sizing:border-box}
.linha h4 .pt.v{background:var(--c)}.linha h4 .pt.m{border:1.2pt solid #6E6253;margin-left:.22in}
.linha .eixo{position:absolute;left:0;right:0;top:1.17in;height:.05in;background:#1E1913;border-radius:.03in}
.ev{position:absolute;width:.66in;font:400 6.9pt/1.22 LivroSans}
.ev b{display:block;font:400 10pt LivroDisp}
.ev.v{bottom:1.08in;color:#1E1913}.ev.v b{color:var(--c)}
.ev.m{top:1.3in;color:#6E6253}
.ev:before{content:"";position:absolute;left:0;width:.11in;height:.11in;border-radius:50%}
.ev.v:before{bottom:-.13in;background:var(--c)}
.ev.m:before{top:-.17in;background:#fff;border:1.2pt solid #6E6253;box-sizing:border-box}
/* 3 obra em foco */
.foco .dados{font:400 7.8pt LivroSans;color:#7A6F60;margin:.0in 0 .1in}
.foco .intro{font:400 10.6pt/1.4 LivroSerif;margin:0 0 .16in;width:6.4in}
.quadro{position:relative;margin:0 0 .16in}
.quadro img{width:100%;display:block;box-shadow:0 .02in .08in rgba(0,0,0,.18)}
.mk{position:absolute;width:.3in;height:.3in;margin:-.15in 0 0 -.15in;border-radius:50%;background:var(--c);border:.03in solid #fff;color:#fff;font:400 10pt/.25in LivroDisp;text-align:center;box-shadow:0 .01in .05in rgba(0,0,0,.4)}
.leg{display:flex;flex-wrap:wrap;gap:.1in .3in;margin:0 0 .18in}
.leg div{width:3.4in;display:flex;gap:.1in;font:400 8.6pt/1.32 LivroSans}
.leg i{flex:none;width:.24in;height:.24in;border-radius:50%;background:var(--c);color:#fff;font:400 8.5pt/.24in LivroDisp;text-align:center;font-style:normal}
.leg b{display:block;font-weight:700}
.vert{display:flex;gap:.28in;align-items:flex-start}
.vert .quadro{flex:none;margin:0}
.vert .quadro img{width:100%;height:auto}
.vert .lado{flex:1}
.vert .leg{flex-direction:column;gap:.14in}
.vert .leg div{width:auto}
.sabia{background:#F6D86B;border-radius:.1in;padding:.15in .2in .14in;position:relative}
.sabia h4{font:400 13pt LivroDisp;margin:0 0 .06in}
.sabia ul{margin:0;padding-left:.16in;font:400 8.8pt/1.38 LivroSans}
.sabia li{margin:0 0 .04in}
/* 4 técnica e obras */
.tec .intro{font:400 10.2pt/1.4 LivroSerif;margin:0 0 .14in}
.passos{display:flex;gap:.14in;margin:0 0 .16in}
.passo{flex:1;border-top:.05in solid var(--c);padding-top:.08in;font:400 7.9pt/1.32 LivroSans}
.passo i{display:inline-block;width:.24in;height:.24in;border-radius:50%;background:var(--c);color:#fff;font:400 9pt/.24in LivroDisp;text-align:center;font-style:normal;margin-bottom:.05in}
.passo b{display:block;font-weight:700;font-size:8.6pt;margin-bottom:.02in}
.azul{display:flex;gap:.2in;align-items:center;background:#EFE8DA;border-radius:.1in;padding:.13in .18in;margin:0 0 .22in}
.azul .tx{flex:1;font:400 8.3pt/1.36 LivroSans}.azul .tx b{display:block;font:400 11pt LivroDisp;margin-bottom:.03in}
.pal{display:flex;gap:.06in}
.pal span{display:block;width:.46in;font:400 5.8pt/1.15 LivroSans;text-align:center;color:#6E6253}
.pal span i{display:block;height:.46in;border-radius:.06in;margin-bottom:.03in;border:.5pt solid rgba(0,0,0,.12)}
.obras{display:flex;gap:.2in;align-items:flex-start;margin:.12in 0 .2in}
.obra{flex:1;font:400 7.6pt/1.3 LivroSans}
.obra .th{height:1.62in;display:flex;align-items:flex-end;justify-content:flex-start;margin-bottom:.06in}
.obra .th img{max-width:100%;max-height:1.62in;display:block;box-shadow:0 .02in .06in rgba(0,0,0,.15)}
.obra b{display:block;font-size:8pt}
.obra em{font-style:normal;color:#7A6F60}
.fim{display:flex;gap:.18in}
.cx{flex:1;border-radius:.1in;padding:.13in .16in;font:400 8.2pt/1.36 LivroSans}
.cx h4{font:700 7.4pt LivroSans;letter-spacing:.14em;text-transform:uppercase;margin:0 0 .07in}
.cx.inf{border:1.2pt solid var(--c)}.cx.inf h4{color:var(--c)}
.cx.inf p{margin:0 0 .05in}.cx.inf b.n{display:inline-block;min-width:.26in;padding:0 .04in;margin-right:.05in;background:var(--c);color:#fff;border-radius:.03in;text-align:center;font:400 7.6pt/1.5 LivroDisp}
.cx.pen{background:#CFE3DA}.cx.pen h4{color:#2E5E4E}
.cx.pal2{background:#EFE8DA}.cx.pal2 p{margin:0 0 .05in}.cx.pal2 b{font-weight:700}
"""

def familias(css):
    """Cada família ganha a versão latin-ext como reserva (macron do japonês: ō, ū)."""
    return re.sub(r'\b(LivroSerif|LivroSans|LivroDisp)\b(?!X)', r'\1,\1X', css)

def aspas(t):
    """Aspas retas viram curvas."""
    return re.sub(r'"([^"]*)"', '“\\1”', t)

def pagina(lado, cls, corpo, folio, cor, id_=''):
    ident = f' id="{id_}"' if id_ else ''
    return f'<section class="pg {lado} {cls}"{ident} style="--c:{cor}">{corpo}<div class="folio">{folio}</div></section>'

def folio_txt(a, n, lado):
    num = f'<b>{n}</b>'
    nome = f'Nº {a["pos"]} · {esc(a["nome"])}'
    return f'{num}{nome}' if lado == 'esq' else f'{nome}{num}'

def foco_corpo(f, mks, leg, sabia):
    """Obra horizontal: imagem na largura toda. Obra vertical (altura maior que 0,85 da largura): imagem à esquerda."""
    s = f'<div class="sabia"><h4>Você sabia?</h4><ul>{sabia}</ul></div>'
    r = razao(f['img'])
    if r > .85:
        # caixa do tamanho exato da imagem (sem distorcer, marcas em % no lugar): até 6,55 pol. de altura e 4,3 de largura
        h = min(6.55, 4.3 * r); w = h / r
        q = f'<div class="quadro" style="width:{w:.3f}in"><img src="{img(f["img"], 2400)}" alt="{esc(f["titulo"])}"/>{mks}</div>'
        return f'<div class="vert">{q}<div class="lado"><div class="leg">{leg}</div>{s}</div></div>'
    q = f'<div class="quadro"><img src="{img(f["img"], 2400)}" alt="{esc(f["titulo"])}"/>{mks}</div>'
    return f'{q}<div class="leg">{leg}</div>{s}'

def retrato(a):
    rt = a.get('retrato')
    if not rt: return ''
    return (f'<div class="ret" style="background-image:url(\'{img(rt["img"], 900)}\');background-position:{rt.get("pos", "center 20%")}"></div>'
            f'<div class="retcap">{esc(rt["legenda"])}</div>')

def artista(a, p0):
    c = cor_ok(a['cor']); P = []
    # 1 abertura
    r = ranking(a)
    barras = f'<div class="barra">Alcance mundial: artigo em <b>{r["wikis"]} idiomas</b> da Wikipédia<div class="t"><i style="width:{min(100, r["wikis"] / 244 * 100):.0f}%"></i></div></div>'
    if r['mundo']:
        barras += (f'<div class="barra">Vaga da <b>volta ao mundo</b>: o pintor de obra livre com mais alcance {regiao_com(r["regiao"])}.</div>'
                   f'<div class="barra">A conta completa está no fim do livro, em “Como fizemos o ranking”.</div>')
    else:
        barras += (f'<div class="barra">Influência: <b>{r["influencia"]} artistas e movimentos</b> registrados como influenciados {esc(a.get("pron", "por ele"))}<div class="t"><i style="width:{min(100, (r["influencia"] or 0) / 59 * 100):.0f}%"></i></div></div>'
                   f'<div class="barra">Nota final: <b>{r["nota"]:.0f} de 100</b>, somando alcance, influência e mídia especializada<div class="t"><i style="width:{r["nota"]:.0f}%"></i></div></div>')
    ficha = ''.join(f'<tr><td class="k">{esc(k)}</td><td>{esc(v)}</td></tr>' for k, v in a['ficha'])
    P.append(pagina('esq', 'ab', f'''
      <div class="heroi" style="background-image:url('{img(a["abertura"]["img"])}');background-position:{a["abertura"].get("pos", "center 40%")}">
        <div class="serie">Os 50 maiores pintores</div>
        <div class="num"><small>NÚMERO</small>{a["pos"]}</div>
      </div>
      <div class="hcap">Na imagem: {esc(a["abertura"]["legenda"])}</div>
      {retrato(a)}
      <div class="corpo">
        <h1>{esc(a["nome"])}</h1><p class="orig">{esc(a.get("nome_original", ""))}</p>
        <p class="dt">{esc(a["vida"])} · {esc(a["origem"])}</p>
        <p class="frase">{esc(a["frase"])}</p>
        <div class="duas"><table class="ficha">{ficha}</table>
          <div class="porque"><h4>Por que está no ranking</h4>{barras}
</div></div>
      </div>''', folio_txt(a, p0, 'esq'), c, f'p{a["pos"]}'))
    # 2 a vida
    fig = a.get('vida_fig')
    figura = f'<figure class="vfig"><img src="{img(fig["img"], 1000)}" alt="{esc(fig["legenda"])}"/><figcaption>{esc(fig["legenda"])}</figcaption></figure>' if fig else ''
    blocos = ''.join(f'<h3>{esc(b["t"])}</h3><p>{esc(b["p"])}</p>' + (f'<div class="cit">“{esc(a["citacao"]["texto"])}”<small>{esc(a["citacao"]["fonte"])}</small></div>' if i == 1 and a.get("citacao") else '') + (figura if i == 2 else '')
                     for i, b in enumerate(a['vida_txt']))
    n = len(a['linha']); evs = ''
    for i, (ano, t, tipo) in enumerate(a['linha']):
        x = i / (n - 1) * 100
        evs += f'<div class="ev {"v" if tipo == "vida" else "m"}" style="left:calc({x:.2f}% - {x / 100 * .66:.3f}in)"><b>{ano}</b>{esc(t)}</div>'
    P.append(pagina('dir', 'vida', f'''<span class="chip">A vida</span><h2>{esc(a.get("vida_titulo") or a["vida_txt"][-1]["t"])}</h2>
      <div class="cols">{blocos}</div>
      <div class="linha"><h4><span class="pt v"></span>{"A vida dela" if a.get("pron") == "por ela" else "A vida dele"}<span class="pt m"></span>O mundo naquele tempo</h4><div class="eixo"></div>{evs}</div>''', folio_txt(a, p0 + 1, 'dir'), c))
    # 3 obra em foco
    f = a['foco']
    mks = ''.join(f'<div class="mk" style="left:{x}%;top:{y}%">{i}</div>' for i, (x, y, t, d) in enumerate(f['marcas'], 1))
    leg = ''.join(f'<div><i>{i}</i><span><b>{esc(t)}</b>{esc(d)}</span></div>' for i, (x, y, t, d) in enumerate(f['marcas'], 1))
    sabia = ''.join(f'<li>{esc(s)}</li>' for s in a['sabia'])
    P.append(pagina('esq', 'foco', f'''<span class="chip">Obra em foco</span><h2>{esc(f["titulo"])}</h2>
      <p class="dados">{esc(f["dados"])}</p><p class="intro">{esc(f["intro"])}</p>
      {foco_corpo(f, mks, leg, sabia)}''', folio_txt(a, p0 + 2, 'esq'), c))
    # 4 técnica e obras
    t = a['tecnica']
    passos = ''.join(f'<div class="passo"><i>{i}</i><b>{esc(k)}</b>{esc(v)}</div>' for i, (k, v) in enumerate(t['passos'], 1))
    pal = ''.join(f'<span><i style="background:{h}"></i>{esc(nm)}</span>' for h, nm in t['paleta'])
    obras = ''.join(f'<div class="obra"><div class="th"><img src="{img(o["img"], 1000)}" alt="{esc(o["titulo"])}"/></div><b>{esc(o["titulo"])}</b><em>{esc(o["ano"])}</em> · {esc(o["nota"])}</div>'
                    for o in a['obras'] if o['img'] != a['abertura']['img'])
    inf = ''.join(f'<p><b class="n">{num}</b>{esc(nm)}</p>' if num else f'<p><b class="n">·</b>{esc(nm)}</p>' for nm, num in a['influenciou'])
    rv = a.get('rival')
    if rv: inf += f'<p style="margin-top:.07in"><b class="n">{rv[1]}</b><b>{esc(rv[0])}</b>: {esc(rv[2])}</p>'
    pal2 = ''.join(f'<p><b>{esc(k)}</b>: {esc(v)}</p>' for k, v in a['palavras'])
    P.append(pagina('dir', 'tec', f'''<span class="chip">{"Como ela trabalhava" if a.get("pron") == "por ela" else "Como ele trabalhava"}</span><h2>{esc(t["titulo"])}</h2>
      <p class="intro">{esc(t["intro"])}</p><div class="passos">{passos}</div>
      <div class="azul"><div class="tx"><b>{esc(t["box_t"])}</b>{esc(t["box"])}</div><div class="pal">{pal}</div></div>
      <span class="chip">Principais obras</span><div class="obras">{obras}</div>
      <div class="fim"><div class="cx inf"><h4>Influenciou · veja no livro</h4>{inf}</div>
        <div class="cx pen"><h4>Para pensar e fazer</h4>{esc(a["pensar"])}</div>
        <div class="cx pal2"><h4>Palavras-chave</h4>{pal2}</div></div>''', folio_txt(a, p0 + 3, 'dir'), c))
    return ''.join(P)

def documento(artistas, p0=2):
    corpo = ''.join(artista(a, p0 + 4 * i) for i, a in enumerate(artistas))
    return f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Os 50 Maiores Pintores</title><style>{font_faces()}{familias(CSS)}</style></head><body>{corpo}</body></html>'

def livro(arts):
    """O livro inteiro: frente (11 páginas), os 50 a partir da página 12, consulta e contracapa."""
    import extras
    n = [1]   # a página 1 é a capa
    def fixa(lado, cls, corpo, rotulo, cor=extras.COR):
        n[0] += 1
        fol = '' if not rotulo else (f'<b>{n[0]}</b>{rotulo}' if lado == 'esq' else f'{rotulo}<b>{n[0]}</b>')
        return pagina(lado, cls, corpo, fol, cor)
    frente = extras.frente(arts, img, esc, fixa, ranking)
    assert n[0] == extras.FRENTE, n[0]
    corpo = ''.join(artista(a, extras.FRENTE + 1 + 4 * i) for i, a in enumerate(arts))
    n[0] = extras.FRENTE + 4 * len(arts)
    fundo = extras.fundo(arts, esc, fixa, ranking, ROOT) + extras.contracapa(arts, esc)
    css = font_faces() + familias(CSS + extras.CSS)
    return (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Os 50 Maiores Pintores</title>'
            f'<meta name="author" content="Pedro Torres"><style>{css}</style></head><body>{frente}{corpo}{fundo}</body></html>')

def carrega(filtro=None):
    fs = sorted(glob.glob(os.path.join(ROOT, 'artistas', '*.json')), key=lambda f: -int(os.path.basename(f).split('-')[0]))
    out = []
    for f in fs:
        if filtro and not os.path.basename(f).startswith(f'{int(filtro):02d}-'): continue
        try:
            a = json.load(open(f))
            falta = [k for k in ('pos', 'nome', 'abertura', 'ficha', 'vida_txt', 'linha', 'foco', 'tecnica', 'obras') if k not in a]
            if falta: raise ValueError('faltam ' + ', '.join(falta))
            refs = re.findall(r'"img": "([^"]+)"', json.dumps(a, ensure_ascii=False))
            sem = [r for r in refs if not os.path.exists(os.path.join(ROOT, 'obras', r))]
            if sem: raise ValueError('imagens ainda não baixadas: ' + ', '.join(sem[:3]))
            out.append(a)
        except Exception as e:
            print(f'AVISO: {os.path.basename(f)} ficou de fora ({e})', file=sys.stderr)
    return out

def verifica(doc, artistas, p0=2):
    """Acusa texto que passa da página: linha abaixo do limite do rodapé ou coluna que escapou para a direita."""
    from weasyprint.formatting_structure import boxes as B
    PX = 96; LIM_Y = (11 - .62) * PX; LIM_X = (8.5 - .35) * PX
    erros = []
    def anda(b, fol=False):
        cls = (b.element.get('class') or '') if getattr(b, 'element', None) is not None else ''
        fol = fol or 'folio' in cls.split()
        yield b, fol
        for c in getattr(b, 'children', []) or []:
            yield from anda(c, fol)
    for i, pg in enumerate(doc.pages):
        k, r = divmod(i, 4); a = artistas[k] if k < len(artistas) else None
        if not a: continue
        for b, fol in anda(pg._page_box):
            if fol or not isinstance(b, B.LineBox): continue
            txt = ''.join(getattr(t, 'text', '') for t, _ in anda(b) if isinstance(t, B.TextBox)).strip()
            if not txt: continue
            if b.position_y + b.height > LIM_Y or b.position_x + b.width > LIM_X + 2:
                erros.append(f'nº {a["pos"]} {a["nome"]}, página {r + 1}: texto fora da página: "{txt[:60]}"')
    return erros

if __name__ == '__main__':
    from weasyprint import HTML
    os.makedirs(os.path.join(ROOT, 'out'), exist_ok=True)
    args = sys.argv[1:]
    if args[:1] == ['verifica']:
        arts = [x for n in (args[1:] or [None]) for x in carrega(n)]
        doc = HTML(string=documento(arts), base_url=ROOT).render()
        es = verifica(doc, arts)
        for e in es: print('ERRO', e)
        print('páginas', len(doc.pages), '·', 'sem estouro' if not es else f'{len(es)} linhas fora')
        sys.exit(1 if es else 0)
    if args[:1] == ['amostra']:
        n = args[1]; out = os.path.join(ROOT, 'out', f'amostra-{n}.pdf')
        HTML(string=documento(carrega(n)), base_url=ROOT).write_pdf(out)
        pre = os.path.join(ROOT, 'out', f'amostra-{n}')
        subprocess.run(['pdftoppm', '-r', '110', '-png', out, pre], check=True)
        pgs = sorted(glob.glob(pre + '-[0-9]*.png'))
        for k in range(0, len(pgs), 2):
            a, b = Image.open(pgs[k]), Image.open(pgs[k + 1]) if k + 1 < len(pgs) else None
            s = Image.new('RGB', (a.width * 2 + 40, a.height + 40), '#3A3A3A'); s.paste(a, (20, 20))
            if b: s.paste(b, (a.width + 20, 20))
            s.save(f'{pre}-spread-{k // 2 + 1}.png')
        for p_ in pgs: os.remove(p_)
        print('ok', out)
    else:
        arts = carrega()
        doc = HTML(string=livro(arts), base_url=ROOT).render()
        print('páginas', len(doc.pages))
        doc.write_pdf(os.path.join(ROOT, 'out', 'Os-50-Maiores-Pintores.pdf'))
        if 'previa' in args:
            subprocess.run(['pdftoppm', '-r', '40', '-png', os.path.join(ROOT, 'out', 'Os-50-Maiores-Pintores.pdf'), os.path.join(ROOT, 'out', 'prev')], check=True)
        print('ok')
