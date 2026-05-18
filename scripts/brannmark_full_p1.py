#!/usr/bin/env python3
"""Brannmark_JBC2010 full benchmark: 100 runs × 6 algorithms, FEV=2000, mean-MSE objective."""

from __future__ import annotations

import json
import sys
import time
import warnings
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
PREFIX = "brannmark_REAL_noReg_R100_B2000"
N_RUNS = 100
FEV = 2000
SEED0 = 2026
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


def main() -> None:
    t0_all = time.perf_counter()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    progress_path = OUT_DIR / "progress_every10.txt"

    ctx = bm.build_context()
    base = benchmark_dir()
    df_c = pd.read_csv(base / "experimentalCondition_Brannmark_JBC2010.tsv", sep="\t")
    plot_x_arr = merge_plot_x(ctx.df_m, df_c).to_numpy(dtype=float)

    params_rows: list[dict] = []
    metrics_rows: list[dict] = []
    best: dict[str, dict] = {
        key: {"mse": float("inf"), "x": None, "preds": None} for _, key, _ in ALGO_SPECS
    }

    seeds = [SEED0 + k for k in range(N_RUNS)]
    if seeds[-1] != 2125:
        raise ValueError(f"Expected last seed 2125, got {seeds[-1]}")

    meta: dict = {
        "benchmark": "Brannmark_JBC2010",
        "objective": "mean(MSE_IR1_P, MSE_IRS1_P, MSE_IRS1_P_DosR)",
        "n_params_optimized": len(ctx.param_ids),
        "sigma_fixed": sorted(bm.SIGMA_PARAM_IDS),
        "fev_per_run": FEV,
        "n_runs_per_algorithm": N_RUNS,
        "algorithms": [a for a, _, _ in ALGO_SPECS],
        "seeds": {"first": SEED0, "last": seeds[-1], "count": N_RUNS},
        "started_unix": time.time(),
    }
    (OUT_DIR / f"{PREFIX}_metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    for label, key, runner in ALGO_SPECS:
        for rep in range(N_RUNS):
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

            n_ok = len(metrics_rows)
            if n_ok % 10 == 0:
                tail = f"progress: {n_ok} successful runs completed (checkpoint every 50)\n"
                with open(progress_path, "a", encoding="utf-8") as fp:
                    fp.write(tail)

            if n_ok > 0 and n_ok % 50 == 0:
                ck = OUT_DIR / f"checkpoint_every50_ck{n_ok:03d}.csv"
                pd.DataFrame(metrics_rows).to_csv(ck, index=False)

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
