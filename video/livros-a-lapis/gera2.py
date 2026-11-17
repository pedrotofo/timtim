"""Vídeo v3: renderiza cena2.html com motion blur (4 subquadros, obturador de 180°) nos trechos rápidos, som e MP4s."""
import json, os, shutil, subprocess, wave
import numpy as np
from PIL import Image
D, FPS, SR = 10, 30, 48000
FAST = [(0, .75), (2.0, 2.7), (4.0, 4.7), (5.35, 6.05), (6.1, 7.6), (7.9, 8.95)]
jobs = []
for i in range(D * FPS):
    t = i / FPS
    subs = [t + k / (FPS * 8) for k in range(4)] if any(a <= t <= b for a, b in FAST) else [t]
    jobs += [[f'{i:04d}_{k}', s] for k, s in enumerate(subs)]
json.dump(jobs, open('jobs.json', 'w'))
js = """const { chromium } = require('playwright'); const path = require('path'), fs = require('fs');
const jobs = JSON.parse(fs.readFileSync('jobs.json')); fs.rmSync('sub', { recursive: true, force: true }); fs.mkdirSync('sub');
(async () => { const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  pg.on('pageerror', e => { console.error('ERRO', e.message); process.exitCode = 1; });
  await pg.goto('file://' + path.resolve('cena2.html')); await pg.evaluate(() => document.fonts.ready);
  const t0 = Date.now();
  for (let n = 0; n < jobs.length; n++) { const [name, t] = jobs[n]; await pg.evaluate(t => render(t), t);
    await pg.waitForFunction(() => [...document.images].every(im => im.complete && im.naturalWidth), null, { timeout: 15000 });
    await pg.screenshot({ path: 'sub/' + name + '.png' });
    if (n % 150 === 0) console.log(n + '/' + jobs.length, ((Date.now() - t0) / (n + 1)).toFixed(0) + ' ms'); }
  await b.close(); })();"""
open('render_sub.js', 'w').write(js); subprocess.run(['node', 'render_sub.js'], check=True)
shutil.rmtree('quadros3', ignore_errors=True); os.makedirs('quadros3')
for i in range(D * FPS):
    fs = sorted(f for f in os.listdir('sub') if f.startswith(f'{i:04d}_'))
    acc = sum(np.asarray(Image.open('sub/' + f).convert('RGB'), np.float32) for f in fs) / len(fs)
    Image.fromarray(acc.round().astype(np.uint8)).save(f'quadros3/{i:04d}.png')
# som
out = np.zeros(SR * D); rng = np.random.default_rng(3)
def env(n, a, d): t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t / d)
def put(t, s): i = int(t * SR); out[i:i + len(s)] += s[:max(0, len(out) - i)]
def tick(f, vol=.35, d=.09):
    n = int(SR * .35); t = np.arange(n) / SR
    return (np.sin(2*np.pi*f*t) + .35*np.sin(2*np.pi*f*2.01*t) + .12*np.sin(2*np.pi*f*3.02*t)) * env(n, .002, d) * vol
def papel(vol=.22, dur=.42):
    n = int(SR * dur); r = rng.standard_normal(n); r = np.convolve(r, np.ones(6) / 6, 'same') - np.convolve(r, np.ones(60) / 60, 'same')
    return r * np.sin(np.linspace(0, np.pi, n)) ** 1.5 * vol
def sopro(vol=.16, dur=.6, up=True):
    n = int(SR * dur); r = np.convolve(rng.standard_normal(n), np.ones(160) / 160, 'same'); e = np.linspace(0, 1, n) ** 2 if up else np.sin(np.linspace(0, np.pi, n))
    return r * e * vol * 7
def baque(vol=.5):
    n = int(SR * .35); t = np.arange(n) / SR; f = 110 * np.exp(-t * 6); return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .003, .09) * vol
put(0.0, sopro(.14, .55)); put(0.5, baque(.45))
for t in (2.05, 4.05): put(t, sopro(.16, .3, True))
for k, t in enumerate((2.335, 4.335)): put(t, tick(660 * 2 ** (k * 2 / 12)))
put(5.35, papel(.24, .55)); put(6.1, papel(.22, .55))
for t in (6.82, 7.007, 7.17, 7.31): put(t + .04, papel(.16, .26))
put(8.2, baque(.3)); put(8.32, sopro(.1, .45, False))
for k, f in enumerate([1046.5, 1318.5, 1568.0]): put(8.72 + k * .07, tick(f, .26, .35))
out = out / np.max(np.abs(out)) * .7
w = wave.open('sfx3.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype(np.int16).tobytes()); w.close()
v = ['-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-movflags', '+faststart']
fr = ['-framerate', '30', '-i', 'quadros3/%04d.png']
subprocess.run(['ffmpeg', '-v', 'error', '-y', *fr, '-i', 'sfx3.wav', *v, '-c:a', 'aac', '-b:a', '192k', '-shortest', 'livros-a-lapis-v3-9x16.mp4'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', *fr, *v, 'livros-a-lapis-v3-9x16-sem-som.mp4'], check=True)
print('pronto')
