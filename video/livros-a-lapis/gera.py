"""Gera o vídeo 9:16 de 10 s a partir de cena.html: quadros, efeitos de som e os dois MP4 (com e sem som)."""
import os, subprocess, wave, numpy as np
D, FPS, SR = 10, 30, 48000
js = """const { chromium } = require('playwright'); const path = require('path'), fs = require('fs');
fs.rmSync('quadros', { recursive: true, force: true }); fs.mkdirSync('quadros');
(async () => { const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  pg.on('pageerror', e => { console.error('ERRO', e.message); process.exitCode = 1; });
  await pg.goto('file://' + path.resolve('cena.html')); await pg.evaluate(() => document.fonts.ready);
  for (let i = 0; i < %d; i++) { await pg.evaluate(t => render(t), i / 30);
    await pg.waitForFunction(() => [...document.images].every(im => im.complete && im.naturalWidth), null, { timeout: 15000 });
    await pg.screenshot({ path: 'quadros/' + String(i).padStart(4, '0') + '.png' }); }
  await b.close(); })();""" % (D * FPS)
open('render_cena.js', 'w').write(js); subprocess.run(['node', 'render_cena.js'], check=True)
out = np.zeros(SR * D); rng = np.random.default_rng(3)
def env(n, a, d): t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t / d)
def put(t, s): i = int(t * SR); out[i:i + len(s)] += s[:max(0, len(out) - i)]
def tick(f, vol=.35, d=.09):
    n = int(SR * .35); t = np.arange(n) / SR
    return (np.sin(2*np.pi*f*t) + .35*np.sin(2*np.pi*f*2.01*t) + .12*np.sin(2*np.pi*f*3.02*t)) * env(n, .002, d) * vol
def folha(vol=.22, dur=.45):  # farfalhar de papel: ruído filtrado com envelope em arco
    n = int(SR * dur); r = rng.standard_normal(n); r = np.convolve(r, np.ones(6) / 6, 'same') - np.convolve(r, np.ones(60) / 60, 'same')
    return r * np.sin(np.linspace(0, np.pi, n)) ** 1.5 * vol
def sopro(vol=.18, dur=.8):
    n = int(SR * dur); r = np.convolve(rng.standard_normal(n), np.ones(200) / 200, 'same'); return r * np.sin(np.linspace(0, np.pi, n)) * vol * 6
put(0.05, sopro())
for k, t in enumerate([3.0, 5.8]): put(t, tick(660 * 2 ** (k * 2 / 12))); put(t, sopro(.12, .6))
for t in [6.75, 7.55, 8.25, 8.95]: put(t + .05, folha())
for k, f in enumerate([1046.5, 1318.5, 1568.0]): put(9.55 + k * .07, tick(f, .26, .35))
out = out / np.max(np.abs(out)) * .7
w = wave.open('sfx.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype(np.int16).tobytes()); w.close()
v = ['-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-movflags', '+faststart']
fr = ['-framerate', '30', '-i', 'quadros/%04d.png']
subprocess.run(['ffmpeg', '-v', 'error', '-y', *fr, '-i', 'sfx.wav', *v, '-c:a', 'aac', '-b:a', '192k', '-shortest', 'livros-a-lapis-v2-9x16.mp4'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', *fr, *v, 'livros-a-lapis-v2-9x16-sem-som.mp4'], check=True)
print('pronto')
