# Estúdio de Vídeo

Skills do Claude para quem filma clientes falando, edita no Premiere e ilustra as falas com
motion. Este repositório é a **fonte única**: o que está aqui é o que aparece no Claude Code em
qualquer projeto, no computador ou na nuvem.

## O que tem

**Do bruto ao Premiere (skills próprias)**

| Skill | Faz |
|---|---|
| `estudio-video` | O mapa: qual skill usar em cada etapa |
| `decupagem` | Transcreve local e de graça (faster-whisper), com timecode por palavra; marca as melhores falas, o que conferir e cada momento que pede ilustração |
| `ilustrar-fala` | Motions sincronizados com a fala, com fundo transparente: mapa do Brasil por estados (malha do IBGE), cidades, rotas, números, listas, lugares reais |
| `premiere-xml` | Leva o corte, os motions e os marcadores da decupagem para o Premiere como timeline editável |

**Motion (pacote que já existia, agora aqui)**: `brand-intake`, `motion-effects`,
`animated-chart`, `title-sequence-3d`, `vox-explainer`, `launch-video`, `apple-launch-film`,
`milestone-reveal`, `interface-escura-3d`, `newsletter-promo`, `loop-cover`, `model-showdown`,
`reel-export`, `motion-brief-writer`, `reference-to-motion`, `blender-film`, `blender-car-film`,
`blender-forest`.

**De terceiros** (`terceiros.txt`, cada uma presa a um commit conferido):
HyperFrames (`hyperframes`, `hyperframes-cli`, `hyperframes-registry`, `media-use`),
Remotion (14 skills `remotion-*`) e `video-editing-skill` (silêncios, "éé", retakes, legenda).

## Como instalar

### Sessões na nuvem (claude.ai/code, app do celular)

O ambiente da nuvem tem um script de preparação que roda `instalar.sh` sozinho em toda sessão
nova, em qualquer repositório. Nada a fazer.

### No seu computador (Claude Code no desktop ou no terminal)

Uma vez, e de novo quando quiser atualizar:

```bash
git clone https://github.com/pedrotofo/estudio-video.git
cd estudio-video
bash instalar.sh          # no Windows: rode no Git Bash
```

Instala em `~/.claude/skills` (vale para todos os projetos) e instala faster-whisper, HyperFrames
e OpenTimelineIO. Precisa de Python 3, Node.js 22+ e ffmpeg. Para atualizar depois:
`git pull && bash instalar.sh`.

## Como mudar uma skill

Edite aqui, faça commit e push. A próxima sessão na nuvem já vem com a mudança; no computador,
`git pull && bash instalar.sh`. Nunca edite a cópia em `~/.claude/skills`: ela é substituída a cada
instalação.

## Privacidade

- A transcrição é local. Nenhum vídeo de cliente sai do computador.
- O HyperFrames roda com `HYPERFRAMES_NO_TELEMETRY=1`.
- Material de cliente (bruto, `.mov`, decupagens) nunca entra neste repositório (`.gitignore`).
