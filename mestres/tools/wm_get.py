"""Baixa as obras de selecao.json em obras/<chave>.jpg pelas miniaturas padrão do Wikimedia (1920 px, ou 1280 px)."""
import json, os, time, hashlib, subprocess, urllib.parse
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
UA = 'drawing-book-builder/1.0 (educational use)'
S = json.load(open('tools/selecao.json'))
for k, f in S.items():
    out = f'obras/{k}.jpg'
    if os.path.exists(out):
        continue
    h = hashlib.md5(f.encode()).hexdigest(); q = urllib.parse.quote(f)
    ext = '.jpg' if f.lower().endswith(('.tif', '.tiff')) else ''
    ok = False
    for w in (1920, 1280, 960):
        u = f'https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{q}/{w}px-{q}{ext}'
        r = subprocess.run(['curl', '-s', '-m', '60', '-A', UA, '-o', '/tmp/wm.tmp', '-w', '%{http_code}', u], capture_output=True, text=True)
        if r.stdout == '200':
            try:
                im = Image.open('/tmp/wm.tmp').convert('RGB'); im.save(out, quality=92); print(k, w, im.size, flush=True); ok = True; break
            except Exception as e:
                print(k, 'img erro', e)
        time.sleep(1)
    if not ok:
        print(k, 'FALHOU', r.stdout, flush=True)
    time.sleep(1)
