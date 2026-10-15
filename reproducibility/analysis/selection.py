#!/usr/bin/env python3
"""
Parameter selection of the paper (Fig. 1, Methods) for PEtab benchmark problems.

For each problem, on the noise-scaled measured outputs y (petab_problem.py):

1. Relative sensitivity matrix ``J = dy/dlog(theta)`` at theta0 by central differences with step
   delta = 1 % (2p simulations).
2. Only biological parameters (SBML parameters and condition parameters) are candidates;
   calibration parameters (observation scalings, offsets) are always re-estimated together with
   the selected ones and are not counted in |S|.
3. Greedy selection with permanent rejection: candidates in decreasing order; a candidate j is
   accepted if the condition number kappa and the largest variance inflation factor VIF of the
   standardised columns of S + {j} are both <= 10.
   * Stage 1: order by the sensitivity energy E_j = ||J_j||^2; stop when
     R_var(S) = sum_{j in S} E_j / sum_j E_j >= 0.89 and |S| >= 2.
   * If the stage-1 subset is not admissible, stage 2: order by the finite effect
     s_j = ||y(theta0 with theta_j * 1.1) - y(theta0)||; stop as soon as S is admissible.
4. Admissibility: 15 random scenarios theta = theta0 * (1 + 0.05 u), u ~ U(-1, 1)^p (seed 42).
   For each scenario the parameters of S (and the calibration parameters) are re-estimated by
   bounded least squares in log|theta| within [|theta0|/10, 10|theta0|] (trust-region reflective,
   two starting points: the scenario value and theta0) to reproduce the full-model output change;
   e_fit = ||Delta y_full - Delta y_S|| / ||Delta y_full||. S is admissible if |S| >= 2 and the
   median of e_fit is <= tau_e = sqrt(1 - 0.9^2) = 0.436. Since e_fit <= e_rel (the error without
   re-estimation), re-estimation is skipped when the median e_rel is already <= tau_e.
   For the eight problems in config.FIRST_ORDER, e_fit is computed to first order,
   min_c ||Delta y_full - J_S c|| / ||Delta y_full||, with the J already computed.
5. Backward elimination: each parameter of S is removed in turn (from the smallest to the largest
   E_j) while the subset remains admissible, until no parameter can be removed; the result is
   minimal with respect to inclusion (Lean: Poda.prune_minimal).

Usage
    python selection.py [Problem ...]                 # baseline -> results/selection/
    python selection.py --variant tauE_0.10 [Problem ...]   # one setting changed (Fig. 5)
                                                      # -> results/settings/tauE_0.10/
Without problem names, all 34 problems (baseline) or the 26 problems of Fig. 5 (variants) are run.
The environment variable NPROC sets the number of processes used for the largest problems.
Output: one JSON file per problem (keys described in README, "Data dictionary").
"""
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

import config as CFG

# ---- settings (a variant changes one of them; see config.SETTINGS_VARIANTS) -------------------
VARIANT = None
if "--variant" in sys.argv:
    _i = sys.argv.index("--variant")
    VARIANT = sys.argv[_i + 1]
    del sys.argv[_i:_i + 2]
    os.environ.update(CFG.SETTINGS_VARIANTS[VARIANT])   # before importing petab_problem (tolerances)

from petab_problem import PetabProblem  # noqa: E402

DELTA = float(os.environ.get("REPRO_DELTA", CFG.DELTA))
TAU_R = float(os.environ.get("REPRO_TAU_R", CFG.TAU_R))
TAU_KAPPA = TAU_VIF = float(os.environ.get("REPRO_TAU_K", CFG.TAU_KAPPA))
EPSILON = float(os.environ.get("REPRO_EPSILON", CFG.EPSILON))
TAU_E = float(os.environ.get("REPRO_TAU_E", CFG.TAU_E))
N_SCEN, SEED = CFG.N_SCENARIOS, CFG.SEED
NPROC = int(os.environ.get("NPROC", os.cpu_count() or 1))
OUT = CFG.SETTINGS / VARIANT if VARIANT else CFG.SELECTION


