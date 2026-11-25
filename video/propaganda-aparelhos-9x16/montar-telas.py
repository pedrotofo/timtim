# Monta tela1/2/3.mp4 (as tomadas em tempo real, 30 fps) e fundo.mp4 (a luta com o lobo-guará, desfocada, 18 s)
import os, sys, subprocess, glob
D = os.path.dirname(os.path.abspath(__file__)); OUT = sys.argv[1]
ALT = os.path.join(D, '..', 'rec', 'clips')  # tomadas antigas, só para a prévia enquanto as novas gravam
def pasta(nome, alt):
    p = os.path.join(D, 'clips', nome)
    return p if len(glob.glob(p + '/*.jpg')) >= 120 else os.path.join(ALT, alt)
ff = lambda *a: subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *a], check=True)
enc = ['-c:v', 'libx264', '-crf', '19', '-pix_fmt', 'yuv420p', '-g', '15', '-movflags', '+faststart']
for n, (nome, alt, ini) in enumerate([('parque', 'corre', 35), ('arraial', 'planar', 0), ('resgate', 'vitoria', 0)], 1):
    ff('-framerate', '30', '-start_number', str(ini), '-i', pasta(nome, alt) + '/%03d.jpg', '-vf', 'scale=1344:756:flags=lanczos', *enc, os.path.join(OUT, f'tela{n}.mp4'))
# fundo: vai e volta (sem salto no laço), 18 s, desfocado e mais saturado
lobo = pasta('lobo', 'lobo-luta')
ff('-framerate', '30', '-i', lobo + '/%03d.jpg', '-filter_complex',
   '[0]scale=640:360,split[a][b];[b]reverse[r];[a][r]concat=n=2:v=1[c];[c]loop=loop=4:size=9999,trim=duration=18,setpts=PTS-STARTPTS,boxblur=18:2,eq=brightness=-0.05:saturation=1.3[o]',
   '-map', '[o]', '-r', '30', *enc, os.path.join(OUT, 'fundo.mp4'))
print('ok')
