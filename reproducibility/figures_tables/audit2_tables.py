#!/usr/bin/env python3
"""Supplementary tables of the second audit (written to PAPER_DIR/tables/):
  tableS_nonlinear.tex       nonlinear e_fit of the six first-order problems
  tableS_admis_audit2.tex    admissibility per problem at +-5 % for every criterion and null control
  tableS_synth_families.tex  synthetic success for three families of truths, CIs and Holm P
  tableS_identif_region.tex  hypotheses of the Lean identifiability theorems by region radius
Usage: PAPER_DIR=../../paper/scirep python audit2_tables.py  (after audit2_stats.py)"""
import csv
import glob
import json
from pathlib import Path

from common import RESULTS as R, TAB

J = lambda f: json.loads(Path(f).read_text(encoding="utf-8"))  # noqa: E731
ST = J(R / "audit2_stats.json")
short = lambda s: s.split("_")[0].replace("SalazarCavazos", "Salazar-Cavazos")  # noqa: E731

# ---- nonlinear
rows = ["\\begin{tabular}{@{}lrrrrr@{}}", "\\toprule",
        "Problem & $e_{\\mathrm{fit}}$ first order & $e_{\\mathrm{fit}}$ nonlinear & Valid scenarios & Pass rate & CPU time (h) \\\\", "\\midrule"]
for n, d in sorted(ST["nonlinear"].items()):
    rows.append(f"{short(n)} & {d['eajuste_med_primer_orden']:.5f} & {d['eajuste_med_nolineal']:.5f} & "
                f"{d['n_escenarios_validos']} & {100 * d['tasa_paso_nolineal']:.0f}\\% & {d['segundos_total'] / 3600:.1f} \\\\")
rows += ["\\bottomrule", "\\end{tabular}"]
(TAB / "tableS_nonlinear.tex").write_text("\n".join(rows) + "\n", encoding="utf-8")

# ---- admissibility per problem (+-5 %)
M = ["ours", "train", "brun", "morris", "perfil", "qr_gks", "qr", "empty"]
H = ["Ours", "Ours (train)", "Brun", "Morris", "Profile", "QR (GKS)", "QR (earlier)", "$k=0$", "Random"]
A = {}
for f in glob.glob(str(R / "criteria_tests_fixedscen" / "*__adm.json")):
    d = J(f)
    if "eajuste_med" not in d:
        continue
    A.setdefault(d["sistema"], {})[d["metodo"]] = d
rows = ["\\begingroup\\scriptsize\\setlength{\\tabcolsep}{2.5pt}",
        "\\begin{longtable}{@{}l" + "c" * len(H) + "@{}}",
        "\\caption{Admissibility at $\\pm$5\\% per problem with the fixed scenario set: median $e_{\\mathrm{fit}}$ of the subset of each criterion (bold, admissible; for $k=0$ without the rule $|S|\\ge2$) and, for random subsets, the number of the 20 draws that are admissible. --, not evaluated.}\\label{tab:admisaudit2}\\\\",
        "\\toprule", "Problem & " + " & ".join(H) + " \\\\", "\\midrule", "\\endfirsthead",
        "\\toprule", "Problem & " + " & ".join(H) + " \\\\", "\\midrule", "\\endhead"]
for s in sorted(A):
    cells = []
    for m in M:
        d = A[s].get(m)
        if not d:
            cells.append("--"); continue
        ok = d.get("admisible_sin_kmin" if m == "empty" else "admisible")
        v = f"{d['eajuste_med']:.2f}"
        cells.append(f"\\textbf{{{v}}}" if ok else v)
    rnd = [A[s].get(f"rand{i}") for i in range(20)]
    rnd = [d for d in rnd if d]
    cells.append(f"{sum(bool(d['admisible']) for d in rnd)}/{len(rnd)}" if rnd else "--")
    rows.append(short(s) + " & " + " & ".join(cells) + " \\\\")
rows += ["\\bottomrule", "\\end{longtable}", "\\endgroup"]
(TAB / "tableS_admis_audit2.tex").write_text("\n".join(rows) + "\n", encoding="utf-8")

# ---- synthetic families
def sg(x):
    """Signed integer percentage without a negative zero."""
    v = int(round(x))
    return "0" if v == 0 else f"{v:+d}"


nom = {"ours": "Our method (all outputs)", "train": "Our method (training outputs)", "brun": "Brun",
       "morris": "Morris", "perfil": "Profile likelihood", "qr_gks": "Pivoted QR (GKS)", "qr": "Pivoted QR (earlier)"}