# --- kappa and VIF of the standardised columns ---------------------------------------------------
def _standardize(X):
    mu = X.mean(axis=0, keepdims=True)
    sd = X.std(axis=0, ddof=1, keepdims=True)
    sd = np.where(~np.isfinite(sd) | (sd < 1e-12), 1.0, sd)
    return np.nan_to_num((X - mu) / sd)


def kappa(J, idx):
    if len(idx) <= 1:
        return 1.0
    F = _standardize(J[:, idx])
    if np.allclose(F, 0):
        return float("inf")
    s = np.linalg.svd(F, compute_uv=False)
    return float("inf") if s[-1] < 1e-12 else float(s[0] / s[-1])


def vif(J, idx):
    if len(idx) <= 1:
        return 1.0
    F = _standardize(J[:, idx])
    C = np.nan_to_num(np.corrcoef(F, rowvar=False))
    np.fill_diagonal(C, 1.0)
    try:
        inv = np.linalg.inv(C)
    except np.linalg.LinAlgError:
        inv = np.linalg.pinv(C)
    v = np.diag(inv)
    return float(np.max(np.where(np.isfinite(v), v, np.inf)))


def greedy(J, order, stop):
    """Greedy selection with permanent rejection; `stop(S)` is the stopping rule of the stage."""
    S = []
    for j in order:
        k, v = kappa(J, S + [j]), vif(J, S + [j])
        if k <= TAU_KAPPA and v <= TAU_VIF:
            S.append(j)
            if stop(S):
                return S, True
    return S, False


# --- parallel evaluation for the largest problems: each process loads its own model copy --------
_SY = None
_Y0 = None


def _w_init(name):
    global _SY, _Y0
    _SY = PetabProblem(name)
    _Y0 = _SY.sim(_SY.theta0)


def _w_col(j):
    th0 = _SY.theta0
    tp, tm = th0.copy(), th0.copy()
    tp[j] *= 1 + DELTA; tm[j] *= 1 - DELTA
    yp, ym = _SY.sim(tp), _SY.sim(tm)
    if yp is None or ym is None:
        return j, None
    return j, (yp - ym).ravel() / (2 * DELTA)


def _w_scan(j):
    th0, y0 = _SY.theta0, _Y0
    tp = th0.copy(); tp[j] *= 1 + CFG.ETA
    yp = _SY.sim(tp)
    return j, (float(np.linalg.norm((yp - y0).ravel())) if yp is not None and y0 is not None
               else 0.0)


