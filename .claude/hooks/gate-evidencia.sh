#!/usr/bin/env bash
# gate-evidencia.sh — Gate 1 do Timtim: BLOQUEIA o fim da resposta enquanto houver mudança no
# jogo sem prova de que ela foi vista rodando.
#
# Por que existe: na produção de 24-25/11/2026, mais da metade dos 50 commits foi refação, e os
# seis últimos foram conserto de celular descoberto no fim. O único controle de qualidade era o
# Pedro jogando e se incomodando — um gate humano que dispara tarde acha tudo de uma vez (71
# achados numa passada, em docs/revisao-hater.md).
#
# Diferente dos 18 hooks que vêm no framework, que avisam e nunca bloqueiam, este devolve 2: no
# evento Stop isso impede a resposta de encerrar e manda o texto do stderr de volta ao modelo.
#
# É BARATO DE PROPÓSITO. O evento Stop dispara a cada resposta, não uma vez por sessão, então
# este script não roda teste nenhum: ele compara datas de arquivo. Quem roda é
# game/tests/provar.sh, que escreve o recibo.
set -u

# --- raiz do projeto (mesma precedência dos outros hooks) --------------------
if [ -f "project.yaml" ] || { [ -d ".claude" ] && [ "${PWD##*/}" != ".claude" ]; }; then
  ROOT="$PWD"
elif [ -n "${CLAUDE_PROJECT_DIR:-}" ] && [ "${CLAUDE_PROJECT_DIR##*/}" != ".claude" ]; then
  ROOT="$CLAUDE_PROJECT_DIR"
else
  ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
fi
cd "$ROOT" 2>/dev/null || exit 0

RECIBO="production/evidencia/prova.ok"

# mtime em segundos, GNU e BSD
mtime() { stat -c %Y "$1" 2>/dev/null || stat -f %m "$1" 2>/dev/null; }

# Sem git não há como saber o que mudou: não bloqueia por falta de infraestrutura.
command -v git >/dev/null 2>&1 || exit 0
git rev-parse --git-dir >/dev/null 2>&1 || exit 0

# --- o que mudou e precisa de prova -----------------------------------------
# Só o que se vê ou se joga. Documentos, testes e o próprio .claude não pedem print.
# game/vendor conta: trocar a biblioteca que desenha o jogo (three.js) é a mudança que mais
# precisa de prova visual, e a primeira versão deste hook não a vigiava.
MUDADOS=$(git status --porcelain -- \
  'game/src' 'game/index.html' 'game/mapa.html' 'game/assets' 'game/vendor' 2>/dev/null \
  | sed 's/^...//' | sed 's/.* -> //')
[ -z "$MUDADOS" ] && exit 0

# o mais novo entre os arquivos mudados
NOVO=0; NOVO_ARQ=""
while IFS= read -r f; do
  [ -n "$f" ] && [ -f "$f" ] || continue
  m=$(mtime "$f"); [ -n "$m" ] || continue
  if [ "$m" -gt "$NOVO" ]; then NOVO="$m"; NOVO_ARQ="$f"; fi
done <<EOF
$MUDADOS
EOF
[ "$NOVO" -gt 0 ] || exit 0

QUANTOS=$(printf '%s\n' "$MUDADOS" | grep -c .)

bloqueia() {
  cat >&2 <<MSG
GATE 1 — evidência pendente. $QUANTOS arquivo(s) do jogo mudaram e $1.

Rode antes de encerrar:

    bash game/tests/provar.sh

Isso roda os três smoke tests, abre o jogo em desktop 960x540 e num iPhone com
safe-area e botões de toque, salva os prints em production/evidencia/ e escreve o
recibo. Se game.js mudou, roda também a regra dos 70% do metricas.js.

Alguma etapa falhando é bug a consertar, não teste a desligar. O arquivo mais
recente sem prova: $NOVO_ARQ

(CLAUDE.md, "Evidência antes de pronto". Para pular de propósito numa mudança que
não se vê na tela, apague o bloco gate-evidencia do .claude/settings.json.)
MSG
  exit 2
}

[ -f "$RECIBO" ] || bloqueia "nunca houve prova nesta árvore"
REC=$(mtime "$RECIBO"); [ -n "$REC" ] || bloqueia "o recibo não pôde ser lido"
[ "$REC" -ge "$NOVO" ] || bloqueia "a última prova é anterior a eles"

# os dois prints obrigatórios têm de existir de fato
for p in desktop iphone; do
  [ -f "production/evidencia/$p.png" ] || bloqueia "falta o print de $p"
done
exit 0
