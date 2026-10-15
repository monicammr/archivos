#!/usr/bin/env python3
"""
Prueba 1 de identificabilidad del problema reducido: ¿se confunde algún parámetro biológico
seleccionado (S) con un parámetro de calibración (Θ_C, escalas y offsets)?

Para cada problema con subconjunto admisible (resultados/reclasificacion_salidas_bio_poda) se
calcula, en θ₀ y sobre las salidas medidas escaladas por el ruido (y_i/σ_i, petab_outputs.PSys),
la matriz de sensibilidad relativa J = ∂y/∂log θ de las columnas S ∪ Θ_C, con las mismas
diferencias centradas (δ = 0,01) que la selección. Los parámetros cuya columna es nula (p. ej. de
ruido, que sólo intervienen en σ, fijo en θ₀) se excluyen y se informan.

Medidas (umbral 10 en todas, el de la selección):
  * κ_std y VIF_std: mismas funciones que la selección (columnas estandarizadas) sobre S ∪ Θ_C;
  * κ_n y VIF_n: columnas normalizadas a norma 1 SIN centrar — condición de la matriz de
    información de Fisher local JᵀJ, la medida estándar de identificabilidad local;
  * el parámetro con mayor VIF_n y el par de columnas con mayor |coseno| (qué se confunde con qué).
Problemas sin parámetros de calibración: J_{S∪Θ_C} = J_S, que ya pasó κ y VIF en la selección.

Las columnas ya calculadas por la selección (resultados/cache/*_salidas_J.npy) se reutilizan.

Uso:  python identificabilidad_local.py [Problema ...]
Salida: resultados/identificabilidad/local/<problema>.json y resumen_local.csv
"""
import sys, json, time, os
from pathlib import Path
from multiprocessing import Pool

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(v, "1")
import numpy as np
import pandas as pd

sys.argv.append("--salidas")          # stage_reclass usa entonces las salidas medidas
from stage_reclass import kappa, vif, DELTA, KAPPA_MAX, VIF_MAX
from certify_systems import SYSTEMS, T_END_OVERRIDE, OUT
from petab_outputs import PSys

SEL = OUT / "reclasificacion_salidas_bio_poda"
DEST = OUT / "identificabilidad" / "local"
CACHE = OUT / "cache"


def t_end_de(name):
    t_def = next((t for n, _, t, _ in SYSTEMS if n == name), 50.0)
    return T_END_OVERRIDE.get(name, t_def)


def kappa_n(J):
    n = np.linalg.norm(J, axis=0)
    s = np.linalg.svd(J / n, compute_uv=False)
    return float("inf") if s[-1] < 1e-12 * s[0] else float(s[0] / s[-1])


def vif_n(J):
    """VIF sin centrar: diagonal de la inversa de la matriz de cosenos entre columnas."""
    n = np.linalg.norm(J, axis=0)
    G = (J / n).T @ (J / n)
    try:
        return np.diag(np.linalg.inv(G))
    except np.linalg.LinAlgError:
        return np.full(len(G), np.inf)


