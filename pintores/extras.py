"""Partes do livro que não são de um pintor: capa, colofão, rosto, prefácio, como ler, sumário, os 50 num relance,
linha do tempo, como fizemos o ranking, glossário, créditos das imagens, índice e contracapa.

Usado só pelo build completo (python3 build.py). As páginas de pintor continuam em build.py."""
import datetime, json, os, re, unicodedata
from PIL import Image

COR = '#9E2B25'          # vermelho do livro: capa, prefácio, partes de consulta
FRENTE = 11              # páginas antes do nº 50 (o nº 50 começa na página 12, à esquerda)

CSS = """
.fr{--c:#9E2B25}
.capa{padding:0;background:#16110D;color:#fff}
.capa .mos{position:absolute;top:0;left:0;width:8.5in;height:11in}
.capa .mos div{position:absolute;width:1.7in;height:1.1in;background-size:cover;background-position:center}
.capa .veu{position:absolute;top:0;left:0;width:8.5in;height:11in;background:linear-gradient(180deg,rgba(22,17,13,.0) 0%,rgba(22,17,13,.0) 38%,rgba(22,17,13,.92) 58%,rgba(22,17,13,.97) 100%)}
.capa .tit{position:absolute;left:.7in;right:.7in;bottom:1.05in}
.capa .tit .n{font:400 150pt/.78 LivroDisp;color:#E9B44C;letter-spacing:-.05em;margin:0}
.capa .tit h1{font:400 44pt/.98 LivroDisp;margin:.08in 0 .18in;color:#fff}
.capa .tit p{font:italic 400 16pt/1.3 LivroSerif;color:#E8DFD0;margin:0;width:5.6in}
.capa .aut{position:absolute;right:.7in;bottom:.5in;font:700 10pt LivroSans;letter-spacing:.28em;color:#E9B44C}
.rosto{display:flex;flex-direction:column;justify-content:center;text-align:left}
.rosto .n{font:400 120pt/.8 LivroDisp;color:var(--c);margin:0}
.rosto h1{font:400 40pt/1 LivroDisp;margin:.1in 0 .2in}
.rosto p{font:italic 400 15pt/1.35 LivroSerif;width:5in}
.rosto .aut{font:700 10pt LivroSans;letter-spacing:.28em;margin-top:.6in;color:var(--c)}
.colo{font:400 8pt/1.5 LivroSans;color:#5A5045;display:flex;flex-direction:column;justify-content:flex-end}
.colo p{margin:0 0 .1in;width:5in}
.pref h2,.consulta h2{font:400 30pt/1 LivroDisp;margin:.08in 0 .2in}
.pref .tx{font:400 11pt/1.5 LivroSerif;text-align:justify}
.pref .tx p{margin:0 0 .12in}
.pref .tx p.ab:first-letter{font:400 46pt/.8 LivroDisp;float:left;margin:.04in .08in 0 0;color:var(--c)}
.fora{background:#EFE8DA;border-radius:.1in;padding:.18in .22in;margin:.1in 0 .18in;font:400 8.8pt/1.42 LivroSans}
.fora h4{font:400 13pt LivroDisp;margin:0 0 .08in;color:var(--c)}
.fora table{border-collapse:collapse;width:100%;margin:.08in 0}
.fora td{padding:.03in .06in .03in 0;border-bottom:.5pt solid #D9CFBE;vertical-align:top}
.fora td.a{font-weight:700;width:1.5in;color:var(--c)}
.nums{margin-top:.35in;border-top:1.5pt solid var(--c);padding-top:.14in}
.nums h4{font:700 7.6pt LivroSans;letter-spacing:.16em;text-transform:uppercase;color:var(--c);margin:0 0 .12in}
.nums .nl{display:flex;flex-wrap:wrap;gap:.18in 0}
.nums p{width:33.3%;margin:0;font:400 8.4pt/1.25 LivroSans;color:#5A5045}
.nums p b{display:block;font:400 30pt/1 LivroDisp;color:#1E1913;margin-bottom:.03in}
.assina{font:italic 400 13pt LivroSerif;text-align:right;margin-top:.15in}
.comoler .pn{display:flex;gap:.22in;margin:0 0 .22in;align-items:flex-start}
.comoler .mini{flex:none;width:1.45in;height:1.88in;border:1pt solid #CFC4B2;border-radius:.05in;background:#fff;position:relative;overflow:hidden}
.comoler .mini i{position:absolute;display:block;border-radius:.02in}
.comoler .tx{font:400 9.6pt/1.42 LivroSans}
.comoler .tx b{display:block;font:400 14pt LivroDisp;margin-bottom:.04in}
.comoler .tx em{font-style:normal;color:var(--c);font-weight:700}
.sum h2{margin-bottom:.12in}
.sum .cols{column-count:2;column-gap:.35in;font:400 8.6pt/1.3 LivroSans}
.sum .e{display:flex;align-items:baseline;gap:.06in;padding:.022in 0;border-bottom:.5pt dotted #CFC4B2;break-inside:avoid}
.sum .e b{font:400 9pt LivroDisp;width:.28in;color:var(--c)}
.sum .e span{flex:1}
.sum .e a{color:#7A6F60;text-decoration:none}
.sum .e a:after{content:target-counter(attr(href), page)}
.sum .grupo{font:700 7pt LivroSans;letter-spacing:.16em;text-transform:uppercase;color:#7A6F60;margin:.14in 0 .04in;break-after:avoid}
.relance h2{font:400 24pt/1 LivroDisp;margin:.05in 0 .14in}
.grade{display:flex;flex-wrap:wrap;gap:.1in}
.grade .g{width:1.32in;font:400 6.8pt/1.2 LivroSans}
.grade .g .q{height:1.32in;background-size:cover;background-position:center;border-radius:.05in;position:relative}
.grade .g .q b{position:absolute;left:.05in;bottom:.03in;font:400 22pt/1 LivroDisp;color:#fff;text-shadow:0 0 .06in rgba(0,0,0,.7)}
.grade .g span{display:block;margin-top:.04in;font-weight:700}
.grade .g em{font-style:normal;color:#7A6F60}
.tl h2{font:400 24pt/1 LivroDisp;margin:.05in 0 .06in}
.tl .sub{font:400 8.4pt/1.35 LivroSans;color:#5A5045;margin:0 0 .16in}
.tl .graf{position:relative;height:8.0in}
.tl .ano{position:absolute;top:0;bottom:0;border-left:.5pt solid #DDD3C2;font:700 6.4pt LivroSans;color:#9A8E7C}
.tl .ano span{position:absolute;top:-.14in;left:-.15in}
.tl .bar{position:absolute;height:.16in;border-radius:.08in}
.tl .lab{position:absolute;font:400 7pt/.16in LivroSans;white-space:nowrap}
.tl .lab b{font-family:LivroDisp;font-weight:400;color:var(--c);margin-right:.04in}
.tl .leg{font:400 7pt LivroSans;color:#5A5045;margin-top:.12in}
.tl .leg i{display:inline-block;width:.16in;height:.09in;border-radius:.05in;margin:0 .04in 0 .14in}
.consulta .tx{font:400 10pt/1.45 LivroSerif;text-align:justify}
.consulta .tx p{margin:0 0 .1in}
.tab{border-collapse:collapse;width:100%;font:400 7.6pt/1.25 LivroSans;margin-top:.1in}
.tab th{text-align:left;font-weight:700;font-size:6.6pt;letter-spacing:.08em;text-transform:uppercase;color:#7A6F60;border-bottom:1pt solid #1E1913;padding:.03in .04in}
.tab td{padding:.025in .04in;border-bottom:.5pt solid #E3DACB}
.tab td.n{font:400 8pt LivroDisp;color:var(--c)}
.flui{width:8.5in;box-sizing:border-box}
@page consulta{margin:.7in .65in .85in .75in;background:#FBF8F2;
  @bottom-center{content:counter(page);font:700 7.5pt LivroSans;color:#7A6F60}}
.flui{page:consulta}
.flui.glos,.flui.cred,.flui.ind{break-before:page}
.flui h2{font:400 28pt/1 LivroDisp;margin:0 0 .18in}
.glos .cols{column-count:2;column-gap:.35in;font:400 9pt/1.38 LivroSans}
.glos p{margin:0 0 .08in;break-inside:avoid}
.glos p b{font-weight:700}
.glos p em{font-style:normal;color:#9A8E7C;font-size:7.4pt}
.cred .cols{column-count:3;column-gap:.25in;font:400 6.4pt/1.32 LivroSans;color:#3E362D}
.cred p{margin:0 0 .05in;break-inside:avoid}
.cred h5{font:400 8.5pt LivroDisp;margin:.08in 0 .03in;break-after:avoid}
.cred .intro{font:400 8.6pt/1.4 LivroSans;margin:0 0 .16in;width:6.8in}
.ind .cols{column-count:3;column-gap:.3in;font:400 9pt/1.6 LivroSans}
.ind p{margin:0}
.ind b{font-family:LivroDisp;font-weight:400;color:#9E2B25}
.contra{break-before:left;background:#16110D;color:#E8DFD0;display:flex;flex-direction:column;justify-content:center;padding:1in}
.contra p{font:400 12pt/1.5 LivroSerif;margin:0 0 .16in;width:6in}
.contra .big{font:400 26pt/1.08 LivroDisp;color:#fff;margin-bottom:.3in}
.contra .nomes{font:400 8.4pt/1.6 LivroSans;color:#B8AC98;margin-top:.3in}
.branca{background:#FBF8F2}
"""

