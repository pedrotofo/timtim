# FILME 2 — "REC" (missão do filmmaker) · v2 Fortaleza

Segue o `PLAYBOOK_fashion_film_open_world.md`: 9:16, 1080x1920, 24 fps, **40 s**, cutscene/gameplay de jogo
de mundo aberto next-gen, **Fortaleza à noite**, base realista e vivida + neon motivado (mesma estética do
filme 1).

**Logline:** ele não carrega arma, carrega uma câmera. Um filmmaker é contratado para gravar escondido quem
recebe uma maleta prata num iate no Mucuripe. A luz vermelha do REC o entrega. Ele foge na garupa da moto da
parceira **sem parar de gravar**, despista o SUV dos bandidos na areia da Praia de Iracema e entrega o vídeo.

---

## 0. O que mudou da v1 e por quê (problema de clareza)
Na v1, quem viesse de fora não entenderia três coisas. Corrigido assim:

| Dúvida do público na v1 | Correção na v2 |
|---|---|
| "De onde surgiu essa moto e quem é essa pessoa?" | A Piloto **leva ele até o píer no take 1** e combina "5 minutos" com um gesto. Quando ela volta, o público já conhece. |
| "Quem são os caras do SUV?" | O SUV aparece **estacionado no cais** durante a troca, e os **mesmos dois homens** entram nele. Mesmo figurino, mesma maleta. |
| "Por que a luz vermelha importa?" | A luz REC é **mostrada acendendo** antes (take 4). Depois, ela é o único ponto vermelho no escuro e o vilão a vê **do ponto de vista dele**. |
| "Como ele escapou?" (salto da ponte não fazia sentido em Fortaleza) | A moto desce para a **areia**, onde o SUV não entra. O SUV para no meio-fio e os homens ficam olhando o escuro. Vitória lógica e visível. |
| "Para que serve a gravação?" | A missão é dita no início ("Grave quem pega a maleta. Me mande o vídeo") e paga no fim (vídeo enviado + "Recebido"). |
| Cartão de memória sem consequência | Cortado. Menos objetos, mais clareza. |

**Regra de ouro:** cada virada da história é mostrada com **ação + reação** em dois takes seguidos, e todo
objeto ou personagem que vai ser importante aparece **antes** de ser usado.

### Plantar e colher (setup → payoff)
| Plantado em | Elemento | Colhido em |
|---|---|---|
| T1 | Piloto e moto preta/laranja | T11 (ela resgata) |
| T2 | Missão: "Grave quem pega a maleta" | T6 (ele grava) e T20 (ele envia) |
| T3 | Gesto "5 minutos" | T11 (ela está esperando, moto ligada) |
| T4 | Luz REC vermelha acende | T7 e T8 (a luz o entrega) |
| T5 | SUV preto parado no cais | T10 e T12 (os homens correm para ele) |
| T15 | Piloto aponta para a praia | T17 e T18 (descem para a areia) |

---

## 1. Bíblia de continuidade (colar SEMPRE, palavra por palavra, nos prompts)
Copiar estes blocos sem mudar nenhuma palavra. A IA só mantém a continuidade se a descrição for idêntica
em todos os takes.

> **Figurino:** o figurino abaixo é provisório. Quando as fotos chegarem, ajusto para a roupa real e travo.

**[CHAR_FILMMAKER]**
`the filmmaker: the man from the face reference images (keep his exact face, hair and beard), wearing a black
zip-up bomber jacket, plain dark grey t-shirt, black cargo trousers, black sneakers with white soles; he
carries a black Sony full-frame mirrorless camera with a 24-70mm lens on a black neck strap, with a small red
recording tally light on the front of the camera`

**[CHAR_PILOTA]**
`the rider: a slim woman whose face is never visible, matte black full-face motorcycle helmet with one thin
orange stripe down the middle and a dark smoked visor always closed, black leather riding jacket, dark jeans,
black boots, black gloves`

