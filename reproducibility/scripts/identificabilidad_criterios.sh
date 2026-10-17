#!/usr/bin/env bash
# Identifiability of the parameters selected by the other criteria (Brun, Morris, standard pivoted
# QR, profile likelihood), with exactly the same profile-likelihood procedure as for our subsets
# (reduced problem: selected + calibration parameters free, the others at theta0; all data).
# Only the problems whose subset differs from ours are profiled; the others reuse our profiles.
# Resumable: points already computed are not recomputed.
#
# Usage (on the server, from the folder reproducibility/):
#   NPROC=80 nohup bash scripts/identificabilidad_criterios.sh > identif_criterios.log 2>&1 &
#   tail -f identif_criterios.log            # progress
set -uo pipefail
cd "$(dirname "$0")/../analysis"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
N=${NPROC:-30}
LOG=../results/logs_criterios
mkdir -p "$LOG"
echo "$(date) start, $N processes"

python prepare_criteria_subsets.py

for c in brun morris qr_gks perfil; do
  echo "$(date) profiles of $c"
  ID_SUBSETS=subsets_$c ID_SOLO_CAMBIADOS=1 NPROC=$N python identifiability_profiles.py > "$LOG/profiles_$c.log" 2>&1
  ID_SUBSETS=subsets_$c CERT_OUT=certificado_$c.csv NPROC=$N python identifiability_conditions.py >> "$LOG/profiles_$c.log" 2>&1
  echo "$(date) $c done"
done

python compare_identifiability_criteria.py | tee "$LOG/comparison.txt"
echo "$(date) all done" > "$LOG/DONE"
