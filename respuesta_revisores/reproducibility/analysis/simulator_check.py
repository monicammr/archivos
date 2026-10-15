#!/usr/bin/env python3
"""
Verification of the simulator of the measured outputs (Supplementary Note "Verification of the
simulator", Supplementary Table S9).

At the nominal parameters theta0, the predictions g_i of petab_problem.py are compared with the
reference simulations distributed with the benchmark (simulations.tsv), matching every measurement
by observable, pre-equilibration and simulation condition, time and repetition (not by position).
Relative difference: |y_i - y_ref_i| / max(|y_ref_i|, 1e-6 max|y_ref| + 1e-12).

Usage: python simulator_check.py [Problem ...]   (default: the 34 problems)
Output: results/simulator_check/simulator_check.jsonl (one JSON object per problem).
"""
import json
import sys

import numpy as np
import pandas as pd

import config as CFG
from petab_problem import PetabProblem

OUT = CFG.RESULTS / "simulator_check" / "simulator_check.jsonl"


def check(name):
    folder = CFG.BENCHMARK / name / "v1"
    S = PetabProblem(name)
    y = S._raw(S.theta0)
    f = folder / "simulations.tsv"
    info = {"sistema": name, "p": len(S.names), "p_y": int(S.in_model.sum()),
            "mediciones": S.n_meas, "condiciones": len(S.groups)}
    if y is None:
        info["error"] = "simulación falla"
        return info
    if f.exists():
        ref = pd.read_csv(f, sep="\t", encoding="utf-8-sig")
        if len(ref) == S.n_meas:
            # match by (observable, conditions, time, repetition), not by position
            def key(d):
                d = d.copy()
                c = "preequilibrationConditionId"
                d[c] = d[c].fillna("").astype(str) if c in d.columns else ""
                d["time"] = d["time"].astype(float).round(9)
                k = ["observableId", c, "simulationConditionId", "time"]
                d["_n"] = d.groupby(k).cumcount()
                return d[k + ["_n"]].astype(str).agg("|".join, axis=1)
            ref = ref.rename(columns={"simulationCondition": "simulationConditionId",
                                      "preequilibrationCondition": "preequilibrationConditionId"})
            ref.index = key(ref)
            r = ref["simulation"].astype(float).reindex(key(S.mea)).to_numpy()
            ok = np.isfinite(r)
            if not ok.any():
                info["nota"] = "simulations.tsv no comparable (otros identificadores de condición)"
                return info
            rel = np.abs(y[ok] - r[ok]) / np.maximum(np.abs(r[ok]), 1e-6 * np.max(np.abs(r[ok])) + 1e-12)
            info["err_rel_max_vs_simulations"] = float(np.max(rel))
            info["err_rel_mediana"] = float(np.median(rel))
        else:
            info["nota"] = f"simulations.tsv tiene {len(ref)} filas"
    return info


if __name__ == "__main__":
    names = sys.argv[1:] or CFG.PROBLEMS
    lines = []
    for n in names:
        try:
            r = check(n)
        except Exception as e:
            r = {"sistema": n, "error": repr(e)}
        print(json.dumps(r), flush=True)
        lines.append(json.dumps(r))
    if not sys.argv[1:]:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text("\n".join(lines) + "\n")
