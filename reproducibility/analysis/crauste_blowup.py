#!/usr/bin/env python3
"""
Why no local reduction is possible for Crauste_CellSystems2017 (Results, "the two non-admissible
problems"; Supplementary Note "System-by-system summary").

The model of the CD8 T-cell response has quadratic proliferation and pathogen-growth terms. This
script
  1. simulates the states at theta0 and with each of the 24 one-at-a-time changes of +-1 % of the
     12 estimated parameters, and records whether the solution exists on the measured horizon
     (28 days) and, if not, when the integration breaks down;
  2. counts the failures of the 15 admissibility scenarios at +-5 % (seed 42);
  3. repeats both counts for relative tolerances from 1e-10 to 1e-5 (absolute tolerance = 1e-3 x
     relative), to show that the failures do not depend on the integrator settings.

Usage: python crauste_blowup.py   -> results/crauste_blowup.json
"""
import json
import warnings

import numpy as np

warnings.filterwarnings("ignore")
import config as CFG  # noqa: E402
from petab_problem import PetabProblem  # noqa: E402

NAME = "Crauste_CellSystems2017"
OUT = CFG.RESULTS / "crauste_blowup.json"
T_END, STEP = 28.0, 0.05


def trajectory(P, theta):
    """States on [0, 28] every 0.05 days; stops at the first interval that cannot be integrated."""
    m = P.m
    m.resetAll()
    for k, v in P._pval(theta).items():
        if k in P.gparams:
            m[k] = float(v)
    m.reset()
    m.timeCourseSelections = ["time"] + ["[" + s + "]" for s in P.species]
    rows, t = [np.asarray(m.simulate(0, 1e-9, 2))[0]], 0.0
    for b in np.arange(STEP, T_END + 1e-9, STEP):
        try:
            r = np.asarray(m.simulate(t, b, 2))
        except Exception:
            return np.array(rows), False
        rows.append(r[-1]); t = b
        if not np.all(np.isfinite(r[-1])):
            return np.array(rows), False
    return np.array(rows), True


def summary(P, X, ok):
    eff = X[:, 1 + P.species.index("EarlyEffector")] + X[:, 1 + P.species.index("LateEffector")]
    k = int(np.argmax(eff))
    return {"existe_en_[0,28]": bool(ok), "t_final": float(X[-1, 0]),
            "efectores_max": float(eff[k]), "t_max": float(X[k, 0]),
            "efectores_t_final": float(eff[-1])}


def main():
    P = PetabProblem(NAME)
    th0, p = P.theta0, len(P.theta0)
    res = {"sistema": NAME, "nominal": summary(P, *trajectory(P, th0)), "un_parametro_1%": [],
           "tolerancias": []}
    for j, n in enumerate(P.names):
        for f in (1.01, 0.99):
            th = th0.copy(); th[j] *= f
            s = summary(P, *trajectory(P, th))
            res["un_parametro_1%"].append(dict(parametro=n, factor=f, **s))
    ig = P.m.getIntegrator()
    for rtol in (1e-10, 1e-8, 1e-7, 1e-6, 1e-5):
        ig.setValue("relative_tolerance", rtol); ig.setValue("absolute_tolerance", rtol * 1e-3)
        f1 = 0
        for j in range(p):
            for f in (1.01, 0.99):
                th = th0.copy(); th[j] *= f
                f1 += P.sim(th) is None
        rng = np.random.default_rng(CFG.SEED); f5 = 0
        for _ in range(CFG.N_SCENARIOS):
            th = th0 * (1 + 0.05 * rng.uniform(-1, 1, size=p))
            f5 += P.sim(th) is None
        res["tolerancias"].append({"rtol": rtol, "atol": rtol * 1e-3,
                                   "fallos_un_parametro_1%": f"{f1}/{2 * p}",
                                   "fallos_escenarios_5%": f"{f5}/{CFG.N_SCENARIOS}"})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
