#!/usr/bin/env python3
"""Abre cada página de um EPUB num navegador sem janela, em tela de celular (390 × 844) e de Kindle Paperwhite
(1072 × 1448 px, mostrado a 536 × 724), mede o que transborda para o lado e monta folhas de contato.

Uso: python3 previa_epub.py livro.epub pasta-de-saida
Saída: <pasta>/epub-celular.jpg, <pasta>/epub-kindle.jpg e a lista de páginas com conteúdo mais largo que a tela.
Não substitui o Kindle Previewer (que mostra a conversão real para KFX): é a conferência rápida, a cada build."""
import os, sys, zipfile, tempfile, json, subprocess
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw

epub, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
td = tempfile.mkdtemp(); zipfile.ZipFile(epub).extractall(td)
NS = {'c': 'urn:oasis:names:tc:opendocument:xmlns:container', 'o': 'http://www.idpf.org/2007/opf'}
opf_p = ET.parse(os.path.join(td, 'META-INF/container.xml')).find('.//c:rootfile', NS).get('full-path')
opf = ET.parse(os.path.join(td, opf_p)); base = os.path.join(td, os.path.dirname(opf_p))
man = {i.get('id'): i.get('href') for i in opf.find('o:manifest', NS)}
docs = [os.path.join(base, man[s.get('idref')]) for s in opf.find('o:spine', NS)]
js = r"""const { chromium } = require('playwright'); const fs = require('fs');
const [docs, out] = [JSON.parse(process.argv[2]), process.argv[3]]; const telas = [['celular', 390, 844, 2], ['kindle', 536, 724, 2]];
(async () => { const b = await chromium.launch(); const res = [];
  for (const [nome, w, h, s] of telas) { const pg = await b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
    for (let i = 0; i < docs.length; i++) { await pg.goto('file://' + docs[i]); await pg.waitForTimeout(150);
      const r = await pg.evaluate(() => { const de = document.documentElement; const largos = [...document.querySelectorAll('img,table,figure,div,p')]
          .filter(e => e.getBoundingClientRect().right > innerWidth + 2).length; return { sw: de.scrollWidth, cw: de.clientWidth, sh: de.scrollHeight, largos }; });
      res.push({ tela: nome, doc: i, ...r });
      await pg.screenshot({ path: `${out}/_${nome}_${String(i).padStart(3, '0')}.png` }); }
    await pg.close(); }
  fs.writeFileSync(out + '/_previa.json', JSON.stringify(res)); await b.close(); })();"""
open(os.path.join(td, 'p.js'), 'w').write(js)
subprocess.run(['node', os.path.join(td, 'p.js'), json.dumps(docs), os.path.abspath(out)], check=True)
res = json.load(open(os.path.join(out, '_previa.json')))
prob = [r for r in res if r['sw'] > r['cw'] + 2 or r['largos']]
for tela in ('celular', 'kindle'):
    fs = sorted(f for f in os.listdir(out) if f.startswith(f'_{tela}_'))
    ims = [Image.open(os.path.join(out, f)).convert('RGB') for f in fs]
    for im in ims: im.thumbnail((195, 422))
    cols = 8; rows = (len(ims) + cols - 1) // cols; W, H = 200, 440
    c = Image.new('RGB', (cols * W, rows * H), '#555'); d = ImageDraw.Draw(c)
    for k, im in enumerate(ims):
        x, y = (k % cols) * W, (k // cols) * H; c.paste(im, (x, y))
        ruim = any(r['tela'] == tela and r['doc'] == k for r in prob)
        d.text((x + 3, y + 425), f'{k}' + (' TRANSBORDA' if ruim else ''), fill='#ff6060' if ruim else 'white')
    c.save(os.path.join(out, f'epub-{tela}.jpg'), quality=82)
    for f in fs: os.remove(os.path.join(out, f))
os.remove(os.path.join(out, '_previa.json'))
print(f'{len(docs)} documentos em 2 telas. Folhas: {out}/epub-celular.jpg e {out}/epub-kindle.jpg')
if prob:
    for r in prob: print(f'[AVISO] {r["tela"]}: documento {r["doc"]} ({os.path.basename(docs[r["doc"]])}) mais largo que a tela: {r["sw"]}px / {r["cw"]}px, {r["largos"]} elementos')
else:
    print('[OK] nada transborda para o lado em nenhuma das duas telas')
