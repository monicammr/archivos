#!/usr/bin/env python3
"""
Statistics of the comparison of selection criteria after the second audit (Table 2, Fig. 4 and the
Supplementary Note "Selection on the training outputs, null controls and standard pivoted QR"):

* admissibility at +-5 % and +-20 % with the fixed scenario set (results/criteria_tests_fixedscen,
  criteria_tests_20pc_fixedscen) for our method (all outputs and training outputs), Brun, Morris,
  profile likelihood, standard pivoted QR (GKS), the earlier pivoted QR variant, calibration only
  (k = 0) and 20 random k-subsets; exact McNemar tests against our method, Holm-adjusted;
* synthetic prediction success (e_pred <= tau_e among the cases with signal, chi2/n of theta0 >= 2)
  for three families of truths, on the cases common to all criteria, with 95 % confidence intervals
  of the difference from our method by resampling whole problems (10,000 replicates, seed 0) and
  Holm-adjusted two-sided p values;
* real data: median ratio of the test chi2/n to that of our method and Wilcoxon signed-rank p.
Output: results/audit2_stats.json and tables/table2_comparison.tex (in PAPER_DIR).
"""
import glob
import json
import math
import collections
from pathlib import Path

import numpy as np
from scipy.stats import binomtest, wilcoxon

from common import RESULTS as R, TAB, EXCLUDE_ADMISSIBILITY

TAU = math.sqrt(1 - 0.81)
ok = lambda x: isinstance(x, (int, float)) and math.isfinite(x)  # noqa: E731
CRIT = ["brun", "morris", "perfil", "qr_gks"]


def J(f):
    return json.loads(Path(f).read_text(encoding="utf-8"))


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, run = [0.0] * len(ps), 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - r) * ps[i]))
        adj[i] = run
    return adj


# ------------------------------------------------------------------------- admissibility
def adm(folder):
    A = collections.defaultdict(dict)
    for f in glob.glob(str(R / folder / "*__adm.json")):
        d = J(f)
        if d.get("sistema") in EXCLUDE_ADMISSIBILITY or "eajuste_med" not in d:
            continue
        key = "admisible_sin_kmin" if d["metodo"] == "empty" else "admisible"
        A[d["metodo"]][d["sistema"]] = bool(d.get(key))
    return A


out = {"admissibility": {}}
for lvl, folder in ((5, "criteria_tests_fixedscen"), (20, "criteria_tests_20pc_fixedscen")):
    A = adm(folder)
    res = {}
    for m in ["ours", "train", "brun", "morris", "perfil", "qr_gks", "qr", "empty"]:
        res[m] = {"admissible": sum(A[m].values()), "n": len(A[m])}
    draws = [sum(A[f"rand{i}"].values()) for i in range(20)]
    nrand = len(A["rand0"])
    frac = {}
    for i in range(20):
        for s, v in A[f"rand{i}"].items():
            frac.setdefault(s, []).append(v)
    res["random"] = {"median_admissible": float(np.median(draws)), "min": min(draws), "max": max(draws),
                     "n": nrand, "problems_majority": sum(np.mean(v) >= 0.5 for v in frac.values()),
                     "median_fraction_per_problem": float(np.median([np.mean(v) for v in frac.values()]))}
    ps = []
    for m in CRIT + ["train"]:
        both = [s for s in A["ours"] if s in A[m]]
        b = sum(A["ours"][s] and not A[m][s] for s in both)
        c = sum(A[m][s] and not A["ours"][s] for s in both)
        p = binomtest(b, b + c, 0.5).pvalue if b + c else 1.0
        res[m].update(mcnemar_only_ours=b, mcnemar_only_other=c, p_raw=p)
        ps.append(p)
    for m, p in zip(CRIT + ["train"], holm(ps[:4]) + [ps[4]]):
        res[m]["p_holm"] = p
    out["admissibility"][lvl] = res


