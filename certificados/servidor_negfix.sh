#!/bin/bash
# Recalcula en el servidor todo lo que cambia tras corregir el recorte max(θ₀(1+εu), 1e-12) de los
# escenarios en Lang y Raimundez (y el parámetro único de Armistead, que quedó pendiente).
#  - Lang deja de ser admisible: sus resultados posteriores a la selección se mueven a
#    resultados/_antes_negfix/ (los scripts ya omiten los problemas no admisibles).
#  - Raimundez cambia de subconjunto: se rehacen todos sus análisis; la identificabilidad con
#    identificabilidad_srv.py, como en la ronda del servidor del 2026-10-14.
#  - Las 15 variantes de ajustes del método, para los dos problemas, en paralelo.
# Uso: nohup bash servidor_negfix.sh > /root/negfix.log 2>&1 &
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONUNBUFFERED=1
R=resultados; B=$R/_antes_negfix
L=Lang_PLOSComputBiol2024; RA=Raimundez_PCB2020; AR=Armistead_CellDeathDis2024
log() { echo "[$(date +%H:%M:%S)] $*"; }

# 1. Selecciones nuevas (calculadas con RECL_TAG=negfix_srv)
while pgrep -f "stage_reclass.py.*$RA" > /dev/null; do sleep 20; done
mkdir -p $R/reclasificacion_salidas_bio_poda_antes_negfix
for P in $L $RA; do
  cp -n $R/reclasificacion_salidas_bio_poda/$P.json $R/reclasificacion_salidas_bio_poda_antes_negfix/
  cp $R/reclasificacion_salidas_bio_poda_negfix_srv/$P.json $R/reclasificacion_salidas_bio_poda/$P.json
done
log "selecciones actualizadas"

# 2. Lang: guardar y retirar los resultados que dependían del subconjunto anterior
for d in patrones validacion_externa_bio validacion_anidada sintetico_semillas control_admis_sint \
         control_admis_sint_nivel020 comparacion_brun control_morris_brun control_aleatorio control_vacio \
         control_perfil identificabilidad/local identificabilidad/perfil un_parametro un_parametro_final; do
  mkdir -p $B/$d
  for f in $R/$d/${L}*; do [ -e "$f" ] && cp -rn "$f" $B/$d/ && rm -rf "$f"; done
done
log "Lang: resultados anteriores movidos a $B"

# 3. Variantes de ajustes (15 x 2 problemas) en paralelo
variante() {   # variante TAG PROBLEMA VAR=VAL ...
  tag=$1; P=$2; shift 2
  d=$R/reclasificacion_salidas_bio_poda_$tag
  mkdir -p $B/reclasificacion_salidas_bio_poda_$tag
  cp -n $d/$P.json $B/reclasificacion_salidas_bio_poda_$tag/ 2>/dev/null
  env RECL_TAG=$tag "$@" python3 stage_reclass.py --v3 --salidas --biologicos --poda $P > /dev/null 2>&1
  echo "[$(date +%H:%M:%S)] ajuste $tag $P hecho"
}
export -f variante; export R B
(
for P in $L $RA; do
  echo "delta0001 $P RECL_DELTA=0.001"; echo "delta005 $P RECL_DELTA=0.05"
  echo "tolfina $P PO_RTOL=1e-9 PO_ATOL=1e-12"; echo "tolgruesa $P PO_RTOL=1e-6 PO_ATOL=1e-8"
  echo "nivel001 $P RECL_NIVEL=0.01"; echo "nivel010 $P RECL_NIVEL=0.10"
  echo "rvar080 $P RECL_RVAR=0.80"; echo "rvar085 $P RECL_RVAR=0.85"; echo "rvar095 $P RECL_RVAR=0.95"
  echo "kv5 $P RECL_KV=5"; echo "kv30 $P RECL_KV=30"
  echo "emax010 $P RECL_EMAX=0.10"; echo "emax020 $P RECL_EMAX=0.20"
  echo "emax030 $P RECL_EMAX=0.30"; echo "emax050 $P RECL_EMAX=0.50"
done | xargs -P 30 -L1 bash -c 'variante "$@"' _
log "ajustes terminados"
) &

# 4. Raimundez: identificabilidad (perfiles en el servidor) en paralelo con el resto
(
for d in identificabilidad/local identificabilidad/perfil; do mkdir -p $B/$d; cp -rn $R/$d/${RA}* $B/$d/ 2>/dev/null; done
rm -rf $R/identificabilidad/perfil/$RA $R/identificabilidad/perfil/$RA.json $R/identificabilidad/local/$RA.json
NPROC=8 python3 identificabilidad_local.py $RA
n=$RA; mkdir -p $R/identificabilidad/perfil/$n
python3 identificabilidad_srv.py min $n 32
for ronda in 0 1 2 3; do
  python3 identificabilidad_srv.py tareas $n | xargs -P 20 -L1 sh -c "python3 identificabilidad_srv.py punto \$0 \$1 \$2 \$3 1"
  if [ $ronda -lt 3 ] && [ -n "$(python3 identificabilidad_srv.py mejora $n)" ]; then
    log "reajuste $n ronda $((ronda+1))"; python3 identificabilidad_srv.py reajusta $n 32
  else break; fi
done
python3 identificabilidad_srv.py clasifica $n
log "identificabilidad $RA terminada"
) &

# 5. Raimundez: resto de análisis (como rehacer_problema.sh, sin la identificabilidad)
(
P=$RA; N=48
for d in patrones validacion_externa_bio validacion_anidada sintetico_semillas control_admis_sint \
         control_admis_sint_nivel020 comparacion_brun control_morris_brun control_aleatorio control_vacio control_perfil; do
  mkdir -p $B/$d; cp -rn $R/$d/${P}* $B/$d/ 2>/dev/null
done
log "$P robustez";            python3 patrones.py $P
log "$P validación externa";  NPROC=$N python3 validacion_externa.py --bio $P
log "$P validación anidada";  NPROC=$N python3 validacion_anidada_par.py $P
log "$P sintético 20 semillas"; rm -rf $R/sintetico_semillas/$P; NPROC=$N python3 sintetico_semillas.py $P
log "$P admisibilidad ±5 %";  rm -f $R/control_admis_sint/${P}__*; NPROC=$N python3 control_admis_sint.py $P
log "$P sintético de los criterios"; SOLO_SINT=1 SINT_SEMILLAS=47,48,49,50,51,52,53,54,55,56,57,58,59,60,61 NPROC=$N python3 control_admis_sint.py $P
log "$P admisibilidad ±20 %"; rm -f $R/control_admis_sint_nivel020/${P}__*; ADM_NIVEL=0.20 NPROC=$N python3 control_admis_sint.py $P
log "$P QR";                  NPROC=$N python3 comparacion_brun.py $P
log "$P Brun y Morris";       NPROC=$N python3 control_morris_brun.py $P
log "$P aleatorios";          NPROC=$N python3 control_aleatorio.py $P
log "$P sólo calibración";    NPROC=$N python3 control_vacio.py $P
log "$P perfilada (fase 3)";  NPROC=$N python3 control_perfil.py $P
log "$P análisis terminados"
) &

# 6. Armistead: parámetro único (lo que quedó pendiente)
(
for d in un_parametro un_parametro_final; do mkdir -p $B/$d; cp -n $R/$d/${AR}* $B/$d/ 2>/dev/null; done
NPROC=8 python3 un_parametro.py $AR; NPROC=8 python3 un_parametro_final.py $AR
log "Armistead parámetro único terminado"
) &

wait
log "TODO TERMINADO"
