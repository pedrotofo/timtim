# Workflow de vídeo com IA

Adaptado do método do Eian (Claude como diretor + gerador de imagem + gerador de vídeo),
com o **Nano Banana Pro (Google Flow)** no lugar do gerador de imagem, porque não gasta créditos.

## Princípio central

**Pegar o erro antes de gastar dinheiro.**
Texto é de graça → imagem (Flow) é de graça → vídeo custa crédito por segundo.
Erro que dá para ver no texto não chega na imagem; erro que dá para ver na imagem não chega no vídeo.

## Papéis

| Quem | Faz |
|---|---|
| Usuário | Escolhe a direção, aprova o estilo, aprova gastos, assiste ao movimento e escuta o som |
| Claude (diretor) | Roteiro, storyboard, todos os prompts, revisão de cada imagem e vídeo, pós-produção com código |
| Nano Banana Pro / Flow (desenhista) | Fichas de personagem, testes de estilo, primeiro e último quadro de cada cena |
| Gerador de vídeo (animador) | Transforma primeiro e último quadro em alguns segundos de vídeo |

## Regras

1. Nenhuma imagem antes de o usuário aprovar o roteiro.
2. Nenhuma cena definitiva antes de o usuário aprovar o estilo.
3. Antes de gerar cada vídeo, um **revisor novo** (subagente sem o histórico da conversa) confere o prompt e as imagens. Ele só aponta erros, não altera arquivos. Se passar, mostrar o custo e esperar o "ok".
4. Se o vídeo tiver problema: primeiro tentar **cortar**, depois **consertar com código**. Só gerar de novo se não der, e só aquela cena, com o prompt ou as imagens corrigidos.
5. Versão nova vai em arquivo novo. Nunca sobrescrever nem apagar (takes antigos podem servir).
6. O Claude não vê movimento nem ouve som, só quadros extraídos. Sempre dizer o que não foi verificado.
7. Nunca comprar créditos. Se o saldo acabar, parar e montar um corte bruto com o que já existe.

## Etapas

### 1. Roteiro
- Estrutura **por episódios**, cada cena independente (é a mais segura). Narrativa contínua só se o usuário pedir.
- Lógica real: para cada virada, perguntar "por quê? de onde veio isso? dá para alcançar?".
- Dá para resumir em **uma frase**? Se não der, o roteiro não está pronto.
- **Gancho nos primeiros 2 segundos**: a imagem mais forte vem primeiro.
- Reações com **ordem**: problema → como o protagonista resolve → reação dos outros, um de cada vez, nunca simultâneas.
- Evitar o que a IA faz mal: personagens se cruzando, mão segurando objeto pequeno, texto, espelhos e reflexos, detalhes assimétricos, troca de luz no meio da cena, 3 ações seguidas da mesma pessoa, plongée sem rosto, muitos figurantes.
- Com música: virada no refrão, ação-chave no tempo forte.
- **Revisor novo** lê só o roteiro final e aponta erros.

### 2. Storyboard
Uma linha por cena com: tempo no filme, segundos a gerar (arredondar para cima e somar ~0,5 s), enquadramento, ângulo, movimento de câmera, quem vai para onde (esquerda/direita **da tela**), qual expressão conduz a cena, **o que se move** e a transição para a próxima.
- Mudar o ângulo a cada cena. No máximo 2 cenas frontais na altura dos olhos no filme inteiro.
- Sempre algo se movendo. Alternar plano geral, médio e close.
- Movimento de câmera com motivo: seguir algo, aproximar devagar para um close ou abrir devagar.
- Olhos ou cabeça a **38% ou 62%** da largura, nunca no centro.
- **Paleta definida antes da primeira imagem**, com uma tabela de cores por cena. Testar em preto e branco: se o personagem some no fundo, falta contraste.
- Esboço em blocos de cor (1920×1080) por cena, feito com código, montado numa prancha para aprovação.

### 3. Estilo e fichas (Flow)
- Testar o estilo com imagem de referência.
- Ficha de cada personagem: frente, perfil e expressões. **Fixar a posição** de detalhes (tatuagem no braço esquerdo, boné, corrente).
- **Quando o personagem é o usuário**: usar 2 a 4 fotos reais dele como referência (frente, perfil, boa luz) e gerar a ficha antes de qualquer cena.
  - As **fotos reais vêm primeiro e mandam no rosto**. Nunca usar uma ficha estilizada como referência principal: ela já distorce cabelo e traços, e cada imagem gerada a partir dela distorce mais.
  - Só seguir para as cenas depois que o usuário aprovar a ficha dizendo "sou eu".
  - Usar a **mesma ferramenta de imagem** (Nano Banana Pro) em todas as cenas. Misturar geradores muda o rosto.

### 4. Primeiro e último quadro (Flow)
- Antes de desenhar, descrever por escrito o primeiro quadro, o último e o que acontece no meio, e passar pelo revisor.
- Desenhar primeiro o quadro mais cheio (geralmente o último) e **editar** a partir dele para fazer o primeiro. Assim a câmera e o enquadramento ficam iguais.
- Para uma aproximação lenta, o último quadro pode ser um recorte ampliado do primeiro.
- Conferir a proporção (16:9 ou 9:16) e se os dois quadros têm o mesmo tamanho.
- **Checklist**:
  1. Todo objeto usado na ação já aparece no primeiro quadro.
  2. A reação de outra pessoa já está posicionada (alguém ao fundo de frente para a câmera).
  3. Pessoas em grupo não estão na mesma pose.
  4. Há espaço livre para a ação e para a cabeça.
  5. O vento sopra para o mesmo lado em tudo.
  6. A cena funciona no tamanho de uma tela de celular.
  7. Não há objetos sobrando nem linhas estranhas.
  8. Sobrepondo o primeiro e o último quadro, o que não deveria mudar está idêntico.
