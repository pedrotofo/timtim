#!/usr/bin/env python3
"""Gera um projeto HyperFrames com um mapa do Brasil animado, de fundo transparente, para pôr
sobre a fala do cliente: estados que acendem no tempo das palavras, pinos de cidade pulsando,
rotas que se desenham e um zoom da câmera até a região citada.

    python3 mapa_brasil.py config.json --saida motions/I1-mapa
    cd motions/I1-mapa && npx hyperframes render --format mov --output ../I1-mapa.mov

config.json (tempos em segundos a partir do começo do motion; só "duracao" é obrigatório):
{
  "duracao": 3.6, "fps": 25, "largura": 1920, "altura": 1080,
  "area": {"x": 1010, "y": 90, "w": 860, "h": 900},      # onde o mapa fica no quadro
  "foco": ["CE", "PE", "BA"],                              # zoom até esses estados; "NE", "BR"...
  "destaques": [{"uf": "CE", "t": 0.6}, {"uf": "PE", "t": 1.3}, {"uf": "BA", "t": 2.25}],
  "pinos": [{"nome": "Fortaleza", "lat": -3.7319, "lon": -38.5267, "t": 0.5}],
  "rotas": [{"de": [-3.73, -38.53], "para": [-23.55, -46.63], "t": 1.0, "dur": 1.2}],
  "rotulos": true,                                         # nome do estado ao acender
  "titulo": "",                                            # texto curto opcional acima do mapa
  "cores": {"base": "rgba(255,255,255,0.10)", "borda": "rgba(255,255,255,0.45)",
            "destaque": "#F2A93B", "texto": "#FFFFFF", "pino": "#FFFFFF"},
  "fonte": "Inter",
  "placa": true,                                           # placa escura atrás do mapa (ou uma cor; false tira)
  "fundo": "transparente"                                  # ou uma cor, para testar ("#101014")
}
Regiões aceitas em "foco": N, NE, CO, SE, S, BR. Estados pela sigla (SP, RJ...).
"""
import argparse, json, math, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
DADOS = json.load(open(os.path.join(AQUI, "..", "dados", "brasil-estados.json"), encoding="utf-8"))
REGIOES = {"N", "NE", "CO", "SE", "S"}


def projetar(lat, lon):
    m = DADOS["mercator"]
    x = m["tx"] + m["scale"] * math.radians(lon)
    y = m["ty"] - m["scale"] * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
    return x, y


