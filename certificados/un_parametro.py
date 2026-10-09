#!/usr/bin/env python3
"""
¿Basta UN parámetro? Prueba de robustez para decidir la regla |S| ≥ 2 (comentario 2).

Para cada sistema donde la prueba de minimalidad (minimalidad.py) encontró un parámetro j que,
solo, cumple e_ajuste ≤ 0,436 a ±5 %, se compara {j*} (el mejor de ellos) con el subconjunto S
seleccionado (|S| ≥ 2) en:
  1. perturbación mayor: mediana de e_ajuste con escenarios a ±10 % (semilla 42);
  2. predicción de experimentos no usados: validacion_externa.uno (datos reales: χ²/n de prueba;
     sintético con ruido: e_pred).
Salida: resultados/un_parametro/<sistema>.json y RESUMEN_UN_PARAMETRO.md
"""
import json, sys, os
from pathlib import Path
from multiprocessing import Pool
import numpy as np
import minimalidad as M
import validacion_externa as V

R = Path(__file__).resolve().parent / "resultados"
OUTD = R / "un_parametro"


def mejor_solo(r):
    ok = [x for x in r["un_parametro"] if x["admisible"]]
    if not ok:
        return None
    clave = lambda x: x["e_ajuste"] if x["e_ajuste"] is not None else x["e_rel"]
    return min(ok, key=clave)["parametro"]


def uno(name):
    r = json.loads((R / "minimalidad" / f"{name}.json").read_text())
    j = mejor_solo(r)
    S = r["S"]
    out = {"sistema": name, "uno": j, "S": S}
    M.NIVEL = 0.10
    ev = M.Evaluador(name)
    for etiqueta, sub in (("uno", [j]), ("S", S)):
        idx = [ev.S.names.index(q) for q in sub]
        ok, e, a = ev.admisible(idx)
        out[f"{etiqueta}_10_admisible"] = ok
        out[f"{etiqueta}_10_eajuste"] = a if a is not None else e
        v = V.uno(name, sub)
        for k in ("division", "no_evaluable", "A_chi2_test_red", "B_epred_red",
                  "A_chi2_test_full", "B_epred_full"):
            if k in v:
                out[f"{etiqueta}_{k}"] = v[k]
    OUTD.mkdir(parents=True, exist_ok=True)
    (OUTD / f"{name}.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps(out, default=str), flush=True)
    return out


def resumen():
    rs = [json.loads(p.read_text()) for p in sorted(OUTD.glob("*.json"))]
    f = lambda x, pct=False: ("—" if x is None or not np.isfinite(x) else
                              (f"{100*x:.1f} %" if pct else f"{x:.2f}"))
    L = ["# ¿Basta un parámetro? (decisión sobre la regla |S| ≥ 2)", "",
         "Mejor parámetro solo {j} frente al subconjunto seleccionado S. e_ajuste a ±10 % "
         "(umbral 43,6 %); predicción de experimentos no usados: χ²/n en prueba con datos reales "
         "(menor es mejor; ≈ 1 = nivel del ruido) y e_pred con datos sintéticos (umbral 0,436).",
         "", "| Sistema | j | S | e_ajuste ±10 %: j / S | χ²/n prueba (real): j / S | "
         "e_pred (sintético): j / S |", "|---|---|---|---|---|---|"]
    ne = lambda r, e, k: "no evaluable" if f"{e}_no_evaluable" in r else f(r.get(f"{e}_{k}"))
    gana_S = gana_j = 0
    for r in rs:
        L.append(f"| {r['sistema']} | {r['uno']} | {', '.join(r['S'])} | "
                 f"{f(r.get('uno_10_eajuste'), True)} / {f(r.get('S_10_eajuste'), True)} | "
                 f"{ne(r, 'uno', 'A_chi2_test_red')} / {ne(r, 'S', 'A_chi2_test_red')} | "
                 f"{ne(r, 'uno', 'B_epred_red')} / {ne(r, 'S', 'B_epred_red')} |")
        a, b = r.get("uno_B_epred_red"), r.get("S_B_epred_red")
        if a is not None and b is not None and np.isfinite(a) and np.isfinite(b):
            gana_S += b < a
            gana_j += a <= b
    L += ["", f"* Sintético (predicción de experimentos nuevos): S predice mejor en {gana_S}, "
              f"un parámetro igual o mejor en {gana_j}.",
          f"* ±10 %: un parámetro sigue siendo admisible en "
          f"{sum(bool(r.get('uno_10_admisible')) for r in rs)} de {len(rs)}; "
          f"S en {sum(bool(r.get('S_10_admisible')) for r in rs)} de {len(rs)}.",
          "* «no evaluable»: el parámetro sólo actúa en las condiciones de prueba (no se puede "
          "estimar con las de entrenamiento)."]
    (OUTD / "RESUMEN_UN_PARAMETRO.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    if "--resumen" in sys.argv:
        resumen(); sys.exit()
    nombres = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not nombres:
        for p in sorted((R / "minimalidad").glob("*.json")):
            d = json.loads(p.read_text())
            if d.get("algun_parametro_solo_basta"):
                nombres.append(p.stem)
    with Pool(int(os.environ.get("NPROC", 2))) as pool:
        list(pool.imap_unordered(uno, nombres))
    resumen()
