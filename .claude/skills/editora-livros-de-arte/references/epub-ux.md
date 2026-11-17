# EPUB sem incômodo: estudo de experiência de leitura

Feito em 17/11/2026 sobre *Grandes Artistas a Lápis*, depois de o autor notar que "a diagramação muda drasticamente no EPUB": capa mal inserida, imagens de exercício pequenas no PDF e enormes no EPUB.

## O que o leitor sente

O PDF é uma página desenhada: cada imagem tem um tamanho que diz sua importância (a obra da aula grande, o modelo do exercício médio, o recorte para copiar pequeno, os balões de detalhe menores ainda). O EPUB refluível perde a página, e se nada for dito sobre o tamanho, **toda imagem vira "largura da tela"**. O leitor sente isso como:

1. **Hierarquia achatada.** Um recorte de 3 cm no PDF ocupa a tela inteira do celular; o exercício parece mais importante que a obra, e a página fica com ar de rascunho.
2. **Ampliação sem qualidade.** Recorte pequeno esticado até a largura da tela mostra o pixel e a compressão.
3. **Capa torta.** Capa como `<img>` com altura máxima deixa faixa branca embaixo ou corta, conforme a tela.
4. **Tripa de texto.** Componentes montados com flex ou grid no PDF (galeria, comparações, marcas, linha das vidas) viram texto corrido sem estilo.
5. **Páginas que só servem impressas.** Folha de progresso para marcar com lápis, referências "p. 42" que não existem na tela.
6. **Modo noturno quebrado.** Cor de texto fixa e fundos coloridos ficam ilegíveis quando o leitor inverte a tela.

## Regras para os livros da série

### Capa
- Página de capa só no EPUB das outras lojas: um `<svg>` com `viewBox` no tamanho da imagem (1600 × 2560) e `preserveAspectRatio="xMidYMid meet"`, item marcado `properties="svg"` no manifesto. A capa fica centrada e inteira em qualquer tela.
- Versão Kindle (`kindle=True`): **sem página de capa**. O Kindle mostra a capa a partir do metadado (`cover-image`) e a página extra vira uma capa repetida.

### Tamanho de cada imagem por papel (a hierarquia do PDF traduzida em largura)

| Papel | Exemplo | Horizontal | Vertical |
|---|---|---|---|
| Obra da aula (`ob-`) | `img/n1_boats.jpg` | 100 % | 72 % |
| Desenho-modelo (`md-`) | `img/l01.jpg`, `img/st-...` | 82 % | 58 % |
| Recorte para copiar (`cp-`) | `img/cp-....jpg` | 66 % | 44 % |
| Abertura de nível (`ab`) | `img/ab_...` | 80 % | 80 % |
| Retrato da galeria | tabela, coluna da imagem | 34 % da tabela | |
| Comparação, três mestres | tabela, coluna da imagem | 42 % da tabela | |
| Marcas dos mestres | tabela, coluna da imagem | 30 % da tabela | |
| Balões de detalhe | tabela de três | ~30 % cada | |

A orientação sai da própria imagem (largura ≥ altura → horizontal). O `kindle_html` põe as classes pelo caminho do arquivo; sem classe, a imagem não ganha 100 % sozinha.

### Componentes
- Tudo que fica lado a lado no PDF vira **tabela** no EPUB (o Kindle ignora flex, grid e largura em porcentagem de `div`).
- A linha das vidas vira tabela de duas colunas (anos | mestre e fato), sem barra desenhada.
- As comparações "O mesmo problema, três mestres" entram no EPUB depois do último capítulo de cada nível, como no PDF.
- Sai do EPUB: folha de progresso, referências de página, ícones, a linha decorativa "Para praticar" duplicada.