fam = {"uniforme": "Uniform $\\pm$20\\%", "loguniforme": "Log-uniform", "dispersa": "Sparse"}
rows = ["\\begin{tabular}{@{}llrrl@{}}", "\\toprule",
        "Family & Criterion & Rate & Difference (95\\% CI) & Holm $P$ \\\\", "\\midrule"]
for fk, fl in fam.items():
    for ref in ("ref_ours", "ref_train"):
        S = ST["synthetic"][fk][ref]
        refm = "ours" if ref == "ref_ours" else "train"
        rows.append(f"\\multicolumn{{5}}{{@{{}}l}}{{\\emph{{{fl}, reference: {nom[refm].lower()}; {S['cases']} cases, {S['problems']} problems}}}} \\\\")
        for m in ([refm] + [x for x in ["brun", "morris", "perfil", "qr_gks", "qr", "ours"] if x != refm and x in S]):
            r = S[m]
            if m == refm:
                rows.append(f" & {nom[m]} & {100 * r['rate']:.0f}\\% & -- & -- \\\\")
            else:
                p = r.get("p_holm", r.get("p_raw"))
                ptxt = "$<0.001$" if p < 0.001 else f"{p:.3f}"
                tag = "" if "p_holm" in r else " (unadj.)"
                rows.append(f" & {nom[m]} & {100 * r['rate']:.0f}\\% & ${sg(100 * r['diff_vs_ref'])}$ "
                            f"(${sg(100 * r['diff_ci'][0])}$ to ${sg(100 * r['diff_ci'][1])}$) & {ptxt}{tag} \\\\")
    rows.append("\\midrule")
rows[-1] = "\\bottomrule"
rows.append("\\end{tabular}")
(TAB / "tableS_synth_families.tex").write_text("\n".join(rows) + "\n", encoding="utf-8")

# ---- identifiability by region
radii = [("10", ""), ("5", "_r5"), ("3", "_r3"), ("2", "_r2"), ("1.5", "_r1.5")]
cert = {}
for r, t in radii:
    for row in csv.DictReader(open(R / "identifiability" / "audit2" / f"certificado_box{t}_parametros.csv", encoding="utf-8")):
        cert.setdefault((row["sistema"], row["parametro"]), {})[r] = row["pf"] == "True"
dense = {}
for f in glob.glob(str(R / "identifiability" / "profiles_dense" / "*.json")):
    d = J(f)
    for p in d["perfiles"]:
        dense[(d["sistema"], p["parametro"])] = p["clase"]
orig = {}
for f in glob.glob(str(R / "identifiability" / "profiles" / "*.json")):
    d = J(f)
    for p in d.get("perfiles", []):
        orig[(d["sistema"], p["parametro"])] = p["clase"]
cls = {"identificable": "identifiable", "no identificable practico": "one side", "plano": "flat"}
rows = ["\\begingroup\\scriptsize\\setlength{\\tabcolsep}{3pt}",
        "\\begin{longtable}{@{}llllccccc@{}}",
        "\\caption{Identifiability of the selected parameters: profile classification with 10 and 20 points per side, and whether the hypotheses of the Lean theorems with the remainder bound on the tail (\\texttt{practically\\_identifiable\\_grad\\_tail} or \\texttt{\\_rel\\_tail}) hold over the whole region within a factor $r$ of the optimum, by sampling (512 points) and adversarial search; a numerical check of the hypotheses, not a certificate.}\\label{tab:identifregion}\\\\",
        "\\toprule", "Problem & Parameter & Profile (10) & Profile (20) & $r=10$ & 5 & 3 & 2 & 1.5 \\\\", "\\midrule", "\\endfirsthead",
        "\\toprule", "Problem & Parameter & Profile (10) & Profile (20) & $r=10$ & 5 & 3 & 2 & 1.5 \\\\", "\\midrule", "\\endhead"]
for k in sorted(orig):
    c = cert.get(k, {})
    rows.append(f"{short(k[0])} & \\texttt{{{k[1].replace('_', chr(92) + '_')}}} & {cls.get(orig[k], orig[k])} & "
                f"{cls.get(dense.get(k), dense.get(k, '--'))} & " +
                " & ".join("yes" if c.get(r) else "--" for r, _ in radii) + " \\\\")
rows += ["\\bottomrule", "\\end{longtable}", "\\endgroup"]
(TAB / "tableS_identif_region.tex").write_text("\n".join(rows) + "\n", encoding="utf-8")
print("ok")
