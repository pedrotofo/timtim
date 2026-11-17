"""Tira a mancha de tinta da chapa (fora do desenho) no Autorretrato de boné, de boca aberta, para uso na capa.
Correção multiplicativa: divide pelo tom local borrado e multiplica pelo tom do papel; as linhas finas que passam por ela continuam."""
import numpy as np
from PIL import Image, ImageFilter
im = Image.open('obras/sp_wide.jpg').convert('RGB'); w, h = im.size
x0, x1, y0, y1 = int(.05 * w), int(.25 * w), int(.52 * h), int(.74 * h)
reg = im.crop((x0, y0, x1, y1))
a = np.asarray(reg, float)
paper = np.array([200., 178., 152.])
# o tom local ignora as linhas: filtro de máximo antes do borrão
base = reg.filter(ImageFilter.MedianFilter(11)).filter(ImageFilter.GaussianBlur(5))
b = np.asarray(base, float)
lum_p = paper.mean() * .985
ratio = np.repeat(np.clip(lum_p / np.maximum(b.mean(axis=2, keepdims=True), 1), 1, 1.6), 3, axis=2)
dark = (ratio.mean(axis=2) - 1.005) / .04
mask = np.asarray(Image.fromarray((np.clip(dark, 0, 1) * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(9)), float)[..., None] / 255
yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
edge = np.minimum.reduce([xx, yy, a.shape[1] - 1 - xx, a.shape[0] - 1 - yy]) / 40
mask = mask * np.clip(edge, 0, 1)[..., None]
hf = a.mean(axis=2, keepdims=True) - b.mean(axis=2, keepdims=True)   # linhas e grão, sem a cor da mancha
fixed = paper + hf
out = np.clip(a * (1 - mask) + fixed * mask, 0, 255).astype('uint8')
im.paste(Image.fromarray(out), (x0, y0))
im.save('img/capa-gravura.jpg', quality=94)
im.crop((0, int(.45 * h), int(.4 * w), int(.85 * h))).resize((380, 440)).save('/tmp/claude-0/-home-user-Tofo/70760256-9ae2-520c-b722-f901ba0ead4c/scratchpad/stain2.jpg')
print('ok')
# só a chapa, com uma margem fina de papel
w2, h2 = im.size
im.crop((int(.012 * w2), int(.008 * h2), int(.988 * w2), int(.992 * h2))).save('img/capa-gravura.jpg', quality=94)
