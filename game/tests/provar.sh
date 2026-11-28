#!/usr/bin/env bash
# provar.sh — roda a prova completa do Timtim e deixa o recibo que o Gate 1 confere.
#
# Os três smoke tests mais a evidência nos dois viewports obrigatórios. Em caso de sucesso
# escreve production/evidencia/prova.ok; o hook .claude/hooks/gate-evidencia.sh só olha se esse
# recibo é mais novo que o último arquivo do jogo que você mexeu — ele não roda nada, por isso é
# barato o bastante para o evento Stop, que dispara a cada resposta.
#
# Uso: bash game/tests/provar.sh
set -u
cd "$(dirname "$0")/../.." || exit 2
OUT=production/evidencia
mkdir -p "$OUT"
rm -f "$OUT/prova.ok"

# Os smoke tests esperam a pasta game/ servida na 8765 (é o que os comentários deles dizem).
# Sobe um servidor só para esta prova e o derruba na saída, para a prova não depender de um
# servidor que alguém tenha de lembrar de abrir.
PORTA=8765
SERV=""
if command -v python3 >/dev/null 2>&1; then
  (cd game && exec python3 -m http.server "$PORTA" >/dev/null 2>&1) &
  SERV=$!
  trap 'if [ -n "$SERV" ]; then kill "$SERV" 2>/dev/null; fi' EXIT INT TERM
  # espera a porta responder, não um tempo fixo
  pronto=0
  for _ in $(seq 1 50); do
    if (exec 3<>/dev/tcp/127.0.0.1/"$PORTA") 2>/dev/null; then pronto=1; exec 3>&- 2>/dev/null; break; fi
    sleep 0.2
  done
  [ "$pronto" = 1 ] || { echo "o servidor local na porta $PORTA não subiu — prova abortada"; exit 2; }
else
  echo "python3 não encontrado: os smoke tests precisam da pasta game/ servida na porta $PORTA"
  exit 2
fi

falhas=0
for t in smoke smoke-arraial smoke-quadro; do
  printf '\n=== %s ===\n' "$t"
  if ! node "game/tests/$t.js"; then falhas=$((falhas + 1)); fi
done

printf '\n=== evidência (desktop + iphone) ===\n'
if ! node game/tests/evidencia.js "$OUT"; then falhas=$((falhas + 1)); fi

# metricas.js só quando o pulo ou o desenho de uma fase mudou: é a regra dos 70% do
# docs/ritmo-das-fases.md, e é lenta demais para rodar em toda prova.
if git diff --quiet HEAD -- game/src/game.js 2>/dev/null; then :; else
  printf '\n=== métricas (game.js mudou: regra dos 70%%) ===\n'
  if ! node game/tests/metricas.js; then falhas=$((falhas + 1)); fi
fi

if [ "$falhas" -gt 0 ]; then
  printf '\n%s etapa(s) falharam — nenhum recibo escrito.\n' "$falhas"
  exit 1
fi
date -u +"%Y-%m-%dT%H:%M:%SZ" > "$OUT/prova.ok"
printf '\nProva completa. Recibo: %s\n' "$OUT/prova.ok"
