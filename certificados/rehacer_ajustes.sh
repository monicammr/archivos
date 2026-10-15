#!/bin/bash
# Rehace las 15 variantes de ajustes del método (Supplementary Note on the method settings) para los
# problemas indicados, con el código corregido de los escenarios. Copia antes los resultados
# anteriores a resultados/_antes_negfix/<carpeta>/.
# Uso: bash rehacer_ajustes.sh Problema [...]
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8
run() {   # run TAG VAR=VAL ...
  tag=$1; shift
  d=resultados/reclasificacion_salidas_bio_poda_$tag
  mkdir -p resultados/_antes_negfix/reclasificacion_salidas_bio_poda_$tag
  for p in "${PROBS[@]}"; do cp $d/$p.json resultados/_antes_negfix/reclasificacion_salidas_bio_poda_$tag/ 2>/dev/null; done
  env RECL_TAG=$tag "$@" python stage_reclass.py --v3 --salidas --biologicos --poda "${PROBS[@]}" > /dev/null 2>&1
  echo "$tag hecho"
}
PROBS=("$@")
run delta0001 RECL_DELTA=0.001
run delta005  RECL_DELTA=0.05
run tolfina   PO_RTOL=1e-9 PO_ATOL=1e-12
run tolgruesa PO_RTOL=1e-6 PO_ATOL=1e-8
run nivel001  RECL_NIVEL=0.01
run nivel010  RECL_NIVEL=0.10
run rvar080   RECL_RVAR=0.80
run rvar085   RECL_RVAR=0.85
run rvar095   RECL_RVAR=0.95
run kv5       RECL_KV=5
run kv30      RECL_KV=30
run emax010   RECL_EMAX=0.10
run emax020   RECL_EMAX=0.20
run emax030   RECL_EMAX=0.30
run emax050   RECL_EMAX=0.50