- Para editar só um pedaço, colar a parte corrigida de volta na imagem original.

### 5. Prompt de vídeo (7 blocos)
```
[ESTILO] uma frase. Estilo, cores e personagens idênticos ao primeiro e ao último quadro.
[CÂMERA] X s, enquadramento, ângulo, movimento (ou "câmera parada, sem corte").
[COMPOSIÇÃO E CORES] onde está cada coisa e cada pessoa, com as cores, igual ao primeiro quadro.
[PERSONAGENS] aparência, roupa e acessórios, sempre descritos da mesma forma.
[SEGUNDO A SEGUNDO]
0–0,2 s: imagem parada, idêntica ao primeiro quadro.
... quem faz o quê, para que lado da tela, onde ficam as mãos ...
últimos 0,3 s: todos parados, idêntico ao último quadro.
[SOM] só sons com origem visível. Ninguém fala.
[RESTRIÇÕES] só as pessoas e os objetos do primeiro quadro; rosto e corpo constantes; plano único; sem texto, legenda ou marca d'água.
```

Erros comuns e como escrever:

| Erro do modelo | Como escrever |
|---|---|
| Todos agem ao mesmo tempo | "A primeiro… 1 a 2 s depois B… C por último" |
| A pessoa faz o que o vento deveria fazer | Dizer a causa + "as mãos nunca tocam X" |
| Nuvem ou planta ganha rosto | Descrever a textura de forma realista, sem "desenho animado" |
| Anda para o lado errado | "Anda para a esquerda da tela" |
| Frase ambígua | Dar a posição exata ("na janela do canto superior esquerdo") |
| A quantidade de objetos muda | Dizer o número ("só um envelope amarelo") |
| "Não faça X" é ignorado | Escrever o que deve acontecer, de forma positiva |
| Objeto aparece do nada | Usar só o que já está no primeiro quadro |
| Boné, tatuagem ou chuva somem | Desenhar no primeiro **e** no último quadro |
| Ações demais | 1 ou 2 ações por cena |
| A boca se mexe sozinha | "Ninguém fala"; se continuar, consertar com código |
| Entra música não pedida | Descartar o áudio e colocar o som na pós |
| A imagem escurece ou esfria com o tempo | Corrigir a cor tomando o primeiro quadro como referência |

### 6. Gerar o vídeo
- Gerar em 720p e ampliar para 1080p na pós.
- Começar pelas 1 ou 2 cenas **mais difíceis** antes de mandar o resto.
- Usar o modelo mais barato que resolve; o caro só nas cenas complexas.
- Escutar antes de usar o áudio nativo.

### 7. Pós-produção (código)
- Transições com motion blur (8 a 16 subquadros, obturador de meio quadro).
- Cor por bloco do filme: só saturação e luminosidade, sem mexer no matiz, protegendo a pele. Sem grão, glow ou vinheta.
- Arquivos intermediários sem perda. Entrega em BT.709.
- Ampliar de 720p para 1080p com lanczos e um leve sharpen. Sem interpolação de quadros.
- Sincronizar com a música medindo as batidas no áudio original. Conferir 3 quadros antes e 3 depois de cada corte.

### 8. Revisão final
- **Revisor novo** recebe só o vídeo pronto: conta a história que entendeu, lista o que ficou confuso e, cena a cena, aponta repetições, objetos que mudam, saltos, mudança de cor e rosto deformado, separando "grave" de "menor". Também diz o que não conseguiu verificar (movimento, som).
- Registrar as lições aprendidas (estilo, prompts que funcionaram, erros) em `docs/licoes/`.

## Lições dos filmes anteriores (nov/2026)

### TLF (ficou ótimo): receita que funcionou
- Imagens: GPT Image 2.6 no Higgsfield, qualidade high, 9:16, com as fotos reais dos looks e os quadros já aprovados como referência de personagem e roupa.
- Animação: Kling 3.0 Pro no Higgsfield, 3 a 4 s por cena, **sempre partindo de um quadro aprovado**.
- Som e edição: Artlist (efeitos em WAV) e montagem com cor, textos e som feito do zero.
- Custo aproximado: cerca de 35 imagens (1,5 crédito cada) e 22 vídeos (6 a 8 créditos cada).

### Tofo GTA (ficou ruim): o que deu errado
- **Rosto estranho**: a referência principal foi uma ficha estilizada, e as fotos reais entraram tarde. → Ficha a partir de fotos reais, aprovada antes de tudo.
- **Roteiro sem continuidade**: cerca de 20 cenas para 40 s, partindo direto para as imagens, sem roteiro aprovado nem storyboard. → Seguir as etapas 1 e 2 com revisor novo; de 8 a 10 cenas em episódios.
- **Imagens estranhas**: ação complexa (moto, SUV, perseguição noturna) descrita só em texto, sem checklist. → Primeiro e último quadro, 1 ou 2 ações por cena e checklist da etapa 4.
- Imagens geradas no Flow (Nano Banana Pro). Ainda não sabemos se a ferramenta pesou no resultado ou se foi só o processo. → Testar a ficha do rosto nas duas ferramentas e comparar antes de produzir.
