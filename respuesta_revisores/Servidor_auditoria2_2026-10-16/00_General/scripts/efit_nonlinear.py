#!/usr/bin/env python3
"""
Nonlinear verification of the final subsets of the problems whose admissibility was decided to
first order (second audit, point A2; Supplementary Note "Nonlinear check of the first-order
problems").

For each problem of config.FIRST_ORDER with an admissible subset, the final subset S (with its
calibration parameters) is re-estimated by nonlinear least squares in each of the 15 admissibility
scenarios of selection.py (same seed, same perturbation size, same bounds, the same two starting
points and the same evaluation budget), exactly as for the problems that are not first order. The
scenarios are independent and are distributed over processes; each scenario is one task and its
result is stored, so an interrupted run is resumed.

Usage:  NPROC=30 python efit_nonlinear.py [Problem ...]
        A2_SUBSETS=selection_fixedscen python efit_nonlinear.py   (subsets of another folder)
Output: results/efit_nonlinear[_<folder>]/<problem>/s<k>.json and <problem>.json (summary: median
        nonlinear e_fit, median first-order e_fit of the selection, admissible or not).
"""
import json
import math
import os
import sys
import time
from multiprocessing import Pool

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(v, "1")
import numpy as np
from scipy.optimize import least_squares

import config as CFG
from petab_problem import PetabProblem

SUBF = os.environ.get("A2_SUBSETS", "selection")
SUBS = CFG.RESULTS / SUBF
OUTD = CFG.RESULTS / ("efit_nonlinear" if SUBF == "selection" else f"efit_nonlinear_{SUBF}")
TAU = CFG.TAU_E
_P = {}


def problem(name):
    if name not in _P:
        Sy = PetabProblem(name)
        th0 = Sy.theta0
        rng = np.random.default_rng(CFG.SEED)
        scen = [th0 * (1 + CFG.EPSILON * rng.uniform(-1, 1, size=len(th0)))
                for _ in range(CFG.N_SCENARIOS)]
        y0 = Sy.sim(th0)
        _P[name] = (Sy, scen, None if y0 is None else y0.ravel())
    return _P[name]


def one(task):
    name, k = task
    out = OUTD / name / f"s{k}.json"
    if out.exists():
        return
    t0 = time.time()
    info = json.loads((SUBS / f"{name}.json").read_text())
    Sy, scen, y0 = problem(name)
    th0, th = Sy.theta0, scen[k]
    S = [Sy.names.index(q) for q in info["S"]] + [Sy.names.index(q) for q in info.get("calibracion", [])]
    r = {"sistema": name, "escenario": k, "S": info["S"]}
    yf = Sy.sim(th)
    floor = max(1e-10 * np.linalg.norm(y0), 1e-6)
    if yf is None:
        r["descartado"] = "falla la simulación del modelo completo"
    elif np.linalg.norm(yf.ravel() - y0) < floor:
        r["descartado"] = "cambio de salida bajo el umbral numérico"
    else:
        yf = yf.ravel()
        nf = np.linalg.norm(yf - y0)
        sgn = np.where(th0[S] < 0, -1.0, 1.0)
        mag0 = np.maximum(np.abs(th0[S]), 1e-12)
        lo, hi = np.log(mag0 / 10), np.log(mag0 * 10)

        def resid(u):
            ts = th0.copy(); ts[S] = sgn * np.exp(u)
            ys = Sy.sim(ts)
            return np.full(yf.size, 10.0) if ys is None else (ys.ravel() - yf) / nf
        ts = th0.copy(); ts[S] = th[S]
        ys = Sy.sim(ts)
        erel = float("inf") if ys is None else float(np.linalg.norm(ys.ravel() - yf) / nf)
        best, starts = erel, {}
        x_scen = np.clip(np.log(np.maximum(np.abs(th[S]), 1e-12)), lo, hi)
        for lab, x0 in (("theta0", np.log(mag0)), ("escenario", x_scen)):
            try:
                o = least_squares(resid, x0, bounds=(lo, hi), method="trf",
                                  max_nfev=100 * (len(S) + 1), diff_step=1e-3)
                starts[lab] = {"e": float(np.linalg.norm(o.fun)), "nfev": int(o.nfev),
                               "status": int(o.status)}
                best = min(best, starts[lab]["e"])
            except Exception as e:
                starts[lab] = {"error": repr(e)}
        r.update(erel=erel, efit=best, arranques=starts)
    r["segundos"] = round(time.time() - t0, 1)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".tmp")
    tmp.write_text(json.dumps(r, indent=1, default=str), encoding="utf-8")
    os.replace(tmp, out)
    print(json.dumps({q: r.get(q) for q in ("sistema", "escenario", "efit", "erel", "descartado",
                                            "segundos")}, default=str), flush=True)


def summary(name):
    info = json.loads((SUBS / f"{name}.json").read_text())
    rs = [json.loads(f.read_text(encoding="utf-8")) for f in sorted((OUTD / name).glob("s*.json"))]
    ef = [r["efit"] for r in rs if "efit" in r]
    if len(rs) < CFG.N_SCENARIOS or not ef:
        return None
    med = float(np.median(ef))
    s = {"sistema": name, "S": info["S"], "n_escenarios_validos": len(ef),
         "eajuste_med_nolineal": med, "eajuste_med_primer_orden": info.get("eajuste_med"),
         "tasa_paso_nolineal": float(np.mean(np.asarray(ef) <= TAU)),
         "admisible_nolineal": bool(len(info["S"]) >= CFG.K_MIN and med <= TAU),
         "segundos_total": round(sum(r["segundos"] for r in rs), 1)}
    (OUTD / f"{name}.json").write_text(json.dumps(s, indent=1), encoding="utf-8")
    return s


if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if not a.startswith("--")] or sorted(CFG.FIRST_ORDER)
    names = [n for n in names if json.loads((SUBS / f"{n}.json").read_text()).get("admisible")]
    # Chen first: its scenarios are by far the slowest
    names.sort(key=lambda n: n != "Chen_MSB2009")
    tasks = [(n, k) for n in names for k in range(CFG.N_SCENARIOS)]
    print(f"{len(names)} problems, {len(tasks)} scenarios", flush=True)
    with Pool(int(os.environ.get("NPROC", 4))) as pool:
        list(pool.imap_unordered(one, tasks, chunksize=1))
    for n in names:
        print(json.dumps(summary(n)), flush=True)
