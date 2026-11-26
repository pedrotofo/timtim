---
name: estudio-video
description: >-
  Roteiro do Estúdio de Vídeo: qual skill usar em cada etapa de um vídeo filmado com cliente ou
  entrevistado, do bruto ao Premiere. Decupar falas, tirar silêncios e "éé", ilustrar a fala com
  motion (mapas, números, listas, lugares), legendar, exportar para Premiere e redes. Use no começo
  de qualquer trabalho de edição ou motion ("tenho um vídeo de cliente", "vamos editar", "o que
  dá para fazer com esse material", "monta o fluxo"), quando não estiver claro qual skill de vídeo
  usar, ou para conferir se o Estúdio está instalado.
---

# Estúdio de Vídeo

A pessoa filma clientes falando, edita no **Adobe Premiere Pro** e ilustra as falas com motion.
Este é o mapa das skills. Escolha pelo pedido; não rode tudo sempre.

## Do bruto ao Premiere

| Etapa | Skill | Sai |
|---|---|---|
| 1. Decupar: transcrição com timecode, melhores falas, o que ilustrar | `/decupagem` | `decup/decupagem.md`, `.json`, `.srt` |
| 2. Tirar silêncios, "éé", gaguejos e retakes | `/video-editing-skill` | `edited/manifest.json` (trechos mantidos) e um MP4 de prévia |
| 3. Ilustrar a fala (mapa, número, lista, lugar, citação) | `/ilustrar-fala` | `motions/*.mov` (ProRes 4444 com alfa) e `insertos.json` |
| 4. Levar para o Premiere como timeline editável | `/premiere-xml` | `premiere/<nome>.xml` |
| 5. Versão vertical para Reels/TikTok | `/reel-export` | MP4 1080×1920 |

Atalhos comuns:
- "Só decupa": etapa 1.
- "Decupa e marca no Premiere": 1 e 4 (sem cortes, só marcadores).
- "Limpa a fala e manda para o Premiere": 1, 2 e 4.
- "Ilustra esse trecho": 1 (só o trecho), 3, 4.

Na etapa 2, use `--plan` primeiro e mostre a lista de cortes. A pessoa finaliza no Premiere,
então o MP4 da `video-editing-skill` é só prévia; o que vale é o `manifest.json` que vira XML.

## Motion e animação

| Pedido | Skill |
|---|---|
| Qualquer vídeo em HTML (base de quase tudo abaixo) | `/hyperframes`, `/hyperframes-cli`, `/hyperframes-registry` (cerca de 450 blocos prontos), `/media-use` |
| Identidade de motion do cliente (cores, fontes, ritmo) | `/brand-intake`, uma vez por cliente |
| 16 efeitos prontos (interface, gráfico que vira linha, tipografia elástica, partículas no logo) | `/motion-effects` |
| Gráfico animado | `/animated-chart` |
| Abertura cinematográfica 3D | `/title-sequence-3d` |
| Explainer estilo documentário | `/vox-explainer` |
| Vídeo de lançamento | `/launch-video`, `/apple-launch-film` |
| Número de marco (seguidores, vendas) | `/milestone-reveal` |
| Apresentar um projeto numa janela 3D escura | `/interface-escura-3d` |
| Newsletter: promo e capa animada | `/newsletter-promo`, `/loop-cover` |
| Comparar 3 IAs no mesmo pedido | `/model-showdown` |
| Projeto de vídeo em React, legendas, mapas Mapbox | `/remotion-best-practices` (e as outras `remotion-*`) |
| Cena 3D realista ou filme curto no Blender | `/blender-film`, `/blender-car-film`, `/blender-forest` (precisa do Blender instalado) |
| Escrever o pedido de um motion | `/motion-brief-writer` (para construir aqui no Claude Code); `/reference-to-motion` (a partir de um vídeo de referência) |
| Prompt para IA que gera vídeo (MiniMax e parecidos) | `prompts-de-motion` (está na sua conta do Claude) |

HyperFrames ou Remotion? **HyperFrames** é o padrão: as skills de motion daqui exportam por ele, e
ele gera `.mov` com transparência. **Remotion** só quando a pessoa pedir ou o projeto já for React.

## Pasta de trabalho

Um projeto por vídeo, fora de qualquer repositório git:

```
<Cliente>/<Projeto>/
  bruto/      o material original (nunca alterado)
  decup/      transcrição e decupagem
  edited/     corte da video-editing-skill (prévia + manifest.json)
  motions/    um projeto HyperFrames por ilustração + os .mov
  premiere/   o XML para importar
```

## Regras do Estúdio

- **Material de cliente não sai do computador.** Transcrição local (faster-whisper). Não suba
  vídeo, áudio nem transcrição para serviços externos sem a pessoa pedir.
- **HyperFrames sem telemetria.** Rode os comandos com `HYPERFRAMES_NO_TELEMETRY=1` e pule as
  "usage notes" e `npx hyperframes events` que as skills dele pedem: o Estúdio deixa isso
  desligado para proteger o material de cliente. Só ligue se a pessoa pedir.
- **Nunca commitar** bruto, `.mov`, decupagem ou transcrição de cliente em repositório.
- O Premiere é o destino: entregue XML + `.mov` com alfa, não um MP4 achatado, a não ser que peçam.

## Onde rodar

- **Claude Code no computador da pessoa (desktop ou terminal):** o lugar certo para material de
  verdade. Os arquivos estão lá, o Premiere também, e transcrever ou renderizar com GPU é rápido.
- **Sessão na nuvem (claude.ai/code, celular):** boa para clipes curtos, testes, motions que não
  dependem do bruto (um mapa, um contador) e para planejar. Vídeo grande é ruim de subir.

## Conferir a instalação

```bash
ls ~/.claude/skills | grep -E 'decupagem|ilustrar-fala|premiere-xml|hyperframes|video-editing'
python3 -c "import faster_whisper" && hyperframes --version && ffmpeg -version | head -1
```

Faltando algo: `bash instalar.sh` no repositório `pedrotofo/estudio-video`.
