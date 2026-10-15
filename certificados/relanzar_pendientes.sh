#!/bin/bash
# Relaunch the pending background analyses, skipping results already on disk.
cd /home/user/archivos/certificados
LOG=${LOG:-/tmp/relanzar}
mkdir -p "$LOG"
# 1. robustness per scenario (patrones.py skips finished problems; per-level checkpoints for the slow ones)
( PATRONES_OUT=patrones_escenarios NPROC=2 python3 patrones.py > "$LOG/patrones.log" 2>&1 ) &
# 2. setting variants with the final method, only problems not yet done
(
  P=$(ls resultados/reclasificacion_salidas_bio_poda_kv5/*.json | xargs -n1 basename | sed 's/.json//')
  for spec in "RECL_DELTA=0.001 delta0001" "RECL_DELTA=0.05 delta005" "PO_RTOL=1e-9 PO_ATOL=1e-12 tolfina" \
              "PO_RTOL=1e-6 PO_ATOL=1e-8 tolgruesa" "RECL_NIVEL=0.01 nivel001" "RECL_NIVEL=0.10 nivel010"; do
    tag=${spec##* }; envs=${spec% *}
    todo=""
    for p in $P; do [ -f "resultados/reclasificacion_salidas_bio_poda_$tag/$p.json" ] || todo="$todo $p"; done
    [ -z "$todo" ] && continue
    env $envs RECL_TAG=$tag NPROC=1 python3 stage_reclass.py --v3 --salidas --poda --biologicos $todo >> "$LOG/var_$tag.log" 2>&1
  done
) &
# 3. single-parameter subsets with the final method
(
  todo=$(python3 -c "
import json,glob,os
SLOW={'Bachmann_MSB2011','Chen_MSB2009','Isensee_JCB2018','Lang_PLOSComputBiol2024','Raimundez_PCB2020'}
print(' '.join(sorted(os.path.basename(f)[:-5] for f in glob.glob('resultados/reclasificacion_salidas_bio_poda/*.json')
  if json.load(open(f))['admisible'] and os.path.basename(f)[:-5] not in SLOW
  and not os.path.exists('resultados/un_parametro_final/'+os.path.basename(f)))))")
  [ -n "$todo" ] && NPROC=1 python3 un_parametro_final.py $todo > "$LOG/unpar.log" 2>&1
) &
wait
echo "ALL DONE"
