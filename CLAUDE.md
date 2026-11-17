# Livros "a Lápis" (Pedro Torres)

- `livro/` é *Van Gogh a Lápis* e `rembrandt/` é *Rembrandt a Lápis*. Um livro novo da série começa copiando `rembrandt/`.
- Para qualquer trabalho num livro da série (novo artista, capa, exercícios, ilustrações, texto), siga a skill `.claude/skills/livro-a-lapis/SKILL.md`.
- Durante a produção, gere só a capa e o PDF: `python3 build.py` (sem argumentos). EPUB e outros formatos só quando o autor disser que o livro está encerrado (`python3 build.py cover pdf epub`).
- Capa aplicada no Rembrandt: `1-gorro-de-veludo-1638` (`tools/capas.py`).
