#!/usr/bin/env python3
"""Conferência completa de um livro antes da entrega: roda todos os verificadores e monta as folhas de contato.

Uso: python3 confere_livro.py <pasta-do-livro> [--saida <pasta>] [--fontes "Serif,Disp,LivroSans"] [--papel branco]

Procura em <pasta>/out: o PDF de leitura, o PDF do miolo impresso (*-miolo-impresso.pdf), a capa inteira impressa
(*-capa-impressa.pdf), os EPUBs e a capa do e-book (capa-ebook-1600x2560.jpg). Para cada um roda o verificador certo
e grava <saida>/relatorio-editora.md, as folhas de contato do PDF (páginas a revisar com borda vermelha) e as
prévias do EPUB. Código de saída 1 se houver qualquer ERRO."""
import argparse, glob, json, os, re, subprocess, sys, tempfile
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))

def py(script, *args):
    r = subprocess.run([sys.executable, os.path.join(HERE, script), *args], capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).replace('Picked up JAVA_TOOL_OPTIONS', '').strip()

def folhas(pdf, marcas, saida, nome):
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(['pdftoppm', '-r', '32', '-png', pdf, f'{td}/p'], check=True)
        fs = sorted(glob.glob(f'{td}/p-*.png')); ims = [Image.open(f).convert('RGB') for f in fs]
        w, h = ims[0].size; out = []
        for b in range(0, len(ims), 24):
            bloco = ims[b:b + 24]; cols = 8; rows = (len(bloco) + cols - 1) // cols
            c = Image.new('RGB', (cols * (w + 10), rows * (h + 22)), '#666'); d = ImageDraw.Draw(c)
            for k, im in enumerate(bloco):
                p = b + k + 1; x, y = (k % cols) * (w + 10), (k // cols) * (h + 22); c.paste(im, (x + 5, y + 4))
                if p in marcas:
                    d.rectangle([x + 2, y + 1, x + w + 7, y + h + 7], outline='#ff3b3b', width=3)
                d.text((x + 6, y + h + 7), str(p) + (' ' + marcas[p] if p in marcas else ''), fill='#ffdddd' if p in marcas else 'white')
            f = os.path.join(saida, f'{nome}-folha-{b // 24 + 1:02d}.jpg'); c.save(f, quality=82); out.append(f)
        return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('pasta'); ap.add_argument('--saida')
    ap.add_argument('--fontes', default='Serif,Disp,LivroSans,LivroSerif,LivroDisp'); ap.add_argument('--papel', default='branco')
    a = ap.parse_args(); od = os.path.join(a.pasta, 'out'); saida = a.saida or os.path.join(od, 'conferencia'); os.makedirs(saida, exist_ok=True)
    rel = [f'# Conferência editorial · {os.path.basename(os.path.abspath(a.pasta))}', '']
    erro = False
    pdfs = sorted(glob.glob(os.path.join(od, '*.pdf')))
    for pdf in pdfs:
        nome = os.path.basename(pdf)
        if 'capa-impressa' in nome:
            n = None
            miolo = [p for p in pdfs if 'miolo-impresso' in p]
            if miolo: n = re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', miolo[0]], capture_output=True, text=True).stdout).group(1)
            code, txt = py('verifica_capa.py', 'impressa', '--paginas', str(n or 0), '--papel', a.papel, '--pdf', pdf) if n else (1, '[ERRO] sem miolo impresso para calcular a lombada')
        else:
            modo = 'impresso' if 'miolo-impresso' in nome else 'digital'
            js = os.path.join(saida, nome + '.json')
            code, txt = py('verifica_pdf.py', pdf, '--modo', modo, '--fontes', a.fontes, '--saida', js)
            marcas = {}
            for it in json.load(open(js)) if os.path.exists(js) else []:
                if it['nivel'] in ('ERRO', 'AVISO', 'REVISAR'):
                    for p in it['paginas']: marcas.setdefault(p, it['codigo'][:14])
            fl = folhas(pdf, marcas, saida, os.path.splitext(nome)[0])
            txt += '\n\nFolhas de contato (páginas a revisar com borda vermelha): ' + ', '.join(os.path.basename(f) for f in fl)
        erro |= code == 1
        rel += [f'## {nome}', '', '```', txt, '```', '']
    for ep in sorted(glob.glob(os.path.join(od, '*.epub'))):
        code, txt = py('verifica_epub.py', ep); erro |= code == 1
        c2, t2 = py('previa_epub.py', ep, os.path.join(saida, os.path.splitext(os.path.basename(ep))[0]))
        rel += [f'## {os.path.basename(ep)}', '', '```', txt, '', t2, '```', '']
    for capa in glob.glob(os.path.join(od, 'capa-ebook*.jpg')):
        code, txt = py('verifica_capa.py', 'ebook', capa); erro |= code == 1
        rel += [f'## {os.path.basename(capa)}', '', '```', txt, '```', '']
    rel += ['## Conferência visual (sempre, por uma pessoa ou por você)', '',
            '- Abra cada folha de contato e olhe as páginas com borda vermelha, depois o livro inteiro de novo.',
            '- Abra as prévias do EPUB no celular e no Kindle: capa, sumário, uma abertura de parte, uma aula com obra e balões, um exercício, o catálogo.',
            '- Antes de enviar ao KDP: Kindle Previewer (EPUB) e o Visualizador de Impressão do próprio KDP (miolo e capa).']
    f = os.path.join(saida, 'relatorio-editora.md'); open(f, 'w').write('\n'.join(rel))
    print('\n'.join(rel)); print(f'\nRelatório: {f}')
    sys.exit(1 if erro else 0)

if __name__ == '__main__':
    main()
