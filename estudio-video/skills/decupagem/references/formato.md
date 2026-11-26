# decupagem.json

O arquivo que liga as skills: `/ilustrar-fala` lê `ilustracoes`, `/premiere-xml` lê tudo.
Tempos em segundos da mídia original (com 3 casas); `tc_*` em HH:MM:SS:FF só para leitura.

```json
{
  "midia": "/caminho/absoluto/cliente.mp4",
  "fps": 25,
  "duracao": 24.49,
  "cliente": "Marina — Doce Raiz",
  "resumo": "Marina conta como a Doce Raiz saiu de uma cozinha em Fortaleza para três estados.",
  "trechos": [
    {
      "id": "T1",
      "inicio": 3.30, "fim": 7.24,
      "tc_in": "00:00:03:07", "tc_out": "00:00:07:06",
      "tema": "Origem",
      "texto": "Bom, a gente começou em 2019 numa cozinha pequena em Fortaleza.",
      "nota": 2,
      "uso": "abertura",
      "obs": "tirar o 'Bom,' do começo"
    }
  ],
  "ilustracoes": [
    {
      "id": "I1",
      "inicio": 11.10, "fim": 14.05,
      "tc_in": "00:00:11:02",
      "gatilhos": [
        {"palavra": "Ceará", "t": 11.70},
        {"palavra": "Pernambuco", "t": 12.40},
        {"palavra": "Bahia", "t": 13.35}
      ],
      "tipo": "mapa",
      "conteudo": {"regiao": "Brasil", "destaques": ["CE", "PE", "BA"], "pino": "Fortaleza"},
      "ideia": "Mapa do Nordeste; cada estado acende quando ela diz o nome.",
      "posicao": "metade direita, a cliente fica à esquerda"
    }
  ],
  "conferir": [
    {"t": 7.82, "tc": "00:00:07:21", "motivo": "ouviu '33 estados'; pelo contexto é 'três'"}
  ]
}
```

- `nota`: 3, 2 ou 1 (★). `uso`: `abertura`, `meio`, `fechamento`, `corte` (não usar) ou livre.
- `tipo` de ilustração: `mapa`, `numero`, `grafico`, `linha-do-tempo`, `lista`, `citacao`,
  `lugar-real`, `produto`, `logo`, `icone`, ou livre. `conteudo` traz o que a animação precisa
  (os números, os nomes, os itens), escrito como a pessoa disse.
- `gatilhos`: as palavras que disparam cada passo da animação, com o tempo vindo de
  `transcricao.json`. É o que deixa o motion sincronizado com a fala.
- `posicao`: onde a ilustração fica no quadro para não cobrir o rosto (olhe um frame:
  `ffmpeg -ss <t> -i VIDEO -frames:v 1 frame.jpg`).
