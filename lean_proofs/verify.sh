#!/usr/bin/env bash
# Compila todas las demostraciones y comprueba que no usan sorry ni axiomas propios.
# Requisitos: elan (https://github.com/leanprover/elan). La versión de Lean se toma de lean-toolchain.
set -euo pipefail
cd "$(dirname "$0")"
ulimit -s unlimited 2>/dev/null || ulimit -s hard 2>/dev/null || true   # pila grande para Chen y Froehlich
echo "1/4  Buscando 'sorry' y declaraciones 'axiom'..."
if grep -rnwE "sorry|axiom" --include=*.lean . | grep -v "^./CheckAxioms.lean"; then
  echo "ERROR: se encontró sorry/axiom"; exit 1; fi
echo "2/4  Descargando Mathlib precompilado..."
lake exe cache get
echo "3/4  Compilando teoría y modelos (la primera vez, ~1–2 h; Chen y Froehlich son los más largos)..."
lake build
echo "4/4  Axiomas usados por cada teorema:"
lake env lean CheckAxioms.lean 2>&1 | tee axiomas.log | tr "\n" " " | grep -oE "depends on axioms: \[[^]]*\]" | sort | uniq -c
echo "Axiomas del teorema final de cada modelo:"
lake env lean --tstack=4000000 CheckModelAxioms.lean 2>&1 | tee axiomas_modelos.log | tr "\n" " " | grep -oE "depends on axioms: \[[^]]*\]" | sort | uniq -c
echo "Listo. Deben aparecer sólo [propext, Classical.choice, Quot.sound] (o subconjuntos)."
