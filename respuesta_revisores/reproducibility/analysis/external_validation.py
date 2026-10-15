#!/usr/bin/env python3
"""
External validation of the reduced models (Fig. 3, Supplementary Note "Synthetic prediction
experiment"): does the subset S, fitted to part of the experiments, predict experiments that were
not used for fitting?

Data: PEtab measurements in the scale of the likelihood, z_i = h(data_i)/sigma_i, and predictions
z_i(theta) = h(g_i(x(t_i), theta))/sigma_i (petab_problem.py). S = final subset of
results/selection/; its calibration parameters are always re-estimated together with it.

Training/test split (deterministic):
  * problems with >= 2 experimental conditions: conditions sorted by identifier; the one at
    position 3k+2 goes to the test set (with 2 conditions: the second) -> new conditions;
  * problems with 1 condition: times after the 2/3 quantile of the distinct measurement times go
    to the test set -> extrapolation in time.

Fits (scipy least_squares, 'trf', in signed log|theta|, bounds [|theta0|/10, 10|theta0|], from theta0):
  * REDUCED model: only S (and the calibration parameters) free, the rest fixed at theta0;
  * FULL model: all parameters that affect y free; not done for Chen and Lang (155 and 277
    parameters with slow simulations, days to weeks of computation).
Parameters that only act in test conditions (e.g. R0_NY when predicting New York from California)
cannot be learned from the training data: they are excluded from both fits and, in experiment B,
their true value is theta0. If S only contains such parameters, or if there is a single condition
and a single measurement time, the problem is marked "no_evaluable".

Experiment A (real data): fit to the real training data; test metric chi2/n = mean of
  (z_pred - z)^2 (about 1 when the error is of the size of the noise). theta0 (estimated by the
  original authors with ALL data, test data included) is reported as an optimistic reference.
Experiment B (synthetic data with noise, no information leak): truth theta* = theta0 (1 + 0.2 u),
  u ~ U(-1, 1) (seed 42), data z* + eps, eps ~ N(0, 1) (noise of the size of sigma). The parameters
  that are not selected stay at theta0 != theta* (realistic situation). Test metrics: chi2/n with
  respect to the noisy data and e_pred = ||z_pred - z*|| / ||z* - z(theta0)|| (relative prediction
  error with respect to the truth, comparable with the threshold 0.436 of e_fit).

Usage: python external_validation.py [Problem ...]   (default: all admissible problems)
Output: results/external_validation/<problem>.json. Long fits save checkpoints every
VAL_CKPT_MIN minutes (default 10) in results/external_validation/checkpoints/ and resume from them.
"""
import json
import os
import sys
import time
import warnings
from multiprocessing import Pool

import numpy as np
from scipy.optimize import least_squares

warnings.filterwarnings("ignore")
import config as CFG  # noqa: E402
import petab_problem as PP  # noqa: E402

SUBSETS = CFG.SELECTION
OUT = CFG.VALIDATION
FULL_FIT_SKIPPED = {"Chen_MSB2009", "Lang_PLOSComputBiol2024"}
SEED, TRUTH_LEVEL = CFG.SEED, 0.20
CKPT_MIN = float(os.environ.get("VAL_CKPT_MIN", 10))
CKDIR = {"dir": None, "resumed": []}


def split(S):
    """Return (training groups, test groups, mask of test rows, kind of split)."""
    G = list(range(len(S.groups)))
    if len(G) >= 2:
        order = sorted(G, key=lambda g: (S.groups[g][1], S.groups[g][0]))
        test = [order[1]] if len(order) == 2 else [g for i, g in enumerate(order) if i % 3 == 2]
        train = [g for g in G if g not in test]
        rows_test = np.zeros(S.n_meas, bool)
        for g in test:
            rows_test[[r[0] for r in S.groups[g][3]]] = True
        return train, test, rows_test, "condiciones nuevas"
    t = S.mea["time"].astype(float).to_numpy()
    tu = np.unique(t[np.isfinite(t)])
    cut = tu[int(np.floor(2 * len(tu) / 3))] if len(tu) >= 3 else np.inf
    return G, G, t >= cut, f"extrapolación temporal (t ≥ {cut:g})"


def group_refs(S, g):
    """Parameter identifiers used by group g (overrides of its condition and of its
    pre-equilibration, and observable/noise parameters of its rows)."""
    pre, sim_c, _, rows = S.groups[g]
    out = set()
    for c in (pre, sim_c):
        out |= {v for _, v in S.cond.get(c, []) if isinstance(v, str)}
    for _, _, _, op, npar in rows:
        out |= {v for v in op + npar if not PP.is_number(v)}
    return out


