# Livros "a Lápis" (Pedro Torres)

- `livro/` é *Van Gogh a Lápis* e `rembrandt/` é *Rembrandt a Lápis*. Cada pasta tem o próprio `build.py`, texto em `src/*.md` e dados em `data.json`.
- Durante o trabalho, gere só a capa e o PDF: `python3 build.py` (sem argumentos). Não gere EPUB nem outros formatos até o autor dizer que o livro está encerrado; aí, `python3 build.py cover pdf epub`.
- As duas capas seguem o mesmo modelo: obra de domínio público sangrando a página inteira, rosto no terço de cima com os olhos no eixo central, nome do autor no alto, título e subtítulo sobre a parte escura de baixo. No Rembrandt a arte sai de `tools/capas.py` (opção aplicada: `1-gorro-de-veludo-1638`).
