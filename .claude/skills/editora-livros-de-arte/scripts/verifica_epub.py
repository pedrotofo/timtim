#!/usr/bin/env python3
"""Verifica um EPUB para Kindle (KDP) e para as lojas que recebem EPUB (Apple Books, Google Play, Kobo).

Uso: python3 verifica_epub.py livro.epub [--loja kdp|geral] [--saida relatorio.json]

1. Roda o EPUBCheck oficial (W3C). Qualquer erro ou fatal reprova.
2. Confere o pacote: mimetype, OPF (título, autor, idioma, identificador, data de modificação, capa declarada),
   documento de navegação, espinha, idioma de cada página, imagens sem texto alternativo, scripts,
   CSS arriscado para leitores (flex, grid, posição absoluta, vw/vh), fontes embutidas, peso de cada imagem,
   tamanho total e a proporção da capa interna.
3. Confere o que as lojas recusam ou o leitor estranha: imagem acima de 4 milhões de pixels (a Apple Books recusa,
   inclusive a capa interna), metadados de acessibilidade (Lei Europeia de Acessibilidade, desde 28/06/2025), frases
   que só valem no papel ("imprima", "p. 42", "página ao lado") e até onde chega a amostra grátis de 10 % da Amazon.
Devolve código 1 se houver ERRO."""
import argparse, json, os, re, subprocess, sys, zipfile, io, shutil
import xml.etree.ElementTree as ET
from PIL import Image

NS = {'opf': 'http://www.idpf.org/2007/opf', 'dc': 'http://purl.org/dc/elements/1.1/', 'c': 'urn:oasis:names:tc:opendocument:xmlns:container',
      'x': 'http://www.w3.org/1999/xhtml', 'epub': 'http://www.idpf.org/2007/ops'}
LIMITE_KDP_MB = 650     # tamanho máximo do arquivo enviado ao KDP
TARIFA_MB = 0.15        # US$ por MB cobrado na opção de 70 % de royalties (Amazon.com); confira a tabela atual da loja
TARIFA_MB_BR = 0.30     # R$ por MB na Amazon.com.br (tabela de preços da KDP, conferida em 17/11/2026)
LIMITE_PIXELS = 4_000_000   # Apple Books: nenhuma imagem dentro do EPUB acima disso
PAPEL = [(r'\bimprim(a|ir|e)\b', 'imprimir'), (r'\bp\. ?\d', 'número de página'), (r'página (ao lado|seguinte|anterior|oposta)', 'página ao lado'),
         (r'\bverso da (folha|página)\b', 'verso da folha'), (r'\b(recorte|destaque) (esta|a) (página|folha)', 'recortar a página')]

def jar():
    if os.environ.get('EPUBCHECK_JAR'): return os.environ['EPUBCHECK_JAR']
    for base in ('/usr/local/lib/python3.13/dist-packages', '/usr/local/lib/python3.13/site-packages', '/usr/lib/python3/dist-packages'):
        p = os.path.join(base, 'epubcheck', 'epubcheck.jar')
        if os.path.exists(p): return p
    try:
        import epubcheck; d = os.path.dirname(epubcheck.__file__)
        for root, _, fs in os.walk(os.path.dirname(d)):
            if 'epubcheck.jar' in fs: return os.path.join(root, 'epubcheck.jar')
    except ImportError: pass
    return None

