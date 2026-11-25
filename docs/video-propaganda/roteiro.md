# Roteiro: propaganda do Timtim (9:16, 13 s)

**Formato:** 1080×1920, 30 fps (390 quadros), feito em HTML no **HyperFrames** (`npx hyperframes render`), com GSAP na linha do tempo.
**Imagens:** só das fases 1 (Parque, azul) e 2 (Arraial, laranja). Nada da fase 3.
**Estilo de base:** janela de app escura em 3D (fundo #0D0E11, janela #16171C, cantos 22px, fonte Inter), com o próprio jogo desfocado atrás e grade de pontos. Zonas seguras: nada importante nos 12% de cima nem nos 15% de baixo.

| Tempo | Cena | O que se vê | Frase na tela | Som |
|---|---|---|---|---|
| 0,0–1,8 s | **1. A janela se monta** | Tela escura com grade de pontos. As peças da janela chegam em 3D de profundidades diferentes e se encaixam: moldura e barra com 3 bolinhas, título "Timtim e o Resgate do Macaco Fedido", tela 16:9 (acende com o Furtão fugindo com o macaco na boca), lista vazia embaixo. Câmera chega inclinada e endireita. | **"Roubaram o Macaco Fedido."** | Whoosh + 3 cliques de encaixe |
| 1,8–4,6 s | **2. Fase 1: o Parque** | Dentro da janela: o Timtim correndo e dando pirueta na floresta azul; corte para o faro (rastro verde) e para a luta com o Furtão. Fundo desfocado fica azul. Etiquetas saem da janela em 3D (com o personagem recortado): "Pulo duplo", "Fareje segredos" e "Chefão: Furtão". | **"Fase 1: o Parque."** | Pulo + latido do Furtão |
| 4,6–7,6 s | **3. Fase 2: o Arraial** | Onda de luz verde sai da janela, corte seco para o Arraial; o fundo muda de azul para laranja. Timtim planando com a bandana sobre a fogueira; debandada de galinhas; lobo-guará. Câmera inclina de leve. Etiquetas: "Plane no ar quente", "Fuja da debandada" e "Chefão: Lobo-guará". | **"Fase 2: o Arraial."** | Cacarejo + ar quente |
| 7,6–10,6 s | **4. Checklist** | A janela gira um pouco e a lista ganha ✓ um a um, com miniatura de personagem em cada linha: ✓ Fase 1 · O Parque (ganha o ✓ no fim da cena 2) · ✓ Fase 2 · O Arraial · ✓ 2 chefões para vencer · ✓ Amigos que dão poderes · ✓ Celular, teclado ou controle. | **"Tudo numa aventura só."** | Tique a cada ✓ |
| 10,6–13,0 s | **5. Fechamento** | Janela gira para o lado e recua; Timtim comemora com o Macaco Fedido; notificação desce: "Macaco resgatado · Fase 1 concluída · Furtão vencido"; Timtim e o macaco saltam para fora da janela. Título do jogo grande + chamada. | **"Jogue agora."** + nome do jogo | Arpejo final (win) |

## Fontes de imagem previstas
- Gravações do próprio jogo rodando (Playwright com relógio quadro a quadro): `index.html` (fase 1) e `index.html#fase2` (fase 2).
- Artes das fases: `assets/bg/floresta-azul.jpg`, `assets/bg/arraial-mata.jpg`, abertura `assets/intro/2-roubo.jpg` (a abertura faz parte da fase 1).
- Miniaturas do checklist: quadros de `assets/anim/` (Timtim, Furtão, lobo-guará, Zara, Elvis, Macaco Fedido).

## Decisões alinhadas
- **Cores:** janela escura; o destaque fica azul (#4AA8FF) na fase 1 e laranja (#FF9A3C) na fase 2. A onda, os ✓ e o botão seguem a cor da fase em que se está.
- **Dentro da janela:** o jogo rodando de verdade, gravado quadro a quadro.
- **Som:** nenhum. O vídeo sai mudo (a coluna "Som" acima fica só como ritmo dos cortes).
- **Final:** nome do jogo + "Jogue agora", sem link.

## Onde está
- Projeto HyperFrames: `video/propaganda-9x16/` (`index.html` + `compositions/janela.html` e `compositions/textos.html`).
- Vídeo final: `video/propaganda-9x16/timtim-propaganda-9x16.mp4`.
