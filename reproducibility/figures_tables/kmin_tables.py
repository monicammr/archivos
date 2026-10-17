#!/usr/bin/env python3
"""
Test of the minimum subset size k_min = 2 (Supplementary Note "Minimum subset size"): table of the
best single parameter against the pair selected by our method, on the 15 problems in which one
parameter already reaches the admissibility threshold, from results/kmin_comparison.json (written
by analysis/compare_single_vs_pair.py after scripts/run_test_kmin.sh).

Writes tables/tableS_kmin.tex (in PAPER_DIR) and prints the summary quoted in the text.
"""
import json
import statistics as st

from scipy.stats import binomtest

from common import RESULTS as R, TAB

K = json.loads((R / "kmin_comparison.json").read_text())
D = K["per_problem"]
probs = sorted(D, key=str.lower)
tex = lambda s: s.replace("_", r"\_\allowbreak{}")
pc = lambda x: "--" if x is None else f"{100 * x:.0f}"


def sign(a, b):
    be, wo = sum(x > y for x, y in zip(a, b)), sum(x < y for x, y in zip(a, b))
    return be, wo, (binomtest(be, be + wo, 0.5).pvalue if be + wo else 1.0)


L = [r"\begin{longtable}{@{}>{\raggedright\arraybackslash}p{1.7cm}>{\raggedright\arraybackslash}p{2.6cm}>{\raggedright\arraybackslash}p{3.0cm}ccccc@{}}",
     r"\caption{Best single parameter against the pair selected by our method, in the 15 problems in which one parameter already reaches the admissibility threshold at $\pm$5\%. Pass rate: percentage of the scenarios, over all perturbation sizes from $\pm$1\% to $\pm$50\%, with $e_{\mathrm{fit}}\le\tau_e$, with paired (P) and independent (I) directions; $e_{\mathrm{fit}}$ at $\pm$50\%: median over the 15 scenarios with independent directions (\%); $\pm$20\%: admissible at $\pm$20\%; Synthetic: cases with signal in which $e_{\mathrm{pred}}\le\tau_e$ over the 20 seeds (identifiability is reported in the text). Each cell gives pair / single.}\label{tab:kmin}\\",
     r"\toprule", r"Problem & Single parameter & Pair & Pass rate P (\%) & Pass rate I (\%) & $e_{\mathrm{fit}}$ $\pm$50\% & $\pm$20\% & Synthetic \\", r"\midrule", r"\endfirsthead",
     r"\toprule", r"Problem & Single parameter & Pair & Pass rate P (\%) & Pass rate I (\%) & $e_{\mathrm{fit}}$ $\pm$50\% & $\pm$20\% & Synthetic \\", r"\midrule", r"\endhead"]
yn = lambda b: "yes" if b else "no"
for p in probs:
    r = D[p]
    sy = lambda m: "--" if not r["synthetic"][m] else f"{r['synthetic'][m][0]}/{r['synthetic'][m][1]}"
    L.append(f"{p.split('_')[0].replace('SalazarCavazos', 'Salazar-Cavazos')} & \\texttt{{{tex(r['single'])}}} & "
             + ", ".join(f"\\texttt{{{tex(x)}}}" for x in r["pair"]) + " & "
             f"{pc(r['robust_paired']['pair']['pass_rate'])} / {pc(r['robust_paired']['single']['pass_rate'])} & "
             f"{pc(r['robust_indep']['pair']['pass_rate'])} / {pc(r['robust_indep']['single']['pass_rate'])} & "
             f"{pc(r['robust_indep']['pair']['median_50'])} / {pc(r['robust_indep']['single']['median_50'])} & "
             f"{yn(r['adm20']['pair'])} / {yn(r['adm20']['single'])} & {sy('pair')} / {sy('single')} \\\\")
L += [r"\bottomrule", r"\end{longtable}"]
(TAB / "tableS_kmin.tex").write_text("\n".join(L) + "\n", encoding="utf-8")

for k in ("robust_paired", "robust_indep"):
    a = [D[p][k]["pair"]["pass_rate"] for p in probs]; b = [D[p][k]["single"]["pass_rate"] for p in probs]
    a50 = [D[p][k]["pair"]["median_50"] for p in probs]; b50 = [D[p][k]["single"]["median_50"] for p in probs]
    print(k, f"pass rate pair {100 * st.mean(a):.0f}% single {100 * st.mean(b):.0f}% sign {sign(a, b)}",
          f"e50 median pair {100 * st.median(a50):.1f}% single {100 * st.median(b50):.1f}% single larger {sign(b50, a50)}",
          "pattern A", sum(D[p][k]["pair"]["pattern"] == "A" for p in probs), sum(D[p][k]["single"]["pattern"] == "A" for p in probs))
print("summary", {k: v for k, v in K["summary"].items() if k in ("adm20", "synthetic", "identifiable_all")})
