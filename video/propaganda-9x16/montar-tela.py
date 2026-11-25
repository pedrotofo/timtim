# Monta tela.mp4 (13 s, 30 fps) e fundo.mp4 (desfocado) a partir dos quadros gravados
import os, sys, subprocess, shutil
D = os.path.dirname(os.path.abspath(__file__))  # clips/ (do gravar-jogo.js) fica ao lado; uso: python3 montar-tela.py assets
OUT = sys.argv[1]
# (clipe, primeiro quadro, quantos quadros)
CORTES = [
  ('roubo', 4, 54),      # 0,00–1,80  Furtão foge com o macaco
  ('corre', 4, 29),      # 1,80–2,77  corrida e pulo duplo
  ('fareja', 6, 27),     # 2,77–3,67  faro
  ('furtao', 2, 28),     # 3,67–4,60  luta com o Furtão
  ('planar', 8, 30),     # 4,60–5,60  planada com a bandana
  ('arquente', 6, 30),   # 5,60–6,60  ar quente da fogueira
  ('lobo-caca', 22, 30), # 6,60–7,60  entrada do lobo-guará
  ('lobo-luta', 0, 66),  # 7,60–9,80  luta com o lobo-guará
  ('arquente', 30, 24),  # 9,80–10,60
  ('vitoria', 14, 72),    # 10,60–13,00 macaco resgatado
]
seq = os.path.join(D, 'seq'); shutil.rmtree(seq, ignore_errors=True); os.makedirs(seq)
n = 0
for nome, a, q in CORTES:
    pasta = os.path.join(D, 'clips', nome)
    have = sorted(os.listdir(pasta)) if os.path.isdir(pasta) else []
    if len(have) < a + q: print('faltando', nome, len(have)); pasta = os.path.join(D, 'clips', 'roubo'); have = sorted(os.listdir(pasta)); a = 0
    for i in range(q):
        f = have[min(a + i, len(have) - 1)]
        os.symlink(os.path.join(pasta, f), os.path.join(seq, '%04d.jpg' % n)); n += 1
print('quadros', n)
ff = ['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '30', '-i', os.path.join(seq, '%04d.jpg')]
subprocess.run(ff + ['-vf', 'scale=1432:806:flags=lanczos', '-c:v', 'libx264', '-crf', '20', '-pix_fmt', 'yuv420p', '-g', '15', os.path.join(OUT, 'tela.mp4')], check=True)
subprocess.run(ff + ['-vf', 'scale=640:360,boxblur=18:2,eq=brightness=-0.06:saturation=1.25', '-c:v', 'libx264', '-crf', '23', '-pix_fmt', 'yuv420p', '-g', '15', os.path.join(OUT, 'fundo.mp4')], check=True)