# ------------------------------------------------------------------------- synthetic
def load_sint(family):
    S = collections.defaultdict(lambda: collections.defaultdict(dict))
    if family == "uniforme":
        srcs = [("criteria_tests", None), ("criteria_tests_fixedscen", None)]
        for f in glob.glob(str(R / "synthetic_seeds" / "*" / "s*.json")):
            d = J(f)
            if ok(d.get("B_epred_red")) and ok(d.get("B_chi2_test_theta0")):
                S[d["sistema"]]["ours"][d["semilla"]] = d
    else:
        srcs = [(f"criteria_tests_sint_{family}", None)]
    for folder, _ in srcs:
        for f in glob.glob(str(R / folder / "*__sint_*.json")):
            d = J(f)
            if ok(d.get("B_epred_red")) and ok(d.get("B_chi2_test_theta0")):
                S[d["sistema"]][d["metodo"]].setdefault(d["semilla"], d)
    return S


def synth(family, methods, ref):
    S = load_sint(family)
    cnt = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    for s in S:
        seeds = set.intersection(*[set(S[s][m]) for m in methods]) if all(S[s][m] for m in methods) else set()
        for k in seeds:
            ds = [S[s][m][k] for m in methods]
            if ds[0]["B_chi2_test_theta0"] < 2:
                continue
            for m, d in zip(methods, ds):
                cnt[s][m][0] += d["B_epred_red"] <= TAU
                cnt[s][m][1] += 1
    sis = sorted(cnt)
    rng = np.random.default_rng(0)
    idx = rng.integers(0, len(sis), size=(10000, len(sis)))
    a = {m: np.array([cnt[s][m][0] for s in sis], float) for m in methods}
    n = np.array([cnt[s][methods[0]][1] for s in sis], float)
    res = {"cases": int(n.sum()), "problems": len(sis)}
    ps = {}
    for m in methods:
        rate = a[m].sum() / n.sum()
        bt = a[m][idx].sum(1) / n[idx].sum(1)
        r = {"rate": rate, "ci": list(np.percentile(bt, [2.5, 97.5]))}
        if m != ref:
            diff = (a[ref][idx].sum(1) - a[m][idx].sum(1)) / n[idx].sum(1)
            r["diff_vs_ref"] = (a[ref].sum() - a[m].sum()) / n.sum()
            r["diff_ci"] = list(np.percentile(diff, [2.5, 97.5]))
            p = 2 * min((diff <= 0).mean(), (diff >= 0).mean())
            r["p_raw"] = float(max(p, 2 / 10000))
            ps[m] = r["p_raw"]
        res[m] = r
    crit = [m for m in CRIT if m in ps]
    for m, p in zip(crit, holm([ps[m] for m in crit])):
        res[m]["p_holm"] = p
    return res


out["synthetic"] = {}
for fam in ["uniforme", "loguniforme", "dispersa"]:
    out["synthetic"][fam] = {
        "ref_ours": synth(fam, ["ours", "brun", "morris", "perfil", "qr_gks", "qr"], "ours"),
        "ref_train": synth(fam, ["train", "brun", "morris", "perfil", "qr_gks", "qr", "ours"], "train")}

# ------------------------------------------------------------------------- real data
nest = {Path(f).stem: J(f) for f in glob.glob(str(R / "nested_validation" / "*.json"))}
ours = {s: d.get("chi2_test_red_original") for s, d in nest.items()}
real = {}
gks = {Path(f).stem: J(f) for f in glob.glob(str(R / "qr_selection_gks" / "*.json"))}
src = {"qr_gks": {s: d.get("chi2_qr") for s, d in gks.items()}}
src["train"] = {}
for f in glob.glob(str(R / "criteria_tests_fixedscen" / "*__train__real.json")):
    d = J(f)
    src["train"][d["sistema"]] = d.get("chi2_test")
for m, dic in src.items():
    r = [dic[s] / ours[s] for s in ours if s in dic and ok(dic.get(s)) and ok(ours[s]) and dic[s] > 0 and ours[s] > 0]
    lr = np.log(r)
    p = wilcoxon(lr, zero_method="wilcox").pvalue if np.any(lr != 0) else 1.0
    real[m] = {"median_ratio": float(np.median(r)), "n": len(r), "p": float(p)}
