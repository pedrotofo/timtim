---
name: ilustrar-fala
description: >-
  Cria os motions que ilustram o que o cliente fala no vídeo, sincronizados palavra por palavra e
  com fundo transparente para pôr por cima no Premiere: mapa do Brasil com os estados citados
  acendendo e pino na cidade, mapa-múndi, EUA e outros países, rota entre cidades, lugar real em
  satélite, número ou contador que cresce, gráfico, linha do tempo, lista que entra item a item,
  citação em tipografia, produto ou logo. Lê a lista "Para ilustrar" da /decupagem, gera cada motion
  com HyperFrames, confere sobre o vídeo e entrega .mov ProRes 4444 com alfa e o insertos.json para
  o /premiere-xml. Use quando pedirem "ilustra essa fala", "anima o mapa que ela cita", "faz um
  motion para quando ele fala do número", "põe um gráfico aqui", "cria os grafismos do vídeo",
  "motion por cima da entrevista", "lower third", ou depois de uma decupagem.
---

# Ilustrar a fala

O cliente fala; o motion mostra o que ele está dizendo, no instante em que diz. Cada ilustração é
um vídeo curto, transparente, que entra sobre a imagem dele no Premiere.

Regras:

1. **A fala manda no tempo.** Cada passo da animação cai numa palavra, com o tempo vindo da
   transcrição. Nunca chute tempo.
2. **Não cubra o rosto.** Olhe um quadro do vídeo antes de escolher onde o motion fica.
3. **Mostre o que é real.** Lugar real, produto real, logo real. Desenho genérico só para ideia
   abstrata.
4. **Pouco e claro.** Uma ideia por motion, legível no celular (texto com 28 px ou mais em 1080p).
5. **Use o que existe antes de construir.** Biblioteca do HyperFrames primeiro
   (`/hyperframes-registry`), depois os geradores desta skill, e só então desenhe do zero.

## Passo 0: entradas

- `decup/decupagem.json` e `decup/transcricao.json` (da `/decupagem`). Sem decupagem, rode a
  `/decupagem` antes ou, para um trecho só, transcreva esse trecho.
- O vídeo do cliente, para ver o enquadramento e conferir o resultado.
- A marca: se existir `brand.md`/`MOTION.md` (`/brand-intake`), use as cores e a fonte dele. Senão
  pergunte uma vez as cores e a fonte do cliente, ou use o padrão (branco, destaque `#F2A93B`,
  Inter).

## Passo 1: planejar cada ilustração

Para cada item de `ilustracoes`:

1. **Tempo.** Ache as palavras-gatilho:
   ```bash
   python3 <esta-skill>/scripts/achar_palavras.py decup/transcricao.json Ceará Pernambuco Bahia --de 10 --ate 16
   ```
   O motion começa cerca de 0,5 s antes da primeira palavra-gatilho (`inicio`) e termina cerca de
   0,8 s depois que a ideia acaba. Dentro do motion, cada passo usa `t = palavra - inicio`.
2. **Lugar no quadro.** `ffmpeg -ss <inicio> -i VIDEO -frames:v 1 quadro.jpg` e olhe: cliente à
   esquerda, motion na direita, e vice-versa. Vertical (9:16): motion no terço de cima.
3. **Tipo e ferramenta:**

| A fala | Ferramenta |
|---|---|
| Estados ou regiões do Brasil, cidade brasileira, rota entre cidades | `scripts/mapa_brasil.py` (abaixo) |
| Países, mundo | bloco `world-map` da biblioteca (`npx hyperframes add world-map`) |
| EUA | `us-map`, `us-map-bubble`, `us-map-flow` |
| Lugar real (a fábrica, o bairro, um zoom do globo até a rua) | mapa de satélite do HyperFrames: `/hyperframes`, `references/film.md` › "Maps and real places" (`bake-basemap.mjs`) |
| Número, crescimento ("de 1.200 para 40 mil") | contador ou gráfico: `npx hyperframes catalog --query "count up number"` / `"bar chart"`, guia `references/types/data.md` |
| Datas, etapas | `catalog --query "timeline"` |
| Lista, passos, "três coisas" | `catalog --query "list reveal"` ou tipografia cinética |
| Frase forte, palavra-chave | `catalog --query "kinetic type"`, `"lower third"`; legendas: `references/captions.md` |
| Produto, site, app, logo | imagem real (`/media-use`, `npx hyperframes capture <url>` para site) |
| Efeito de marca, interface, partículas | `/motion-effects` (16 efeitos prontos) |

