#!/usr/bin/env bash
# provar.sh — atalho para `node game/tests/provar.js`.
#
# A prova viveu aqui até 28/11/2026, em bash, e não rodava no Windows: chamava python3 (que lá é
# python ou py) e usava /dev/tcp, que o Git Bash não suporta. Agora ela é Node, que os testes já
# exigem, e roda igual nos três sistemas. Este arquivo fica só para não quebrar quem decorou o
# comando ou para os documentos que o citam.
exec node "$(dirname "$0")/provar.js" "$@"