out["real"] = real

# ------------------------------------------------------------------------- other numbers
a5 = [J(f) for f in glob.glob(str(R / "selection_fixedscen" / "*.json"))]
a1 = [J(f) for f in glob.glob(str(R / "selection_train_fixedscen" / "*.json"))]
orig = {Path(f).stem: J(f) for f in glob.glob(str(R / "selection" / "*.json"))}
out["fixed_scenarios"] = {"changed": [d["sistema"] for d in a5 if set(d.get("S", [])) != set(orig[d["sistema"]].get("S", []))],
                          "nested_pairs": sum(d.get("monotonia", {}).get("nested_pairs", 0) for d in a5 + a1),
                          "violations": sum(d.get("monotonia", {}).get("violations", 0) for d in a5 + a1)}
out["train_selection"] = {"admissible": sum(bool(d.get("admisible")) for d in a1), "n": len(a1),
                          "different": sum(set(d.get("S", [])) != set(orig[d["sistema"]].get("S", [])) for d in a1)}
out["nonlinear"] = {Path(f).stem: J(f) for f in glob.glob(str(R / "efit_nonlinear" / "*.json"))}
(R / "audit2_stats.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")


# ------------------------------------------------------------------------- Table 2
def pc(x):
    return f"{100 * x:.0f}\\%"


def pv(p):
    if p is None:
        return "--"
    return "$<0.001$" if p < 0.001 else f"{p:.3f}" if p < 0.01 else f"{p:.2f}"


A5, A20 = out["admissibility"][5], out["admissibility"][20]
U = out["synthetic"]["uniforme"]["ref_ours"]
LG = out["synthetic"]["loguniforme"]["ref_ours"]
DS = out["synthetic"]["dispersa"]["ref_ours"]
Ut = out["synthetic"]["uniforme"]["ref_train"]
rows = [
    ("Ours (all)", "", "ours"),
    ("Ours (train.)", "", "train"),
    ("Brun", "", "brun"),
    ("Morris", "", "morris"),
    ("Profile lik.", "", "perfil"),
    ("Pivoted QR", "", "qr_gks"),
]
# identifiability of the selected parameters (identif_criteria_tables.py), if computed
_IDF = R / "identifiability" / "criteria_identifiability.json"
IDF = json.loads(_IDF.read_text())["criteria"] if _IDF.exists() else {}


def idcells(m):
    r = IDF.get(m)
    if not r:
        return "--"
    both = f"\\textbf{{{r['identifiable_and_admissible']}}}" if m == "ours" else f"{r['identifiable_and_admissible']}"
    return f"{r['identifiable']}/{r['selected']} ({both})"


lines = ["% Generated by figures_tables/audit2_stats.py (second audit, fixed scenario set).",
         "\\begin{tabular}{@{}lccccccccc@{}}", "\\toprule",
         " & \\multicolumn{2}{c}{Admissible} & Identifiable & \\multicolumn{4}{c}{Synthetic: $e_{\\mathrm{pred}}\\le\\tau_e$} & Real data \\\\",
         "\\cmidrule(lr){2-3}\\cmidrule(lr){4-4}\\cmidrule(lr){5-8}\\cmidrule(lr){9-9}",
         "Criterion & $\\pm$5\\% & $\\pm$20\\% & \\begin{tabular}[b]{@{}c@{}}Param.\\\\(both)\\end{tabular} & Uniform & \\begin{tabular}[b]{@{}c@{}}Ours $-$ other\\\\(95\\% CI)\\end{tabular} & Log-unif. & Sparse & \\begin{tabular}[b]{@{}c@{}}$\\chi^2$ ratio\\\\($P$)\\end{tabular} \\\\",
         "\\midrule"]
