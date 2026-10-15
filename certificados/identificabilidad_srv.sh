#!/bin/bash
# Perfiles del modelo reducido en el servidor: cada problema en paralelo; dentro de cada uno, los
# puntos del perfil en paralelo (xargs) y, para los de simulación lenta, el Jacobiano de cada
# ajuste repartido entre varios procesos.  Uso: nohup bash identificabilidad_srv.sh > srv.log 2>&1 &
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONUNBUFFERED=1

uno() {   # uno PROBLEMA NPROC_MIN NPROC_PUNTO PARALELOS
  local n=$1 nm=$2 np=$3 par=$4
  mkdir -p resultados/identificabilidad/perfil/$n
  [ -f resultados/identificabilidad/perfil/$n/minimo.npz ] || python3 identificabilidad_srv.py min $n $nm
  for ronda in 0 1 2 3; do
    python3 identificabilidad_srv.py tareas $n | \
      xargs -P $par -L1 sh -c "python3 identificabilidad_srv.py punto \$0 \$1 \$2 \$3 $np"
    if [ $ronda -lt 3 ] && [ -n "$(python3 identificabilidad_srv.py mejora $n)" ]; then
      echo "{\"reajuste\": \"$n\", \"ronda\": $((ronda+1))}"
      python3 identificabilidad_srv.py reajusta $n $nm
    else
      break
    fi
  done
  python3 identificabilidad_srv.py clasifica $n
  echo "{\"terminado\": \"$n\"}"
}

uno Chen_MSB2009             5  4 40 &
uno Lang_PLOSComputBiol2024  18 1 20 &
uno Bachmann_MSB2011         32 1 20 &
uno Raimundez_PCB2020        32 1 20 &
uno Smith_BMCSystBiol2013    11 1 20 &
uno Isensee_JCB2018          13 1 20 &
wait
echo "Done"
