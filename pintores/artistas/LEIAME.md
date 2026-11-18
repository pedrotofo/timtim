# Como escrever a ficha de um pintor (Os 50 Maiores Pintores)

Cada pintor é um arquivo `artistas/NN-chave.json` (NN com dois dígitos: `01-van-gogh.json`, `19-hokusai.json`). O build monta 4 páginas fixas de 21,6 × 27,9 cm a partir dele. **O modelo pronto é `19-hokusai.json`: copie a estrutura e o tom.** Veja as páginas dele em `out/amostra-19.pdf` (gere com `python3 build.py amostra 19`).

## Público e tom

Livro de arte com cara de livro didático, para jovens e adultos curiosos, em português do Brasil. Frases curtas, concretas, sem jargão sem explicação, sem adjetivo vazio ("genial", "magistral", "icônico", "único"). Conte fatos que o leitor visualize: onde, quando, com quem, como. Cada pintor é tratado por "ele" ou "ela"; Artemisia Gentileschi leva `"pron": "por ela"`, os outros `"pron": "por ele"`.

## Exatidão (o mais importante)

- Só escreva o que é fato bem estabelecido. Na dúvida, tire, ou diga "segundo a tradição", "conta-se que", "pelas estimativas".
- Datas de obra como os museus dão (c. 1665, 1503–1519). Medidas em cm, altura × largura. Museu atual correto.
- **Citação** só se for documentada (carta, diário, tratado, depoimento publicado), com a fonte no campo `fonte` (ex.: "Carta ao irmão Theo, 1888"). Tradução sua, fiel. Se o pintor não deixou nada escrito, use um contemporâneo ou biógrafo antigo (Vasari, Van Mander, Pacheco) com fonte. Nunca invente.
- Linha do tempo "mundo": fatos históricos certos, de preferência ligados ao Brasil quando a época permitir (1500, 1808, 1822, 1888, 1889...).

## Imagens (direitos e escolha)

- Só imagens do **Wikimedia Commons em domínio público ou CC0** (reprodução fiel de obra antiga). Nada de foto CC-BY de museu, nada de obra de quem morreu depois de 1955.
- Mondrian, Kandinsky, Munch e Matisse: **só obras feitas até 1930** (regra dos EUA).
- **Sem nudez** como regra. Exceção: obras canônicas que todo livro escolar mostra e em que o nu não é o assunto (A criação de Adão, O nascimento de Vênus). Nunca nu na abertura. Obras com nu podem ser citadas no texto.
- Prefira arquivos grandes (mais de 2000 px no lado maior), de museus (Google Art Project, Met, Rijksmuseum, National Gallery of Art, Art Institute of Chicago). Evite foto torta, moldura, reflexo.
- Liste cada imagem em `"imagens": {"arquivo.jpg": "File:Nome exato no Commons.jpg"}`. Nos outros campos, a imagem é `"chave/arquivo.jpg"` (a chave é o campo `chave` do JSON).
- Ache os nomes com `python3 tools/commons.py busca "termos"` e confira com `python3 tools/commons.py info "File:..."` (tamanho e licença). Baixe com `python3 tools/baixa.py NN` (só os seus números; ele recusa o que não for domínio público). O Commons às vezes responde 429: o script espera sozinho, tenha paciência e não rode downloads em paralelo.

Quantas imagens: abertura (1, horizontal ou que aceite corte horizontal: ocupa a faixa de cima da página inteira), retrato (autorretrato ou retrato da época; se não existe nenhum seguro, `"retrato": null`), `vida_fig` (1, opcional, um desenho, documento, lugar ou obra secundária), obra em foco (1, a mais importante), principais obras (3 outras, diferentes da abertura e da obra em foco). Total de 6 a 7.

## Campos e limites (as páginas são fixas: texto a mais some)

