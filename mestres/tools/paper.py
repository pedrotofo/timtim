"""Uniformiza os desenhos gerados: corta bordas de folha/caderno e leva o tom do papel a um creme único.
Lê gen/<chave>.png e grava img/<chave>.jpg. Modelos em papel cinza (TONED) só têm as bordas cortadas."""
import glob, os
import numpy as np
from PIL import Image
TARGET = np.array([246, 240, 226], float)
CROP = {'s02': .07, 'f02': .055, 's05': .05, 'l01': .05, 's01': .05, 'f05': .04}
TONED = {'s02'}      # papel cinza: não clarear
def fix(im, crop=.035, toned=False):
    im = im.convert('RGB')
    if crop:
        w, h = im.size; dx, dy = int(w * crop), int(h * crop)
        im = im.crop((dx, dy, w - dx, h - dy))
    if toned:
        return im
    a = np.asarray(im, float)
    small = np.asarray(im.resize((90, 120)), float).reshape(-1, 3)
    paper = np.percentile(small, 85, axis=0)
    gain = np.clip(TARGET / paper, .88, 1.22)
    return Image.fromarray(np.clip(np.minimum(a * gain, TARGET + 2), 0, 255).astype('uint8'))
for f in sorted(glob.glob('gen/*.png')):
    k = os.path.basename(f)[:-4]
    fix(Image.open(f), CROP.get(k, .035), k in TONED).save(f'img/{k}.jpg', quality=88, optimize=True)
print('ok')
