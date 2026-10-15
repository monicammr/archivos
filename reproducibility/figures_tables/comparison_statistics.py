#!/usr/bin/env python3
"""
Statistics over problems for the comparison of criteria (Methods, "Statistics"):
  * synthetic experiment (20 seeds): difference in the fraction of cases with e_pred <= tau_e between
    our method and each criterion, with a 95 % CI from resampling whole problems with all their seeds
    (10,000 replicates, seed 0); cases common to the five criteria with signal;
  * admissibility (one outcome per problem): exact McNemar test at each perturbation level available
    (results/criteria_tests = +-5 %, results/criteria_tests_20pc = +-20 %).
Output: output/comparison/6_bootstrap_y_mcnemar.md
Usage: python comparison_statistics.py
"""
import sys, json, glob, math, collections
from pathlib import Path
import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
from common import RESULTS as R, FIG, TAB, OUT as _OUT, EXCLUDE_ADMISSIBILITY
OUT = _OUT / "comparison"
OUT.mkdir(parents=True, exist_ok=True)
TAU = math.sqrt(1 - 0.9 ** 2)
M = ["ours", "qr", "brun", "morris", "perfil"]
NOM = {"ours": "Nuestro método", "qr": "QR pivotado", "brun": "Brun", "morris": "Morris",
       "perfil": "Verosimilitud perfilada"}
B, SEMILLA = 10000, 0
ok = lambda x: isinstance(x, (int, float)) and math.isfinite(x)

# ── 1. sintético ──────────────────────────────────────────────────────────────────
S = collections.defaultdict(lambda: collections.defaultdict(dict))
for f in glob.glob(str(R / "criteria_tests" / "*__sint_*.json")):
    d = json.loads(Path(f).read_text(encoding="utf-8"))
    if ok(d.get("B_epred_red")):
        S[d["sistema"]][d["metodo"]][d["semilla"]] = d
for f in glob.glob(str(R / "synthetic_seeds" / "*" / "s*.json")):
    d = json.loads(Path(f).read_text(encoding="utf-8"))
    if ok(d.get("B_epred_red")):
        S[d["sistema"]]["ours"][d["semilla"]] = d
por_sis = collections.defaultdict(list)          # sistema -> lista de {método: acierto}
for s in S:
    for k in range(42, 62):
        ds = [S[s][m].get(k) for m in M]
        if all(ds) and ds[0]["B_chi2_test_theta0"] >= 2:
            por_sis[s].append({m: d["B_epred_red"] <= TAU for m, d in zip(M, ds)})
sis = sorted(por_sis)
rng = np.random.default_rng(SEMILLA)
# matriz de aciertos y número de casos por sistema
A = {m: np.array([sum(c[m] for c in por_sis[s]) for s in sis], float) for m in M}
N = np.array([len(por_sis[s]) for s in sis], float)
idx = rng.integers(0, len(sis), size=(B, len(sis)))
L = ["# Estadística por sistema de la comparación de métodos", "",
     "## Sintético: diferencia de la tasa de acierto (bootstrap por sistemas)", "",
     f"{int(N.sum())} casos comunes con señal en {len(sis)} sistemas; se remuestrean sistemas completos "
     f"(B = {B}). Diferencia > 0: nuestro método acierta más.", "",
     "| Nuestro método contra | Tasa nuestra | Tasa del otro | Diferencia | IC 95 % | p (bootstrap) |",
     "|---|---|---|---|---|---|"]
for m in M[1:]:
    tasa = lambda a: a[idx].sum(1) / N[idx].sum(1)
    dif = tasa(A["ours"]) - tasa(A[m])
    obs = A["ours"].sum() / N.sum() - A[m].sum() / N.sum()
    lo, hi = np.percentile(dif, [2.5, 97.5])
    p = min(1.0, 2 * min((dif <= 0).mean(), (dif >= 0).mean()))
    L.append(f"| {NOM[m]} | {A['ours'].sum() / N.sum():.0%} | {A[m].sum() / N.sum():.0%} | "
             f"{obs:+.1%} | {lo:+.1%} a {hi:+.1%} | {max(p, 1 / B):.2g} |")

# ── 2. admisibilidad: McNemar exacto por sistema ─────────────────────────────────
for carpeta in sorted(glob.glob(str(R / "criteria_tests*"))):
    nombre = Path(carpeta).name
    nivel = "±5 %" if nombre == "criteria_tests" else "±" + nombre.split("_")[-1].replace("pc", "") + " %"
    adm = collections.defaultdict(dict)
    for f in glob.glob(carpeta + "/*__adm.json"):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        if d.get("sistema") in EXCLUDE_ADMISSIBILITY:
            continue
        if "admisible" in d:
            adm[d["sistema"]][d["metodo"]] = bool(d["admisible"])
    if not adm:
        continue
    L += ["", f"## Admisibilidad a {nivel} (McNemar exacto por sistema)", "",
          "| Método | Admisibles |", "|---|---|"]
    for m in M:
        v = [a[m] for a in adm.values() if m in a]
        L.append(f"| {NOM[m]} | {sum(v)} de {len(v)} |")
    L += ["", "| Nuestro método contra | Sistemas comparados | Sólo el nuestro admisible | Sólo el otro | p |",
          "|---|---|---|---|---|"]
    for m in M[1:]:
        pares = [(a["ours"], a[m]) for a in adm.values() if "ours" in a and m in a]
        b = sum(o and not x for o, x in pares)
        c = sum(x and not o for o, x in pares)
        p = stats.binomtest(b, b + c).pvalue if b + c else float("nan")
        L.append(f"| {NOM[m]} | {len(pares)} | {b} | {c} | {p:.2g} |")
(OUT / "6_bootstrap_y_mcnemar.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
