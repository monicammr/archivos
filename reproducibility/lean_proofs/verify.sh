#!/usr/bin/env bash
# Compiles all proofs and checks that they use neither sorry nor additional axioms.
# Requirements: elan (https://github.com/leanprover/elan). The Lean version is taken from lean-toolchain.
set -euo pipefail
cd "$(dirname "$0")"
ulimit -s unlimited 2>/dev/null || ulimit -s hard 2>/dev/null || true   # large stack for Chen and Froehlich
echo "1/4  Looking for 'sorry' and 'axiom' declarations..."
if grep -rnwE "sorry|axiom" --include=*.lean . | grep -v "^./CheckAxioms.lean"; then
  echo "ERROR: sorry/axiom found"; exit 1; fi
echo "2/4  Downloading the precompiled Mathlib..."
lake exe cache get
echo "3/4  Compiling the theory and the models (first time about 1-2 h; Chen and Froehlich take longest)..."
lake build
echo "4/4  Axioms used by every theorem:"
lake env lean CheckAxioms.lean > axioms.log 2>&1 || { cat axioms.log; echo "ERROR: CheckAxioms.lean failed"; exit 1; }
lake env lean --tstack=4000000 CheckModelAxioms.lean > axioms_models.log 2>&1 || { cat axioms_models.log; echo "ERROR: CheckModelAxioms.lean failed"; exit 1; }
for f in axioms.log axioms_models.log; do
  src=$([ "$f" = axioms.log ] && echo CheckAxioms.lean || echo CheckModelAxioms.lean)
  expected=$(grep -c "^#print axioms" "$src")
  # one line per declaration (Lean may wrap the axiom list over several lines)
  decl=$(tr '\n' ' ' < "$f" | grep -oE "depends on axioms: \[[^]]*\]" | tr -s ' ')
  found=$(printf '%s\n' "$decl" | grep -c "depends on axioms" || true)
  bad=$(printf '%s\n' "$decl" | tr -d ' ' | grep -vE '^dependsonaxioms:\[(propext|Classical\.choice|Quot\.sound|,)*\]$' | grep -c . || true)
  echo "$src: $found of $expected declarations reported, $bad with non-standard axioms"
  printf '%s\n' "$decl" | sort | uniq -c
  if [ "$found" -ne "$expected" ] || [ "$bad" -ne 0 ] || grep -q "sorryAx" "$f"; then echo "ERROR in $src"; exit 1; fi
done
echo "Done: every theorem and every model uses only [propext, Classical.choice, Quot.sound] (or a subset)."
