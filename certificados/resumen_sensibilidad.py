#!/usr/bin/env python3
"""
Análisis de sensibilidad a las decisiones técnicas (comentario 6 del revisor).

Compara cada variante con su configuración base:
  * salidas medidas (base: resultados/reclasificacion_salidas/): δ = 0,1 % y 5 % (base 1 %),
    tolerancias del integrador finas (1e-9/1e-12) y gruesas (1e-6/1e-8) (base 1e-7/1e-10),
    perturbación de los escenarios ±1 % y ±10 % (base ±5 %);
  * estados (base: resultados/reclasificacion_v3/): malla de 30 y 120 puntos (base 60) y
    horizonte 2T.
Para cada sistema: ¿mismo subconjunto S?, índice de Jaccard |S ∩ S'|/|S ∪ S'|, ¿misma etapa?,
¿misma decisión de admisibilidad?, e_ajuste.
Salida: resultados/sensibilidad/SENSIBILIDAD.md y sensibilidad.csv
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd

R = Path(__file__).resolve().parent / "resultados"
OUT = R / "sensibilidad"
VARIANTES = [
    ("reclasificacion_salidas", "delta0001", "δ = 0,1 %"),
    ("reclasificacion_salidas", "delta005", "δ = 5 %"),
    ("reclasificacion_salidas", "tolfina", "tolerancias 1e-9 / 1e-12"),
    ("reclasificacion_salidas", "tolgruesa", "tolerancias 1e-6 / 1e-8"),
    ("reclasificacion_salidas", "nivel001", "perturbación ±1 %"),
    ("reclasificacion_salidas", "nivel010", "perturbación ±10 %"),
    ("reclasificacion_v3", "npts30", "malla de 30 puntos"),
    ("reclasificacion_v3", "npts120", "malla de 120 puntos"),
    ("reclasificacion_v3", "tfac2", "horizonte 2T"),
]


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
    return r.get("erel_med") if v is None else v


def main():
    filas = []
    for base, tag, desc in VARIANTES:
        dv = R / f"{base}_{tag}"
        if not dv.exists():
            continue
        B, V = carga(R / base), carga(dv)
        for n, rv in V.items():
            rb = B.get(n)
            if not rb or "error" in rv or "error" in rb:
                continue
            sb, sv = set(rb.get("S", [])), set(rv.get("S", []))
            filas.append({
                "variante": desc, "base": "salidas" if "salidas" in base else "estados",
                "sistema": n, "mismo_S": sb == sv,
                "jaccard": len(sb & sv) / len(sb | sv) if sb | sv else 1.0,
                "misma_etapa": rb.get("etapa") == rv.get("etapa"),
                "misma_admisibilidad": bool(rb.get("admisible")) == bool(rv.get("admisible")),
                "admisible_base": bool(rb.get("admisible")),
                "admisible_var": bool(rv.get("admisible")),
                "eaj_base": eaj(rb), "eaj_var": eaj(rv),
                "S_base": ", ".join(rb.get("S", [])), "S_var": ", ".join(rv.get("S", [])),
            })
    df = pd.DataFrame(filas)
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "sensibilidad.csv", index=False)
    if df.empty:
        print("sin variantes todavía")
        return
    L = ["# Sensibilidad a las decisiones técnicas (comentario 6)", "",
         "Cada fila resume una variante frente a la configuración del artículo (δ = 1 %, "
         "tolerancias 1e-7/1e-10, perturbación ±5 %, malla de 60 puntos en [0, T]).", "",
         "| Variante | Sobre | Sistemas | Mismo S | Jaccard medio | Misma etapa | "
         "Misma decisión de admisibilidad |", "|---|---|---|---|---|---|---|"]
    for (desc, base), g in df.groupby(["variante", "base"], sort=False):
        n = len(g)
        L.append(f"| {desc} | {base} | {n} | {g.mismo_S.sum()}/{n} | {g.jaccard.mean():.2f} | "
                 f"{g.misma_etapa.sum()}/{n} | {g.misma_admisibilidad.sum()}/{n} |")
    cambios = df[~df.misma_admisibilidad]
    L += ["", "## Sistemas cuya decisión de admisibilidad cambia", ""]
    if cambios.empty:
        L.append("Ninguno.")
    else:
        L += ["| Variante | Sistema | Base | Variante | e_ajuste base | e_ajuste variante |",
              "|---|---|---|---|---|---|"]
        for r in cambios.itertuples():
            fb = "—" if r.eaj_base is None or not np.isfinite(r.eaj_base) else f"{100*r.eaj_base:.1f} %"
            fv = "—" if r.eaj_var is None or not np.isfinite(r.eaj_var) else f"{100*r.eaj_var:.1f} %"
            L.append(f"| {r.variante} | {r.sistema} | {'✓' if r.admisible_base else '✗'} | "
                     f"{'✓' if r.admisible_var else '✗'} | {fb} | {fv} |")
    (OUT / "SENSIBILIDAD.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
