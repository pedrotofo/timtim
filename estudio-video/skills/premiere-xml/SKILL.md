---
name: premiere-xml
description: >-
  Leva o trabalho para o Adobe Premiere Pro como uma sequência editável (XML do Final Cut Pro 7,
  Arquivo > Importar): a mídia original cortada nos trechos mantidos (sem silêncios, "éé" e
  retakes), os motions com fundo transparente na V2 exatamente no tempo da fala, e um marcador em
  cada fala boa, ponto de ilustração e trecho a conferir da decupagem. Nada é renderizado nem
  achatado. Use quando pedirem "manda para o Premiere", "XML para o Premiere", "timeline do
  Premiere", "marcadores no Premiere", "quero editar no Premiere", "importar o corte", ou ao fim de
  /decupagem, /video-editing-skill ou /ilustrar-fala quando a pessoa finaliza no Premiere.
---

# Premiere XML

A pessoa finaliza no Premiere. Esta skill entrega o que as outras fizeram como uma timeline que
ela abre e continua editando, em vez de um MP4 fechado.

## Entradas

| Arquivo | De onde vem | Obrigatório |
|---|---|---|
| `decupagem.json` | `/decupagem` | sim: a mídia, o fps, os marcadores |
| `manifest.json` (`kept_spans`) | `/video-editing-skill` depois do render, ou `cortes.json` (`[[inicio, fim], ...]`) escrito por você | não: sem ele, a mídia vai inteira |
| `insertos.json` | `/ilustrar-fala` | não |

Os tempos são sempre da mídia original; o script leva para a timeline cortada. Um motion que caiu
num trecho cortado fica de fora, com aviso.

## Gerar

```bash
python3 <esta-skill>/scripts/gerar_xml.py --decupagem decup/decupagem.json \
  --manifest edited/manifest.json --insertos motions/insertos.json \
  --raiz "D:/Clientes/Marina" --nome "Marina - corte 1" --saida marina.xml
```

- `--raiz`: a pasta, **no computador da pessoa**, onde vão estar o vídeo original e os `.mov`.
  Pergunte uma vez ("em que pasta você vai guardar o bruto e os motions?"). Sem ela, o Premiere
  pede para localizar a mídia na primeira vez; aponte o arquivo e ele acha o resto.
- `--nota-minima 3`: só as falas ★★★ ganham marcador.
- fps, tamanho e canais de áudio vêm do próprio arquivo (ffprobe); se o vídeo não estiver nesta
  máquina, vêm de `decupagem.json`.

## Conferir antes de entregar

```bash
python3 -c "import xml.dom.minidom as m; m.parse('marina.xml'); print('ok')"
```

Se `opentimelineio` e `otio-fcp-adapter` estiverem instalados, leia o XML de volta e confira os
tempos dos clipes, dos motions e dos marcadores (é um leitor independente do Premiere):

```bash
python3 -c "import opentimelineio as o; t=o.adapters.read_from_file('marina.xml', adapter_name='fcp_xml'); print(t)"
```

## Entregar

Diga à pessoa, nesta ordem:

1. Coloque o vídeo original e a pasta `motions/` em `--raiz` (os mesmos nomes de arquivo).
2. No Premiere: **Arquivo > Importar** > `marina.xml`. Vem uma sequência nova com o mesmo nome.
3. Na V1, os trechos mantidos; os cortes são cortes de verdade e dá para abrir qualquer um com o
   Trim. Na V2, os motions com transparência. Os marcadores ficam na régua da sequência.
4. Se o Premiere pedir para localizar a mídia, aponte o arquivo original; os outros ele acha.

Não prometa cor nos marcadores nem efeitos e transições: o XML do FCP7 leva cortes, camadas e
marcadores; o resto se faz no Premiere.