| Campo | Limite |
|---|---|
| `pos`, `chave`, `nome`, `nome_original` (só se for outra escrita: 葛飾北斎; senão ""), `vida` ("1853–1890"), `origem` (país) | |
| `cor` | cor de destaque tirada da obra mais importante, escura o bastante para texto branco (o build escurece se precisar) |
| `frase` | 1 frase, até 22 palavras: quem é e por que importa |
| `retrato` | `{"img", "legenda", "pos"}`; `pos` opcional, enquadramento do rosto no círculo ("center 20%") |
| `abertura` | `{"img", "legenda", "pos"}`; `pos` = foco do corte horizontal ("center 40%") |
| `ficha` | exatamente 6 linhas: Nasceu, Morreu, Movimento, Técnica, Obra (quantas obras, aproximado), Onde ver (3 museus). Até 12 palavras cada |
| `vida_titulo` | título da página da vida, até 6 palavras, diferente dos subtítulos |
| `vida_txt` | 4 blocos `{"t", "p"}`; `t` até 5 palavras; `p` de 60 a 80 palavras. Total até 310 palavras |
| `citacao` | `{"texto", "fonte"}`, texto até 50 palavras |
| `vida_fig` | `{"img", "legenda"}`, legenda até 20 palavras (ou omita) |
| `linha` | exatamente 10 eventos `[ano, "texto", "vida"/"mundo"]` em ordem de ano, 5 de cada tipo, texto até 6 palavras |
| `foco` | `titulo` (nome da obra em português), `dados` ("1889 · óleo sobre tela · 73,7 × 92,1 cm · MoMA, Nova York"), `intro` até 45 palavras, `marcas`: 4 itens `[x%, y%, "título até 3 palavras", "texto até 22 palavras"]`, x e y em % da imagem (0,0 = canto superior esquerdo), colocados SOBRE o detalhe de que falam; abra a imagem e confira |
| `sabia` | 3 curiosidades, até 30 palavras cada |
| `tecnica` | `titulo` (até 5 palavras), `intro` até 40 palavras, `passos`: 4 `["título até 3 palavras", "até 25 palavras"]`, `box_t` até 5 palavras, `box` até 55 palavras, `paleta`: 5 `["#hex", "nome até 2 palavras"]` tirados das obras |
| `obras` | 3 `{"img", "titulo" (até 7 palavras), "ano", "nota" (até 14 palavras)}` |
| `influenciou` | até 4 `["Nome", número no livro]` só de quem ele influenciou de fato; se a pessoa não está no livro, `["Nome", null]` |
| `rival` | opcional: `["Nome", número no livro, "até 14 palavras"]` (rival, mestre ou contemporâneo que está no livro) |
| `pensar` | uma atividade de olhar ou desenhar, até 45 palavras |
| `palavras` | 3 `["Termo", "definição até 22 palavras"]` |
| `imagens` | mapa arquivo → título no Commons |

## Conferir antes de entregar

1. `python3 tools/baixa.py NN` sem ERRO.
2. `python3 build.py verifica NN` diz "sem estouro". Se estourou, corte texto.
3. `python3 build.py amostra NN` e abra (Read) `out/amostra-NN-spread-1.png` e `-2.png`: as marcas caem no lugar certo? O rosto aparece no círculo? A abertura mostra a parte boa da obra? Nada cortado, nada vazio demais?
4. Releia os fatos uma vez procurando só erro de data, nome, museu e atribuição.

## Os 50, em contagem regressiva (número no livro e país)

50 Arturo Michelena (Venezuela) · 49 Kim Hong-do (Coreia) · 48 Tom Roberts (Austrália) · 47 Juan Luna (Filipinas) · 46 Gu Kaizhi (China) · 45 Pedro Américo (Brasil) · 44 Osman Hamdi Bey (Império Otomano) · 43 Kamāl ud-Dīn Behzād (Pérsia) · 42 Raja Ravi Varma (Índia) · 41 Hiroshige (Japão) · 40 Ilya Repin · 39 Artemisia Gentileschi · 38 Amedeo Modigliani · 37 Piet Mondrian · 36 Nicolas Poussin · 35 Henri de Toulouse-Lautrec · 34 Jacques-Louis David · 33 Pieter Bruegel, o Velho · 32 Camille Pissarro · 31 Gustave Courbet · 30 Edvard Munch · 29 Pierre-Auguste Renoir · 28 Hieronymus Bosch · 27 Wassily Kandinsky · 26 Caspar David Friedrich · 25 Eugène Delacroix · 24 El Greco · 23 Sandro Botticelli · 22 Jean-Auguste-Dominique Ingres · 21 Edgar Degas · 20 Édouard Manet · 19 Katsushika Hokusai · 18 Caravaggio · 17 Paul Gauguin · 16 Giotto · 15 Gustav Klimt · 14 Peter Paul Rubens · 13 Johannes Vermeer · 12 Henri Matisse · 11 Francisco de Goya · 10 Ticiano · 9 Paul Cézanne · 8 Diego Velázquez · 7 Claude Monet · 6 Albrecht Dürer · 5 Rafael · 4 Rembrandt · 3 Michelangelo · 2 Leonardo da Vinci · 1 Vincent van Gogh

Os 10 primeiros (50 a 41) são as vagas da "volta ao mundo": o pintor de obra livre com mais alcance da sua região. Ficaram fora por direito autoral, e podem ser citados no texto como influência: Picasso, Frida Kahlo, Diego Rivera, Dalí, Miró, Chagall, Warhol, Pollock, Magritte, Tarsila do Amaral.