### Cor, fonte e modo noturno
- `body` sem `color`; links com `color:inherit`. O leitor escolhe tema.
- Nada de fundo colorido em bloco de texto: a caixa "Na vida dele" e a linha das vidas usam só borda à esquerda na cor do nível.
- Fontes com nome próprio (`LivroSerif`, `LivroDisp`, `LivroSans`), nunca `Serif` ou `Sans`.

### Peso (custo de entrega na Amazon)
- Loja Amazon: fotos a 1000 px no lado maior, JPEG qualidade 76 progressivo. Abaixo disso a obra perde o traço em tablet.
- Balões em PNG com transparência: **256 cores** (quantização). Um recorte de desenho não muda a olho e cai de ~180 KB para ~30 KB. Em 17/11/2026 isso tirou 12 MB do EPUB da Amazon (29,4 → 16,8 MB).
- Antes de mudar a resolução, veja o que pesa (`unzip -lv` ou o resumo de `verifica_epub.py`): o vilão costuma ser um tipo de arquivo, não as fotos.

### Kindle de tinta eletrônica (Kindle básico, Paperwhite)
- **A capa não preenche a tela.** A tela do Kindle básico é 1072 × 1448 (1,35:1) e a capa é 1,6:1: ela entra inteira, encaixada pela altura, com uma faixa branca de uns 8 % de cada lado. Nos celulares (cerca de 2:1) as faixas ficam em cima e embaixo. Não há proporção que preencha todas as telas, e a KDP usa a mesma capa na loja: mantenha 1,6:1.
- O livro abre no início do conteúdo, não na capa; a capa aparece na biblioteca, na tela de bloqueio (modelos sem anúncios) e em "Ir para > Capa".
- **16 tons de cinza.** A cor de cada nível some: o nível precisa estar escrito ("Nível 1 · Linha e contorno"), nunca indicado só pela cor. Desenhos muito claros (ponta de prata, sanguínea fraca) ficam suaves; não use um desses como única imagem de uma explicação.
- O fundo creme da capa vira um cinza claro diferente da faixa branca. É aceitável e comum.

### Amostra grátis (Amazon)
- A Amazon dá os primeiros 10 % do e-book como amostra. Quem baixa precisa ver **pelo menos uma aula ou um exercício**; uma amostra só de prefácio e galeria não vende um livro de exercícios. O `verifica_epub.py` diz onde a amostra termina. Se a primeira aula ficar de fora, leve para depois no EPUB o que é consulta (galeria longa, linha do tempo).

## Como conferir
1. `previa_epub.py` nas duas telas, celular e Kindle: nada transborda; olhe a folha inteira procurando imagem que ocupa a tela sem ser a obra da aula.
2. Abra lado a lado uma aula no PDF e a mesma aula na prévia: a ordem dos tamanhos (obra > modelo > recorte > balão) tem de ser a mesma.
3. Capa: sem faixa branca na prévia de celular; na versão Kindle, nenhuma página de capa no começo.
4. Modo noturno: no Kindle Previewer, ligue o fundo preto e passe pela galeria, uma aula e a linha das vidas.
5. Tinta eletrônica: no Kindle Previewer escolha um Kindle (não tablet) e veja a capa e uma aula em cinza.
6. Frases do papel: `verifica_epub.py` aponta "imprima", "p. 42", "página ao lado". Cada uma ganha uma versão de tela no `kindle_html` ou sai do texto.

## PDF, EPUB e a Amazon
- A Amazon **não vende PDF para baixar**. Na KDP o PDF serve para o livro impresso (brochura e capa dura).
- Um PDF pode virar e-book de **layout fixo (Print Replica)** pelo Kindle Create: fica igual ao PDF, mas o texto não muda de tamanho e só abre em parte dos aparelhos (apps Kindle e tablets Fire). Serve para quem quer a página exata; não substitui o EPUB.
- O EPUB refluível é o que alcança todos os Kindles e as outras lojas. A recomendação da série: **EPUB refluível bem diagramado para o Kindle e as lojas, PDF para o impresso**.
