#!/usr/bin/env bash
# Identifiability analyses requested after the second audit (server). Resumable.
#   (a) profiles of the subsets selected on the training outputs (only the problems whose subset
#       differs from the main one), and the hypotheses of the Lean theorem for them
#   (b) dense profiles (20 displacements per side) of the main subsets, from the same optimum
#   (c) hypotheses of the Lean theorems (absolute and relative remainder on the tail) over the
#       admissible set, by sampling and adversarial search, for regions of radius 10, 5, 3, 2, 1.5
# Usage: NPROC=30 nohup bash scripts/identificabilidad_audit2.sh > identif.log 2>&1 &
set -uo pipefail
cd "$(dirname "$0")/../analysis"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
N=${NPROC:-30}
LOG=../results/logs_fase_a
mkdir -p "$LOG"
ID=../results/identifiability
echo "$(date) start identifiability"

# (b) dense profiles from the optimum of the main profiles
for d in $ID/profiles/*/; do
  n=$(basename "$d")
  mkdir -p "$ID/profiles_dense/$n"
  [ -f "$ID/profiles_dense/$n/minimo.npz" ] || cp "$d/minimo.npz" "$ID/profiles_dense/$n/"
done
(ID_DENSE=1 NPROC=$N python identifiability_profiles.py > "$LOG/id_dense.log" 2>&1 &&
 ID_DENSE=1 CERT_OUT=certificado_dense.csv NPROC=$N python identifiability_conditions.py >> "$LOG/id_dense.log" 2>&1;
 echo "$(date) (b) done") &

# (a) subsets selected on the training outputs
(ID_SUBSETS=selection_train_fixedscen ID_SOLO_CAMBIADOS=1 NPROC=$N python identifiability_profiles.py > "$LOG/id_train.log" 2>&1 &&
 ID_SUBSETS=selection_train_fixedscen CERT_OUT=certificado_train.csv NPROC=$N python identifiability_conditions.py >> "$LOG/id_train.log" 2>&1;
 echo "$(date) (a) done") &

# (c) over the admissible set
for r in 10 5 3 2 1.5; do
  ID_BOX_RADIUS=$r ID_BOX_N=${ID_BOX_N:-512} NPROC=$N python identifiability_box.py > "$LOG/id_box_r$r.log" 2>&1
  echo "$(date) (c) radius $r done"
done
wait
echo "identifiability done $(date)" > "$LOG/ID_DONE"
