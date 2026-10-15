#!/bin/bash
# Corrige la cascada limpia de Raimundez: sin VAL_PMAX=200 (por defecto 60) su modelo completo (136
# parámetros) no se ajustó, la validación anidada no se generó y QR, aleatorios y sólo calibración
# quedaron sin chi2_ours; la admisibilidad de los otros criterios no se calculó porque sus selecciones
# se generaron después. Se conservan los puntos de control (son del subconjunto actual).
# Uso: nohup bash servidor_raimundez_fix.sh PID_REHACER_LIMPIO > /root/raimundez_fix.log 2>&1 &
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONUNBUFFERED=1
export VAL_PMAX=200
R=resultados; P=Raimundez_PCB2020; N=40
log() { echo "[$(date +%H:%M:%S)] $*"; }
mata() { for c in $(pgrep -P $1); do mata $c; done; kill $1 2>/dev/null; }
[ -n "$1" ] && mata $1 && log "ejecución anterior detenida ($1)"
sleep 3
[ -n "$1" ] || rm -f $R/validacion_externa_bio/$P.json $R/comparacion_brun/$P.json $R/control_morris_brun/$P.json \
      $R/control_aleatorio/$P.json $R/control_vacio/$P.json $R/control_perfil/$P.json
# la externa ajusta el modelo completo en un solo núcleo; la anidada reparte su Jacobiano: en paralelo
log "validación externa y anidada (en paralelo)"
NPROC=4 python3 validacion_externa.py --bio $P &
NPROC=4 JAC_NPROC=70 python3 validacion_anidada_par.py $P &
wait
log "validaciones terminadas"
log "QR";                  NPROC=$N python3 comparacion_brun.py $P
log "Brun y Morris";       NPROC=$N python3 control_morris_brun.py $P
log "aleatorios";          NPROC=$N python3 control_aleatorio.py $P
log "sólo calibración";    NPROC=$N python3 control_vacio.py $P
log "perfilada";           NPROC=$N python3 control_perfil.py $P
log "admisibilidad de los otros criterios ±5 %"; NPROC=$N python3 control_admis_sint.py $P
log "sintético de los criterios"; SOLO_SINT=1 SINT_SEMILLAS=47,48,49,50,51,52,53,54,55,56,57,58,59,60,61 NPROC=$N python3 control_admis_sint.py $P
log "admisibilidad ±20 %"; ADM_NIVEL=0.20 NPROC=$N python3 control_admis_sint.py $P
log "Armistead parámetro único"; NPROC=8 python3 un_parametro_final.py Armistead_CellDeathDis2024
log "FIX TERMINADO"