Mostre o plano antes de produzir: uma linha por ilustração (tempo, tipo, o que acontece em cada
palavra, onde fica). Com muitas ilustrações, produza primeiro uma, para a pessoa aprovar o estilo.

## Passo 2: produzir

Um projeto HyperFrames por ilustração em `motions/<id>-<tipo>/`, sempre **1920×1080 (ou o tamanho
do vídeo), no fps do vídeo, com fundo transparente** (sem cor no `body` nem no `#root`).

### Mapa do Brasil

```bash
python3 <esta-skill>/scripts/mapa_brasil.py motions/I1.json --saida motions/I1-mapa
```

`I1.json`, com os tempos relativos ao começo do motion:

```json
{"duracao": 3.6, "fps": 25,
 "area": {"x": 1010, "y": 90, "w": 860, "h": 900},
 "foco": ["CE", "PE", "BA"],
 "destaques": [{"uf": "CE", "t": 0.6}, {"uf": "PE", "t": 1.3}, {"uf": "BA", "t": 2.25}],
 "pinos": [{"nome": "Fortaleza", "lat": -3.7319, "lon": -38.5267, "t": 0.45}],
 "rotas": [{"de": [-3.73, -38.53], "para": [-23.55, -46.63], "t": 1.0, "dur": 1.2}],
 "cores": {"destaque": "#F2A93B"}, "placa": true}
```

- `foco`: siglas ou regiões (`N`, `NE`, `CO`, `SE`, `S`, `BR`). A câmera sai do Brasil inteiro e
  vai até lá. Sem `foco`, vai até os estados destacados.
- Coordenadas de cidades: use as que você souber com segurança (capitais) ou pergunte. Não invente.
- Os contornos vêm da malha oficial do IBGE (`dados/brasil-estados.json`; para refazer, veja
  `dados/gerar-brasil-estados.mjs`).
- O resultado é HTML comum: ajuste cores, tamanhos e easing direto no `index.html` gerado.

### Outros tipos

Siga `/hyperframes` (contrato, `check`, revisão) e `/hyperframes-registry` (blocos prontos). Para
ficar transparente, tire o fundo do bloco (`background` do root e do `body`) e mantenha só os
elementos. Sincronize cada tween com os tempos do Passo 1.

## Passo 3: conferir e renderizar

```bash
cd motions/I1-mapa
npx hyperframes check                       # corrija todo erro (contraste, texto pequeno, contrato)
npx hyperframes render --format mov --fps 25 --output ../I1-mapa.mov   # ProRes 4444 com alfa
cd ../.. && bash <esta-skill>/scripts/previa.sh VIDEO motions/I1-mapa.mov <inicio> motions/I1-previa
```

Olhe `I1-previa.jpg` (três quadros com o motion sobre o cliente) antes de mostrar. Confira se não
cobre o rosto, se o texto lê, se cada estado acende na palavra. Avisos de `first_frame_empty` e
`line_unread` não se aplicam a um motion que entra e sai com a fala.

O `.mov` fica grande (cerca de 10 MB por segundo em 1080p). É o formato certo para o Premiere; não
converta para MP4, que perde a transparência.

## Passo 4: entregar

Escreva `motions/insertos.json`, um item por motion pronto, com `inicio` no tempo do vídeo original:

```json
[{"arquivo": "I1-mapa.mov", "inicio": 11.95, "duracao": 3.6, "nome": "I1 mapa CE PE BA"}]
```

Depois ofereça `/premiere-xml`, que põe cada motion na V2, no tempo certo, sobre o corte. Mostre à
pessoa a prévia (`I1-previa.mp4` ou `.jpg`) de cada motion.
