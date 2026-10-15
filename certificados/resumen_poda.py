#!/usr/bin/env python3
"""Resumen de la poda (stage_reclass.py --v3 --salidas --poda) → resultados/salidas/PODA.md"""
import json
from pathlib import Path
import numpy as np

R = Path(__file__).resolve().parent / "resultados"
D = R / "reclasificacion_salidas_poda"


def main():
    rs = [json.loads(p.read_text()) for p in sorted(D.glob("*.json"))]
    pct = lambda x: "—" if x is None or not np.isfinite(x) else f"{100 * x:.1f} %"
    L = ["# Selección con poda (comentario 2)", "",
         "Selección voraz sobre las salidas medidas y, después, eliminación hacia atrás: se quita "
         "cada parámetro (del menos al más influyente) mientras el subconjunto siga siendo "
         "admisible (|S| ≥ 2 y e_ajuste ≤ 43,6 %). Resultado mínimo por inclusión "
         "(Lean: `Poda.prune_spec`).", "",
         "| Sistema | Etapa | |S| antes | |S| después | Quitados | S final | e_ajuste | Admisible |",
         "|---|---|---|---|---|---|---|---|"]
    antes = despues = 0
    for r in rs:
        if "error" in r or "S_antes_poda" not in r:
            L.append(f"| {r['sistema']} | {r.get('etapa', 'error')} | | | | | | ✗ |")
            continue
        a, d = len(r["S_antes_poda"]), len(r["S"])
        if r.get("admisible"):
            antes += a; despues += d
        L.append(f"| {r['sistema']} | {r.get('etapa')} | {a} | {d} | "
                 f"{', '.join(r.get('podados', [])) or '—'} | {', '.join(r['S'])} | "
                 f"{pct(r.get('eajuste_med'))} | {'✓' if r.get('admisible') else '✗'} |")
    n_adm = sum(1 for r in rs if r.get("admisible"))
    L += ["", f"* Admisibles: {n_adm} de {len(rs)}.",
          f"* Parámetros en los subconjuntos admisibles: {antes} antes de la poda, {despues} "
          f"después ({antes - despues} eliminados por redundantes)."]
    (R / "salidas" / "PODA.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
