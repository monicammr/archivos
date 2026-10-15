#!/bin/bash
# Sube a GitHub cada 15 minutos el avance de los cálculos de salidas medidas
# (caché parcial de J, barrido, e_rel/e_ajuste y JSON terminados), para no perderlo si el
# servidor se reinicia. Uso: nohup bash certificados/sync_avance.sh > /dev/null 2>&1 &
cd "$(dirname "$0")/.."
RAMA=claude/ode-variable-reduction-papers-tv9zdf
while true; do
  git add -A certificados/resultados/cache certificados/resultados/reclasificacion_salidas \
      certificados/resultados/salidas 2>/dev/null
  if ! git diff --cached --quiet; then
    git commit -qm "Avance automático de cálculos (salidas medidas, sistemas grandes)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01CGtKFF44maRu7hoajRT9Sw"
    for i in 1 2 3 4; do git push -q -u origin $RAMA && break; sleep $((2**i)); done
  fi
  sleep 900
done
