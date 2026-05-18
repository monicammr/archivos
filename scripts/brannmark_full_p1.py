#!/usr/bin/env python3
"""Brannmark_JBC2010 full benchmark: 100 runs × 6 algorithms, FEV=2000, mean-MSE objective.

Decision-vector box: for each optimized parameter, lower = nominal/100, upper = nominal×100
(PEtab nominals); sigma* noise parameters stay fixed at nominal.

Each successful run is appended to ``*_partial_runs.csv`` and every 50 runs to
``checkpoint_every50_ckNNN_full.csv`` with **all 18 kinetic parameters** (not metrics-only).

Resume: only from a complete ``*_partial_runs.csv``. Use ``--fresh`` to delete prior campaign
outputs and start again from run 1/600.
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

# After each successful run: full snapshot (18 kinetic + fixed σ + R² + MSE) in this file — required for resume.
PARTIAL_SUFFIX = "_partial_runs.csv"


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Brannmark_JBC2010: 6 optimizers × 100 runs, tight bounds, mean-MSE objective."
    )
    p.add_argument(
        "--fresh",
        action="store_true",
        help=(
            "Remove prior campaign files for this PREFIX (partial_runs, checkpoints, progress). "
            "Does not remove master_run.log (delete/truncate that file yourself before launch if you want a clean log)."
        ),
    )
    return p.parse_args(argv)


def _fresh_cleanup(out_dir: Path, prefix: str) -> list[str]:
    removed: list[str] = []
    for path in sorted(out_dir.glob(f"{prefix}*")):
        if path.is_file():
            path.unlink()
            removed.append(path.name)
    for path in sorted(out_dir.glob("checkpoint_every50_*.csv")):
        if path.is_file():
            path.unlink()
            removed.append(path.name)
    # Do not delete master_run.log here: if the user starts with `>> master_run.log`, the shell may
    # open the file before Python runs --fresh; deleting the path breaks the redirect. Truncate or
    # remove the log manually when you want a clean file.
    for name in ("progress_every10.txt",):
        p = out_dir / name
        if p.is_file():
            p.unlink()
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

R2_METRIC_KEYS = ("r2_mean", "r2_IR1_P", "r2_IRS1_P", "r2_IRS1_P_DosR")


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


def _rows_from_partial_csv(path: Path, ctx: bm.ForwardContext) -> tuple[list[dict], list[dict], dict[str, dict]] | None:
    if not path.is_file():
        return None
    df = pd.read_csv(path)
    if df.empty:
        return None
    for pid in ctx.param_ids:
        if pid not in df.columns:
            print(
                f"Resume rejected: {path.name} has no column {pid!r} (need all 18 kinetic parameters). "
                "Use --fresh for a clean run.",
                flush=True,
            )
            return None
    for _, row in df.iterrows():
        for pid in ctx.param_ids:
            if not np.isfinite(float(row[pid])):
                print(
                    f"Resume rejected: {path.name} has missing/invalid kinetic values. Use --fresh for a clean run.",
                    flush=True,
                )
                return None
    metrics_rows: list[dict] = []
    params_rows: list[dict] = []
    best: dict[str, dict] = {
        key: {"mse": float("inf"), "x": None, "preds": None} for _, key, _ in ALGO_SPECS
    }
    for _, row in df.iterrows():
        mrow = {
            "global_run_index": int(row["global_run_index"]),
            "algorithm": str(row["algorithm"]),
            "run_within_algo": int(row["run_within_algo"]),
            "seed": int(row["seed"]),
            "fevals": int(row["fevals"]),
            "wall_seconds": float(row["wall_seconds"]),
            "mse_objective_mean": float(row["mse_objective_mean"]),
            "r2_mean": float(row["r2_mean"]),
            "r2_IR1_P": float(row["r2_IR1_P"]),
            "r2_IRS1_P": float(row["r2_IRS1_P"]),
            "r2_IRS1_P_DosR": float(row["r2_IRS1_P_DosR"]),
        }
        metrics_rows.append(mrow)
        prow = {c: row[c] for c in df.columns if c not in R2_METRIC_KEYS}
        params_rows.append(prow)
        key = str(row["algorithm"])
        xv = np.array([float(row[pid]) for pid in ctx.param_ids], dtype=float)
        if np.all(np.isfinite(xv)) and float(row["mse_objective_mean"]) < best[key]["mse"]:
            best[key]["mse"] = float(row["mse_objective_mean"])
            best[key]["x"] = xv.copy()
            best[key]["preds"] = None
    for key in best:
        if best[key]["x"] is not None:
            _, pr = bm.forward_mse_and_preds(ctx, best[key]["x"])
            best[key]["preds"] = pr.copy()
    metrics_rows, params_rows = _sort_resume_rows(metrics_rows, params_rows)
    for i, (mr, pr) in enumerate(zip(metrics_rows, params_rows, strict=True)):
        mr["global_run_index"] = i
        pr["global_run_index"] = i
    return metrics_rows, params_rows, best


def _sort_resume_rows(
    metrics_rows: list[dict], params_rows: list[dict]
) -> tuple[list[dict], list[dict]]:
    order = []
    for i, mr in enumerate(metrics_rows):
        key = str(mr["algorithm"])
        ai = _algo_index(key)
        order.append((ai, int(mr["run_within_algo"]), i))
    perm = [i for _, _, i in sorted(order)]
    return [metrics_rows[i] for i in perm], [params_rows[i] for i in perm]


def _completed_pairs(metrics_rows: list[dict]) -> set[tuple[str, int]]:
    return {(str(r["algorithm"]), int(r["run_within_algo"])) for r in metrics_rows}


def _dataframe_full_runs(params_rows: list[dict], metrics_rows: list[dict]) -> pd.DataFrame:
    """One row per successful run: metadata, fixed σ, 18 kinetic parameters, R², MSE."""
    if not params_rows:
        return pd.DataFrame()
    keys = list(params_rows[0].keys()) + list(R2_METRIC_KEYS)
    rows: list[dict] = []
    for pr, mr in zip(params_rows, metrics_rows, strict=True):
        row = dict(pr)
        row.update({k: mr[k] for k in R2_METRIC_KEYS})
        rows.append(row)
    return pd.DataFrame(rows, columns=keys)


def _save_partial_runs(path: Path, params_rows: list[dict], metrics_rows: list[dict]) -> None:
    df = _dataframe_full_runs(params_rows, metrics_rows)
    if not df.empty:
        df.to_csv(path, index=False)


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


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    t0_all = time.perf_counter()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    progress_path = OUT_DIR / "progress_every10.txt"

    if args.fresh:
        removed = _fresh_cleanup(OUT_DIR, PREFIX)
        print(f"--fresh: removed {len(removed)} file(s) from campaign output directory.", flush=True)

    ctx0 = bm.build_context()
    nom = np.array([float(ctx0.p_template[pid]) for pid in ctx0.param_ids], dtype=float)
    lb_t = nom / 100.0
    ub_t = nom * 100.0
    ctx = replace(ctx0, lb=lb_t, ub=ub_t)
    base = benchmark_dir()
    df_c = pd.read_csv(base / "experimentalCondition_Brannmark_JBC2010.tsv", sep="\t")
    plot_x_arr = merge_plot_x(ctx.df_m, df_c).to_numpy(dtype=float)

    partial_path = OUT_DIR / f"{PREFIX}{PARTIAL_SUFFIX}"
    meta_path = OUT_DIR / f"{PREFIX}_metadata.json"

    params_rows: list[dict] = []
    metrics_rows: list[dict] = []
    best: dict[str, dict] = {
        key: {"mse": float("inf"), "x": None, "preds": None} for _, key, _ in ALGO_SPECS
    }

    loaded = _rows_from_partial_csv(partial_path, ctx)
    if loaded is not None:
        metrics_rows, params_rows, best = loaded
        print(
            f"Resume from {partial_path.name}: {len(metrics_rows)} completed runs (kinetic parameters OK).",
            flush=True,
        )

    completed = _completed_pairs(metrics_rows)

    seeds = [SEED0 + k for k in range(N_RUNS)]
    if seeds[-1] != 2125:
        raise ValueError(f"Expected last seed 2125, got {seeds[-1]}")

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
        "decision_bounds": "per-parameter [nominal/100, nominal*100] from PEtab nominalValue",
        "sigma_fixed": sorted(bm.SIGMA_PARAM_IDS),
        "fev_per_run": FEV,
        "n_runs_per_algorithm": N_RUNS,
        "algorithms": [a for a, _, _ in ALGO_SPECS],
        "seeds": {"first": SEED0, "last": seeds[-1], "count": N_RUNS},
        "started_unix": started,
        "resume_completed_pairs_at_start": len(completed),
    }
    if completed:
        meta["resumed_unix"] = time.time()
    (OUT_DIR / f"{PREFIX}_metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    for label, key, runner in ALGO_SPECS:
        for rep in range(N_RUNS):
            if (key, rep) in completed:
                continue
            seed = seeds[rep]
            t0 = time.perf_counter()
            try:
                x_best, n_eval, obj = runner(ctx, seed, FEV)
                _, preds = bm.forward_mse_and_preds(ctx, x_best)
            except Exception as exc:
                elapsed = time.perf_counter() - t0
                line = (
                    f"[{label} | run {rep + 1}/{N_RUNS} | seed={seed}] FAILED after {elapsed:.1f}s: {exc!r}"
                )
                print(line, flush=True)
                with open(progress_path, "a", encoding="utf-8") as fp:
                    fp.write(line + "\n")
                continue

            elapsed = time.perf_counter() - t0
            r2s = bm.r2_per_observable(ctx.df_m, preds)
            rm = bm.r2_mean(r2s)
            a = float(r2s["IR1_P"])
            b = float(r2s["IRS1_P"])
            c = float(r2s["IRS1_P_DosR"])
            line = (
                f"[{label} | run {rep + 1}/{N_RUNS} | seed={seed}] "
                f"R2_mean={rm:.6f}  IR1_P={a:.6f}  IRS1_P={b:.6f}  IRS1_P_DosR={c:.6f}  "
                f"mse_mean={obj:.6g}  FEV={n_eval}  t={elapsed:.1f}s"
            )
            print(line, flush=True)

            if obj < best[key]["mse"]:
                best[key]["mse"] = float(obj)
                best[key]["x"] = x_best.copy()
                best[key]["preds"] = preds.copy()

            row_id = len(metrics_rows)

            prow = {
                "global_run_index": row_id,
                "algorithm": key,
                "algorithm_label": label,
                "run_within_algo": rep,
                "seed": seed,
                "fevals": n_eval,
                "wall_seconds": elapsed,
                "mse_objective_mean": obj,
            }
            for sid in sorted(bm.SIGMA_PARAM_IDS):
                prow[f"fixed_{sid}"] = float(ctx.p_template[sid])
            for pid, val in zip(ctx.param_ids, x_best, strict=True):
                prow[pid] = float(val)
            params_rows.append(prow)

            mrow = {
                "global_run_index": row_id,
                "algorithm": key,
                "run_within_algo": rep,
                "seed": seed,
                "fevals": n_eval,
                "wall_seconds": elapsed,
                "mse_objective_mean": obj,
                "r2_mean": rm,
                "r2_IR1_P": a,
                "r2_IRS1_P": b,
                "r2_IRS1_P_DosR": c,
            }
            metrics_rows.append(mrow)

            _save_partial_runs(partial_path, params_rows, metrics_rows)

            n_ok = len(metrics_rows)
            if n_ok % 10 == 0:
                tail = f"progress: {n_ok} successful runs completed (checkpoint every 50)\n"
                with open(progress_path, "a", encoding="utf-8") as fp:
                    fp.write(tail)

            if n_ok > 0 and n_ok % 50 == 0:
                ck = OUT_DIR / f"checkpoint_every50_ck{n_ok:03d}_full.csv"
                _dataframe_full_runs(params_rows, metrics_rows).to_csv(ck, index=False)

    df_p = pd.DataFrame(params_rows)
    df_m = pd.DataFrame(metrics_rows)
    df_p.to_csv(OUT_DIR / f"{PREFIX}_params.csv", index=False)
    df_m.to_csv(OUT_DIR / f"{PREFIX}_runs_metrics.csv", index=False)

    w = ctx.df_m.copy().reset_index(drop=True)
    w["plot_x"] = plot_x_arr
    for _, key, _ in ALGO_SPECS:
        pr = best[key]["preds"]
        if pr is not None:
            w[f"sim_best_{key}"] = pr
        else:
            w[f"sim_best_{key}"] = np.nan
    w.to_csv(OUT_DIR / f"{PREFIX}_preds_wide.csv", index=False)

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