**[MOTO]**
`a matte black naked sport motorcycle with orange accents and a thin orange stripe on the wheel rims, round
LED headlight, no visible brand logos`

**[CHAR_HOMEM_A]** (entrega a maleta)
`man A: heavy-set man in his fifties, short grey hair, white linen shirt, gold wristwatch`

**[CHAR_HOMEM_B]** (recebe a maleta e persegue)
`man B: tall lean man in his forties, black baseball cap, dark navy polo shirt`

**[MALETA]** `a silver aluminium briefcase`

**[SUV]**
`a black full-size SUV with dark tinted windows and a thin horizontal cold-white LED headlight bar, no visible
brand logos`

**[IATE]** `a white motor yacht with a single navy-blue stripe on the hull`

**[ESTILO]** (início de todo prompt de imagem)
`Cutscene frame from a 2026 next-gen open-world video game set in Fortaleza, Brazil, at night, real-time
game-engine render with ray-traced reflections, slightly stylized AAA game character shading (not a
photograph). Lived-in realistic city with motivated neon: magenta, violet and cyan light coming from real
signs and facades, mixed with orange sodium streetlights and greenish fluorescent light. Vertical 9:16.`

**[FORTALEZA]** (quando houver cidade em quadro)
`Fortaleza geography: flat seafront, tall residential towers along the beach avenue, no hills or mountains
anywhere, plain grey concrete pavers on the sidewalk (no black-and-white wave mosaic), coconut palms with
warm string lights, beach kiosks with plastic chairs, food carts, motorcycle taxis, overhead tangled power
lines, worn asphalt with only a few puddles`

**[EVITAR]** (fim de todo prompt)
`No one looks into the camera. No visible brand logos except the Sony camera. No pink-teal colour cast over
everything, no mirror-wet ground in the whole frame, no empty city, no light without a source, no text
unless specified.`

### Regras de câmera e direção de cena
- **Direção de tela na fuga:** a moto **sempre se move da esquerda para a direita** nos planos laterais e
  aéreos. O SUV vem **atrás, entrando pela esquerda**. Nunca inverter, ou o público acha que mudou de lado.
- **Estado dos objetos:** a câmera dele está **sempre na mão ou no olho e sempre gravando** do T4 ao T19 (luz
  vermelha acesa). Do T11 em diante ele está **na garupa, atrás da Piloto**. A maleta fica com o Homem B do
  T6 em diante.
- **Luz por local** (repetir no prompt de cada local):
  - Mucuripe: sódio laranja dos postes do cais + verde fluorescente de um galpão de pesca + reflexo frio da água.
  - Beira-Mar: magenta e violeta de letreiros de bares e hotéis + cordões quentes nos coqueiros.
  - Praia de Iracema: ciano e magenta de neon de bar + luz azul dos refletores da Ponte dos Ingleses.
- Ninguém olha para a lente. O vilão olha **para o ponto vermelho**, não para a câmera do filme.

---

## 2. Referências mestre (gerar e aprovar ANTES dos takes)
Gerar estas imagens primeiro e usá-las como referência em todos os takes. É o que garante a continuidade.
1. **REF_FILMMAKER:** folha de personagem (frente, 3/4, costas, com a câmera no olho), a partir das suas fotos.
2. **REF_PILOTA_MOTO:** a Piloto montada na moto, de lado, com a moto inteira em quadro.
3. **REF_VILOES_SUV:** Homem A e Homem B lado a lado com a maleta, e o SUV atrás.
4. **REF_LOCAL_MUCURIPE:** cais de pesca com jangadas, píer de madeira, iate branco, guindastes do porto ao
   fundo com luzes vermelhas de aviação.
5. **REF_LOCAL_BEIRAMAR:** Av. Beira-Mar à noite, com prédios, coqueiros, barracas da feirinha e trânsito.
6. **REF_LOCAL_IRACEMA:** calçadão e areia da Praia de Iracema, com a Ponte dos Ingleses iluminada ao fundo.

