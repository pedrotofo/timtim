#!/usr/bin/env python3
"""Verifica um PDF de livro para leitura digital ou para impressão sob demanda (KDP Paperback).

Uso:
  python3 verifica_pdf.py livro.pdf --modo digital|impresso [--corte 6x9] [--fontes "Serif,Disp,Sans"] [--saida relatorio.json]

Checa: tamanho de página (com e sem sangria), número de páginas, fontes embutidas e fontes não previstas,
resolução efetiva das imagens, páginas em branco, páginas sangradas, margens de segurança e páginas
com pouco conteúdo (meia página vazia). Imprime um relatório e devolve código 1 se houver ERRO.
Requer poppler-utils (pdfinfo, pdffonts, pdfimages, pdftoppm), numpy e Pillow."""
import argparse, json, os, re, subprocess, sys, tempfile, glob
import numpy as np
from PIL import Image

PT = 72.0
SANGRIA = 0.125            # pol. KDP: +0,125 na largura (lado de fora) e +0,25 na altura
MARGEM_EXT = {False: .25, True: .375}   # margem externa/topo/base mínima, sem e com sangria
def margem_interna(paginas):
    for lim, m in ((150, .375), (300, .5), (500, .625), (700, .75), (828, .875)):
        if paginas <= lim:
            return m
    return .875

def run(*c):
    return subprocess.run(list(c), capture_output=True, text=True).stdout

