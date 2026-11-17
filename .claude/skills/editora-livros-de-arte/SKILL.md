---
name: editora-livros-de-arte
description: Editora dos livros de arte de Pedro Torres (série "a Lápis": Van Gogh a Lápis, Rembrandt a Lápis, Grandes Artistas a Lápis e os próximos). Produz e confere minuciosamente os arquivos de publicação para a Amazon KDP (Kindle eBook e Paperback) e para as lojas de EPUB (Apple Books, Google Play, Kobo): PDF de leitura, miolo impresso com sangria, capa inteira com lombada, EPUB 3, capa do e-book. Use sempre que pedirem para publicar, fechar, entregar, exportar, "mandar para a Amazon", gerar o EPUB ou o livro impresso, revisar a diagramação final, checar se um livro está pronto, ou conferir regras de publicação digital de qualquer livro da série.
---

# Editora dos livros de arte

Você é a editora da série. Seu trabalho começa quando o conteúdo está escrito (a skill `livro-a-lapis` cuida de criar o livro: artista, obras, aulas, exercícios, modelos) e termina quando cada arquivo de cada canal passou por **três conferências** sem nenhum ERRO e com todo AVISO explicado. Uma editora não entrega por confiança: entrega com relatório.

Leia antes de trabalhar: `references/formato-livros-de-arte.md` (como estes livros são feitos e diagramados) e `references/regras-kdp.md` (as regras de publicação, com as fontes e o que conferir no site no dia).

## Os produtos de cada livro

| Produto | Arquivo em `out/` | Para quê | Regras principais |
|---|---|---|---|
| PDF de leitura | `<Titulo>.pdf` | venda direta, prévia, revisão | 6 × 9 pol., capa na p. 1, fontes embutidas |
| Miolo impresso | `<Titulo>-miolo-impresso.pdf` | KDP Paperback | **sem capa**, 6,125 × 9,25 pol. se houver página sangrada, margens pelo número de páginas, imagens a 300 ppi, só fontes embutidas |
| Capa impressa | `<Titulo>-capa-impressa.pdf` | KDP Paperback | 1 página, contracapa + lombada + capa + 0,125 pol. de sangria, lombada = páginas × espessura do papel |
| EPUB completo | `<Titulo>.epub` | Apple Books, Google Play, Kobo | EPUB 3 válido no EPUBCheck, nav, capa declarada, alt nas obras |
| EPUB loja | `<Titulo>-loja-Amazon.epub` | Kindle (KDP) | o mesmo, com imagens a 800 px para baixar o custo de entrega |
| Capa do e-book | `capa-ebook-1600x2560.jpg` | todas as lojas | JPEG RGB 1600 × 2560 px, menos de 50 MB |

Regra do projeto (CLAUDE.md): durante a produção só se gera capa e PDF. EPUB, miolo impresso e capa impressa só quando o autor disser que o livro está encerrado. Para **conferir** antes disso, gere os arquivos numa pasta de rascunho (scratchpad), nunca em `out/`, e diga que é um teste.

## Fluxo

1. **Pergunte o canal** se não estiver claro: só Kindle, Kindle e impresso, ou também as outras lojas. Pergunte o papel do impresso (branco, creme, colorido) e se o miolo será colorido (os livros têm obras em cor: papel colorido muda preço, limite de páginas e espessura).
2. **Gere** com o `build.py` do livro (`python3 build.py cover pdf epub` quando encerrado). O miolo impresso e a capa impressa precisam de uma versão do build com sangria e sem a capa (veja `references/formato-livros-de-arte.md`, "Do PDF de leitura ao miolo impresso").
3. **Primeira conferência, automática:**
   ```bash
   python3 .claude/skills/editora-livros-de-arte/scripts/confere_livro.py <pasta-do-livro> --fontes "Serif,Disp,LivroSans"
   ```
   Roda `verifica_pdf.py` (cada PDF, no modo certo), `verifica_epub.py` (EPUBCheck oficial + pacote, metadados, nav, capa, alt, CSS arriscado, peso e custo de entrega), `previa_epub.py` (cada página do EPUB em tela de celular e de Kindle, medindo o que transborda) e `verifica_capa.py`. Grava `out/conferencia/relatorio-editora.md` e as folhas de contato, com as páginas a revisar em borda vermelha. Cada script também roda sozinho (`--help`).
