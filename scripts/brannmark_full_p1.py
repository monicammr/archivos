#!/usr/bin/env python3
"""Brannmark_JBC2010 full benchmark: 100 runs × 6 algorithms, FEV=2000, mean-MSE objective.

Decision-vector box: for each optimized parameter, lower = nominal/100, upper = nominal×100
(PEtab nominals); sigma* noise parameters stay fixed at nominal.

Outputs use a **canonical column layout** for downstream analysis (params, runs_metrics, preds_wide).
See ``CANONICAL_PARAMS_COLS``, ``CANONICAL_RUNS_METRICS_COLS``.

Checkpoints every **5** successful global runs:
``checkpoint_every5_ckNNN_params.csv`` and ``checkpoint_every5_ckNNN_runs_metrics.csv``.

With ``--fresh``, runs a **preflight** of 6 jobs (one per algorithm, TrueSeed=2026) before the
main loop; ``(method, rep=0)`` is marked done so those rows are not duplicated.

Resume: ``{PREFIX}_partial_params.csv`` with Metodo, Seed, TrueSeed + 18 kinetics + fixed σ.
Use ``--fresh`` to delete prior campaign files.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import warnings
from dataclasses import replace
from pathlib import Path

warnings.filterwarnings("ignore", message="lsoda:")
warnings.filterwarnings("ignore", category=RuntimeWarning, module="brannmark_nominal_r2")

import numpy as np
import pandas as pd

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import brannmark_smoke_optim as bm

OUT_DIR = Path(__file__).resolve().parent.parent / "BRANNMARK_P1"
PREFIX = "brannmark_TIGHT_nom100_R100_B2000"
N_RUNS = 100
FEV = 2000
SEED0 = 2026
# Successful-run checkpoint interval (also used in progress log + metadata).
CHECKPOINT_EVERY_N = 5

OBS_ORDER = list(bm.OBSERVABLES_MSE)  # IR1_P, IRS1_P, IRS1_P_DosR

METHOD_DISPLAY: dict[str, str] = {
    "de": "DE",
    "ga": "GA",
    "cma": "CMA-ES",
    "pso": "PSO",
    "sa": "SA",
    "rs": "RS",
}

METHOD_KEY: dict[str, str] = {v: k for k, v in METHOD_DISPLAY.items()}

FIXED_SIGMA_NAMES = tuple(f"fixed_{s}" for s in sorted(bm.SIGMA_PARAM_IDS))

CANONICAL_PARAMS_COLS = (
    "Metodo",
    "Seed",
    "TrueSeed",
    "k1a",
    "k1aBasic",
    "k1b",
    "k1c",
    "k1d",
    "k1e",
    "k1f",
    "k1g",
    "k1r",
    "k21",
    "k22",
    "k3",
    "k_IRP_1Step",
    "k_IRSiP_1Step",
    "k_IRSiP_2Step",
    "k_IRSiP_DosR",
    "km2",
    "km3",
    "fixed_sigmaY1TimR",
    "fixed_sigmaY2Step",
    "fixed_sigmaY2TimR",
    "fixed_sigmaYDosR",
)

CANONICAL_RUNS_METRICS_COLS = (
    "Metodo",
    "Seed",
    "TrueSeed",
    "R2",
    "RMSE",
    "MAE",
    "MSE",
    "sMAPE",
    "Tiempo_s",
    "FEV",
    "R2_IR1_P",
    "R2_IRS1_P",
    "R2_IRS1_P_DosR",
    "RMSE_IR1_P",
    "RMSE_IRS1_P",
    "RMSE_IRS1_P_DosR",
)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Brannmark_JBC2010: 6 optimizers × 100 runs, tight bounds, mean-MSE objective."
    )
    p.add_argument(
        "--fresh",
        action="store_true",
        help=(
            "Remove prior campaign files for this PREFIX (partial, checkpoints, progress). "
            "Does not remove master_run.log (truncate manually if needed)."
        ),
    )
    p.add_argument(
        "--test-de",
        type=int,
        metavar="N",
        default=0,
        help="Smoke test: run only DE for N repetitions then write outputs and exit.",
    )
    p.add_argument(
        "--fev",
        type=int,
        default=None,
        help="Override function-evaluation budget per run (default: 2000).",
    )
    p.add_argument(
        "--no-preflight",
        action="store_true",
        help="With --fresh, skip the 6-method TrueSeed=2026 preflight (not recommended).",
    )
    return p.parse_args(argv)


def _fresh_cleanup(out_dir: Path, prefix: str) -> list[str]:
    removed: list[str] = []
    for path in sorted(out_dir.glob(f"{prefix}*")):
        if path.is_file():
            path.unlink()
            removed.append(path.name)
    for path in sorted(out_dir.glob(f"checkpoint_every{CHECKPOINT_EVERY_N}_*.csv")):
        if path.is_file():
            path.unlink()
            removed.append(path.name)
    for path in sorted(out_dir.glob("checkpoint_every10_*.csv")):
        if path.is_file():
            path.unlink()
            removed.append(path.name)
    for path in sorted(out_dir.glob("checkpoint_every50_*.csv")):
        if path.is_file():
            path.unlink()
            removed.append(path.name)
    for name in (
        "progress_every5.txt",
        "progress_every10.txt",
        "params.csv",
        "runs_metrics.csv",
        "preds_wide.csv",
    ):
        pth = out_dir / name
        if pth.is_file():
            pth.unlink()
            removed.append(name)
    return removed


ALGO_SPECS: list[tuple[str, str, object]] = [
    ("DE", "de", bm.run_de),
    ("GA", "ga", bm.run_ga),
    ("CMA", "cma", bm.run_cma),
    ("PSO", "pso", bm.run_pso),
    ("SA", "sa", bm.run_sa),
    ("RS", "rs", bm.run_rs),
]


def benchmark_dir() -> Path:
    return bm.benchmark_dir()


def merge_plot_x(df_m: pd.DataFrame, df_c: pd.DataFrame) -> pd.Series:
    m = df_m.merge(
        df_c,
        left_on="simulationConditionId",
        right_on="conditionId",
        how="left",
        suffixes=("", "_cond"),
    )
    xs: list[float] = []
    for row in m.itertuples(index=False):
        iv = str(row.independentVariableId)
        if iv == "time":
            xs.append(float(row.time))
        elif iv == "insulin_dose_1":
            xs.append(float(row.insulin_dose_1))
        else:
            xs.append(float(row.time))
    return pd.Series(xs, index=df_m.index, dtype=float)


def _algo_index(key: str) -> int:
    keys = [spec[1] for spec in ALGO_SPECS]
    return keys.index(key)


def per_observable_fit_metrics(df_m: pd.DataFrame, preds: np.ndarray) -> dict[str, dict[str, float]]:
    r2s = bm.r2_per_observable(df_m, preds)
    out: dict[str, dict[str, float]] = {}
    for oid in OBS_ORDER:
        mask = (df_m["observableId"].to_numpy() == oid).astype(bool)
        y_t = df_m.loc[mask, "measurement"].to_numpy(dtype=float)
        y_p = preds[mask]
        err = y_t - y_p
        mse_o = float(np.mean(err**2))
        denom = np.abs(y_t) + np.abs(y_p) + 1e-12
        smape_o = float(200.0 * np.mean(np.abs(err) / denom))
        out[oid] = {
            "R2": float(r2s[oid]),
            "MSE": mse_o,
            "RMSE": float(np.sqrt(mse_o)),
            "MAE": float(np.mean(np.abs(err))),
            "sMAPE": smape_o,
        }
    return out


def aggregate_three_obs(per: dict[str, dict[str, float]]) -> dict[str, float]:
    """Mean of R2, RMSE, MAE, MSE, sMAPE across the 3 observables."""
    r2 = float(np.mean([per[o]["R2"] for o in OBS_ORDER]))
    rmse = float(np.mean([per[o]["RMSE"] for o in OBS_ORDER]))
    mae = float(np.mean([per[o]["MAE"] for o in OBS_ORDER]))
    mse = float(np.mean([per[o]["MSE"] for o in OBS_ORDER]))
    smape = float(np.mean([per[o]["sMAPE"] for o in OBS_ORDER]))
    return {"R2": r2, "RMSE": rmse, "MAE": mae, "MSE": mse, "sMAPE": smape}


def build_canonical_runs_metrics_row(
    key: str,
    rep: int,
    seed: int,
    fevals: int,
    wall_seconds: float,
    per: dict[str, dict[str, float]],
    agg: dict[str, float],
) -> dict:
    mname = METHOD_DISPLAY[key]
    row = {
        "Metodo": mname,
        "Seed": rep + 1,
        "TrueSeed": seed,
        "R2": agg["R2"],
        "RMSE": agg["RMSE"],
        "MAE": agg["MAE"],
        "MSE": agg["MSE"],
        "sMAPE": agg["sMAPE"],
        "Tiempo_s": wall_seconds,
        "FEV": fevals,
        "R2_IR1_P": per["IR1_P"]["R2"],
        "R2_IRS1_P": per["IRS1_P"]["R2"],
        "R2_IRS1_P_DosR": per["IRS1_P_DosR"]["R2"],
        "RMSE_IR1_P": per["IR1_P"]["RMSE"],
        "RMSE_IRS1_P": per["IRS1_P"]["RMSE"],
        "RMSE_IRS1_P_DosR": per["IRS1_P_DosR"]["RMSE"],
    }
    return row


def build_canonical_params_row(
    ctx: bm.ForwardContext,
    key: str,
    rep: int,
    seed: int,
    x_best: np.ndarray,
) -> dict:
    row: dict = {
        "Metodo": METHOD_DISPLAY[key],
        "Seed": rep + 1,
        "TrueSeed": seed,
    }
    for pid, val in zip(ctx.param_ids, x_best, strict=True):
        row[pid] = float(val)
    for sid in sorted(bm.SIGMA_PARAM_IDS):
        row[f"fixed_{sid}"] = float(ctx.p_template[sid])
    return row


def _rows_from_partial_params(path: Path, ctx: bm.ForwardContext) -> tuple[dict[tuple[str, int], np.ndarray], dict[str, dict], int] | None:
    """Load canonical partial_params.csv; return preds_by_run reconstruction, best dict, count."""
    if not path.is_file():
        return None
    df = pd.read_csv(path)
    if df.empty:
        return None
    expected = list(CANONICAL_PARAMS_COLS)
    for c in expected:
        if c not in df.columns:
            print(f"Resume rejected: {path.name} missing column {c!r}. Use --fresh.", flush=True)
            return None
    preds_by_run: dict[tuple[str, int], np.ndarray] = {}
    best: dict[str, dict] = {
        k: {"mse": float("inf"), "x": None, "preds": None} for _, k, _ in ALGO_SPECS
    }
    for _, row in df.iterrows():
        mlabel = str(row["Metodo"]).strip()
        key = METHOD_KEY.get(mlabel)
        if key is None:
            print(f"Resume rejected: unknown Metodo {mlabel!r}", flush=True)
            return None
        rep = int(row["Seed"]) - 1
        xv = np.array([float(row[pid]) for pid in ctx.param_ids], dtype=float)
        if not np.all(np.isfinite(xv)):
            print("Resume rejected: non-finite kinetic parameters.", flush=True)
            return None
        obj, preds = bm.forward_mse_and_preds(ctx, xv)
        preds_by_run[(key, rep)] = preds.copy()
        if obj < best[key]["mse"]:
            best[key]["mse"] = float(obj)
            best[key]["x"] = xv.copy()
            best[key]["preds"] = preds.copy()
    return preds_by_run, best, len(df)


def _completed_pairs_from_partial(df: pd.DataFrame) -> set[tuple[str, int]]:
    out: set[tuple[str, int]] = set()
    for _, row in df.iterrows():
        key = METHOD_KEY[str(row["Metodo"]).strip()]
        rep = int(row["Seed"]) - 1
        out.add((key, rep))
    return out


def _recompute_runs_metrics_from_params(
    ctx: bm.ForwardContext, params_rows: list[dict], fev_default: int
) -> list[dict]:
    """Rebuild canonical runs_metrics rows from saved parameter vectors (e.g. missing metrics file)."""
    out: list[dict] = []
    for row in params_rows:
        key = METHOD_KEY[str(row["Metodo"]).strip()]
        rep = int(row["Seed"]) - 1
        seed = int(row["TrueSeed"])
        xv = np.array([float(row[pid]) for pid in ctx.param_ids], dtype=float)
        _obj, preds = bm.forward_mse_and_preds(ctx, xv)
        per = per_observable_fit_metrics(ctx.df_m, preds)
        agg = aggregate_three_obs(per)
        out.append(
            build_canonical_runs_metrics_row(key, rep, seed, fev_default, float("nan"), per, agg)
        )
    return out


def plot_best_fits(
    df_m: pd.DataFrame,
    plot_x: np.ndarray,
    best_preds: dict[str, np.ndarray | None],
    algo_keys: list[str],
    out_png: Path,
) -> None:
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    obs_order = list(bm.OBSERVABLES_MSE)
    fig, axes = plt.subplots(
        len(obs_order),
        len(algo_keys),
        figsize=(4 * len(algo_keys), 3.2 * len(obs_order)),
        squeeze=False,
    )
    for i, oid in enumerate(obs_order):
        mask = df_m["observableId"].to_numpy() == oid
        x = plot_x[mask]
        y_meas = df_m.loc[mask, "measurement"].to_numpy(dtype=float)
        order = np.argsort(x)
        xo, yo = x[order], y_meas[order]
        for j, ak in enumerate(algo_keys):
            ax = axes[i][j]
            pr = best_preds.get(ak)
            if pr is None:
                ax.set_visible(False)
                continue
            y_sim = pr[mask][order]
            ax.scatter(xo, yo, s=18, alpha=0.75, label="data", color="0.25")
            ax.plot(xo, y_sim, "-", lw=1.8, label="sim", color="C0")
            if i == 0:
                ax.set_title(ak.upper(), fontsize=10)
            if j == 0:
                ax.set_ylabel(f"{oid}\nvalue", fontsize=9)
            ax.grid(True, alpha=0.3)
            if i == len(obs_order) - 1:
                ax.set_xlabel("time or dose (see PEtab)", fontsize=8)
    leg = [
        Line2D([0], [0], linestyle="None", marker="o", color="0.25", markersize=5, label="data"),
        Line2D([0], [0], color="C0", lw=2, label="sim"),
    ]
    fig.legend(handles=leg, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.02))
    fig.suptitle("Brannmark_JBC2010 — best fit per method (mean-MSE objective)", fontsize=12, y=1.06)
    fig.tight_layout()
    fig.savefig(out_png, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _write_preds_wide(
    out_path: Path,
    df_m: pd.DataFrame,
    plot_x: np.ndarray,
    preds_by_run: dict[tuple[str, int], np.ndarray],
    n_run_cap: int,
) -> None:
    n = len(df_m)
    y_ir1 = np.full(n, np.nan)
    y_irs = np.full(n, np.nan)
    y_dos = np.full(n, np.nan)
    oid_np = df_m["observableId"].to_numpy()
    meas = df_m["measurement"].to_numpy(dtype=float)
    for i in range(n):
        o = str(oid_np[i])
        if o == "IR1_P":
            y_ir1[i] = meas[i]
        elif o == "IRS1_P":
            y_irs[i] = meas[i]
        elif o == "IRS1_P_DosR":
            y_dos[i] = meas[i]
    cols: dict[str, np.ndarray] = {
        "t": plot_x.astype(float),
        "y_IR1_P": y_ir1,
        "y_IRS1_P": y_irs,
        "y_IRS1_P_DosR": y_dos,
    }
    for label, key, _ in ALGO_SPECS:
        m = METHOD_DISPLAY[key]
        for rep in range(n_run_cap):
            k2 = (key, rep)
            name = f"{m}_s{rep + 1}"
            if k2 in preds_by_run:
                cols[name] = preds_by_run[k2].astype(float)
            else:
                cols[name] = np.full(n, np.nan)
    # column order: t, y_*, then methods in ALGO_SPECS order, each s1..sN
    order_cols = ["t", "y_IR1_P", "y_IRS1_P", "y_IRS1_P_DosR"]
    for _, key, _ in ALGO_SPECS:
        m = METHOD_DISPLAY[key]
        for rep in range(n_run_cap):
            order_cols.append(f"{m}_s{rep + 1}")
    pd.DataFrame({c: cols[c] for c in order_cols}).to_csv(out_path, index=False)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    t0_all = time.perf_counter()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    progress_path = OUT_DIR / "progress_every5.txt"
    fev_budget = int(args.fev) if args.fev is not None else FEV

    if args.fresh:
        removed = _fresh_cleanup(OUT_DIR, PREFIX)
        print(f"--fresh: removed {len(removed)} file(s).", flush=True)

    ctx0 = bm.build_context()
    nom = np.array([float(ctx0.p_template[pid]) for pid in ctx0.param_ids], dtype=float)
    lb_t = nom / 100.0
    ub_t = nom * 100.0
    ctx = replace(ctx0, lb=lb_t, ub=ub_t)
    base = benchmark_dir()
    df_c = pd.read_csv(base / "experimentalCondition_Brannmark_JBC2010.tsv", sep="\t")
    plot_x_arr = merge_plot_x(ctx.df_m, df_c).to_numpy(dtype=float)

    partial_params_path = OUT_DIR / f"{PREFIX}_partial_params.csv"
    meta_path = OUT_DIR / f"{PREFIX}_metadata.json"

    partial_rm_path = OUT_DIR / f"{PREFIX}_partial_runs_metrics.csv"

    params_canonical: list[dict] = []
    runs_metrics_canonical: list[dict] = []
    preds_by_run: dict[tuple[str, int], np.ndarray] = {}
    best: dict[str, dict] = {
        key: {"mse": float("inf"), "x": None, "preds": None} for _, key, _ in ALGO_SPECS
    }

    loaded = _rows_from_partial_params(partial_params_path, ctx)
    completed: set[tuple[str, int]] = set()
    if loaded is not None:
        preds_resume, best, _n = loaded
        preds_by_run.update(preds_resume)
        params_canonical = pd.read_csv(partial_params_path).to_dict("records")
        if partial_rm_path.is_file():
            runs_metrics_canonical = pd.read_csv(partial_rm_path).to_dict("records")
        else:
            runs_metrics_canonical = _recompute_runs_metrics_from_params(ctx, params_canonical, fev_budget)
            pd.DataFrame(runs_metrics_canonical, columns=list(CANONICAL_RUNS_METRICS_COLS)).to_csv(
                partial_rm_path, index=False
            )
        completed = _completed_pairs_from_partial(pd.read_csv(partial_params_path))
        print(f"Resume from {partial_params_path.name}: {len(completed)} runs restored.", flush=True)

    seeds = [SEED0 + k for k in range(N_RUNS)]
    if seeds[-1] != 2125:
        raise ValueError(f"Expected last seed 2125, got {seeds[-1]}")

    if args.test_de and args.test_de > 0:
        algo_loop = [ALGO_SPECS[0]]
        n_reps = min(int(args.test_de), N_RUNS)
        n_run_cap = N_RUNS
    else:
        algo_loop = ALGO_SPECS
        n_reps = N_RUNS
        n_run_cap = N_RUNS

    started = time.time()
    if meta_path.is_file() and not args.fresh:
        try:
            old_meta = json.loads(meta_path.read_text(encoding="utf-8"))
            started = float(old_meta.get("started_unix", started))
        except (json.JSONDecodeError, OSError):
            pass

    meta: dict = {
        "benchmark": "Brannmark_JBC2010",
        "objective": "mean(MSE_IR1_P, MSE_IRS1_P, MSE_IRS1_P_DosR)",
        "n_params_optimized": len(ctx.param_ids),
        "canonical_params_columns": list(CANONICAL_PARAMS_COLS),
        "canonical_runs_metrics_columns": list(CANONICAL_RUNS_METRICS_COLS),
        "decision_bounds": "per-parameter [nominal/100, nominal*100] from PEtab nominalValue",
        "sigma_fixed": sorted(bm.SIGMA_PARAM_IDS),
        "fev_per_run": fev_budget,
        "n_runs_per_algorithm": N_RUNS,
        "algorithms": [a for a, _, _ in ALGO_SPECS],
        "seeds": {"first": SEED0, "last": seeds[-1], "count": N_RUNS},
        "started_unix": started,
        "resume_completed_pairs_at_start": len(completed),
    }
    if args.test_de:
        meta["smoke_test_de_runs"] = n_reps
    if completed:
        meta["resumed_unix"] = time.time()
    meta["checkpoint_every_n_successful_runs"] = CHECKPOINT_EVERY_N
    (OUT_DIR / f"{PREFIX}_metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    def flush_partials_and_checkpoint() -> int:
        """Write partial CSVs; return current successful run count."""
        df_p = pd.DataFrame(params_canonical, columns=list(CANONICAL_PARAMS_COLS))
        df_p.to_csv(partial_params_path, index=False)
        df_m_c = pd.DataFrame(runs_metrics_canonical, columns=list(CANONICAL_RUNS_METRICS_COLS))
        df_m_c.to_csv(partial_rm_path, index=False)
        n_ok = len(runs_metrics_canonical)
        if n_ok % CHECKPOINT_EVERY_N == 0:
            tail = f"progress: {n_ok} successful runs (checkpoint every {CHECKPOINT_EVERY_N})\n"
            with open(progress_path, "a", encoding="utf-8") as fp:
                fp.write(tail)
        if n_ok > 0 and n_ok % CHECKPOINT_EVERY_N == 0:
            ck = f"checkpoint_every{CHECKPOINT_EVERY_N}_ck{n_ok:03d}"
            df_p.to_csv(OUT_DIR / f"{ck}_params.csv", index=False)
            df_m_c.to_csv(OUT_DIR / f"{ck}_runs_metrics.csv", index=False)
        return n_ok

    # --- Preflight: one completed run per algorithm, TrueSeed = SEED0 (2026), Seed = 1 ---
    if (
        args.fresh
        and not args.test_de
        and not args.no_preflight
        and len(completed) == 0
    ):
        print(
            "=== PREFLIGHT: 6 methods × TrueSeed=2026 (Seed=1) before full campaign ===",
            flush=True,
        )
        pf_seed = seeds[0]
        preflight_r2: list[float] = []
        for label, key, runner in ALGO_SPECS:
            rep = 0
            t0 = time.perf_counter()
            try:
                x_best, n_eval, obj = runner(ctx, pf_seed, fev_budget)
                _, preds = bm.forward_mse_and_preds(ctx, x_best)
            except Exception as exc:
                elapsed = time.perf_counter() - t0
                print(f"[PREFLIGHT | {label} | FAILED] {exc!r}", flush=True)
                continue
            elapsed = time.perf_counter() - t0
            per = per_observable_fit_metrics(ctx.df_m, preds)
            agg = aggregate_three_obs(per)
            prow_c = build_canonical_params_row(ctx, key, rep, pf_seed, x_best)
            mrow_c = build_canonical_runs_metrics_row(
                key, rep, pf_seed, n_eval, elapsed, per, agg
            )
            params_canonical.append(prow_c)
            runs_metrics_canonical.append(mrow_c)
            preds_by_run[(key, rep)] = preds.copy()
            preflight_r2.append(float(agg["R2"]))
            line = (
                f"[PREFLIGHT | {label} | run {rep + 1}/{N_RUNS} | seed={pf_seed}] "
                f"R2_mean={agg['R2']:.6f}  IR1_P={per['IR1_P']['R2']:.6f}  "
                f"IRS1_P={per['IRS1_P']['R2']:.6f}  IRS1_P_DosR={per['IRS1_P_DosR']['R2']:.6f}  "
                f"mse_mean={obj:.6g}  FEV={n_eval}  t={elapsed:.1f}s"
            )
            print(line, flush=True)
            if obj < best[key]["mse"]:
                best[key]["mse"] = float(obj)
                best[key]["x"] = x_best.copy()
                best[key]["preds"] = preds.copy()
            completed.add((key, 0))
            flush_partials_and_checkpoint()
        u = len({round(x, 6) for x in preflight_r2})
        if len(preflight_r2) == 6 and u == 6:
            print(
                "PREFLIGHT OK: R2 (mean over observables) differs across all 6 methods.",
                flush=True,
            )
        elif len(preflight_r2) == 6:
            print(
                f"WARNING: only {u} distinct R2 values in preflight (rounded to 6 decimals).",
                flush=True,
            )
        print("=== Full campaign (remaining runs) ===", flush=True)

    for label, key, runner in algo_loop:
        for rep in range(n_reps):
            if (key, rep) in completed:
                continue
            seed = seeds[rep]
            t0 = time.perf_counter()
            try:
                x_best, n_eval, obj = runner(ctx, seed, fev_budget)
                _, preds = bm.forward_mse_and_preds(ctx, x_best)
            except Exception as exc:
                elapsed = time.perf_counter() - t0
                line = (
                    f"[{label} | run {rep + 1}/{n_reps} | seed={seed}] FAILED after {elapsed:.1f}s: {exc!r}"
                )
                print(line, flush=True)
                with open(progress_path, "a", encoding="utf-8") as fp:
                    fp.write(line + "\n")
                continue

            elapsed = time.perf_counter() - t0
            per = per_observable_fit_metrics(ctx.df_m, preds)
            agg = aggregate_three_obs(per)
            prow_c = build_canonical_params_row(ctx, key, rep, seed, x_best)
            mrow_c = build_canonical_runs_metrics_row(
                key, rep, seed, n_eval, elapsed, per, agg
            )
            params_canonical.append(prow_c)
            runs_metrics_canonical.append(mrow_c)
            preds_by_run[(key, rep)] = preds.copy()

            line = (
                f"[{label} | run {rep + 1}/{n_reps} | seed={seed}] "
                f"R2_mean={agg['R2']:.6f}  IR1_P={per['IR1_P']['R2']:.6f}  "
                f"IRS1_P={per['IRS1_P']['R2']:.6f}  IRS1_P_DosR={per['IRS1_P_DosR']['R2']:.6f}  "
                f"mse_mean={obj:.6g}  FEV={n_eval}  t={elapsed:.1f}s"
            )
            print(line, flush=True)

            if obj < best[key]["mse"]:
                best[key]["mse"] = float(obj)
                best[key]["x"] = x_best.copy()
                best[key]["preds"] = preds.copy()

            flush_partials_and_checkpoint()

    # If resume: merge saved partial with newly built lists — reload from disk for simplicity
    if partial_params_path.is_file():
        params_canonical = pd.read_csv(partial_params_path).to_dict("records")
        runs_metrics_canonical = pd.read_csv(OUT_DIR / f"{PREFIX}_partial_runs_metrics.csv").to_dict(
            "records"
        )

    df_p_final = pd.DataFrame(params_canonical, columns=list(CANONICAL_PARAMS_COLS))
    df_m_final = pd.DataFrame(runs_metrics_canonical, columns=list(CANONICAL_RUNS_METRICS_COLS))
    df_p_final.to_csv(OUT_DIR / f"{PREFIX}_params.csv", index=False)
    df_m_final.to_csv(OUT_DIR / f"{PREFIX}_runs_metrics.csv", index=False)
    # Pipeline-friendly aliases
    df_p_final.to_csv(OUT_DIR / "params.csv", index=False)
    df_m_final.to_csv(OUT_DIR / "runs_metrics.csv", index=False)

    _write_preds_wide(OUT_DIR / f"{PREFIX}_preds_wide.csv", ctx.df_m, plot_x_arr, preds_by_run, n_run_cap)
    _write_preds_wide(OUT_DIR / "preds_wide.csv", ctx.df_m, plot_x_arr, preds_by_run, n_run_cap)

    meta["finished_unix"] = time.time()
    meta["wall_seconds_total"] = time.perf_counter() - t0_all
    meta["best_mse_per_algorithm"] = {k: best[k]["mse"] for k in best}
    (OUT_DIR / f"{PREFIX}_metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    algo_keys = [spec[1] for spec in ALGO_SPECS]
    plot_best_fits(
        ctx.df_m,
        plot_x_arr,
        {k: best[k]["preds"] for k in best},
        algo_keys,
        OUT_DIR / "best_fits_all_methods.png",
    )
    print(f"Done. Outputs under {OUT_DIR}", flush=True)


if __name__ == "__main__":
    main()