class Rel:
    def __init__(self): self.itens = []
    def add(self, nivel, codigo, msg): self.itens.append({'nivel': nivel, 'codigo': codigo, 'msg': msg})
    def imprime(self, titulo):
        print(f'\n=== {titulo}')
        for n in ('ERRO', 'AVISO', 'REVISAR', 'OK'):
            for i in self.itens:
                if i['nivel'] == n: print(f'[{n}] {i["codigo"]}: {i["msg"]}')

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('epub'); ap.add_argument('--loja', choices=['kdp', 'geral'], default='kdp'); ap.add_argument('--saida')
    a = ap.parse_args(); R = Rel()
    tam = os.path.getsize(a.epub) / 1e6

    # 1. EPUBCheck
    j = jar()
    if not j or not shutil.which('java'):
        R.add('ERRO', 'epubcheck-ausente', 'EPUBCheck não encontrado (pip install epubcheck, Java 11+). Não entregue sem essa validação.')
    else:
        out = subprocess.run(['java', '-jar', j, a.epub], capture_output=True, text=True)
        txt = out.stdout + out.stderr
        m = re.search(r'Messages:\s*(\d+) fatals? / (\d+) errors? / (\d+) warnings?', txt)
        ver = re.search(r'EPUBCheck v([\d.]+)', txt)
        if m:
            f, e, w = map(int, m.groups())
            linhas = [l for l in txt.splitlines() if l.startswith(('FATAL', 'ERROR', 'WARNING'))]
            if f or e: R.add('ERRO', 'epubcheck', f'{f} fatais, {e} erros, {w} avisos. ' + ' | '.join(linhas[:8]))
            elif w: R.add('AVISO', 'epubcheck', f'{w} avisos. ' + ' | '.join(linhas[:8]))
            else: R.add('OK', 'epubcheck', 'EPUBCheck: nenhum erro ou aviso')
        else:
            R.add('ERRO', 'epubcheck', 'não consegui ler o resultado do EPUBCheck: ' + txt[-400:])

    z = zipfile.ZipFile(a.epub); nomes = z.namelist()
    # 2. pacote
    info0 = z.infolist()[0]
    if info0.filename != 'mimetype' or info0.compress_type != zipfile.ZIP_STORED or z.read('mimetype') != b'application/epub+zip':
        R.add('ERRO', 'mimetype', 'o primeiro arquivo do ZIP deve ser "mimetype", sem compressão, com "application/epub+zip"')
    cont = ET.fromstring(z.read('META-INF/container.xml'))
    opf_path = cont.find('.//c:rootfile', NS).get('full-path'); base = os.path.dirname(opf_path)
    opf = ET.fromstring(z.read(opf_path)); ver = opf.get('version')
    md = opf.find('opf:metadata', NS)
    def dc(tag): e = md.find(f'dc:{tag}', NS); return (e.text or '').strip() if e is not None else ''
    tit, aut, lang, ident = dc('title'), dc('creator'), dc('language'), dc('identifier')
    falta = [n for n, v in (('título', tit), ('autor', aut), ('idioma', lang), ('identificador', ident)) if not v]
    if falta: R.add('ERRO', 'metadados', 'faltam no OPF: ' + ', '.join(falta))
    else: R.add('OK', 'metadados', f'EPUB {ver} · "{tit}" · {aut} · {lang} · {ident}')
    if lang and not lang.lower().startswith('pt'): R.add('AVISO', 'idioma', f'idioma declarado "{lang}"; os livros da série são em pt-BR')
    if ver and ver.startswith('3') and not any(m_.get('property') == 'dcterms:modified' for m_ in md.findall('opf:meta', NS)):
        R.add('ERRO', 'modificado', 'EPUB 3 exige <meta property="dcterms:modified">')
    props = [m_.get('property') or '' for m_ in md.findall('opf:meta', NS)]
    a11y = [p_ for p_ in props if p_.startswith('schema:access')]
    if not a11y: R.add('AVISO', 'acessibilidade', 'sem metadados de acessibilidade (schema:accessMode, accessibilityFeature, accessibilityHazard, accessibilitySummary). '
                       'Desde 28/06/2025 a Lei Europeia de Acessibilidade pede essas informações para e-books vendidos na UE; as lojas mostram o que o OPF declara.')
    else:
        falta_a = [k for k in ('schema:accessMode', 'schema:accessibilityFeature', 'schema:accessibilityHazard', 'schema:accessibilitySummary') if k not in props]
        R.add('AVISO' if falta_a else 'OK', 'acessibilidade', ('faltam ' + ', '.join(falta_a)) if falta_a else f'{len(a11y)} metadados de acessibilidade')
    if md.find('dc:description', NS) is None: R.add('AVISO', 'descricao', 'sem dc:description (a sinopse ajuda nas lojas que leem o OPF)')
    man = {i.get('id'): i for i in opf.find('opf:manifest', NS)}
    href = lambda i: os.path.normpath(os.path.join(base, i.get('href'))).replace('\\', '/')
    capa = [i for i in man.values() if 'cover-image' in (i.get('properties') or '')]
    if not capa:
        cm = md.find("opf:meta[@name='cover']", NS)
        if cm is not None and cm.get('content') in man: capa = [man[cm.get('content')]]
    if not capa: R.add('ERRO', 'capa-interna', 'nenhuma imagem marcada como capa (properties="cover-image")')
    else:
        im = Image.open(io.BytesIO(z.read(href(capa[0])))); w, h = im.size; r = h / w
        msg = f'capa interna {w} × {h} px, proporção {r:.2f}:1, modo {im.mode}'
        if abs(r - 1.6) > .02: R.add('AVISO', 'capa-interna', msg + ' (a recomendada é 1,6:1)')
        elif w * h > LIMITE_PIXELS: R.add('ERRO', 'capa-interna', msg + f' = {w * h / 1e6:.2f} milhões de pixels; a Apple Books recusa imagem interna acima de 4 milhões. '
                                         'Dentro do EPUB use 1500 × 2400; a capa de 1600 × 2560 vai à parte para a loja.')
        elif w < 1400: R.add('AVISO', 'capa-interna', msg + ' (a Apple pede pelo menos 1400 px no lado menor)')
        else: R.add('OK', 'capa-interna', msg)
    nav = [i for i in man.values() if 'nav' in (i.get('properties') or '')]
    if ver and ver.startswith('3'):
        if not nav: R.add('ERRO', 'sumario', 'EPUB 3 sem documento de navegação (properties="nav")')
        else:
            n = ET.fromstring(z.read(href(nav[0])))
            toc = [x for x in n.iter('{http://www.w3.org/1999/xhtml}nav') if x.get('{http://www.idpf.org/2007/ops}type') == 'toc']
            lis = len(list(toc[0].iter('{http://www.w3.org/1999/xhtml}li'))) if toc else 0
            R.add('OK' if lis >= 3 else 'ERRO', 'sumario', f'sumário com {lis} entradas' if toc else 'nav sem epub:type="toc"')
    if not any(i.get('media-type') == 'application/x-dtbncx+xml' for i in man.values()):
        R.add('OK', 'ncx', 'sem NCX (não é exigido no EPUB 3; leitores antigos usam o nav)')
    spine = opf.find('opf:spine', NS); itens = [s.get('idref') for s in spine]
    R.add('OK', 'espinha', f'{len(itens)} documentos na ordem de leitura')
    # amostra grátis: a Amazon mostra os primeiros 10 % do conteúdo (a conta aqui é pelo texto, aproximada)
    textos = []
    for idr in itens:
        if idr in man:
            t = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', z.read(href(man[idr])).decode('utf-8', 'replace')))
            textos.append((os.path.basename(man[idr].get('href')), t))
    total = sum(len(t) for _, t in textos) or 1; acc = 0; corte = None
    for nm_, t in textos:
        acc += len(t)
        if acc / total >= .10: corte = nm_; break
    if corte:
        aula = next((nm_ for nm_, _ in textos if re.search(r'cap\d|capitulo|aula', nm_)), None)
        pos_aula = sum(len(t) for nm_, t in textos[:[n for n, _ in textos].index(aula)]) / total if aula else None
        R.add('REVISAR', 'amostra', f'a amostra de 10 % termina em {corte}' + (f'; a primeira aula ({aula}) começa em {pos_aula * 100:.0f} % do texto' if aula else '') +
              '. Quem baixa a amostra deveria ver ao menos uma aula ou um exercício: o que vem antes (galerias, linhas do tempo) pode ir para depois no e-book.')
    papel = []
    for nm_, t in textos:
        for pat, nome in PAPEL:
            for m_ in re.finditer(pat, t, re.I): papel.append(f'{nome} em {nm_}: "…{t[max(0, m_.start() - 40):m_.end() + 40].strip()}…"')
    if papel: R.add('REVISAR', 'so-no-papel', f'{len(papel)} trechos que só valem impressos: ' + ' | '.join(papel[:6]))
    else: R.add('OK', 'so-no-papel', 'nenhuma frase de livro impresso (imprimir, número de página, página ao lado)')

    # 3. páginas XHTML
    sem_alt, scripts, sem_lang, css_risco = [], [], [], set()
    for nm in nomes:
        if nm.endswith(('.xhtml', '.html')):
            t = z.read(nm).decode('utf-8', 'replace')
            if re.search(r'<script\b', t): scripts.append(nm)
            if not re.search(r'<html[^>]*\b(xml:)?lang=', t): sem_lang.append(nm)
            for m_ in re.finditer(r'<img\b[^>]*>', t):
                if not re.search(r'\balt="[^"]', m_.group(0)) and 'cover' not in nm and 'role="presentation"' not in m_.group(0): sem_alt.append(nm)
            for st in re.findall(r'style="([^"]*)"', t): _css(st, css_risco)
        if nm.endswith('.css'): _css(z.read(nm).decode('utf-8', 'replace'), css_risco)
    if scripts: R.add('AVISO', 'scripts', f'{len(scripts)} páginas com <script>; o Kindle ignora scripts')
    if sem_lang: R.add('AVISO', 'lang', f'{len(sem_lang)} páginas sem atributo lang (afeta hifenização e leitura em voz alta)')
    if sem_alt: R.add('AVISO', 'alt', f'{len(sem_alt)} imagens com alt vazio ou ausente; obra de arte pede descrição (título e artista), só ornamento leva alt vazio: ' + ', '.join(sorted(set(sem_alt))[:6]))
    else: R.add('OK', 'alt', 'todas as imagens com texto alternativo (ou decorativas declaradas)')
    if css_risco: R.add('AVISO', 'css-leitores', 'CSS que leitores e o Kindle tratam mal em livro refluível: ' + ', '.join(sorted(css_risco)) +
                        '. Confira essas páginas na prévia de celular e de Kindle.')
    else: R.add('OK', 'css-leitores', 'sem flex, grid, posição absoluta ou unidades de tela')

    # 4. imagens e fontes
    imgs = [n for n in nomes if n.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp'))]
    pesadas = [(n, z.getinfo(n).file_size / 1e6) for n in imgs if z.getinfo(n).file_size > 5e6]
    grandes, megapix, cmyk = [], [], []
    for n in imgs:
        if n.lower().endswith(('.jpg', '.jpeg', '.png')):
            try:
                im_ = Image.open(io.BytesIO(z.read(n))); w_, h_ = im_.size
                if max(w_, h_) > 4000: grandes.append(f'{os.path.basename(n)} {w_}×{h_}')
                if w_ * h_ > LIMITE_PIXELS: megapix.append(f'{os.path.basename(n)} {w_}×{h_}')
                if im_.mode in ('CMYK', 'I;16', 'I'): cmyk.append(f'{os.path.basename(n)} {im_.mode}')
            except Exception: R.add('ERRO', 'imagem-corrompida', n)
    webp = [n for n in imgs if n.lower().endswith('.webp')]
    if webp: R.add('ERRO', 'webp', 'imagens WebP não são aceitas pelo Kindle: ' + ', '.join(webp[:5]))
    if megapix: R.add('ERRO', 'imagem-4mp', 'imagens acima de 4 milhões de pixels (a Apple Books recusa o arquivo): ' + ', '.join(megapix[:8]))
    if cmyk: R.add('ERRO', 'imagem-cmyk', 'imagens fora de RGB (leitores mostram cores erradas ou nada): ' + ', '.join(cmyk[:8]))
    if pesadas: R.add('AVISO', 'imagem-pesada', 'imagens acima de 5 MB: ' + ', '.join(f'{os.path.basename(n)} {s:.1f}MB' for n, s in pesadas[:8]))
    if grandes: R.add('AVISO', 'imagem-grande', 'imagens com mais de 4000 px no lado maior (não ganham nitidez no leitor e pesam): ' + ', '.join(grandes[:6]))
    R.add('OK', 'imagens', f'{len(imgs)} imagens, {sum(z.getinfo(n).file_size for n in imgs) / 1e6:.1f} MB no total')
    fontes = [n for n in nomes if n.lower().endswith(('.ttf', '.otf', '.woff', '.woff2'))]
    if fontes: R.add('OK', 'fontes', f'{len(fontes)} fontes embutidas: ' + ', '.join(os.path.basename(f) for f in fontes) + '. Confirme que a licença permite embutir (EB Garamond e Archivo: SIL OFL, permitido).')

    # 5. tamanho
    if a.loja == 'kdp':
        if tam > LIMITE_KDP_MB: R.add('ERRO', 'tamanho', f'{tam:.1f} MB; o KDP aceita até {LIMITE_KDP_MB} MB')
        elif tam > 10: R.add('AVISO', 'tamanho', f'{tam:.1f} MB. Na opção de 70 % o KDP desconta a entrega por MB do arquivo convertido: perto de '
                             f'US$ {tam * TARIFA_MB:.2f} por venda nos EUA (US$ {TARIFA_MB:.2f}/MB) e R$ {tam * TARIFA_MB_BR:.2f} no Brasil (R$ {TARIFA_MB_BR:.2f}/MB). '
                             f'Use a versão "loja" e compare com a opção de 35 % (sem tarifa): no Brasil a de 70 % só compensa acima de R$ {tam * TARIFA_MB_BR * 2:.2f}.')
        else: R.add('OK', 'tamanho', f'{tam:.1f} MB (custo de entrega estimado na opção de 70 %: US$ {tam * TARIFA_MB:.2f}; o KDP calcula sobre o arquivo convertido)')
    else:
        R.add('OK' if tam < 100 else 'AVISO', 'tamanho', f'{tam:.1f} MB')
    R.imprime(f'EPUB {os.path.basename(a.epub)} · loja {a.loja}')
    if a.saida: json.dump(R.itens, open(a.saida, 'w'), ensure_ascii=False, indent=1)
    sys.exit(1 if any(i['nivel'] == 'ERRO' for i in R.itens) else 0)

def _css(txt, acc):
    for pat, nome in ((r'display\s*:\s*(inline-)?flex', 'display:flex'), (r'display\s*:\s*grid', 'display:grid'),
                      (r'position\s*:\s*(absolute|fixed)', 'position:absolute/fixed'), (r'\d(vw|vh)\b', 'unidades vw/vh')):
        if re.search(pat, txt): acc.add(nome)

if __name__ == '__main__':
    main()