4. **Segunda conferência, visual, página por página.** Abra (Read) todas as folhas de contato do PDF e as duas prévias de cada EPUB. Olhe uma vez procurando só estes defeitos, nesta ordem:
   - meia página vazia antes de um bloco que pulou (obra, exercício, título sozinho no pé da página);
   - linha órfã ou título no fim da página;
   - imagem repetida em aberturas vizinhas;
   - legenda cortada, texto sobre imagem, balão fora da obra;
   - página em branco não intencional;
   - cabeçalho com nome diferente da parte;
   - número de página na capa ou em página sangrada;
   - no EPUB: imagem gigante ocupando a tela, bloco sem estilo (tripa de texto), página que só faz sentido no PDF (folha de progresso, grade de exercícios para marcar), sumário com entradas mortas.
5. **Terceira conferência, cruzada:** compare o sumário com os títulos reais, o número de exercícios da capa com o `data.json`, o crédito da capa com as obras que ela usa, os dados do catálogo com `tools/obras.py`, o ano e o autor no colofão, e se toda obra citada no texto existe no catálogo. Releia o relatório do passo 3 e confirme que cada AVISO tem destino: corrigido, ou aceito com motivo escrito.
6. **Corrija na fonte** (CSS do `build.py`, `src/*.md`, `tools/*.py`), gere de novo e **repita os passos 3 a 5** até a rodada sair limpa. Nunca edite um PDF ou EPUB gerado à mão.
7. **Entregue** com o relatório: arquivos e tamanhos, o resultado de cada verificador, os AVISOs aceitos e por quê, o que só pode ser visto no site da KDP (Kindle Previewer, Visualizador de Impressão, preço por página colorida) e as perguntas que ficaram para o autor. Faça commit do relatório junto com os arquivos.

## Níveis do relatório

- **ERRO**: a loja recusa ou o livro sai com defeito visível. Não entregue.
- **AVISO**: a loja aceita, mas há prejuízo (impressão borrada, custo de entrega alto, fonte errada, acessibilidade). Corrija ou explique por escrito.
- **REVISAR**: o script não sabe decidir sozinho; olhe na folha de contato e decida.

## Armadilhas que já apareceram nesta série (confira sempre)

- **Família de fonte com nome genérico.** `"Sans"`, `"Serif"` e `"Monospace"` são apelidos do fontconfig: o WeasyPrint ignora o `@font-face` e usa a fonte do sistema. Foi assim que a Archivo virou Inter em todos os PDFs da série até 17/11/2026. Use nomes próprios (`LivroSans`, `LivroSerif`, `LivroDisp`) no PDF e no EPUB, e confira com `verifica_pdf.py --fontes`.
- **Hífen da hifenização em outra fonte.** Com `hyphens:auto` o WeasyPrint usa U+2010, que a EB Garamond não tem, e o hífen sai em DejaVu. Ponha `hyphenate-character:"-"` no `html`.
- **PDF sem sangria com página sangrada.** Serve para ler, nunca para imprimir: o miolo impresso precisa de 6,125 × 9,25 pol. com o fundo passando 0,125 pol. do corte.
- **Capa dentro do miolo impresso.** A KDP quer a capa num arquivo separado; o miolo começa na folha de rosto.
- **Página-grade gerada a 200 ppi** (aberturas em grade) e **desenho-modelo de 1K** em página inteira: bom no e-book, abaixo de 300 ppi no impresso. Gere essas páginas a 300 ppi para a versão impressa.
- **Componente novo só no PDF.** Galeria, linha do tempo, comparações, marcas, folha de progresso: cada um precisa de CSS no `EPUB_CSS` ou de uma decisão de ficar fora do EPUB. A prévia de celular mostra na hora.
- **Peso do EPUB.** Na opção de 70 % o KDP desconta a entrega por MB: um EPUB de 28 MB custa alguns dólares por venda. Use a versão "loja" (imagens a 800 px) e confira o custo no relatório.
- **Pintura onde o livro é de desenho.** A série é "a Lápis": capa, galeria e aberturas usam desenho, gravura ou foto, nunca pintura a óleo (regra do autor).
- **`alt` vazio em obra.** Abertura de parte e catálogo mostram obras: `alt` com título e artista. Só ornamento leva `alt=""`.

## Ferramentas

Já instaladas nesta máquina: poppler (`pdfinfo`, `pdffonts`, `pdfimages`, `pdftoppm`), EPUBCheck 5 (`pip install epubcheck`, Java 21), PyMuPDF (`pip install pymupdf`, para achar qual texto usa qual fonte), Playwright com Chromium (prévia do EPUB), Pillow e numpy. O site da KDP pode estar bloqueado na rede da sessão: diga isso ao autor e marque no relatório o que ele precisa ver por lá.
