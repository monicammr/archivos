#!/usr/bin/env python3
"""LaTeX tables of the paper, generated from the stored results.

  tables/table1.tex   per-problem results (Table 1, main text)
  tables/tableS1.tex  selected parameters of each problem (Supplementary Table S1)

Sources: results/selection, results/external_validation, results/robustness; the numbers of
measurements come from results/simulator_check (one entry per row of measurements.tsv).
"""
import numpy as np

import json
import pandas as pd

from common import RESULTS, TAB as OUT, efit_final, fmt_efit, load, load_validation, measurements

SEL, VAL, PAT = load("selection"), load_validation(), load("robustness")
LIN = {"Alkan_SciSignal2018", "Bachmann_MSB2011", "Beer_MolBioSystems2014", "Chen_MSB2009",
       "Isensee_JCB2018", "Lang_PLOSComputBiol2024", "Lucarelli_CellSystems2018", "Raimundez_PCB2020"}
meas = measurements()


def tex(s):
    return s.replace("_", r"\_")


def chi(x):
    if x is None or not np.isfinite(x):
        return "--"
    if x < 0.01:
        return r"$<$0.01"
    if x < 100:
        return f"{x:.2f}"
    if x < 1e4:
        return f"{x:,.0f}".replace(",", "{,}")
    e = int(np.floor(np.log10(x)))
    return f"{x / 10 ** e:.1f}e{e}"


def identif():
    """Per problem: (identifiable by the profiles, Lean hypotheses hold, selected parameters), from
    results/identifiability (the same sources as identifiability_table.py)."""
    R = RESULTS / "identifiability"
    cert = pd.concat([pd.read_csv(f) for f in sorted(R.glob("certificado*.csv"))], ignore_index=True)
    cert = cert[cert["error"].isna()] if "error" in cert else cert
    cert = cert.drop_duplicates(["sistema", "parametro"], keep="last").set_index(["sistema", "parametro"])
    out = {}
    for f in sorted((R / "profiles").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        s = d["sistema"]
        ni = sum(p["clase"] == "identificable" for p in d["perfiles"])
        lc = sum(bool(cert.loc[(s, p["parametro"])].get("certificado_local", False))
                 for p in d["perfiles"] if (s, p["parametro"]) in cert.index)
        out[s] = (ni, lc, len(d["perfiles"]))
    return out


def table1():
    IDF = identif()
    L = [r"\begin{tabular}{@{}lrrrrcrrcccc@{}}", r"\toprule",
         r"System & $p$ & $m$ & $|\Theta_C|$ & $|S|$ & Stage & $e_{\mathrm{rel}}$ & $e_{\mathrm{fit}}$ & Level & Pattern & Ident. & Test $\chi^2/n$ \\",
         r" & & & & & & (\%) & (\%) & & & (Lean) & red. / full \\",
         r"\midrule"]
    for name, d in sorted(SEL.items(), key=lambda kv: kv[0].lower()):
        short = name.split("_")[0]
        m = meas.get(name, ("--", "--"))[0]
        c = len(d.get("calibracion", []))
        k = len(d["S"])
        st = "1" if d.get("etapa") == "Stage 1" else "2"
        er = d.get("erel_med", np.nan); ef, _ = efit_final(name, d)
        efs = fmt_efit(ef) + (r"$^{\ast}$" if name in LIN else "")
        if not d["admisible"]:
            efs = r"\textit{" + efs + "}"
        if name == "Crauste_CellSystems2017":     # no solution for changes of +-1 % (results/crauste_blowup.json)
            efs = r"\textit{n.d.}$^{\dagger}$"; er = np.nan
        pt = PAT.get(name, {}).get("patron", "--") if d["admisible"] else "--"
        v = VAL.get(name, {})
        r, f = v.get("A_chi2_test_red"), v.get("A_chi2_test_full")
        vs = "--" if r is None else f"{chi(r)} / {chi(f)}"
        lv = nivel(d)
        idf = IDF.get(name)
        ids = "--" if idf is None or not d["admisible"] else f"{idf[0]}/{idf[2]} ({idf[1]})"
        ks = "--" if name == "Crauste_CellSystems2017" else str(k)   # no admissible subset
        L.append(f"{tex(short)} & {d['p']} & {m} & {c} & {ks} & {st} & {'--' if not np.isfinite(er) else f'{100 * er:.0f}'} & {efs} & {lv or '--'} & {pt} & {ids} & {vs} \\\\")
    L += [r"\bottomrule", r"\end{tabular}"]
    (OUT / "table1.tex").write_text("\n".join(L) + "\n")


def nivel(d):
    """Level of guarantee of an admissible subset: 1 = e_fit; 2 = also cos Delta >= c; 3 = also R_var >= 0.89."""
    if not d.get("admisible"):
        return None
    lv = 1
    if d["cos_med"] >= 0.9:
        lv = 2
        if d["Rvar_%"] >= 89:
            lv = 3
    return lv


def tableS1():
    brk = lambda t: tex(t).replace(r"\_", r"\_\allowbreak{}").replace(", ", ", \\allowbreak{}")
    L = [r"\begin{longtable}{@{}>{\raggedright\arraybackslash}p{1.9cm}>{\raggedright\arraybackslash}p{3.9cm}>{\raggedright\arraybackslash}p{2.7cm}rrrrrc@{}}", r"\caption{Selected biological parameters of each benchmark problem and characteristics of the subset.}\label{tab:selected}\\", r"\toprule",
         r"System & Selected biological parameters $S$ & Removed by backward elimination & $\kappa$ & VIF & $R_{\mathrm{var}}$ (\%) & $\cos\Delta$ & $e_{\mathrm{fit}}$ (\%) & Level \\", r"\midrule",
         r"\endfirsthead", r"\toprule", r"System & Selected biological parameters $S$ & Removed by backward elimination & $\kappa$ & VIF & $R_{\mathrm{var}}$ (\%) & $\cos\Delta$ & $e_{\mathrm{fit}}$ (\%) & Level \\", r"\midrule", r"\endhead"]
    for name, d in sorted(SEL.items(), key=lambda kv: kv[0].lower()):
        lv = nivel(d)
        ef, _ = efit_final(name, d)
        efs = "n.d." if name == "Crauste_CellSystems2017" else fmt_efit(ef) + (r"$^{\ast}$" if name in LIN else "")
        L.append(f"{brk(name.split('_')[0])} & {brk(', '.join(d['S']))} & {brk(', '.join(d.get('podados', []) or ['--']))} & "
                 f"{d['kappa']:.1f} & {d['VIF']:.1f} & {d['Rvar_%']:.0f} & {d['cos_med']:.3f} & {efs} & {lv if lv else '--'} \\\\")
    L += [r"\bottomrule", r"\end{longtable}"]
    (OUT / "tableS1.tex").write_text("\n".join(L) + "\n")
    lv = [nivel(d) for d in SEL.values() if d.get("admisible")]
    print("levels of guarantee:", {k: lv.count(k) for k in (1, 2, 3)})


if __name__ == "__main__":
    table1(); tableS1()
    print("tables written to", OUT)