for name, basis, m in rows:
    a, b = A5[m], A20[m]
    if m == "ours":
        syn, d, lg, ds, rl = pc(U["ours"]["rate"]), "--", pc(LG["ours"]["rate"]), pc(DS["ours"]["rate"]), "--"
        cell5, cell20 = f"\\textbf{{{a['admissible']}/{a['n']}}}", f"\\textbf{{{b['admissible']}/{b['n']}}}"
    elif m == "train":
        syn = pc(Ut["train"]["rate"])
        o = Ut["ours"]
        d = f"${-100 * o['diff_vs_ref']:+.0f}$ [${-100 * o['diff_ci'][1]:.0f}$, ${-100 * o['diff_ci'][0]:.0f}$]"
        lg = pc(out["synthetic"]["loguniforme"]["ref_train"]["train"]["rate"])
        ds = pc(out["synthetic"]["dispersa"]["ref_train"]["train"]["rate"])
        rl = f"{real['train']['median_ratio']:.2f} ({pv(real['train']['p'])})"
        cell5, cell20 = f"{a['admissible']}/{a['n']}", f"{b['admissible']}/{b['n']}"
    else:
        r = U[m]
        syn = pc(r["rate"])
        d = f"${100 * r['diff_vs_ref']:+.0f}$ [${100 * r['diff_ci'][0]:.0f}$, ${100 * r['diff_ci'][1]:.0f}$]"
        lg, ds = pc(LG[m]["rate"]), pc(DS[m]["rate"])
        rl = {"brun": "1.00 (0.27)", "morris": "1.00 (0.46)", "perfil": "1.00 (0.44)"}.get(m)
        if m == "qr_gks":
            rl = f"{real['qr_gks']['median_ratio']:.2f} ({pv(real['qr_gks']['p'])})"
        cell5, cell20 = f"{a['admissible']}/{a['n']}", f"{b['admissible']}/{b['n']}"
    ip = idcells(m)
    lines.append(f"{name} & {cell5} & {cell20} & {ip} & {syn} & {d} & {lg} & {ds} & {rl} \\\\")
rnd = A5["random"]
lines.append(f"Random (20) &{rnd['median_admissible']:.0f}/{rnd['n']} & "
             f"{A20['random']['median_admissible']:.0f}/{A20['random']['n']} & -- & -- & -- & -- & -- & 1.00 (0.27) \\\\")
lines.append(f"Calib. ($k=0$) & {A5['empty']['admissible']}/{A5['empty']['n']} & "
             f"{A20['empty']['admissible']}/{A20['empty']['n']} & -- & -- & -- & -- & -- & 0.99 (0.003) \\\\")
lines += ["\\botrule", "\\end{tabular}"]
(TAB / "table2_comparison.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(json.dumps({"adm5": {m: (v.get("admissible", v.get("median_admissible")), v["n"], round(v.get("p_holm", -1), 4) if "p_holm" in v else None) for m, v in A5.items()},
                  "adm20": {m: (v.get("admissible", v.get("median_admissible")), v["n"], round(v.get("p_holm", -1), 4) if "p_holm" in v else None) for m, v in A20.items()},
                  "uniform": {m: (round(v["rate"], 3), round(v.get("p_holm", v.get("p_raw", -1)), 4)) for m, v in U.items() if isinstance(v, dict)},
                  "uniform_cases": (U["cases"], U["problems"]),
                  "uniform_train": {m: (round(v["rate"], 3), round(v.get("p_holm", v.get("p_raw", -1)), 4)) for m, v in Ut.items() if isinstance(v, dict)},
                  "train_cases": (Ut["cases"], Ut["problems"]),
                  "logunif": {m: (round(v["rate"], 3), round(v.get("p_holm", v.get("p_raw", -1)), 4)) for m, v in LG.items() if isinstance(v, dict)},
                  "logunif_cases": (LG["cases"], LG["problems"]),
                  "sparse": {m: (round(v["rate"], 3), round(v.get("p_holm", v.get("p_raw", -1)), 4)) for m, v in DS.items() if isinstance(v, dict)},
                  "sparse_cases": (DS["cases"], DS["problems"]),
                  "real": real, "fixed": out["fixed_scenarios"], "train_sel": out["train_selection"]}, indent=0, default=float))
