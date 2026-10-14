#!/usr/bin/env python3
"""
Leakage-free nested validation (Supplementary Note "Leakage-free nested validation").

theta0 was estimated with ALL data, test data included, and the reduced model keeps the
non-selected parameters at theta0. For each admissible problem this program:
  1. fits the FULL model on the training data only -> theta_train;
  2. fits the REDUCED model (S + calibration) starting from theta_train, with the non-selected
     parameters fixed at theta_train and search bounds derived from theta_train;
  3. reports the test chi2/n of the original (theta0-anchored) reduced model, of the full training
     fit and of the nested reduced model.
The nested reduced model coincides with the full training fit by construction (its re-estimation
starts at the training optimum); the comparison that matters is nested versus original.

With JAC_NPROC > 1 the columns of the finite-difference Jacobian of each fit are evaluated in
parallel (same steps as SciPy's '2-point' scheme), which is what made Chen (155 free parameters)
feasible; this needs Linux (fork). Chen was run with PO_RTOL=1e-6 PO_ATOL=1e-8 (REPRO_RTOL /
REPRO_ATOL in this package).

Usage:  python nested_validation.py [Problem ...]
        VAL_PMAX=200 JAC_NPROC=110 python nested_validation.py Chen_MSB2009
Output: results/nested_validation/<problem>.json
"""
import sys
import json
import time
import os
import warnings
from pathlib import Path
from multiprocessing import Pool

import numpy as np
from scipy.optimize import least_squares

warnings.filterwarnings("ignore")
import petab_problem as PP

import config as CFG
import external_validation as EV
SUBS = CFG.SELECTION
OUTD = CFG.NESTED
ORIG = CFG.VALIDATION   # original results for comparison
P_MAX_COMPLETO = int(os.environ.get("VAL_PMAX", 60))
NPROC = int(os.environ.get("NPROC", 4))


# ── helpers (same as validacion_externa.py) ──────────────────────────────────

CKPT_INTERVAL = 600  # save partial checkpoint every 10 minutes
JAC_NPROC = int(os.environ.get("JAC_NPROC", 1))  # >1: finite-difference Jacobian in parallel
JAC_MIN_P = 20      # below this many free parameters the serial Jacobian is used
DIFF_STEP = 1e-3
_RESID = None       # residual function inherited by the forked Jacobian workers


def _resid_hijo(u):
    return _RESID(u)

def ajusta(S, libres, th_ini, gidx, objetivo, filas, max_nfev, ckpt=None):
    th0 = th_ini  # bounds and signs relative to starting point, not global theta0
    sgn = np.where(th0[libres] < 0, -1.0, 1.0)
    mag0 = np.maximum(np.abs(th0[libres]), 1e-12)
    lo, hi = np.log(mag0 / 10), np.log(mag0 * 10)
    x0 = np.clip(np.log(np.maximum(np.abs(th_ini[libres]), 1e-12)), lo + 1e-9, hi - 1e-9)

    if ckpt is not None and Path(ckpt).exists():
        d = np.load(ckpt)
        if len(d["u"]) == len(libres) and bool(d["terminado"]):
            th = th_ini.copy(); th[libres] = sgn * np.exp(d["u"])
            return th, int(d["nfev"])
        elif len(d["u"]) == len(libres):  # partial checkpoint: resume from best so far
            x0 = np.clip(d["u"], lo + 1e-9, hi - 1e-9)

    def theta(u):
        t = th_ini.copy(); t[libres] = sgn * np.exp(u)
        return t

    mejor = {"c": np.inf, "u": x0.copy(), "n": 0, "t": time.time()}

    def resid(u):   # pure residual (no bookkeeping): also what the Jacobian workers run
        z = S.z(theta(u), gidx)
        r = np.full(int(filas.sum()), 1e3) if z is None else z[filas] - objetivo[filas]
        return np.where(np.isfinite(r), r, 1e3)

    def guarda():
        if ckpt is not None and time.time() - mejor["t"] > CKPT_INTERVAL:
            try:
                np.savez(ckpt, u=mejor["u"], terminado=False, nfev=mejor["n"])
            except Exception:
                pass
            mejor["t"] = time.time()

    ultimo = {"u": None, "r": None}

    def res(u):
        r = resid(u)
        ultimo["u"], ultimo["r"] = np.array(u, copy=True), r
        mejor["n"] += 1
        c = float(r @ r)
        if c < mejor["c"]:
            mejor["c"], mejor["u"] = c, np.array(u, copy=True)
        guarda()
        return r

    paralelo = JAC_NPROC > 1 and len(libres) >= JAC_MIN_P
    pool = None
    jac = "2-point"
    if paralelo:
        # same forward-difference steps as scipy's '2-point' with diff_step and bounds;
        # only the evaluation of the columns is distributed over the workers
        from scipy.optimize._numdiff import _compute_absolute_step, _adjust_scheme_to_bounds
        global _RESID
        _RESID = resid
        pool = Pool(min(JAC_NPROC, len(libres)))
        t_ini, it = time.time(), {"k": 0}

        def jac(u):
            u = np.asarray(u, dtype=float)
            f0 = ultimo["r"] if ultimo["u"] is not None and np.array_equal(ultimo["u"], u) else resid(u)
            h = _compute_absolute_step(DIFF_STEP, u, f0, "2-point")
            h, _ = _adjust_scheme_to_bounds(u, h, 1, "1-sided", lo, hi)
            pts = []
            for j in range(len(u)):
                x = u.copy(); x[j] += h[j]
                pts.append(x)
            cols = pool.map(_resid_hijo, pts, chunksize=1)
            J = np.empty((len(f0), len(u)))
            for j, fj in enumerate(cols):
                J[:, j] = (fj - f0) / (pts[j][j] - u[j])
            mejor["n"] += len(u)
            it["k"] += 1
            print(f"[{Path(ckpt).stem if ckpt else 'fit'}] jac {it['k']}  coste={float(f0 @ f0):.6g}  "
                  f"mejor={mejor['c']:.6g}  fallos={int(sum(np.all(c == 1e3) for c in cols))}  "
                  f"t={time.time() - t_ini:.0f}s", flush=True)
            guarda()
            return J

    try:
        r = least_squares(res, x0, jac=jac, bounds=(lo, hi), method="trf", max_nfev=max_nfev,
                          diff_step=DIFF_STEP)
        th = theta(r.x)
        if ckpt is not None:
            np.savez(ckpt, u=r.x, terminado=True, nfev=int(r.nfev))
        return th, int(r.nfev)
    except Exception:
        return th_ini.copy(), 0
    finally:
        if pool is not None:
            pool.terminate()
            pool.join()


