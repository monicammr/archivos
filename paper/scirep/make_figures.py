#!/usr/bin/env python3
"""Figures for the Scientific Reports manuscript, generated from the results in certificados/resultados.

  fig1_pipeline.pdf   method overview (flow diagram)
  fig2_benchmark.pdf  (a) parameters: total p, calibration, selected biological k
                      (b) fidelity at ±5 %: cos Δ, e_rel (no re-estimation) and e_fit (re-estimation)
  fig3_validation.pdf held-out experimental conditions: χ²/n of the reduced vs the full model
  fig4_robustness.pdf median e_fit versus perturbation size (±1 % to ±50 %)

Usage: python3 make_figures.py   (writes figures/*.pdf)
"""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = Path(__file__).resolve().parent
RES = HERE.parent.parent / "certificados" / "resultados"
OUT = HERE / "figures"
OUT.mkdir(exist_ok=True)
TAU = float(np.sqrt(1 - 0.9 ** 2))
plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans"],
                     "font.size": 8, "axes.linewidth": 0.8, "pdf.fonttype": 42})


def short(name):
    return name.split("_")[0]


def load(d):
    return {f.stem: json.loads(f.read_text()) for f in sorted((RES / d).glob("*.json"))}


SEL = load("reclasificacion_salidas_bio_poda")
VAL = load("validacion_externa_bio")
PAT = {k: v for k, v in load("patrones").items() if "niveles" in v}


def fig1():
    fig, ax = plt.subplots(figsize=(7.0, 2.9))
    ax.set_xlim(-1, 101); ax.set_ylim(0, 40); ax.axis("off")
    W, G = 18.4, 2.0
    X = [i * (W + G) for i in range(5)]
    boxes = [
        (X[0], 22, W, 15, "Measured outputs\n$y_i=h(g_i(x(t_i),\\theta))/\\sigma_i$\nPEtab conditions,\nnoise, transforms"),
        (X[1], 22, W, 15, "Parameter classes\nbiological $\\theta_B$\ncalibration $\\theta_C$\n(always re-estimated)"),
        (X[2], 22, W, 15, "Relative sensitivity\n$J=\\partial y/\\partial\\log\\theta$\nenergies $E_j$"),
        (X[3], 22, W, 15, "Stage 1: greedy\nselection by $E_j$\n$\\kappa$, VIF $\\leq\\tau_\\kappa$\nuntil $R_{\\mathrm{var}}\\geq\\tau_R$"),
        (X[4], 22, W, 15, "Admissible?\n$|S|\\geq 2$ and median\n$e_{\\mathrm{fit}}(S)\\leq\\tau_e$\n(re-estimate $\\theta_S,\\theta_C$)"),
        (X[3], 1, W, 14, "Stage 2: greedy\nselection by finite\neffect $s_j$ until\nadmissible"),
        (X[4], 1, W, 14, "Backward\nelimination:\ninclusion-minimal $S$;\nexternal validation"),
    ]
    for x, y, w, h, t in boxes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.2",
                                    fc="#f2f5fa", ec="#3b5b8c", lw=0.9))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=6.6)
    arr = dict(arrowstyle="-|>", color="#3b5b8c", lw=0.9)
    for i in range(4):
        ax.annotate("", (X[i + 1] - 0.4, 29.5), (X[i] + W + 0.4, 29.5), arrowprops=arr)
    cx3, cx4 = X[3] + W / 2, X[4] + W / 2
    ax.annotate("", (cx3 + 3, 15.4), (cx4 - 3, 21.6), arrowprops=arr)
    ax.text((cx3 + cx4) / 2 - 1, 19.5, "no", fontsize=6.6, color="#3b5b8c")
    ax.annotate("", (cx4 + 3, 15.4), (cx4 + 3, 21.6), arrowprops=arr)
    ax.text(cx4 + 4, 17.8, "yes", fontsize=6.6, color="#3b5b8c")
    ax.annotate("", (X[4] - 0.4, 8), (X[3] + W + 0.4, 8), arrowprops=arr)
    fig.savefig(OUT / "fig1_pipeline.pdf", bbox_inches="tight"); plt.close(fig)


def fig2():
    rows = sorted(SEL.values(), key=lambda d: d["p"])
    n = len(rows); yy = np.arange(n)
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 5.6), sharey=True,
                               gridspec_kw={"width_ratios": [1, 1.2]})
    lc = False
    for i, d in enumerate(rows):
        p, c, k = d["p"], len(d.get("calibracion", [])), len(d["S"])
        a.plot([k, p], [i, i], color="0.8", lw=0.8, zorder=1)
        a.scatter(p, i, s=14, marker="o", color="0.45", zorder=2, label="all parameters $p$" if i == 0 else None)
        if c:
            a.scatter(c, i, s=14, marker="s", color="#4c8bc9", zorder=3,
                      label=None if lc else "calibration $|\\Theta_C|$")
            lc = True
        a.scatter(k, i, s=18, marker="D", color="#c0392b" if d["admisible"] else "white",
                  edgecolor="#c0392b", zorder=4, label="selected biological $|S|$" if i == 0 else None)
    a.set_xscale("log"); a.set_xlabel("Number of parameters")
    a.set_yticks(yy); a.set_yticklabels([short(d["sistema"]) for d in rows], fontsize=6.5)
    a.legend(loc="lower right", fontsize=6.5, frameon=False)
    a.text(-0.02, 1.01, "a", transform=a.transAxes, fontweight="bold", fontsize=10, ha="right")
    for i, d in enumerate(rows):
        e = d.get("eajuste_med", np.nan); r = d.get("erel_med", np.nan)
        b.plot([e, r], [i, i], color="0.85", lw=0.8, zorder=1)
        b.scatter(r, i, s=14, marker="o", facecolor="white", edgecolor="0.4", zorder=2,
                  label="$e_{\\mathrm{rel}}$ (no re-estimation)" if i == 0 else None)
        b.scatter(e, i, s=18, marker="D", color="#c0392b" if d["admisible"] else "white",
                  edgecolor="#c0392b", zorder=3, label="$e_{\\mathrm{fit}}$ (re-estimation)" if i == 0 else None)
    b.axvline(TAU, color="k", ls="--", lw=0.8)
    b.text(TAU * 1.04, n - 0.6, "$\\tau_e=0.436$", fontsize=6.5)
    b.set_xscale("symlog", linthresh=0.01); b.set_xlim(0, 3)
    b.set_xlabel("Median relative error at $\\pm$5 % (15 scenarios)")
    b.legend(loc="lower right", fontsize=6.5, frameon=False)
    b.text(-0.02, 1.01, "b", transform=b.transAxes, fontweight="bold", fontsize=10, ha="right")
    fig.tight_layout(); fig.savefig(OUT / "fig2_benchmark.pdf", bbox_inches="tight"); plt.close(fig)


