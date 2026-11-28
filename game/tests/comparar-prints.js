// comparar-prints.js — diferença numérica entre dois prints do jogo.
//
// Existe para o upgrade do Three.js (r144 -> r186): o jogo tem 433 literais de cor e, do r152
// em diante, THREE.ColorManagement converte sRGB para linear por padrão. "Está igual?" não se
// responde de olho — se responde medindo. Decodifica as duas imagens num canvas do Chromium
// (sem dependência nova) e devolve a diferença média e máxima por canal.
//
// Uso: node game/tests/comparar-prints.js antes.png depois.png [limiar]
//   limiar   diferença média aceitável em níveis de 0 a 255 (padrão 2)
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');

const [a, b, limiarArg] = process.argv.slice(2);
if (!a || !b) { console.error('uso: node game/tests/comparar-prints.js antes.png depois.png [limiar]'); process.exit(2); }
const LIMIAR = parseFloat(limiarArg || '2');
for (const f of [a, b]) if (!fs.existsSync(f)) { console.error('não existe: ' + f); process.exit(2); }

const dataUri = f => 'data:image/png;base64,' + fs.readFileSync(f).toString('base64');

(async () => {
  const navegador = await chromium.launch();
  const pg = await navegador.newPage();
  const r = await pg.evaluate(async ([ua, ub]) => {
    const carrega = src => new Promise((ok, erro) => { const i = new Image(); i.onload = () => ok(i); i.onerror = erro; i.src = src; });
    const [ia, ib] = await Promise.all([carrega(ua), carrega(ub)]);
    if (ia.width !== ib.width || ia.height !== ib.height)
      return { erro: `tamanhos diferentes: ${ia.width}x${ia.height} contra ${ib.width}x${ib.height}` };
    const px = img => { const c = document.createElement('canvas'); c.width = img.width; c.height = img.height;
      const x = c.getContext('2d', { willReadFrequently: true }); x.drawImage(img, 0, 0);
      return x.getImageData(0, 0, c.width, c.height).data; };
    const pa = px(ia), pb = px(ib);
    let soma = 0, max = 0, n = 0, diferentes = 0;
    for (let i = 0; i < pa.length; i += 4) {
      let d = 0;
      for (let k = 0; k < 3; k++) d = Math.max(d, Math.abs(pa[i + k] - pb[i + k]));
      soma += d; if (d > max) max = d; if (d > 8) diferentes++; n++;
    }
    return { largura: ia.width, altura: ia.height, media: soma / n, max, pctDiferente: (100 * diferentes) / n };
  }, [dataUri(a), dataUri(b)]);
  await navegador.close();

  if (r.erro) { console.error('FALHA ' + r.erro); process.exit(1); }
  console.log(`${path.basename(a)} contra ${path.basename(b)}  (${r.largura}x${r.altura})`);
  console.log(`  diferença média .... ${r.media.toFixed(2)} níveis (limiar ${LIMIAR})`);
  console.log(`  diferença máxima ... ${r.max} níveis`);
  console.log(`  pixels com desvio > 8 niveis: ${r.pctDiferente.toFixed(2)}%`);
  if (r.media > LIMIAR) { console.log(`\nFALHA a imagem mudou mais que o limiar — veja os dois prints antes de aceitar.`); process.exit(1); }
  console.log(`\nok a imagem está dentro do limiar.`);
})().catch(e => { console.error('comparar-prints.js quebrou: ' + e.message); process.exit(2); });
