#!/usr/bin/env python3
"""
Error tras reestimar (e_ajuste): ¿basta con los parámetros seleccionados para reproducir el
comportamiento del modelo completo si se les permite reajustarse?

Para cada sistema y cada uno de los 15 escenarios (±5 %, semilla 42, como cos Δ y e_rel):
  1. "Datos": y_full = x(θ) con TODOS los parámetros perturbados.
  2. Modelo reducido: los parámetros descartados quedan en θ₀; sólo se mueven los de S.
  3. Reestimación por mínimos cuadrados no lineales (scipy.optimize.least_squares, 'trf'),
     en log θ_S, con límites [θ₀/10, 10·θ₀], desde dos puntos de partida (θ₀_S y θ_S del
     escenario); se toma el mejor.
  4. e_ajuste = ‖y_full − y_ajuste‖ / ‖y_full − y₀‖.
Se informa también e_rel (sin reajuste) y cos Δ del mismo escenario. Siempre e_ajuste ≤ e_rel.

Los subconjuntos S se leen de resultados/reclasificacion_v2/<sistema>.json
(generados por `stage_reclass.py --v2`).

Uso:
  python3 refit_systems.py                       # todos menos Froehlich, Lang y Chen
  python3 refit_systems.py Lang_PLOSComputBiol2024 Chen_MSB2009
  python3 refit_systems.py --bench C:/ruta/Benchmark-Models-PEtab/problems Froehlich_CellSystems2018
Opciones: --bench RUTA (carpeta `problems` del benchmark PEtab), --escenarios N (por defecto 15),
          --max-nfev N (evaluaciones máximas por ajuste, por defecto 100·(|S|+1)).
"""
import sys, json, time
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import least_squares
import certify_systems as CS

GRANDES = ["Froehlich_CellSystems2018", "Lang_PLOSComputBiol2024", "Chen_MSB2009"]
NIVEL, SEED = 0.05, 42
HERE = Path(__file__).resolve().parent
SUBSETS = HERE / "resultados" / "reclasificacion_v2"
OUTD = HERE / "resultados" / "ajuste"


def args():
    a = sys.argv[1:]
    opt = {"bench": None, "escenarios": 15, "max_nfev": None}
    names = []
    i = 0
    while i < len(a):
        if a[i] == "--bench":
            opt["bench"] = a[i + 1]; i += 2
        elif a[i] == "--escenarios":
            opt["escenarios"] = int(a[i + 1]); i += 2
        elif a[i] == "--max-nfev":
            opt["max_nfev"] = int(a[i + 1]); i += 2
        else:
            names.append(a[i]); i += 1
    return names, opt


def t_end_of(name):
    for n, _, t, _ in CS.SYSTEMS:
        if n == name:
            return CS.T_END_OVERRIDE.get(n, t)
    return CS.T_END_OVERRIDE.get(name, 50.0)


