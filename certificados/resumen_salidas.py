#!/usr/bin/env python3
"""Comparación de la reclasificación sobre ESTADOS (v3) y sobre SALIDAS MEDIDAS (v3 --salidas).

Lee resultados/reclasificacion_v3/*.json y resultados/reclasificacion_salidas/*.json y escribe
resultados/salidas/COMPARACION_ESTADOS_SALIDAS.md y resultados/salidas/resumen_salidas.csv.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
R = HERE / "resultados"
V3, SAL = R / "reclasificacion_v3", R / "reclasificacion_salidas"
OUT = R / "salidas"
EMAX = float(np.sqrt(1 - 0.9 ** 2))


def carga(d):
    out = {}
    for f in sorted(d.glob("*.json")):
        try:
            out[f.stem] = json.loads(f.read_text())
        except Exception:
            pass
    return out


def eaj(r):
    v = r.get("eajuste_med")
    if v is None:
        v = r.get("eajuste_cota")
    return v


def fmt(x, pct=False):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "—"
    return f"{100 * x:.1f} %" if pct else f"{x:.3f}"


def estado(r):
    if not r:
        return "—"
    if r.get("error"):
        return "error"
    e = r.get("etapa", "—")
    if e == "Técnico":
        return "Técnico"
    if len(r.get("S", [])) < 2:
        return f"{e} (|S| = 1)"
    return f"{e} {'✓' if r.get('admisible') else '✗'}"


def main():
    a, b = carga(V3), carga(SAL)
    nombres = sorted(set(a) | set(b))
    filas = []
    for n in nombres:
        ra, rb = a.get(n, {}), b.get(n, {})
        comunes = sorted(set(ra.get("S", [])) & set(rb.get("S", [])))
        filas.append({
            "sistema": n,
            "estados_etapa": estado(ra), "estados_|S|": len(ra.get("S", [])),
            "salidas_etapa": estado(rb), "salidas_|S|": len(rb.get("S", [])),
            "salidas_p": rb.get("p"), "salidas_cos": rb.get("cos_med"),
            "salidas_erel": rb.get("erel_med"), "salidas_eajuste": eaj(rb),
            "salidas_admisible": rb.get("admisible"),
            "S_salidas": ", ".join(rb.get("S", [])),
            "en_comun": len(comunes),
        })
    df = pd.DataFrame(filas)
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "resumen_salidas.csv", index=False)

    L = ["# Selección sobre estados frente a salidas medidas", "",
         "**Estados**: trayectorias de todos los estados x(t) en 60 puntos de [0, T] (v3). "
         "**Salidas**: predicciones de las mediciones de PEtab, y_i = h(g_i(x(t_i), θ))/σ_i "
         "(observables, condiciones experimentales, preequilibrio, transformación y ruido; "
         "`petab_outputs.py`). Mismas reglas en ambos casos (Etapa 1: R_var ≥ 0,89; Etapa 2: "
         "barrido; admisible ⇔ |S| ≥ 2 y e_ajuste ≤ 0,436). ✓ = admisible, ✗ = no admisible.", "",
         "| Sistema | Estados | Salidas | p | |S| salidas | cos Δ | e_rel | e_ajuste | "
         "Parámetros comunes |",
         "|---|---|---|---|---|---|---|---|---|"]
    for r in filas:
        L.append(f"| {r['sistema']} | {r['estados_etapa']} ({r['estados_|S|']}) | "
                 f"{r['salidas_etapa']} | {r['salidas_p'] or '—'} | {r['salidas_|S|']} | "
                 f"{fmt(r['salidas_cos'])} | {fmt(r['salidas_erel'], True)} | "
                 f"{fmt(r['salidas_eajuste'], True)} | {r['en_comun']} |")
    adm_a = sum(1 for n in nombres if a.get(n, {}).get("admisible"))
    adm_b = sum(1 for n in nombres if b.get(n, {}).get("admisible"))
    L += ["", f"Admisibles: estados {adm_a}/{len(a)}, salidas {adm_b}/{len(b)}.", ""]
    L += ["## Subconjuntos seleccionados (salidas)", ""]
    for r in filas:
        if r["S_salidas"]:
            L.append(f"* **{r['sistema']}**: {r['S_salidas']}")
    (OUT / "COMPARACION_ESTADOS_SALIDAS.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[:len(filas) + 12]))


if __name__ == "__main__":
    main()
