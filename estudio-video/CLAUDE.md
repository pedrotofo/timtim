# Estúdio de Vídeo (este repositório)

Repositório de skills do Claude para edição de vídeo e motion. Ele é instalado em
`~/.claude/skills` por `instalar.sh`, em toda sessão na nuvem e no computador da pessoa.

- Skills próprias em `skills/<nome>/SKILL.md`. Escritas em português do Brasil, para a pessoa.
- Skills de terceiros não ficam aqui: `terceiros.txt` lista repositório, commit conferido e
  pastas. Para atualizar uma, leia o diff do upstream (scripts que acessam a rede, que rodam
  comandos, que enviam dados) antes de trocar o commit.
- Ao mudar uma skill, rode `bash instalar.sh --so-skills` e teste numa sessão nova.
- Teste os scripts com um vídeo de exemplo antes de commitar (transcrição, render, XML).
- Nunca commite vídeo, áudio, `.mov`, transcrição ou decupagem de cliente.