def test_only_parameters(S, train, test):
    """Parameters that only act in the test conditions: no fit to the training data can estimate
    them, neither with the reduced nor with the full model."""
    if set(train) == set(test):
        return set()
    rt = set().union(*[group_refs(S, g) for g in test]) if test else set()
    rr = set().union(*[group_refs(S, g) for g in train]) if train else set()
    shared = set(S.gparams)
    for f, g, _ in S.obs.values():
        shared |= {str(x) for x in f.free_symbols | g.free_symbols}
    return {S.idx[n] for n in rt - rr - shared if n in S.idx}


def fit(S, free, th_ini, gidx, target, rows, max_nfev, tag=None):
    th0 = S.theta0
    sgn = np.where(th0[free] < 0, -1.0, 1.0)
    mag0 = np.maximum(np.abs(th0[free]), 1e-12)
    lo, hi = np.log(mag0 / 10), np.log(mag0 * 10)
    x0 = np.clip(np.log(np.maximum(np.abs(th_ini[free]), 1e-12)), lo + 1e-9, hi - 1e-9)

    def theta(u):
        t = th_ini.copy(); t[free] = sgn * np.exp(u)
        return t

    ck = CKDIR["dir"] / f"{tag}.npz" if (tag and CKDIR["dir"] is not None) else None
    if ck is not None and ck.exists():
        d = np.load(ck)
        if len(d["u"]) == len(free):
            if bool(d["terminado"]):
                return theta(d["u"]), int(d["nfev"])
            x0 = np.clip(d["u"], lo + 1e-9, hi - 1e-9)       # continue from the best saved theta
            CKDIR["resumed"].append(tag)
    best = {"c": np.inf, "u": x0.copy(), "n": 0, "t": time.time()}

    def save(u, finished, nfev):
        if ck is not None:
            tmp = ck.with_suffix(".tmp.npz")
            np.savez(tmp, u=u, terminado=finished, nfev=nfev)
            os.replace(tmp, ck)

    def res(u):
        z = S.z(theta(u), gidx)
        if z is None:
            r = np.full(int(rows.sum()), 1e3)
        else:
            r = z[rows] - target[rows]
            r = np.where(np.isfinite(r), r, 1e3)
        best["n"] += 1
        c = float(r @ r)
        if c < best["c"]:
            best["c"], best["u"] = c, np.array(u, copy=True)
        if time.time() - best["t"] >= 60 * CKPT_MIN:
            save(best["u"], False, best["n"]); best["t"] = time.time()
        return r

    try:
        r = least_squares(res, x0, bounds=(lo, hi), method="trf", max_nfev=max_nfev,
                          diff_step=1e-3)
        save(r.x, True, int(r.nfev))
        return theta(r.x), int(r.nfev)
    except Exception:
        return th_ini.copy(), 0


def chi2(z, target, rows):
    if z is None:
        return float("nan")
    r = z[rows] - target[rows]
    r = r[np.isfinite(r)]
    return float(np.mean(r ** 2)) if len(r) else float("nan")


