#!/usr/bin/env python3
"""Sensibilidad a los umbrales del método (revisor 2, comentario 4) → resultados/sensibilidad/UMBRALES.md

Selección final (salidas medidas, parámetros biológicos, poda) repetida cambiando un umbral cada
vez: τ_R (R_var de la Etapa 1), τ_κ = τ_VIF (κ y VIF) y τ_e (e_ajuste). Base: τ_R = 0,89,
τ_κ = τ_VIF = 10, τ_e = 0,436. Para cada variante: sistemas admisibles, tamaño medio de S, cuántos
sistemas conservan exactamente el mismo S y la misma etapa que la base.
"""
import json
from pathlib import Path
import numpy as np

R = Path(__file__).resolve().parent / "resultados"
BASE = R / "reclasificacion_salidas_bio_poda"
VARS = [("rvar080", "τ_R = 0,80"), ("rvar085", "τ_R = 0,85"), (None, "base"),
        ("rvar095", "τ_R = 0,95"), ("kv5", "τ_κ = τ_VIF = 5"), ("kv30", "τ_κ = τ_VIF = 30"),
        ("emax010", "τ_e = 0,10"), ("emax020", "τ_e = 0,20"), ("emax030", "τ_e = 0,30"),
        ("emax050", "τ_e = 0,50")]


def carga(d):
    return {p.stem: json.loads(p.read_text()) for p in sorted(d.glob("*.json"))}


def main():
    B = carga(BASE)
    L = ["# Sensibilidad a los umbrales del método", "",
         "Selección final (salidas medidas, parámetros biológicos, poda) en los sistemas pequeños y "
         "medianos, cambiando un umbral cada vez.", "",
         "| Variante | Sistemas | Admisibles | |S| medio (admisibles) | Etapa 1 | Mismo S que la base | "
         "Misma etapa |", "|---|---|---|---|---|---|---|"]
    for tag, desc in VARS:
        V = B if tag is None else carga(R / f"reclasificacion_salidas_bio_poda_{tag}")
        V = {k: v for k, v in V.items() if k in B}
        if not V:
            continue
        adm = [v for v in V.values() if v.get("admisible")]
        mismo = sum(set(V[k].get("S", [])) == set(B[k].get("S", [])) for k in V)
        etapa = sum(V[k].get("etapa") == B[k].get("etapa") for k in V)
        e1 = sum(v.get("etapa") == "Stage 1" for v in V.values())
        L.append(f"| {desc} | {len(V)} | {len(adm)} | "
                 f"{np.mean([len(v['S']) for v in adm]):.2f} | {e1} | {mismo}/{len(V)} | "
                 f"{etapa}/{len(V)} |")
    out = R / "sensibilidad" / "UMBRALES.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
