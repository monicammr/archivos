#!/usr/bin/env python3
"""
Computational cost (Supplementary Note "Computational cost", Supplementary Table S15).

The dominant cost of the method is the computation of J (2p simulations) and of the stage-2
ordering (p simulations); the selection, the condition-number tests, backward elimination and the
first-order e_fit only use linear algebra on J. This script measures the time of one simulation of
the measured outputs at theta0 (after loading the model); the cost table multiplies it by 3p.

Froehlich (4,231 parameters, 1,228 species, 9,169 experimental conditions) is timed on its state
trajectories (one simulation of the model, 60 time points in [1e-6, 50]), because on its measured
outputs each evaluation requires about 9,000 simulations.

Times depend on the machine. The stored values (results/cost/simulation_times.json) were measured
on a four-core server; Smith was measured on a second machine and scaled by 1.55, the mean ratio of
the times of Boehm and Weber between both machines (field "nota").

Usage: python timing.py Problem [Problem ...]   -> prints {"p", "t_sim", "modo"} per problem
       python timing.py --write Problem ...      -> also updates results/cost/simulation_times.json
"""
import json
import sys
import time
import warnings

import pandas as pd

warnings.filterwarnings("ignore")
import roadrunner as rr  # noqa: E402

import config as CFG  # noqa: E402
from petab_problem import PetabProblem  # noqa: E402

OUT = CFG.RESULTS / "cost" / "simulation_times.json"
STATES = {"Froehlich_CellSystems2018"}


def time_states(name, t_end=50.0, n_points=60):
    """One simulation of the state trajectories (as in the first version of the analysis)."""
    folder = CFG.BENCHMARK / name / "v1"
    df = pd.read_csv(folder / "parameters.tsv", sep="\t")
    df = df[df["estimate"] == 1] if "estimate" in df.columns else df
    m = rr.RoadRunner(str(folder / "model.xml"))
    ig = m.getIntegrator()
    for k, v in [("relative_tolerance", 1e-7), ("absolute_tolerance", 1e-10),
                 ("maximum_num_steps", 200000), ("stiff", True)]:
        try:
            ig.setValue(k, v)
        except Exception:
            pass
    gp = set(m.model.getGlobalParameterIds())
    theta = {n: float(v) for n, v in zip(df["parameterId"], df["nominalValue"]) if n in gp}
    m.resetAll()
    for n, v in theta.items():
        m[n] = v
    t = time.time()
    m.simulate(1e-6, t_end, n_points)
    return {"p": int(len(df)), "t_sim": time.time() - t, "modo": "estados"}


def time_outputs(name):
    S = PetabProblem(name)
    t = time.time()
    y = S.sim(S.theta0)
    dt = time.time() - t
    if y is None:
        raise RuntimeError("the nominal simulation fails")
    return {"p": len(S.names), "t_sim": dt, "modo": "salidas"}


if __name__ == "__main__":
    write = "--write" in sys.argv
    names = [a for a in sys.argv[1:] if not a.startswith("--")]
    stored = json.loads(OUT.read_text()) if OUT.exists() else {}
    for n in names:
        r = time_states(n) if n in STATES else time_outputs(n)
        print(json.dumps({n: r}), flush=True)
        stored[n] = r
    if write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(stored, indent=1))
