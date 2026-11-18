# Livros "a Lápis" (Pedro Torres)

- `livro/` é *Van Gogh a Lápis*, `rembrandt/` é *Rembrandt a Lápis* e `mestres/` é *Grandes Artistas a Lápis* (dez mestres em cinco níveis, uma cor azul por nível, aulas montadas a partir de obras com `{{obra:chave}}`). Um livro novo de um artista só começa copiando `rembrandt/`.
- `pintores/` é *Os 50 Maiores Pintores* (em pesquisa): fora da série "a Lápis", sobre pintura, com diagramação de livro didático. O ranking e as fontes estão em `pintores/pesquisa/ranking.md`.
- Para qualquer trabalho num livro da série (novo artista, capa, exercícios, ilustrações, texto), siga a skill `.claude/skills/livro-a-lapis/SKILL.md`.
- Para publicar, gerar EPUB ou impresso, ou conferir se um livro está pronto, siga a skill `.claude/skills/editora-livros-de-arte/SKILL.md` (três conferências, relatório em `out/conferencia/`).
- Durante a produção, gere só a capa e o PDF: `python3 build.py` (sem argumentos). EPUB e outros formatos só quando o autor disser que o livro está encerrado (`python3 build.py cover pdf epub`).
- Capa aplicada no Rembrandt: `1-gorro-de-veludo-1638` (`tools/capas.py`).
- Grandes Artistas: capa em mosaico de rostos (`mestres/tools/capas.py`, opções em `tools/capas_opcoes.json`); aplicada a capa em grade `9-gabinete` (`tools/capas_grade.py usar 9-gabinete`, gera img/cover-pdf.jpg e img/cover-ebook.jpg); só desenhos, nunca pintura. Obras em `tools/obras.py`, exercícios em `tools/make_data.py`.
