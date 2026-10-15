#!/bin/bash
# Rehace todos los análisis que dependen de los escenarios aleatorios o del subconjunto seleccionado
# de un problema, tras corregir el recorte max(θ₀(1+εu), 1e-12) de los escenarios (parámetros con
# valor nominal negativo o menor que 1e-12: Armistead, Raimundez, Lang).
# Antes de rehacer, copia los resultados anteriores del problema a resultados/_antes_negfix/.
# Uso: bash rehacer_problema.sh Problema [NPROC]
set -u
P=$1; N=${2:-4}
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
R=resultados; B=$R/_antes_negfix; mkdir -p $B
for d in patrones validacion_externa_bio validacion_anidada sintetico_semillas control_admis_sint \
         control_admis_sint_nivel020 comparacion_brun control_morris_brun control_aleatorio control_vacio \
         control_perfil identificabilidad/local identificabilidad/perfil; do
  mkdir -p $B/$d
  cp -r $R/$d/${P}* $B/$d/ 2>/dev/null
done
log() { echo "[$(date +%H:%M:%S)] $*"; }
log "robustez";            python patrones.py $P
log "validación externa";  NPROC=$N python validacion_externa.py --bio $P
log "validación anidada";  NPROC=$N python validacion_anidada_par.py $P
log "sintético 20 semillas"; rm -rf $R/sintetico_semillas/$P; NPROC=$N python sintetico_semillas.py $P
log "admisibilidad ±5 %";  rm -f $R/control_admis_sint/${P}__*; NPROC=$N python control_admis_sint.py $P
log "sintético de los criterios (semillas 47-61)"; SOLO_SINT=1 SINT_SEMILLAS=47,48,49,50,51,52,53,54,55,56,57,58,59,60,61 NPROC=$N python control_admis_sint.py $P
log "admisibilidad ±20 %"; rm -f $R/control_admis_sint_nivel020/${P}__*; ADM_NIVEL=0.20 NPROC=$N python control_admis_sint.py $P
log "QR";                  NPROC=$N python comparacion_brun.py $P
log "Brun y Morris";       NPROC=$N python control_morris_brun.py $P
log "aleatorios";          NPROC=$N python control_aleatorio.py $P
log "sólo calibración";    NPROC=$N python control_vacio.py $P
log "perfilada (fase 3)";  NPROC=$N python control_perfil.py $P
log "identificabilidad";   rm -rf $R/identificabilidad/perfil/$P $R/identificabilidad/perfil/$P.json $R/identificabilidad/local/$P.json
NPROC=$N python identificabilidad_local.py $P
NPROC=$N python identificabilidad_perfil.py $P
log "fin $P"