Em cada take, anexar só as referências citadas na linha **Refs**, mais o **frame do take anterior** quando o
take continua a mesma ação.

---

## 3. Roteiro take a take
Formato de cada take:
- **Entender:** o que o público precisa captar.
- **Imagem:** prompt para GPT Image 2.6, sempre precedido por [ESTILO] e seguido por [EVITAR].
- **Movimento:** prompt para Kling 3.0 pro: o que se move, do início ao fim.

Textos de tela (celular e HUD) entram **na edição**, não na geração. Nos frames, a tela do celular sai em
branco e brilhante.

### ATO 1 — A ENCOMENDA (0 a 10 s)

**T1 · 0,0–2,0 s · Chegada**
- Entender: uma dupla de moto chega de noite numa área portuária de Fortaleza.
- Refs: REF_PILOTA_MOTO, REF_FILMMAKER, REF_LOCAL_MUCURIPE
- Imagem: `High aerial drone shot at night over the Mucuripe fishing harbour in Fortaleza: [MOTO] ridden by
  [CHAR_PILOTA] with [CHAR_FILMMAKER] on the pillion seat, travelling left to right on the harbour road toward
  a wooden pier; jangadas moored, [IATE] lit at the end of the pier, port cranes with red aviation lights in
  the distance, beachfront towers along the horizon. [FORTALEZA]`
- Movimento: `Drone slowly tilts down and follows the motorcycle as it rides left to right and slows near the
  pier entrance.`
- HUD (edição): **MISSÃO: A PROVA**

**T2 · 2,0–3,5 s · A ordem**
- Entender: ele recebe a missão por mensagem.
- Refs: REF_FILMMAKER
- Imagem: `Over-the-shoulder close-up from behind [CHAR_FILMMAKER] seated on the pillion of the parked [MOTO],
  holding a smartphone with a bright blank white chat screen, his face partly lit by the screen, harbour
  sodium lights blurred behind.`
- Movimento: `Phone vibrates slightly in his hand, his thumb scrolls once, subtle breathing.`
- Tela do celular (edição): **"Iate branco, Mucuripe. Grave quem pega a maleta prata. Me mande o vídeo."**

**T3 · 3,5–5,0 s · O combinado**
- Entender: ele desce, e ela vai esperar 5 minutos ali.
- Refs: REF_FILMMAKER, REF_PILOTA_MOTO, REF_LOCAL_MUCURIPE
- Imagem: `Medium shot at the wooden pier entrance: [CHAR_FILMMAKER] stepping off the pillion of [MOTO];
  [CHAR_PILOTA] stays seated, engine on, turning her helmet toward him and tapping two gloved fingers on her
  wrist. Orange sodium lamp overhead, fish market shed with green fluorescent light behind.`
- Movimento: `He swings his leg off the bike and walks toward the pier; she taps her wrist twice and nods.`

**T4 · 5,0–6,5 s · O REC acende** (plantio)
- Entender: a câmera tem uma luz vermelha que acende quando grava.
- Refs: REF_FILMMAKER
- Imagem: `Extreme close-up of [CHAR_FILMMAKER]'s hands holding the black Sony mirrorless camera, thumb pressing
  the record button, the small red tally light on the front of the camera just turning on, glowing in the
  dark; shallow depth, harbour lights in bokeh.`
- Movimento: `Thumb presses the button, the red light turns on and stays glowing.`

**T5 · 6,5–8,0 s · O esconderijo**
- Entender: ele se esconde e vê o iate, os dois homens e o SUV parado.
- Refs: REF_FILMMAKER, REF_VILOES_SUV, REF_LOCAL_MUCURIPE
- Imagem: `Over-the-shoulder wide shot from behind [CHAR_FILMMAKER] crouched between stacked fishing crates
  and a jangada on the pier, camera raised to his eye; in the background at the end of the pier [IATE] under
  deck lights, [CHAR_HOMEM_A] and [CHAR_HOMEM_B] standing on the deck, and [SUV] parked on the quay with
  headlights off.`