def uno(name):
    t0 = time.time()
    sel = json.loads((SEL / f"{name}.json").read_text())
    if not sel.get("admisible"):
        return {"sistema": name, "evaluable": False, "motivo": "sin subconjunto admisible"}
    Sy = PSys(name, t_end_de(name))
    names, th0 = list(Sy.names), Sy.theta0
    S = [names.index(s) for s in sel["S"]]
    C = [names.index(c) for c in sel.get("calibracion", [])]
    cols = S + C
    # columnas ya calculadas en la selección
    J = np.full((Sy.sim(th0).size, len(cols)), np.nan)
    fJ, fm = CACHE / f"{name}_salidas_J.npy", CACHE / f"{name}_salidas_J_hechas.npy"
    reus = 0
    if fJ.exists() and fm.exists():
        Jc, hechas = np.load(fJ, mmap_mode="r"), np.load(fm)
        for k, j in enumerate(cols):
            if hechas[j]:
                J[:, k] = np.asarray(Jc[:, j], dtype=float); reus += 1
    for k, j in enumerate(cols):
        if np.isnan(J[:, k]).all():
            tp, tm = th0.copy(), th0.copy()
            tp[j] *= 1 + DELTA; tm[j] *= 1 - DELTA
            yp, ym = Sy.sim(tp), Sy.sim(tm)
            J[:, k] = np.nan if yp is None or ym is None else (yp - ym).ravel() / (2 * DELTA)
    ok = np.isfinite(J).all(axis=0) & (np.linalg.norm(np.nan_to_num(J), axis=0) > 1e-12)
    nulas = [names[j] for j, o in zip(cols, ok) if not o]
    Sk = [k for k in range(len(S)) if ok[k]]
    Ck = [k for k in range(len(S), len(cols)) if ok[k]]
    if len(Sk) < len(S):
        return {"sistema": name, "evaluable": False, "S": sel["S"],
                "motivo": "columna nula de un parámetro seleccionado", "nulas": nulas}
    idx = Sk + Ck
    Jx = J[:, idx]
    etiquetas = [names[cols[k]] for k in idx]
    vn = vif_n(Jx)
    U = Jx / np.linalg.norm(Jx, axis=0)
    Cos = np.abs(U.T @ U); np.fill_diagonal(Cos, 0)
    # par más parecido con al menos un parámetro de S
    mejor = (0.0, None, None)
    for a in range(len(Sk)):
        for b in range(len(idx)):
            if b != a and Cos[a, b] > mejor[0]:
                mejor = (float(Cos[a, b]), etiquetas[a], etiquetas[b])
    r = {
        "sistema": name, "evaluable": True, "S": sel["S"],
        "n_calibracion": len(C), "calibracion_usada": [etiquetas[k] for k in range(len(Sk), len(idx))],
        "columnas_nulas_excluidas": nulas, "n_filas": int(Jx.shape[0]),
        "kappa_S_std": kappa(J, Sk), "VIF_S_std": vif(J, Sk),
        "kappa_SC_std": kappa(Jx, list(range(len(idx)))), "VIF_SC_std": vif(Jx, list(range(len(idx)))),
        "kappa_SC_n": kappa_n(Jx), "VIF_SC_n_max": float(np.max(vn)),
        "VIF_SC_n_S": {etiquetas[k]: float(vn[k]) for k in range(len(Sk))},
        "param_VIF_max": etiquetas[int(np.argmax(vn))],
        "par_mas_parecido_con_S": {"coseno": mejor[0], "a": mejor[1], "b": mejor[2]},
        "columnas_reutilizadas": reus, "segundos": round(time.time() - t0, 1),
    }
    r["pasa_std"] = bool(r["kappa_SC_std"] <= KAPPA_MAX and r["VIF_SC_std"] <= VIF_MAX)
    r["pasa_n"] = bool(r["kappa_SC_n"] <= KAPPA_MAX and r["VIF_SC_n_max"] <= VIF_MAX)
    # lo que importa para S: VIF de sus propias columnas en el problema conjunto
    r["pasa_S_n"] = bool(max(r["VIF_SC_n_S"].values()) <= VIF_MAX)
    return r


def tarea(name):
    f = DEST / f"{name}.json"
    if f.exists():
        return json.loads(f.read_text())
    try:
        r = uno(name)
    except Exception as ex:
        r = {"sistema": name, "evaluable": False, "error": repr(ex)}
    f.write_text(json.dumps(r, indent=1, default=str))
    print(f"{name}: {'ok' if r.get('evaluable') else r.get('motivo', r.get('error'))} "
          f"({r.get('segundos', '-')} s)", flush=True)
    return r


if __name__ == "__main__":
    DEST.mkdir(parents=True, exist_ok=True)
    which = [a for a in sys.argv[1:] if not a.startswith("--")]
    todos = sorted(p.stem for p in SEL.glob("*.json"))
    lista = [n for n in todos if not which or n in which]
    # los más lentos primero, para repartir mejor
    lentos = ["Lang_PLOSComputBiol2024", "Chen_MSB2009", "Raimundez_PCB2020", "Bachmann_MSB2011"]
    lista = [n for n in lentos if n in lista] + [n for n in lista if n not in lentos]
    with Pool(int(os.environ.get("NPROC", os.cpu_count() or 1))) as pool:
        res = pool.map(tarea, lista, chunksize=1)
    pd.DataFrame([{k: v for k, v in r.items() if not isinstance(v, (dict, list))} for r in res]) \
        .to_csv(DEST / "resumen_local.csv", index=False)
