#!/usr/bin/env python3
"""Brannmark_JBC2010: ODE from SBML structure, nominal parameters from PEtab TSV, R² per observable.

Trajectories match `simulatedData_Brannmark_JBC2010.tsv` from the upstream benchmark (numerical integration).
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

SPECIES_IDS = ("IR", "IRins", "IRp", "IRiP", "IRi", "IRS", "IRSiP", "X", "Xp")


@dataclass
class InsulinParams:
    insulin_time_1: float
    insulin_dose_1: float
    insulin_time_2: float
    insulin_dose_2: float


def load_species_ic(sbml_path: Path) -> np.ndarray:
    tree = ET.parse(sbml_path)
    root = tree.getroot()
    ns = {"sbml": "http://www.sbml.org/sbml/level2/version4"}
    ic = {}
    for sp in root.findall(".//sbml:listOfSpecies/sbml:species", ns):
        sid = sp.get("id")
        ic0 = float(sp.get("initialConcentration", "0"))
        ic[sid] = ic0
    missing = [s for s in SPECIES_IDS if s not in ic]
    if missing:
        raise ValueError(
            f"SBML model {sbml_path} is missing initial concentrations for "
            f"species {missing}; found {sorted(ic)}."
        )
    return np.array([ic[s] for s in SPECIES_IDS], dtype=float)


def insulin_at_time(t: float, ip: InsulinParams) -> float:
    d1 = ip.insulin_dose_1 * (1.0 if t >= ip.insulin_time_1 else 0.0)
    d2 = ip.insulin_dose_2 * (1.0 if t >= ip.insulin_time_2 else 0.0)
    return d1 + d2


def rhs(t: float, y: np.ndarray, p: dict[str, float], ip: InsulinParams) -> np.ndarray:
    IR, IRins, IRp, IRiP, IRi, IRS, IRSiP, X, Xp = y
    ins = insulin_at_time(t, ip)

    k1a, k1aBasic, k1b, k1c = p["k1a"], p["k1aBasic"], p["k1b"], p["k1c"]
    k1d, k1e, k1f, k1g, k1r = p["k1d"], p["k1e"], p["k1f"], p["k1g"], p["k1r"]
    k21, k22, k3, km2, km3 = p["k21"], p["k22"], p["k3"], p["km2"], p["km3"]

    v0 = IR * (k1aBasic + ins * k1a)
    v1 = IRins * k1b
    v2 = IRins * k1c
    v3 = IRp * k1d
    v4 = IRiP * (k1e + (Xp * k1f) / (Xp + 1.0))
    v5 = IRp * k1g
    v6 = IRi * k1r
    v7 = IRS * k21 * (IRp + k22 * IRiP)
    v8 = IRSiP * km2
    v9 = X * IRSiP * k3
    v10 = Xp * km3

    dIR = -v0 + v1 + v5 + v6
    dIRins = v0 - v1 - v2
    dIRp = v2 - v3 - v5
    dIRiP = v3 - v4
    dIRi = v4 - v6
    dIRS = -v7 + v8
    dIRSiP = v7 - v8
    dX = -v9 + v10
    dXp = v9 - v10
    return np.array([dIR, dIRins, dIRp, dIRiP, dIRi, dIRS, dIRSiP, dX, dXp], dtype=float)


def simulate(
    y0: np.ndarray,
    p: dict[str, float],
    ip: InsulinParams,
    t_span: tuple[float, float],
    t_eval: np.ndarray | None,
    max_step: float | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    def fun(t, y):
        return rhs(t, y, p, ip)

    kwargs: dict = dict(
        method="BDF",
        atol=1e-10,
        rtol=1e-8,
    )
    if max_step is not None:
        kwargs["max_step"] = max_step

    sol = solve_ivp(fun, t_span, y0, t_eval=t_eval, **kwargs)
    if not sol.success:
        raise RuntimeError(sol.message)
    return sol.t, sol.y


def preequilibrate(
    y0: np.ndarray,
    p: dict[str, float],
    ip: InsulinParams,
) -> np.ndarray:
    """Reach steady state under zero-insulin (or fixed preequil) protocol."""
    y = y0.copy()
    for t_end in (2_000.0, 10_000.0, 50_000.0):
        _, y_tr = simulate(y, p, ip, (0.0, t_end), None, max_step=50.0)
        y = y_tr[:, -1]
        rnorm = float(np.linalg.norm(rhs(t_end, y, p, ip)))
        if rnorm < 1e-7:
            break
    return y


def predict_observable(
    obs_id: str,
    y: np.ndarray,
    scale: float,
) -> float:
    IR, IRins, IRp, IRiP, IRi, IRS, IRSiP, X, Xp = y
    if obs_id == "IR1_P":
        return scale * (IRp + IRiP)
    if obs_id in ("IRS1_P", "IRS1_P_DosR"):
        return scale * IRSiP
    raise ValueError(obs_id)


def r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    ss_res = np.sum((y_true - y_pred) ** 2)
    y_mean = np.mean(y_true)
    ss_tot = np.sum((y_true - y_mean) ** 2)
    if ss_tot <= 0:
        return float("nan")
    return float(1.0 - ss_res / ss_tot)


def main() -> None:
    base = Path(__file__).resolve().parent.parent / "Benchmark-Models-PEtab" / "Benchmark-Models" / "Brannmark_JBC2010"
    if not base.is_dir():
        base = Path("/workspace/Benchmark-Models-PEtab/Benchmark-Models/Brannmark_JBC2010")

    sbml = base / "model_Brannmark_JBC2010.xml"
    df_p = pd.read_csv(base / "parameters_Brannmark_JBC2010.tsv", sep="\t")
    df_c = pd.read_csv(base / "experimentalCondition_Brannmark_JBC2010.tsv", sep="\t")
    df_m = pd.read_csv(base / "measurementData_Brannmark_JBC2010.tsv", sep="\t")

    p = {row.parameterId: float(row.nominalValue) for row in df_p.itertuples(index=False)}
    y_ic = load_species_ic(sbml)

    conditions: dict[str, InsulinParams] = {}
    for row in df_c.itertuples(index=False):
        cid = row.conditionId
        conditions[cid] = InsulinParams(
            float(row.insulin_time_1),
            float(row.insulin_dose_1),
            float(row.insulin_time_2),
            float(row.insulin_dose_2),
        )

    needed = df_m[
        ["preequilibrationConditionId", "simulationConditionId", "time"]
    ].drop_duplicates()
    groups: dict[tuple[str, str], list[float]] = {}
    for row in needed.itertuples(index=False):
        key = (row.preequilibrationConditionId, row.simulationConditionId)
        groups.setdefault(key, []).append(float(row.time))
    for key in groups:
        groups[key] = sorted(set(groups[key]))

    cache: dict[tuple[str, str], tuple[np.ndarray, np.ndarray, dict[float, np.ndarray]]] = {}

    preeq_ids = df_m["preequilibrationConditionId"].unique()
    if len(preeq_ids) != 1:
        raise NotImplementedError("Multiple preequilibration conditions require separate steady states.")
    preeq_id = str(preeq_ids[0])
    y_ss = preequilibrate(y_ic, p, conditions[preeq_id])

    for (preeq_id2, sim_id), times in groups.items():
        if preeq_id2 != preeq_id:
            raise NotImplementedError("Mismatched preequilibration in cache key.")
        ip_sim = conditions[sim_id]
        t_max = max(times)
        t_eval = np.sort(np.unique(np.concatenate([[0.0], np.array(times, dtype=float)])))
        t_eval = t_eval[t_eval <= t_max + 1e-12]
        t_out, y_traj = simulate(y_ss, p, ip_sim, (0.0, t_max), t_eval)
        state_at_t = {float(tt): y_traj[:, i] for i, tt in enumerate(t_out)}
        cache[(preeq_id2, sim_id)] = (t_out, y_traj, state_at_t)

    preds: dict[str, list[float]] = {oid: [] for oid in df_m["observableId"].unique()}
    trues: dict[str, list[float]] = {oid: [] for oid in df_m["observableId"].unique()}

    for row in df_m.itertuples(index=False):
        key = (row.preequilibrationConditionId, row.simulationConditionId)
        t_out, y_traj, state_at_t = cache[key]
        tt = float(row.time)
        yq = state_at_t.get(tt)
        if yq is None:
            for tkey, vec in state_at_t.items():
                if abs(tkey - tt) < 1e-9:
                    yq = vec
                    break
        if yq is None:
            yq = np.array([np.interp(tt, t_out, y_traj[i, :]) for i in range(y_traj.shape[0])])
        scale = float(p[row.observableParameters])
        yhat = predict_observable(row.observableId, yq, scale)
        oid = row.observableId
        preds[oid].append(yhat)
        trues[oid].append(float(row.measurement))

    print("Nominal R² by observable (PEtab nominalValue, full ODE + preequilibration):")
    green = True
    for oid in sorted(preds.keys()):
        r2 = r2_score(np.array(trues[oid]), np.array(preds[oid]))
        ok = "OK" if r2 > 0.85 else "LOW"
        if r2 <= 0.85:
            green = False
        print(f"  {oid}: R² = {r2:.6f}  ({ok}, n={len(trues[oid])})")
    print("all_above_0.85:", green)


if __name__ == "__main__":
    main()
