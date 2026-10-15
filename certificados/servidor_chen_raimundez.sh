#!/bin/bash
# Completa la comparación de criterios en los dos problemas que faltaban:
#   * Chen (155 parámetros libres, ~35 s por simulación): selecciones de QR pivotado, Brun y Morris
#     con chen_criterios.py (mismas funciones, simulaciones en paralelo), su validación externa y
#     la prueba de admisibilidad a ±5 % y ±20 % de los cinco criterios. Sin experimento sintético:
#     Chen no tiene subconjunto de la perfilada, así que no entraría en los casos comunes.
#   * Raimundez (126 parámetros libres): verosimilitud perfilada del modelo completo (PL_PMAX=200)
#     y, con su subconjunto, las pruebas de los criterios (admisibilidad ±5 % y ±20 %, sintético con
#     20 semillas), como servidor_perfil_grandes.sh hizo para Bachmann y Lucarelli.
# Los dos problemas corren a la vez: Chen con NUC_CHEN núcleos, Raimundez con el resto.
#
# Uso (en el servidor, dentro de archivos/certificados):
#   bash servidor_chen_raimundez.sh instala
#   nohup bash servidor_chen_raimundez.sh corre > /root/chen_raimundez.log 2>&1 &
#   bash servidor_chen_raimundez.sh estado
#   bash servidor_chen_raimundez.sh empaqueta
cd "$(dirname "$0")"
NUCLEOS=$(nproc)      # antes de fijar OMP_NUM_THREADS=1: nproc obedece esa variable
export PYTHONIOENCODING=utf-8 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONUNBUFFERED=1
PY=${PY:-/root/venv/bin/python}
NPROC=${NPROC:-$(( NUCLEOS - 4 ))}
[ "$NPROC" -ge 8 ] || { echo "NPROC=$NPROC no válido"; exit 1; }
NUC_CHEN=${NUC_CHEN:-40}
NUC_RAIM=${NUC_RAIM:-$(( NPROC - NUC_CHEN ))}
TOPE=${TOPE:-24h}
CH=Chen_MSB2009; RA=Raimundez_PCB2020
R=resultados; B=$R/_antes_chen_raimundez; LOGD=$R/logs_chen_raimundez
log() { echo "[$(date -u +%F' '%T)] $*" | tee -a $LOGD/avance.txt; }
respaldo() {   # respaldo <carpeta> <patrón>
  mkdir -p $B/$1; cp -r --update=none $R/$1/$2 $B/$1/ 2>/dev/null; true
}

case "$1" in
instala)
  python3 -m venv /root/venv || { apt-get update -qq && apt-get install -y -qq python3-venv && python3 -m venv /root/venv; }
  /root/venv/bin/pip install -q --upgrade pip
  /root/venv/bin/pip install -q numpy==2.4.6 scipy==1.17.1 pandas==3.0.6 sympy==1.14.0 \
    libroadrunner==2.10.0 python-libsbml==5.21.2 petab
  $PY -c "import roadrunner,scipy,numpy;print('roadrunner',roadrunner.__version__,'scipy',scipy.__version__,'numpy',numpy.__version__)"
  $PY -c "import control_perfil as C
d=C.preparar('$RA'); print('$RA','libres',len(d['libres']),'bio',len(d['bio']))"
  # comprobación rápida de chen_criterios con un problema pequeño (selección sin ajustes)
  CRIT_PROBLEMA=Boehm_JProteomeRes2014 CRIT_SOLO_SELECCION=1 NPROC=8 $PY chen_criterios.py | tail -2
  ;;

