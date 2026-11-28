# progresso

Mostra numa faixa **acima do campo de digitação** quantas das tarefas declaradas já estão prontas
— em barra, fração e porcentagem, com o assunto da que está em curso:

```
▓▓▓▓░░░░░░ 4/10 · 40% · Revisar a progressão da fase 2
```

Feito para o projeto Timtim depois de uma sessão em que o trabalho correu horas sem que o outro
lado soubesse em que pé estava.

## A porcentagem é honesta, e por isso ela pode andar para trás

Ela é calculada **sobre as tarefas declaradas**, não sobre "quanto falta do trabalho". A segunda
não é mensurável: trabalho aparece no meio do caminho. Numa sessão real, "consertar um teste
vermelho" virou sete pontos frágeis — qualquer porcentagem dada no início estaria errada.

Então, quando aparece trabalho novo, o total cresce e a barra **recua**. Isso é intencional. Uma
barra que cai de 60% para 40% porque apareceu mais trabalho informa; uma que só sobe, mente.

## O aviso mais importante que ele dá

```
○ nenhuma tarefa declarada
```

Quando não há tarefa nenhuma, ele diz isso em vez de ficar em branco. É a informação que mais
importa: significa que ninguém está acompanhando nada, e que a sessão pode correr às cegas.

## Como ele sabe

Observa as chamadas das ferramentas de tarefa e lê o que o motor devolve, sem inferir nada:

| Ferramenta | O que ele lê |
|---|---|
| `TaskList` | a lista inteira — é a fonte autoritativa e conserta qualquer deriva da contagem |
| `TaskCreate` | uma tarefa nova entrou: o total cresce |
| `TaskUpdate` | o `statusChange { from, to }` que o próprio motor devolve |

A contagem vive em `$.state`, então sobrevive a um recarregamento do mod dentro da sessão.

## Limites

- A faixa só muda quando uma ferramenta de tarefa é chamada. Se ninguém declarar nada, ela fica no
  aviso de "nenhuma tarefa declarada" — o que é o comportamento certo.
- Ela sai da frente durante uma pesquisa do próprio aplicativo (`hasSurvey`).
- A porcentagem trata toda tarefa como de igual peso. Uma tarefa de dez minutos e outra de duas
  horas contam o mesmo.