def fig3():
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 3.2))
    for ax, key, lab in ((a, "A_chi2_test_full", "full model re-estimated on training data"),
                         (b, "A_chi2_test_theta0", "published estimate $\\theta_0$ (all data)")):
        xs, ys, nm = [], [], []
        for k, d in VAL.items():
            r, f = d.get("A_chi2_test_red"), d.get(key)
            t0 = d.get("A_chi2_test_theta0")
            if r is None or f is None or not (np.isfinite(r) and np.isfinite(f)) or r <= 0 or f <= 0:
                continue
            if t0 is not None and t0 < 1e-2:      # noise-free benchmark data: χ² not interpretable
                continue
            xs.append(f); ys.append(r); nm.append(short(k))
        xs, ys = np.array(xs), np.array(ys)
        lo, hi = min(xs.min(), ys.min()) / 2, max(xs.max(), ys.max()) * 2
        ax.plot([lo, hi], [lo, hi], "k--", lw=0.7)
        better = ys <= xs * 1.05
        ax.scatter(xs[better], ys[better], s=16, color="#c0392b", zorder=3)
        ax.scatter(xs[~better], ys[~better], s=16, facecolor="white", edgecolor="#c0392b", zorder=3)
        for x, y, t in zip(xs, ys, nm):
            if abs(np.log10(y / x)) < 0.3 and y < 20:
                continue
            ax.annotate(t, (x, y), fontsize=5.5, xytext=(2, 2), textcoords="offset points", color="0.3")
        ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
        ax.set_xlabel(f"Test $\\chi^2/n$, {lab}"); ax.set_ylabel("Test $\\chi^2/n$, reduced model")
        ax.set_aspect("equal")
    a.text(-0.12, 1.02, "a", transform=a.transAxes, fontweight="bold", fontsize=10)
    b.text(-0.12, 1.02, "b", transform=b.transAxes, fontweight="bold", fontsize=10)
    fig.tight_layout(); fig.savefig(OUT / "fig3_validation.pdf", bbox_inches="tight"); plt.close(fig)


def fig4():
    lv = [1, 5, 10, 20, 30, 40, 50]
    col = {"A": "#4c8bc9", "B": "#c0392b", "C": "#e69f00", "D": "0.3"}
    fig, ax = plt.subplots(figsize=(4.6, 3.2))
    seen = set()
    for k, d in sorted(PAT.items()):
        y = [d["niveles"].get(str(l), {}).get("eaj_med", np.nan) for l in lv]
        pt = d["patron"]
        ax.plot(lv, y, "-o", ms=2.5, lw=0.9, color=col[pt], alpha=0.85,
                label=f"pattern {pt}" if pt not in seen else None)
        seen.add(pt)
        if pt != "A":
            ax.annotate(short(k), (lv[-1], y[-1]), fontsize=5.5, xytext=(3, 0), textcoords="offset points",
                        color=col[pt])
    ax.axhline(TAU, color="k", ls="--", lw=0.8)
    ax.text(1.05, TAU * 1.05, "$\\tau_e=0.436$", fontsize=6.5)
    ax.set_xscale("log"); ax.set_xticks(lv); ax.set_xticklabels([f"{l}" for l in lv])
    ax.set_xlabel("Perturbation size (±%)"); ax.set_ylabel("Median $e_{\\mathrm{fit}}$ (15 scenarios)")
    ax.set_ylim(0, 0.8); ax.set_xlim(0.9, 75)
    ax.legend(fontsize=6.5, frameon=False, loc="upper left")
    fig.tight_layout(); fig.savefig(OUT / "fig4_robustness.pdf", bbox_inches="tight"); plt.close(fig)


def exportar():
    """Archivos individuales para el envío: EPS (vectorial) y TIFF a 300 dpi."""
    import subprocess
    for f in sorted(OUT.glob("fig*.pdf")):
        subprocess.run(["pdftops", "-eps", str(f), str(f.with_suffix(".eps"))], check=True)
        subprocess.run(["pdftoppm", "-tiff", "-tiffcompression", "lzw", "-r", "300", "-singlefile",
                        str(f), str(f.with_suffix(""))], check=True)


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4(); exportar()
    print("figures written to", OUT)