def validate(name, subset=None):
    """External validation of the selected subset of `name`, or of `subset` (list of parameter
    names, e.g. a single parameter) with the same calibration parameters."""
    t0 = time.time()
    info = json.loads((SUBSETS / f"{name}.json").read_text())
    if subset is not None:
        info = dict(info, S=list(subset))
    S = PP.PetabProblem(name)
    th0 = S.theta0
    CKDIR["dir"] = OUT / "checkpoints" / (name if subset is None else name + "_" + "_".join(subset))
    CKDIR["dir"].mkdir(parents=True, exist_ok=True)
    CKDIR["resumed"] = []
    Ssel = [S.names.index(q) for q in info["S"] if q in S.names]
    n_bio = len(Ssel)
    Ssel += [S.names.index(q) for q in info.get("calibracion", []) if q in S.names]
    free_full = [int(j) for j in np.nonzero(S.in_model)[0]]
    train, test, ftest, kind = split(S)
    ftrain_all = ~ftest
    if not ftrain_all.any() or not ftest.any():
        return {"sistema": name, "division": kind, "n_condiciones": len(S.groups),
                "no_evaluable": "una sola condición y un solo tiempo de medición "
                                "(no se puede separar entrenamiento y prueba)"}
    loc = test_only_parameters(S, train, test)
    res = {"sistema": name, "division": kind, "n_condiciones": len(S.groups),
           "n_train": int(ftrain_all.sum()), "n_test": int(ftest.sum()),
           "S": info["S"], "|S|": n_bio, "n_calibracion": len(Ssel) - n_bio,
           "p_y": len(free_full),
           "locales_prueba": [S.names[j] for j in sorted(loc)],
           "S_locales_prueba": [S.names[j] for j in Ssel if j in loc]}
    # parameters that only act in the test conditions cannot be estimated from the training data
    Ssel = [j for j in Ssel if j not in loc]
    free_full = [j for j in free_full if j not in loc]
    if len(Ssel) == 0:
        res["no_evaluable"] = ("todos los parámetros de S son exclusivos de las condiciones de "
                               "prueba")
        return res
    do_full = name not in FULL_FIT_SKIPPED
    nf_red, nf_full = 30 * (len(Ssel) + 1), 15 * (len(free_full) + 1)

    # ---------------- A: real data
    zd = S.zdata()
    ftr = ftrain_all & np.isfinite(zd)
    fte = ftest & np.isfinite(zd)
    z0 = S.z(th0)
    res["A_chi2_test_theta0"] = chi2(z0, zd, fte)
    th_r, _ = fit(S, Ssel, th0, train, zd, ftr, nf_red, "A_red")
    zr = S.z(th_r)
    res["A_chi2_train_red"] = chi2(zr, zd, ftr)
    res["A_chi2_test_red"] = chi2(zr, zd, fte)
    if do_full:
        th_f, _ = fit(S, free_full, th0, train, zd, ftr, nf_full, "A_full")
        zf = S.z(th_f)
        res["A_chi2_train_full"] = chi2(zf, zd, ftr)
        res["A_chi2_test_full"] = chi2(zf, zd, fte)

    # ---------------- B: synthetic data with noise (truth unknown to the fit)
    rng = np.random.default_rng(SEED)
    u = rng.uniform(-1, 1, size=len(th0))
    th_true = th0.copy()
    th_true[free_full] = th0[free_full] * (1 + TRUTH_LEVEL * u[free_full])
    # (parameters that only act in the test conditions stay at theta0 in the truth: they cannot
    #  be learned from other conditions)
    zt = S.z(th_true)
    if zt is None:
        res["B_error"] = "la simulación de la verdad θ* falla"
    else:
        data = zt + rng.standard_normal(len(zt))
        ftr_b, fte_b = ftrain_all.copy(), ftest.copy()
        th_rb, _ = fit(S, Ssel, th0, train, data, ftr_b, nf_red, "B_red")
        zrb = S.z(th_rb)
        den = np.linalg.norm((zt - z0)[fte_b])
        res["B_chi2_test_theta0"] = chi2(z0, data, fte_b)
        res["B_chi2_test_red"] = chi2(zrb, data, fte_b)
        res["B_epred_red"] = (float(np.linalg.norm((zrb - zt)[fte_b]) / den)
                              if zrb is not None and den > 0 else float("nan"))
        res["B_epred_theta0"] = 1.0
        if do_full:
            th_fb, _ = fit(S, free_full, th0, train, data, ftr_b, nf_full, "B_full")
            zfb = S.z(th_fb)
            res["B_chi2_test_full"] = chi2(zfb, data, fte_b)
            res["B_epred_full"] = (float(np.linalg.norm((zfb - zt)[fte_b]) / den)
                                   if zfb is not None and den > 0 else float("nan"))
    res["segundos"] = round(time.time() - t0, 1)
    if CKDIR["resumed"]:
        res["etapas_reanudadas"] = list(CKDIR["resumed"])   # continued from a checkpoint
    return res


def _safe(name):
    try:
        r = validate(name)
    except Exception as e:
        r = {"sistema": name, "error": repr(e)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps(r, indent=1, default=str), encoding="utf-8")
    print(json.dumps(r, default=str), flush=True)
    return r


if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not names:
        for f in sorted(SUBSETS.glob("*.json")):
            d = json.loads(f.read_text())
            if d.get("admisible") and len(d.get("S", [])) >= 2:
                names.append(f.stem)
    with Pool(int(os.environ.get("NPROC", 2))) as pool:
        list(pool.imap_unordered(_safe, names))
