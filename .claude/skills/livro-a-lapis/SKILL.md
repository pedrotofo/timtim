---
name: livro-a-lapis
description: Como fazer, revisar ou refazer um livro da série "<Artista> a Lápis", de Pedro Torres (Van Gogh a Lápis, Rembrandt a Lápis e os próximos, como Schiele). Use sempre que o pedido for criar um livro novo da série sobre um artista, mexer na capa, nos exercícios, nas ilustrações ou no texto de um desses livros, ou gerar o PDF.
---

# Série "a Lápis"

Livros-curso em português do Brasil que ensinam a desenhar a lápis na linguagem de um mestre. Autor: Pedro Torres. Já existem `livro/` (Van Gogh) e `rembrandt/` (Rembrandt). Um livro novo nasce copiando `rembrandt/`, que é o modelo mais recente e mais limpo.

## Decisões fixas

**Título.** "<Sobrenome> a Lápis", mesmo quando o artista usava pena ou pincel: lápis é o material do leitor, e a série precisa se reconhecer. O subtítulo varia (Van Gogh: "Teoria e prática para desenhar como Vincent"; Rembrandt: "Luz e sombra, traço por traço").

**Leitor.** Iniciante, como o próprio autor. O material principal é lápis grafite comum (2B e 6B), borracha macia, borracha moldável e esfuminho ou cotonete. Nada de jargão sem explicação (a palavra "sanguínea" foi vetada; diga "giz vermelho"). Quando o artista usou outro meio, o capítulo 1 traz uma tabela "ele usava / para fazer / você usa".

**Formato.** PDF 6 x 9 pol. com WeasyPrint, a partir de `src/*.md` e `data.json`. Enquanto o livro estiver em produção, gere só capa e PDF (`python3 build.py`). EPUB e outros formatos só quando o autor disser que o livro está encerrado.

**Identidade visual (igual em toda a série).** Fontes EB Garamond (texto e título da capa) e Archivo / Archivo Black (números, cabeçalhos, legendas). Papel `#EEEAE0`, tinta `#1E1913`. Cada livro tem uma cor de destaque própria nas aberturas de parte e nos números de capítulo (Van Gogh: ocre `#BF8A5A`; Rembrandt: siena `#9A4A2C`). Mesma grade, mesmas caixas "Na vida dele", balões circulares de detalhe, linhas "Para praticar", páginas de exercício com Tempo / Material / Teoria e "Pronto quando".

**Capa (modelo da série).** Uma obra de domínio público do artista sangrando a página inteira, como o *Retrato de Joseph Roulin* no Van Gogh. Nome do autor em versalete no alto, título grande e subtítulo em itálico sobre a parte escura de baixo, linha "N exercícios em quatro níveis" no pé. Regras que vieram de erros:
- A obra precisa ter rosto no terço de cima e massa escura (roupa, fundo) embaixo, onde o título assenta. Uma cabeça que enche a folha não serve: o título cai no queixo.
- Os olhos ficam no eixo vertical central da capa. Confira com uma grade sobre a imagem antes de recortar.
- Use escaneamento grande (3.840 px; o tamanho de 1.920 px estica e borra uma gravura pequena).
- Não troque o modelo por "obra emoldurada sobre fundo de cor": isso quebra a identidade da série.
- As sombras do topo e da base vão aplicadas na imagem (`tools/capas.py`, função `sombra`). Gradiente em CSS deixa uma linha fina no papel claro.
- Gere 3 opções em `out/capas/` com uma comparação lado a lado e deixe o autor escolher; aplique com `python3 tools/capas.py usar NOME`.

## Estrutura do livro

1. Capa, folha de rosto, direitos (com o crédito exato da obra da capa), sumário em uma página.
2. Prefácio (assinado "Pedro Torres") e "Como usar este livro" (por onde começar, os desenhos-modelo, desenhar por cima, as cartas ou as vozes).
3. **Parte I**: a vida pelo que ela mostra do desenho, com "N endereços" e "N anos em dez traços" (recortes horizontais de obras datadas).
4. **Parte II, A linguagem**, 8 capítulos: 1 Materiais; 2 o alfabeto de marcas do artista; 3 o princípio central dele (Van Gogh: direção e fluxo; Rembrandt: a luz); 4 o rosto; 5 os autorretratos; 6 o corpo; 7 como ele construía uma folha (três sequências em 4 etapas); 8 cópia de mestre (três cópias que ele fez e cinco métodos). Cada capítulo abre com "Na vida dele", usa obras em blocos `<div class="obra">` com balões de detalhe e termina com os *Primeiros passos* (Nível 1).
5. **Parte III, Estudos**: Níveis 2 (essenciais), 3 (aprofundamento) e 4 (provas de mestre, com cópias de obras reais e um projeto pessoal). Cerca de 55 a 70 exercícios no total; códigos por letra do capítulo (no Rembrandt: T traços, L luz, C cabeças, A autorretratos, B corpo, P projeto). Cerca de 10 exercícios com 4 etapas.
6. Consulta: glossário, cartas citadas ou "Vozes citadas" (quando o artista não deixou cartas), fontes e leituras, catálogo das obras, créditos (declarando que os desenhos-modelo foram feitos com IA a partir de orientações do autor).

