#!/usr/bin/env bash
# Identifiability of the parameters selected by the other criteria (Brun, Morris, standard pivoted
# QR, profile likelihood), with exactly the same profile-likelihood procedure as for our subsets
# (reduced problem: selected + calibration parameters free, the others at theta0; all data).
# Only the problems whose subset differs from ours are profiled; the others reuse our profiles.
# The four criteria run at the same time, each with NPROC/4 processes, so that the cores left idle
# by one criterion (e.g. while it waits for the initial fit of a slow problem) are used by the
# others. Resumable: points already computed are not recomputed.
#
# Usage (on the server, from the folder reproducibility/):
#   NPROC=128 nohup bash scripts/run_identifiability_other_criteria.sh > identif_criterios.log 2>&1 &
#   tail -f identif_criterios.log            # progress
set -uo pipefail
cd "$(dirname "$0")/../analysis"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
N=${NPROC:-32}
CRIT="brun morris qr_gks perfil"
PER=$(( N / 4 )); [ "$PER" -lt 1 ] && PER=1
LOG=../results/logs_other_criteria
mkdir -p "$LOG"
echo "$(date) start, $N processes ($PER per criterion, four criteria at the same time)"

python prepare_criteria_subsets.py

for c in $CRIT; do
  (echo "$(date) profiles of $c"
   ID_SUBSETS=subsets_$c ID_SOLO_CAMBIADOS=1 NPROC=$PER python identifiability_profiles.py > "$LOG/profiles_$c.log" 2>&1
   ID_SUBSETS=subsets_$c CERT_OUT=audit2/certificado_$c.csv NPROC=$PER python identifiability_conditions.py >> "$LOG/profiles_$c.log" 2>&1
   echo "$(date) $c done") &
done
wait

python compare_identifiability_criteria.py | tee "$LOG/comparison.txt"
echo "$(date) all done" > "$LOG/DONE"
