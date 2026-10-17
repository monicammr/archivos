#!/usr/bin/env bash
# Test of the role of the calibration parameters (pre-submission audit, L6): the admissibility test
# at +-5 % is repeated with the calibration parameters kept at theta0, so that only the biological
# parameters are perturbed (the same biological perturbations as the standard test), for the 14
# problems with calibration parameters and for our subsets, our training-output subsets, the
# calibration parameters alone, the 20 random k-subsets and the subsets of Brun, Morris, profile
# likelihood and standard pivoted QR (27 subsets per problem, 378 single-core tasks).
# All tasks share one pool of NPROC processes, slowest problems first. Resumable: finished tasks
# are skipped. With CAL_20PC=1 the same test is then repeated at +-20 %.
# Usage (from reproducibility/):  NPROC=126 nohup bash scripts/run_test_calibration_fixed.sh > run_test_calibration_fixed.log 2>&1 &
set -uo pipefail
cd "$(dirname "$0")/../analysis"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
N=${NPROC:-32}
LOG=../results/logs_calibration_fixed
mkdir -p "$LOG"
METHODS="ours,train,empty,brun,morris,perfil,qr_gks"
for i in $(seq 0 19); do METHODS="$METHODS,rand$i"; done
echo "$(date) start, $N processes"
CT_CAL_FIXED=1 CT_PRUEBAS=adm CT_METODOS=$METHODS NPROC=$N python criteria_tests.py > "$LOG/calfixed_5.log" 2>&1
echo "$(date) +-5 % done"
if [ "${CAL_20PC:-0}" = "1" ]; then
  ADM_NIVEL=0.20 CT_CAL_FIXED=1 CT_PRUEBAS=adm CT_METODOS=$METHODS NPROC=$N python criteria_tests.py > "$LOG/calfixed_20.log" 2>&1
  echo "$(date) +-20 % done"
fi
python calibration_fixed_summary.py | tee "$LOG/summary.txt"
echo "$(date) all done" > "$LOG/DONE"
