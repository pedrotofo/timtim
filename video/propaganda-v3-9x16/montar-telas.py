# Monta as telas dos aparelhos, o mapa e o fundo desfocado (18 s) a partir das tomadas em tempo real.
import os, sys, subprocess, shutil
V3 = os.path.dirname(os.path.abspath(__file__)); V2 = os.path.join(V3, '..', 'v2', 'clips'); OUT = sys.argv[1]
ARTE = '/home/user/timtim/game/assets/capa.jpg'
ff = lambda *a: subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *a], check=True)
enc = ['-c:v', 'libx264', '-crf', '19', '-pix_fmt', 'yuv420p', '-g', '15', '-movflags', '+faststart', '-r', '30']
def tomada(pasta, ini, n, saida, vf):
    tmp = os.path.join(V3, '_seq'); shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    for i in range(n): os.symlink(os.path.join(pasta, '%03d.jpg' % (ini + i)), os.path.join(tmp, '%04d.jpg' % i))
    ff('-framerate', '30', '-i', tmp + '/%04d.jpg', '-vf', vf, *enc, saida)
tela = 'scale=1280:720:flags=lanczos'
tomada(os.path.join(V2, 'parque'), 55, 150, os.path.join(OUT, 'tela1.mp4'), tela)
tomada(os.path.join(V2, 'arraial'), 0, 160, os.path.join(OUT, 'tela2.mp4'), tela)
tomada(os.path.join(V3, 'clips', 'toldos'), 8, 142, os.path.join(OUT, 'tela3.mp4'), tela)
tomada(os.path.join(V3, 'm', 'clips', 'mapa'), 20, 80, os.path.join(OUT, 'mapa.mp4'), 'scale=1280:720:flags=neighbor')
# fundo: capa (0–2,6 s) → luta com o Furtão (até 7,0) → lobo-guará (até 12,1) → girassóis (até 16,2) → mapa (até 18)
seg = os.path.join(V3, '_fundo'); shutil.rmtree(seg, ignore_errors=True); os.makedirs(seg)
blur = 'scale=640:360,boxblur=16:2,eq=brightness=-0.04:saturation=1.3,setsar=1'
ff('-loop', '1', '-i', ARTE, '-t', '2.6', '-vf', 'scale=1280:720,zoompan=z=\'1+0.0015*on\':d=78:s=640x360:fps=30,boxblur=16:2,eq=brightness=-0.04:saturation=1.3,setsar=1', *enc, seg + '/0.mp4')
tomada(os.path.join(V2, 'resgate'), 0, 132, seg + '/1.mp4', blur)
tomada(os.path.join(V2, 'lobo'), 0, 153, seg + '/2.mp4', blur)
tomada(os.path.join(V3, 'clips', 'girassois'), 0, 123, seg + '/3.mp4', blur)
tomada(os.path.join(V3, 'm', 'clips', 'mapa'), 0, 54, seg + '/4.mp4', blur)
with open(seg + '/lista.txt', 'w') as f: f.write(''.join(f"file '{seg}/{i}.mp4'\n" for i in range(5)))
ff('-f', 'concat', '-safe', '0', '-i', seg + '/lista.txt', *enc, os.path.join(OUT, 'fundo.mp4'))
print('ok')
