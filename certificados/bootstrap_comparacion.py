#!/usr/bin/env python3
"""
Estadística por sistema (sin suponer independencia entre semillas) de la comparación de métodos.

1. Sintético (20 semillas): diferencia de la tasa de acierto (e_pred ≤ τ) entre nuestro método y
   cada uno de los otros, con intervalo de confianza del 95 % por BOOTSTRAP POR GRUPOS: se
   remuestrean sistemas completos (con todas sus semillas), B = 10 000 réplicas, semilla 0.
   Sólo casos comunes a los cinco métodos y con señal (χ²/n de θ₀ ≥ 2). p bilateral = 2·min de
   la fracción de réplicas con diferencia ≤ 0 o ≥ 0.
2. Admisibilidad (un valor por sistema): prueba exacta de McNemar sobre los sistemas en que sólo
   uno de los dos subconjuntos es admisible, para cada nivel de perturbación disponible
   (control_admis_sint = ±5 %, control_admis_sint_nivel020 = ±20 %, …).

Uso:   python bootstrap_comparacion.py [carpeta_resultados]
Salida: <carpeta_resultados>/comparacion_metodos/6_bootstrap_y_mcnemar.md
"""
import sys, json, glob, math, collections
from pathlib import Path
import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
R = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "resultados"
OUT = R / "comparacion_metodos"
OUT.mkdir(parents=True, exist_ok=True)
TAU = math.sqrt(1 - 0.9 ** 2)
M = ["ours", "qr", "brun", "morris", "perfil"]
NOM = {"ours": "Nuestro método", "qr": "QR pivotado", "brun": "Brun", "morris": "Morris",
       "perfil": "Verosimilitud perfilada"}
B, SEMILLA = 10000, 0
ok = lambda x: isinstance(x, (int, float)) and math.isfinite(x)

# ── 1. sintético ──────────────────────────────────────────────────────────────────
S = collections.defaultdict(lambda: collections.defaultdict(dict))
for f in glob.glob(str(R / "control_admis_sint" / "*__sint_*.json")):
    d = json.loads(Path(f).read_text(encoding="utf-8"))
    if ok(d.get("B_epred_red")):
        S[d["sistema"]][d["metodo"]][d["semilla"]] = d
for f in glob.glob(str(R / "sintetico_semillas" / "*" / "s*.json")):
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
for carpeta in sorted(glob.glob(str(R / "control_admis_sint*"))):
    nombre = Path(carpeta).name
    if nombre.endswith("_v1"):
        continue
    nivel = "±5 %" if nombre == "control_admis_sint" else f"±{int(nombre[-3:])} %"
    adm = collections.defaultdict(dict)
    for f in glob.glob(carpeta + "/*__adm.json"):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
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
