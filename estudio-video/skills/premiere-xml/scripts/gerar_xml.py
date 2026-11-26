#!/usr/bin/env python3
"""Gera uma sequência do Premiere (XML do Final Cut Pro 7, Arquivo > Importar) a partir da
decupagem, do corte e dos motions: a mídia original cortada nos trechos mantidos (V1 + áudio),
os motions com transparência na V2, no tempo da fala, e um marcador em cada fala boa e em cada
ponto de ilustração. Tudo continua editável: nada é renderizado.

    python3 gerar_xml.py --decupagem decup/decupagem.json \
        [--manifest edited/manifest.json]   # trechos mantidos (kept_spans) da video-editing-skill
        [--cortes cortes.json]              # ou uma lista própria: [[inicio, fim], ...]
        [--insertos motions/insertos.json]  # motions de /ilustrar-fala
        [--raiz "D:/Clientes/Marina"]       # pasta onde os arquivos estarão no seu computador
        [--nome "Marina - corte 1"] --saida marina.xml

Sem --manifest/--cortes, a sequência usa a mídia inteira (só marcadores e motions).
--raiz troca a pasta de todos os arquivos pela sua pasta local, mantendo os nomes; se faltar,
o Premiere pede para localizar a mídia na primeira vez e acha o resto sozinho.

insertos.json: [{"arquivo": "motions/I1-mapa.mov", "inicio": 11.10, "duracao": 3.4, "nome": "I1 mapa"}]
com "inicio" no tempo da mídia original (o script leva para o tempo da timeline cortada).
"""
import argparse, json, os, subprocess, sys
from urllib.parse import quote
from xml.sax.saxutils import escape


def sondar(caminho):
    """(fps, largura, altura, canais de áudio, duração em s) ou None se não der para ler."""
    if not os.path.exists(caminho):
        return None
    cmd = ["ffprobe", "-v", "error", "-show_entries",
           "stream=codec_type,r_frame_rate,width,height,channels:format=duration", "-of", "json", caminho]
    try:
        d = json.loads(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout)
    except Exception:
        return None
    fps, w, h, ch = None, 1920, 1080, 0
    for s in d.get("streams", []):
        if s.get("codec_type") == "video" and fps is None:
            n, m = s.get("r_frame_rate", "30/1").split("/")
            fps, w, h = float(n) / float(m), s.get("width", 1920), s.get("height", 1080)
        elif s.get("codec_type") == "audio":
            ch = max(ch, s.get("channels", 2))
    return fps, w, h, ch, float(d.get("format", {}).get("duration", 0) or 0)


def rate_xml(fps):
    """timebase inteiro + flag NTSC (23,976 / 29,97 / 59,94)."""
    tb = round(fps)
    ntsc = abs(fps - tb) > 0.01
    return f"<rate><timebase>{tb}</timebase><ntsc>{'TRUE' if ntsc else 'FALSE'}</ntsc></rate>"


def pathurl(caminho, raiz):
    if raiz:
        caminho = raiz.rstrip("/\\") + "/" + os.path.basename(caminho)
    caminho = caminho.replace("\\", "/")
    if len(caminho) > 1 and caminho[1] == ":":          # Windows: D:/... -> D%3a/...
        caminho = caminho[0] + "%3a" + caminho[2:]
    return "file://localhost" + ("" if caminho.startswith("/") else "/") + quote(caminho, safe="/%")


class Linha:
    """Leva tempos da mídia original para a timeline cortada."""

    def __init__(self, spans, fps):
        self.fps = fps
        self.pedacos, t = [], 0
        for a, b in spans:
            fa, fb = round(a * fps), round(b * fps)
            if fb > fa:
                self.pedacos.append((fa, fb, t))
                t += fb - fa
        self.total = t

    def quadro(self, seg):
        """Quadro na timeline para um tempo da mídia, ou None se caiu num trecho cortado."""
        f = round(seg * self.fps)
        for fa, fb, t in self.pedacos:
            if fa <= f < fb:
                return t + f - fa
        return None


