#!/usr/bin/env python3
"""
Nested external validation (leakage-free).

For each admissible problem, this script:
  1. Fits the FULL model on training data only  --> th_full_train  (= theta0_train)
  2. Fits the REDUCED model (S + calibration) starting from th_full_train,
     with non-selected parameters fixed at th_full_train (not at theta0).
  3. Reports chi2/n on the test set for both approaches side by side.

This addresses the data-leakage concern: theta0 was estimated with ALL data
(including test). By using th_full_train as the fixed-parameter anchor we
ensure the test set was never seen when constructing the reduced model.

The SAME selected subset S from the original analysis is used (selection was
done at theta0, but selection only computes derivatives -- it does not use
test labels -- so this is the conservative/fair choice).

Usage:
    python3 validacion_anidada.py [Problem ...]

Output: resultados/validacion_anidada/<problem>.json
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
import petab_outputs as PO

HERE = Path(__file__).resolve().parent
SUBS = HERE / "resultados" / "reclasificacion_salidas_bio_poda"
OUTD = HERE / "resultados" / "validacion_anidada"
ORIG = HERE / "resultados" / "validacion_externa_bio"   # original results for comparison
P_MAX_COMPLETO = int(os.environ.get("VAL_PMAX", 60))
NPROC = int(os.environ.get("NPROC", 4))


# ── helpers (same as validacion_externa.py) ──────────────────────────────────

def division(S):
    G = list(range(len(S.groups)))
    if len(G) >= 2:
        orden = sorted(G, key=lambda g: (S.groups[g][1], S.groups[g][0]))
        test = [orden[1]] if len(orden) == 2 else [g for i, g in enumerate(orden) if i % 3 == 2]
        train = [g for g in G if g not in test]
        filas_test = np.zeros(S.n_meas, bool)
        for g in test:
            filas_test[[r[0] for r in S.groups[g][3]]] = True
        return train, test, filas_test, "condiciones nuevas"
    t = S.mea["time"].astype(float).to_numpy()
    tu = np.unique(t[np.isfinite(t)])
    corte = tu[int(np.floor(2 * len(tu) / 3))] if len(tu) >= 3 else np.inf
    return G, G, t >= corte, f"extrapolacion temporal (t >= {corte:g})"


def refs_grupo(S, g):
    pre, sim_c, _, rows = S.groups[g]
    out = set()
    for c in (pre, sim_c):
        out |= {v for _, v in S.cond.get(c, []) if isinstance(v, str)}
    for _, _, _, op, npar in rows:
        out |= {v for v in op + npar if not PO._isnum(v)}
    return out


def locales_de_prueba(S, train, test):
    if set(train) == set(test):
        return set()
    rt = set().union(*[refs_grupo(S, g) for g in test]) if test else set()
    rr = set().union(*[refs_grupo(S, g) for g in train]) if train else set()
    compartidos = set(S.gparams)
    for f, g, _ in S.obs.values():
        compartidos |= {str(x) for x in f.free_symbols | g.free_symbols}
    return {S.idx[n] for n in rt - rr - compartidos if n in S.idx}


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

    def theta(u):
        t = th_ini.copy(); t[libres] = sgn * np.exp(u)
        return t

    mejor = {"c": np.inf, "u": x0.copy(), "n": 0}

    def res(u):
        z = S.z(theta(u), gidx)
        r = np.full(int(filas.sum()), 1e3) if z is None else z[filas] - objetivo[filas]
        r = np.where(np.isfinite(r), r, 1e3)
        mejor["n"] += 1
        c = float(r @ r)
        if c < mejor["c"]:
            mejor["c"], mejor["u"] = c, np.array(u, copy=True)
        return r

    try:
        r = least_squares(res, x0, bounds=(lo, hi), method="trf", max_nfev=max_nfev, diff_step=1e-3)
        th = theta(r.x)
        if ckpt is not None:
            np.savez(ckpt, u=r.x, terminado=True, nfev=int(r.nfev))
        return th, int(r.nfev)
    except Exception:
        return th_ini.copy(), 0


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

    S = PO.PSys(name)
    th0 = S.theta0.copy()

    Ssel = [S.names.index(q) for q in info["S"] if q in S.names]
    n_bio = len(Ssel)
    Ssel += [S.names.index(q) for q in info.get("calibracion", []) if q in S.names]
    libres_full = [int(j) for j in np.nonzero(S.in_model)[0]]

    train, test, ftest, tipo = division(S)
    ftrain = ~ftest

    if not ftrain.any() or not ftest.any():
        return {"sistema": name, "no_evaluable": "single condition/time"}

    loc = locales_de_prueba(S, train, test)
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
    with Pool(NPROC) as pool:
        list(pool.imap_unordered(_seguro, nombres))
    print("Done.", flush=True)
