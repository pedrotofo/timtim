"""Prompts dos desenhos-modelo (OpenArt, Nano Banana 2). Gera tools/prompts.json."""
import json
BASE = ("Flat scan of a soft graphite pencil drawing on warm cream paper filling the whole frame, no edges, no frame. "
        "Rembrandt-like quick sketch in pencil: lines thick in shadow and broken in light, economical, much empty paper, one light source, "
        "tone made with the side of the lead, lightly smudged. Rough, unfinished, not academic. Graphite only, no color, no text, no signature. ")
OLD = "17th-century Dutch clothing. "
NOW = "Contemporary everyday clothing, present day. "
P = {
 't01': "A practice sheet: ten long, gently curving lines drawn across the sheet from left to right, stacked one below the other; each line starts thin, swells thick and dark in the middle, and tapers thin again at the end.",
 't02': "A simple round ceramic jug on a table, lit strongly from the left. Drawn only with contour lines, no shading inside: the right-hand contour of the jug, its handle and the base are drawn with a very thick, heavy, dark line pressed hard; the left-hand contour is a very thin, faint line that breaks into short pieces with gaps. Strong contrast between the heavy right line and the faint broken left line.",
 't03': "A practice sheet with three horizontal bands of parallel straight hatching strokes, all in the same diagonal direction; in each band the strokes get closer together from left to right, making a smooth gradient from light to dark.",
 't04': "A practice sheet with three squares side by side: the first with one layer of parallel hatching, the second with two layers crossing at a strong angle, the third with three layers, making three clear tones from light to dark.",
 't05': "A practice sheet with exactly three broad rectangular patches of tone side by side, made with the side of a soft pencil lead: left one pale, middle one medium, right one dark and smudged smooth with a blending stump. Nothing else on the sheet: no figures, no drawings, no objects, only the three patches on empty paper.",
 't06': "A single tree in a field: thin trunk in a few lines, the crown made only of loose zig-zag scribbles, denser and darker at the bottom and on the right shadow side, open and light at the top-left.",
 'l01': "A ball resting on a table, lit from the upper left: the lit side left as bare paper, the shadow side a flat mid-grey tone, a dark cast shadow on the table to the right, and one tiny black accent where the ball touches the table.",
 'l02': "A plain wooden box on a table next to a window on the left: the face toward the window left as bare paper, the side face a flat mid-grey tone, a long dark cast shadow stretching to the right.",
 'l03': "A white egg on a table against a dark smudged background; the background is darkest right next to the lit left side of the egg and lighter next to its shadow side; the egg has no outline at all.",
 'c01': "Construction study of a simple egg-shaped bald head in three-quarter view, lit strongly from the left. One light line runs down the forehead, around the nose and down the chin, dividing the face in two. The whole right half of the face (the shadow side) is filled with a flat, even mid-grey tone made with the side of the pencil; the left half is bare paper. Eyes, nose and mouth only as faint marks.",
 'c02': "Study of a man's head in three-quarter view lit from the upper left: half of the face in shadow, and on the shadowed cheek, just below the eye, a small bright triangle of light (Rembrandt lighting). Features drawn with few lines.",
 'c03': "Head and shoulders of a man wearing a wide-brimmed hat, strong light from directly above: the brim casts a broad, very dark shadow band across the whole upper face, covering the forehead and both eyes completely, so the eyes are only dim shapes inside the dark band; below the shadow the nose tip, mouth and chin are lit bare paper. " + OLD,
 'a01': "A sheet with three small self-portrait heads of a young man with messy curly hair, each the size of a matchbox, making exaggerated faces in a mirror: one wide-eyed and surprised, one frowning, one shouting with open mouth. Only forehead, brows, eyes and mouth are worked; hair as quick scribble. " + NOW,
 'a02': "Self-portrait study of a young woman seen in a mirror: body turned sideways, face turned back over the shoulder toward the viewer. Only the head, the hair and one line for the shoulder; light from the left. " + NOW,
 'b01': "A sheet of ten small quick gesture figures, each about one minute: people walking, bending, carrying a basket, sitting, leaning on a stick, a mother lifting a child. One flowing gesture line per figure and a few strokes. " + OLD,
 'b02': "A person seated in a wooden chair, slumped and tired, drawn with only five confident lines and one patch of smudged shadow under the chair. " + OLD,
 'b03': "Four studies of a left hand on one sheet: open, closed in a fist, holding a cup, supporting a cheek. Broken contours, a small patch of tone on the shadow side of each; no hand has all five fingers fully outlined.",
 't07': "A flat Dutch landscape with a low horizon, a dirt path, a wooden fence and a small farmhouse in the distance, drawn with only about twenty lines; sky and fields left as bare paper.",
 't08': "A small thatched cottage between two masses of dark trees: roof and tree trunks in line, tree crowns in scribble and smudged tone with the side of the pencil, the cottage walls left light, sky completely blank paper.",
 'l04': "A young woman seated at a table reading a book next to a window on the left; light falls on her face, hands and the book; the room around her darkens in broad smudged tone. " + OLD,
 'l05': "An old man standing, lit from above: his head and shoulders bright and nearly bare paper, the body getting darker downward, the feet almost lost in shadow. " + OLD,
 'l06': "A low hill with three dark trees against a bright sky on the right; on the left the sky is crossed by diagonal hatching like rain; the plain below in bands from light to shadow.",
 'c04': "Head of an old bearded man in three-quarter view, light from the left: the lit side almost bare paper, the shadow side in mid-tone with a small triangle of light under the eye, deep dark eye socket, beard in loose strokes, a dark smudged background only behind the lit side of the face.",
 'c05': "Head and shoulders of an old woman in a soft hood, looking down: the lit side bare paper with a few short wrinkle lines, the shadow side covered with hatching that follows the folds of the skin; the hood in long loose lines, the coat dissolving into free strokes. " + OLD,
 'c06': "A young woman in a wide-brimmed straw hat, facing the viewer: light, delicate contour lines, the only shadow a soft band under the brim, eyes and mouth in very few strokes, almost all bare paper. " + OLD,
 'a03': "Large self-portrait of a young man shouting with his mouth wide open, messy curly hair as loose scribble, light from the side leaving half the face in shadow, clothing in four lines. " + NOW,
 'a04': "Self-portrait of a man in his thirties leaning one arm on a table edge, body turned sideways, face looking back over the shoulder at the viewer, wearing a soft cap: face crisp and detailed, the wide sleeve in front a dark mass of hatching, the table edge almost bare paper. " + NOW,
 'a05': "Self-portrait of a woman sitting next to a window on the left, drawing in a sketchbook: light falls on her face, her hand and the page; the rest of the room falls into dark smudged shadow. " + NOW,
 'b04': "A young woman asleep, her head resting on her folded arm on the back of a chair, drawn like a brush sketch but with the flat side of a soft pencil: only broad grey patches and a few dark touches; no outlines at all, no contour lines around the face, arm or dress; the shapes are read only from the patches of tone and the bare paper between them. " + OLD,
 'b05': "An adult bending over and holding a toddler by both hands, helping the child take first steps; the curved back of the adult and the upright line of the child are the strongest lines; clothes in a few folds. " + OLD,
 'b06': "An old beggar standing, leaning on a walking stick, in a cloak and hat, his weight on one side; hatching only on his back and under the arm. " + OLD,
 'b07': "A woman standing and carrying a small child who hugs her neck; the figure almost all bare paper with a few lines; behind her on the right a wall in a strong dark smudged tone. " + OLD,
 'b08': "An elephant seen from the side: body as a round heavy mass, legs like columns, the wrinkles of the skin in short strokes that follow the form, a little shadow under the belly.",
 't09': "A small wooden footbridge over a canal with two men leaning on its railing; water, sky and path left as bare paper; less than a tenth of the sheet has any marks. " + OLD,
 't10': "A farmhouse in a snowy landscape with a fence crossing the sheet diagonally toward it; the snow is bare paper; very few lines.",
 'l07': "A figure seated with their back to a bright window: the figure almost a dark silhouette in smudged tone, only the edge of the hair and shoulders catching light; the window bare paper. " + OLD,
 'l08': "A face lit from below by a candle held in front: the chin, the tip of the nose and the underside of the brows bright, the forehead and the background in deep smudged darkness; the small flame is the brightest spot. " + OLD,
 'l09': "A cone seashell lying on a table, light from the left, all shading in fine hatching that wraps around the form, as in an etching.",
 'c07': "Head of an old man wearing a tall fur hat: the hat in dense cross-hatching, nearly black; the face in light hatching; background bare paper. " + OLD,
 'c08': "Profile of an old bearded man facing right, strongly backlit: a bright light source is behind his head, so the whole face and beard are in a dark even mid-to-dark tone, and only a thin bright rim of bare paper runs along the edge of the forehead, nose, lips and beard; the background behind him is light paper. " + OLD,
 'a06': "Double self-portrait: a man in the foreground with stronger contrast and darker lines, and a woman just behind his shoulder, lighter and fainter, both looking at the viewer. " + NOW,
 'a07': "Full-length self-portrait of a person standing in work clothes with a long apron, hands on hips, quick pen-like pencil lines, almost no shading, weight on both legs. " + NOW,
 'b09': "Half figure of a man leaning forward on his folded arms, wearing a floppy hat: thick broken lines, shadow in smudged tone, the face the only area with detail. Absolutely no signature, no monogram, no date, no inscription anywhere on the sheet. " + OLD,
 'b10': "A lion lying down, resting: the mane in smudged tone made with the side of the pencil, the body in broken contour, the paws in four strokes, heavy on the ground.",
 'b11': "Two figures facing each other: one speaking with a raised hand, the other listening with the head bowed; the gesture of the raised hand is the center of the drawing. " + OLD,
 'b12': "An old woman seated, cooking at a small pan, with a group of children around her, each child in a different gesture: reaching, pushing, watching, holding a toy; the old woman in shadow at the center. " + OLD,
 'b13': "A woman lying in a bed propped up on pillows, the bed curtain hanging around her as a dark smudged frame, the figure and sheets light. " + OLD,
 'p08': "A corner of a present-day home with a window on the left; a person sits at a kitchen table peeling fruit; light from the window falls on them and the table; the rest of the room in smudged shadow. " + NOW,
}
MARKS = {
 'm01': "Practice swatch on cream paper: three long curving pencil lines that swell thick and dark in the middle and taper thin at both ends.",
 'm02': "Practice swatch on cream paper: the outline of a draped cloth drawn with a broken contour, thick and dark on the right side, interrupted and faint on the left.",
 'm03': "Practice swatch on cream paper: a patch of straight parallel hatching strokes, all the same direction, getting closer together toward the right.",
 'm04': "Practice swatch on cream paper: a patch of cross-hatching in two and three layers building a deep dark tone.",
 'm05': "Practice swatch on cream paper: loose zig-zag scribble in soft pencil, dense on one side and open on the other, like foliage.",
 'm06': "Practice swatch on cream paper: a broad patch of tone made with the side of a soft pencil lead, grain of the paper visible.",
 'm07': "Practice swatch on cream paper: a broad dark patch of soft pencil smudged smooth with a blending stump, soft edges.",
 'm08': "Practice swatch on cream paper: a few small, very dark short accent touches of soft pencil scattered over a light sketch.",
}
SWATCH = "Monochrome graphite only, the paper fills the entire image, no text, no numbers, no frame, flat scan."
DIAG = {
 'fig-tons': ("A teaching illustration in soft graphite on cream paper: a sphere and a cube side by side on a table, lit from the upper left. Each shows exactly three tones: lit side bare paper, shadow side flat mid-grey, cast shadow dark; tiny black accents where the shapes touch the table. Clean, simple, no text. " + SWATCH, '3:2'),
 'fig-rosto': ("A teaching illustration in soft graphite on cream paper: the same man's head in three-quarter view drawn four times in a row, showing four steps: 1) egg shape with a light line dividing light from shadow; 2) mid-tone filled on the shadow half; 3) a small triangle of light left under the eye on the shadow cheek; 4) finished with eyes, nose, mouth and dark accents. No text, no numbers. " + SWATCH, '21:9'),
 'bad-luz1': ("A pear on a table drawn in pencil and shaded evenly all around its edges with soft grey, no clear light direction, flat and dull, beginner's drawing. " + SWATCH, '3:4'),
 'bom-luz1': ("A pear on a table drawn in pencil with one strong light from the upper left: lit side bare paper, shadow side flat mid-tone, a dark cast shadow to the right. " + SWATCH, '3:4'),
 'bad-luz2': ("A pale standing figure in a long light dress drawn in thin pencil lines against a pale empty background, the figure gets lost and looks flat. " + SWATCH, '3:4'),
 'bom-luz2': ("The same pale standing figure in a long light dress, now against a dark smudged pencil background placed right next to the lit side of the figure; the figure stands out strongly. " + SWATCH, '3:4'),
 'bad-luz3': ("A pencil drawing of an old man seated in a room where every part of the sheet is equally detailed and equally shaded: the floorboards, the wall, the chair, the clothes, the face; busy and confusing. " + SWATCH, '3:4'),
 'bom-luz3': ("A pencil drawing of an old man seated in a room where light and detail concentrate on his face and hands, and everything else fades into simple broad tone and empty paper toward the edges. " + SWATCH, '3:4'),
}
out = {k: {'prompt': BASE + v, 'ar': '3:4'} for k, v in P.items()}
out.update({k: {'prompt': v + ' ' + SWATCH, 'ar': '4:3'} for k, v in MARKS.items()})
out.update({k: {'prompt': v[0], 'ar': v[1]} for k, v in DIAG.items()})
json.dump(out, open('tools/prompts.json', 'w'), ensure_ascii=False, indent=1)
print(len(out))
