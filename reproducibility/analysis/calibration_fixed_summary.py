#!/usr/bin/env python3
"""
Summary of the test of the role of the calibration parameters (pre-submission audit, L6).

For the problems with calibration parameters, compares the admissibility test at +-5 % with the
standard scenarios (all parameters perturbed; results/criteria_tests_fixedscen/) and with the
calibration parameters kept at theta0 (only the biological parameters perturbed, same biological
perturbations; results/criteria_tests_calfixed/), for our subsets, the calibration parameters
alone (k = 0, without the rule |S| >= 2), the 20 random k-subsets and the subsets of the other
criteria. It also reports, per problem, the median share of the output change of the standard
scenarios that the calibration parameters alone produce.

Usage:   python calibration_fixed_summary.py
Output:  results/calibration_fixed_summary.json and a table on standard output.
"""
import json, glob
from pathlib import Path
import numpy as np
import config as CFG

R = CFG.RESULTS
STD, CAL = R / "criteria_tests_fixedscen", R / "criteria_tests_calfixed"
CRIT = ["ours", "train", "brun", "morris", "perfil", "qr_gks"]


def load(folder):
    A = {}
    for f in glob.glob(str(folder / "*__adm.json")):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        if "eajuste_med" in d:
            A[(d["sistema"], d["metodo"])] = d
    return A


def ok(d, m):
    if d is None:
        return None
    return bool(d["admisible_sin_kmin"] if m == "empty" else d["admisible"])


S, C = load(STD), load(CAL)
probs = sorted({p for p, m in C if m == "ours"})
rows, out = [], {"problems": {}, "counts": {}}
for p in probs:
    r = {"share_calibration": C[(p, "ours")].get("frac_cambio_calibracion_med")}
    for tag, A in (("standard", S), ("calfixed", C)):
        r[tag] = {m: ok(A.get((p, m)), m) for m in CRIT + ["empty"]}
        r[tag]["efit_ours"] = A.get((p, "ours"), {}).get("eajuste_med")
        rnd = [ok(A.get((p, f"rand{i}")), "rand") for i in range(20)]
        rnd = [x for x in rnd if x is not None]
        r[tag]["random_fraction"] = float(np.mean(rnd)) if rnd else None
        r[tag]["discriminates"] = bool(r[tag]["empty"] is False and rnd != [] and np.mean(rnd) < 0.5)
    out["problems"][p] = r
for tag in ("standard", "calfixed"):
    cnt = {}
    for m in CRIT + ["empty"]:
        v = [out["problems"][p][tag][m] for p in probs if out["problems"][p][tag][m] is not None]
        cnt[m] = {"admissible": int(sum(v)), "n": len(v)}
    rf = [out["problems"][p][tag]["random_fraction"] for p in probs if out["problems"][p][tag]["random_fraction"] is not None]
    cnt["random_median_fraction"] = float(np.median(rf)) if rf else None
    cnt["random_majority_problems"] = int(sum(x >= 0.5 for x in rf))
    cnt["discriminating_problems"] = [p for p in probs if out["problems"][p][tag]["discriminates"]]
    out["counts"][tag] = cnt
out["processor_hours"] = round(sum(d.get("segundos", 0) for d in C.values()) / 3600, 2)
(R / "calibration_fixed_summary.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")

print(f"{len(probs)} problems with calibration parameters; processor time {out['processor_hours']} h")
print(f"{'problem':<28}{'share C':>8}  {'ours std/cal':>13}  {'calib. only':>12}  {'random std/cal':>15}")
for p in probs:
    r = out["problems"][p]
    sh = r["share_calibration"]
    f = lambda x: "--" if x is None else ("yes" if x else "no")
    rf = lambda x: "--" if x is None else f"{x:.2f}"
    print(f"{p.split('_')[0]:<28}{('--' if sh is None else f'{sh:.2f}'):>8}  "
          f"{f(r['standard']['ours']) + '/' + f(r['calfixed']['ours']):>13}  "
          f"{f(r['standard']['empty']) + '/' + f(r['calfixed']['empty']):>12}  "
          f"{rf(r['standard']['random_fraction']) + '/' + rf(r['calfixed']['random_fraction']):>15}")
for tag in ("standard", "calfixed"):
    c = out["counts"][tag]
    print(tag, {m: f"{c[m]['admissible']}/{c[m]['n']}" for m in CRIT + ["empty"]},
          "random median fraction", c["random_median_fraction"], "| problems where the test discriminates:",
          len(c["discriminating_problems"]))