def select(name):
    t0 = time.time()
    first_order = name in CFG.FIRST_ORDER
    Sy = PetabProblem(name)
    names, th0 = Sy.names, Sy.theta0
    p = len(names)
    # problems with p > 200 or with slow simulations: J and s on disk (float32), resumable
    cached = p > 200 or first_order
    y0 = Sy.sim(th0)
    if y0 is None:
        return {"sistema": name, "etapa": "Técnico", "motivo": "la simulación nominal falla",
                "admisible": False}
    act = np.nonzero(Sy.in_model)[0]
    CAL = [int(j) for j in act if Sy.calib[j]]
    act = np.array([j for j in act if not Sy.calib[j]], dtype=int)
    # --- relative J by central differences in log(theta), for the biological AND the calibration
    # parameters: the first-order re-estimation uses J[:, S + CAL], so the calibration columns are
    # needed (an earlier version computed only the biological columns; see README, "Corrections")
    cols_J = [int(j) for j in act] + CAL
    if cached:
        CFG.CACHE.mkdir(parents=True, exist_ok=True)
        fJ, fm = CFG.CACHE / f"{name}_J.npy", CFG.CACHE / f"{name}_J_done.npy"
        if fJ.exists() and fm.exists():
            J = np.load(fJ, mmap_mode="r+"); done = np.load(fm)
        else:
            J = np.lib.format.open_memmap(fJ, mode="w+", dtype=np.float32, shape=(y0.size, p))
            done = np.zeros(p, dtype=bool)
        pend = [j for j in cols_J if not done[j]]
        print(f"  J: {int(done.sum())} columns already done, {len(pend)} to go", flush=True)
        with Pool(NPROC, initializer=_w_init, initargs=(name,)) as pool:
            for k, (j, col) in enumerate(pool.imap_unordered(_w_col, pend, chunksize=8)):
                if col is not None:
                    J[:, j] = col
                done[j] = True
                if k % 10 == 0:
                    J.flush(); np.save(fm, done)
                    print(f"  J: {int(done.sum())}/{len(cols_J)} columns", flush=True)
        J.flush(); np.save(fm, done)
        J = np.asarray(J, dtype=float) if J.nbytes < 4e9 else J
    else:
        J = np.zeros((y0.size, p))
        for j in cols_J:
            tp, tm = th0.copy(), th0.copy()
            tp[j] *= 1 + DELTA; tm[j] *= 1 - DELTA
            yp, ym = Sy.sim(tp), Sy.sim(tm)
            if yp is not None and ym is not None:
                J[:, j] = (yp - ym).ravel() / (2 * DELTA)
    E = np.sum(J ** 2, axis=0)
    tot = float(E[act].sum())
    if not tot > 0:
        return {"sistema": name, "p": p, "etapa": "Técnico",
                "motivo": "Jacobiano nulo (ningún parámetro dinámico afecta a las salidas medidas)",
                "admisible": False}
    rvar = lambda S: float(E[S].sum() / tot) if tot > 0 else float("nan")  # noqa: E731
    # --- admissibility scenarios
    rng = np.random.default_rng(SEED)
    scen = [th0 * (1 + EPSILON * rng.uniform(-1, 1, size=p))
            for _ in range(N_SCEN)]
    full = []
    for th in scen:
        yf = Sy.sim(th)
        full.append(None if yf is None else (yf - y0).ravel())
    floor = max(1e-10 * np.linalg.norm(y0), 1e-6)   # scenarios with a smaller change are discarded

    def validate(S):
        """Median cos(Delta) and e_rel over the scenarios (S set to the scenario values)."""
        S = list(S) + CAL          # calibration parameters always accompany S
        cs, es = [], []
        for th, df_ in zip(scen, full):
            if df_ is None or np.linalg.norm(df_) < floor:
                continue
            ts = th0.copy(); ts[S] = th[S]
            ys = Sy.sim(ts)
            if ys is None:
                continue
            ds_ = (ys - y0).ravel()
            nf, ns = np.linalg.norm(df_), np.linalg.norm(ds_)
            if ns == 0:
                cs.append(0.0); es.append(1.0); continue
            cs.append(float(df_ @ ds_ / (nf * ns)))
            es.append(float(np.linalg.norm(df_ - ds_) / nf))
        if not cs:
            return float("nan"), float("nan"), 0
        return float(np.median(cs)), float(np.median(es)), len(cs)

    from scipy.optimize import least_squares

    def efit(S):
        """Median e_fit (re-estimation of S and of the calibration parameters).
        First order for the problems in config.FIRST_ORDER: min_c ||Dy_full - J_S c|| / ||Dy_full||
        with the J already computed (no additional simulations)."""
        S = list(S) + CAL          # calibration parameters are always re-estimated
        if first_order:
            Js = np.asarray(J[:, S], dtype=float)
            es = []
            for df_ in full:
                if df_ is None or np.linalg.norm(df_) < floor:
                    continue
                c_, *_ = np.linalg.lstsq(Js, df_, rcond=None)
                es.append(float(np.linalg.norm(df_ - Js @ c_) / np.linalg.norm(df_)))
            return float(np.median(es)) if es else float("nan")
        sgn = np.where(th0[S] < 0, -1.0, 1.0)
        mag0 = np.maximum(np.abs(th0[S]), 1e-12)
        lo, hi = np.log(mag0 / 10), np.log(mag0 * 10)
        es = []
        for th, df_ in zip(scen, full):
            if df_ is None or np.linalg.norm(df_) < floor:
                continue
            nf = np.linalg.norm(df_)
            yf = y0.ravel() + df_

            def resid(u):
                ts = th0.copy(); ts[S] = sgn * np.exp(u)
                ys = Sy.sim(ts)
                return np.full(yf.size, 10.0) if ys is None else (ys.ravel() - yf) / nf
            r0 = resid(np.log(np.maximum(np.abs(th[S]), 1e-12)))
            best = float(np.linalg.norm(r0))          # value without re-estimation (e_rel)
            x_scen = np.clip(np.log(np.maximum(np.abs(th[S]), 1e-12)), lo, hi)
            for x0 in (np.log(mag0), x_scen):
                try:
                    r = least_squares(resid, x0, bounds=(lo, hi), method="trf",
                                      max_nfev=100 * (len(S) + 1), diff_step=1e-3)
                    best = min(best, float(np.linalg.norm(r.fun)))
                except Exception:
                    pass
            es.append(best)
        return float(np.median(es)) if es else float("nan")

    memo_fit, memo_val = {}, {}
    # large problems: e_rel and e_fit already computed are stored on disk to resume
    f_fit = CFG.CACHE / f"{name}_fits.json" if cached else None
    if f_fit is not None and f_fit.exists():
        _d = json.loads(f_fit.read_text())
        memo_fit = {tuple(json.loads(k)): v for k, v in _d.get("aj", {}).items()}
        memo_val = {tuple(json.loads(k)): tuple(v) for k, v in _d.get("va", {}).items()}

    def _save():
        if f_fit is not None:
            f_fit.parent.mkdir(parents=True, exist_ok=True)
            f_fit.write_text(json.dumps({
                "aj": {json.dumps(list(k)): v for k, v in memo_fit.items()},
                "va": {json.dumps(list(k)): list(v) for k, v in memo_val.items()}}))

    def admissible(S):
        """|S| >= 2 and median e_fit <= tau_e (no re-estimation if already median e_rel <= tau_e)."""
        if len(S) < CFG.K_MIN:
            return False
        key = tuple(S)
        if key not in memo_val:
            memo_val[key] = validate(S); _save()
        c, e, n = memo_val[key]
        if np.isfinite(e) and e <= TAU_E:
            return True
        if key not in memo_fit:
            memo_fit[key] = efit(S); _save()
        return bool(np.isfinite(memo_fit[key]) and memo_fit[key] <= TAU_E)

    res = {"sistema": name, "p": p}
    # --- stage 1
    order1 = [int(j) for j in act[np.argsort(-E[act])] if E[j] > 0]
    S1, ok1 = greedy(J, order1, lambda S: rvar(S) >= TAU_R and len(S) >= CFG.K_MIN)
    res.update({"S1": [names[j] for j in S1], "Rvar_S1_%": 100 * rvar(S1) if S1 else 0.0,
                "S1_cumple": ok1})
    pass1 = False
    if ok1:
        c, e, n = validate(S1)
        res.update({"cos_S1": c, "erel_S1": e})
        pass1 = admissible(S1)
    if pass1:
        res.update({"etapa": "Stage 1", "S": res["S1"], "Rvar_%": 100 * rvar(S1),
                    "kappa": kappa(J, S1), "VIF": vif(J, S1), "cos_med": c, "erel_med": e,
                    "n_escenarios": n})
    else:
        if ok1:
            res["motivo_stage2"] = "Stage 1 cumple R_var pero no es admisible"
        # --- stage 2: finite effect s_j of a 10 % change of each parameter
        s = np.zeros(p)
        if cached:
            CFG.CACHE.mkdir(parents=True, exist_ok=True)
            fs, fsm = CFG.CACHE / f"{name}_s.npy", CFG.CACHE / f"{name}_s_done.npy"
            hs = np.zeros(p, dtype=bool)
            if fs.exists() and fsm.exists():
                s, hs = np.load(fs), np.load(fsm)
            pend = [int(j) for j in act if not hs[j]]
            with Pool(NPROC, initializer=_w_init, initargs=(name,)) as pool:
                for k, (j, v) in enumerate(pool.imap_unordered(_w_scan, pend, chunksize=8)):
                    s[j] = v; hs[j] = True
                    if k % 10 == 0:
                        np.save(fs, s); np.save(fsm, hs)
                        print(f"  finite effects: {int(hs.sum())}/{len(act)}", flush=True)
            np.save(fs, s); np.save(fsm, hs)
        else:
            for j in act:
                tp = th0.copy(); tp[j] *= 1 + CFG.ETA
                yp = Sy.sim(tp)
                s[j] = np.linalg.norm((yp - y0).ravel()) if yp is not None else 0.0
        order2 = [int(j) for j in act[np.argsort(-s[act])] if s[j] > 0]
        S2, ok2 = greedy(J, order2, admissible)
        c, e, n = validate(S2) if S2 else (float("nan"), float("nan"), 0)
        res.update({"etapa": "Stage 2", "S": [names[j] for j in S2],
                    "Rvar_%": 100 * rvar(S2) if S2 else 0.0,
                    "kappa": kappa(J, S2) if S2 else float("nan"),
                    "VIF": vif(J, S2) if S2 else float("nan"),
                    "cos_med": c, "erel_med": e, "n_escenarios": n})
    # --- backward elimination: try to remove each parameter, from the least to the most
    # influential (E_j), while the subset remains admissible; repeat until none can be removed.
    # Result: minimal with respect to inclusion (Lean: Poda.prune_minimal).
    Sp = [names.index(q) for q in res["S"]]
    res["S_antes_poda"] = list(res["S"])
    if admissible(Sp):
        changed = True
        while changed:
            changed = False
            for j in sorted(Sp, key=lambda k: E[k]):
                sub = [k for k in Sp if k != j]
                if admissible(sub):
                    Sp = sub
                    changed = True
                    break
        c, e, n = validate(Sp)
        res.update({"S": [names[j] for j in Sp], "Rvar_%": 100 * rvar(Sp),
                    "kappa": kappa(J, Sp), "VIF": vif(J, Sp),
                    "cos_med": c, "erel_med": e, "n_escenarios": n})
    res["podados"] = [q for q in res["S_antes_poda"] if q not in res["S"]]
    # --- final e_fit and admissibility
    Sf = [names.index(q) for q in res["S"]]
    if tuple(Sf) in memo_fit:
        res["eajuste_med"] = memo_fit[tuple(Sf)]     # already computed during the selection
    elif len(Sf) >= 1 and (p <= 200 or len(Sf) <= 10):
        res["eajuste_med"] = efit(Sf)
    else:
        # very large problems: bound e_fit <= e_rel (the point without re-estimation)
        res["eajuste_med"] = None
        res["eajuste_cota"] = res["erel_med"]
    e_fit = res["eajuste_med"] if res["eajuste_med"] is not None else res["erel_med"]
    res["admisible"] = bool(len(Sf) >= CFG.K_MIN and np.isfinite(e_fit) and
                            min(e_fit, res["erel_med"]) <= TAU_E)
    res["calibracion"] = [names[j] for j in CAL]
    if first_order:
        res["eajuste_metodo"] = "linealizado (primer orden, J relativa)"
    res["segundos"] = round(time.time() - t0, 1)
    return res


if __name__ == "__main__":
    which = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not which:
        which = CFG.SETTINGS_PROBLEMS if VARIANT else CFG.PROBLEMS
    OUT.mkdir(parents=True, exist_ok=True)
    for name in which:
        print(f"== {name}", flush=True)
        try:
            r = select(name)
        except Exception as ex:
            r = {"sistema": name, "error": repr(ex)}
        print(json.dumps(r, default=str), flush=True)
        (OUT / f"{name}.json").write_text(json.dumps(r, default=str, indent=1))
