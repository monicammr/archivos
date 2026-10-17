#!/usr/bin/env python3
"""
Test of the role of the calibration parameters (Supplementary Note "Admissibility with the
calibration parameters fixed"): the admissibility test at +-5 % with the standard scenarios (all
parameters perturbed; results/criteria_tests_fixedscen/) and with the calibration parameters kept
at theta0 (results/criteria_tests_calfixed/, written by scripts/run_test_calibration_fixed.sh), for
the 14 problems with calibration parameters.

Writes tables/tableS_calfixed.tex (per problem) and tables/tableS_calfixed_criteria.tex (per
criterion) in PAPER_DIR and prints the numbers quoted in the text.
"""
import json, glob
from pathlib import Path
import numpy as np

from common import RESULTS as R, TAB

STD, CAL = R / "criteria_tests_fixedscen", R / "criteria_tests_calfixed"
TAU = float(np.sqrt(1 - 0.81))
SUM = json.loads((R / "calibration_fixed_summary.json").read_text(encoding="utf-8"))


def load(folder):
    A = {}
    for f in glob.glob(str(folder / "*__adm.json")):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        if "eajuste_med" in d:
            A[(d["sistema"], d["metodo"])] = d
    return A


S, C = load(STD), load(CAL)
probs = sorted(SUM["problems"], key=str.lower)
short = lambda s: s.split("_")[0]


def ef(A, p, m):
    d = A.get((p, m))
    return None if d is None else min(d["eajuste_med"], d["erel_med"])


def cell(x):
    if x is None:
        return "--"
    v = f"{100 * x:.1f}"
    return f"\\textbf{{{v}}}" if x <= TAU else v


def nrand(A, p):
    v = [A[(p, f"rand{i}")]["admisible"] for i in range(20) if (p, f"rand{i}") in A]
    return f"{sum(v)}/{len(v)}" if v else "--"


rows = []
for p in probs:
    sh = SUM["problems"][p]["share_calibration"]
    ncal = C[(p, "ours")]["n_calibracion"]
    rows.append(f"{short(p)} & {ncal} & {100 * sh:.0f} & {cell(ef(S, p, 'ours'))} & {cell(ef(C, p, 'ours'))} & "
                f"{cell(ef(S, p, 'empty'))} & {cell(ef(C, p, 'empty'))} & {nrand(S, p)} & {nrand(C, p)} \\\\")
T1 = [r"\begin{longtable}{@{}lrrrrrrrr@{}}",
      r"\caption{Admissibility at $\pm$5\% with the standard scenarios (Std.: all parameters perturbed) and with the calibration parameters kept at $\theta_0$ (Fixed: only the biological parameters perturbed, with the same biological perturbations), for the 14 problems with calibration parameters. $|\Theta_C|$: calibration parameters; Share: median over the standard scenarios of the fraction of $\|\Delta y_{\mathrm{full}}\|^2$ produced by the calibration parameters alone (\%); our subset and calibration only ($k=0$, without the rule $|S|\ge2$): median $e_{\mathrm{fit}}$ over the 15 scenarios (\%; bold, admissible, $\le\tau_e=43.6\%$; first order in Alkan, Bachmann, Isensee and Raimundez, as for every criterion); random: admissible draws of the 20 random $k$-subsets.}\label{tab:calfixed}\\",
      r"\toprule",
      r" & & & \multicolumn{2}{c}{Our subset} & \multicolumn{2}{c}{Calibration only} & \multicolumn{2}{c}{Random} \\",
      r"\cmidrule(lr){4-5}\cmidrule(lr){6-7}\cmidrule(lr){8-9}",
      r"Problem & $|\Theta_C|$ & Share & Std. & Fixed & Std. & Fixed & Std. & Fixed \\",
      r"\midrule", r"\endfirsthead",
      r"\toprule", r"Problem & $|\Theta_C|$ & Share & Std. & Fixed & Std. & Fixed & Std. & Fixed \\", r"\midrule", r"\endhead"]
T1 += rows + [r"\bottomrule", r"\end{longtable}"]
(TAB / "tableS_calfixed.tex").write_text("\n".join(T1) + "\n", encoding="utf-8")

nom = {"ours": "Our method (all outputs)", "train": "Our method (training outputs)", "brun": "Brun",
       "morris": "Morris", "perfil": "Profile likelihood", "qr_gks": "Pivoted QR", "empty": "Calibration only ($k=0$)"}
cs, cc = SUM["counts"]["standard"], SUM["counts"]["calfixed"]
rows = [f"{nom[m]} & {cs[m]['admissible']}/{cs[m]['n']} & {cc[m]['admissible']}/{cc[m]['n']} \\\\"
        for m in ["ours", "train", "brun", "morris", "perfil", "qr_gks", "empty"]]
rand_s = sum(int(nrand(S, p).split("/")[0]) for p in probs); rand_c = sum(int(nrand(C, p).split("/")[0]) for p in probs)
rows.append(f"Random $k$-subsets (all draws) & {rand_s}/{20 * len(probs)} & {rand_c}/{20 * len(probs)} \\\\")
T2 = [r"\begin{table}[H]", r"\centering\small",
      r"\caption{Admissible subsets at $\pm$5\% in the 14 problems with calibration parameters, with the standard scenarios and with the calibration parameters kept at $\theta_0$ (profile likelihood: 13 problems; no subset for Raimundez).}\label{tab:calfixedcrit}",
      r"\begin{tabular}{@{}lcc@{}}", r"\toprule", r"Subsets & Standard & Calibration fixed \\", r"\midrule"]
T2 += rows + [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
(TAB / "tableS_calfixed_criteria.tex").write_text("\n".join(T2) + "\n", encoding="utf-8")

shares = [SUM["problems"][p]["share_calibration"] for p in probs]
print("problems", len(probs), "| share median %.2f range %.2f-%.2f" % (np.median(shares), min(shares), max(shares)))
print("ours", cs["ours"], "->", cc["ours"], "| calibration only", cs["empty"], "->", cc["empty"])
print("random admissible draws", rand_s, "->", rand_c, "of", 20 * len(probs))
print("discriminating problems std", cs["discriminating_problems"], "| fixed", cc["discriminating_problems"])
print("processor hours", SUM["processor_hours"])
print("ours e_fit increase (pp): median %.1f" % np.median([100 * (ef(C, p, "ours") - ef(S, p, "ours")) for p in probs]))
