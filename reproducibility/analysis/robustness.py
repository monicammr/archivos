#!/usr/bin/env python3
"""
Robustness of the selected subsets to the size of the parameter changes (Fig. 4, Supplementary
Note "Robustness to the size of parameter changes").

For every admissible problem of results/selection/, with its subset S FIXED (plus its calibration
parameters, which are always re-estimated), the fitting error is evaluated at perturbation sizes
epsilon = 1, 5, 10, 20, 30, 40, 50 %, with 15 scenarios per size,
theta^(k)(epsilon) = theta0 * (1 + epsilon u^(k)), u^(k) ~ U(-1, 1)^p. The fifteen directions u^(k)
are drawn once (seed 42) and reused at every size (paired design), so that +-5 % reproduces the
scenarios of the selection; they are stored in the output ("u").

Per scenario: cos(Delta), e_rel (S set to the scenario values, no re-estimation) and e_fit
(nonlinear re-estimation of S and the calibration parameters, least squares in log|theta|, bounds
[|theta0|/10, 10|theta0|], started from the scenario values and from theta0; first order for the
problems in config.FIRST_ORDER, as in the selection).

Patterns (median e_fit per size, threshold tau_e = 0.436):
  A  admissible at all sizes (robust up to +-50 %);
  B  admissible up to a size >= +-20 %, then not admissible and does not recover;
  C  irregular: stops being admissible and becomes admissible again at a larger size;
  D  not admissible already at +-10 % or less.

Usage: python robustness.py [Problem ...]   (default: all admissible problems not yet done)
Output: results/robustness/<problem>.json (per size: median, quartiles, and the values of every
valid scenario). Partial results are saved per size in results/robustness/partial/ to resume.
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

SEL = CFG.SELECTION
OUT = CFG.ROBUSTNESS
LEVELS = CFG.LEVELS
N_SCEN, SEED = CFG.N_SCENARIOS, CFG.SEED
TAU_E = CFG.TAU_E


def evaluate(name):
    t0 = time.time()
    info = json.loads((SEL / f"{name}.json").read_text())
    Sy = PP.PetabProblem(name)
    th0 = Sy.theta0
    p = len(th0)
    idx = [Sy.names.index(q) for q in info["S"] + info.get("calibracion", []) if q in Sy.names]
    y0 = Sy.sim(th0).ravel()
    floor = max(1e-10 * np.linalg.norm(y0), 1e-6)
    sgn = np.where(th0[idx] < 0, -1.0, 1.0)
    mag0 = np.maximum(np.abs(th0[idx]), 1e-12)
    lo, hi = np.log(mag0 / 10), np.log(mag0 * 10)
    first_order = name in CFG.FIRST_ORDER
    if first_order:   # columns of J (relative, central differences, delta = 0.01) for S and C only
        Js = np.zeros((y0.size, len(idx)))
        for c, j in enumerate(idx):
            tp, tm = th0.copy(), th0.copy()
            tp[j] *= 1.01; tm[j] *= 0.99
            yp, ym = Sy.sim(tp), Sy.sim(tm)
            if yp is not None and ym is not None:
                Js[:, c] = (yp - ym).ravel() / 0.02
    res = {"sistema": name, "S": info["S"], "n_calibracion": len(info.get("calibracion", [])),
           "niveles": {}}
    U = np.random.default_rng(SEED).uniform(-1, 1, size=(N_SCEN, p))   # the 15 directions u(k)
    res["semilla"] = SEED
    res["u"] = U.tolist()
    ckf = OUT / "partial" / f"{name}.json"          # checkpoint per size (resume)
    done = json.loads(ckf.read_text()) if ckf.exists() else {}
    for level in LEVELS:
        key = f"{int(round(100 * level))}"
        if key in done:
            res["niveles"][key] = done[key]
            continue
        cs, es, fs, ks = [], [], [], []
        rng = np.random.default_rng(SEED)   # same seed at every size: +-5 % = selection scenarios
        for k in range(N_SCEN):
            u_k = rng.uniform(-1, 1, size=p)
            assert np.array_equal(u_k, U[k])   # same directions at every size (paired design)
            th = np.maximum(th0 * (1 + level * u_k), 1e-12)
            yf = Sy.sim(th)
            if yf is None:
                continue
            d = yf.ravel() - y0
            nf = np.linalg.norm(d)
            if nf < floor:
                continue
            ts = th0.copy(); ts[idx] = th[idx]
            ys = Sy.sim(ts)
            if ys is None:
                continue
            ds = ys.ravel() - y0
            ns = np.linalg.norm(ds)
            cs.append(float(d @ ds / (nf * ns)) if ns > 0 else 0.0)
            er = float(np.linalg.norm(d - ds) / nf)
            es.append(er)

            ks.append(k)
            if first_order:
                c_, *_ = np.linalg.lstsq(Js, d, rcond=None)
                fs.append(min(er, float(np.linalg.norm(d - Js @ c_) / nf)))
                continue

            def resid(u):
                t = th0.copy(); t[idx] = sgn * np.exp(u)
                y = Sy.sim(t)
                return np.full(d.size, 10.0) if y is None else (y.ravel() - yf.ravel()) / nf
            best = er
            for x0 in (np.clip(np.log(np.maximum(np.abs(th[idx]), 1e-12)), lo, hi), np.log(mag0)):
                try:
                    r = least_squares(resid, x0, bounds=(lo, hi), method="trf",
                                      max_nfev=100 * (len(idx) + 1), diff_step=1e-3)
                    best = min(best, float(np.linalg.norm(r.fun)))
                except Exception:
                    pass
            fs.append(best)
        q = lambda v, k: float(np.percentile(v, k)) if v else float("nan")  # noqa: E731
        res["niveles"][f"{int(round(100 * level))}"] = {
            "n": len(fs), "cos_med": q(cs, 50), "erel_med": q(es, 50),
            "eaj_med": q(fs, 50), "eaj_q25": q(fs, 25), "eaj_q75": q(fs, 75),
            "escenarios": ks, "eaj": fs, "erel": es, "cos": cs}
        ckf.parent.mkdir(parents=True, exist_ok=True)
        done[key] = res["niveles"][key]
        ckf.write_text(json.dumps(done))
    ok = [res["niveles"][k]["eaj_med"] <= TAU_E for k in res["niveles"]
          if np.isfinite(res["niveles"][k]["eaj_med"])]
    lev = [LEVELS[i] for i in range(len(ok))]
    if all(ok):
        pat = "A"
    else:
        f = ok.index(False)
        recovers = any(ok[f:])
        if recovers:
            pat = "C"
        elif lev[f] >= 0.20:
            pat = "B"
        else:
            pat = "D"
    res["patron"] = pat
    res["eajuste_metodo"] = "linealizado" if first_order else "no lineal"
    res["segundos"] = round(time.time() - t0, 1)
    return res


def _safe(name):
    try:
        r = evaluate(name)
    except Exception as e:
        r = {"sistema": name, "error": repr(e)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps(r, indent=1))
    print(json.dumps({k: r.get(k) for k in ("sistema", "patron", "error", "segundos")}),
          flush=True)


if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not names:
        for f in sorted(SEL.glob("*.json")):
            d = json.loads(f.read_text())
            if d.get("admisible") and not (OUT / f"{f.stem}.json").exists():
                names.append(f.stem)
    with Pool(int(os.environ.get("NPROC", 3))) as pool:
        list(pool.imap_unordered(_safe, names))