Exercícios ficam em `tools/make_data.py` (gera `data.json`). Obras: título, legenda curta, comentário, técnica, dimensões, acervo. Nada de dado inventado: se não confirmou data ou acervo, deixe em branco.

## Imagens das obras (Wikimedia Commons)

- A API do Commons dá 429 nesta rede. Busque pela página `Special:MediaSearch` (`tools/wm_search.py`) e baixe pelas miniaturas em tamanho padrão de `upload.wikimedia.org/wikipedia/commons/thumb/...`: 960, 1280, 1920 e 3840 px funcionam; tamanhos fora do padrão e o arquivo original dão 429 ou 400 (`tools/wm_get.py`).
- Rijksmuseum, Met e NGA são bloqueados pela rede; use as cópias deles no Commons.
- Antes de escrever sobre uma obra, olhe a imagem (com grade por cima) e confira se a descrição bate: lado da luz, onde fica o fundo escuro, o que está à esquerda e à direita. Isso já gerou erros.
- Balões de detalhe e recortes da linha do tempo usam coordenadas em fração da imagem; confira cada recorte numa folha de contato.

## Desenhos-modelo (OpenArt, Nano Banana 2)

- Custo: cerca de 20 créditos por imagem. Limite de 4 gerações simultâneas na conta (outras sessões do autor podem estar ocupando vagas). Mande lotes de 4, registre `chave historyId` em `tools/ledger.txt`, baixe com `tools/fetch.py` / `tools/from_list.py`. Precisa de `cdn.openart.ai` liberado na rede do ambiente.
- Prompts em `tools/prompts.py`, etapas em `tools/stages.py` (image2image a partir do modelo pronto; diga "flat scan of the sheet, no board, no pencil, no hands" e evite pedir tom e "sem tom" na mesma etapa).
- O que deu cara de IA e deve ser evitado no prompt: rostos bonitos, simétricos, de banco de imagem ou de galã; sombreado liso; folhas com borda de caderno ou papel envelhecido; assinaturas e datas falsas no canto. O prompt que funcionou melhor começa com "Scan of a real sketchbook page... drawn quickly from life by a student of <artista>'s drawings: searching, restated lines, visible corrections, uneven pressure... ordinary, unidealized people with plain asymmetric faces; proportions slightly off; nothing polished" (ver `tools/redo.py`).
- Depois de baixar, rode `tools/paper.py`: corta bordas e leva todo modelo ao mesmo creme.
- Revise cada lote numa folha de contato. Quando o par "errado / certo" ilustra um erro, gere o "errado" a partir do próprio modelo "certo" (image2image), para ser o mesmo desenho.
- Não use fotos fotorrealistas geradas por IA (materiais, mãos medindo): num livro de desenho elas denunciam a IA. Prefira diagrama de linha ou nada.

## Texto

- Escreva em português do Brasil, frases diretas, voz de professor que desenha. Depois de escrever, passe a skill **humanizer** (repositório `blader/humanizer`; se não estiver em `/home/user/blader/humanizer`, clone com `GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/blader/humanizer /home/user/blader/humanizer` e leia `SKILL.md`). Os padrões que mais apareceram nestes livros: frase final que repete o parágrafo ("Tudo o que importa está entre a testa e o queixo"), "não é X: é Y" sem nada a corrigir, perguntas encenadas, trios paralelos, frases sobre o próprio livro, travessão (use "1606 a 1631", nunca "1606–1631").
- Mantenha um contraste quando ele corrige uma crença real do leitor (a lenda da *Ronda Noturna*, "a neve não foi desenhada: é o papel").
- O prefácio tem a assinatura do autor: não reescreva sem perguntar.
- Não copie frases do prefácio de outro livro da série.
- Verifique fatos e datas; quando a identificação de uma obra é tradicional ou discutida, diga isso.

## Revisão de diagramação

Depois de cada build: `pdftoppm -r 55` em todas as páginas e folhas de contato de 15 a 18 páginas. Procure meia página vazia antes de bloco que pula de página (`.obra` força quebra; use texto corrido ou `.keep`), exercício sozinho em meia página (o build já usa o layout cheio nesse caso), legenda cortada em página sangrada, título de nível encavalado, imagem repetida em duas aberturas, cabeçalho com nome diferente da parte.

## Próximos livros

Schiele (morto em 1918, domínio público): desenhou de fato a lápis, então o título é natural. Muitos desenhos são nus explícitos; escolha obras e modelos com cuidado por causa de anúncios e lojas (Amazon). Acervos principais: Albertina e Leopold Museum (Viena), com cópias no Commons. O princípio central do capítulo 3 provavelmente é o contorno (linha única, angulosa, sem preenchimento), e o capítulo de autorretratos é forte.

Ao terminar uma etapa: commit na branch de trabalho com mensagem descritiva e push; mande o PDF ao autor.
