#!/usr/bin/env python3
"""
Conciliación de los recuentos de parámetros que aparecen en el artículo (punto C11 de la auditoría).

Para cada problema: p (parámetros estimados en PEtab) = biológicos (del modelo SBML o de la tabla de
condiciones) + calibración (escalas y offsets de las observables, re-estimados siempre) + ruido
(parámetros que sólo entran en la desviación típica σ, fijos en θ₀ porque σ se evalúa en θ₀).
Además: parámetros libres en la verosimilitud perfilada del modelo completo (entrenamiento: se
excluyen los que sólo actúan en condiciones de prueba) y en el problema reducido (S ∪ Θ_C).
Salida: paper/scirep/tables/tableS_counts.tex
"""
import json
from pathlib import Path
import numpy as np
import petab_outputs as PO

HERE = Path(__file__).resolve().parent
SEL = HERE / "resultados" / "reclasificacion_salidas_bio_poda"
PL = HERE / "resultados" / "control_perfil"
OUT = HERE.parent / "paper" / "scirep" / "tables" / "tableS_counts.tex"


def corto(s):
    return s.split("_")[0].replace("SalazarCavazos", "Salazar-Cavazos")


filas = []
for f in sorted(SEL.glob("*.json")):
    d = json.loads(f.read_text())
    n = d["sistema"]
    S = PO.PSys(n, simular=False)
    calib, inm = np.array(S.calib), np.array(S.in_model)
    bio = int((~calib & inm).sum()); cal = int((calib & inm).sum()); ruido = int((calib & ~inm).sum())
    assert bio + cal + ruido == len(S.names), n
    pl = json.loads((PL / f"{n}.json").read_text()) if (PL / f"{n}.json").exists() else {}
    if "n_bio" in pl:
        perfil = f"{pl['n_bio']} / {pl['p_libres']}"
    elif "no_evaluable" in pl:
        perfil = "n.e."
    else:
        perfil = "--"
    k = len(d.get("S", [])) if d.get("admisible") else 0
    red = f"{k} + {cal}" if d.get("admisible") else "--"
    filas.append([corto(n), str(len(S.names)), str(bio), str(cal), str(ruido), perfil, red])

L = [r"\begin{longtable}{@{}lrrrrcc@{}}",
     r"\caption{Parameter counts of every problem. $p$: parameters estimated in the PEtab problem (Table~1 of the main text), split into biological parameters (of the SBML model or of the condition table; candidates for selection), calibration parameters $\Theta_C$ (scalings and offsets of the observables, always re-estimated) and noise parameters (they enter only the standard deviation $\sigma_i$, which is evaluated at $\theta_0$ and kept fixed). Full-model profile: biological / free parameters in the profile likelihood of the full model on the training data, which excludes the parameters that act only in test conditions (so the numbers can be smaller than those of the PEtab problem); n.e., not evaluated (more than 60 free parameters or no training/test split). Reduced problem: free parameters in the reduced problem, $|S|+|\Theta_C|$.}\label{tab:counts}\\",
     r"\toprule",
     r"Problem & $p$ & Biological & Calibration & Noise & Full-model profile & Reduced problem \\",
     r"\midrule", r"\endfirsthead",
     r"\toprule",
     r"Problem & $p$ & Biological & Calibration & Noise & Full-model profile & Reduced problem \\",
     r"\midrule", r"\endhead"]
L += [" & ".join(r) + r" \\" for r in filas]
L += [r"\bottomrule", r"\end{longtable}"]
OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
print(len(filas), "problemas")
