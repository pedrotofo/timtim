"""Copia obras/<chave>.jpg (ou obras/hd) para img/<chave>.jpg, com recorte de molduras e no máximo 1800 px."""
import os, sys
sys.path.insert(0, 'tools')
from PIL import Image
from obras import OBRAS
Image.MAX_IMAGE_PIXELS = None
# recorte (x0, y0, x1, y1) em frações
CROP = {'n3_ideal': (0, 0, .865, .975), 'n3_sleeping': (.055, .04, .935, .95), 'n5_crau': (0, .02, 1, .935),
        'n1_cats': (.03, .02, .97, .98), 'n5_rembrandt_land': (0, 0, .86, 1)}
for k in OBRAS:
    p = f'obras/hd/{k}.jpg' if os.path.exists(f'obras/hd/{k}.jpg') else f'obras/{k}.jpg'
    im = Image.open(p).convert('RGB')
    if k in CROP:
        x0, y0, x1, y1 = CROP[k]; w, h = im.size
        im = im.crop((round(x0 * w), round(y0 * h), round(x1 * w), round(y1 * h)))
    im.thumbnail((1800, 1800), Image.LANCZOS)
    im.save(f'img/{k}.jpg', quality=88, optimize=True)
print(len(OBRAS))
