#!/usr/bin/env python3
"""LaTeX tables for the Scientific Reports manuscript, generated from certificados/resultados.

  tables/table1.tex   per-system benchmark summary (main text)
  tables/tableS1.tex  selected parameters per system (Supplementary Information)

Measurement and condition counts are read from respuesta_revisores/tables_en.md (Table A).
"""
import json, re
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RES = ROOT / "certificados" / "resultados"
OUT = HERE / "tables"
OUT.mkdir(exist_ok=True)
TAU = float(np.sqrt(1 - 0.9 ** 2))


def load(d):
    return {f.stem: json.loads(f.read_text()) for f in sorted((RES / d).glob("*.json"))}


SEL, VAL, PAT = load("reclasificacion_salidas_bio_poda"), load("validacion_externa_bio"), load("patrones")
LIN = {"Alkan_SciSignal2018", "Bachmann_MSB2011", "Beer_MolBioSystems2014", "Chen_MSB2009",
       "Isensee_JCB2018", "Lang_PLOSComputBiol2024", "Lucarelli_CellSystems2018", "Raimundez_PCB2020"}

meas = {}
for line in (ROOT / "respuesta_revisores" / "tables_en.md").read_text().splitlines():
    c = [x.strip() for x in line.split("|")]
    if len(c) > 12 and c[2].isdigit() and c[3].isdigit() and c[4].isdigit():
        meas[c[1]] = (int(c[3]), int(c[4]))


def tex(s):
    return s.replace("_", r"\_")


def chi(x):
    if x is None or not np.isfinite(x):
        return "--"
    if x < 0.01:
        return r"$<$0.01"
    return f"{x:.2f}" if x < 100 else f"{x:.3g}" if x < 1e4 else f"{x:.2e}".replace("e+0", "e").replace("e+", "e")


def table1():
    L = [r"\begin{tabular}{@{}lrrrrcrrcc@{}}", r"\toprule",
         r"System & $p$ & $m$ & $|\Theta_C|$ & $|S|$ & Stage & $e_{\mathrm{rel}}$ & $e_{\mathrm{fit}}$ & Pattern & Test $\chi^2/n$ \\",
         r" & & & & & & (\%) & (\%) & & reduced / full \\",
         r"\midrule"]
    for name, d in sorted(SEL.items(), key=lambda kv: kv[0].lower()):
        short = name.split("_")[0]
        m = meas.get(short, ("--", "--"))[0]
        c = len(d.get("calibracion", []))
        k = len(d["S"])
        st = "1" if d.get("etapa") == "Stage 1" else "2"
        er = d.get("erel_med", np.nan); ef = d.get("eajuste_med", np.nan)
        efs = f"{100 * ef:.1f}" + (r"$^{\ast}$" if name in LIN else "")
        if not d["admisible"]:
            efs = r"\textit{" + efs + "}"
        if name == "Crauste_CellSystems2017":     # sin solución para perturbaciones de ±1 %
            efs = r"\textit{n.d.}$^{\dagger}$"; er = np.nan
        pt = PAT.get(name, {}).get("patron", "--") if d["admisible"] else "--"
        v = VAL.get(name, {})
        r, f = v.get("A_chi2_test_red"), v.get("A_chi2_test_full")
        vs = "--" if r is None else f"{chi(r)} / {chi(f)}"
        L.append(f"{tex(short)} & {d['p']} & {m} & {c} & {k} & {st} & {'--' if not np.isfinite(er) else f'{100 * er:.0f}'} & {efs} & {pt} & {vs} \\\\")
    L += [r"\botrule", r"\end{tabular}"]
    (OUT / "table1.tex").write_text("\n".join(L) + "\n")


def tableS1():
    brk = lambda t: tex(t).replace(r"\_", r"\_\allowbreak{}").replace(", ", ", \\allowbreak{}")
    L = [r"\begin{longtable}{@{}>{\raggedright\arraybackslash}p{3.3cm}>{\raggedright\arraybackslash}p{6.3cm}>{\raggedright\arraybackslash}p{5.0cm}@{}}", r"\toprule",
         r"System & Selected biological parameters $S$ & Removed by backward elimination \\", r"\midrule",
         r"\endhead"]
    for name, d in sorted(SEL.items(), key=lambda kv: kv[0].lower()):
        L.append(f"{brk(name.split('_')[0])} & {brk(', '.join(d['S']))} & {brk(', '.join(d.get('podados', []) or ['--']))} \\\\")
    L += [r"\bottomrule", r"\end{longtable}"]
    (OUT / "tableS1.tex").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    table1(); tableS1()
    print("tables written to", OUT)
