# Livros "a Lápis" (Pedro Torres)

- `livro/` é *Van Gogh a Lápis*, `rembrandt/` é *Rembrandt a Lápis* e `mestres/` é *Grandes Artistas a Lápis* (dez mestres em cinco níveis, uma cor azul por nível, aulas montadas a partir de obras com `{{obra:chave}}`). Um livro novo de um artista só começa copiando `rembrandt/`.
- Para qualquer trabalho num livro da série (novo artista, capa, exercícios, ilustrações, texto), siga a skill `.claude/skills/livro-a-lapis/SKILL.md`.
- Durante a produção, gere só a capa e o PDF: `python3 build.py` (sem argumentos). EPUB e outros formatos só quando o autor disser que o livro está encerrado (`python3 build.py cover pdf epub`).
- Capa aplicada no Rembrandt: `1-gorro-de-veludo-1638` (`tools/capas.py`).
- Grandes Artistas: capa em mosaico de rostos (`mestres/tools/capas.py`, opções em `tools/capas_opcoes.json`); provisória `1-seis-desenhos`, aguardando escolha do autor. Obras em `tools/obras.py`, exercícios em `tools/make_data.py`.
