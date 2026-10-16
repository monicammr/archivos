#!/usr/bin/env python3
"""
Conditioning of the final subsets with the two normalisations of the sensitivity columns (second
audit): selection.py tests kappa and VIF on columns that are CENTRED and scaled to unit variance
(the correlation matrix of the columns of J_S), whereas the Lean statements on the linearised
least-squares problem (Supplementary Table "modules", steps 7-9) use columns scaled to unit length
WITHOUT centring, Z = J_S diag(||J_j||)^-1. This script computes both for every final subset (the
columns of J_S and of the calibration parameters, central differences with delta = 1 %; 2|S| + 2|C|
simulations per problem).

Usage:  NPROC=8 python conditioning_check.py
Output: results/conditioning_check.json
"""
import json
import os
from multiprocessing import Pool

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(v, "1")
import numpy as np

import config as CFG
from petab_problem import PetabProblem
import selection as SEL


def unit_length(X):
    n = np.linalg.norm(X, axis=0)
    return X / np.where(n > 0, n, 1.0)


def kappa_vif(Z):
    s = np.linalg.svd(Z, compute_uv=False)
    G = Z.T @ Z
    v = np.diag(np.linalg.pinv(G)) * np.diag(G)
    return float(s[0] / s[-1]) if s[-1] > 0 else float("inf"), float(v.max())


def run(name):
    info = json.loads((CFG.SELECTION / f"{name}.json").read_text())
    if not info.get("admisible"):
        return None
    Sy = PetabProblem(name)
    th0 = Sy.theta0
    S = [Sy.names.index(q) for q in info["S"]]
    C = [Sy.names.index(q) for q in info.get("calibracion", [])]
    cols = {}
    for j in S + C:
        tp, tm = th0.copy(), th0.copy()
        tp[j] *= 1 + CFG.DELTA; tm[j] *= 1 - CFG.DELTA
        yp, ym = Sy.sim(tp), Sy.sim(tm)
        cols[j] = (yp - ym).ravel() / (2 * CFG.DELTA)
    JS = np.column_stack([cols[j] for j in S])
    JSC = np.column_stack([cols[j] for j in S + C])
    k_u, v_u = kappa_vif(unit_length(JS))
    k_uc, v_uc = kappa_vif(unit_length(JSC))
    idx = list(range(len(S)))
    r = {"sistema": name, "S": info["S"],
         "kappa_centred": SEL.kappa(JS, idx), "VIF_centred": SEL.vif(JS, idx),
         "kappa_unit": k_u, "VIF_unit": v_u,
         "kappa_unit_with_calibration": k_uc, "VIF_unit_with_calibration": v_uc,
         "kappa_selection_json": info.get("kappa"), "VIF_selection_json": info.get("VIF")}
    print(json.dumps({k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()
                      if k != "S"}), flush=True)
    return r


if __name__ == "__main__":
    with Pool(int(os.environ.get("NPROC", 8))) as pool:
        out = [r for r in pool.map(run, CFG.PROBLEMS, chunksize=1) if r]
    (CFG.RESULTS / "conditioning_check.json").write_text(json.dumps(out, indent=1))
