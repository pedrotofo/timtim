#!/usr/bin/env python3
"""clarear-crina.py — tira a crina do lobo-guará de preto chapado e a põe no marrom da arte pintada.

Item 13 do laudo do pente fino. A crina é o PONTO FRACO da luta da fase 2 e, pelo art bible, devia
ser o ponto claro do vilão — no sprite ela era a parte MAIS ESCURA, invisível como alvo.

Alvo medido no card pintado da fase 2 (assets/intro/fase2.jpg), que é a referência canônica: lá a
crina é marrom-escura e quente (v 0,46 contra 0,58 do corpo, razão 0,79), não preta. No sprite a
razão era 0,46.

COMO SEPARA: a crina é escura E quase sem cor; o corpo é laranja saturado e a boca aberta é
vermelha saturada, então o guarda de saturação já os poupa. O que a saturação NÃO separa são as
patas, também pretas — por isso a banda vertical: só os 55% de cima da caixa opaca DE CADA QUADRO
entram. Pata preta é do bicho e fica; crina preta é o defeito.

POR QUE GRADUAR E NÃO REGERAR: as seis tiras são 172 quadros tirados de vídeo. Regerar custa
crédito e, pelo design.md (24/11/2026), devolve quadros que variam entre si — a animação treme.

Rodar da raiz:  python3 tools/clarear-crina.py
Para refazer do original:  git checkout game/assets/anim/guara-*.webp game/assets/sprites/guara-*.png
"""
from PIL import Image
import numpy as np, pathlib, json, sys

HUE, LIFT, SAT, BANDA = 24 / 360.0, 1.6, 0.66, 0.55

def _hsv(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx, mn = rgb.max(-1), rgb.min(-1); d = np.maximum(mx - mn, 1e-6)
    h = np.select([mx == r, mx == g, mx == b],
                  [((g - b) / d) % 6, (b - r) / d + 2, (r - g) / d + 4], default=0.) / 6
    return h, np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-6), 0.), mx

def _rgb(h, s, v):
    i = h * 6.; f = i - np.floor(i)
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    idx = (np.floor(i).astype(np.int32) % 6)[..., None]
    opc = np.stack([np.stack([v, t, p], -1), np.stack([q, v, p], -1), np.stack([p, v, t], -1),
                    np.stack([p, q, v], -1), np.stack([t, p, v], -1), np.stack([v, p, q], -1)], 0)
    return np.take_along_axis(opc, idx[None, ...], 0)[0]

def clarear(a):
    """a: array HxWx4 float de UM quadro (a banda é relativa à caixa opaca dele)."""
    rgb, A = a[..., :3] / 255., a[..., 3]
    h, s, v = _hsv(rgb)
    sg = s * np.clip(v / 0.22, 0, 1)        # no quase-preto a saturação é ruído
    w = np.clip((0.44 - v) / 0.30, 0, 1) * np.clip((0.40 - sg) / 0.16, 0, 1) * (A / 255.)
    linhas = np.where((A > 128).any(1))[0]
    if len(linhas):
        y0, y1 = linhas[0], linhas[-1]
        fr = (np.arange(a.shape[0])[:, None] - y0) / max(y1 - y0, 1)
        w = w * np.clip((BANDA - fr) / 0.12, 0, 1)   # só a metade de cima: as patas pretas ficam
    v2 = v ** (1 / (1 + LIFT * w))          # curva, não soma: o preto chapado é que precisa subir
    s2 = np.clip(s + (SAT - s) * w * 0.9, 0, 0.78)
    dh = (HUE - h + 0.5) % 1 - 0.5
    out = np.clip(_rgb((h + dh * w) % 1, s2, np.clip(v2, 0, 1)), 0, 1)
    return np.concatenate([out * 255, A[..., None]], -1)

def razao(a):
    """crina/corpo por valor, medido nos 45% de cima contra o resto — para ter um número de antes e depois."""
    rgb, A = a[..., :3] / 255., a[..., 3]
    _, s, v = _hsv(rgb)
    op = A > 128
    escuro = op & (v < 0.40) & (s < 0.40)
    corpo = op & (v > 0.35) & (s > 0.55)
    if escuro.sum() < 20 or corpo.sum() < 20: return 0.
    return v[escuro].mean() / v[corpo].mean()

if __name__ == '__main__':
    raiz = pathlib.Path(__file__).resolve().parent.parent
    alvos = sorted((raiz / 'game/assets/anim').glob('guara-*.webp')) + \
            sorted((raiz / 'game/assets/sprites').glob('guara-*.png'))
    if not alvos: sys.exit('nenhum arquivo do lobo-guará encontrado')
    for p in alvos:
        im = Image.open(p).convert('RGBA')
        a = np.asarray(im).astype(np.float32)
        meta_p = p.with_suffix('.json')
        if meta_p.exists():                 # tira de animação: grade de quadros, um a um
            m = json.load(open(meta_p)); cw, ch = a.shape[1] // m['cols'], a.shape[0] // m['rows']
            antes = razao(a[:ch, :cw])
            for r in range(m['rows']):
                for c in range(m['cols']):
                    sl = (slice(r * ch, (r + 1) * ch), slice(c * cw, (c + 1) * cw))
                    if a[sl][..., 3].max() < 128: continue
                    a[sl] = clarear(a[sl])
            depois = razao(a[:ch, :cw])
        else:
            antes = razao(a); a = clarear(a); depois = razao(a)
        out = Image.fromarray(a.astype(np.uint8), 'RGBA')
        if p.suffix == '.webp': out.save(p, 'WEBP', quality=90, method=5)
        else: out.save(p, 'PNG', optimize=True)
        print(f'{p.relative_to(raiz)}: crina/corpo {antes:.2f} -> {depois:.2f}  ({p.stat().st_size // 1024} KB)')
    print('alvo do card pintado da fase 2: 0,79')
