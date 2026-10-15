#!/bin/bash
# Segunda parte de servidor_negfix.sh (Raimundez), relanzada tras detener los análisis que habían
# arrancado con la selección anterior: espera al ARCHIVO de la selección nueva, lo promueve, borra
# los puntos de control de robustez e identificabilidad de Raimundez y rehace sus análisis.
# Después lanza B5 (robustez con direcciones independientes por nivel) y C3 (señal del sintético y
# otras amplitudes) para todos los problemas admisibles.
# Uso: nohup bash servidor_raimundez.sh > /root/raimundez.log 2>&1 &
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONUNBUFFERED=1
R=resultados; B=$R/_antes_negfix; RA=Raimundez_PCB2020
log() { echo "[$(date +%H:%M:%S)] $*"; }
NUEVA=$R/reclasificacion_salidas_bio_poda_negfix_srv/$RA.json
until [ -s $NUEVA ]; do sleep 20; done
sleep 5
cp $NUEVA $R/reclasificacion_salidas_bio_poda/$RA.json
log "selección de $RA actualizada: $(python3 -c "import json;print(json.load(open('$NUEVA'))['S'])")"
rm -rf $R/patrones/parcial/$RA.json $R/patrones/$RA.json

# 4. Raimundez: identificabilidad (perfiles en el servidor) en paralelo con el resto
(
for d in identificabilidad/local identificabilidad/perfil; do mkdir -p $B/$d; cp -r --update=none $R/$d/${RA}* $B/$d/ 2>/dev/null; done
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
  mkdir -p $B/$d; cp -r --update=none $R/$d/${P}* $B/$d/ 2>/dev/null
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


wait
log "Raimundez terminado"

# B5: robustez con direcciones independientes por nivel (todos los admisibles)
log "B5 inicio"; PATRONES_INDEP=1 PATRONES_OUT=patrones_indep NPROC=40 python3 patrones.py; log "B5 fin"
# C3: señal y(θ*) − y(θ₀) del sintético del artículo (a = 0,20) y otras amplitudes (10 semillas)
log "C3 señal"; SINT_SOLO_SENAL=1 SINT_SEEDS=42-61 NPROC=60 python3 sintetico_semillas.py
for a in 0.05 0.50; do
  SINT_SOLO_SENAL=1 SINT_AMPLITUD=$a SINT_SEEDS=42-51 NPROC=60 python3 sintetico_semillas.py
  log "C3 amplitud $a"; SINT_AMPLITUD=$a SINT_SEEDS=42-51 NPROC=60 python3 sintetico_semillas.py
done
log "TODO TERMINADO"
