# Como os livros de arte são feitos e diagramados

O conteúdo (artista, obras, texto, exercícios, desenhos-modelo) segue a skill `livro-a-lapis`. Aqui está o que a editora precisa saber para produzir e conferir os arquivos.

## Duas famílias, uma identidade

- **Monográfico** (`livro/` Van Gogh, `rembrandt/` Rembrandt): Parte I a vida, Parte II a linguagem em 8 capítulos com os *Primeiros passos*, Parte III os estudos em níveis 2 a 4, consulta. Livro novo de um artista: copiar `rembrandt/`.
- **Coletivo** (`mestres/` Grandes Artistas): abertura com a galeria dos dez mestres, a linha das vidas e os dez traços; cinco níveis (Linha e contorno, Forma e proporção, Luz e sombra, Rosto e figura, Composição), cada um com aulas de uma obra e dois exercícios (estudo com modelo e cópia de um trecho), uma página "O mesmo problema, três mestres" no fim de cada nível; consulta com marcas dos mestres, glossário, vozes citadas, fontes, folha de progresso, catálogo, índice.

Em comum: formato 6 × 9 pol.; papel `#EEEAE0`, tinta `#1E1913`; EB Garamond para o texto e os títulos de capa; Archivo e Archivo Black para números, rótulos e legendas; uma cor de destaque por livro (Van Gogh ocre `#BF8A5A`, Rembrandt siena `#9A4A2C`, Grandes Artistas um azul por nível, de `#5B87A6` a `#243B5E`). Caixa "Na vida dele", balões circulares de detalhe, linha "Para praticar", exercícios com Tempo / Material / Teoria / Pronto quando.

## Como o livro é montado

```
<livro>/
  build.py            monta tudo: PDF (WeasyPrint), EPUB 3, capa do e-book
  data.json           gerado por tools/make_data.py (exercícios, obras, fichas)
  src/*.md            texto, em seções <!-- id: x | Título | tipo -->; {{obra:chave}} insere obra com legenda
  tools/              obras.py (catálogo), make_data.py, recortes.py (cópias, balões, linha do tempo),
                      capas*.py, paper.py (uniformiza os modelos), prep_obras.py, aberturas.py
  img/                tudo o que entra no livro (obras preparadas, modelos, recortes, capas)
  obras/, gen/        originais baixados e gerados (fora do git)
  out/                PDF, EPUBs, capa do e-book, conferência
```

Tipos de seção: `front` (prefácio, como usar), `part` (abertura de parte ou nível), `chapter` (capítulo ou aula), `back` (consulta). O build insere sozinho os exercícios depois de cada aula, as comparações no fim de cada nível, o catálogo, o índice e os créditos.

## Diagramação do PDF (valores atuais do `PDF_CSS`)

- Página 6 × 9 pol.; margens: topo 0,62, base 0,82, interna 0,72, externa 0,55 pol. (passa com folga na regra KDP até 300 páginas).
- Corpo EB Garamond 10,3 pt / 1,42, justificado, hifenizado (`hyphens:auto`). Falta nos três livros, em 17/11/2026: `hyphenate-character:"-"` (sem ele o hífen sai em DejaVu) e renomear a família `Sans` (sem isso a Archivo vira Inter).
- Rodapé com número e nome da seção (`string-set`), sem rodapé na primeira página de cada capítulo e nas páginas cheias.
- Páginas cheias (`page:full`): capa, aberturas em grade, página de imagem sangrada, fim e contracapa. Páginas de parte (`page:partN`) com fundo da cor do nível.
- Abertura de capítulo: rótulo, número grande na cor, título, a obra logo abaixo com balões ao lado (obra vertical) ou embaixo (obra horizontal), "Na vida dele" depois. Nada de `break-before` no bloco da obra: ele fica onde couber.
- Exercícios: dois por página (meia página cada); um sozinho ocupa a página inteira; exercício com etapas tem página própria com o modelo grande e três etapas ao lado.

## Do PDF de leitura ao miolo impresso

O PDF de leitura (`build.py pdf`) não serve para a gráfica. Para o miolo impresso, o build precisa de um modo de impressão:

1. `@page{size:6.125in 9.25in}` e as margens somadas à sangria (topo e base +0,125; externa +0,125; a interna não muda).
2. Toda página cheia passa a medir 6,125 × 9,25 com a imagem ou a cor indo até a borda, posicionada para o corte cair 0,125 pol. dentro do lado de fora, do topo e da base.
3. Tirar a capa, a contracapa e qualquer elemento de capa do miolo. Começar pela folha de rosto (página ímpar, à direita).
4. Gerar as imagens de página inteira (aberturas em grade, obras sangradas) a 300 ppi.
5. Número total de páginas par; a KDP acrescenta uma branca no fim se faltar.
6. A capa inteira (`-capa-impressa.pdf`) em arquivo separado, calculada por `verifica_capa.py impressa --paginas N --papel P`: contracapa (sinopse, área do código de barras livre), lombada com título e autor (acima de 79 páginas), capa.

## Do PDF ao EPUB

O EPUB é refluível e não imita a página do PDF. O `build_epub` reaproveita o HTML de cada seção e simplifica (`kindle_html`): tira os ícones, troca os balões e as etapas por tabelas de imagens (o Kindle não respeita lado a lado por porcentagem), tira as referências de página. A versão "loja" reduz cada imagem a 800 px e comprime a 68 %.

Ao criar qualquer componente novo no PDF, decida no mesmo dia como ele aparece no EPUB: ou ganha regra no `EPUB_CSS`, ou é retirado do EPUB (páginas que só fazem sentido impressas, como a folha de progresso para marcar), ou é refeito como tabela simples. Confira na prévia de celular.

## Conferência visual: o que olhar em cada tipo de página

| Página | O que precisa estar certo |
|---|---|
| Capa | só desenho (nunca pintura); título legível em miniatura; crédito no colofão bate com as obras usadas |
| Sumário | cabe em uma ou duas páginas; números de página corretos; nenhuma entrada que não existe |
| Abertura de parte ou nível | imagem diferente da aula seguinte; cor certa |
| Aula | obra, balões e "Na vida dele" na primeira página; sem meia página vazia; legenda inteira |
| Exercício | modelo, tempo, material, teoria e "Pronto quando"; cópia com o recorte certo |
| Comparação | três recortes do mesmo assunto, mestres diferentes |
| Catálogo | toda obra citada está lá, com dados conferidos; campo em branco quando não confirmado |
| Créditos | domínio público declarado; modelos feitos com IA declarados |
| EPUB | capa, sumário clicável, imagens no tamanho da tela, nenhum bloco sem estilo |
