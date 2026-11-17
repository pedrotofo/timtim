#!/usr/bin/env python3
"""Verifica um EPUB para Kindle (KDP) e para as lojas que recebem EPUB (Apple Books, Google Play, Kobo).

Uso: python3 verifica_epub.py livro.epub [--loja kdp|geral] [--saida relatorio.json]

1. Roda o EPUBCheck oficial (W3C). Qualquer erro ou fatal reprova.
2. Confere o pacote: mimetype, OPF (título, autor, idioma, identificador, data de modificação, capa declarada),
   documento de navegação, espinha, idioma de cada página, imagens sem texto alternativo, scripts,
   CSS arriscado para leitores (flex, grid, posição absoluta, vw/vh), fontes embutidas, peso de cada imagem,
   tamanho total e a proporção da capa interna.
Devolve código 1 se houver ERRO."""
import argparse, json, os, re, subprocess, sys, zipfile, io, shutil
import xml.etree.ElementTree as ET
from PIL import Image

NS = {'opf': 'http://www.idpf.org/2007/opf', 'dc': 'http://purl.org/dc/elements/1.1/', 'c': 'urn:oasis:names:tc:opendocument:xmlns:container',
      'x': 'http://www.w3.org/1999/xhtml', 'epub': 'http://www.idpf.org/2007/ops'}
LIMITE_KDP_MB = 650     # tamanho máximo do arquivo enviado ao KDP
TARIFA_MB = 0.15        # US$ por MB cobrado na opção de 70 % de royalties (Amazon.com); confira a tabela atual da loja

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
        elif h < 2560: R.add('AVISO', 'capa-interna', msg + ' (recomendado 1600 × 2560 px)')
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
    grandes = []
    for n in imgs:
        if n.lower().endswith(('.jpg', '.jpeg', '.png')):
            try:
                w_, h_ = Image.open(io.BytesIO(z.read(n))).size
                if max(w_, h_) > 4000: grandes.append(f'{os.path.basename(n)} {w_}×{h_}')
            except Exception: R.add('ERRO', 'imagem-corrompida', n)
    webp = [n for n in imgs if n.lower().endswith('.webp')]
    if webp: R.add('ERRO', 'webp', 'imagens WebP não são aceitas pelo Kindle: ' + ', '.join(webp[:5]))
    if pesadas: R.add('AVISO', 'imagem-pesada', 'imagens acima de 5 MB: ' + ', '.join(f'{os.path.basename(n)} {s:.1f}MB' for n, s in pesadas[:8]))
    if grandes: R.add('AVISO', 'imagem-grande', 'imagens com mais de 4000 px no lado maior (não ganham nitidez no leitor e pesam): ' + ', '.join(grandes[:6]))
    R.add('OK', 'imagens', f'{len(imgs)} imagens, {sum(z.getinfo(n).file_size for n in imgs) / 1e6:.1f} MB no total')
    fontes = [n for n in nomes if n.lower().endswith(('.ttf', '.otf', '.woff', '.woff2'))]
    if fontes: R.add('OK', 'fontes', f'{len(fontes)} fontes embutidas: ' + ', '.join(os.path.basename(f) for f in fontes) + '. Confirme que a licença permite embutir (EB Garamond e Archivo: SIL OFL, permitido).')

    # 5. tamanho
    if a.loja == 'kdp':
        if tam > LIMITE_KDP_MB: R.add('ERRO', 'tamanho', f'{tam:.1f} MB; o KDP aceita até {LIMITE_KDP_MB} MB')
        elif tam > 10: R.add('AVISO', 'tamanho', f'{tam:.1f} MB. Na opção de 70 % o KDP desconta a entrega por MB (cerca de US$ {TARIFA_MB:.2f}/MB nos EUA, '
                             f'perto de US$ {tam * TARIFA_MB:.2f} por venda pelo arquivo convertido). Use a versão "loja" com imagens menores.')
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
