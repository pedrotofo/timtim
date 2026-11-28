# Ritmo e medidas das fases 1 a 3

Revisão feita em 25/11/2026 com a skill **level-design** (medidas tiradas do Timtim de verdade, rota de cada buraco,
ritmo de tensão e descanso) e a skill **platformer** (pulo). Para repetir as medições: `node game/tests/metricas.js`.

## Medidas do Timtim (iguais em qualquer computador)

As regras do jogo agora andam em passos fixos de 1/240 s. Antes, o pulo dependia da taxa de quadros:
149 px num computador lento (30 quadros por segundo) e 161 px num rápido (144).

| Movimento | Altura | Tempo no ar | Distância correndo (mesma altura) |
|---|---|---|---|
| Pulo cheio | 162 px | 0,83 s | 257 px |
| Toque curto | 98 px | 0,55 s | — |
| Pulo duplo | 281 px | 1,29 s | 399 px |
| Pulo + planar (fases 2 e 3) | 162 px | 1,74 s | 539 px |
| Pulo duplo + planar | 281 px | 2,90 s | 899 px |

Regras usadas para conferir:
- No caminho principal, nenhum salto passa de **70%** do alcance do movimento que ele pede.
- Uma tábua que se alcança com o pulo simples fica pelo menos **20 px abaixo** do topo do pulo
  (ou bem acima, de propósito, pedindo o pulo duplo). Assim nunca fica no "quase".
- Chocolate ou mancha de tinta (5 s lento) não pode vir logo antes de um buraco que o Timtim lento não atravessa.

## O que mudou

| Fase | Mudança | Por quê |
|---|---|---|
| Todas | Pulo calculado em passos fixos | O pulo saía 12 px mais baixo em computador lento |
| 1 | Tábuas de 5220, 6300, 7260 e 8160 desceram de 152 para 130 px | Ficavam a 3 px do topo do pulo; num computador lento nem eram alcançadas |
| 1 | Bandeira nova em 2600 | Eram 13 s correndo até a primeira bandeira, a maior distância das 3 fases, logo na primeira fase |
| 2 | Tábua de 2150 desceu para 130 px (com os biscoitos de cima) | Mesmo "quase" |
| 2 | As tábuas da quadrilha passaram a andar no relógio da fase (`S.clock`), não no da música | Andavam **1,55×** mais rápido que o período declarado (picos de 16×), e **saltavam 195 px** ao voltar da pausa. A rota pelo vão de 1380 px dependia da máquina de quem jogava; agora `per` vale o que esta tabela supõe (medido: 21%) |
| 2 | Saiu o chocolate de 1950 | Lento, o Timtim não atravessava o vão de 630 px logo depois (só a 85% do alcance com pulo duplo + planar da tábua) |
| 3 | Tábuas de 2250 e 6150 desceram para 130 px (com os biscoitos de cima) | Mesmo "quase" |

## Rota de cada buraco (depois das mudanças)

**Fase 1, só pulo e pulo duplo.** Os 7 buracos têm uma tábua no meio: nenhum salto passa de 10% do alcance.
O buraco mais largo (7190–7420, 230 px) se atravessa pela tábua de 7260 ou direto a 68%.

**Fase 2, com planar:**
- 1150–1670 (520 px): aula do planar, a 52% com pulo duplo + planar. Cair não custa coração até aprender.
- 2370–3000 (630 px): a 64% com pulo duplo + planar. É o primeiro buraco que pede os dois juntos.
- 4500–5880 (1380 px): pelas tábuas da quadrilha, nenhum salto passa de 21%.
- 6160–6300: a 16%.

**Fase 3, com planar e redemoinhos:** nenhum salto passa de 27%. A tábua de 3250 (202 px) pede pulo duplo;
o redemoinho de 3450 é o outro caminho. As estrelas que piscam (6420 e 6520) pedem pulo duplo,
e são o teste final antes do Corvo-Borrão.

## Ritmo (tensão por trecho de 800 px)

Conta: inimigo 0,16 · buraco 0,1 + largura/4000 · chocolate 0,08 · revoada 0,06 por bicho ·
tábua móvel 0,1 · estrela 0,12; amigo e bandeira contam como descanso.

```
Fase 1          Fase 2              Fase 3
   0 ·            0 ·                 0 ·
 800 ███        800 █████           800 █         (redemoinho de aula, sobre o chão)
1600 ████      1600 █████████       1600 █████████ (girassóis que sobem e descem)
2400 ████      2400 ██              2400 █████
3200 ██████    3200 ██████          3200 █████████
4000 ██        4000 ██████████      4000 ███████████ (o pico: revoada de 4 + buraco)
4800 ████      4800 ████            4800 ·         (descanso: amigo + bandeira)
5600 ████████  5600 ·  (amigo)      5600 ████
6400 █████     6400 █████████       6400 ████████  (estrelas)
7200 ███
8000 ████████
8800 ·  (bandeira antes do chefão)
```

- As 3 fases começam com um trecho de aula e sobem em dente de serra, com descanso entre os picos. É o que a skill pede.
- Todas têm bandeira logo antes da arena do chefão.
- Fase 2: o trecho de 1600 é o mais alto da fase logo depois da aula (galinhas, inimigo, o vão de 630 px).
  Tirar o chocolate desse trecho já baixou a tensão; o resto ficou de propósito, porque é o "agora sem rede" do planar.
- Fase 3: as estrelas que piscam vêm logo antes do chefão, sem descanso. Ficou assim porque o cartão de abertura
  da luta serve de pausa, e cair nelas volta para a bandeira de 6080, bem perto.

## Perguntas para quem jogar (teste com uma criança)

Jogue do começo ao chefão sem ajuda e anote:
1. Em que lugar não soube para onde ir?
2. Qual salto errou mais de 3 vezes? (diga a fase e o que tinha perto)
3. Qual trecho ficou chato ou comprido demais?
4. Quanto tempo levou cada fase?
