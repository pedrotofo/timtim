"""Folhas de contato do PDF: python3 tools/contato.py pdf pasta"""
import glob, subprocess, sys, os, shutil
from PIL import Image, ImageDraw
pdf, S = sys.argv[1], sys.argv[2]
shutil.rmtree(S, ignore_errors=True); os.makedirs(S)
subprocess.run(['pdftoppm', '-r', '40', '-png', pdf, f'{S}/p'], check=True)
fs = sorted(glob.glob(f'{S}/p-*.png'))
for b in range(0, len(fs), 18):
    ims = [Image.open(f) for f in fs[b:b + 18]]; w, h = ims[0].size
    c = Image.new('RGB', (6 * (w + 6), 3 * (h + 16)), '#777'); d = ImageDraw.Draw(c)
    for i, im in enumerate(ims):
        x, y = (i % 6) * (w + 6), (i // 6) * (h + 16); c.paste(im, (x, y)); d.text((x + 2, y + h + 2), str(b + i + 1), fill='white')
    c.save(f'{S}/sheet{b // 18:02d}.jpg', quality=80)
print(len(fs))
