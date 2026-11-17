"""Uniformiza os desenhos gerados: corta bordas de folha/caderno e leva o tom do papel a um creme único.
Lê gen/<chave>.png e grava img/<chave>.jpg. Também recorta duas amostras de traço a partir de modelos do livro."""
import glob, os
import numpy as np
from PIL import Image
TARGET = np.array([246, 240, 226], float)
CROP = {k: .06 for k in 'a06 a07 l08 a03 a01 c06 p08 b01'.split()}
CROP.update({k: .05 for k in 'b04 b09 t09 t10 c07 c08 b12 st-b12-1 st-b12-2 st-b12-3 a05 st-a05-1 st-a05-2 st-a05-3 b13 fig-tons b05 b10'.split()})
def fix(im, crop=0):
    im = im.convert('RGB')
    if crop:
        w, h = im.size; dx, dy = int(w * crop), int(h * crop)
        im = im.crop((dx, dy, w - dx, h - dy))
    a = np.asarray(im, float)
    small = np.asarray(im.resize((90, 120)), float).reshape(-1, 3)
    paper = np.percentile(small, 85, axis=0)
    gain = np.clip(TARGET / paper, .88, 1.22)
    return Image.fromarray(np.clip(np.minimum(a * gain, TARGET + 2), 0, 255).astype('uint8'))
for f in sorted(glob.glob('gen/*.png')):
    k = os.path.basename(f)[:-4]
    fix(Image.open(f), CROP.get(k, 0)).save(f'img/{k}.jpg', quality=88, optimize=True)
# amostras recortadas de modelos (no lugar de duas amostras geradas)
t02 = Image.open('img/t02.jpg'); t02.crop((150, 330, 870, 870)).save('img/m02.jpg', quality=88)
c04 = Image.open('img/c04.jpg'); c04.crop((400, 270, 880, 630)).save('img/m08.jpg', quality=88)
print('ok')
