"""Baixa imagens do OpenArt: python3 tools/fetch.py chave arquivo.png [chave arquivo.png ...]. Salva gen/<chave>.png e img/<chave>.jpg."""
import sys, subprocess, os
from PIL import Image
B = 'https://cdn.openart.ai/openart-ai/production/2026-11/create-image/MPlYjLbSAtvk0yvA505B/'
a = sys.argv[1:]
for k, f in zip(a[::2], a[1::2]):
    u = f if f.startswith('http') else B + f
    subprocess.run(['curl', '-sf', '-o', f'gen/{k}.png', u], check=True)
    Image.open(f'gen/{k}.png').convert('RGB').save(f'img/{k}.jpg', quality=90)
    open('tools/urls.txt', 'a').write(f'{k} {u}\n')
    print(k, 'ok')
