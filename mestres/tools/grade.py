"""Folha com obras e grade de décimos: python3 tools/grade.py saida.jpg chave [chave...]"""
import sys
from PIL import Image, ImageDraw
ks = sys.argv[2:]; H = 700
ims = []
for k in ks:
    im = Image.open(f'obras/{k}.jpg').convert('RGB'); im.thumbnail((900, H)); d = ImageDraw.Draw(im)
    for i in range(1, 10):
        x = im.width * i / 10; y = im.height * i / 10
        d.line([(x, 0), (x, im.height)], fill=(255, 0, 0) if i == 5 else (0, 160, 255), width=1)
        d.line([(0, y), (im.width, y)], fill=(255, 0, 0) if i == 5 else (0, 160, 255), width=1)
        d.text((x + 2, 2), str(i), fill='red'); d.text((2, y + 2), str(i), fill='red')
    d.text((5, im.height - 14), k, fill='red'); ims.append(im)
W = sum(i.width for i in ims) + 10 * len(ims)
c = Image.new('RGB', (W, H), 'white'); x = 0
for i in ims: c.paste(i, (x, 0)); x += i.width + 10
c.save(sys.argv[1], quality=85)
