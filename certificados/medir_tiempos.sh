#!/bin/bash
# Mide el tiempo de reloj del método completo (selección + admisibilidad + poda), desde cero
# (sin caché), en dos configuraciones, sin tocar los resultados del artículo:
#   1. paralelo : un sistema cada vez, J y barrido de la etapa 2 repartidos en NPROC núcleos
#                 (RECL_PARALELO=1) → resultados/reclasificacion_salidas_bio_poda_tiempopar/
#   2. serie    : un núcleo por sistema (todos los sistemas a la vez, cada uno en su proceso)
#                 → resultados/reclasificacion_salidas_bio_poda_tiemposerie/
# Los 8 sistemas que en el artículo usan e_ajuste de primer orden se corren igual
# (RECL_AJUSTE_LINEAL=1). El tiempo de cada sistema queda en el campo "segundos" de su JSON.
# Espera a que no haya otro cálculo pesado corriendo (control_perfil.py).
cd "$(dirname "$0")"
PY=${PY:-/root/venv/bin/python}
NPROC=${NPROC:-120}
LOG=${LOG:-/tmp/medir_tiempos}
mkdir -p "$LOG"
LINEAL="Alkan_SciSignal2018 Bachmann_MSB2011 Beer_MolBioSystems2014 Chen_MSB2009 Isensee_JCB2018 Lang_PLOSComputBiol2024 Lucarelli_CellSystems2018 Raimundez_PCB2020"
TODOS=$(ls resultados/reclasificacion_salidas_bio_poda/*.json | xargs -n1 basename | sed 's/.json//')

while pgrep -f "[c]ontrol_perfil.py" > /dev/null; do sleep 60; done
echo "inicio $(date -u)" > "$LOG/estado.txt"

es_lineal() { case " $LINEAL " in *" $1 "*) return 0;; esac; return 1; }

# 1. paralelo, un sistema cada vez
rm -rf resultados/cache
for s in $TODOS; do
  extra=""; es_lineal "$s" && extra="RECL_AJUSTE_LINEAL=1"
  env $extra RECL_TAG=tiempopar RECL_PARALELO=1 NPROC=$NPROC \
    $PY -u stage_reclass.py --v3 --salidas --poda --biologicos "$s" >> "$LOG/paralelo.log" 2>&1
  echo "paralelo $s $(date -u)" >> "$LOG/estado.txt"
done

# 2. serie: todos a la vez, un núcleo cada uno (sin caché: se borra la del paso 1).
#    Chen se excluye (35 s por simulación: unas 4–5 h en un núcleo); su tiempo es el del paso 1.
rm -rf resultados/cache
for s in $TODOS; do
  [ "$s" = "Chen_MSB2009" ] && continue
  extra=""; es_lineal "$s" && extra="RECL_AJUSTE_LINEAL=1"
  ( env $extra RECL_TAG=tiemposerie NPROC=1 \
      $PY -u stage_reclass.py --v3 --salidas --poda --biologicos "$s" > "$LOG/serie_$s.log" 2>&1
    echo "serie $s $(date -u)" >> "$LOG/estado.txt" ) &
done
wait
echo "FIN $(date -u)" >> "$LOG/estado.txt"
