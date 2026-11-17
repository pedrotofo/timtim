#!/usr/bin/env python3
"""Monta o vídeo interface-escura-3d a partir de um projeto JSON (veja SKILL.md).
Uso: python3 build.py projeto.json [--preview 1.0,4.5,9.0]   (--preview só gera PNGs desses instantes, sem vídeo)"""
import json, os, sys, shutil, subprocess, wave
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); SKILL = os.path.dirname(HERE)
cfg_path = os.path.abspath(sys.argv[1]); BASE = os.path.dirname(cfg_path)
P = json.load(open(cfg_path)); FPS = 30
WORK = os.path.join(BASE, P.get('work', 'interface-escura-3d-work')); os.makedirs(WORK, exist_ok=True)
src = lambda p: p if os.path.isabs(p) else os.path.join(BASE, p)
run = lambda *c: subprocess.run(list(c), check=True)

# 1) quadros de cada ato: trecho de vídeo (video + from) ou imagens (images: uma ou mais, divididas igualmente no tempo do ato)
acts = []
for i, a in enumerate(P['acts']):
    d = os.path.join(WORK, 'frames', f'ato{i+1}'); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    dur = a['end'] - a['start']; n = max(1, round(dur * FPS))
    if 'video' in a:
        run('ffmpeg', '-v', 'error', '-y', '-ss', str(a.get('from', 0)), '-i', src(a['video']), '-t', f'{dur + 0.2:.3f}',
            '-vf', 'fps=30,scale=1280:-2', '-q:v', '3', '-start_number', '0', os.path.join(d, '%05d.jpg'))
        count = len(os.listdir(d))
    else:
        imgs = [src(x) for x in a['images']]
        conv = []
        for j, im in enumerate(imgs):  # converte cada imagem uma vez
            o = os.path.join(d, f'img{j}.jpg'); run('ffmpeg', '-v', 'error', '-y', '-i', im, '-vf', 'scale=1280:-2', '-q:v', '3', o); conv.append(o)
        for k in range(n):  # cada imagem ocupa uma fatia igual do ato
            shutil.copy(conv[min(len(conv) - 1, k * len(conv) // n)], os.path.join(d, f'{k:05d}.jpg'))
        count = n
    th = os.path.join(WORK, f'thumb{i+1}' + os.path.splitext(a['thumb'])[1]); shutil.copy(src(a['thumb']), th)
    acts.append({ 'name': a['name'], 'thumb': os.path.basename(th), 'start': a['start'], 'end': a['end'], 'frames': f'frames/ato{i+1}', 'count': count,
                  'fit': a.get('fit', 'cover'), 'zoom': a.get('zoom', [1, 1] if 'video' in a else [1.0, 1.06]) })
page = { 'title': P['title'], 'button': P.get('button', 'Abrir'), 'toast': P['toast'], 'duration': P['duration'], 'final': P['final'], 'acts': acts }
if 'camera' in P: page['camera'] = P['camera']
open(os.path.join(WORK, 'config.js'), 'w').write('window.CFG = ' + json.dumps(page, ensure_ascii=False) + ';\n')
shutil.copy(os.path.join(SKILL, 'template', 'anim.html'), os.path.join(WORK, 'anim.html'))

# prévia: só alguns instantes, para aprovar antes de renderizar tudo
if '--preview' in sys.argv:
    times = sys.argv[sys.argv.index('--preview') + 1]
    js = f"""const {{ chromium }} = require('playwright'); (async () => {{ const b = await chromium.launch(); const pg = await b.newPage({{ viewport: {{ width: 1080, height: 1920 }} }});
      await pg.goto('file://{WORK}/anim.html'); await pg.evaluate(() => document.fonts.ready);
      for (const t of [{times}]) {{ await pg.evaluate(t => render(t), t); await pg.waitForFunction(() => [...document.images].every(im => im.complete && im.naturalWidth)); await pg.waitForTimeout(150);
        await pg.screenshot({{ path: '{BASE}/previa-' + t + 's.png' }}); }} await b.close(); }})();"""
    open(os.path.join(WORK, 'preview.js'), 'w').write(js); run('node', os.path.join(WORK, 'preview.js')); print('prévias salvas em', BASE); sys.exit()

# 2) render quadro a quadro
run('node', os.path.join(HERE, 'render.js'), WORK, str(P['duration']))

# 3) efeitos de interface: clique no botão, "tique" subindo de tom a cada ✓ e um arpejo no fechamento
SR = 48000; out = np.zeros(int(SR * P['duration']))
def env(n, a, d): t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t / d)
def put(t, s): i = int(t * SR); out[i:i + len(s)] += s[:max(0, len(out) - i)]
def tick(f, vol=.35, d=.09):
    n = int(SR * .35); t = np.arange(n) / SR
    s = (np.sin(2*np.pi*f*t) + .35*np.sin(2*np.pi*f*2.01*t) + .12*np.sin(2*np.pi*f*3.02*t)) * env(n, .002, d)
    c = np.random.default_rng(1).standard_normal(int(SR*.006)) * np.linspace(1, 0, int(SR*.006)) * .25; s[:len(c)] += c; return s * vol
r = np.random.default_rng(2).standard_normal(int(SR*.05)); put(0.64, np.convolve(r, np.ones(12)/12, 'same') * np.exp(-np.arange(len(r))/SR/.008) * .5)
for k, a in enumerate(P['acts'][1:]): put(a['start'], tick(660 * 2 ** (k * 2 / 12)))
for k, f in enumerate([1046.5, 1318.5, 1568.0]): put(P['final'] + k * .07, tick(f, .26, .35))
out = out / np.max(np.abs(out)) * .7
w = wave.open(os.path.join(WORK, 'sfx.wav'), 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype(np.int16).tobytes()); w.close()

# 4) vídeo final: com os efeitos e uma cópia sem som (H.264, yuv420p, bt709, pronto para Reels/TikTok)
name = os.path.join(BASE, P.get('out', 'apresentacao-9x16'))
v = ['-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-color_range', 'tv', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-movflags', '+faststart']
frames = ['-framerate', '30', '-i', os.path.join(WORK, 'vframes', '%04d.png')]
run('ffmpeg', '-v', 'error', '-y', *frames, '-i', os.path.join(WORK, 'sfx.wav'), *v, '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', name + '.mp4')
run('ffmpeg', '-v', 'error', '-y', *frames, *v, name + '-sem-som.mp4')
print('pronto:', name + '.mp4', 'e', name + '-sem-som.mp4')