def chi2n(S, th, objetivo, filas):
    z = S.z(th)
    if z is None:
        return float("nan")
    r = (z[filas] - objetivo[filas])
    r = r[np.isfinite(r)]
    return float(np.mean(r ** 2)) if len(r) else float("nan")


# ── main per-problem function ─────────────────────────────────────────────────

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

    S = PP.PetabProblem(name)
    th0 = S.theta0.copy()

    Ssel = [S.names.index(q) for q in info["S"] if q in S.names]
    n_bio = len(Ssel)
    Ssel += [S.names.index(q) for q in info.get("calibracion", []) if q in S.names]
    libres_full = [int(j) for j in np.nonzero(S.in_model)[0]]

    train, test, ftest, tipo = EV.split(S)
    ftrain = ~ftest

    if not ftrain.any() or not ftest.any():
        return {"sistema": name, "no_evaluable": "single condition/time"}

    loc = EV.test_only_parameters(S, train, test)
    Ssel_v = [j for j in Ssel if j not in loc]
    libres_full_v = [j for j in libres_full if j not in loc]

    if len(Ssel_v) == 0:
        return {"sistema": name, "no_evaluable": "S only in test conditions"}

    hacer_full = len(libres_full_v) <= P_MAX_COMPLETO
    if not hacer_full:
        return {"sistema": name, "no_evaluable": f"full model too large ({len(libres_full_v)} params)"}

    zd = S.zdata()
    ftr = ftrain & np.isfinite(zd)
    fte = ftest & np.isfinite(zd)
    nf_red  = 30 * (len(Ssel_v) + 1)
    nf_full = 15 * (len(libres_full_v) + 1)

    # ── Original approach (theta0 anchor, with leakage) ──────────────────────
    th_r_orig, _ = ajusta(S, Ssel_v, th0, train, zd, ftr, nf_red,
                          ckpt=str(ckdir / "orig_red.npz"))
    chi2_orig = chi2n(S, th_r_orig, zd, fte)

    # ── Step 1: fit FULL model on training only --> theta0_train ─────────────
    th_full_train, _ = ajusta(S, libres_full_v, th0, train, zd, ftr, nf_full,
                              ckpt=str(ckdir / "full_train.npz"))
    chi2_full_train = chi2n(S, th_full_train, zd, fte)

    # ── Step 2: fit REDUCED model from theta0_train (leakage-free) ───────────
    th_r_nested, _ = ajusta(S, Ssel_v, th_full_train, train, zd, ftr, nf_red,
                            ckpt=str(ckdir / "nested_red.npz"))
    chi2_nested = chi2n(S, th_r_nested, zd, fte)

    # ── theta0 reference ─────────────────────────────────────────────────────
    chi2_th0 = chi2n(S, th0, zd, fte)

    res = {
        "sistema": name,
        "S": info["S"],
        "|S|": n_bio,
        "division": tipo,
        "n_train": int(ftr.sum()),
        "n_test": int(fte.sum()),
        # original (current paper)
        "chi2_test_red_original": chi2_orig,
        # full model re-estimated on training only
        "chi2_test_full_train": chi2_full_train,
        # nested (leakage-free): reduced anchored at theta0_train
        "chi2_test_red_nested": chi2_nested,
        # published theta0 reference
        "chi2_test_theta0": chi2_th0,
        # ratio: does leakage matter?
        "ratio_nested_vs_original": (chi2_nested / chi2_orig
                                     if chi2_orig > 0 else float("nan")),
        "segundos": round(time.time() - t0, 1),
    }
    (OUTD / f"{name}.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({k: res[k] for k in ("sistema", "chi2_test_red_original",
                                           "chi2_test_red_nested", "ratio_nested_vs_original",
                                           "chi2_test_full_train", "segundos")},
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
        # all admissible problems with full model <= P_MAX_COMPLETO params
        SLOW = {"Bachmann_MSB2011", "Chen_MSB2009", "Isensee_JCB2018",
                "Lang_PLOSComputBiol2024", "Raimundez_PCB2020"}
        nombres = sorted(
            f.stem for f in SUBS.glob("*.json")
            if json.loads(f.read_text()).get("admisible") and f.stem not in SLOW
        )
    print(f"Running nested validation for {len(nombres)} problems with NPROC={NPROC}",
          flush=True)
    if JAC_NPROC > 1:
        # problems run one at a time in the main process (pool workers cannot fork their own)
        for n in nombres:
            _seguro(n)
    else:
        with Pool(NPROC) as pool:
            list(pool.imap_unordered(_seguro, nombres))
    print("Done.", flush=True)
