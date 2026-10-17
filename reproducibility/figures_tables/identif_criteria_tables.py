#!/usr/bin/env python3
"""
Identifiability of the parameters selected by every criterion (Supplementary Note "Identifiability
of the subsets of other criteria" and the column "Identifiable" of Table 2).

The profiles of the subsets of the other criteria were computed by
scripts/identificabilidad_criterios.sh with exactly the procedure used for our subsets (reduced
problem: selected and calibration parameters free, all other parameters at theta0, all data;
Delta chi2 = 3.84 on both sides). Where a criterion chose the same subset as our method, our
profiles are used.

Writes (in PAPER_DIR/tables):
  tableS_identif_criteria.tex           summary per criterion (problems common to all criteria)
  tableS_identif_criteria_problems.tex  per problem and criterion
and results/identifiability/criteria_identifiability.json (numbers quoted in the text and Table 2).
"""
import glob
import json
import math
import statistics
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

from common import RESULTS as R, TAB, EXCLUDE_ADMISSIBILITY

ID = R / "identifiability"
CRIT = ["ours", "train", "brun", "morris", "perfil", "qr_gks"]
LABEL = {"ours": "Ours (all outputs)", "train": "Ours (training)", "brun": "Brun", "morris": "Morris",
         "perfil": "Profile likelihood", "qr_gks": "Pivoted QR"}
SUBF = {"train": "selection_train_fixedscen", "brun": "subsets_brun", "morris": "subsets_morris",
        "perfil": "subsets_perfil", "qr_gks": "subsets_qr_gks"}
PROF = {"ours": "profiles", "train": "profiles_selection_train_fixedscen", "brun": "profiles_subsets_brun",
        "morris": "profiles_subsets_morris", "perfil": "profiles_subsets_perfil", "qr_gks": "profiles_subsets_qr_gks"}
short = lambda s: s.split("_")[0].replace("SalazarCavazos", "Salazar-Cavazos")


def profiles(folder):
    out = {}
    for f in (ID / folder).glob("*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        if "perfiles" in d:
            out[f.stem] = {p["parametro"]: p["clase"] for p in d["perfiles"]}
    return out


def cpu_hours(folder):
    t = 0.0
    for d in (ID / folder).iterdir() if (ID / folder).exists() else []:
        if d.is_dir():
            t += sum(json.loads(f.read_text()).get("segundos", 0.0) for f in d.glob("p_*.json"))
            if (d / "minimo.npz").exists():
                m = np.load(d / "minimo.npz")
                t += float(m["segundos"]) if "segundos" in m.files else 0.0
    return t / 3600


def admissibility():
    A = {}
    for f in glob.glob(str(R / "criteria_tests_fixedscen" / "*__adm.json")):
        d = json.loads(Path(f).read_text())
        if d.get("sistema") in EXCLUDE_ADMISSIBILITY or "eajuste_med" not in d:
            continue
        A.setdefault(d["metodo"], {})[d["sistema"]] = bool(d.get("admisible"))
    A["perfil"] = A.get("perfil", {})
    return A


sel = {f.stem: json.loads(f.read_text()) for f in (R / "selection").glob("*.json")}
ours = profiles("profiles")
res, same = {"ours": ours}, {"ours": {p: True for p in ours}}
for c in CRIT[1:]:
    prof = profiles(PROF[c])
    r, s = {}, {}
    for f in (R / SUBF[c]).glob("*.json"):
        d = json.loads(f.read_text())
        p = f.stem
        if not d.get("admisible") or p not in sel or not sel[p].get("admisible"):
            continue
        if set(d["S"]) == set(sel[p]["S"]) and p in ours:
            r[p], s[p] = ours[p], True
        elif p in prof:
            r[p], s[p] = prof[p], False
    res[c], same[c] = r, s

OTHERS = ["brun", "morris", "perfil", "qr_gks"]
common = sorted(set(ours).intersection(*[set(res[c]) for c in OTHERS]) - set(EXCLUDE_ADMISSIBILITY))
ADM = admissibility()
ni = lambda c, p: sum(v == "identificable" for v in res[c][p].values())
allid = lambda c, p: all(v == "identificable" for v in res[c][p].values())

summary = {"common_problems": common, "criteria": {}}
for c in CRIT:
    ps = [p for p in common if p in res[c]]
    adm = ADM.get(c if c != "ours" else "ours", {})
    both = [p for p in ps if allid(c, p) and adm.get(p, False)]
    row = {"problems": len(ps), "identifiable": sum(ni(c, p) for p in ps),
           "selected": sum(len(res[c][p]) for p in ps), "all_identifiable": sum(allid(c, p) for p in ps),
           "admissible_5": sum(adm.get(p, False) for p in ps), "identifiable_and_admissible": len(both),
           "identical_to_ours": sum(same[c].get(p, False) for p in ps),
           "cpu_h": round(cpu_hours(PROF[c]), 1) if c not in ("ours", "train") else None}
    if c != "ours":
        b = sum(allid("ours", p) and not allid(c, p) for p in ps)
        k = sum(allid(c, p) and not allid("ours", p) for p in ps)
        row["mcnemar_all_identifiable"] = {"only_ours": b, "only_other": k,
                                           "p": binomtest(b, b + k, 0.5).pvalue if b + k else 1.0}
        b2 = sum((allid("ours", p) and ADM["ours"].get(p, False)) and not (allid(c, p) and adm.get(p, False)) for p in ps)
        k2 = sum((allid(c, p) and adm.get(p, False)) and not (allid("ours", p) and ADM["ours"].get(p, False)) for p in ps)
        row["mcnemar_both"] = {"only_ours": b2, "only_other": k2,
                               "p": binomtest(b2, b2 + k2, 0.5).pvalue if b2 + k2 else 1.0}
    summary["criteria"][c] = row
def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, run = [0.0] * len(ps), 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - r) * ps[i]))
        adj[i] = run
    return adj


