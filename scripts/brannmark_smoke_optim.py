#!/usr/bin/env python3
"""Brannmark_JBC2010 smoke / optimization helpers (DE, GA, CMA-ES, PSO, RS, SA).

**Objective (default):** mean of per-observable mean squared errors (MSE), across
``IR1_P``, ``IRS1_P``, and ``IRS1_P_DosR``. Each MSE is ``mean((y_meas - y_sim)^2)``
over all measurement rows for that observable.

**Noise / scale:** all ``sigma*`` parameters from the PEtab parameters table are **fixed**
at their nominal TSV values and are **not** part of the optimization vector. Only the
remaining ``estimate=1`` parameters (18 kinetic / scaling parameters in this benchmark)
are optimized.

Integrator during search: LSODA (SciPy). LSODA warnings are filtered.
"""

from __future__ import annotations

import sys
import warnings
from dataclasses import dataclass
from pathlib import Path

warnings.filterwarnings("ignore", message="lsoda:")

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
from scipy.optimize import dual_annealing

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import brannmark_nominal_r2 as core

# Full multi-algorithm smoke (slow): set ``SMOKE_ALL_ALGORITHMS = True``.
SMOKE_ALL_ALGORITHMS = False
N_REPS_FULL = 10
N_REPS_DE_SMOKE = 5
FEV = 500

# PEtab noise-parameter IDs (fixed at nominal; excluded from the decision vector).
SIGMA_PARAM_IDS = frozenset(
    {
        "sigmaY1TimR",  # IR1_P
        "sigmaY2Step",  # IRS1_P (two-step experiment)
        "sigmaY2TimR",  # IRS1_P (one-step time course)
        "sigmaYDosR",  # IRS1_P_DosR
    }
)

OBSERVABLES_MSE = ("IR1_P", "IRS1_P", "IRS1_P_DosR")


def benchmark_dir() -> Path:
    base = Path(__file__).resolve().parent.parent / "Benchmark-Models-PEtab" / "Benchmark-Models" / "Brannmark_JBC2010"
    if base.is_dir():
        return base
    return Path("/workspace/Benchmark-Models-PEtab/Benchmark-Models/Brannmark_JBC2010")