def caixa(ufs):
    xs, ys = [], []
    for e in DADOS["estados"]:
        if e["uf"] in ufs:
            nums = [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", e["d"])]
            xs += nums[0::2]; ys += nums[1::2]
    return min(xs), min(ys), max(xs), max(ys)


def viewbox_para(ufs, aspecto, margem=0.12):
    x0, y0, x1, y1 = caixa(ufs)
    w, h = x1 - x0, y1 - y0
    w, h = w * (1 + 2 * margem), h * (1 + 2 * margem)
    if w / h < aspecto:
        w = h * aspecto
    else:
        h = w / aspecto
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return cx - w / 2, cy - h / 2, w, h


def resolver(foco):
    if not foco or foco == "BR" or foco == ["BR"]:
        return [e["uf"] for e in DADOS["estados"]]
    foco = [foco] if isinstance(foco, str) else foco
    ufs = []
    for f in foco:
        ufs += [e["uf"] for e in DADOS["estados"] if e["reg"] == f] if f in REGIOES else [f]
    return ufs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config")
    ap.add_argument("--saida", required=True)
    a = ap.parse_args()
    c = json.load(open(a.config, encoding="utf-8"))

    D = float(c["duracao"]); fps = c.get("fps", 30)
    W, H = c.get("largura", 1920), c.get("altura", 1080)
    area = c.get("area", {"x": W * 0.52, "y": H * 0.08, "w": W * 0.45, "h": H * 0.84})
    cor = {"base": "rgba(255,255,255,0.10)", "borda": "rgba(255,255,255,0.45)", "destaque": "#F2A93B",
           "texto": "#FFFFFF", "texto_destaque": "#1A1206", "pino": "#FFFFFF", **c.get("cores", {})}
    fonte = c.get("fonte", "Inter")
    fundo = c.get("fundo", "transparente")
    aspecto = area["w"] / area["h"]
    siglas = {e["uf"] for e in DADOS["estados"]}
    for d in c.get("destaques", []):
        if d["uf"] not in siglas:
            sys.exit(f"sigla desconhecida: {d['uf']}")

    vb0 = viewbox_para(resolver("BR"), aspecto, 0.04)
    foco = resolver(c.get("foco") or [d["uf"] for d in c.get("destaques", [])] or "BR")
    vb1 = viewbox_para(foco, aspecto)
    zoom = vb1[2] / vb0[2]                     # quanto o mundo encolhe: textos e pinos acompanham
    px = vb1[2] / area["w"]                     # unidades do mapa por pixel no quadro final

    estados = "\n".join(
        f'<path id="uf-{e["uf"]}" class="uf" d="{e["d"]}"/>' for e in DADOS["estados"])
    rotulos = ""
    if c.get("rotulos", True):
        rotulos = "\n".join(
            f'<text id="rot-{d["uf"]}" class="rot" x="{e["cx"]}" y="{e["cy"]}" '
            f'font-size="{30 * px:.2f}">{e["nome"]}</text>'
            for d in c.get("destaques", []) for e in DADOS["estados"] if e["uf"] == d["uf"])
    pinos = ""
    for i, p in enumerate(c.get("pinos", [])):
        x, y = projetar(p["lat"], p["lon"])
        pinos += (f'<g id="pino-{i}" class="pino" transform="translate({x:.1f},{y:.1f})">'
                  f'<circle class="onda" r="{9 * px:.2f}"/><circle class="ponto" r="{7 * px:.2f}"/>'
                  f'<text class="rotpino" x="{16 * px:.2f}" y="{10 * px:.2f}" font-size="{30 * px:.2f}">'
                  f'{p.get("nome", "")}</text></g>')
    rotas = ""
    for i, r in enumerate(c.get("rotas", [])):
        (x0, y0), (x1, y1) = projetar(*r["de"]), projetar(*r["para"])
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        dx, dy = x1 - x0, y1 - y0
        cx, cy = mx - dy * 0.25, my + dx * 0.25      # arco para um lado, não linha reta
        rotas += (f'<path id="rota-{i}" class="rota" pathLength="100" d="M{x0:.1f},{y0:.1f} '
                  f'Q{cx:.1f},{cy:.1f} {x1:.1f},{y1:.1f}" stroke-width="{4 * px:.2f}"/>')

    js = ['tl.fromTo("#placa", {opacity: 0}, {opacity: 1, duration: 0.35, ease: "power2.out"}, 0);'] if c.get("placa", True) else []
    js += [f'tl.fromTo("#mapa", {{opacity: 0, scale: 0.96}}, {{opacity: 1, scale: 1, duration: 0.45, ease: "power3.out"}}, 0);']
    if vb1 != vb0:
        js.append(f'tl.fromTo("#svg", {{attr: {{viewBox: "{" ".join(f"{v:.1f}" for v in vb0)}"}}}}, '
                  f'{{attr: {{viewBox: "{" ".join(f"{v:.1f}" for v in vb1)}"}}, duration: {min(1.0, D * 0.3):.2f}, '
                  f'ease: "power2.inOut"}}, 0.1);')
    for d in c.get("destaques", []):
        t = float(d["t"])
        js.append(f'tl.to("#uf-{d["uf"]}", {{fill: "{cor["destaque"]}", duration: 0.35, ease: "power2.out"}}, {t:.2f});')
        if c.get("rotulos", True):
            js.append(f'tl.fromTo("#rot-{d["uf"]}", {{opacity: 0, y: {8 * px:.2f}}}, {{opacity: 1, y: 0, duration: 0.35, ease: "power2.out"}}, {t + 0.08:.2f});')
    for i, p in enumerate(c.get("pinos", [])):
        t = float(p["t"])
        js.append(f'tl.fromTo("#pino-{i} .ponto", {{scale: 0, transformOrigin: "50% 50%"}}, {{scale: 1, duration: 0.3, ease: "back.out(2.2)"}}, {t:.2f});')
        js.append(f'tl.fromTo("#pino-{i} .rotpino", {{opacity: 0}}, {{opacity: 1, duration: 0.3}}, {t + 0.1:.2f});')
        ondas = max(0, int((D - t - 0.4) / 1.1))
        if ondas:
            js.append(f'tl.fromTo("#pino-{i} .onda", {{scale: 1, opacity: 0.8, transformOrigin: "50% 50%"}}, '
                      f'{{scale: 3.2, opacity: 0, duration: 1.1, ease: "power1.out", repeat: {ondas - 1}}}, {t + 0.15:.2f});')
    for i, r in enumerate(c.get("rotas", [])):
        js.append(f'tl.fromTo("#rota-{i}", {{strokeDashoffset: 100}}, {{strokeDashoffset: 0, duration: {r.get("dur", 1.0)}, ease: "power2.inOut"}}, {float(r["t"]):.2f});')
    if c.get("titulo"):
        js.append('tl.fromTo("#titulo", {opacity: 0, y: 16}, {opacity: 1, y: 0, duration: 0.4, ease: "power3.out"}, 0.2);')
    js.append(f'tl.to("#mapa, #titulo, #placa", {{opacity: 0, duration: 0.3, ease: "power2.in"}}, {max(0.5, D - 0.3):.2f});')

    placa_cfg = c.get("placa", True)
    placa = placa_cfg if isinstance(placa_cfg, str) else "rgba(12,12,16,0.62)"
    fundo_css = "transparent" if fundo in ("transparente", "transparent", None) else fundo
    titulo = (f'<div id="titulo" style="left:{area["x"]}px;top:{area["y"] - 70}px;width:{area["w"]}px">'
              f'{c["titulo"]}</div>') if c.get("titulo") else ""
    html = f"""<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: {fundo_css}; }}
      #root {{ width: 100%; height: 100%; position: relative; font-family: "{fonte}", sans-serif; background: {fundo_css}; }}
      #mapa {{ position: absolute; left: {area["x"]}px; top: {area["y"]}px; width: {area["w"]}px; height: {area["h"]}px; }}
      #svg {{ width: 100%; height: 100%; overflow: hidden; }}
      #mapa {{ -webkit-mask-image: radial-gradient(ellipse 72% 72% at 50% 50%, #000 62%, transparent 100%); mask-image: radial-gradient(ellipse 72% 72% at 50% 50%, #000 62%, transparent 100%); }}
      #placa {{ position: absolute; left: {area["x"] - 24}px; top: {area["y"] - 24}px; width: {area["w"] + 48}px; height: {area["h"] + 48}px; border-radius: 28px; background: {placa}; opacity: 0; }}
      .uf {{ fill: {cor["base"]}; stroke: {cor["borda"]}; stroke-width: 1.2; vector-effect: non-scaling-stroke; stroke-linejoin: round; }}
      .rot {{ fill: {cor["texto_destaque"]}; font-weight: 700; text-anchor: middle; dominant-baseline: central; opacity: 0; }}
      .ponto {{ fill: {cor["pino"]}; }}
      .onda {{ fill: none; stroke: {cor["pino"]}; stroke-width: 2; vector-effect: non-scaling-stroke; opacity: 0; }}
      .rotpino {{ fill: {cor["texto"]}; font-weight: 700; opacity: 0; paint-order: stroke; stroke: rgba(0,0,0,0.55); stroke-width: {5 * px:.2f}px; }}
      .rota {{ fill: none; stroke: {cor["destaque"]}; stroke-linecap: round; stroke-dasharray: 100 120; stroke-dashoffset: 100; }}
      #titulo {{ position: absolute; color: {cor["texto"]}; font-size: 40px; font-weight: 700; text-align: center; letter-spacing: -0.01em; opacity: 0; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{D}" data-width="{W}" data-height="{H}">
      {'<div id="placa"></div>' if placa_cfg else ''}
      {titulo}
      <div id="mapa" class="clip" data-start="0" data-duration="{D}" data-track-index="0">
        <svg id="svg" viewBox="{" ".join(f"{v:.1f}" for v in vb0)}" preserveAspectRatio="xMidYMid meet">
          <g id="estados">
{estados}
          </g>
          <g id="rotas">{rotas}</g>
          <g id="rotulos">{rotulos}</g>
          <g id="pinos">{pinos}</g>
        </svg>
      </div>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {chr(10).join("      " + l for l in js).lstrip()}
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""
    os.makedirs(a.saida, exist_ok=True)
    with open(os.path.join(a.saida, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    nome = os.path.basename(os.path.abspath(a.saida))
    with open(os.path.join(a.saida, "hyperframes.json"), "w") as f:
        json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
                   "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
                   "paths": {"blocks": "compositions", "components": "compositions/components",
                             "assets": "assets"}, "media": {"autoProxy": True}}, f, indent=2)
    with open(os.path.join(a.saida, "meta.json"), "w") as f:
        json.dump({"id": nome, "name": nome}, f, indent=2)
    print(f"{a.saida}/index.html: {D}s, zoom {1 / zoom:.1f}x, {len(c.get('destaques', []))} estados, "
          f"{len(c.get('pinos', []))} pinos, {len(c.get('rotas', []))} rotas", file=sys.stderr)


if __name__ == "__main__":
    main()
