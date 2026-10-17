#!/usr/bin/env python3
"""
Writes the subsets chosen by the other selection criteria in the format read by
identifiability_profiles.py (ID_SUBSETS=<folder>), so that the identifiability of the selected
parameters can be compared between criteria with exactly the same procedure as for our subsets.

For every problem with an admissible subset of our method and a subset of the criterion:
  results/subsets_<criterion>/<problem>.json = {"sistema", "S", "calibracion", "admisible": true,
                                                "origen"}
The calibration parameters are those of our selection (they are always re-estimated, by every
criterion). "admisible" only marks the problem for profiling; it does not mean that the subset of
the criterion reproduces the full model (that is the admissibility test of criteria_tests.py).

Criteria (all selected on the training outputs, with the same k = |S| as our method):
  brun     results/brun_morris/<p>.json, key S_brun
  morris   results/brun_morris/<p>.json, key S_morris
  qr_gks   results/qr_selection_gks/<p>.json, key S_qr  (standard Golub-Klema-Stewart pivoted QR)
  perfil   results/profile_likelihood/<p>.json, key S_perfil

Usage: python prepare_criteria_subsets.py      -> prints the number of problems per criterion
"""
import json

import config as CFG

R = CFG.RESULTS
SOURCES = {"brun": ("brun_morris", "S_brun"), "morris": ("brun_morris", "S_morris"),
           "qr_gks": ("qr_selection_gks", "S_qr"), "perfil": ("profile_likelihood", "S_perfil")}

if __name__ == "__main__":
    sel = {f.stem: json.loads(f.read_text()) for f in CFG.SELECTION.glob("*.json")}
    for crit, (folder, key) in SOURCES.items():
        out = R / f"subsets_{crit}"
        out.mkdir(parents=True, exist_ok=True)
        n = same = 0
        for f in sorted((R / folder).glob("*.json")):
            p = f.stem
            ours = sel.get(p)
            if not ours or not ours.get("admisible"):
                continue
            S = json.loads(f.read_text()).get(key) or []
            if not S:
                continue
            (out / f"{p}.json").write_text(json.dumps({
                "sistema": p, "S": S, "calibracion": ours.get("calibracion", []), "admisible": True,
                "origen": f"{folder}/{p}.json:{key}"}, indent=1))
            n += 1
            same += set(S) == set(ours["S"])
        print(f"{crit:7s} {n:3d} problems written to {out.name}/ ({same} identical to our subset, "
              f"{n - same} to profile)")
