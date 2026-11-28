#!/usr/bin/env python3
"""grade-furtao.py — põe o Furtão na cor que o fato não-negociável manda: marrom, nunca cinza-azulado.

Item 13 do laudo do pente fino (docs/laudo-pente-fino.md). Vale para as cinco tiras de animação
(game/assets/anim/furtao-*.webp) e as seis poses paradas (game/assets/sprites/brute-*.png).

POR QUE GRADUAR E NÃO REGERAR: as tiras saíram de vídeo do Google Flow — são 149 quadros contínuos.
O design.md (24/11/2026) é explícito: quadros desenhados um a um pela IA variam entre si e a
animação treme; os de vídeo são contínuos. Regerar custaria crédito e devolveria uma animação pior.
Medido no arquivo, o pelo nem era azul: era marrom lavado (R 0,345 G 0,299 B 0,269, saturação 0,24).
Lido sob a névoa azul da fase 1, isso vira cinza. A conta é de saturação e matiz, não de desenho.

Alvo tirado da própria abertura pintada (assets/intro/2-roubo.jpg), que é a referência que o
design.md cita: R/B 2,03, saturação 0,56.

Rodar da raiz do repositório:  python3 tools/grade-furtao.py
É idempotente no sentido prático (já graduado, quase não mexe), mas o certo é rodar sobre o original:
git checkout game/assets/anim/furtao-*.webp game/assets/sprites/brute-*.png
"""
from PIL import Image
import numpy as np, pathlib, sys

HUE_ALVO = 22.0 / 360.0     # o marrom quente da abertura pintada
HUE_K, SAT_TETO = 1.0, 0.70
ALVO_RB = 2.05               # R/B que todas as poses têm de atingir (a abertura pintada mede 2,03)

def grade(img, SAT_K):
    a = np.asarray(img.convert('RGBA')).astype(np.float32)
    rgb, A = a[..., :3] / 255.0, a[..., 3]
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx, mn = rgb.max(-1), rgb.min(-1)
    v = mx
    s = np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-6), 0.0)
    d = np.maximum(mx - mn, 1e-6)
    h = np.select([mx == r, mx == g, mx == b],
                  [((g - b) / d) % 6, (b - r) / d + 2, (r - g) / d + 4], default=0.0) / 6.0
    # peso: pega o pelo (meio-tom), poupa o couro escuro da coleira e o focinho/peito claros
    w = np.clip((v - 0.10) / 0.10, 0, 1) * np.clip((0.86 - v) / 0.14, 0, 1)
    # poupa o metal dos espinhos (cinza puro E claro); as listras lavadas do pelo continuam entrando,
    # senão ficam cinza contra o marrom e leem como uma faixa lilás no lombo
    w = w * np.clip((s - 0.035) / 0.06, 0, 1) * (1 - np.clip((0.12 - s) / 0.12, 0, 1) * np.clip((v - 0.42) / 0.12, 0, 1))
    w = w * (A / 255.0)
    dh = (HUE_ALVO - h + 0.5) % 1.0 - 0.5
    h2 = (h + dh * HUE_K * w) % 1.0
    s2 = np.clip(s * (1 + (SAT_K - 1) * w), 0, SAT_TETO)
    i = h2 * 6.0; f = i - np.floor(i)
    p, q, t = v * (1 - s2), v * (1 - s2 * f), v * (1 - s2 * (1 - f))
    idx = (np.floor(i).astype(np.int32) % 6)[..., None]
    opc = np.stack([np.stack([v, t, p], -1), np.stack([q, v, p], -1), np.stack([p, v, t], -1),
                    np.stack([p, q, v], -1), np.stack([t, p, v], -1), np.stack([v, p, q], -1)], 0)
    out = np.take_along_axis(opc, idx[None, ...], 0)[0]
    return Image.fromarray(np.concatenate([np.clip(out, 0, 1) * 255.0, A[..., None]], -1).astype(np.uint8), 'RGBA')

def razao(img):
    a = np.asarray(img.convert('RGBA')).astype(np.float32)
    rgb, A = a[..., :3] / 255.0, a[..., 3]
    v = rgb.max(-1); sel = (A > 128) & (v > 0.2) & (v < 0.6)
    if sel.sum() == 0: return 0.0
    return rgb[..., 0][sel].mean() / max(rgb[..., 2][sel].mean(), 1e-6)

if __name__ == '__main__':
    raiz = pathlib.Path(__file__).resolve().parent.parent
    alvos = sorted((raiz / 'game/assets/anim').glob('furtao-*.webp')) + \
            sorted((raiz / 'game/assets/sprites').glob('brute-*.png'))
    if not alvos: sys.exit('nenhum arquivo do Furtão encontrado')
    for p in alvos:
        im = Image.open(p); antes = razao(im)
        # cada folha saiu de um vídeo com a sua própria luz, então uma força fixa deixava o Furtão entre
        # R/B 2,01 e 2,58 conforme a pose — ele mudava de tom ao trocar de pose. A força é calibrada por
        # arquivo, por busca binária, para todas as poses chegarem no mesmo marrom.
        lo, hi = 1.0, 6.0
        for _ in range(22):
            mid = (lo + hi) / 2
            if razao(grade(im, mid)) < ALVO_RB: lo = mid
            else: hi = mid
        out = grade(im, (lo + hi) / 2); depois = razao(out)
        if p.suffix == '.webp': out.save(p, 'WEBP', quality=90, method=5)
        else: out.save(p, 'PNG', optimize=True)
        print(f'{p.relative_to(raiz)}: R/B {antes:.2f} -> {depois:.2f}  (força {(lo + hi) / 2:.2f}, {p.stat().st_size // 1024} KB)')
    print('alvo da abertura pintada: R/B 2,03')
