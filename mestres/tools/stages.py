"""Etapas dos exercícios em 4 etapas, por image2image a partir do modelo pronto.
python3 tools/stages.py chave resourceId imprime o pedido em JSON (3 imagens: st-<chave>-1..3)."""
import json, sys
BASE = ("Same drawing, same sheet, same composition, same pose and same proportions as the reference, flat scan of the sheet, no board, no pencil, no hands, "
        "graphite only on plain cream paper, no text, no signature. Show it at an earlier stage of the same drawing: ")
ST = ["only the first very light searching construction lines: a few faint lines for the tilt of the body, ovals for the head and the joints, "
      "the chair as a light box; no details, no dark lines, nothing finished.",
      "the firm contour lines drawn over the light construction, the clothes, boots and chair outlined, the face indicated with a few marks; "
      "no shading or tone at all yet.",
      "the full contour plus the first broad strokes of tone on the coat, under the arms and on the boots, the floor lines added; "
      "the face and hands not yet finished, the darkest accents not yet added."]
k, rid = sys.argv[1], sys.argv[2]
print(json.dumps([{'model': 'nano-banana-2', 'mode': 'image2image',
                   'params': {'aspectRatio': '3:4', 'resolution': '1K', 'prompt': BASE + s,
                              'visualReferences': [{'type': 'image', 'id': f'resource:{rid}', 'label': k}]}} for s in ST], ensure_ascii=False))
