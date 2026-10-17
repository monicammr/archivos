#!/usr/bin/env bash
# Test of the minimum subset size k_min = 2: the best single parameter of each of the 15 problems in
# which one parameter already reaches the threshold is put through the same tests as our selected
# pair (robustness to the size of the change with paired and independent directions, admissibility
# at +-20 %, synthetic prediction with 20 seeds, identifiability by profile likelihood).
# All analyses run at the same time and share the cores. Resumable.
# Usage (from reproducibility/):  NPROC=88 nohup bash scripts/prueba_kmin.sh > prueba_kmin.log 2>&1 &
set -uo pipefail
cd "$(dirname "$0")/../analysis"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
N=${NPROC:-32}
Q=$(( N / 4 )); [ "$Q" -lt 1 ] && Q=1
LOG=../results/logs_kmin
mkdir -p "$LOG"
echo "$(date) start, $N processes"
python prepare_single_subsets.py
PROBS=$(ls ../results/subsets_single/*.json | xargs -n1 basename | sed 's/.json//' | tr '\n' ' ')

(ROBUST_SUBSETS=subsets_single NPROC=$Q python robustness.py $PROBS > "$LOG/robust_paired.log" 2>&1; echo "$(date) robustness paired done") &
(ROBUST_SUBSETS=subsets_single ROBUST_INDEP=1 NPROC=$Q python robustness.py $PROBS > "$LOG/robust_indep.log" 2>&1; echo "$(date) robustness independent done") &
(ID_SUBSETS=subsets_single NPROC=$Q python identifiability_profiles.py $PROBS > "$LOG/profiles.log" 2>&1
 ID_SUBSETS=subsets_single CERT_OUT=audit2/certificado_single.csv NPROC=$Q python identifiability_conditions.py >> "$LOG/profiles.log" 2>&1
 echo "$(date) identifiability done") &
(CT_METODOS=single CT_PRUEBAS=adm,sint SINT_SEMILLAS=42,43,44,45,46 NPROC=$Q python criteria_tests.py $PROBS > "$LOG/criteria_5.log" 2>&1
 CT_METODOS=single SOLO_SINT=1 SINT_SEMILLAS=47,48,49,50,51,52,53,54,55,56,57,58,59,60,61 NPROC=$Q python criteria_tests.py $PROBS >> "$LOG/criteria_5.log" 2>&1
 ADM_NIVEL=0.20 CT_METODOS=single CT_PRUEBAS=adm NPROC=$Q python criteria_tests.py $PROBS > "$LOG/criteria_20.log" 2>&1
 echo "$(date) admissibility and synthetic done") &
wait
python compare_single_vs_pair.py | tee "$LOG/comparison.txt"
echo "$(date) all done" > "$LOG/DONE"