def arquivo_xml(fid, caminho, raiz, info, fps, completo):
    if not completo:
        return f'<file id="{fid}"/>'
    f_fps, w, h, ch, dur = info
    nome = escape(os.path.basename(caminho))
    audio = (f"<audio><samplecharacteristics><depth>16</depth><samplerate>48000</samplerate>"
             f"</samplecharacteristics><channelcount>{ch}</channelcount></audio>") if ch else ""
    return (f'<file id="{fid}"><name>{nome}</name><pathurl>{escape(pathurl(caminho, raiz))}</pathurl>'
            f"{rate_xml(f_fps or fps)}<duration>{round(dur * (f_fps or fps))}</duration>"
            f"<media><video><samplecharacteristics>{rate_xml(f_fps or fps)}<width>{w}</width>"
            f"<height>{h}</height><pixelaspectratio>square</pixelaspectratio></samplecharacteristics>"
            f"</video>{audio}</media></file>")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--decupagem", required=True)
    ap.add_argument("--manifest")
    ap.add_argument("--cortes")
    ap.add_argument("--insertos")
    ap.add_argument("--raiz", default="")
    ap.add_argument("--nome", default="")
    ap.add_argument("--nota-minima", type=int, default=2, help="falas com nota abaixo disso ficam sem marcador")
    ap.add_argument("--saida", required=True)
    a = ap.parse_args()

    dec = json.load(open(a.decupagem, encoding="utf-8"))
    midia = dec["midia"]
    info = sondar(midia)
    fps = (info[0] if info and info[0] else None) or float(dec.get("fps", 30))
    if not info:
        print(f"  aviso: não achei {midia} aqui; uso {fps} fps, 1920x1080 e áudio estéreo da decupagem",
              file=sys.stderr)
        info = (fps, 1920, 1080, 2, float(dec.get("duracao", 0)))
    _, W, H, canais, dur = info

    if a.manifest:
        spans = json.load(open(a.manifest, encoding="utf-8"))["kept_spans"]
    elif a.cortes:
        spans = json.load(open(a.cortes, encoding="utf-8"))
    else:
        spans = [[0, dur]]
    linha = Linha(spans, fps)
    R = rate_xml(fps)
    nome_seq = escape(a.nome or os.path.splitext(os.path.basename(midia))[0] + " - decupado")

    # V1 e áudio: um clipitem por trecho mantido, vídeo e áudio ligados
    v1, a_tracks = [], {c: [] for c in range(1, min(canais, 2) + 1)}
    for i, (fa, fb, t) in enumerate(linha.pedacos, 1):
        ids = [f"v1-{i}"] + [f"a{c}-{i}" for c in a_tracks]
        link = "".join(f"<link><linkclipref>{x}</linkclipref></link>" for x in ids)
        base = (f"<name>{escape(os.path.basename(midia))}</name><enabled>TRUE</enabled>"
                f"<duration>{round(dur * fps)}</duration>{R}<start>{t}</start><end>{t + fb - fa}</end>"
                f"<in>{fa}</in><out>{fb}</out>")
        v1.append(f'<clipitem id="v1-{i}">{base}{arquivo_xml("midia-1", midia, a.raiz, info, fps, i == 1)}{link}</clipitem>')
        for c in a_tracks:
            a_tracks[c].append(
                f'<clipitem id="a{c}-{i}">{base}<file id="midia-1"/>'
                f"<sourcetrack><mediatype>audio</mediatype><trackindex>{c}</trackindex></sourcetrack>{link}</clipitem>")

    # V2: motions no tempo da fala
    v2, fora = [], []
    if a.insertos:
        for k, ins in enumerate(json.load(open(a.insertos, encoding="utf-8")), 1):
            arq = ins["arquivo"]
            if not os.path.isabs(arq):
                arq = os.path.abspath(os.path.join(os.path.dirname(a.insertos), arq))
            t0 = linha.quadro(float(ins["inicio"]))
            if t0 is None:
                fora.append(ins.get("nome", arq)); continue
            ii = sondar(arq) or (fps, W, H, 0, float(ins["duracao"]))
            n = round(float(ins.get("duracao") or ii[4]) * fps)
            nm = escape(ins.get("nome") or os.path.basename(arq))
            v2.append(f'<clipitem id="v2-{k}"><name>{nm}</name><enabled>TRUE</enabled>'
                      f"<duration>{round(ii[4] * fps)}</duration>{R}<start>{t0}</start><end>{t0 + n}</end>"
                      f"<in>0</in><out>{n}</out>{arquivo_xml(f'motion-{k}', arq, a.raiz, ii, fps, True)}"
                      f"<compositemode>normal</compositemode></clipitem>")

    # Marcadores da sequência: falas boas e pontos de ilustração
    marcas = []
    for tr in dec.get("trechos", []):
        if tr.get("nota", 0) >= a.nota_minima:
            q = linha.quadro(float(tr["inicio"]))
            if q is not None:
                fim = linha.quadro(max(float(tr["inicio"]), float(tr["fim"]) - 0.04))
                marcas.append((q, fim if fim is not None else -1,
                               f"{'★' * tr['nota']} {tr.get('tema', '')}".strip(),
                               f"{tr.get('texto', '')} {('— ' + tr['obs']) if tr.get('obs') else ''}".strip()))
    for il in dec.get("ilustracoes", []):
        q = linha.quadro(float(il["inicio"]))
        if q is not None:
            marcas.append((q, -1, f"ILUSTRAR {il.get('id', '')}: {il.get('tipo', '')}", il.get("ideia", "")))
    for cf in dec.get("conferir", []):
        q = linha.quadro(float(cf["t"]))
        if q is not None:
            marcas.append((q, -1, "CONFERIR", cf.get("motivo", "")))
    marcas_xml = "".join(f"<marker><name>{escape(n)}</name><comment>{escape(c)}</comment>"
                         f"<in>{i}</in><out>{o}</out></marker>" for i, o, n, c in sorted(marcas))

    fmt = (f"<format><samplecharacteristics>{R}<width>{W}</width><height>{H}</height>"
           f"<pixelaspectratio>square</pixelaspectratio><fielddominance>none</fielddominance>"
           f"</samplecharacteristics></format>")
    trilha = lambda itens: f"<track>{''.join(itens)}<enabled>TRUE</enabled><locked>FALSE</locked></track>"
    video = fmt + trilha(v1) + (trilha(v2) if v2 else "")
    audio = "".join(trilha(x) for x in a_tracks.values())
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n<xmeml version="4">'
           f'<sequence id="sequencia-1"><name>{nome_seq}</name><duration>{linha.total}</duration>{R}'
           f"<timecode>{R}<string>00:00:00:00</string><frame>0</frame><displayformat>NDF</displayformat></timecode>"
           f"<media><video>{video}</video><audio><numOutputChannels>2</numOutputChannels>{audio}</audio></media>"
           f"{marcas_xml}</sequence></xmeml>\n")
    with open(a.saida, "w", encoding="utf-8") as f:
        f.write(xml)

    print(f"{a.saida}: {len(linha.pedacos)} trechos ({linha.total / fps:.1f} s de {dur:.1f} s), "
          f"{len(v2)} motions na V2, {len(marcas)} marcadores", file=sys.stderr)
    if fora:
        print(f"  aviso: caíram em trechos cortados e ficaram de fora: {', '.join(fora)}", file=sys.stderr)


if __name__ == "__main__":
    main()