def _fold(s):
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()

def frente(arts, img, esc, pagina_fixa, ranking):
    """Páginas 1 a 11."""
    por_pos = {a['pos']: a for a in arts}
    H = []
    # 1 capa: mosaico das 50 aberturas, número grande
    ordem = list(range(1, 51))
    cel = ''
    for i, p in enumerate(ordem):
        a = por_pos.get(p)
        if not a: continue
        x, y = (i % 5) * 1.7, (i // 5) * 1.1
        cel += f'<div style="left:{x:.2f}in;top:{y:.2f}in;background-image:url(\'{img(a["abertura"]["img"], 700)}\');background-position:{a["abertura"].get("pos", "center")}"></div>'
    H.append(f'''<section class="pg capa fr"><div class="mos">{cel}</div><div class="veu"></div>
      <div class="tit"><p class="n">50</p><h1>Os 50 Maiores<br/>Pintores</h1>
      <p>História, técnica e obras dos mestres da pintura no mundo, em contagem regressiva</p></div>
      <div class="aut">PEDRO TORRES</div></section>''')
    ano = datetime.date.today().year
    H.append(pagina_fixa('esq', 'colo fr', f'''<p><b>Os 50 Maiores Pintores</b><br/>História, técnica e obras dos mestres da pintura no mundo</p>
      <p>© {ano} Pedro Torres. Todos os direitos reservados. Nenhuma parte deste livro pode ser reproduzida sem autorização do autor, exceto trechos curtos em resenhas.</p>
      <p>As obras reproduzidas estão em domínio público e vêm do Wikimedia Commons, em geral de fotografias feitas pelos próprios museus; a lista completa, imagem por imagem, está em "Créditos das imagens", no fim do livro.</p>
      <p>Ranking feito em novembro de 2026 a partir do Wikidata, da Wikipédia e da mídia especializada; o método está em "Como fizemos o ranking".</p>
      <p>Texto composto em EB Garamond e Archivo.</p>''', ''))
    H.append(pagina_fixa('dir', 'rosto fr', '''<p class="n">50</p><h1>Os 50 Maiores<br/>Pintores</h1>
      <p>História, técnica e obras dos mestres da pintura no mundo, em contagem regressiva</p><div class="aut">PEDRO TORRES</div>''', ''))
    # 4 e 5 prefácio
    H.append(pagina_fixa('esq', 'pref fr', f'''<span class="chip">Prefácio</span><h2>Antes de começar</h2><div class="tx">
      <p>Todo mundo já parou diante de um quadro famoso e se perguntou: por que este, e não outro? Este livro tenta responder a uma pergunta parecida, só que maior. Quem são os pintores mais importantes da história, e por quê?</p>
      <p>Em vez de dar a minha opinião, fui atrás de números. Medi em quantas línguas cada pintor tem artigo na Wikipédia, que é um bom retrato do quanto o mundo inteiro o conhece. Consultei o que dizem a mídia especializada e as grandes histórias da arte: as buscas no banco de preços da Artnet, o índice de Charles Murray, o projeto Pantheon, do MIT, os recordes de público dos museus. E contei quantos artistas cada um influenciou. Juntei tudo numa nota de 0 a 100. A conta inteira, com as fontes, está no fim do livro.</p>
      <p>Os números têm um defeito: enxergam melhor a Europa do que o resto do mundo. Se eu seguisse só a nota, quase todos os 50 seriam europeus. Por isso as dez primeiras vagas do livro são de uma volta ao mundo: o pintor de mais alcance de cada região, da Venezuela à Coreia, do Brasil à Pérsia.</p>
      <p>O livro conta de trás para frente, do 50º ao 1º, como uma parada de sucessos. Cada pintor tem quatro páginas: quem foi, como viveu, uma obra olhada de perto e o jeito como ele trabalhava. O número de cada um aparece sempre que outro pintor do livro o cita, para você ir e voltar.</p>
      </div><div class="fora"><h4>Quem ficou de fora, e por quê</h4>
      <p>Pela lei brasileira, a obra de um artista fica protegida por 70 anos depois da morte, contados a partir de 1º de janeiro do ano seguinte. Até lá, reproduzir os quadros depende de licença dos herdeiros. Decidi que este livro mostraria todas as obras de que fala, e por isso só entram pintores cuja obra já é livre. Pela nota, estes estariam entre os 50:</p>
      <table>
      <tr><td class="a">Pablo Picasso</td><td>seria o número 1 da conta; obra livre no Brasil em 2044</td></tr>
      <tr><td class="a">Andy Warhol</td><td>livre em 2058</td></tr>
      <tr><td class="a">Frida Kahlo</td><td>livre no Brasil desde 2025, mas protegida no México até 2054 e, na maior parte, nos Estados Unidos</td></tr>
      <tr><td class="a">Marc Chagall</td><td>livre em 2056</td></tr>
      <tr><td class="a">Salvador Dalí</td><td>livre em 2060</td></tr>
      <tr><td class="a">Joan Miró</td><td>livre em 2054</td></tr>
      <tr><td class="a">Jackson Pollock</td><td>livre no Brasil em 2027</td></tr>
      <tr><td class="a">René Magritte</td><td>livre em 2038</td></tr>
      <tr><td class="a">Diego Rivera</td><td>livre no Brasil em 2028; no México, só em 2058</td></tr>
      </table>
      <p>Nas vagas da volta ao mundo ficaram de fora, pelo mesmo motivo, Tarsila do Amaral (livre em 2044), o chinês Qi Baishi (2028), a sul-africana Irma Stern (2037) e o australiano Albert Namatjira (2030). Todos eles aparecem no livro quando um pintor daqui os influenciou.</p></div>
''', esc('Prefácio'), COR))
    paises = sorted({a['origem'].split('/')[0].strip() for a in arts})
    anos = [int(re.findall(r'\d{3,4}', a['vida'])[0]) for a in arts] + [int(re.findall(r'\d{3,4}', a['vida'])[-1]) for a in arts]
    nobras = sum(1 + len(a.get('obras', [])) + 1 for a in arts)
    nums = f'''<div class="nums"><h4>Este livro em números</h4><div class="nl">
      <p><b>50</b>pintores</p><p><b>{len(paises)}</b>países e regiões de origem</p><p><b>{max(anos) - min(anos)}</b>anos, de {min(anos)} a {max(anos)}</p>
      <p><b>{nobras}</b>obras reproduzidas</p><p><b>{len(arts) * 4}</b>páginas de pintores</p><p><b>1</b>regra: só obra livre</p></div></div>'''
    H.append(pagina_fixa('dir', 'pref fr', f'''      <div class="tx"><p><b>E a África?</b> Nenhum pintor africano de obra já livre tem hoje o alcance dos outros 50. A pintura moderna da África, de Aina Onabolu, Ben Enwonwu e Gerard Sekoto, é do século XX e ainda tem direito autoral. A arte africana mais antiga, das pinturas nas rochas às igrejas da Etiópia, é quase toda anônima: não cabe numa lista de nomes, e merecia um livro só dela.</p>
      <p>Use este livro como quiser: de trás para frente, do 1 para o 50, aos pulos. Quando um quadro chamar sua atenção, procure o original. Nenhuma página substitui ficar de pé diante de uma pintura.</p>
      <p class="assina">Pedro Torres</p></div>{nums}''', esc('Prefácio'), COR))
    # 6 como ler
    def mini(blocos):
        return '<div class="mini">' + ''.join(f'<i style="left:{x}%;top:{y}%;width:{w}%;height:{h}%;background:{c}"></i>' for x, y, w, h, c in blocos) + '</div>'
    az, ar, cz, am, vd = '#1F3F66', '#D8CDB9', '#B9AE9A', '#F6D86B', '#CFE3DA'
    H.append(pagina_fixa('esq', 'comoler fr', f'''<span class="chip">Como ler</span><h2 style="font:400 30pt/1 LivroDisp;margin:.08in 0 .25in">Quatro páginas por pintor</h2>
      <div class="pn">{mini([(0, 0, 100, 42, '#6A86A6'), (6, 28, 26, 14, '#fff'), (66, 34, 24, 18, ar), (6, 50, 50, 5, '#1E1913'), (6, 60, 80, 4, cz), (6, 70, 46, 22, ar), (58, 70, 36, 22, '#EFE8DA')])}
        <div class="tx"><b>1. A abertura</b>O <em>número</em> do pintor no ranking sobre a obra que o representa, o retrato, uma frase que resume quem ele foi e a <em>ficha</em>: onde nasceu e morreu, movimento, técnica, quanto pintou e onde ver. O quadro <em>Por que está no ranking</em> mostra os números que o puseram ali.</div></div>
      <div class="pn">{mini([(6, 6, 18, 4, az), (6, 12, 70, 5, '#1E1913'), (6, 22, 42, 44, cz), (52, 22, 42, 18, az), (52, 44, 42, 22, cz), (6, 76, 88, 2, '#1E1913'), (6, 70, 6, 4, az), (30, 80, 6, 4, cz), (60, 70, 6, 4, az)])}
        <div class="tx"><b>2. A vida</b>A história em quatro partes, uma <em>frase dele</em> em destaque e a <em>linha do tempo</em>: em cima, a vida do pintor; embaixo, o que acontecia no mundo e no Brasil enquanto isso.</div></div>
      <div class="pn">{mini([(6, 6, 18, 4, az), (6, 12, 70, 5, '#1E1913'), (6, 24, 88, 44, cz), (22, 34, 7, 5, az), (60, 50, 7, 5, az), (6, 72, 40, 6, ar), (52, 72, 40, 6, ar), (6, 84, 88, 12, am)])}
        <div class="tx"><b>3. Obra em foco</b>A obra mais importante, grande, com <em>marcas numeradas</em> nos detalhes que valem o olhar e a explicação de cada um. Embaixo, o <em>Você sabia?</em> traz curiosidades.</div></div>
      <div class="pn">{mini([(6, 6, 18, 4, az), (6, 12, 70, 5, '#1E1913'), (6, 22, 20, 12, ar), (28, 22, 20, 12, ar), (50, 22, 20, 12, ar), (72, 22, 20, 12, ar), (6, 38, 88, 9, '#EFE8DA'), (6, 52, 26, 18, cz), (37, 52, 26, 18, cz), (68, 52, 26, 18, cz), (6, 76, 27, 18, '#fff'), (37, 76, 27, 18, vd), (68, 76, 27, 18, '#EFE8DA')])}
        <div class="tx"><b>4. Como trabalhava</b>A técnica em <em>quatro passos</em>, as cores que ele usava, as <em>principais obras</em> e três caixas para fechar: quem ele <em>influenciou</em> (com o número no livro), uma atividade em <em>Para pensar e fazer</em> e as <em>palavras-chave</em>, que estão também no glossário.</div></div>''', esc('Como ler'), COR))
    # 7 sumário
    ent = ''
    for gp, (t, faixa) in enumerate((('A volta ao mundo', range(50, 40, -1)), ('O ranking', range(40, 0, -1)))):
        ent += f'<p class="grupo">{t}</p>'
        for p in faixa:
            a = por_pos.get(p)
            nm = esc(a['nome']) if a else '—'
            ent += f'<div class="e"><b>{p}</b><span>{nm}</span>' + (f'<a href="#p{p}"></a>' if a else '') + '</div>'
    ent += '<p class="grupo">Consulta</p>' + ''.join(f'<div class="e"><b>·</b><span>{t}</span><a href="#{h}"></a></div>' for t, h in (('Como fizemos o ranking', 'met'), ('Glossário', 'glos'), ('Créditos das imagens', 'cred'), ('Índice dos pintores', 'ind')))
    H.append(pagina_fixa('dir', 'sum fr', f'<span class="chip">Sumário</span><h2 style="font:400 28pt/1 LivroDisp;margin:.08in 0 .12in">Os 50, do último ao primeiro</h2><div class="cols">{ent}</div>', '', COR))
    # 8 e 9 os 50 num relance
    def grade(faixa):
        out = ''
        for p in faixa:
            a = por_pos.get(p)
            if not a: out += f'<div class="g"><div class="q" style="background:#E3DACB"><b>{p}</b></div><span>—</span></div>'; continue
            out += (f'<div class="g"><div class="q" style="background-image:url(\'{img(a["abertura"]["img"], 600)}\');background-position:{a["abertura"].get("pos", "center")}"><b>{p}</b></div>'
                    f'<span>{esc(a["nome"])}</span><em>{esc(a["origem"])} · {esc(a["vida"])}</em></div>')
        return out
    H.append(pagina_fixa('esq', 'relance fr', f'<span class="chip">Os 50 num relance</span><h2>Do 50º ao 26º</h2><div class="grade">{grade(range(50, 25, -1))}</div>', esc('Os 50 num relance'), COR))
    H.append(pagina_fixa('dir', 'relance fr', f'<span class="chip">Os 50 num relance</span><h2>Do 25º ao 1º</h2><div class="grade">{grade(range(25, 0, -1))}</div>', esc('Os 50 num relance'), COR))
    # 10 e 11 linha do tempo
    REG = {'Europa': '#1F3F66', 'Ásia': '#B23A2B', 'América Latina': '#2E7D4F', 'América do Norte': '#7A4E9C', 'Oceania': '#C27A12', 'Oriente Médio': '#8C6D3F'}
    def vida(a):
        m = re.findall(r'\d{3,4}', a['vida']); return int(m[0]), int(m[-1])
    def regiao(a):
        o = a['origem']
        if any(k in o for k in ('Japão', 'China', 'Coreia', 'Índia', 'Filipinas')): return 'Ásia'
        if any(k in o for k in ('Pérsia', 'Otomano', 'Turquia', 'Irã')): return 'Oriente Médio'
        if any(k in o for k in ('Brasil', 'Venezuela', 'México')): return 'América Latina'
        if 'Austrália' in o: return 'Oceania'
        if 'EUA' in o: return 'América do Norte'
        return 'Europa'
    def tl(lista, a0, a1, passo):
        W = 7.1; rows = len(lista); dy = min(.3, 7.6 / max(rows, 1)); out = ''
        for y in range(a0, a1 + 1, passo):
            out += f'<div class="ano" style="left:{(y - a0) / (a1 - a0) * W:.3f}in"><span>{y}</span></div>'
        antigos = [a for a in lista if vida(a)[1] < a0]
        lista = [a for a in lista if vida(a)[1] >= a0]
        for a in antigos:
            n, m = vida(a)
            out += f'<div class="lab" style="left:0;top:-.02in"><b>{a["pos"]}</b>{esc(a["nome"])} viveu muito antes: c. {n}–{m}</div>'
        for i, a in enumerate(lista):
            i += len(antigos)
            n, m = vida(a); x0 = (max(n, a0) - a0) / (a1 - a0) * W; x1 = min(W, (m - a0) / (a1 - a0) * W); top = .12 + i * dy
            out += f'<div class="bar" style="left:{x0:.3f}in;width:{max(x1 - x0, .05):.3f}in;top:{top:.3f}in;background:{REG[regiao(a)]}"></div>'
            lab = f'<b>{a["pos"]}</b>{esc(a["nome"])}' + (f' ({n}–{m})' if n < a0 else '')
            if x1 + 1.7 < W: out += f'<div class="lab" style="left:{x1 + .06:.3f}in;top:{top:.3f}in">{lab}</div>'
            else: out += f'<div class="lab" style="right:{W - x0 + .06:.3f}in;top:{top:.3f}in;text-align:right">{lab}</div>'
        return out
    leg = ''.join(f'<i style="background:{c}"></i>{r}' for r, c in REG.items())
    ordem = sorted(arts, key=lambda a: vida(a)[0])
    antes = [a for a in ordem if vida(a)[0] < 1760]; depois = [a for a in ordem if vida(a)[0] >= 1760]
    H.append(pagina_fixa('esq', 'tl fr', f'''<span class="chip">Linha do tempo</span><h2>Quando viveram</h2>
      <p class="sub">Cada barra vai do nascimento à morte. Nesta página, os nascidos antes de 1760; na seguinte, os outros.</p>
      <div class="graf">{tl(antes, 1250, 1850, 50)}</div><p class="leg">{leg}</p>''', esc('Linha do tempo'), COR))
    H.append(pagina_fixa('dir', 'tl fr', f'''<span class="chip">Linha do tempo</span><h2>Quando viveram</h2>
      <p class="sub">Os nascidos de 1760 em diante. Repare como muitos se cruzaram: Hokusai ainda vivia quando Manet nasceu.</p>
      <div class="graf">{tl(depois, 1740, 1960, 20)}</div><p class="leg">{leg}</p>''', esc('Linha do tempo'), COR))
    return ''.join(H)

def fundo(arts, esc, pagina_fixa, ranking, root):
    por_pos = {a['pos']: a for a in arts}
    H = []
    # como fizemos o ranking (2 páginas fixas, esquerda e direita)
    linhas = ''
    for p in range(1, 51):
        a = por_pos.get(p)
        if not a: continue
        r = ranking(a)
        nota = f'{r["nota"]:.0f}' if r.get('nota') is not None else 'vaga do mundo'
        inf = r['influencia'] if r.get('influencia') is not None else '—'
        linhas += f'<tr><td class="n">{p}</td><td>{esc(a["nome"])}</td><td>{r["wikis"]}</td><td>{inf}</td><td>{nota}</td></tr>'
    H.append(pagina_fixa('esq', 'consulta fr', '''<span class="chip">Consulta</span><h2 id="met">Como fizemos o ranking</h2><div class="tx">
      <p>Cada um dos 108 pintores pesquisados ganhou uma nota de 0 a 100, somando três medidas.</p>
      <p><b>Alcance mundial (50%).</b> Em quantas Wikipédias, das mais de 300 línguas que existem, o pintor tem artigo. É a base do Índice de Popularidade Histórica do projeto Pantheon, do MIT, e mostra quanto o mundo inteiro o conhece, não só um país. Dados do Wikidata, novembro de 2026.</p>
      <p><b>Mídia especializada e cânone (30%).</b> Presença nas listas de referência: os artistas mais buscados no banco de preços da Artnet em 2025; o artista mais buscado no Google em cada país (estudo Ken Bromley, 2020); os mais procurados no arquivo de imagens das universidades alemãs Prometheus em 2025; o índice de Charles Murray, tirado de 163 histórias da arte; o projeto Pantheon; o relatório Artprice de 2025; os recordes de público do Rijksmuseum (Vermeer, 2023) e da National Gallery de Londres (Van Gogh, 2024–25).</p>
      <p><b>Influência direta (20%).</b> Quantos artistas e movimentos o Wikidata registra como "influenciados por" ele.</p>
      <p>Alcance e influência viram posição relativa entre os 108, para que nenhuma escala domine. Com a nota pronta, tiramos quem ainda tem direito autoral (veja o prefácio) e ficamos com os 40 primeiros. As 10 vagas da volta ao mundo foram para o pintor de obra livre com mais Wikipédias em cada região que não tinha nenhum nome entre os 40.</p>
      <p><b>Limites.</b> Números de Wikipédia e de buscas medem fama, não qualidade, e enxergam melhor a arte europeia. Não medimos quantas pessoas leem os artigos hoje: com esse dado, nomes muito amados, como Vermeer e Klimt, provavelmente subiriam. A pesquisa completa, com os 108 candidatos, está nos arquivos do livro.</p></div>''', esc('Como fizemos o ranking'), COR))
    H.append(pagina_fixa('dir', 'consulta fr', f'''<table class="tab"><tr><th>Nº</th><th>Pintor</th><th>Wikipédias</th><th>Influenciou</th><th>Nota</th></tr>{linhas}</table>''', esc('Como fizemos o ranking'), COR))
    # glossário (flui)
    termos = {}
    for a in arts:
        for k, v in a.get('palavras', []):
            termos.setdefault(_fold(k), (k, v, []))[2].append(a['pos'])
    gl = ''.join(f'<p><b>{esc(k)}</b>: {esc(v)} <em>(nº {", ".join(str(x) for x in sorted(set(ps)))})</em></p>'
                 for _, (k, v, ps) in sorted(termos.items()))
    H.append(f'<section class="flui glos"><h2 id="glos">Glossário</h2><div class="cols">{gl}</div></section>')
    # créditos
    cr = ''
    for p in range(50, 0, -1):
        a = por_pos.get(p)
        if not a: continue
        cf = os.path.join(root, 'pesquisa', 'creditos', a['chave'] + '.json')
        c = json.load(open(cf)) if os.path.exists(cf) else {}
        itens = ''
        for arq in a.get('imagens', {}):
            v = c.get(f'{a["chave"]}/{arq}')
            if not v: continue
            fonte = re.sub(r'<[^>]+>', '', v.get('credito') or '').strip() or 'Wikimedia Commons'
            itens += f'<p>{esc(arq.rsplit(".", 1)[0].replace("-", " "))}: {esc(fonte[:110])} · {esc(v["licenca"])} · {esc(v["arquivo"].replace("File:", "commons: "))[:120]}</p>'
        cr += f'<h5>{p} · {esc(a["nome"])}</h5>{itens}'
    H.append(f'''<section class="flui cred"><h2 id="cred">Créditos das imagens</h2>
      <p class="intro">Todas as obras deste livro estão em domínio público. As fotografias vêm do Wikimedia Commons, quase sempre feitas pelos próprios museus e liberadas como domínio público ou CC0. Para cada imagem: o nome do arquivo no livro, a fonte, a licença e o arquivo no Commons (commons.wikimedia.org).</p>
      <div class="cols">{cr}</div></section>''')
    # índice
    CHAVE = {1: 'Gogh', 2: 'Leonardo', 3: 'Michelangelo', 5: 'Rafael', 10: 'Ticiano', 16: 'Giotto', 18: 'Caravaggio', 24: 'Greco',
             44: 'Osman Hamdi', 46: 'Gu Kaizhi', 49: 'Kim Hong-do', 33: 'Bruegel'}
    k = lambda a: _fold(CHAVE.get(a['pos'], a['nome'].split()[-1]))
    ind = ''.join(f'<p>{esc(a["nome"])} <b>{a["pos"]}</b></p>' for a in sorted(arts, key=k))
    H.append(f'<section class="flui ind"><h2 id="ind">Índice dos pintores</h2><div class="cols">{ind}</div></section>')
    return ''.join(H)

def contracapa(arts, esc):
    nomes = ' · '.join(esc(a['nome']) for a in sorted(arts, key=lambda a: -a['pos']))
    return f'''<section class="pg contra fr"><p class="big">De Gu Kaizhi a Van Gogh, mil e seiscentos anos de pintura, contados do 50º ao 1º.</p>
      <p>Quem são os pintores mais importantes da história? Este livro responde com números: o alcance de cada um no mundo, o que diz a mídia especializada e quantos artistas cada um influenciou.</p>
      <p>Cada pintor ganha quatro páginas com a vida, a linha do tempo, uma obra olhada de perto, a técnica explicada em passos, as principais obras e atividades para olhar e desenhar. Dez vagas fazem a volta ao mundo: Venezuela, Coreia, Austrália, Filipinas, China, Brasil, Turquia, Pérsia, Índia e Japão.</p>
      <p class="nomes">{nomes}</p></section>'''
