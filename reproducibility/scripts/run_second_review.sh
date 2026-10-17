#!/usr/bin/env bash
# Re-analyses requested by the second audit (phase A), for a many-core server. Every step skips the
# tasks whose result file exists (criteria_tests.py, efit_nonlinear.py), so the script can be resumed.
#   A5  selection.py, REPRO_FIXED_SCEN=1: fixed scenario set, first-order e_fit = min(e_rel, proj.)
#   A1  selection.py, REPRO_OUTPUTS=train REPRO_FIXED_SCEN=1: selection on the training outputs
#   A2  efit_nonlinear.py: nonlinear e_fit of the final subsets of the first-order problems
#   A4  qr_selection.py, QR_VARIANT=gks: standard Golub-Klema-Stewart QR
#   A3  criteria_tests.py: admissibility of k = 0 and of 20 random k-subsets (+-5 % and +-20 %),
#       together with the five criteria under the same (fixed-scenario) rule
#   A6  criteria_tests.py, SINT_FAMILIA=loguniforme / dispersa: other synthetic truths (10 seeds)
# Usage: NCORES=88 nohup bash scripts/run_second_review.sh > second_review.log 2>&1 &
set -uo pipefail
cd "$(dirname "$0")/../analysis"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
N=${NCORES:-$(nproc)}
LOG=../results/logs_second_review
mkdir -p "$LOG"
PROBS=$(python -c "import config as C; print(' '.join(C.PROBLEMS))")
RAND=$(python -c "print(','.join(f'rand{i}' for i in range(20)))")
ALL="ours,qr,qr_gks,brun,morris,perfil,empty,$RAND"
echo "$(date) start, $N cores"

# --- block 1, in parallel: A5 and A1 (8 problems at a time each; large problems use 6 cores) and A2
sel() {  # sel <log> <env...>
  local log=$1; shift
  printf '%s\n' $PROBS | xargs -P 8 -I{} env "$@" NPROC=6 python selection.py {} > "$LOG/$log" 2>&1
}
sel a5_all_fixedscen.log REPRO_FIXED_SCEN=1 &
P_A5=$!
sel a1_train_fixedscen.log REPRO_OUTPUTS=train REPRO_FIXED_SCEN=1 &
P_A1=$!
NPROC=30 python efit_nonlinear.py > "$LOG/a2_efit_nonlinear.log" 2>&1 &
P_A2=$!
# A4 (minutes)
QR_VARIANT=gks NPROC=8 python qr_selection.py > "$LOG/a4_qr_gks.log" 2>&1
echo "$(date) A4 done"

# --- block 2: A3 + A4 admissibility at +-5 % and +-20 %, QR standard on real and synthetic data
NPROC=$((N / 2)) CT_PRUEBAS=adm CT_METODOS=$ALL python criteria_tests.py > "$LOG/adm05.log" 2>&1
echo "$(date) adm 5 % done"
NPROC=$((N / 2)) ADM_NIVEL=0.20 CT_PRUEBAS=adm CT_METODOS=$ALL python criteria_tests.py > "$LOG/adm20.log" 2>&1
echo "$(date) adm 20 % done"
NPROC=$((N / 2)) CT_PRUEBAS=real,sint CT_METODOS=qr_gks SINT_SEMILLAS=$(seq -s, 42 61) \
  python criteria_tests.py > "$LOG/qr_gks_tests.log" 2>&1
echo "$(date) QR standard done"

# --- block 3: A6, other families of synthetic truths
wait $P_A5 $P_A1
echo "$(date) A5 and A1 done"
for fam in loguniforme dispersa; do
  NPROC=$((N - 30)) SINT_FAMILIA=$fam CT_PRUEBAS=sint CT_METODOS=ours,qr,qr_gks,brun,morris,perfil,train \
    SINT_SEMILLAS=$(seq -s, 42 51) python criteria_tests.py > "$LOG/sint_$fam.log" 2>&1
  echo "$(date) family $fam done"
done

# --- block 4: A1, the subsets selected on the training outputs, through the same tests
NPROC=$((N - 30)) CT_PRUEBAS=adm,real,sint CT_METODOS=train SINT_SEMILLAS=$(seq -s, 42 61) \
  python criteria_tests.py > "$LOG/train_tests.log" 2>&1
NPROC=$((N - 30)) ADM_NIVEL=0.20 CT_PRUEBAS=adm CT_METODOS=train python criteria_tests.py >> "$LOG/train_tests.log" 2>&1
echo "$(date) train tests done"

wait $P_A2
echo "$(date) A2 done"
echo "fase A done $(date)" > "$LOG/DONE"
