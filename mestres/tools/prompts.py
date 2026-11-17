"""Prompts dos desenhos-modelo de Grandes Artistas a Lápis (OpenArt, Nano Banana 2).
python3 tools/prompts.py chave [chave ...] imprime o pedido em JSON para openart_generate_image_batch."""
import json, sys

def hand(who):
    return ("Scan of a real sketchbook page: graphite pencil on plain cream drawing paper filling the whole frame, flat scan of the sheet, "
            f"no board, no pencil, no hands. Drawn quickly from life by a student learning from {who}: searching, restated lines, "
            "visible corrections, uneven pressure, lines thick in shadow and thin in light. Ordinary, unidealized people with plain asymmetric faces; "
            "proportions slightly off; nothing polished, no smooth airbrushed shading, no comic-book, fashion or stock-illustration look. "
            "Lots of bare paper. Graphite only, no color, no text, no letters, no signature, no date, no border. ")

# chave: (mestre, proporção, assunto)
P = {
 'l01': ('a drawing teacher', '3:4', "A practice sheet of pencil warm-up marks arranged in loose rows: long straight lines that go from thin to thick and back to thin by pressure alone; "
         "slow curves and fast curves; a row of short parallel strokes getting closer; zigzags; spirals; a few circles drawn in one motion and restated. Hand-drawn, slightly wobbly, no rulers."),
 'l02': ('Albrecht Dürer in his pen studies of pillows', '3:4', "Six studies of the same soft cushion seen in different positions, scattered on one sheet: squashed, folded, standing on its edge, "
         "pressed by an invisible hand. Each cushion drawn with a firm contour and short curved hatching lines that follow the folds; creases as small dark hooks; no background."),
 'l03': ('Leonardo da Vinci in his sheets of cat studies', '4:3', "A sheet of about twelve small quick sketches of an ordinary house cat: sleeping curled up, washing a paw, stretching, "
         "turning its head, crouching to jump, seen from behind. Each one a few flowing lines of the back and head, some restated, of different sizes and overlapping slightly."),
 'l04': ('Vincent van Gogh in his reed-pen drawings', '4:3', "Three small fishing boats pulled up on a beach, a low horizon with the sea and a sky. Everything made of distinct marks: "
         "firm outlines for the hulls and masts, rows of dots for the sand, short horizontal dashes for the water, little hooks and dashes for the sky, parallel strokes on the hull. "
         "No smudging, no blending, each mark separate, done with a soft pencil pressed hard."),
 'l05': ('Jean-Auguste-Dominique Ingres in his graphite portrait drawings', '3:4', "Full-length portrait of an ordinary middle-aged man standing in a coat and trousers, one hand in a pocket, "
         "a hat held in the other hand: the clothes in very light, fast, single contour lines with a few folds; only the face is carefully modelled with soft fine tone and precise features; "
         "the head is small in the sheet."),
 'l06': ('Egon Schiele in his angular contour drawings of clothed sitters', '3:4', "A young woman sitting on a chair with one knee raised, wearing a striped dress and boots, fully clothed: "
         "a single nervous angular contour line, sharp corners at the elbows and knees, the stripes following the folds, the face drawn with a few hard lines, no shading at all, the chair barely indicated."),
 'f01': ('Albrecht Dürer in his silverpoint self-portrait at thirteen', '3:4', "Self-portrait of a plain teenage boy seen in a mirror, head and shoulders in three-quarter view, wearing a soft cap, "
         "pointing with one hand; very light even lines, fine parallel hatching only in the shadow side; faint light construction lines visible: a vertical axis and horizontal lines through the eyes, nose and mouth."),
 'f02': ('Hans Holbein the Younger in his chalk portrait drawings', '3:4', "Head and shoulders of a plain middle-aged man in three-quarter view wearing a flat cap and a fur collar: "
         "a clean confident contour, soft hatching on the shadow side of the face, the cap and coat only outlined, the eyes and mouth precise; faint construction lines of the head still visible."),
 'f03': ('Leonardo da Vinci in his silverpoint studies of hands', '4:3', "A sheet with four studies of the same pair of ordinary hands: resting crossed on a table, one hand holding a cup, "
         "one hand open palm up, fingers bent. Fine lines, light parallel hatching from left to right, knuckles and nails simple, some fingers restated."),
 'f04': ('Vincent van Gogh in his black chalk figure drawings of 1882', '3:4', "An old man in work clothes sitting on a wooden chair, leaning forward, elbows on knees, hands hanging, "
         "seen from the side; heavy dark contour, the coat in broad strokes, the boots big and flat on the floor, the floorboards in a few lines."),
 'f05': ('Edgar Degas in his drawings of dancers', '3:4', "A young woman in a leotard, practice skirt and ballet tights bending forward to tie the ribbon of her shoe, one foot on a bench, fully clothed: "
         "long flowing lines for the back and the bent leg, several restated contour lines, a little tone under the skirt, the face hidden."),
 's01': ('Leonardo da Vinci in his drapery studies', '3:4', "A heavy cloth thrown over the knees of a seated figure, the figure itself not drawn, only the drapery: deep folds falling to the floor, "
         "soft continuous tone made with the side of the pencil, light from the upper left, the darkest darks in the deepest folds, highlights left as paper."),
 's02': ('Albrecht Dürer in his brush drawing of praying hands on blue paper', '3:4', "Two ordinary hands with joined palms seen from the side, in sleeves, drawn on mid-grey toned paper "
         "with graphite for the shadows and white pencil for the lights: fine hatching following the form, white strokes on the knuckles, fingertips and the lit side, the grey paper as the middle tone. Grey paper, graphite and white only."),
 's03': ('Michelangelo in his black chalk heads', '3:4', "Head and shoulders of a woman in a wrapped headscarf, looking down to the side, three-quarter view, "
         "softly modelled with dense fine hatching that turns into tone, light from the upper left, the shadow side of the face deep but transparent, the scarf in looser lines."),
 's04': ('Rembrandt in his brush drawings', '4:3', "A person asleep in an armchair, head resting on a hand: drawn almost only with broad flat masses of tone made with the side of a soft pencil, "
         "three values only, paper for the light, a middle grey, and a few dark accents; no closed contour lines, the face just two or three marks."),
 's05': ('John Singer Sargent in his charcoal portraits', '3:4', "Head and shoulders portrait of a man with untidy hair and round glasses, three-quarter view: big soft masses of dark for the hair and the coat, "
         "the face modelled with a few broad planes of tone, smudged and then lifted with an eraser for the lights, the background a loose patch of tone behind the lit side."),
 'r01': ('Albrecht Dürer in his charcoal portrait of his mother', '3:4', "Head and shoulders of a very old thin woman in a headscarf, looking straight out, hollow cheeks, prominent bones, "
         "sunken eyes, unflattering and truthful; firm dark lines for the bone structure, the scarf in broad strokes, light from the left."),
 'r02': ('Leonardo da Vinci in his silverpoint head of a young woman', '3:4', "Head of a young person turning to look back over the shoulder towards the viewer, three-quarter view, "
         "fine parallel hatching from upper left to lower right, the shoulder and hair in a few loose quick lines, the eyes and mouth delicate; an ordinary face, not beautiful, not glamorous."),
 'r03': ('Hans Holbein the Younger in his chalk portraits of women', '3:4', "Head and shoulders of a plain middle-aged woman wearing a white linen cap and a high collar, three-quarter view, "
         "eyes lowered: precise contour, soft hatching on the shadow side of the face, the cap and collar only outlined."),
 'r04': ('Egon Schiele in his drawings of clothed men', '3:4', "Half-length portrait of a thin young man in a jacket with his arms crossed and his shoulders raised, head tilted: "
         "angular nervous contour, big bony hands, the jacket in sharp broken lines, the face with intense eyes and a few hard lines, no shading."),
 'r05': ('Michelangelo in his red chalk studies for the Sistine ceiling', '3:4', "Study sheet: a young man in a sleeveless vest seen from behind, twisting at the waist and lifting his arms, "
         "the shoulder blades and the arms modelled with hatching that follows the muscles; at the side, smaller separate studies of his hand and his foot. Fully clothed, vest and trousers."),
 'r06': ('Edgar Degas in his charcoal studies of dancers', '4:3', "Two young women in rehearsal clothes, leotards and practice skirts, fully clothed, stretching side by side, one with an arm raised, "
         "the other bending to touch her ankle: long fluid contour lines, restated several times, a little broad tone on the skirts, no faces."),
 'r07': ('Vincent van Gogh in his black chalk drawings of peasants digging', '3:4', "A gardener in work clothes and a cap digging with a spade, foot on the blade, back bent, "
         "seen from the side: heavy contour, the weight on the front leg, a few strokes of earth, no details of the face."),
 'c01': ('Leonardo da Vinci in his first landscape drawing', '4:3', "A wide valley seen from a hilltop: a rocky hill in the foreground drawn with quick curving strokes, "
         "a river plain with fields in the distance made of tiny horizontal strokes, small trees as dots and squiggles, far hills on the horizon as a light line."),
 'c02': ('Rembrandt in his pen landscape drawings', '4:3', "A small farmhouse among trees by a path: the house in a few lines, the trees in loose scribbled masses, the path and the fields as almost bare paper, "
         "a dark accent in the doorway, a low horizon, most of the sheet empty."),
 'c03': ('Vincent van Gogh in his reed-pen drawings of the plain of La Crau', '4:3', "A wide flat plain seen from a hill, with fields like a patchwork reaching to a range of low hills: "
         "each field filled with a different mark, dots, dashes, short parallel strokes, little crosses; a road with a small cart; marks get smaller towards the horizon; the sky blank."),
 'c04': ('Jean-Auguste-Dominique Ingres in his graphite family portraits', '4:3', "A family of four in a present-day living room: a father standing, a mother seated, a teenager leaning on the sofa, "
         "a child sitting on the floor: clothes and furniture in light quick contour, only the four faces carefully modelled, the group linked by touching hands and shoulders."),
 'c05': ('John Singer Sargent in his pencil studies for a society portrait', '3:4', "A woman in a long dark evening dress standing in profile with one hand resting on a small table, "
         "the head turned sideways: a few long confident lines for the silhouette of the dress, the arm and the neck, the dress partly filled with loose dark strokes, almost no detail."),
}

if __name__ == '__main__':
    print(json.dumps([{'model': 'nano-banana-2', 'mode': 'text2image',
                       'params': {'aspectRatio': P[k][1], 'resolution': '1K', 'prompt': hand(P[k][0]) + P[k][2]}} for k in sys.argv[1:]], ensure_ascii=False))
