#!/usr/bin/env python3
"""
Reproduction error of the selected subsets in units of the recorded noise (Supplementary Note on the
method settings, "Reproduction error in units of the noise"; point C1 of the review).

e_fit is relative to the change of the model response ||Delta y_full||. The outputs of
petab_problem.py are already divided by sigma_i, so for every scenario k at +-5 %
    error RMS  = e_fit,k * ||Delta y_full,k|| / sqrt(n)     (sigma per measurement)
    change RMS =           ||Delta y_full,k|| / sqrt(n)
with n the number of measurements. The e_fit,k of every scenario are read from results/robustness/
(+-5 %, seed 42: the scenarios of the selection) and ||Delta y_full,k|| is recomputed with the same
directions u(k).

Usage: python absolute_error.py [Problem ...]   -> results/absolute_error/<problem>.json
"""
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(v, "1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as CFG  # noqa: E402
import petab_problem as PP  # noqa: E402

SEL, ROB = CFG.SELECTION, CFG.ROBUSTNESS
OUT = CFG.RESULTS / "absolute_error"
KEY = "5"


def evaluate(name):
    rob = json.loads((ROB / f"{name}.json").read_text())
    lev = rob["niveles"][KEY]
    Sy = PP.PetabProblem(name)
    th0 = Sy.theta0
    U = np.array(rob["u"])
    y0 = Sy.sim(th0).ravel()
    n = y0.size
    rows = []
    for k, ef in zip(lev["escenarios"], lev["eaj"]):
        yf = Sy.sim(th0 * (1 + CFG.EPSILON * U[k]))
        if yf is None:
            continue
        change = float(np.linalg.norm(yf.ravel() - y0) / np.sqrt(n))
        rows.append({"k": int(k), "e_fit": float(ef), "cambio_rms_sigma": change, "error_rms_sigma": float(ef) * change})
    med = lambda c: float(np.median([r[c] for r in rows])) if rows else float("nan")
    return {"sistema": name, "S": rob["S"], "n": n, "n_escenarios": len(rows), "e_fit_med": med("e_fit"),
            "cambio_rms_sigma_med": med("cambio_rms_sigma"), "error_rms_sigma_med": med("error_rms_sigma"),
            "error_rms_sigma_max": max((r["error_rms_sigma"] for r in rows), default=float("nan")),
            "escenarios": rows}


def safe(name):
    try:
        r = evaluate(name)
    except Exception as e:
        r = {"sistema": name, "error": repr(e)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps(r, indent=1))
    print(json.dumps({k: r.get(k) for k in ("sistema", "e_fit_med", "error_rms_sigma_med", "error")}), flush=True)


if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not names:
        names = [f.stem for f in sorted(SEL.glob("*.json")) if json.loads(f.read_text()).get("admisible")]
    with Pool(int(os.environ.get("NPROC", 4))) as pool:
        list(pool.imap_unordered(safe, names))
