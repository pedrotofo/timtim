"""Segunda rodada: refaz os modelos com cara de IA num traço mais rabiscado. python3 tools/redo.py chave [chave...] imprime o pedido."""
import json, sys
HAND = ("Scan of a real sketchbook page: soft graphite pencil on cream paper filling the whole frame. Drawn quickly from life by a student of Rembrandt's drawings: "
        "searching, restated lines, visible corrections, uneven pressure, lines thick in shadow and broken in light, one light source from the left, tone scribbled with the side of the lead. "
        "Ordinary, unidealized people with plain asymmetric faces; proportions slightly off; nothing polished, no smooth shading, no comic-book, fashion or stock-illustration look. "
        "Lots of bare paper. Graphite only, no color, no text, no signature, no border. ")
P = {
 'a06': "Double self-portrait seen in a mirror: a middle-aged man with a tired plain face in the foreground wearing a knitted beanie, drawn with heavy dark lines and one side of the face in shadow; behind his shoulder a woman in a headscarf drawn much lighter and fainter with only a few lines. Both look toward the viewer.",
 'a07': "Full-length self-portrait in a mirror of a stocky middle-aged person standing in work clothes and a long apron, hands on hips, feet apart: quick angular lines only, almost no shading, the face indicated with five or six marks, the hands as simple shapes.",
 'l08': "A woman's face in three-quarter view lit from below by a candle she holds: chin, underside of the nose and one cheek lit, eye sockets and forehead in rough dark scribbled tone, the background a rough dark patch of hatching; the small flame left as bare paper.",
 'a03': "Large self-portrait of a young man with messy hair shouting, mouth wide open, head tilted and turned three-quarters, brows knotted; half of the face in rough scribbled shadow; hair as a loose tangle of scribbles; shoulders in four lines.",
 'a01': "Three small rough self-portrait heads loosely scattered on one sheet, each about the size of a matchbox, the same plain young man pulling faces in a mirror: surprised with raised brows, scowling, shouting. Scribbly, only a few lines each, hair as tangles, the three heads of uneven size.",
 'c06': "Head and shoulders of a young woman in a wide straw hat, three-quarter view, looking slightly down and to the side: thin light contour, a soft band of shadow under the brim across the forehead, eyes and mouth in very few strokes, almost all bare paper, the brim one loose ellipse restated twice. 17th-century Dutch clothing.",
 'p08': "Corner of a present-day kitchen with a window on the left; an older person sits at the table peeling fruit; light from the window falls on the hands, face and table; the rest of the room in broad rough scribbled shadow made with the side of the pencil; furniture only hinted with a few lines.",
 'b01': "A sheet of ten tiny one-minute gesture sketches of people: walking, bending, carrying a basket, sitting, leaning on a stick, lifting a child. Each figure is only one sweeping line for the spine plus five or six quick strokes, no faces, no details, almost stick-like, different sizes scattered over the sheet.",
}
print(json.dumps([{'model': 'nano-banana-2', 'mode': 'text2image', 'params': {'aspectRatio': '3:4', 'resolution': '1K', 'prompt': HAND + P[k]}} for k in sys.argv[1:]], ensure_ascii=False))
