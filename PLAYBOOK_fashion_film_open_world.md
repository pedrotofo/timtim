# PLAYBOOK — Fashion film "jogo de mundo aberto" (aprendizados do projeto TLF "A Entrega")

Cole este arquivo no início de uma conversa nova e diga: "Siga este playbook para um novo filme".

## 1. O formato que deu certo
- Vídeo vertical 9:16, 1080x1920, 24 fps, **40 s**, estética de cutscene/gameplay de jogo de mundo aberto
  next-gen, **noturno**, com cara de trend do momento.
- **Não é desfile de looks: é um filme com começo, meio e fim**, uma missão com mistério e tensão madura,
  sem violência explícita. O produto da marca é o "tesouro" ou a revelação final.
- Muitos cortes de 1 a 2,5 s (20 a 25 takes). Alternar planos abertos com detalhes: olhar, passo no chão,
  mão, textura da peça, objeto.
- Nomes de linhas/coleções aparecem **dentro do cenário** (placa de carro, letreiro neon, painel de LED,
  mensagem de celular, etiqueta), nunca como letreiro gritando.
- Logo da marca escondido em detalhes: chaveiro, adesivo no capacete, placa gravada na maleta, fachada,
  etiqueta da peça.
- Textos de missão estilo jogo ("Siga a moto", "Pegue a maleta"…) e "MISSÃO CUMPRIDA" numa versão;
  outra versão limpa.
- **Última tela: só o logo da marca minimalista** (branco no preto), com impacto sonoro.
- Gancho final que abre uma "parte 2" (ex.: celular vibra com "Nova missão disponível").

## 2. Fluxo de produção
1. **Briefing:** looks reais (prints servem; recortar as fotos), nomes das linhas/coleções, cidade.
2. **Roteiro curto:** atos com tempos, cenas, onde cada linha/logo aparece. Aprovar antes de gerar.
3. **Frames de estilo (2 a 4)** para aprovar a direção de arte antes de tudo.
4. **Storyboard completo** em imagens (GPT Image 2.6 no Higgsfield, qualidade high, 9:16), usando as
   fotos dos looks e os frames aprovados como referência de personagem/roupa.
5. **Animação:** Kling 3.0 pro no Higgsfield, 3 a 4 s por take, partindo do frame aprovado.
6. **Edição:** cortes, grade de cor, grão e textos, com o som feito do zero (ver seção 4).
7. **Entrega:** versão com missão, versão limpa, versão só com efeitos e pacote para o Premiere (seção 6).

## 3. Direção de arte aprovada (evitar cara de IA genérica)
O que **não** fazer, porque deu cara de IA:
- paleta rosa/azul-esverdeado em tudo, chão molhado espelhado em todo frame, mundo limpo e vazio
- personagem posando para a câmera, desfoque de fundo em tudo, luz sem origem

O que funcionou: uma **base realista e vivida + neon motivado** (como nos trailers do jogo):
- cidade real e viva: fiação, bares com cadeiras de plástico, carrinhos de comida, patinetes, mototáxi,
  frentista no celular, pedestres; asfalto gasto com **poças pontuais**
- neon magenta/violeta/ciano **vindo de fontes reais** (letreiro, tubo na cobertura do posto, fachada de
  hotel), misturado com poste de sódio laranja e fluorescente esverdeada
- coqueiros com cordões de luz quentes, reflexos no vidro do carro, primeiro plano emoldurando o quadro
  (painel, porta, janela)
- câmera de terceira pessoa de gameplay, perseguição, POV de dentro do carro; ninguém olhando para a lente
- personagem com acabamento de cutscene de jogo AAA (poros, leve estilização), não foto
- trecho de prompt que funcionou: "Cutscene frame from a 2026 next-gen open-world video game set in a neon
  tropical beach city, real-time game-engine render with ray-traced reflections, slightly stylized AAA game
  character shading (not a photograph)…"
- cidade específica: descrever a geografia real (ex.: Fortaleza = orla plana, prédios altos, píer, **sem
  morros**; pedir "plain grey concrete pavers, no black-and-white wave mosaic" para não virar Copacabana)
- usar "She wears EXACTLY the outfit from the reference image… keep cut, wash, seams…" + "use the
  reference only for the clothing" quando não houver autorização de rosto

## 4. Desenho de som (o que impressionou)
- **Silenciar todo o áudio gerado pelos clipes** (fica cortado e inconsistente). Som 100% refeito.
- Efeitos do **Artlist em WAV** (download_track com format "wav"; os links expiram em cerca de 60 s, então
  baixar em lotes de 3 a 4 logo após gerar o link).
- Camadas: ambiência por local (cidade, bar, interior de carro, neon), foley (saltos, maleta, travas,
  respiração), veículos fortes (ignição esportiva, V6/V8, burnout, pneu, moto, passagens), tensão
  (drone, sub pulsante, riser), **impactos de trailer** (braam, sub-drop, "heavy whoosh into impact",
  slam final), **whooshes graves e maduros** nos cortes, sucção reversa antes dos golpes.
- Sincronia: medir movimento/brilho quadro a quadro dos clipes para achar o instante da ação e alinhar o
  transiente de cada efeito.
- Perspectiva no corte: o mesmo som abafado de dentro do carro e cru do lado de fora.
- Master: passa-alta 28 Hz, compressor 2,5:1 em -18 dB, limitador em -1 dBTP, **-14 LUFS**.

## 5. Música (se o cliente mandar uma faixa)
- Detectar BPM, compassos, breakdowns e drops, e identificar o **refrão** (trecho de energia máxima com voz
  forte que se repete). **O refrão deve tocar na maior parte do vídeo**.
- Alinhar os cortes-chave a compassos (entrada, golpe principal, corte seco num clique).
- Na tensão, deixar o refrão **abafado** (passa-baixa) em vez de trocar de trecho; abrir de volta no golpe.
- Faixa comercial: avisar que para publicar precisa de licença de sincronização, e entregar também a versão
  só com efeitos.

## 6. Pacote Premiere (o que funcionou)
- Sequência em XML do Final Cut 7 (xmeml), importável no Premiere: V1 takes graduados com sobra de imagem,
  V2 textos PNG transparentes, áudio com cada efeito como clipe próprio já processado e com silêncio inicial
  para sincronia exata à amostra, faixas estéreo por categoria, mix de referência desligada, marcadores.
- **Gravar caminhos absolutos do computador da pessoa** (perguntar o caminho antes). Windows:
  `file://localhost/D%3a/...`. Mídia numa estrutura única, sem nomes com pontos extras.
- Limite de envio de arquivo: 500 MB, então dividir em partes e orientar a extrair tudo **na mesma pasta**.

## 7. Cuidados
- Não copiar logo, fonte ou nome do jogo: usar a estética. Se o cliente insistir, avisar uma vez do risco.
- Conferir e cobrir logos de terceiros que a IA inventar (ex.: estrela de montadora em roda).
- Rosto real de modelo só com autorização por escrito de uso de imagem em IA.
- Créditos usados no Higgsfield por filme: cerca de 35 imagens high (~1,5 crédito cada) + 22 vídeos
  Kling 3.0 pro de 3 a 4 s (~6 a 8 créditos cada).
