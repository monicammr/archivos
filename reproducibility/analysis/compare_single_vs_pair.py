#!/usr/bin/env python3
"""
Test of k_min = 2: compares, on the problems in which a single biological parameter already reaches
the admissibility threshold, the best single parameter j* with the pair selected by our method,
with the same tests (run by scripts/prueba_kmin.sh):

  * robustness: pattern A-D and largest perturbation size up to which the median e_fit stays
    admissible, paired and independent directions (robustness.py);
  * admissibility at +-20 % (criteria_tests.py, method "single" against "ours", fixed scenarios);
  * synthetic prediction: fraction of the seeds with signal in which e_pred <= tau_e (20 seeds);
  * identifiability: every selected parameter practically identifiable (profile likelihood).

Paired comparisons over problems use the exact sign (binomial) test on the problems that differ.
Output: printed table and results/kmin_comparison.json.
"""
import json
import math
from pathlib import Path

from scipy.stats import binomtest

import config as CFG

R = CFG.RESULTS
TAU = math.sqrt(1 - 0.9 ** 2)
LEVELS = ["1", "5", "10", "20", "30", "40", "50"]
probs = sorted(f.stem for f in (R / "subsets_single").glob("*.json"))


def jload(p):
    p = Path(p)
    return json.loads(p.read_text()) if p.exists() else None


def robust(folder, p):
    d = jload(R / folder / f"{p}.json")
    if not d or "niveles" not in d:
        return None
    ok = [lv for lv in LEVELS if lv in d["niveles"] and d["niveles"][lv].get("eaj_med") is not None
          and d["niveles"][lv]["eaj_med"] <= TAU]
    upto = 0
    for lv in LEVELS:
        m = d["niveles"].get(lv, {}).get("eaj_med")
        if m is None or not m <= TAU:
            break
        upto = int(lv)
    pr = [d["niveles"][lv].get("eaj") or [] for lv in LEVELS if lv in d["niveles"]]
    passrate = sum(sum(e <= TAU for e in x) for x in pr) / max(sum(len(x) for x in pr), 1)
    return {"pattern": d.get("patron"), "admissible_up_to": upto, "pass_rate": passrate,
            "median_50": d["niveles"].get("50", {}).get("eaj_med")}


def adm(folder, p, m):
    d = jload(R / folder / f"{p}__{m}__adm.json")
    if not d or "eajuste_med" not in d:
        return None
    return bool(d.get("admisible_sin_kmin", d.get("admisible")))


def synth(p, m):
    vals = []
    if m == "ours":
        for f in (R / "synthetic_seeds" / p).glob("s*.json"):
            d = json.loads(f.read_text())
            if d.get("B_chi2_test_theta0", 0) >= 2 and d.get("B_epred_red") is not None:
                vals.append(d["B_epred_red"] <= TAU)
    else:
        for f in (R / "criteria_tests_fixedscen").glob(f"{p}__{m}__sint_*.json"):
            d = json.loads(f.read_text())
            if d.get("B_chi2_test_theta0", 0) >= 2 and d.get("B_epred_red") is not None:
                vals.append(d["B_epred_red"] <= TAU)
    return (sum(vals), len(vals)) if vals else None


def ident(folder, p):
    d = jload(R / "identifiability" / folder / f"{p}.json")
    if not d or "perfiles" not in d:
        return None
    cl = [q["clase"] for q in d["perfiles"]]
    return (cl.count("identificable"), len(cl))


rows, out = [], {"problems": probs, "per_problem": {}}
for p in probs:
    r = {"single": jload(R / "subsets_single" / f"{p}.json")["S"][0],
         "pair": jload(R / "selection" / f"{p}.json")["S"],
         "robust_paired": {"pair": robust("robustness", p), "single": robust("robustness_subsets_single", p)},
         "robust_indep": {"pair": robust("robustness_independent", p),
                          "single": robust("robustness_independent_subsets_single", p)},
         "adm20": {"pair": adm("criteria_tests_20pc_fixedscen", p, "ours"),
                   "single": adm("criteria_tests_20pc_fixedscen", p, "single")},
         "synthetic": {"pair": synth(p, "ours"), "single": synth(p, "single")},
         "identifiable": {"pair": ident("profiles", p), "single": ident("profiles_subsets_single", p)}}
    out["per_problem"][p] = r


def paired(get, better):
    b = w = n = 0
    for p in probs:
        a, s = get(p, "pair"), get(p, "single")
        if a is None or s is None:
            continue
        n += 1
        if better(a, s):
            b += 1
        elif better(s, a):
            w += 1
    pv = binomtest(b, b + w, 0.5).pvalue if b + w else 1.0
    return {"n": n, "pair_better": b, "single_better": w, "p": pv}


S = {}
for key in ("robust_paired", "robust_indep"):
    g = lambda p, m, k=key: (out["per_problem"][p][k][m] or {}).get("admissible_up_to")
    S[f"{key}_admissible_up_to"] = paired(lambda p, m: g(p, m), lambda a, b: a > b)
    gA = lambda p, m, k=key: None if out["per_problem"][p][k][m] is None else out["per_problem"][p][k][m]["pattern"] == "A"
    S[f"{key}_pattern_A"] = {"pair": sum(bool(gA(p, "pair")) for p in probs),
                             "single": sum(bool(gA(p, "single")) for p in probs)}
S["adm20"] = paired(lambda p, m: out["per_problem"][p]["adm20"][m], lambda a, b: a and not b)
S["adm20"].update(pair=sum(bool(out["per_problem"][p]["adm20"]["pair"]) for p in probs),
                  single=sum(bool(out["per_problem"][p]["adm20"]["single"]) for p in probs))
fr = lambda t: None if not t else t[0] / t[1]
S["synthetic"] = paired(lambda p, m: fr(out["per_problem"][p]["synthetic"][m]), lambda a, b: a > b)
tot = lambda m: [sum(t[i] for p in probs if (t := out["per_problem"][p]["synthetic"][m])) for i in (0, 1)]
S["synthetic"].update(pair_cases=tot("pair"), single_cases=tot("single"))
allid = lambda p, m: None if not (t := out["per_problem"][p]["identifiable"][m]) else t[0] == t[1]
S["identifiable_all"] = paired(allid, lambda a, b: a and not b)
S["identifiable_all"].update(pair=sum(bool(allid(p, "pair")) for p in probs),
                             single=sum(bool(allid(p, "single")) for p in probs))
out["summary"] = S
(R / "kmin_comparison.json").write_text(json.dumps(out, indent=1, default=str))

print(f"{len(probs)} problems in which a single parameter reaches the threshold at +-5 %")
for k, v in S.items():
    print(f"  {k:40s} {v}")
print(f"\n{'problem':16s} {'pair up to (paired/indep)':>26s} {'single up to':>14s}  adm20 p/s  synth p/s  ident p/s")
for p in probs:
    r = out["per_problem"][p]
    u = lambda k, m: (r[k][m] or {}).get("admissible_up_to")
    print(f"{p.split('_')[0]:16s} {str(u('robust_paired', 'pair')) + '/' + str(u('robust_indep', 'pair')):>26s} "
          f"{str(u('robust_paired', 'single')) + '/' + str(u('robust_indep', 'single')):>14s}  "
          f"{r['adm20']['pair']}/{r['adm20']['single']}  {r['synthetic']['pair']}/{r['synthetic']['single']}  "
          f"{r['identifiable']['pair']}/{r['identifiable']['single']}")
