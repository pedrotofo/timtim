#!/usr/bin/env bash
# Põe o motion (com transparência) sobre o vídeo do cliente no tempo certo e gera uma folha com
# 3 quadros (começo, meio, fim) e um MP4 curto para conferir antes de mandar para o Premiere.
#
#   bash previa.sh VIDEO MOTION.mov INICIO_EM_SEGUNDOS [saida-sem-extensao]
#
# Escreve <saida>.jpg (folha de 3 quadros) e <saida>.mp4 (o trecho com o motion por cima).
set -euo pipefail
VIDEO="$1"; MOTION="$2"; INICIO="$3"; SAIDA="${4:-${MOTION%.*}-previa}"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$MOTION")
FPS=$(ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of csv=p=0 "$VIDEO")
N=$(python3 -c "f=$FPS; print(int(round(float($DUR)*(f if isinstance(f,float) else f))))" 2>/dev/null \
    || python3 -c "n,d='$FPS'.split('/'); print(int(round($DUR*int(n)/int(d))))")
A=$((N / 6)); B=$((N / 2)); C=$((N * 5 / 6))
ffmpeg -v error -y -ss "$INICIO" -t "$DUR" -i "$VIDEO" -i "$MOTION" \
  -filter_complex "[0:v][1:v]overlay=0:0:format=auto,split[v][w];[w]select='eq(n\,$A)+eq(n\,$B)+eq(n\,$C)',scale=960:-1,tile=3x1[f]" \
  -map "[f]" -frames:v 1 -update 1 "$SAIDA.jpg" \
  -map "[v]" -map 0:a? -c:v libx264 -pix_fmt yuv420p -crf 20 -c:a aac "$SAIDA.mp4"
echo "$SAIDA.jpg e $SAIDA.mp4"