def simulate_opt(
    y0: np.ndarray,
    p: dict[str, float],
    ip: core.InsulinParams,
    t_span: tuple[float, float],
    t_eval: np.ndarray | None,
    max_step: float | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    def fun(t, y):
        return core.rhs(t, y, p, ip)

    kwargs: dict = dict(method="LSODA", atol=1e-8, rtol=1e-6)
    if max_step is not None:
        kwargs["max_step"] = max_step
    sol = solve_ivp(fun, t_span, y0, t_eval=t_eval, **kwargs)
    if not sol.success:
        raise RuntimeError(sol.message)
    return sol.t, sol.y


def preequilibrate_opt(
    y0: np.ndarray,
    p: dict[str, float],
    ip: core.InsulinParams,
) -> np.ndarray:
    y = y0.copy()
    for t_end in (2_000.0, 10_000.0, 25_000.0):
        _, y_tr = simulate_opt(y, p, ip, (0.0, t_end), None, max_step=50.0)
        y = y_tr[:, -1]
        rnorm = float(np.linalg.norm(core.rhs(t_end, y, p, ip)))
        if rnorm < 1e-7:
            break
    return y


@dataclass
class ForwardContext:
    y_ic: np.ndarray
    conditions: dict[str, core.InsulinParams]
    df_m: pd.DataFrame
    groups: dict[tuple[str, str], list[float]]
    preeq_id: str
    param_ids: list[str]
    p_template: dict[str, float]
    lb: np.ndarray
    ub: np.ndarray


def build_context() -> ForwardContext:
    base = benchmark_dir()
    df_p = pd.read_csv(base / "parameters_Brannmark_JBC2010.tsv", sep="\t")
    df_c = pd.read_csv(base / "experimentalCondition_Brannmark_JBC2010.tsv", sep="\t")
    df_m = pd.read_csv(base / "measurementData_Brannmark_JBC2010.tsv", sep="\t")

    p_template = {row.parameterId: float(row.nominalValue) for row in df_p.itertuples(index=False)}
    est = df_p[df_p["estimate"].astype(int) == 1]
    est_opt = est[~est["parameterId"].astype(str).isin(SIGMA_PARAM_IDS)]
    param_ids = [str(x) for x in est_opt["parameterId"].tolist()]
    lb = np.array([float(r.lowerBound) for r in est_opt.itertuples(index=False)], dtype=float)
    ub = np.array([float(r.upperBound) for r in est_opt.itertuples(index=False)], dtype=float)

    conditions = {}
    for row in df_c.itertuples(index=False):
        conditions[str(row.conditionId)] = core.InsulinParams(
            float(row.insulin_time_1),
            float(row.insulin_dose_1),
            float(row.insulin_time_2),
            float(row.insulin_dose_2),
        )

    needed = df_m[["preequilibrationConditionId", "simulationConditionId", "time"]].drop_duplicates()
    groups: dict[tuple[str, str], list[float]] = {}
    for row in needed.itertuples(index=False):
        key = (str(row.preequilibrationConditionId), str(row.simulationConditionId))
        groups.setdefault(key, []).append(float(row.time))
    for key in groups:
        groups[key] = sorted(set(groups[key]))

    preeq_ids = df_m["preequilibrationConditionId"].unique()
    if len(preeq_ids) != 1:
        raise NotImplementedError("Expected a single preequilibration condition.")
    preeq_id = str(preeq_ids[0])

    y_ic = core.load_species_ic(base / "model_Brannmark_JBC2010.xml")
    return ForwardContext(y_ic, conditions, df_m, groups, preeq_id, param_ids, p_template, lb, ub)


def vec_to_params(ctx: ForwardContext, x: np.ndarray) -> dict[str, float]:
    x = np.clip(np.asarray(x, dtype=float), ctx.lb, ctx.ub)
    p = dict(ctx.p_template)
    for i, pid in enumerate(ctx.param_ids):
        p[pid] = float(x[i])
    return p


def combined_mean_mse(df_m: pd.DataFrame, preds: np.ndarray) -> float:
    mses: list[float] = []
    for oid in OBSERVABLES_MSE:
        mask = (df_m["observableId"].to_numpy() == oid).astype(bool)
        y_t = df_m.loc[mask, "measurement"].to_numpy(dtype=float)
        y_p = preds[mask]
        mses.append(float(np.mean((y_t - y_p) ** 2)))
    return float(np.mean(mses))


def forward_mse_and_preds(ctx: ForwardContext, x: np.ndarray) -> tuple[float, np.ndarray]:
    p = vec_to_params(ctx, x)
    try:
        y_ss = preequilibrate_opt(ctx.y_ic, p, ctx.conditions[ctx.preeq_id])
        cache: dict[tuple[str, str], tuple[np.ndarray, np.ndarray, dict[float, np.ndarray]]] = {}
        for (preeq_id2, sim_id), times in ctx.groups.items():
            if preeq_id2 != ctx.preeq_id:
                raise NotImplementedError
            ip_sim = ctx.conditions[sim_id]
            t_max = max(times)
            t_eval = np.sort(np.unique(np.concatenate([[0.0], np.array(times, dtype=float)])))
            t_eval = t_eval[t_eval <= t_max + 1e-12]
            t_out, y_traj = simulate_opt(y_ss, p, ip_sim, (0.0, t_max), t_eval)
            state_at_t = {float(tt): y_traj[:, i] for i, tt in enumerate(t_out)}
            cache[(preeq_id2, sim_id)] = (t_out, y_traj, state_at_t)

        preds: list[float] = []
        for row in ctx.df_m.itertuples(index=False):
            key = (str(row.preequilibrationConditionId), str(row.simulationConditionId))
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
            scale = float(p[str(row.observableParameters)])
            yhat = core.predict_observable(str(row.observableId), yq, scale)
            if not np.isfinite(yhat):
                return 1e12, np.full(len(ctx.df_m), np.nan)
            preds.append(yhat)
        pred_arr = np.array(preds, dtype=float)
        return combined_mean_mse(ctx.df_m, pred_arr), pred_arr
    except Exception:
        return 1e12, np.full(len(ctx.df_m), np.nan)


def r2_per_observable(df_m: pd.DataFrame, preds: np.ndarray) -> dict[str, float]:
    out: dict[str, float] = {}
    for oid in sorted(df_m["observableId"].unique()):
        mask = (df_m["observableId"].to_numpy() == oid).astype(bool)
        y_t = df_m.loc[mask, "measurement"].to_numpy(dtype=float)
        y_p = preds[mask]
        out[str(oid)] = core.r2_score(y_t, y_p)
    return out


def r2_mean(r2s: dict[str, float]) -> float:
    vals = [v for v in r2s.values() if np.isfinite(v)]
    return float(np.mean(vals)) if vals else float("nan")


def nominal_decision_vector(ctx: ForwardContext) -> np.ndarray:
    return np.clip(
        np.array([ctx.p_template[pid] for pid in ctx.param_ids], dtype=float),
        ctx.lb,
        ctx.ub,
    )


def run_de(ctx: ForwardContext, seed: int, fev: int | None = None) -> tuple[np.ndarray, int, float]:
    budget = int(fev if fev is not None else FEV)
    rng = np.random.default_rng(seed)
    npop = 15
    d = len(ctx.param_ids)
    lb, ub = ctx.lb, ctx.ub
    pop = rng.uniform(lb, ub, (npop, d))
    pop[0] = nominal_decision_vector(ctx)
    fit = np.array([forward_mse_and_preds(ctx, pop[i])[0] for i in range(npop)])
    n_eval = npop
    f_w, cr = 0.8, 0.9
    while n_eval < budget:
        for i in range(npop):
            if n_eval >= budget:
                break
            choices = [j for j in range(npop) if j != i]
            a, b, c = rng.choice(choices, 3, replace=False)
            mutant = pop[a] + f_w * (pop[b] - pop[c])
            mutant = np.clip(mutant, lb, ub)
            trial = pop[i].copy()
            j_rand = int(rng.integers(0, d))
            for j in range(d):
                if rng.random() < cr or j == j_rand:
                    trial[j] = mutant[j]
            ft = forward_mse_and_preds(ctx, trial)[0]
            n_eval += 1
            if ft <= fit[i]:
                pop[i] = trial
                fit[i] = ft
    bi = int(np.argmin(fit))
    return pop[bi].copy(), n_eval, float(fit[bi])


def _tournament(rng: np.random.Generator, pop: np.ndarray, fit: np.ndarray, k: int) -> int:
    idx = rng.choice(len(fit), size=k, replace=False)
    return int(idx[np.argmin(fit[idx])])


def _sbx(rng: np.random.Generator, p1: np.ndarray, p2: np.ndarray, eta: float) -> np.ndarray:
    u = rng.random(len(p1))
    beta = np.where(u <= 0.5, (2 * u) ** (1 / (eta + 1)), (1 / (2 * (1 - u))) ** (1 / (eta + 1)))
    c = 0.5 * ((1 + beta) * p1 + (1 - beta) * p2)
    return c


def _mutate_polynomial(rng: np.random.Generator, x: np.ndarray, lb: np.ndarray, ub: np.ndarray, eta: float) -> np.ndarray:
    d = len(x)
    y = x.copy()
    for j in range(d):
        if rng.random() > 1.0 / d:
            continue
        u = rng.random()
        delta = (ub[j] - lb[j]) * 0.1
        if u < 0.5:
            dq = (2 * u) ** (1 / (eta + 1)) - 1
        else:
            dq = 1 - (2 * (1 - u)) ** (1 / (eta + 1))
        y[j] = np.clip(y[j] + dq * delta, lb[j], ub[j])
    return y


def run_ga(ctx: ForwardContext, seed: int, fev: int | None = None) -> tuple[np.ndarray, int, float]:
    budget = int(fev if fev is not None else FEV)
    rng = np.random.default_rng(seed)
    npop = 20
    d = len(ctx.param_ids)
    lb, ub = ctx.lb, ctx.ub
    pop = rng.uniform(lb, ub, (npop, d))
    fit = np.array([forward_mse_and_preds(ctx, pop[i])[0] for i in range(npop)])
    n_eval = npop
    while n_eval < budget:
        i1 = _tournament(rng, pop, fit, 3)
        i2 = _tournament(rng, pop, fit, 3)
        if rng.random() < 0.9:
            child = _sbx(rng, pop[i1], pop[i2], 15.0)
        else:
            child = pop[i1].copy() if fit[i1] < fit[i2] else pop[i2].copy()
        child = _mutate_polynomial(rng, child, lb, ub, 20.0)
        child = np.clip(child, lb, ub)
        fc = forward_mse_and_preds(ctx, child)[0]
        n_eval += 1
        worst = int(np.argmax(fit))
        if fc < fit[worst]:
            pop[worst] = child
            fit[worst] = fc
    bi = int(np.argmin(fit))
    return pop[bi].copy(), n_eval, float(fit[bi])


def run_cma(ctx: ForwardContext, seed: int, fev: int | None = None) -> tuple[np.ndarray, int, float]:
    import cma

    budget = int(fev if fev is not None else FEV)
    x0 = (ctx.lb + ctx.ub) / 2.0
    sigma0 = 0.2 * float(np.mean(ctx.ub - ctx.lb))
    opts = {
        "bounds": [ctx.lb.tolist(), ctx.ub.tolist()],
        "seed": int(seed),
        "maxfevals": budget,
        "verbose": -9,
    }
    es = cma.CMAEvolutionStrategy(x0, sigma0, opts)
    while not es.stop():
        xs = es.ask()
        ar = [forward_mse_and_preds(ctx, np.clip(np.asarray(x, dtype=float), ctx.lb, ctx.ub))[0] for x in xs]
        es.tell(xs, ar)
    xb = np.clip(np.asarray(es.result.xfavorite, dtype=float), ctx.lb, ctx.ub)
    ne = int(es.result.evaluations)
    fb = float(es.result.fbest)
    return xb, ne, fb


def run_pso(ctx: ForwardContext, seed: int, fev: int | None = None) -> tuple[np.ndarray, int, float]:
    budget = int(fev if fev is not None else FEV)
    rng = np.random.default_rng(seed)
    s = 20
    d = len(ctx.param_ids)
    lb, ub = ctx.lb, ctx.ub
    x = rng.uniform(lb, ub, (s, d))
    v = rng.uniform(-0.05, 0.05, (s, d)) * (ub - lb)
    pbest = x.copy()
    fit = np.array([forward_mse_and_preds(ctx, x[i])[0] for i in range(s)])
    n_eval = s
    pbest_fit = fit.copy()
    g_idx = int(np.argmin(pbest_fit))
    w, c1, c2 = 0.72, 1.496, 1.496
    while n_eval < budget:
        for i in range(s):
            if n_eval >= budget:
                break
            r1, r2 = rng.random(d), rng.random(d)
            v[i] = w * v[i] + c1 * r1 * (pbest[i] - x[i]) + c2 * r2 * (pbest[g_idx] - x[i])
            vmax = (ub - lb) * 0.5
            v[i] = np.clip(v[i], -vmax, vmax)
            x[i] = np.clip(x[i] + v[i], lb, ub)
            fi = forward_mse_and_preds(ctx, x[i])[0]
            n_eval += 1
            if fi < pbest_fit[i]:
                pbest[i] = x[i].copy()
                pbest_fit[i] = fi
                if fi < pbest_fit[g_idx]:
                    g_idx = i
    return pbest[g_idx].copy(), n_eval, float(pbest_fit[g_idx])


def run_rs(ctx: ForwardContext, seed: int, fev: int | None = None) -> tuple[np.ndarray, int, float]:
    budget = int(fev if fev is not None else FEV)
    rng = np.random.default_rng(seed)
    best_x = None
    best_f = float("inf")
    for _ in range(budget):
        x = rng.uniform(ctx.lb, ctx.ub)
        f, _ = forward_mse_and_preds(ctx, x)
        if f < best_f:
            best_f = f
            best_x = x.copy()
    assert best_x is not None
    return best_x, budget, best_f


def run_sa(ctx: ForwardContext, seed: int, fev: int | None = None) -> tuple[np.ndarray, int, float]:
    budget = int(fev if fev is not None else FEV)
    bounds = [(float(lo), float(hi)) for lo, hi in zip(ctx.lb, ctx.ub, strict=True)]

    def wrapped(z):
        return forward_mse_and_preds(ctx, np.asarray(z, dtype=float))[0]

    ret = dual_annealing(
        wrapped,
        bounds=bounds,
        maxfun=budget,
        seed=seed,
        no_local_search=True,
    )
    x_best = np.clip(np.asarray(ret.x, dtype=float).ravel(), ctx.lb, ctx.ub)
    n_eval = int(getattr(ret, "nfev", budget))
    return x_best, n_eval, float(ret.fun)


def main() -> None:
    ctx = build_context()

    if SMOKE_ALL_ALGORITHMS:
        n_rep = N_REPS_FULL
        algos = [
            ("de", run_de),
            ("ga", run_ga),
            ("cma", run_cma),
            ("pso", run_pso),
            ("rs", run_rs),
            ("sa", run_sa),
        ]
    else:
        n_rep = N_REPS_DE_SMOKE
        algos = [("de", run_de)]

    out_dir = Path(__file__).resolve().parent.parent / "smoke_brannmark_output"
    out_dir.mkdir(parents=True, exist_ok=True)
    params_rows: list[dict] = []
    metrics_rows: list[dict] = []

    run_id = 0
    for algo_name, runner in algos:
        for rep in range(n_rep):
            seed = 10_000 + run_id
            x_best, n_eval, obj_best = runner(ctx, seed)
            _, preds = forward_mse_and_preds(ctx, x_best)
            r2s = r2_per_observable(ctx.df_m, preds)
            rm = r2_mean(r2s)
            print(
                f"[{algo_name.upper()} rep {rep + 1}/{n_rep}] "
                f"fevals={n_eval} mse_objective={obj_best:.6g} "
                f"R2_mean={rm:.6f} "
                + " ".join(f"R2_{k}={v:.6f}" for k, v in sorted(r2s.items())),
                flush=True,
            )

            prow: dict = {
                "run_id": run_id,
                "algorithm": algo_name,
                "replication": rep,
                "fevals": n_eval,
                "mse_objective_mean": obj_best,
            }
            for sid in sorted(SIGMA_PARAM_IDS):
                prow[f"fixed_{sid}"] = float(ctx.p_template[sid])
            for pid, val in zip(ctx.param_ids, x_best, strict=True):
                prow[pid] = val
            params_rows.append(prow)

            mrow = {
                "run_id": run_id,
                "algorithm": algo_name,
                "replication": rep,
                "fevals": n_eval,
                "mse_objective_mean": obj_best,
                "r2_mean": rm,
            }
            mrow.update({f"r2_{k}": v for k, v in sorted(r2s.items())})
            metrics_rows.append(mrow)
            run_id += 1

    df_params = pd.DataFrame(params_rows)
    df_metrics = pd.DataFrame(metrics_rows)
    p_csv = out_dir / "params.csv"
    m_csv = out_dir / "runs_metrics.csv"
    df_params.to_csv(p_csv, index=False)
    df_metrics.to_csv(m_csv, index=False)

    all_pos = True
    for _, row in df_metrics.iterrows():
        for oid in OBSERVABLES_MSE:
            v = float(row[f"r2_{oid}"])
            if not (v > 0.0 and np.isfinite(v)):
                all_pos = False
                break
        if not all_pos:
            break
    r2m = df_metrics["r2_mean"].to_numpy(dtype=float)
    print(
        f"\nAll per-observable R² > 0 in every run: {all_pos} "
        f"(R2_mean min={float(np.nanmin(r2m)):.6f})",
        flush=True,
    )

    print("\n--- params.csv (first 10 rows) ---", flush=True)
    print(df_params.head(10).to_string(), flush=True)
    print("\n--- runs_metrics.csv (first 10 rows) ---", flush=True)
    print(df_metrics.head(10).to_string(), flush=True)
    print(f"\nWrote {p_csv} and {m_csv}", flush=True)


if __name__ == "__main__":
    main()