corre)
  mkdir -p $LOGD
  log "inicio: NPROC=$NPROC (Chen $NUC_CHEN, Raimundez $NUC_RAIM), TOPE=$TOPE, $NUCLEOS núcleos, $(free -g | awk '/Mem:/{print $2}') GB"

  chen() {
    respaldo comparacion_brun "$CH*"; respaldo control_morris_brun "$CH*"
    respaldo control_admis_sint "${CH}__*"; respaldo control_admis_sint_nivel020 "${CH}__*"
    log "$CH selección QR, Brun y Morris y validación externa ($NUC_CHEN núcleos)"
    t0=$(date +%s)
    NPROC=$NUC_CHEN timeout --kill-after=120 $TOPE $PY -u chen_criterios.py >> $LOGD/criterios_seleccion_$CH.log 2>&1
    log "$CH selección: código $?, $(( $(date +%s) - t0 )) s"
    pkill -f "chen_criterios.py" 2>/dev/null
    grep -q '"S_brun"' $R/control_morris_brun/$CH.json 2>/dev/null || { log "$CH: sin selecciones, no se hacen las pruebas"; return; }
    rm -f $R/control_admis_sint/${CH}__* $R/control_admis_sint_nivel020/${CH}__*
    log "$CH admisibilidad ±5 % (cinco criterios)"
    SOLO_ADM=1 NPROC=5 $PY -u control_admis_sint.py $CH >> $LOGD/criterios_$CH.log 2>&1
    log "$CH admisibilidad ±20 %"
    SOLO_ADM=1 ADM_NIVEL=0.20 NPROC=5 $PY -u control_admis_sint.py $CH >> $LOGD/criterios_$CH.log 2>&1
    log "$CH terminado"
  }

  raimundez() {
    respaldo control_perfil "$RA*"; respaldo control_admis_sint "${RA}__perfil__*"; respaldo control_admis_sint_nivel020 "${RA}__perfil__*"
    rm -f $R/control_perfil/$RA.json
    log "$RA perfilada (PL_PMAX=200, $NUC_RAIM núcleos)"
    t0=$(date +%s)
    PL_PMAX=200 NPROC=$NUC_RAIM timeout --kill-after=120 $TOPE $PY -u control_perfil.py $RA >> $LOGD/perfil_$RA.log 2>&1
    st=$?
    pkill -f "control_perfil.py $RA" 2>/dev/null
    log "$RA perfilada: código $st, $(( $(date +%s) - t0 )) s"
    if [ $st -eq 124 ]; then
      log "$RA: tope de $TOPE agotado, perfilada no terminada"
      echo "{\"sistema\": \"$RA\", \"no_evaluable\": \"perfilada no terminada en $TOPE con $NUC_RAIM núcleos\"}" > $R/control_perfil/$RA.json
      return
    fi
    grep -q '"S_perfil"' $R/control_perfil/$RA.json || { log "$RA: sin S_perfil, no se hacen las pruebas"; return; }
    rm -f $R/control_admis_sint/${RA}__perfil__* $R/control_admis_sint_nivel020/${RA}__perfil__*
    log "$RA criterios: admisibilidad ±5 % y sintético 42-46"
    NPROC=$NUC_RAIM $PY -u control_admis_sint.py $RA >> $LOGD/criterios_$RA.log 2>&1
    log "$RA criterios: sintético 47-61"
    SOLO_SINT=1 SINT_SEMILLAS=47,48,49,50,51,52,53,54,55,56,57,58,59,60,61 NPROC=$NUC_RAIM \
      $PY -u control_admis_sint.py $RA >> $LOGD/criterios_$RA.log 2>&1
    log "$RA criterios: admisibilidad ±20 %"
    SOLO_ADM=1 ADM_NIVEL=0.20 NPROC=$NUC_RAIM $PY -u control_admis_sint.py $RA >> $LOGD/criterios_$RA.log 2>&1
    log "$RA terminado"
  }

  chen & raimundez &
  wait
  log "TODO TERMINADO"
  ;;

estado)
  tail -n 20 $LOGD/avance.txt
  echo "$RA: $(ls $R/control_perfil/$RA/perfil_*.json 2>/dev/null | wc -l) puntos de perfil (unos 570)"
  tail -n 3 $LOGD/criterios_seleccion_$CH.log 2>/dev/null
  free -g | awk '/Mem:/{print "memoria usada", $3, "de", $2, "GB"}'; echo "procesos python: $(pgrep -c python)"
  ;;

empaqueta)
  f=/root/chen_raimundez_$(date -u +%F).tar.gz
  tar czf $f $LOGD $B $R/control_perfil/$RA.json $R/control_perfil/$RA $R/comparacion_brun/$CH.json \
    $R/control_morris_brun/$CH.json $R/criterios_tmp_$CH \
    $(ls $R/control_admis_sint/${CH}__* $R/control_admis_sint_nivel020/${CH}__* \
         $R/control_admis_sint/${RA}__perfil__* $R/control_admis_sint_nivel020/${RA}__perfil__* 2>/dev/null)
  ls -la $f
  ;;

*) echo "uso: bash $0 instala|corre|estado|empaqueta"; exit 1 ;;
esac
