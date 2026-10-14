#!/usr/bin/env python3
"""
Brun/QR-pivoted parameter selection comparison.

For each admissible problem, selects k = |S_ours| biological parameters by
QR-pivoted normalized sensitivity (Brun 2001), then runs the same external
validation protocol as the main paper. Compares chi2/n vs our method.

Usage:
    python3 comparacion_brun.py [Problem ...]
    VAL_PMAX=200 NPROC=3 python3 comparacion_brun.py

Output: resultados/comparacion_brun/<problem>.json
"""
import sys
import json
import time
import os
import warnings
from pathlib import Path
from multiprocessing import Pool

import numpy as np
from scipy.linalg import qr as scipy_qr

warnings.filterwarnings("ignore")
import petab_outputs as PO

# Import shared helpers from the main nested-validation script
from validacion_anidada import (
    division, refs_grupo, locales_de_prueba, ajusta, chi2n, CKPT_INTERVAL,
)

HERE = Path(__file__).resolve().parent
SUBS = HERE / "resultados" / "reclasificacion_salidas_bio_poda"
# chi2_ours loaded from nested validation: same chi2n() scale as chi2_qr
NESTED = HERE / "resultados" / "validacion_anidada"
OUTD = HERE / "resultados" / "comparacion_brun"
NPROC = int(os.environ.get("NPROC", 3))


# ── QR-pivoted selection ──────────────────────────────────────────────────────

def qr_selection(S, bio_idx, k, gidx, zd, ftrain):
    """
    Rank bio_idx parameters by QR-pivoted normalized sensitivity at theta0
    (training data only) and return the top-k indices.
    """
    th0 = S.theta0
    z0 = S.z(th0, gidx)
    if z0 is None or not ftrain.any():
        return list(bio_idx[:k])

    z0_tr = z0[ftrain]
    n_obs = int(ftrain.sum())
    n_bio = len(bio_idx)
    J = np.zeros((n_obs, n_bio))

    for col, j in enumerate(bio_idx):
        v = th0[j]
        eps = max(abs(v) * 1e-4, 1e-8)
        th_p = th0.copy()
        th_p[j] = v + eps
        zp = S.z(th_p, gidx)
        if zp is not None:
            dz = zp[ftrain] - z0_tr
            dz = np.where(np.isfinite(dz), dz, 0.0)
            J[:, col] = dz / eps

    norms = np.linalg.norm(J, axis=0)
    valid = norms > 1e-10

    if valid.sum() < k:
        # fallback: use valid first, then zero-sensitivity ones
        sel = list(np.array(bio_idx)[valid])
        for jj in np.array(bio_idx)[~valid]:
            if len(sel) >= k:
                break
            sel.append(jj)
        return sel[:k]

    J_norm = J[:, valid] / norms[valid]
    # Column-pivoted QR: A[:,P] = QR; P[0] = index of most informative column
    _, _, piv = scipy_qr(J_norm, pivoting=True)

    valid_idx = np.where(valid)[0]
    return [bio_idx[valid_idx[piv[i]]] for i in range(k)]


# ── per-problem function ───────────────────────────────────────────────────────

def uno(name):
    t0 = time.time()
    OUTD.mkdir(parents=True, exist_ok=True)
    ckdir = OUTD / "checkpoints" / name
    ckdir.mkdir(parents=True, exist_ok=True)

    info_path = SUBS / f"{name}.json"
    if not info_path.exists():
        return {"sistema": name, "error": "no selection result"}
    info = json.loads(info_path.read_text())
    if not info.get("admisible"):
        return {"sistema": name, "error": "not admissible"}

    S = PO.PSys(name)
    th0 = S.theta0.copy()

    cal = info.get("calibracion", [])
    S_ours = info["S"]
    k = len(S_ours)

    # Biological parameter indices: in-model, not calibration
    cal_set = set(cal)
    bio_idx = [
        j for j in np.nonzero(S.in_model)[0]
        if S.names[j] not in cal_set
    ]
    cal_idx = [S.names.index(q) for q in cal if q in S.names]

    train, test, ftest, tipo = division(S)
    ftrain = ~ftest
    zd = S.zdata()
    ftr = ftrain & np.isfinite(zd)
    fte = ftest  & np.isfinite(zd)

    if not ftr.any() or not fte.any():
        return {"sistema": name, "no_evaluable": "single condition/time"}
    if len(bio_idx) < k:
        return {"sistema": name, "no_evaluable":
                f"only {len(bio_idx)} bio params < k={k}"}

    # QR selection
    sel_qr = qr_selection(S, bio_idx, k, train, zd, ftr)
    S_qr = [S.names[j] for j in sel_qr]

    # Exclude test-local parameters
    loc = locales_de_prueba(S, train, test)
    libres_qr = [j for j in (sel_qr + cal_idx) if j not in loc]

    if not libres_qr:
        return {"sistema": name, "no_evaluable": "all QR params are test-local"}

    nf = 30 * (len(libres_qr) + 1)
    th_qr, _ = ajusta(S, libres_qr, th0, train, zd, ftr, nf,
                      ckpt=str(ckdir / "qr.npz"))
    chi2_qr = chi2n(S, th_qr, zd, fte)

    # Our method chi2 from nested validation (same chi2n() scale as chi2_qr)
    chi2_ours = None
    nested_path = NESTED / f"{name}.json"
    if nested_path.exists():
        nested = json.loads(nested_path.read_text())
        chi2_ours = nested.get("chi2_test_red_original")

    overlap = len(set(S_ours) & set(S_qr))
    ratio = (chi2_qr / chi2_ours
             if chi2_ours and chi2_ours > 0 else None)

    res = {
        "sistema": name,
        "k": k,
        "S_ours": S_ours,
        "S_qr": S_qr,
        "overlap": overlap,
        "chi2_ours": chi2_ours,
        "chi2_qr": chi2_qr,
        "ratio_qr_vs_ours": ratio,
        "tipo": tipo,
        "segundos": round(time.time() - t0, 1),
    }
    (OUTD / f"{name}.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps(
        {k2: res[k2] for k2 in ("sistema", "k", "overlap",
                                 "chi2_ours", "chi2_qr",
                                 "ratio_qr_vs_ours", "segundos")},
        default=str), flush=True)
    return res


def _seguro(name):
    try:
        return uno(name)
    except Exception as e:
        r = {"sistema": name, "error": repr(e)}
        (OUTD / f"{name}.json").write_text(json.dumps(r, indent=1))
        print(json.dumps(r), flush=True)
        return r


if __name__ == "__main__":
    nombres = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not nombres:
        # Skip Chen (running) and Lang (too expensive)
        SKIP = {"Chen_MSB2009", "Lang_PLOSComputBiol2024"}
        nombres = sorted(
            f.stem for f in SUBS.glob("*.json")
            if json.loads(f.read_text()).get("admisible") and f.stem not in SKIP
        )
    print(f"Brun/QR comparison: {len(nombres)} problems, NPROC={NPROC}", flush=True)
    with Pool(NPROC) as pool:
        list(pool.imap_unordered(_seguro, nombres))
    print("Done.", flush=True)
