#!/usr/bin/env python3
"""
Test of the minimum subset size k_min = 2: writes, for every problem in which a single biological
parameter already reaches the admissibility threshold (results/single_parameter/, Supplementary Note
"Single-parameter subsets"), the best such parameter j* (smallest median e_fit at +-5 %) as a
subset of size one, in the format read by robustness.py (ROBUST_SUBSETS), criteria_tests.py
(method "single") and identifiability_profiles.py (ID_SUBSETS):

  results/subsets_single/<problem>.json = {"sistema", "S": [j*], "calibracion", "admisible": true,
                                           "e_fit_5", "S_ours"}

The calibration parameters are those of our selection; they are re-estimated with j*, as with the
selected pair. "admisible" marks the problem for the other programs; the size rule |S| >= 2 is not
applied to these subsets.

Usage: python prepare_single_subsets.py
"""
import json

import config as CFG

R = CFG.RESULTS
if __name__ == "__main__":
    out = R / "subsets_single"
    out.mkdir(parents=True, exist_ok=True)
    n = 0
    for f in sorted((R / "single_parameter").glob("*.json")):
        d = json.loads(f.read_text())
        adm = [u for u in d.get("un_parametro", []) if u.get("admisible")]
        if not adm:
            continue
        best = min(adm, key=lambda u: u["e_fit"])
        sel = json.loads((CFG.SELECTION / f.name).read_text())
        (out / f.name).write_text(json.dumps({
            "sistema": f.stem, "S": [best["parametro"]], "calibracion": sel.get("calibracion", []),
            "admisible": True, "e_fit_5": best["e_fit"], "S_ours": sel["S"]}, indent=1))
        n += 1
        print(f"{f.stem:38s} single: {best['parametro']:40s} e_fit {best['e_fit']:.3f}   ours: {', '.join(sel['S'])}")
    print(f"{n} problems written to {out}")
