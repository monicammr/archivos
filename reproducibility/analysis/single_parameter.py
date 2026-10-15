#!/usr/bin/env python3
"""
Single-parameter subsets (Supplementary Note "Single-parameter subsets"; justification of the
minimum size k_min = 2).

For every admissible problem of results/selection/, the candidates are the K = 10 biological
parameters with the largest sensitivity energy E_j and the K = 10 with the largest finite effect
s_j (the two orderings of the method). Each candidate j is tested ALONE, with the calibration
parameters re-estimated together with it as in the method: {j} is admissible if the median e_fit
over the same 15 scenarios at +-5 % (seed 42) is <= 0.436 (without the requirement |S| >= 2).
For the best admissible candidate j* (smallest median e_fit) the script also computes
  * the median e_fit at +-10 % for {j*} and for the selected subset S (same scenarios);
  * the external validation of {j*} (real data: test chi2/n; synthetic data: e_pred), exactly as
    for S (external_validation.validate, with the same calibration parameters).
The five problems in SLOW are not included (repeated nonlinear re-estimation is too costly).

Usage: python single_parameter.py [Problem ...]
Output: results/single_parameter/<problem>.json
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
import external_validation as EV  # noqa: E402
import petab_problem as PP  # noqa: E402

SEL = CFG.SELECTION
OUT = CFG.SINGLE
TAU_E = CFG.TAU_E
K, DELTA = 10, CFG.DELTA
N_SCEN, SEED = CFG.N_SCENARIOS, CFG.SEED
SLOW = {"Bachmann_MSB2011", "Chen_MSB2009", "Isensee_JCB2018", "Lang_PLOSComputBiol2024", "Raimundez_PCB2020"}


class Evaluator:
    """Scenarios theta0 * (1 + level * u), u ~ U(-1, 1)^p (seed 42), and the errors e_rel and
    e_fit of a subset of parameter indices."""

    def __init__(self, name, level):
        self.S = PP.PetabProblem(name)
        th0 = self.th0 = self.S.theta0
        self.y0 = self.S.sim(th0).ravel()
        p = len(th0)
        rng = np.random.default_rng(SEED)
        self.scen = [th0 * (1 + level * rng.uniform(-1, 1, size=p))
                     for _ in range(N_SCEN)]
        floor = max(1e-10 * np.linalg.norm(self.y0), 1e-6)
        self.full = []
        for th in self.scen:
            yf = self.S.sim(th)
            d = None if yf is None else yf.ravel() - self.y0
            self.full.append(d if d is not None and np.linalg.norm(d) >= floor else None)

    def erel(self, idx):
        es = []
        for th, d in zip(self.scen, self.full):
            if d is None:
                continue
            ts = self.th0.copy(); ts[idx] = th[idx]
            ys = self.S.sim(ts)
            if ys is None:
                continue
            es.append(np.linalg.norm(d - (ys.ravel() - self.y0)) / np.linalg.norm(d))
        return float(np.median(es)) if es else float("nan")

    def efit(self, idx):
        th0 = self.th0
        sgn = np.where(th0[idx] < 0, -1.0, 1.0)
        mag0 = np.maximum(np.abs(th0[idx]), 1e-12)
        lo, hi = np.log(mag0 / 10), np.log(mag0 * 10)
        es = []
        for th, d in zip(self.scen, self.full):
            if d is None:
                continue
            nf = np.linalg.norm(d)
            yf = self.y0 + d

            def resid(u):
                ts = th0.copy(); ts[idx] = sgn * np.exp(u)
                ys = self.S.sim(ts)
                return np.full(yf.size, 10.0) if ys is None else (ys.ravel() - yf) / nf

            best = float(np.linalg.norm(resid(np.log(np.maximum(np.abs(th[idx]), 1e-12)))))
            for x0 in (np.log(mag0), np.clip(np.log(np.maximum(np.abs(th[idx]), 1e-12)), lo, hi)):
                try:
                    r = least_squares(resid, x0, bounds=(lo, hi), method="trf",
                                      max_nfev=100 * (len(idx) + 1), diff_step=1e-3)
                    best = min(best, float(np.linalg.norm(r.fun)))
                except Exception:
                    pass
            es.append(best)
        return float(np.median(es)) if es else float("nan")


def validate_single(name, jbest):
    """External validation of {j*} exactly as for the selected subset S (same calibration
    parameters, re-estimated together with j*)."""
    return EV.validate(name, subset=[jbest])


def evaluate(name):
    t0 = time.time()
    info = json.loads((SEL / f"{name}.json").read_text())
    ev = Evaluator(name, CFG.EPSILON)
    Sy = ev.S
    names = Sy.names
    cal = [names.index(q) for q in info.get("calibracion", []) if q in names]
    bio = [int(j) for j in np.nonzero(Sy.in_model)[0] if not Sy.calib[j]]
    E, s = np.zeros(len(ev.th0)), np.zeros(len(ev.th0))
    for j in bio:
        tp, tm = ev.th0.copy(), ev.th0.copy()
        tp[j] *= 1 + DELTA; tm[j] *= 1 - DELTA
        yp, ym = Sy.sim(tp), Sy.sim(tm)
        if yp is not None and ym is not None:
            E[j] = float(np.sum(((yp - ym).ravel() / (2 * DELTA)) ** 2))
        t1 = ev.th0.copy(); t1[j] *= 1.1
        y1 = Sy.sim(t1)
        s[j] = float(np.linalg.norm(y1.ravel() - ev.y0)) if y1 is not None else 0.0
    cand = []
    for order in (np.argsort(-E), np.argsort(-s)):
        for j in order[:K]:
            j = int(j)
            if j in bio and j not in cand and (E[j] > 0 or s[j] > 0):
                cand.append(j)
    singles = []
    for j in cand:
        idx = [j] + cal
        e = ev.erel(idx)
        a = ev.efit(idx) if not (np.isfinite(e) and e <= TAU_E) else e
        singles.append({"parametro": names[j], "e_rel": e, "e_fit": min(a, e) if np.isfinite(e) else a,
                        "admisible": bool(np.isfinite(a) and min(a, e if np.isfinite(e) else a) <= TAU_E)})
    res = {"sistema": name, "S": info["S"], "calibracion": info.get("calibracion", []),
           "candidatos": len(cand), "un_parametro": singles,
           "algun_parametro_solo_basta": any(x["admisible"] for x in singles)}
    ok = [x for x in singles if x["admisible"]]
    if ok:
        jbest = min(ok, key=lambda x: x["e_fit"])["parametro"]
        res["mejor"] = jbest
        ev10 = Evaluator(name, 0.10)
        jb = [names.index(jbest)] + cal
        Sf = [names.index(q) for q in info["S"]] + cal
        res["mejor_efit_10"] = ev10.efit(jb)
        res["S_efit_10"] = ev10.efit(Sf)
        v = validate_single(name, jbest)
        res["mejor_validacion"] = {k: v.get(k) for k in ("A_chi2_test_red", "B_chi2_test_theta0", "B_epred_red",
                                                         "no_evaluable", "B_error")}
        res["mejor_validacion_calibracion"] = len(cal)
    res["segundos"] = round(time.time() - t0, 1)
    return res


def _safe(name):
    try:
        r = evaluate(name)
    except Exception as e:
        r = {"sistema": name, "error": repr(e)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps(r, indent=1, default=str))
    print(json.dumps({k: r.get(k) for k in ("sistema", "algun_parametro_solo_basta", "mejor", "error", "segundos")}), flush=True)


if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not names:
        names = sorted(f.stem for f in SEL.glob("*.json")
                       if json.loads(f.read_text())["admisible"] and f.stem not in SLOW)
    with Pool(int(os.environ.get("NPROC", 2))) as pool:
        list(pool.imap_unordered(_safe, names))
