#!/usr/bin/env python3
"""Verifica as capas: a do e-book (Kindle e lojas de EPUB) e a capa inteira do livro impresso (KDP Paperback).

E-book:   python3 verifica_capa.py ebook capa.jpg
Impressa: python3 verifica_capa.py impressa --paginas 142 --papel branco|creme|cor [--corte 6x9] [--pdf capa-inteira.pdf]
          Sem --pdf, só calcula o tamanho que a capa inteira deve ter (lombada + sangria) e diz se cabe texto na lombada."""
import argparse, os, re, subprocess, sys
from PIL import Image

ESPESSURA = {'branco': 0.002252, 'creme': 0.0025, 'cor': 0.002347}   # pol. por página (KDP). "cor": papel colorido premium; confira o padrão
SANGRIA = 0.125

def ebook(f):
    ok = True; im = Image.open(f); w, h = im.size; mb = os.path.getsize(f) / 1e6; r = h / w
    print(f'\n=== CAPA DO E-BOOK {os.path.basename(f)}')
    def line(n, m):
        nonlocal ok
        if n == 'ERRO': ok = False
        print(f'[{n}] {m}')
    line('OK' if im.format in ('JPEG', 'TIFF') else 'ERRO', f'formato {im.format} (KDP aceita JPEG ou TIFF)')
    line('OK' if im.mode == 'RGB' else 'ERRO', f'cor {im.mode} (precisa ser RGB; CMYK é recusado)')
    line('OK' if (w, h) == (1600, 2560) else ('AVISO' if h >= 1000 and w >= 625 else 'ERRO'), f'{w} × {h} px (ideal 1600 × 2560; mínimo 625 × 1000)')
    line('OK' if abs(r - 1.6) < .01 else 'AVISO', f'proporção {r:.3f}:1 (ideal 1,6:1)')
    line('OK' if mb < 50 else 'ERRO', f'{mb:.1f} MB (limite 50 MB)')
    # bordas: capa clara precisa de contorno para não sumir na loja de fundo branco
    sm = im.convert('RGB').resize((80, 128)); px = sm.load()
    borda = [px[x, y] for x in range(80) for y in (0, 127)] + [px[x, y] for y in range(128) for x in (0, 79)]
    claro = sum(sum(c) / 3 > 235 for c in borda) / len(borda)
    if claro > .6: line('AVISO', 'mais de 60 % da borda é quase branca: na página branca da loja a capa perde o contorno; considere um fio fino ou um fundo levemente tingido')
    return ok

def impressa(a):
    cw, ch = (float(x) for x in a.corte.lower().split('x'))
    lomb = a.paginas * ESPESSURA[a.papel]
    W, H = SANGRIA + cw + lomb + cw + SANGRIA, ch + 2 * SANGRIA
    print(f'\n=== CAPA IMPRESSA · {a.paginas} páginas · papel {a.papel} · corte {cw:g} × {ch:g}')
    print(f'[INFO] lombada {lomb:.4f} pol. ({lomb * 25.4:.2f} mm)')
    print(f'[INFO] capa inteira {W:.4f} × {H:.4f} pol. = {round(W * 300)} × {round(H * 300)} px a 300 ppi (contracapa + lombada + capa, com 0,125 pol. de sangria)')
    print(f'[{"OK" if a.paginas >= 79 else "AVISO"}] texto na lombada: ' + ('cabe (KDP exige mais de 79 páginas e margem de 0,0625 pol. de cada lado do texto)' if a.paginas > 79 else 'não use texto na lombada com 79 páginas ou menos'))
    print('[INFO] área de segurança: texto e rostos a pelo menos 0,125 pol. do corte; a KDP põe o código de barras no canto inferior direito da contracapa (2 × 1,2 pol.), deixe livre')
    ok = True
    if a.pdf:
        info = subprocess.run(['pdfinfo', a.pdf], capture_output=True, text=True).stdout
        w, h = (float(x) / 72 for x in re.search(r'Page size:\s+([\d.]+) x ([\d.]+)', info).groups())
        n = int(re.search(r'Pages:\s+(\d+)', info).group(1))
        bate = abs(w - W) < .01 and abs(h - H) < .01
        print(f'[{"OK" if bate else "ERRO"}] PDF da capa {w:.4f} × {h:.4f} pol. (esperado {W:.4f} × {H:.4f})'); ok &= bate
        print(f'[{"OK" if n == 1 else "ERRO"}] {n} página(s) no PDF da capa (deve ser 1)'); ok &= n == 1
    return ok

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='tipo', required=True)
    e = sp.add_parser('ebook'); e.add_argument('arquivo')
    i = sp.add_parser('impressa'); i.add_argument('--paginas', type=int, required=True); i.add_argument('--papel', choices=list(ESPESSURA), default='branco')
    i.add_argument('--corte', default='6x9'); i.add_argument('--pdf')
    a = ap.parse_args()
    sys.exit(0 if (ebook(a.arquivo) if a.tipo == 'ebook' else impressa(a)) else 1)
