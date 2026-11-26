#!/usr/bin/env python3
"""Transcreve um vídeo ou áudio para a decupagem: tempo por palavra, timecode no fps do vídeo,
pausas e legenda SRT. Roda local e de graça com faster-whisper (CPU ou GPU).

    python3 transcrever.py VIDEO --saida decup/ [--termos "Doce Raiz, Marina"] [--modelo small]
                           [--idioma pt] [--falantes 2]

Escreve em --saida:
  transcricao.json  segmentos com palavras, início/fim em segundos, fps e duração da mídia
  transcricao.txt   uma linha por frase: [HH:MM:SS:FF - HH:MM:SS:FF] (F1) texto
  pausas.json       silêncios entre palavras maiores que --pausa (padrão 0,7 s)
  legenda.srt       legenda pronta (até 42 caracteres por linha, 2 linhas)

--falantes N separa quem fala (entrevistador x cliente) com pyannote. Precisa de
`pip install pyannote.audio` e de um HF_TOKEN com acesso a pyannote/speaker-diarization-3.1.
Sem isso o script avisa e segue sem separar.

Modelos: small (rápido, bom para decupar), medium ou large-v3 (mais preciso, lento em CPU;
use em máquina com GPU NVIDIA ou para a legenda final).
"""
import argparse, json, os, subprocess, sys


def sondar(video):
    """fps e duração da mídia via ffprobe. Áudio puro usa 30 fps para o timecode."""
    cmd = ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,r_frame_rate:format=duration",
           "-of", "json", video]
    try:
        d = json.loads(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout)
    except Exception as e:
        sys.exit(f"ffprobe não conseguiu ler {video}: {e}")
    fps = 30.0
    for s in d.get("streams", []):
        if s.get("codec_type") == "video" and s.get("r_frame_rate", "0/0") != "0/0":
            n, m = s["r_frame_rate"].split("/")
            fps = float(n) / float(m)
            break
    return fps, float(d.get("format", {}).get("duration", 0) or 0)


def tc(seg, fps):
    """Segundos -> HH:MM:SS:FF (sem drop-frame)."""
    base = round(fps)
    total = int(round(seg * fps))
    ff = total % base
    s = total // base
    return f"{s // 3600:02d}:{s // 60 % 60:02d}:{s % 60:02d}:{ff:02d}"