for key in ("mcnemar_all_identifiable", "mcnemar_both"):
    adj = holm([summary["criteria"][c][key]["p"] for c in OTHERS])
    for c, a in zip(OTHERS, adj):
        summary["criteria"][c][key]["p_holm"] = a
(ID / "criteria_identifiability.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")

# ---- summary table
fp = lambda x: "--" if x is None else (f"{x:.2g}" if x >= 0.001 else "$<$0.001")
L = [r"\begin{longtable}{@{}lrrrrrrr@{}}",
     r"\caption{Practical identifiability of the parameters selected by every criterion, with the profile-likelihood procedure of our subsets (reduced problem, all data, $\Delta\chi^2=3.84$ on both sides), over the " + str(len(common)) +
     r" problems in which every criterion has a subset. Identifiable: selected parameters whose 95\% profile-likelihood interval is bounded on both sides within the bounds of the study. All identifiable: problems in which every selected parameter is identifiable. Admissible: the subset reproduces the full model at $\pm$5\% (Table~2 of the main text). Both: all parameters identifiable \emph{and} the subset admissible. $P$: exact McNemar test against our subsets (all outputs) over problems, for ``all identifiable'' and for ``both'', Holm-adjusted over the four existing criteria (for our subsets selected on the training outputs, unadjusted). Bertozzi is excluded, as in the comparison of admissibility. Same as ours: problems in which the criterion chose exactly our subset, whose profiles are then ours. Our subsets selected on the training outputs are shown only for the problems in which that selection gave an admissible subset.}\label{tab:identifcrit}\\",
     r"\toprule", r"Criterion & Problems & Identifiable & All identifiable & Admissible & Both & $P$ (all id.; both) & Same as ours \\", r"\midrule", r"\endfirsthead",
     r"\toprule", r"Criterion & Problems & Identifiable & All identifiable & Admissible & Both & $P$ (all id.; both) & Same as ours \\", r"\midrule", r"\endhead"]
for c in CRIT:
    r = summary["criteria"][c]
    pv = "--" if c == "ours" else f"{fp(r['mcnemar_all_identifiable'].get('p_holm', r['mcnemar_all_identifiable']['p']))}; {fp(r['mcnemar_both'].get('p_holm', r['mcnemar_both']['p']))}"
    L.append(f"{LABEL[c]} & {r['problems']} & {r['identifiable']}/{r['selected']} ({100 * r['identifiable'] / r['selected']:.0f}\\%) & "
             f"{r['all_identifiable']} & {r['admissible_5']} & {r['identifiable_and_admissible']} & {pv} & "
             f"{'--' if c == 'ours' else r['identical_to_ours']} \\\\")
L += [r"\bottomrule", r"\end{longtable}"]
(TAB / "tableS_identif_criteria.tex").write_text("\n".join(L) + "\n", encoding="utf-8")

# ---- per-problem table
cols = CRIT
L = [r"\begin{longtable}{@{}l" + "c" * len(cols) + r"@{}}",
     r"\caption{Identifiable parameters / selected parameters for every problem and criterion (profile likelihood of the reduced problem). $=$, same subset as ours (profiles shared); $^{\ast}$, the subset is admissible at $\pm$5\%; --, no subset. Problems below the line are not common to all criteria and are not included in the summary of Supplementary Table~\ref{tab:identifcrit}.}\label{tab:identifcritprob}\\",
     r"\toprule", "Problem & " + " & ".join(LABEL[c] for c in cols) + r" \\", r"\midrule", r"\endfirsthead",
     r"\toprule", "Problem & " + " & ".join(LABEL[c] for c in cols) + r" \\", r"\midrule", r"\endhead"]
allp = sorted(set().union(*[set(res[c]) for c in cols]), key=str.lower)


def cell(c, p):
    if p not in res[c]:
        return "--"
    s = f"{ni(c, p)}/{len(res[c][p])}"
    if c != "ours" and same[c].get(p):
        s = "$=$ " + s
    if ADM.get(c, {}).get(p):
        s += r"$^{\ast}$"
    return s


for p in [q for q in allp if q in common]:
    L.append(f"{short(p)} & " + " & ".join(cell(c, p) for c in cols) + r" \\")
rest = [q for q in allp if q not in common]
if rest:
    L.append(r"\midrule")
    for p in rest:
        L.append(f"{short(p)} & " + " & ".join(cell(c, p) for c in cols) + r" \\")
L += [r"\bottomrule", r"\end{longtable}"]
(TAB / "tableS_identif_criteria_problems.tex").write_text("\n".join(L) + "\n", encoding="utf-8")

print(f"common problems: {len(common)}")
for c in CRIT:
    r = summary["criteria"][c]
    extra = "" if c == "ours" else f"  P(all id)={fp(r['mcnemar_all_identifiable']['p'])} P(both)={fp(r['mcnemar_both']['p'])} Holm(both)={fp(r['mcnemar_both'].get('p_holm', -1))}"
    print(f"{c:7s} id {r['identifiable']}/{r['selected']}  allid {r['all_identifiable']}/{r['problems']}  adm {r['admissible_5']}  both {r['identifiable_and_admissible']}  cpu {r['cpu_h']} h{extra}")
