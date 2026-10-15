#!/bin/bash
# Verosimilitud perfilada en los dos problemas admisibles con más de 60 parámetros libres que son
# baratos de simular: Lucarelli (72 libres, 720 puntos de perfil) y Bachmann (90 libres, 27
# biológicos, 270 puntos). Hasta ahora no se habían perfilado por el límite PL_PMAX=60
# (control_perfil.py); aquí se sube a 200 para medir si la perfilada es factible y cuánto cuesta.
# Después, con el subconjunto que elige la perfilada, se rehacen las pruebas de los criterios
# (admisibilidad ±5 % y ±20 % y sintético con 20 semillas), como en servidor_raimundez.sh.
#
# Cada problema tiene un tope de tiempo (TOPE, por defecto 24 h). Si se agota, el problema queda
# sin terminar: eso es el resultado "no factible con este presupuesto", y los puntos ya calculados
# se conservan (al relanzar se reutilizan).
#
# Uso (en el servidor, dentro de archivos/certificados):
#   bash servidor_perfil_grandes.sh instala       # venv con las mismas versiones que antes
#   nohup bash servidor_perfil_grandes.sh corre > /root/perfil_grandes.log 2>&1 &
#   bash servidor_perfil_grandes.sh estado        # avance
#   bash servidor_perfil_grandes.sh empaqueta     # resultados para traer a la laptop
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONUNBUFFERED=1
PY=${PY:-/root/venv/bin/python}
NPROC=${NPROC:-$(( $(nproc) - 4 ))}
TOPE=${TOPE:-24h}
PROBLEMAS=${PROBLEMAS:-"Lucarelli_CellSystems2018 Bachmann_MSB2011"}
R=resultados; B=$R/_antes_perfil_grandes; LOGD=$R/logs_perfil_grandes
log() { echo "[$(date -u +%F' '%T)] $*" | tee -a $LOGD/avance.txt; }

case "$1" in
instala)
  python3 -m venv /root/venv || { apt-get update -qq && apt-get install -y -qq python3-venv && python3 -m venv /root/venv; }
  /root/venv/bin/pip install -q --upgrade pip
  /root/venv/bin/pip install -q numpy==2.4.6 scipy==1.17.1 pandas==3.0.6 sympy==1.14.0 \
    libroadrunner==2.10.0 python-libsbml==5.21.2 petab
  $PY -c "import roadrunner,scipy,numpy;print('roadrunner',roadrunner.__version__,'scipy',scipy.__version__,'numpy',numpy.__version__)"
  $PY -c "import control_perfil as C
for n in '$PROBLEMAS'.split():
    d=C.preparar(n); print(n,'libres',len(d['libres']),'bio',len(d['bio']))"
  ;;

corre)
  mkdir -p $LOGD
  log "inicio: $PROBLEMAS, NPROC=$NPROC, TOPE=$TOPE, $(nproc) núcleos, $(free -g | awk '/Mem:/{print $2}') GB"
  for P in $PROBLEMAS; do
    # copia de lo anterior (los JSON "no_evaluable" y los resultados "sin subconjunto" de los criterios)
    for d in control_perfil control_admis_sint control_admis_sint_nivel020; do
      mkdir -p $B/$d; cp -r --update=none $R/$d/${P}* $B/$d/ 2>/dev/null
    done
    rm -f $R/control_perfil/$P.json
    log "$P perfilada (PL_PMAX=200)"
    t0=$(date +%s)
    PL_PMAX=200 NPROC=$NPROC timeout --kill-after=120 $TOPE $PY -u control_perfil.py $P >> $LOGD/perfil_$P.log 2>&1
    st=$?
    pkill -f "control_perfil.py $P" 2>/dev/null      # hijos del Pool que sobrevivan al tope
    log "$P perfilada: código $st, $(( $(date +%s) - t0 )) s de reloj"
    if [ $st -eq 124 ]; then
      log "$P: tope de $TOPE agotado, perfilada no terminada"
      echo "{\"sistema\": \"$P\", \"no_evaluable\": \"perfilada no terminada en $TOPE con $NPROC núcleos\", \"segundos\": $(( $(date +%s) - t0 ))}" > $R/control_perfil/$P.json
      continue
    fi
    grep -q '"S_perfil"' $R/control_perfil/$P.json || { log "$P: sin S_perfil, no se hacen las pruebas"; continue; }
    # pruebas de los criterios con el subconjunto de la perfilada (los demás métodos se reutilizan)
    rm -f $R/control_admis_sint/${P}__perfil__* $R/control_admis_sint_nivel020/${P}__perfil__*
    log "$P criterios: admisibilidad ±5 % y sintético 42-46"
    NPROC=$NPROC $PY -u control_admis_sint.py $P >> $LOGD/criterios_$P.log 2>&1
    log "$P criterios: sintético 47-61"
    SOLO_SINT=1 SINT_SEMILLAS=47,48,49,50,51,52,53,54,55,56,57,58,59,60,61 NPROC=$NPROC \
      $PY -u control_admis_sint.py $P >> $LOGD/criterios_$P.log 2>&1
    log "$P criterios: admisibilidad ±20 %"
    ADM_NIVEL=0.20 NPROC=$NPROC $PY -u control_admis_sint.py $P >> $LOGD/criterios_$P.log 2>&1
    log "$P terminado"
  done
  log "TODO TERMINADO"
  ;;

estado)
  tail -n 20 $LOGD/avance.txt
  for P in $PROBLEMAS; do
    n=$(ls $R/control_perfil/$P/perfil_*.json 2>/dev/null | wc -l)
    echo "$P: $n puntos de perfil calculados"
  done
  free -g | awk '/Mem:/{print "memoria usada", $3, "de", $2, "GB"}'; echo "procesos python: $(pgrep -c python)"
  ;;

empaqueta)
  f=/root/perfil_grandes_$(date -u +%F).tar.gz
  tar czf $f $LOGD $(for P in $PROBLEMAS; do echo $R/control_perfil/$P.json $R/control_perfil/$P; \
    ls $R/control_admis_sint/${P}__perfil__* $R/control_admis_sint_nivel020/${P}__perfil__* 2>/dev/null; done)
  ls -la $f
  ;;

*) echo "uso: bash $0 instala|corre|estado|empaqueta"; exit 1 ;;
esac
