#!/usr/bin/env python3
"""Resumen de la validación externa (validacion_externa.py) → RESUMEN_VALIDACION.md y CSV."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
import sys
D = HERE / "resultados" / ("validacion_externa_bio" if "--bio" in sys.argv else "validacion_externa")
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
    # Experimento B: la señal (efecto de la perturbación ±20 % en las salidas de prueba) frente al
    # ruido. Como χ²(θ₀) ≈ 1 + ‖z* − ẑ(θ₀)‖²/n, si χ²(θ₀) < 2 la señal es menor que el ruido y
    # e_pred (relativo a la señal) no es informativo: se evalúa entonces si el reducido predice
    # al nivel del ruido (χ²/n ≤ 2).
    snr_ok = [r for r in ok if r.get("B_chi2_test_theta0", 0) >= 2]
    snr_bajo = [r for r in ok if r.get("B_chi2_test_theta0", 0) < 2 and "B_chi2_test_red" in r]
    n_ep = sum(1 for r in snr_ok if np.isfinite(r.get("B_epred_red", np.nan))
               and r["B_epred_red"] <= EMAX)
    n_ep_mejor = sum(1 for r in snr_ok if np.isfinite(r.get("B_epred_full", np.nan))
                     and r.get("B_epred_red", np.inf) <= r["B_epred_full"])
    n_ep_comp = sum(1 for r in snr_ok if np.isfinite(r.get("B_epred_full", np.nan)))
    n_ruido = sum(1 for r in snr_bajo if r["B_chi2_test_red"] <= 2)
    # datos reales relativos al ajuste publicado (θ₀ usó todos los datos)
    a_rel = [(r["A_chi2_test_red"], r["A_chi2_test_theta0"]) for r in ok
             if np.isfinite(r.get("A_chi2_test_red", np.nan)) and r.get("A_chi2_test_theta0", 0) > 0]
    n_rel = sum(1 for x, y in a_rel if x <= 2 * y)
    L += ["", "## Resumen", "",
          f"* Sistemas evaluados: {len(ok)}; no evaluables: {len(ne)}; errores: "
          f"{len(rs) - len(ok) - len(ne)}.",
          f"* Datos reales: el reducido predice igual o mejor que el completo reajustado en "
          f"{a_mejor} de {len(a_comp)} sistemas.",
          f"* Sintético: e_pred del reducido ≤ 0,436 en {n_ok} de {len(ok)}; reducido igual o "
          f"mejor que el completo en {n_mejor} de {n_comp}.",
          f"* Sintético, sistemas donde la señal supera al ruido (χ²(θ₀) ≥ 2): {len(snr_ok)}; "
          f"e_pred ≤ 0,436 en {n_ep}; reducido igual o mejor que el completo en {n_ep_mejor} de "
          f"{n_ep_comp}.",
          f"* Sintético, señal menor que el ruido: {len(snr_bajo)}; el reducido predice al nivel "
          f"del ruido (χ²/n ≤ 2) en {n_ruido} (e_pred no informativo en estos casos).",
          f"* Datos reales frente al ajuste publicado θ₀ (que usó todos los datos): χ²/n del "
          f"reducido ≤ 2·χ²/n(θ₀) en {n_rel} de {len(a_rel)}. En Okuonghae, Oliveira y Smith "
          f"incluso θ₀ tiene χ²/n ≫ 1: los σ del benchmark no corresponden a la dispersión de "
          f"los datos."]
    if ne:
        L += ["", "No evaluables:", ""] + [f"* {r['sistema']}: {r['no_evaluable']}" for r in ne]
    (D / "RESUMEN_VALIDACION.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