- Movimento: `He settles into position and raises the camera to his eye; the men on the yacht talk; gentle
  water motion.`

**T6 · 8,0–10,0 s · A troca gravada**
- Entender: pela câmera, vemos o Homem A entregar a maleta ao Homem B.
- Refs: REF_VILOES_SUV, REF_LOCAL_MUCURIPE
- Imagem: `Telephoto view through a camera at night: on the deck of [IATE], [CHAR_HOMEM_A] hands [MALETA] to
  [CHAR_HOMEM_B]; deck lights, slight digital noise, both men in clear profile.`
- Movimento: `Focus pulls from soft to sharp on the briefcase changing hands; slight handheld drift.`
- Edição: moldura de visor com **● REC 00:00:12** e HUD **GRAVE A TROCA**

### ATO 2 — DESCOBERTO (10 a 15 s)

**T7 · 10,0–11,0 s · O ponto vermelho**
- Entender: no escuro, a única coisa visível é a luz vermelha dele.
- Refs: REF_FILMMAKER, REF_LOCAL_MUCURIPE
- Imagem: `Dark wide shot of the pier crates where [CHAR_FILMMAKER] hides, almost entirely in shadow; the only
  bright point is the small red recording light on his camera.`
- Movimento: `Static; the red light blinks once.`

**T8 · 11,0–12,0 s · O vilão vê** (contraplano)
- Entender: o Homem B vê a luz e aponta para ela.
- Refs: REF_VILOES_SUV, REF_LOCAL_MUCURIPE
- Imagem: `Over-the-shoulder shot from behind [CHAR_HOMEM_B] on the yacht deck holding [MALETA], looking down
  the dark pier; far away among the crates, one tiny red dot of light; his free arm starting to point at it.`
- Movimento: `He turns his head, freezes, and points his arm toward the red dot.`

**T9 · 12,0–13,0 s · A lanterna**
- Entender: ele foi descoberto.
- Refs: REF_FILMMAKER
- Imagem: `Close-up of [CHAR_FILMMAKER] behind the crates, a harsh white flashlight beam hitting his face from
  frame right, eyes wide, camera still at chest height with the red light on.`
- Movimento: `Flashlight beam sweeps onto his face; he flinches and starts to rise.`

**T10 · 13,0–15,0 s · A corrida**
- Entender: ele foge pelo píer sem parar de filmar, e o SUV acende atrás.
- Refs: REF_FILMMAKER, REF_VILOES_SUV, REF_LOCAL_MUCURIPE
- Imagem: `Low tracking shot in front of [CHAR_FILMMAKER] running toward camera along the wooden pier, his arm
  extended behind him pointing the camera backward (red light on); in the background [CHAR_HOMEM_A] and
  [CHAR_HOMEM_B] running to [SUV], whose white LED headlight bar is switching on.`
- Movimento: `He sprints toward camera; behind him the SUV headlights flash on.`
- HUD (edição): **●○○○○ FUJA SEM PARAR DE GRAVAR**

### ATO 3 — A FUGA (15 a 31 s)

**T11 · 15,0–16,5 s · O resgate**
- Entender: a Piloto estava esperando, como combinado.
- Refs: REF_FILMMAKER, REF_PILOTA_MOTO, REF_LOCAL_MUCURIPE (+ frame do T3)
- Imagem: `Same pier entrance as before: [CHAR_PILOTA] on [MOTO] with the headlight on, twisting the throttle,
  reaching her gloved hand back; [CHAR_FILMMAKER] leaping onto the pillion seat, camera in his hand.`
- Movimento: `He jumps onto the pillion; she grabs his arm; the rear wheel spins.`

**T12 · 16,5–18,0 s · A largada**
- Entender: os dois arrancam, e o SUV sai do cais atrás deles.
- Refs: REF_PILOTA_MOTO, REF_VILOES_SUV
- Imagem: `Low ground-level side shot: [MOTO] with [CHAR_PILOTA] and [CHAR_FILMMAKER] launching left to right,
  rear tyre smoking; in the background left, [SUV] pulling out from the quay with headlights blazing.`
