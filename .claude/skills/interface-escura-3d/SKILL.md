---
name: interface-escura-3d
description: Gera um vídeo vertical 9:16 de 10 s (1080×1920) no estilo "interface escura 3D" para apresentar um projeto pronto — um jogo, livros, um app — numa janela de app escura em perspectiva, com o conteúdo rodando dentro, o próprio conteúdo desfocado no fundo, uma lista de atos que ganham ✓ verde-menta, onda de pontos verdes a cada ✓, cursor clicando no começo e notificação no fim. Use quando pedirem "apresentação interface-escura-3d", "vídeo vertical do meu projeto nesse estilo", "aquele vídeo da janela 3D com os checks", ou para mostrar livros, jogos ou produtos em Reels/TikTok.
---

# Apresentação interface-escura-3d (9:16, 10 s)

Um vídeo curto para a pessoa falar por cima: o projeto aparece numa janela de app escura em 3D, e uma lista de 3 a 5 "atos" vai ganhando ✓ conforme os melhores momentos passam. Sem títulos fora da janela. Som: só efeitos de interface (clique, tique a cada ✓, arpejo no fim); sempre entregue também uma cópia sem som.

## DNA do estilo (não mude sem pedirem)
- Fundo #0D0E11; o próprio conteúdo do ato atual desfocado (blur 30px, brilho .68) por trás, deslizando ao contrário da câmera; grade de pontos branca a 7%.
- Uma janela #16171C, borda #26282E, cantos 22px: barra com 3 bolinhas e uma pílula de endereço; título do projeto + botão verde; barra de progresso; a tela 16:9 com o conteúdo; a lista de atos (✓, miniatura, nome, barra-esqueleto, pílula).
- Um só acento: verde-menta #3CD48C (botão, ✓, progresso, onda). Texto #EAEAEE, fonte Inter.
- Câmera: chega inclinada de longe (0–1,1 s) → de frente → inclina de leve no ato do meio → gira para o lado no fechamento, quando aparece a notificação.
- Cada troca de ato é um corte seco dentro da janela, no mesmo instante do ✓ do ato anterior, do tique sonoro e da onda verde que sai da janela até as bordas.
- Zonas seguras: nada importante nos 12% de cima nem nos 15% de baixo; a janela fica centralizada.

## Como fazer
1. **Escolha os atos** com a pessoa: 3 a 5 momentos, cada um com um nome curto ("O roubo", "Van Gogh a lápis") e uma miniatura (PNG de personagem, capa do livro…). Distribua os 10 s: o primeiro ato começa em 0 (inclui a chegada da janela), o último dura uns 3 s e contém o `final` (o instante do último ✓ e da notificação, ~8,9 s).
2. **Fonte de cada ato**: um trecho de vídeo (`video` + `from`, em segundos) ou imagens (`images`: uma ou várias, divididas igualmente no ato; ganham uma aproximação lenta, `zoom` [1, 1.06]). Para páginas de livro, use `"fit": "contain"` se a página não puder ser cortada.
3. **Escreva o projeto JSON** ao lado das mídias:
```json
{
  "title": "Timtim e o Resgate do Macaco Fedido",
  "button": "Jogar",
  "toast": { "title": "Macaco resgatado", "subtitle": "Fase concluída · Furtão vencido" },
  "duration": 10, "final": 8.9,
  "out": "timtim-9x16",
  "acts": [
    { "name": "A história", "thumb": "monkey.png", "start": 0.0, "end": 1.6, "video": "gameplay.mp4", "from": 3.3 },
    { "name": "O roubo",    "thumb": "furtao.png", "start": 1.6, "end": 3.4, "video": "gameplay.mp4", "from": 16.1 },
    { "name": "Capa",       "thumb": "capa.png",   "start": 3.4, "end": 5.2, "images": ["capa.jpg", "pagina-12.jpg"], "fit": "contain" }
  ]
}
```
4. **Prévia antes do vídeo final** (a pessoa sempre quer ver antes): `python3 scripts/build.py projeto.json --preview 1.0,4.5,9.4` gera `previa-*.png` ao lado do JSON. Mostre e ajuste.
5. **Vídeo final**: `python3 scripts/build.py projeto.json` → `<out>.mp4` (com efeitos) e `<out>-sem-som.mp4`. Leva ~0,6 s por quadro (300 quadros ≈ 3 min). Confira uma folha de contato dos quadros antes de entregar.

## Requisitos
Python 3 com numpy, ffmpeg, Node com Playwright (Chromium). Os scripts usam caminhos relativos ao JSON; a pasta de trabalho é `interface-escura-3d-work/` ao lado dele.

## Cuidados
- Textos são um contrato: título da janela, nomes dos atos e a notificação são as únicas palavras no quadro. Não invente números na notificação (estrelas, vendas, páginas) que não sejam verdade.
- Nomes de atos longos são cortados com reticências: prefira até ~22 caracteres.
- Se a fonte for vídeo de jogo 3D gravado numa máquina sem placa de vídeo, grave com relógio virtual quadro a quadro (o print direto custa ~2 s por quadro).
