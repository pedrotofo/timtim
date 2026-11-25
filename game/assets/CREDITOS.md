# Origem e licença dos arquivos do jogo

Lista feita em 25/11/2026 a partir do histórico do projeto (o commit que trouxe ou mudou cada arquivo por último).
Serve para publicar o jogo: lojas como a Steam e a itch.io perguntam o que foi feito com IA e de onde vêm os sons.

Legenda da coluna **Confirmar**: ✅ origem clara no histórico · ⚠️ falta conferir a ferramenta ou a licença.

## Personagem (referência)

| Arquivos | Origem | Licença / observação | Confirmar |
|---|---|---|---|
| `timtim-referencia.png`, `tintim-character-sheet.png`, `tintim-foto.jpg` | Ficha oficial e foto do Timtim, enviadas pelo Pedro | Do Pedro. Só referência: não aparecem no jogo | ✅ |

## Imagens geradas com IA

| Arquivos | Origem | Licença / observação | Confirmar |
|---|---|---|---|
| Fase 3 inteira: `bg/vg-*.jpg`, `props/vg-*.png`, `props/frente-vg-*.png`, `props/galhos-vg.png`, `sprites/vg/*`, `sprites/vg-estrela.png`, `sprites/vg-redemoinho.png`, `sprites/toy-girassol.png`, `sprites/toy-bolinha.png`, `tex/vg-*.jpg` | Google Flow, Nano Banana 2.1 (sem créditos) | Gerado com IA | ✅ |
| Mapa das fases: `mapa/mapa.png`, `mapa/timtim.png` | Google Flow (sem créditos), com a ficha do Timtim de referência; paleta e grade de pixels acertadas em código | Gerado com IA e editado | ✅ |
| Arraial e cenário 3.0: `props/barraca.png`, `pescaria.png`, `fogueira.png`, `mastro.png`, `agapanto.png`, `capim.png`, `flores.png`, `samambaia.png`, `tropical.png`, `tocha.png`, `troncos.png`, `galinheiro.png`, `lanterna.png`, `frente-arraial-*.png`, `galhos-arraial.png`, `bg/arraial-mata.jpg`, `tex/*.jpg` (menos `vg-*`), `sprites/toy-sanfona.png`, `sprites/bilhete.png`, `sprites/fruta.png`, `sprites/ovo.png`, `sprites/galinha.png`, `sprites/bandana-asa.png` | Google Flow | Gerado com IA | ✅ |
| Fase 1: `bg/floresta-azul.jpg`, `props/flores-luz.png`, `props/frente-galhos.png`, `props/frente-raizes-*.png`, `props/pantano-*.png` | Google Flow | Gerado com IA | ✅ |
| `bg/shelf.jpg`, `sprites/tintim-sniff.png`, `sprites/toy-duck.png`, `sprites/tintim-glide.png` | Google Flow | Gerado com IA | ✅ |
| Animações `anim/*.webp` e `anim/*.json` | Vídeos gerados no Google Flow (Veo 3.1 Lite) e cortados em quadros | Gerado com IA | ✅ |
| `sprites/tintim-run.png` | Quadros tirados de vídeo do Google Flow (Veo 3.1 Lite) | Gerado com IA | ✅ |
| Lobo-guará: `sprites/guara-*.png` | Google Flow (edição com o chapéu de pato) | Gerado com IA | ✅ |
| `sprites/tintim-idle.png`, `tintim-jump.png`, `tintim-fall.png`, `tintim-hurt.png`, `tintim-win.png`, `cookie.png`, `pigeon.png` | Higgsfield (12/11/2026), com ajustes depois | Gerado com IA | ⚠️ conferir se ainda são as do Higgsfield |
| Furtão: `sprites/brute-*.png` | Recortados de uma ficha de personagem gerada com IA (16 e 24/11/2026) | Gerado com IA | ⚠️ conferir a ferramenta |
| Zara e Elvis: `sprites/chi-pb*.png`, `sprites/chi-br*.png` | Primeiras versões do jogo (12–13/11/2026) | Gerado com IA | ⚠️ conferir a ferramenta |
| Macaco Fedido e abertura: `sprites/monkey-*.png`, `intro/*.jpg` | Gerados com a arte do jogo de referência (13–17/11/2026) | Gerado com IA | ⚠️ conferir a ferramenta |
| `title.jpg`, `bg/figs.png` | Arte do título e figueiras (13–16/11/2026) | Gerado com IA | ⚠️ conferir a ferramenta |

## Sons, música e voz

| Arquivos | Origem | Licença / observação | Confirmar |
|---|---|---|---|
| `sfx/*.mp3` (24 efeitos: latidos, pulos, biscoito, pancadas, fanfarra...) | Artlist (16/11/2026), cortados e com volume igualado | Licença da assinatura Artlist do Pedro | ⚠️ confirmar se o plano cobre jogos |
| `sfx/cluck1.mp3`, `cluck2.mp3`, `henCoop.mp3`, `henFlap.mp3`, `henPanic.mp3` | Artlist (galinhas, 24/11/2026) | Licença da assinatura Artlist | ⚠️ confirmar se o plano cobre jogos |
| `sfx/cookie.mp3`, `sfx/pigeon.mp3`, `sfx/thud.mp3`, `sfx/laugh.mp3` | Artlist (16–17/11/2026) | Licença da assinatura Artlist | ⚠️ confirmar a fonte e se o plano cobre jogos |
| `voice/intro1.mp3`, `intro2.mp3`, `intro3.mp3` | Voz gerada no Artlist (ElevenLabs Multilingual v2) | Voz gerada com IA | ⚠️ confirmar a licença da voz |
| `music/theme.mp3` ("Forest Treats"), `music/boss.mp3` ("Triumph of the Brave") | Músicas do Pedro feitas no Suno | Música gerada com IA; uso comercial depende do plano do Suno usado na época | ⚠️ confirmar o plano |
| Sons de reserva sintetizados (`src/audio.js`) | Feitos em código | Do projeto | ✅ |

## Regras para o que entrar daqui em diante

- Todo arquivo novo ganha uma linha aqui: origem, ferramenta, data e licença.
- Sons só do Artlist (nunca Openverse). Imagens do Flow com Nano Banana não gastam créditos; o resto, só com o ok do Pedro.
- Na Steam, responder a pesquisa de conteúdo com IA usando esta lista: tudo marcado "gerado com IA" foi feito antes e vai junto com o jogo (não é gerado enquanto se joga).
