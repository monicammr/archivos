#!/usr/bin/env python3
"""
Supplementary Table "Conditioning of the final subsets" (tables/tableS_conditioning.tex): kappa and VIF
of the selected sensitivity columns, centred and scaled as in the selection and scaled to unit length as
in the Lean statements, and kappa of the unit-length columns of the selected and calibration parameters
together, from results/conditioning_check.json (written by analysis/conditioning_check.py).
"""
import json

from common import RESULTS as R, TAB

D = json.loads((R / "conditioning_check.json").read_text(encoding="utf-8"))


def f(x):
    return f"{x:.2f}" if x < 1000 else f"{x:.1e}"


L = ["% generated from results/conditioning_check.json (analysis/conditioning_check.py)",
     r"\begin{tabular}{@{}lrrrrrr@{}}", r"\toprule",
     r" & & \multicolumn{2}{c}{Centred, scaled} & \multicolumn{2}{c}{Unit length} & With $\Theta_C$ \\",
     r"\cmidrule(lr){3-4}\cmidrule(lr){5-6}\cmidrule(lr){7-7}",
     r"Problem & $|S|$ & $\kappa$ & VIF & $\kappa$ & VIF & $\kappa$ \\", r"\midrule"]
for d in sorted(D, key=lambda d: d["sistema"].lower()):
    L.append(f"{d['sistema'].split('_')[0]} & {len(d['S'])} & {f(d['kappa_centred'])} & {f(d['VIF_centred'])} & "
             f"{f(d['kappa_unit'])} & {f(d['VIF_unit'])} & {f(d['kappa_unit_with_calibration'])} \\\\")
L += [r"\bottomrule", r"\end{tabular}"]
(TAB / "tableS_conditioning.tex").write_text("\n".join(L) + "\n", encoding="utf-8")
print("written tableS_conditioning.tex,", len(D), "problems")
