#!/usr/bin/env python3
"""
Two baselines for the external validation (Results, "Comparison with existing selection criteria";
Supplementary Note "Comparison on real data"):

* random subsets: k = |S| biological parameters drawn at random (20 draws, seeds 0-19), re-estimated
  with the calibration parameters on the training data from theta0; the median test chi2/n over the
  draws is reported;
* calibration only (k = 0): only the calibration parameters are re-estimated (theta0 itself if the
  problem has none).

Same split, fit and test metric as external_validation.py (experiment A).

Usage:  python baselines.py [Problem ...]          (default: admissible problems except Chen, Lang)
Output: results/random_subsets/<problem>.json, results/calibration_only/<problem>.json
"""
import json
import os
import sys
import time
import warnings
from multiprocessing import Pool

import numpy as np

warnings.filterwarnings("ignore")
import config as CFG  # noqa: E402
import external_validation as EV  # noqa: E402
import petab_problem as PP  # noqa: E402

N_SEEDS = int(os.environ.get("N_SEEDS", 20))
SKIP = {"Chen_MSB2009", "Lang_PLOSComputBiol2024"}
EV.CKDIR["dir"] = None


def ours_chi2(name):
    f = CFG.NESTED / f"{name}.json"
    return json.loads(f.read_text()).get("chi2_test_red_original") if f.exists() else None


def run(name):
    t0 = time.time()
    info = json.loads((CFG.SELECTION / f"{name}.json").read_text())
    S = PP.PetabProblem(name)
    th0 = S.theta0.copy()
    cal = info.get("calibracion", [])
    k = len(info["S"])
    bio = [j for j in np.nonzero(S.in_model)[0] if S.names[j] not in set(cal)]
    cal_idx = [S.names.index(q) for q in cal if q in S.names]
    train, test, ftest, kind = EV.split(S)
    zd = S.zdata()
    ftr = ~ftest & np.isfinite(zd)
    fte = ftest & np.isfinite(zd)
    if not ftr.any() or not fte.any():
        out = {"sistema": name, "no_evaluable": "single condition/time"}
        return out, out
    loc = EV.test_only_parameters(S, train, test)
    chi2_ours = ours_chi2(name)

    # random subsets
    per_seed = []
    for seed in range(N_SEEDS):
        rng = np.random.default_rng(seed)
        sel = list(rng.choice(bio, size=k, replace=False))
        free = [j for j in sel + cal_idx if j not in loc]
        if not free:
            per_seed.append(float("nan")); continue
        th, _ = EV.fit(S, free, th0, train, zd, ftr, 30 * (len(free) + 1))
        per_seed.append(EV.chi2(S.z(th), zd, fte))
    v = [x for x in per_seed if np.isfinite(x)]
    med = float(np.median(v)) if v else float("nan")
    rnd = {"sistema": name, "k": k, "n_seeds": N_SEEDS, "n_validas": len(v), "chi2_ours": chi2_ours,
           "chi2_rand_median": med,
           "chi2_rand_q1": float(np.percentile(v, 25)) if v else float("nan"),
           "chi2_rand_q3": float(np.percentile(v, 75)) if v else float("nan"),
           "ratio_rand_vs_ours": med / chi2_ours if chi2_ours else None,
           "chi2_por_semilla": per_seed, "segundos": round(time.time() - t0, 1)}

    # calibration only
    t1 = time.time()
    free_cal = [j for j in cal_idx if j not in loc]
    if free_cal:
        th, _ = EV.fit(S, free_cal, th0, train, zd, ftr, 30 * (len(free_cal) + 1))
        c = EV.chi2(S.z(th), zd, fte)
        vac = {"sistema": name, "k": k, "n_cal": len(free_cal)}
    else:
        c = EV.chi2(S.z(th0), zd, fte)
        vac = {"sistema": name, "k": k, "nota": "sin calibracion, th0 directo"}
    vac.update(chi2_ours=chi2_ours, chi2_vacio=c, ratio_vacio_vs_ours=c / chi2_ours if chi2_ours else None,
               segundos=round(time.time() - t1, 1))
    return rnd, vac


def _safe(name):
    try:
        rnd, vac = run(name)
    except Exception as e:
        rnd = vac = {"sistema": name, "error": repr(e)}
    for folder, r in ((CFG.RANDOM_SUBSETS, rnd), (CFG.CALIBRATION_ONLY, vac)):
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f"{name}.json").write_text(json.dumps(r, indent=1, default=str), encoding="utf-8")
    print(json.dumps({"sistema": name, "rand": rnd.get("chi2_rand_median"), "vac": vac.get("chi2_vacio")},
                     default=str), flush=True)


if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if not a.startswith("--")] or sorted(
        f.stem for f in CFG.SELECTION.glob("*.json")
        if json.loads(f.read_text()).get("admisible") and f.stem not in SKIP)
    with Pool(int(os.environ.get("NPROC", 4))) as pool:
        list(pool.imap_unordered(_safe, names))
