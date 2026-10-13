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
lake env lean CheckAxioms.lean 2>&1 | tee axioms.log | tr "\n" " " | grep -oE "depends on axioms: \[[^]]*\]" | sort | uniq -c
echo "Axioms of the final theorem of every model:"
lake env lean --tstack=4000000 CheckModelAxioms.lean 2>&1 | tee axioms_models.log | tr "\n" " " | grep -oE "depends on axioms: \[[^]]*\]" | sort | uniq -c
echo "Done. Only [propext, Classical.choice, Quot.sound] (or subsets) should appear."