- Movimento: `Motorcycle accelerates out of frame right; the SUV follows from the left.`

**T13 · 18,0–19,5 s · Filmando de costas**
- Entender: ele vai virado para trás na garupa, filmando o SUV.
- Refs: REF_FILMMAKER, REF_PILOTA_MOTO, REF_VILOES_SUV, REF_LOCAL_BEIRAMAR
- Imagem: `Front tracking shot of [MOTO] on Avenida Beira-Mar at night: [CHAR_PILOTA] riding toward camera;
  behind her [CHAR_FILMMAKER] twisted backward on the pillion, holding the camera with the red light on
  aimed at [SUV] chasing a few metres behind. [FORTALEZA]`
- Movimento: `Camera tracks backward ahead of the bike; the SUV closes the distance; street lights stream past.`
- HUD (edição): **●●○○○**

**T14 · 19,5–21,0 s · O que a câmera dele vê**
- Entender: o SUV está quase encostando.
- Refs: REF_VILOES_SUV, REF_LOCAL_BEIRAMAR
- Imagem: `Handheld point-of-view through a camera aimed backward from a moving motorcycle: [SUV] fills the frame,
  LED headlight bar blooming, [CHAR_HOMEM_B] visible in the passenger seat through the windshield, Beira-Mar
  neon behind.`
- Movimento: `Shaky handheld; the SUV lunges closer; headlights flare.`
- Edição: moldura de visor **● REC**

**T15 · 21,0–23,0 s · A decisão**
- Entender: a Piloto tem um plano e aponta para a praia.
- Refs: REF_PILOTA_MOTO, REF_FILMMAKER, REF_LOCAL_BEIRAMAR
- Imagem: `Medium side shot of [MOTO] travelling left to right along the beachfront: [CHAR_PILOTA] extends her left
  arm and points toward the dark beach on the right side of the road; [CHAR_FILMMAKER] turns his head to look.
  Palms with string lights, kiosks with plastic chairs. [FORTALEZA]`
- Movimento: `She points firmly toward the beach; he looks and nods.`
- HUD (edição): **●●●○○**

**T16 · 23,0–25,0 s · Costurando o trânsito**
- Entender: a moto escapa pelo meio da feirinha e dos carros, e o SUV fica para trás.
- Refs: REF_PILOTA_MOTO, REF_VILOES_SUV, REF_LOCAL_BEIRAMAR
- Imagem: `High aerial shot of Avenida Beira-Mar at night: [MOTO] weaving left to right between taxis and
  mototaxis past the craft fair stalls with white tents; [SUV] behind on the left, braking hard behind a bus.
  [FORTALEZA]`
- Movimento: `Motorcycle threads through traffic; the SUV brakes and swerves.`
- HUD (edição): **●●●●○**

**T17 · 25,0–28,5 s · Descendo para a areia** (clímax)
- Entender: eles saem da avenida e descem do calçadão direto para a areia.
- Refs: REF_PILOTA_MOTO, REF_FILMMAKER, REF_LOCAL_IRACEMA
- Imagem: `Dramatic low-angle side shot at Praia de Iracema: [MOTO] airborne for a moment as it drops off the edge
  of the concrete promenade onto the sand, travelling left to right, [CHAR_PILOTA] riding and [CHAR_FILMMAKER]
  holding on with one hand and the camera in the other (red light on); Ponte dos Ingleses lit blue in the
  background, neon bar signs on the left.`
- Movimento: `Slow motion: the bike leaves the promenade edge, floats, and lands in the sand, spraying it.`
- HUD (edição): **●●●●●**

