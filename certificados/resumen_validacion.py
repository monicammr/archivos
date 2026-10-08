#!/usr/bin/env python3
"""Resumen de la validación externa (validacion_externa.py) → RESUMEN_VALIDACION.md y CSV."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
D = HERE / "resultados" / "validacion_externa"
EMAX = float(np.sqrt(1 - 0.9 ** 2))


def f(x, d=2):
    return "—" if x is None or not np.isfinite(x) else f"{x:.{d}f}"


def main():
    rs = [json.loads(p.read_text()) for p in sorted(D.glob("*.json"))]
    pd.DataFrame(rs).to_csv(D / "resumen_validacion.csv", index=False)
    ok = [r for r in rs if "error" not in r and "no_evaluable" not in r]
    ne = [r for r in rs if "no_evaluable" in r]
    L = ["# Validación externa del modelo reducido (comentario 5)", "",
         "Ajuste con una parte de los experimentos y predicción de los que NO se usaron "
         "(condiciones nuevas, o tiempos posteriores si sólo hay una condición). "
         "χ²/n = media de los residuos estandarizados al cuadrado en el conjunto de prueba "
         "(≈ 1: error del tamaño del ruido experimental). e_pred = error relativo de "
         "predicción frente a la verdad (sólo en el experimento sintético; umbral 0,436).", "",
         "## A. Datos reales", "",
         "| Sistema | División | |S| / p | χ²/n prueba reducido | χ²/n prueba completo | "
         "χ²/n prueba θ₀ (vio todos los datos) |", "|---|---|---|---|---|---|"]
    for r in ok:
        L.append(f"| {r['sistema']} | {r['division']} | {r['|S|']} / {r['p_y']} | "
                 f"{f(r.get('A_chi2_test_red'))} | {f(r.get('A_chi2_test_full'))} | "
                 f"{f(r.get('A_chi2_test_theta0'))} |")
    L += ["", "## B. Sintético con ruido (verdad θ* = θ₀ ± 20 %, ruido N(0, σ²))", "",
          "| Sistema | e_pred reducido | e_pred completo | χ²/n prueba reducido | "
          "χ²/n prueba completo | Reducido ≤ 0,436 |", "|---|---|---|---|---|---|"]
    n_ok = n_mejor = n_comp = 0
    for r in ok:
        er, ef = r.get("B_epred_red"), r.get("B_epred_full")
        pasa = er is not None and np.isfinite(er) and er <= EMAX
        n_ok += bool(pasa)
        if ef is not None and np.isfinite(ef) and er is not None and np.isfinite(er):
            n_comp += 1
            n_mejor += er <= ef
        L.append(f"| {r['sistema']} | {f(er)} | {f(ef)} | {f(r.get('B_chi2_test_red'))} | "
                 f"{f(r.get('B_chi2_test_full'))} | {'sí' if pasa else 'no'} |")
    a_comp = [(r["A_chi2_test_red"], r["A_chi2_test_full"]) for r in ok
              if np.isfinite(r.get("A_chi2_test_red", np.nan))
              and np.isfinite(r.get("A_chi2_test_full", np.nan))]
    a_mejor = sum(1 for x, y in a_comp if x <= y)
    L += ["", "## Resumen", "",
          f"* Sistemas evaluados: {len(ok)}; no evaluables: {len(ne)}; errores: "
          f"{len(rs) - len(ok) - len(ne)}.",
          f"* Datos reales: el reducido predice igual o mejor que el completo reajustado en "
          f"{a_mejor} de {len(a_comp)} sistemas.",
          f"* Sintético: e_pred del reducido ≤ 0,436 en {n_ok} de {len(ok)}; reducido igual o "
          f"mejor que el completo en {n_mejor} de {n_comp}."]
    if ne:
        L += ["", "No evaluables:", ""] + [f"* {r['sistema']}: {r['no_evaluable']}" for r in ne]
    (D / "RESUMEN_VALIDACION.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
