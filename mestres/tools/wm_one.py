"""Baixa um arquivo do Commons pela miniatura padrão: python3 tools/wm_one.py Arquivo.jpg saida.jpg [larguras...]"""
import sys, hashlib, subprocess, urllib.parse, time
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
UA = 'drawing-book-builder/1.0 (educational use)'
f, out = sys.argv[1], sys.argv[2]
ws = [int(x) for x in sys.argv[3:]] or [1920, 1280, 960]
h = hashlib.md5(f.encode()).hexdigest(); q = urllib.parse.quote(f)
ext = '.jpg' if f.lower().endswith(('.tif', '.tiff')) else ('.png' if f.lower().endswith('.png') else '')
for w in ws:
    u = f'https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{q}/{w}px-{q}{ext}'
    r = subprocess.run(['curl', '-s', '-m', '90', '-A', UA, '-o', out + '.tmp', '-w', '%{http_code}', u], capture_output=True, text=True)
    if r.stdout == '200':
        try:
            im = Image.open(out + '.tmp').convert('RGB'); im.save(out, quality=92); print(out, w, im.size); break
        except Exception as e:
            print('erro', e)
    time.sleep(4)
else:
    print(out, 'FALHOU', r.stdout)
subprocess.run(['rm', '-f', out + '.tmp'])
