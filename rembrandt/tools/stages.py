"""Pedidos image2image das etapas: python3 tools/stages.py st-t08-1 st-t08-2 ... (usa a URL do modelo final em tools/urls.txt)."""
import json, sys
U = {}
for l in open('tools/urls.txt'):
    k, u = l.split(); U[k] = u
C = {  # (etapa 1, etapa 2, etapa 3)
 't08': ('the horizon, the outline of the cottage and the rough outer shapes of the two tree masses', 'the roof, the tree trunks and the fence drawn as firm lines', 'the tree crowns in scribble and smudged tone and the shadow side of the cottage'),
 'l04': ('the window, the seated figure and the table', 'the gesture of the figure and the lines of the window drawn firmly', 'the broad smudged shadow of the room around her, leaving the light from the window on her face, hands and book'),
 'l05': ('the standing figure in a few construction lines', 'the contour and the folds of the clothes', 'the tone getting darker from the waist down'),
 'l06': ('the horizon, the hill and three simple shapes for the trees', 'the tree trunks and the edge of the hill drawn firmly', 'the dark masses of the trees and the bands of the plain'),
 'c04': ('the egg shape of the head, the central axis and one line dividing light from shadow', 'a flat mid-tone on the shadow side of the face with a small triangle of light left under the eye', 'the eyes, nose, mouth and the beard in loose strokes'),
 'c05': ('the head, the hood and the shoulders in construction lines', 'the features and the lines of the hood', 'the hatching on the shadow side of the face'),
 'a04': ('the head, the turned shoulders, the arm and the table edge', 'the face drawn clearly and the outline of the sleeve', 'the hatching of the sleeve and the shadow of the cap'),
 'a05': ('the window, the seated figure and the sketchbook', 'the face, the hand and the sketchbook drawn firmly', 'the smudged shadow of the room, leaving the light on the face, hand and page'),
 'b07': ('the standing woman and the child as a few gesture lines', 'the contours of the figures and the folds of the dress', 'the dark smudged wall on the right'),
 'b12': ('the seated old woman and the children as simple gesture lines', 'the contours of every figure', 'the shadow around the old woman at the center'),
}
WHAT = {1: 'only the very first light sketch in faint 2B pencil: {0}; no tone and no dark lines at all, most of the sheet empty',
        2: 'the light sketch plus {1}; nothing else yet',
        3: 'the lines of the previous stages plus {2}; no final dark accents yet'}
out = []
for a in sys.argv[1:]:
    _, k, n = a.split('-'); n = int(n)
    w = WHAT[n].format(*C[k])
    p = ('The reference image is a finished pencil drawing. Show an EARLIER, UNFINISHED STAGE of exactly the same drawing, as a flat scan of the sheet (no board, no pencil, no hands, no table): '
         f'same paper, same composition, same position and size of every shape. This stage shows {w}. Graphite only on warm cream paper filling the whole frame, no text, no signature.')
    out.append({'model': 'nano-banana-2', 'mode': 'image2image', 'params': {'aspectRatio': '3:4', 'resolution': '1K', 'prompt': p,
               'visualReferences': [{'type': 'image', 'id': f'final-{k}', 'label': 'finished drawing', 'url': U[k]}]}})
print(json.dumps(out, ensure_ascii=False))