class Rel:
    def __init__(self): self.itens = []
    def add(self, nivel, codigo, msg, paginas=None):
        self.itens.append({'nivel': nivel, 'codigo': codigo, 'msg': msg, 'paginas': paginas or []})
    def erros(self): return [i for i in self.itens if i['nivel'] == 'ERRO']
    def imprime(self, titulo):
        print(f'\n=== {titulo}')
        for n in ('ERRO', 'AVISO', 'REVISAR', 'OK'):
            for i in self.itens:
                if i['nivel'] == n:
                    pg = ''
                    if i['paginas']:
                        p = i['paginas']; pg = ' · p. ' + ', '.join(map(str, p[:25])) + (f' (+{len(p) - 25})' if len(p) > 25 else '')
                    print(f'[{n}] {i["codigo"]}: {i["msg"]}{pg}')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf'); ap.add_argument('--modo', choices=['digital', 'impresso'], default='digital')
    ap.add_argument('--corte', default='6x9', help='formato final em polegadas, ex.: 6x9')
    ap.add_argument('--fontes', default='', help='famílias previstas, separadas por vírgula (sem o prefixo de subconjunto)')
    ap.add_argument('--papel', default='EEEAE0', help='cor do papel das páginas, em hex, para achar o conteúdo')
    ap.add_argument('--capa', choices=['sim', 'nao'], help='a página 1 é a capa? padrão: sim no modo digital, não no impresso')
    ap.add_argument('--saida'); a = ap.parse_args()
    R = Rel(); impresso = a.modo == 'impresso'
    capa = (a.capa or ('nao' if impresso else 'sim')) == 'sim'
    if impresso and capa: R.add('ERRO', 'capa-no-miolo', 'o miolo impresso não pode trazer a capa: a KDP recebe a capa inteira em arquivo separado')
    cw, ch = (float(x) for x in a.corte.lower().split('x'))

    # 1. páginas e tamanho
    info = run('pdfinfo', a.pdf)
    n = int(re.search(r'Pages:\s+(\d+)', info).group(1))
    w, h = (float(x) for x in re.search(r'Page size:\s+([\d.]+) x ([\d.]+)', info).groups())
    wi, hi = w / PT, h / PT
    sem = abs(wi - cw) < .01 and abs(hi - ch) < .01
    com = abs(wi - (cw + SANGRIA)) < .01 and abs(hi - (ch + 2 * SANGRIA)) < .01
    tem_sangria = com
    if sem: R.add('OK', 'tamanho', f'{wi:.3f} × {hi:.3f} pol., igual ao corte {cw:g} × {ch:g} (sem sangria)')
    elif com: R.add('OK', 'tamanho', f'{wi:.3f} × {hi:.3f} pol., corte {cw:g} × {ch:g} com sangria de {SANGRIA} pol.')
    else: R.add('ERRO', 'tamanho', f'{wi:.3f} × {hi:.3f} pol. não corresponde a {cw:g} × {ch:g} nem a {cw + SANGRIA:g} × {ch + 2 * SANGRIA:g} (com sangria)')
    tamanhos = set(re.findall(r'(\d+(?:\.\d+)? x \d+(?:\.\d+)?) pts', run('pdfinfo', '-f', '1', '-l', str(n), a.pdf)))
    if len(tamanhos) > 1: R.add('ERRO', 'tamanho-variavel', f'páginas com tamanhos diferentes: {sorted(tamanhos)}')
    if impresso:
        if n < 24: R.add('ERRO', 'paginas', f'{n} páginas; o mínimo do KDP Paperback é 24')
        elif n > 828: R.add('ERRO', 'paginas', f'{n} páginas; o máximo do KDP Paperback é 828 (menos em alguns papéis e formatos)')
        else: R.add('OK', 'paginas', f'{n} páginas (KDP aceita de 24 a 828 em preto e branco; confira o limite do papel colorido escolhido)')
        if n % 2: R.add('AVISO', 'paridade', f'{n} páginas, número ímpar: a gráfica acrescenta uma página em branco no fim')
    else:
        R.add('OK', 'paginas', f'{n} páginas')
    m = re.search(r'Title:\s+(.*)', info); au = re.search(r'Author:\s+(.*)', info)
    R.add('OK' if m and m.group(1).strip() else 'AVISO', 'metadados', f'título "{m.group(1).strip() if m else ""}", autor "{au.group(1).strip() if au else ""}"')

    # 2. fontes
    fl = run('pdffonts', a.pdf).splitlines()[2:]
    fam, nao_emb = set(), []
    for l in fl:
        partes = l.split()
        if len(partes) < 5: continue
        nome = partes[0].split('+', 1)[-1]
        emb = l[l.find(partes[0]) + 0:].split()
        # colunas emb/sub/uni ficam antes do id do objeto; procura "yes"/"no" na ordem
        yn = re.findall(r'\b(yes|no)\b', l)
        if yn and yn[0] == 'no': nao_emb.append(nome)
        fam.add(re.sub(r'-(Bold|Italic|Semi-?Bold|Medium|Regular|Light|Black).*$', '', nome))
    if nao_emb: R.add('ERRO', 'fontes-nao-embutidas', 'fontes não embutidas (KDP rejeita): ' + ', '.join(sorted(set(nao_emb))))
    else: R.add('OK', 'fontes-embutidas', f'{len(fl)} fontes, todas embutidas')
    if a.fontes:
        prev = {x.strip() for x in a.fontes.split(',') if x.strip()}
        extra = sorted(f for f in fam if not any(f.startswith(p) for p in prev))
        if extra: R.add('AVISO', 'fontes-de-reserva', 'fontes fora da identidade do livro: ' + ', '.join(extra) +
                        '. Em geral entram por um caractere que a fonte do livro não tem (espaços especiais, setas, símbolos). Ache o caractere e troque ou declare uma fonte para ele.')
        else: R.add('OK', 'fontes-da-identidade', 'só as famílias previstas: ' + ', '.join(sorted(fam)))

    # 3. imagens: resolução efetiva
    baixa, media = [], []
    for l in run('pdfimages', '-list', a.pdf).splitlines()[2:]:
        c = l.split()
        if len(c) < 14 or c[2] in ('smask', 'stencil'): continue
        pg, xp, yp = int(c[0]), int(c[12]), int(c[13])
        ppi = min(xp, yp)
        if ppi < 200: baixa.append((pg, ppi))
        elif ppi < 300: media.append((pg, ppi))
    lim_err = 'ERRO' if impresso else 'AVISO'
    if baixa: R.add(lim_err, 'imagem-baixa-resolucao', 'imagens abaixo de 200 ppi efetivos (borram na impressão): ' +
                    ', '.join(f'p.{p} {v}ppi' for p, v in sorted(set(baixa))[:20]), sorted({p for p, _ in baixa}))
    if media: R.add('AVISO' if impresso else 'OK', 'imagem-abaixo-300ppi', f'{len(media)} imagens entre 200 e 299 ppi efetivos; a KDP recomenda 300 ppi para impressão',
                    sorted({p for p, _ in media}))
    if not baixa and not media: R.add('OK', 'imagens', 'todas as imagens com 300 ppi efetivos ou mais')

    # 4. leitura visual das páginas: brancas, sangradas, margens, pouco conteúdo
    papel = np.array([int(a.papel[i:i + 2], 16) for i in (0, 2, 4)], float)
    dpi = 40
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(['pdftoppm', '-r', str(dpi), '-png', a.pdf, f'{td}/p'], check=True)
        fs = sorted(glob.glob(f'{td}/p-*.png'))
        brancas, sangradas, margem_ruim, vazias = [], [], [], []
        mi = margem_interna(n); me = MARGEM_EXT[tem_sangria]
        for k, f in enumerate(fs, 1):
            im = np.asarray(Image.open(f).convert('RGB'), float); H, W, _ = im.shape
            borda = np.concatenate([im[:3].reshape(-1, 3), im[-3:].reshape(-1, 3), im[:, :3].reshape(-1, 3), im[:, -3:].reshape(-1, 3)])
            fundo = np.median(borda, axis=0)
            mask = np.abs(im - papel).sum(2) > 45
            if mask.mean() < .002:
                brancas.append(k); continue
            if capa and k == 1: continue
            ys, xs = np.where(mask)
            esq, dir_, top, base = xs.min() / dpi, (W - 1 - xs.max()) / dpi, ys.min() / dpi, (H - 1 - ys.max()) / dpi
            if np.abs(fundo - papel).sum() > 45 or sum(v < .04 for v in (esq, dir_, top, base)) >= 2:
                sangradas.append(k); continue
            # recto (ímpar) tem a lombada à esquerda; verso (par), à direita
            dentro, fora = (esq, dir_) if k % 2 else (dir_, esq)
            off = SANGRIA if tem_sangria else 0
            falhas = []
            if dentro < mi - .02: falhas.append(f'interna {dentro:.2f}<{mi}')
            if fora - off < me - .02: falhas.append(f'externa {fora - off:.2f}<{me}')
            if top - (off if tem_sangria else 0) < me - .02: falhas.append(f'topo {top:.2f}<{me}')
            if base - (off if tem_sangria else 0) < me - .02: falhas.append(f'base {base:.2f}<{me}')
            if falhas: margem_ruim.append((k, falhas))
            # pouco conteúdo: só a parte de cima da mancha ocupada (meia página vazia antes de um bloco que pulou)
            linhas = mask[:, int(W * .1):int(W * .9)].any(1)
            area = linhas[int(H * .07):int(H * .9)]
            if area.size and area.mean() < .42 and k not in (1, n):
                vazias.append(k)
    if brancas:
        R.add('AVISO' if len(brancas) > 2 else 'OK', 'paginas-em-branco', f'{len(brancas)} página(s) em branco', brancas)
        seq = max((len(list(g)) for g in _sequencias(brancas)), default=0)
        if impresso and seq > 2: R.add('AVISO', 'brancas-seguidas', f'{seq} páginas em branco seguidas; a KDP pode recusar sequências longas de páginas vazias')
    if sangradas:
        if impresso and not tem_sangria:
            R.add('ERRO', 'sangria-ausente', f'{len(sangradas)} página(s) com imagem ou cor até a borda, mas o PDF não tem sangria. '
                  f'Para impressão gere em {cw + SANGRIA:g} × {ch + 2 * SANGRIA:g} pol. com o fundo passando 0,125 pol. do corte', sangradas)
        else:
            R.add('OK', 'paginas-sangradas', f'{len(sangradas)} página(s) com imagem ou cor até a borda', sangradas)
    if margem_ruim:
        R.add('ERRO' if impresso else 'AVISO', 'margem', f'{len(margem_ruim)} página(s) com conteúdo dentro da margem mínima (interna {mi} pol. para {n} páginas, externa {me} pol.): ' +
              '; '.join(f'p.{p} ' + ', '.join(x) for p, x in margem_ruim[:12]), [p for p, _ in margem_ruim])
    else: R.add('OK', 'margem', f'mancha dentro das margens mínimas (interna {mi} pol., externa {me} pol.)')
    if vazias: R.add('REVISAR', 'pouco-conteudo', f'{len(vazias)} página(s) com mais da metade vazia; confira na folha de contato se é fim de seção ou um bloco que pulou de página', vazias)

    R.imprime(f'PDF {os.path.basename(a.pdf)} · modo {a.modo}')
    if a.saida: json.dump(R.itens, open(a.saida, 'w'), ensure_ascii=False, indent=1)
    sys.exit(1 if R.erros() else 0)

def _sequencias(ps):
    run_ = []
    for p in ps:
        if run_ and p != run_[-1] + 1:
            yield run_; run_ = []
        run_.append(p)
    if run_: yield run_

if __name__ == '__main__':
    main()
