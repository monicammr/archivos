#!/usr/bin/env python3
"""
Selection by column-pivoted QR (Vélez-Reyes and Verghese, 1995) with the same protocol as the other
criteria (Supplementary Note "Pivoted QR selection"): the sensitivity matrix of the training
outputs at theta0 (forward differences, relative step 1e-4) is normalised column by column, and the
first k = |S| pivots of its column-pivoted QR decomposition are selected; the subset, with the
calibration parameters, is re-estimated on the training data and evaluated on the test data.
(An earlier version of the paper attributed this criterion to Brun et al.; Brun's collinearity index
is implemented in brun_morris.py.)

QR_VARIANT=gks selects instead with the standard subset selection of Golub, Klema and Stewart
(Golub & Van Loan, Algorithm 12.2.1), the one used by Velez-Reyes and Verghese: the SVD of the same
normalised matrix, J = U Sigma V^T, and the first k pivots of the column-pivoted QR decomposition of
V_k^T (the k dominant right singular vectors). Output: results/qr_selection_gks/.

Usage:  python qr_selection.py [Problem ...]        (default: admissible problems except Chen, Lang)
Output: results/qr_selection/<problem>.json
"""
import json
import os
import sys
import time
import warnings
from multiprocessing import Pool

import numpy as np
from scipy.linalg import qr as scipy_qr

warnings.filterwarnings("ignore")
import config as CFG  # noqa: E402
import external_validation as EV  # noqa: E402
import petab_problem as PP  # noqa: E402

SKIP = {"Chen_MSB2009", "Lang_PLOSComputBiol2024"}
EV.CKDIR["dir"] = None
GKS = os.environ.get("QR_VARIANT") == "gks"
OUTD = CFG.RESULTS / "qr_selection_gks" if GKS else CFG.QR_SELECTION


def qr_select(S, bio, k, gidx, ftrain):
    th0 = S.theta0
    z0 = S.z(th0, gidx)
    y0 = z0[ftrain]
    J = np.zeros((len(y0), len(bio)))
    for c, j in enumerate(bio):
        eps = max(abs(th0[j]) * 1e-4, 1e-8)
        th = th0.copy(); th[j] += eps
        zp = S.z(th, gidx)
        if zp is not None:
            d = zp[ftrain] - y0
            J[:, c] = np.where(np.isfinite(d), d, 0.0) / eps
    nrm = np.linalg.norm(J, axis=0)
    valid = nrm > 1e-10
    if valid.sum() < k:
        sel = list(np.array(bio)[valid]) + [j for j in np.array(bio)[~valid]]
        return [int(j) for j in sel[:k]]
    Z = J[:, valid] / nrm[valid]
    if GKS:
        # Golub-Klema-Stewart: pivoted QR of V_k^T, the k dominant right singular vectors
        _, _, Vt = np.linalg.svd(Z, full_matrices=False)
        _, _, piv = scipy_qr(Vt[:k, :], pivoting=True)
    else:
        _, _, piv = scipy_qr(Z, pivoting=True)
    vi = np.where(valid)[0]
    return [int(bio[vi[piv[i]]]) for i in range(k)]


def run(name):
    t0 = time.time()
    info = json.loads((CFG.SELECTION / f"{name}.json").read_text())
    S = PP.PetabProblem(name)
    th0 = S.theta0.copy()
    cal = info.get("calibracion", [])
    k = len(info["S"])
    bio = [int(j) for j in np.nonzero(S.in_model)[0] if S.names[j] not in set(cal)]
    cal_idx = [S.names.index(q) for q in cal if q in S.names]
    train, test, ftest, kind = EV.split(S)
    zd = S.zdata()
    ftr = ~ftest & np.isfinite(zd)
    fte = ftest & np.isfinite(zd)
    if not ftr.any() or not fte.any():
        return {"sistema": name, "no_evaluable": "single condition/time"}
    sel = qr_select(S, bio, k, train, ftr)
    loc = EV.test_only_parameters(S, train, test)
    free = [j for j in sel + cal_idx if j not in loc]
    if not free:
        return {"sistema": name, "no_evaluable": "all QR params are test-local"}
    th, _ = EV.fit(S, free, th0, train, zd, ftr, 30 * (len(free) + 1))
    c_qr = EV.chi2(S.z(th), zd, fte)
    f = CFG.NESTED / f"{name}.json"
    c_ours = json.loads(f.read_text()).get("chi2_test_red_original") if f.exists() else None
    S_qr = [S.names[j] for j in sel]
    return {"sistema": name, "k": k, "S_ours": info["S"], "S_qr": S_qr,
            "overlap": len(set(S_qr) & set(info["S"])), "chi2_ours": c_ours, "chi2_qr": c_qr,
            "ratio_qr_vs_ours": c_qr / c_ours if c_ours else None, "tipo": kind,
            "segundos": round(time.time() - t0, 1)}


def _safe(name):
    try:
        r = run(name)
    except Exception as e:
        r = {"sistema": name, "error": repr(e)}
    r["variant"] = "gks" if GKS else "pivoted_qr_of_J"
    OUTD.mkdir(parents=True, exist_ok=True)
    (OUTD / f"{name}.json").write_text(json.dumps(r, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: r.get(k) for k in ("sistema", "S_qr", "chi2_qr")}, default=str), flush=True)


if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if not a.startswith("--")] or sorted(
        f.stem for f in CFG.SELECTION.glob("*.json")
        if json.loads(f.read_text()).get("admisible") and f.stem not in SKIP)
    with Pool(int(os.environ.get("NPROC", 4))) as pool:
        list(pool.imap_unordered(_safe, names))
