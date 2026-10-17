#!/usr/bin/env python3
"""
Computing time of the test of k_min = 2 (scripts/prueba_kmin.sh), written to
results/kmin_times.json for the Supplementary Note on computing time.

Most programs record the time of every task (field "segundos"): robustness of each problem,
admissibility and synthetic tasks of criteria_tests.py, and profile points. The exception is the
robustness of Smith and Schwen, which was moved during the run to one process per perturbation
size (ROBUST_LEVEL); those processes do not record their time, which is therefore taken from the
modification times of their checkpoint files (partial/<problem>__L<size>.json) minus the launch
time, plus the time the serial runs had spent on these two problems before they were stopped.
Run: 07:25:44 to 07:53:08 UTC on 17 October 2026 on an 88-core server (log in
results/logs_kmin_resumen/prueba_kmin.log).
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

import config as CFG

R = CFG.RESULTS
START = datetime(2026, 10, 17, 7, 25, 44, tzinfo=timezone.utc).timestamp()
RELAUNCH = datetime(2026, 10, 17, 7, 33, 30, tzinfo=timezone.utc).timestamp()   # per-size processes
END = datetime(2026, 10, 17, 7, 53, 8, tzinfo=timezone.utc).timestamp()
SLOW = ["Smith_BMCSystBiol2013", "Schwen_PONE2014"]

out = {"elapsed_s": END - START, "per_problem_s": {}, "method": __doc__.strip()}
probs = sorted(f.stem for f in (R / "subsets_single").glob("*.json"))
for p in probs:
    t = 0.0
    for d in ("robustness_subsets_single", "robustness_independent_subsets_single"):
        if p in SLOW:
            t += RELAUNCH - START                                  # serial run before it was stopped
            for f in (R / d / "partial").glob(f"{p}__L*.json"):
                t += f.stat().st_mtime - RELAUNCH
        else:
            r = json.loads((R / d / f"{p}.json").read_text())
            t += r.get("segundos", 0.0)
    for folder in ("criteria_tests_fixedscen", "criteria_tests_20pc_fixedscen"):
        for f in (R / folder).glob(f"{p}__single__*.json"):
            t += json.loads(f.read_text()).get("segundos", 0.0)
    pd = R / "identifiability" / "profiles_subsets_single" / p
    if pd.exists():
        t += sum(json.loads(f.read_text()).get("segundos", 0.0) for f in pd.glob("p_*.json"))
        if (pd / "minimo.npz").exists():
            m = np.load(pd / "minimo.npz")
            t += float(m["segundos"]) if "segundos" in m.files else 0.0
    out["per_problem_s"][p] = round(t, 1)
out["total_cpu_h"] = round(sum(out["per_problem_s"].values()) / 3600, 2)
(R / "kmin_times.json").write_text(json.dumps(out, indent=1))
print(f"elapsed {out['elapsed_s'] / 60:.0f} min; processor time {out['total_cpu_h']} h")
for p, t in sorted(out["per_problem_s"].items(), key=lambda x: -x[1])[:5]:
    print(f"  {p}: {t / 3600:.2f} h")