def srt_tempo(seg):
    ms = int(round(seg * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def falantes(video, n, segmentos):
    """Rótulo de falante por segmento (pyannote). Devolve False se não der."""
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
    try:
        from pyannote.audio import Pipeline
    except ImportError:
        print("  aviso: pyannote.audio não instalado; seguindo sem separar falantes", file=sys.stderr)
        return False
    if not token:
        print("  aviso: sem HF_TOKEN; seguindo sem separar falantes", file=sys.stderr)
        return False
    wav = os.path.join(os.path.dirname(segmentos[0]["_saida"]), "_audio16k.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-ac", "1", "-ar", "16000", wav], check=True)
    pipe = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=token)
    diar = pipe(wav, num_speakers=n)
    turnos = [(t.start, t.end, f) for t, _, f in diar.itertracks(yield_label=True)]
    nomes = {}
    for s in segmentos:
        # o falante que mais se sobrepõe à frase
        melhor = max(turnos, key=lambda t: min(t[1], s["fim"]) - max(t[0], s["inicio"]), default=None)
        if melhor:
            s["falante"] = nomes.setdefault(melhor[2], f"F{len(nomes) + 1}")
    os.remove(wav)
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--saida", default="decup")
    ap.add_argument("--modelo", default="small")
    ap.add_argument("--idioma", default="pt")
    ap.add_argument("--termos", default="", help="nomes, marcas e jargões, separados por vírgula")
    ap.add_argument("--pausa", type=float, default=0.7, help="pausa mínima registrada, em segundos")
    ap.add_argument("--falantes", type=int, default=0, help="número de pessoas que falam (0 = não separar)")
    a = ap.parse_args()

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("faster-whisper não está instalado: pip install faster-whisper 'av<16'")

    os.makedirs(a.saida, exist_ok=True)
    fps, duracao = sondar(a.video)
    termos = [t.strip() for t in a.termos.split(",") if t.strip()]
    # O prompt inicial faz o Whisper escrever hesitações ("é...", "hã") e soletrar os termos certos.
    prompt = "Hã, é... então, tipo assim. " + (", ".join(termos) + "." if termos else "")

    print(f"  transcrevendo com faster-whisper '{a.modelo}' ({a.idioma}, {fps:.3f} fps)...", file=sys.stderr)
    modelo = WhisperModel(a.modelo, device="auto", compute_type="auto")
    segs, info = modelo.transcribe(a.video, language=a.idioma or None, word_timestamps=True,
                                   vad_filter=True, initial_prompt=prompt,
                                   hotwords=", ".join(termos) or None, condition_on_previous_text=False)
    segmentos = []
    for s in segs:
        palavras = [{"p": w.word.strip(), "inicio": round(w.start, 3), "fim": round(w.end, 3),
                     "conf": round(w.probability, 3)} for w in (s.words or []) if w.word.strip()]
        if not palavras:
            continue
        segmentos.append({"id": len(segmentos) + 1, "inicio": palavras[0]["inicio"], "fim": palavras[-1]["fim"],
                          "texto": s.text.strip(), "palavras": palavras,
                          "_saida": os.path.join(a.saida, "x")})

    tem_falantes = falantes(a.video, a.falantes, segmentos) if a.falantes and segmentos else False
    for s in segmentos:
        s.pop("_saida", None)

    todas = [w for s in segmentos for w in s["palavras"]]
    pausas = [{"inicio": x["fim"], "fim": y["inicio"], "dur": round(y["inicio"] - x["fim"], 2),
               "tc": tc(x["fim"], fps)}
              for x, y in zip(todas, todas[1:]) if y["inicio"] - x["fim"] >= a.pausa]

    with open(os.path.join(a.saida, "transcricao.json"), "w", encoding="utf-8") as f:
        json.dump({"midia": os.path.abspath(a.video), "fps": fps, "duracao": duracao,
                   "idioma": info.language, "modelo": a.modelo, "falantes": tem_falantes,
                   "segmentos": segmentos}, f, ensure_ascii=False, indent=1)
    with open(os.path.join(a.saida, "pausas.json"), "w", encoding="utf-8") as f:
        json.dump(pausas, f, ensure_ascii=False, indent=1)
    with open(os.path.join(a.saida, "transcricao.txt"), "w", encoding="utf-8") as f:
        for s in segmentos:
            quem = f"({s['falante']}) " if s.get("falante") else ""
            duvida = " [?]" if min(w["conf"] for w in s["palavras"]) < 0.4 else ""
            f.write(f"[{tc(s['inicio'], fps)} - {tc(s['fim'], fps)}] {quem}{s['texto']}{duvida}\n")
    with open(os.path.join(a.saida, "legenda.srt"), "w", encoding="utf-8") as f:
        n = 0
        for s in segmentos:
            bloco, linha = [], []
            for w in s["palavras"]:
                if len(" ".join(linha + [w["p"]])) > 42:
                    bloco.append(linha); linha = []
                linha.append(w["p"])
            bloco.append(linha)
            # junta de duas em duas linhas por legenda, com o tempo das palavras de cada par
            ws, i = s["palavras"], 0
            for k in range(0, len(bloco), 2):
                par = [l for l in bloco[k:k + 2] if l]
                qtd = sum(len(l) for l in par)
                if not qtd:
                    continue
                n += 1
                f.write(f"{n}\n{srt_tempo(ws[i]['inicio'])} --> {srt_tempo(ws[i + qtd - 1]['fim'])}\n"
                        + "\n".join(" ".join(l) for l in par) + "\n\n")
                i += qtd

    print(f"{len(segmentos)} frases, {len(todas)} palavras, {len(pausas)} pausas >= {a.pausa}s "
          f"-> {a.saida}/transcricao.txt", file=sys.stderr)


if __name__ == "__main__":
    main()