**T18 · 28,5–31,0 s · Despistados** (vitória)
- Entender: o SUV não entra na areia e os bandidos perdem a dupla.
- Refs: REF_VILOES_SUV, REF_LOCAL_IRACEMA
- Imagem: `Wide shot from the sand looking back at the promenade: [SUV] stopped hard at the kerb, headlight bar
  pointing at empty dark sand; [CHAR_HOMEM_B] standing by the open door, holding [MALETA], looking around;
  far right in the darkness, one small orange tail light disappearing along the shoreline.`
- Movimento: `Man B slams his hand on the SUV roof; the distant tail light fades away.`
- HUD (edição): as bolinhas apagam **○○○○○ VOCÊ DESPISTOU**

### ATO 4 — A PROVA (31 a 40 s)

**T19 · 31,0–34,5 s · O vídeo enviado**
- Entender: ele confere a gravação, manda o vídeo e a missão é cumprida.
- Refs: REF_FILMMAKER, REF_PILOTA_MOTO, REF_LOCAL_IRACEMA
- Imagem: `Late-night blue hour at the end of the Ponte dos Ingleses pier: [MOTO] parked; [CHAR_PILOTA] leaning on
  it; [CHAR_FILMMAKER] holding the Sony camera, its rear screen showing [CHAR_HOMEM_B] receiving [MALETA]
  sharp and clear, and in his other hand a smartphone with a bright blank white screen. City towers lit on the
  horizon.`
- Movimento: `He looks at the camera screen, then taps the phone; she looks over his shoulder.`
- Telas (edição): celular **"Enviando vídeo… 100%"**, depois a resposta **"Recebido. Pagamento feito."**
- HUD (edição): **MISSÃO CUMPRIDA**

**T20 · 34,5–37,5 s · O gancho**
- Entender: já tem outra missão chegando.
- Refs: REF_FILMMAKER, REF_PILOTA_MOTO
- Imagem: `Close two-shot: [CHAR_FILMMAKER] looking down at the phone with a slight smile; beside him [CHAR_PILOTA]
  turning her helmet toward him; the phone lights up both of them, sea and city lights behind.`
- Movimento: `The phone vibrates again; he raises an eyebrow; she starts the bike.`
- Tela (edição): **"Nova missão disponível"**

**T21 · 37,5–40,0 s · Assinatura**
- Tela preta com **seu logo/assinatura** minimalista em branco e um slam grave.

---

## 4. Som (resumo, conforme playbook seção 4)
- Ato 1: ambiência de cais (água, cordas, gerador de barco), foley da câmera (clique do REC bem audível no T4).
- Ato 2: corte para silêncio no T7, **bip** da luz, sucção reversa no T8, **braam** no T9.
- Ato 3: moto forte, SUV V8 grave, pass-bys na Beira-Mar, perspectiva abafada no POV da câmera (T14), corte
  para só sub + respiração no ar (T17) e impacto na areia.
- Ato 4: mar calmo, notificação do celular, sub-drop no MISSÃO CUMPRIDA e slam na assinatura.
- Música: synthwave/eletrônica noturna do Artlist. Se vier uma faixa sua, aplicar a seção 5 do playbook.

## 5. Fotos que preciso de você
- 3 a 5 de rosto (frente e 3/4 dos dois lados), luz uniforme, sem óculos escuros
- 2 de corpo inteiro com a roupa do filme (aí travo o figurino da bíblia)
- 2 a 3 **segurando sua Sony** do jeito que você segura (no olho e na cintura)
- 1 da câmera sozinha com a lente que você usa
- Seu logo/assinatura para a tela final (PNG, se tiver)

## 6. Cuidados
- Nada de logo, fonte, nome ou "estrelas de procurado" do jogo: o HUD de bolinhas REC substitui.
- Hashtags e menção ao lançamento ficam na legenda do post.
- Conferir se a IA não deforma o logo da Sony e cobrir logos de montadora inventados no SUV ou na moto.
- Sem violência: ninguém atira; a ameaça é a lanterna e o SUV.
- Créditos estimados: 6 referências mestre + ~22 frames high + 20 vídeos Kling 3.0 pro.
