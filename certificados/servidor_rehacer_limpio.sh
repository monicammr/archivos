#!/bin/bash
# Rehace, desde cero, los análisis de Armistead y Raimundez que dependen del subconjunto seleccionado.
# Varios scripts reanudan desde puntos de control que sólo comprueban el tamaño del subconjunto
# (validación externa y anidada, QR, aleatorios, sólo calibración) o se saltan los resultados ya
# existentes; por eso antes de cada problema se guardan en resultados/_antes_negfix/ (sin
# sobrescribir copias previas) y se BORRAN sus resultados y puntos de control.
# Uso: nohup bash servidor_rehacer_limpio.sh PID_CASCADA > /root/rehacer_limpio.log 2>&1 &
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONUNBUFFERED=1
R=resultados; B=$R/_antes_negfix
log() { echo "[$(date +%H:%M:%S)] $*"; }
mata() { for c in $(pgrep -P $1); do mata $c; done; kill $1 2>/dev/null; }
[ -n "$1" ] && mata $1 && log "cascada anterior detenida ($1)"

limpia() {   # limpia PROBLEMA
  local P=$1
  for d in validacion_externa_bio validacion_anidada comparacion_brun control_aleatorio control_vacio \
           control_morris_brun un_parametro_final; do
    for f in $R/$d/${P}* $R/$d/checkpoints/${P}*; do
      [ -e "$f" ] || continue
      rel=${f#$R/}; mkdir -p "$B/$(dirname $rel)"
      cp -r --update=none "$f" "$B/$(dirname $rel)/" && rm -rf "$f"
    done
  done
  mkdir -p $B/control_perfil; cp --update=none $R/control_perfil/$P.json $B/control_perfil/ 2>/dev/null
  rm -f $R/control_perfil/$P.json      # resumen; los puntos del perfil del modelo completo no dependen de S
  log "$P limpio"
}

rehace() {   # rehace PROBLEMA NPROC SINTETICO(0/1) ADMIS(0/1)
  local P=$1 N=$2
  limpia $P
  log "$P validación externa";  NPROC=$N python3 validacion_externa.py --bio $P
  log "$P validación anidada";  NPROC=$N python3 validacion_anidada_par.py $P
  if [ $3 = 1 ]; then log "$P sintético 20 semillas"; NPROC=$N python3 sintetico_semillas.py $P; fi
  if [ $4 = 1 ]; then
    log "$P admisibilidad ±5 %";  rm -f $R/control_admis_sint/${P}__*; NPROC=$N python3 control_admis_sint.py $P
    log "$P sintético de los criterios"; SOLO_SINT=1 SINT_SEMILLAS=47,48,49,50,51,52,53,54,55,56,57,58,59,60,61 NPROC=$N python3 control_admis_sint.py $P
    log "$P admisibilidad ±20 %"; rm -f $R/control_admis_sint_nivel020/${P}__*; ADM_NIVEL=0.20 NPROC=$N python3 control_admis_sint.py $P
  fi
  log "$P QR";                  NPROC=$N python3 comparacion_brun.py $P
  log "$P Brun y Morris";       NPROC=$N python3 control_morris_brun.py $P
  log "$P aleatorios";          NPROC=$N python3 control_aleatorio.py $P
  log "$P sólo calibración";    NPROC=$N python3 control_vacio.py $P
  log "$P perfilada (fase 3)";  NPROC=$N python3 control_perfil.py $P
  log "$P TERMINADO"
}

rehace Armistead_CellDeathDis2024 8 0 0 &
rehace Raimundez_PCB2020 40 1 1 &
wait
log "Armistead parámetro único"; NPROC=8 python3 un_parametro_final.py Armistead_CellDeathDis2024
log "TODO TERMINADO"