def refit_one(name, S_names, n_esc, max_nfev):
    t0 = time.time()
    Sy = CS.Sys(name, t_end_of(name))
    th0 = Sy.theta0
    p = len(th0)
    S = [Sy.names.index(q) for q in S_names if q in Sy.names]
    y0 = Sy.sim(th0)
    if y0 is None or not S:
        return {"sistema": name, "error": "sin simulación nominal o sin subconjunto"}, []
    rng = np.random.default_rng(SEED)
    escen = [np.maximum(th0 * (1 + NIVEL * rng.uniform(-1, 1, size=p)), 1e-12)
             for _ in range(n_esc)]
    umbral = max(1e-10 * np.linalg.norm(y0), 1e-6)
    lo, hi = np.log(th0[S] / 10), np.log(th0[S] * 10)
    nfev = max_nfev or 100 * (len(S) + 1)
    filas = []
    for k, th in enumerate(escen):
        yf = Sy.sim(th)
        if yf is None:
            continue
        dfull = (yf - y0).ravel()
        nf = np.linalg.norm(dfull)
        if nf < umbral:
            continue
        # residuo normalizado por ‖Δx_full‖ (respuestas de tamaños muy distintos entre sistemas)
        def resid(u):
            ts = th0.copy(); ts[S] = np.exp(u)
            ys = Sy.sim(ts)
            if ys is None:
                return np.full(yf.size, 10.0)  # residuo grande si la simulación falla
            return (ys - yf).ravel() / nf

        # sin reajuste (e_rel, cos Δ)
        ts = th0.copy(); ts[S] = th[S]
        ys = Sy.sim(ts)
        if ys is None:
            continue
        dsel = (ys - y0).ravel()
        ns = np.linalg.norm(dsel)
        erel = float(np.linalg.norm(dfull - dsel) / nf)
        cos = float(dfull @ dsel / (nf * ns)) if ns > 0 else 0.0
        mejor = None
        for x0 in (np.log(th0[S]), np.clip(np.log(th[S]), lo, hi)):
            try:
                r = least_squares(resid, x0, bounds=(lo, hi), method="trf", max_nfev=nfev, diff_step=1e-3,
                                  x_scale=1.0)
                if mejor is None or r.cost < mejor.cost:
                    mejor = r
            except Exception as ex:
                print(f"  aviso: ajuste fallido en el escenario {k}: {ex!r}", flush=True)
        eaj = float(np.linalg.norm(resid(mejor.x))) if mejor is not None else float("nan")
        eaj = min(eaj, erel)  # el punto sin reajuste también es candidato
        filas.append({"sistema": name, "escenario": k, "cos": cos, "e_rel": erel,
                      "e_ajuste": eaj})
    df = pd.DataFrame(filas)
    res = {"sistema": name, "|S|": len(S), "S": [Sy.names[j] for j in S],
           "n_escenarios": len(df)}
    if len(df):
        res.update({"cos_med": float(df.cos.median()), "erel_med": float(df.e_rel.median()),
                    "eajuste_med": float(df.e_ajuste.median()),
                    "eajuste_p90": float(df.e_ajuste.quantile(0.9)),
                    "eajuste<=0.10": f"{int((df.e_ajuste <= 0.10).sum())}/{len(df)}",
                    "eajuste<=0.436": f"{int((df.e_ajuste <= 0.436).sum())}/{len(df)}"})
    res["segundos"] = round(time.time() - t0, 1)
    return res, filas


if __name__ == "__main__":
    names, opt = args()
    if opt["bench"]:
        CS.BENCH = Path(opt["bench"])
    OUTD.mkdir(parents=True, exist_ok=True)
    if not names:
        names = sorted(p.stem for p in SUBSETS.glob("*.json")
                       if p.stem not in GRANDES and p.stem != "SCT_Bandura")
    out = []
    for name in names:
        f = SUBSETS / f"{name}.json"
        if not f.exists():
            print(f"[{name}] falta {f}: ejecute antes `python3 stage_reclass.py --v2 {name}`")
            continue
        info = json.loads(f.read_text())
        S_names = info.get("S") or []
        if not S_names:
            print(f"[{name}] sin subconjunto ({info.get('etapa')}): se omite")
            continue
        print(f"== {name} (|S| = {len(S_names)})", flush=True)
        try:
            r, filas = refit_one(name, S_names, opt["escenarios"], opt["max_nfev"])
        except Exception as e:
            r, filas = {"sistema": name, "error": repr(e)}, []
        r["admisible_v2"] = info.get("admisible")
        print(json.dumps(r, default=str), flush=True)
        (OUTD / f"{name}.json").write_text(json.dumps(r, default=str, indent=1))
        pd.DataFrame(filas).to_csv(OUTD / f"{name}_escenarios.csv", index=False)
        out.append(r)
    if out:
        pd.DataFrame(out).to_csv(OUTD / "resumen_ajuste.csv", index=False)
