#!/usr/bin/env python3
"""Figures of the paper, generated from the stored results (written to figures/ of the output folder).

  fig1_pipeline.pdf      method overview (schematic)
  fig2_benchmark.pdf     (a) reduction from the full to the retained parameters;
                         (b) error before and after re-estimation at +-5 %          [results/selection]
  fig3_validation.pdf    prediction of held-out experiments (ratio plot) and
  figS1_validation_scatter.pdf  the same as a scatter plot      [results/external_validation]
  fig4_robustness.pdf    median e_fit and pass rate versus perturbation size     [results/robustness]
  fig5_settings.pdf      sensitivity of the selection to the method settings    [results/settings]
  fig6_architecture.pdf  architecture of the formal and numerical verification (TikZ)
Each figure is also exported as EPS and as TIFF at 300 dpi (individual files for submission).

Usage: python make_figures.py
"""
import os
import shutil
import subprocess
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from common import efit_final, fmt_efit, HERE, FIG as OUT, load

TAU = float(np.sqrt(1 - 0.9 ** 2))
plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans"],
                     "font.size": 8, "axes.linewidth": 0.8, "pdf.fonttype": 42})


def short(name):
    return name.split("_")[0]


SEL = load("selection")
VAL = load("external_validation")


def fig1():
    """Method overview: the steps of the method arranged by phase, with the stage-1/stage-2 decision loop."""
    from matplotlib.patches import Polygon
    INK, MUTED = "#222222", "#6b6b6b"
    BLUE, ORANGE, GREEN = "#2a78d6", "#eb6834", "#1baf7a"
    fig, ax = plt.subplots(figsize=(7.0, 2.9))
    ax.set_xlim(0, 100); ax.set_ylim(0, 42); ax.axis("off")
    W = 17.4
    cols = [0.9 + 20.0 * i for i in range(5)]
    phases = ["Inputs", "Sensitivity", "Selection", "Decision", "Result"]
    for x, ph in zip(cols, phases):                   # phase columns
        ax.text(x + W / 2, 38.6, ph.upper(), ha="center", va="center", fontsize=6.6,
                color={"Decision": ORANGE, "Result": GREEN}.get(ph, BLUE),
                fontweight="bold", zorder=1)

    def box(x, y, h, text, n, color, fc="white", w=None, ls="-"):
        w = W if w is None else w
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.0",
                                    fc=fc, ec=color, lw=1.0, ls=ls, zorder=2))
        ax.text(x + w / 2 + 0.3, y + h / 2, text, ha="center", va="center", fontsize=6.0, color=INK, zorder=3,
                linespacing=1.25)
        ax.text(x + 0.2, y + h - 0.2, str(n), ha="center", va="center", fontsize=6.2, fontweight="bold",
                color="white", zorder=4, bbox=dict(boxstyle="circle,pad=0.22", fc=color, ec="none"))

    arr = dict(arrowstyle="-|>", color=INK, lw=0.9, shrinkA=0, shrinkB=0)
    yT, yB, h = 20.0, 3.0, 14.0        # top and bottom rows
    yM = 11.5                          # middle row
    box(cols[0], yT, h, "Measured outputs\n$y_i=h(g_i(x(t_i),\\theta))/\\sigma_i$\nPEtab conditions,\nnoise, transforms", 1, BLUE)
    box(cols[0], yB, h, "Parameter classes\nbiological $\\theta_B$\ncalibration $\\theta_C$\n(always re-estimated)", 2, BLUE)
    box(cols[1], yM, h, "Relative sensitivity\n$J=\\partial y/\\partial\\log\\theta$\nenergies $E_j$", 3, BLUE)
    box(cols[2], yT, h, "Stage 1: greedy\nselection by $E_j$\n$\\kappa$, VIF $\\leq\\tau_\\kappa$\nuntil $R_{\\mathrm{var}}\\geq\\tau_R$", 4, BLUE)
    box(cols[2], yB, h, "Stage 2: greedy\nselection by finite\neffect $s_j$ until\nadmissible", 5, ORANGE, ls=(0, (3, 1.5)))
    box(cols[4] + 1.2, yM, h, "Backward\nelimination:\nno single parameter\ncan be removed;\nexternal validation", 7, GREEN, w=W - 0.4)
    # decision node (hexagon)
    cx, cy, hw, hh = cols[3] + W / 2, yM + h / 2, W / 2 + 0.2, 9.2
    hexa = [(cx - hw, cy), (cx - hw + 3, cy + hh), (cx + hw - 3, cy + hh), (cx + hw, cy), (cx + hw - 3, cy - hh), (cx - hw + 3, cy - hh)]
    ax.add_patch(Polygon(hexa, closed=True, fc="#fdf0ea", ec=ORANGE, lw=1.0, zorder=2))
    ax.text(cx, cy, "Admissible?\n$|S|\\geq 2$ and median\n$e_{\\mathrm{fit}}(S)\\leq\\tau_e$\n(re-estimate $\\theta_S,\\theta_C$)",
            ha="center", va="center", fontsize=6.0, color=INK, zorder=3, linespacing=1.25)
    ax.text(cx - hw + 2.2, cy + hh - 0.6, "6", ha="center", va="center", fontsize=6.2, fontweight="bold", color="white",
            zorder=4, bbox=dict(boxstyle="circle,pad=0.22", fc=ORANGE, ec="none"))
    # arrows: inputs -> sensitivity
    xin = cols[1] - 0.2
    for y0_ in (yT + h / 2, yB + h / 2):
        ax.annotate("", (xin, yM + h / 2 + (2.5 if y0_ > yM + h / 2 else -2.5)), (cols[0] + W + 0.2, y0_), arrowprops=dict(arr, connectionstyle="arc3,rad=0"))
    # sensitivity -> stage 1
    ax.annotate("", (cols[2] - 0.2, yT + h / 2), (cols[1] + W + 0.2, yM + h / 2 + 2.5), arrowprops=arr)
    # stage 1 -> decision
    ax.annotate("", (cx - hw + 1.2, cy + 3.6), (cols[2] + W + 0.2, yT + h / 2), arrowprops=arr)
    # decision -> no -> stage 2 (bottom loop)
    yl = 1.3
    ax.plot([cx, cx, cols[2] + W / 2], [cy - hh, yl, yl], color=ORANGE, lw=0.9, zorder=1, solid_joinstyle="round")
    ax.annotate("", (cols[2] + W / 2, yB - 0.1), (cols[2] + W / 2, yl), arrowprops=dict(arr, color=ORANGE))
    ax.text(cx + 1.0, (cy - hh + yl) / 2, "no", fontsize=6.0, color=ORANGE, fontweight="bold", va="center")
    # stage 2 -> decision
    ax.annotate("", (cx - hw + 1.2, cy - 3.6), (cols[2] + W + 0.2, yB + h / 2), arrowprops=dict(arr, color=ORANGE))
    # decision -> yes -> result
    ax.annotate("", (cols[4] + 1.0, cy), (cx + hw + 0.2, cy), arrowprops=dict(arr, color=GREEN))
    ax.text((cx + hw + cols[4] + 1.2) / 2, cy + 1.8, "yes", fontsize=6.0, color=GREEN, fontweight="bold", ha="center")
    fig.savefig(OUT / "fig1_pipeline.pdf", bbox_inches="tight", pad_inches=0.02); plt.close(fig)


def fig2():
    """(a) Reduction from the full to the retained parameters; (b) error before and after re-estimation."""
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    LIN = {"Alkan_SciSignal2018", "Bachmann_MSB2011", "Beer_MolBioSystems2014", "Chen_MSB2009",
           "Isensee_JCB2018", "Lang_PLOSComputBiol2024", "Lucarelli_CellSystems2018", "Raimundez_PCB2020"}
    INK, MUTED, GRID = "#222222", "#6b6b6b", "#e6e6e6"
    BLUE, ORANGE, GREEN, GREY = "#2a78d6", "#eb6834", "#1baf7a", "#8c8c8c"
    rows = []
    for d in SEL.values():
        k, c = len(d["S"]), len(d.get("calibracion", []))
        rows.append(dict(d=d, k=k, c=c, red=1 - (k + c) / d["p"]))
    rows.sort(key=lambda r: (not r["d"]["admisible"], -r["red"], r["d"]["sistema"].lower()))
    n = len(rows); yy = np.arange(n)[::-1]
    nad = sum(r["d"]["admisible"] for r in rows)

    fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 9.2), sharey=True, gridspec_kw={"width_ratios": [1, 1]})
    fig.subplots_adjust(left=0.14, right=0.985, top=0.91, bottom=0.115, wspace=0.16)
    for ax in (a, b):
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.spines["left"].set_color(MUTED); ax.spines["bottom"].set_color(MUTED)
        ax.tick_params(labelsize=6.8, length=2.5, color=MUTED)
        ax.axhline(yy[nad - 1] - 0.5, color=ORANGE, ls=(0, (3, 2)), lw=0.9)
    # ---- a: reduction
    for y, r in zip(yy, rows):
        d = r["d"]; p = d["p"]; ret = r["k"] + r["c"]; ok = d["admisible"]
        col = BLUE if ok else ORANGE
        a.plot([ret, p], [y, y], color="#cfd8e3" if ok else "#f5c6b1", lw=2.2, solid_capstyle="round", zorder=1)
        a.scatter(p, y, s=16, color=GREY, zorder=3)
        if ok:
            a.scatter(ret, y, s=20, color=BLUE, zorder=4)
        else:
            a.scatter(ret, y, s=26, marker="D", facecolor="white", edgecolor=ORANGE, lw=1.1, zorder=4)
        comp = f"{r['k']}" + (f"+{r['c']}" if r["c"] else "")
        a.text(p * 1.13, y, f"{100 * r['red']:.0f}%  ({comp})", va="center", fontsize=6.0, color=INK if ok else ORANGE)
    a.set_xscale("log"); a.set_xlim(0.8, 1500)
    a.set_yticks(yy); a.set_yticklabels([short(r["d"]["sistema"]) for r in rows], fontsize=6.8)
    a.set_ylim(-0.8, n - 0.2)
    a.grid(axis="x", color=GRID, lw=0.5, which="major"); a.set_axisbelow(True)
    a.set_xlabel("Number of estimated parameters (log scale)", fontsize=7.2, labelpad=4)
    # ---- b: error before / after re-estimation
    b.axvspan(0, 100 * TAU, color="#e8f6f0", lw=0, zorder=0)
    b.axvline(100 * TAU, color=INK, ls="--", lw=0.8, zorder=1)
    b.text(100 * TAU + 1.5, n - 0.6, "$\\tau_e=43.6\\%$", fontsize=6.4, va="center", color=INK)
    b.text(1.5, n - 0.6, "admissible", fontsize=6.4, va="center", color="#138a60", fontweight="bold")
    for y, r in zip(yy, rows):
        d = r["d"]; ok = d["admisible"]
        er, ef = 100 * d.get("erel_med", np.nan), 100 * efit_final(d["sistema"], d)[0]
        if d["sistema"].startswith("Crauste"):
            b.text(2, y, "not defined (no solution for 1% changes)", fontsize=6.0, va="center", color=ORANGE, style="italic")
            continue
        if er - ef > 2.5:
            b.annotate("", (ef + 1.2, y), (er - 1.2, y), arrowprops=dict(arrowstyle="-|>", color="#a8a8a8", lw=0.8, mutation_scale=6))
        b.scatter(er, y, s=18, facecolor="white", edgecolor=GREY, lw=0.9, zorder=3)
        if not ok:
            b.scatter(ef, y, s=26, marker="D", facecolor="white", edgecolor=ORANGE, lw=1.1, zorder=4)
        elif d["sistema"] in LIN:
            b.scatter(ef, y, s=50, marker="*", color=GREEN, edgecolor="white", lw=0.3, zorder=4)
        else:
            b.scatter(ef, y, s=20, color=GREEN, zorder=4)
    b.set_xlim(0, 140)
    b.grid(axis="x", color=GRID, lw=0.5); b.set_axisbelow(True)
    b.set_xlabel("Median relative error at $\\pm$5% (15 scenarios, %)", fontsize=7.2, labelpad=4)
    b.text(139, yy[nad - 1] - 0.5 + 0.35, "no admissible subset", fontsize=6.0, color=ORANGE, ha="right", va="bottom", fontweight="bold")
    # ---- panel headings: title and a separate subtitle line
    for ax, letter, title, sub in (
            (a, "a", "Reduction: full model $\\rightarrow$ retained", "labels: % reduction (biological + calibration retained)"),
            (b, "b", "Recovery: before $\\rightarrow$ after re-estimation", "re-estimation brings the error below $\\tau_e$")):
        ax.text(0.0, 1.062, letter, transform=ax.transAxes, fontsize=10, fontweight="bold", va="bottom", color=INK)
        ax.text(0.065 if ax is a else 0.07, 1.062, title, transform=ax.transAxes, fontsize=8.2, fontweight="bold", va="bottom", color=INK)
        ax.text(0.065 if ax is a else 0.07, 1.022, sub, transform=ax.transAxes, fontsize=6.6, va="bottom", color=MUTED)
    # ---- legend, below both panels
    h = [Line2D([], [], marker="o", ls="", color=GREY, ms=4.5, label="full model, $p$"),
         Line2D([], [], marker="o", ls="", color=BLUE, ms=4.8, label="retained, $|S|+|\\Theta_C|$"),
         Line2D([], [], marker="o", ls="", mfc="white", mec=GREY, ms=4.8, label="before, $e_{\\mathrm{rel}}$"),
         Line2D([], [], marker="o", ls="", color=GREEN, ms=4.8, label="after, $e_{\\mathrm{fit}}$"),
         Line2D([], [], marker="*", ls="", color=GREEN, ms=7, label="after, selected to first order (value: nonlinear check)"),
         Line2D([], [], marker="D", ls="", mfc="white", mec=ORANGE, ms=4.8, label="not admissible"),
         Patch(fc="#e8f6f0", ec="none", label="admissible region, $e_{\\mathrm{fit}}\\leq\\tau_e$")]
    fig.legend(handles=h, loc="lower center", ncol=4, fontsize=6.8, frameon=False, bbox_to_anchor=(0.56, 0.005),
               columnspacing=1.6, handletextpad=0.4)
    fig.savefig(OUT / "fig2_benchmark.pdf"); plt.close(fig)


def fig3():
    """Held-out prediction: ratio plot (main text) and scatter plot (Supplementary Fig. S1), both
    produced and verified against the consolidated table by make_figure3.py."""
    subprocess.run([sys.executable, str(HERE / "make_figure3.py")], check=True)


def fig4():
    """(a) Median e_fit versus perturbation size; (b) pass rate: share of the 15 paired scenarios with e_fit <= tau_e.
    Per-scenario data: results/robustness (robustness.py, same 15 directions at every size)."""
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.gridspec import GridSpec
    PS = load("robustness")
    lv = [1, 5, 10, 20, 30, 40, 50]
    INK, MUTED = "#222222", "#666666"
    col = {"A": "#2a78d6", "B": "#eb6834", "C": "#1baf7a", "D": "#555555"}
    fig = plt.figure(figsize=(7.2, 5.6))
    gs = GridSpec(1, 2, figure=fig, width_ratios=[1.0, 1.05], wspace=0.42, left=0.08, right=0.93, top=0.9, bottom=0.1)
    a = fig.add_subplot(gs[0, 0])
    seen = set()
    for k, d in sorted(PS.items()):
        y = [d["niveles"][str(l)]["eaj_med"] if d["niveles"].get(str(l), {}).get("eaj") else np.nan for l in lv]
        pt = d["patron"]
        a.plot(lv, 100 * np.array(y), "-o", ms=2.6, lw=0.9, color=col[pt], alpha=0.9 if pt != "A" else 0.55,
               label=f"pattern {pt} ({sum(v['patron'] == pt for v in PS.values())})" if pt not in seen else None, zorder=3 if pt != "A" else 2)
        seen.add(pt)
        if pt != "A":
            a.annotate(short(k), (lv[-1], 100 * y[-1]), fontsize=6, xytext=(4, 0), textcoords="offset points", color=col[pt], va="center")
    a.axhline(100 * TAU, color=INK, ls="--", lw=0.8)
    a.text(1.05, 100 * TAU + 1.5, "$\\tau_e=43.6\\%$", fontsize=6.5)
    a.set_xscale("log"); a.set_xticks([1, 5, 10, 20, 50]); a.set_xticklabels(["1", "5", "10", "20", "50"], fontsize=6.8); a.minorticks_off()
    a.set_xlabel("Perturbation size ($\\pm$%)", fontsize=7.5); a.set_ylabel("Median $e_{\\mathrm{fit}}$ over 15 scenarios (%)", fontsize=7.5)
    a.set_ylim(0, 80); a.set_xlim(0.9, 80); a.tick_params(labelsize=6.8)
    a.legend(fontsize=6.5, frameon=False, loc="upper left")
    for sp in ("top", "right"):
        a.spines[sp].set_visible(False)
    a.text(-0.16, 1.04, "a", transform=a.transAxes, fontsize=10.5, fontweight="bold")
    a.text(-0.06, 1.04, "Median error", transform=a.transAxes, fontsize=8.2, fontweight="bold")
    # ---- b: pass rate heat map
    b = fig.add_subplot(gs[0, 1])
    order = sorted(PS, key=lambda k: ("ABCD".index(PS[k]["patron"]),
                                      -np.nanmean([np.mean(np.array(PS[k]["niveles"][str(l)]["eaj"]) <= TAU) for l in lv
                                                   if PS[k]["niveles"][str(l)]["eaj"]]), short(k).lower()))
    M = np.full((len(order), len(lv)), np.nan)
    for i, k in enumerate(order):
        for j, l in enumerate(lv):
            e = PS[k]["niveles"][str(l)]["eaj"]
            if e:
                M[i, j] = 100 * np.mean(np.array(e) <= TAU)
    cmap = LinearSegmentedColormap.from_list("pass", ["#fbe3d6", "#f2a27a", "#9cc3ec", "#1f5fa8"])
    im = b.imshow(M, aspect="auto", cmap=cmap, vmin=0, vmax=100, interpolation="nearest")
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]
            if np.isfinite(v) and v < 100:
                b.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=6.5, color=INK if v > 40 else "#5a1d00")
            elif not np.isfinite(v):
                b.text(j, i, "--", ha="center", va="center", fontsize=6.5, color=MUTED)
    b.set_xticks(range(len(lv))); b.set_xticklabels([str(l) for l in lv], fontsize=6.8)
    b.set_yticks(range(len(order)))
    b.set_yticklabels([f"{short(k)}  {PS[k]['patron']}" for k in order], fontsize=7)
    for t, k in zip(b.get_yticklabels(), order):
        t.set_color(col[PS[k]["patron"]] if PS[k]["patron"] != "A" else INK)
    b.set_xlabel("Perturbation size ($\\pm$%)", fontsize=7.5)
    b.tick_params(length=0)
    for sp in b.spines.values():
        sp.set_visible(False)
    cb = fig.colorbar(im, ax=b, fraction=0.045, pad=0.03); cb.ax.tick_params(labelsize=6); cb.outline.set_visible(False)
    cb.set_label("Scenarios with $e_{\\mathrm{fit}}\\leq\\tau_e$ (%)", fontsize=6.8)
    b.text(-0.42, 1.04, "b", transform=b.transAxes, fontsize=10.5, fontweight="bold")
    b.text(-0.32, 1.04, "Pass rate (numbers shown below 100%)", transform=b.transAxes, fontsize=8.2, fontweight="bold")
    fig.savefig(OUT / "fig4_robustness.pdf"); plt.close(fig)


def fig5():
    subprocess.run([sys.executable, str(HERE / "make_fig5_settings.py")], check=True)


def fig6():
    """Architecture (standalone TikZ, compiled with pdflatex)."""
    shutil.copy(HERE / "fig6_architecture.tex", OUT / "fig6_architecture.tex")
    subprocess.run(["pdflatex", "-interaction=batchmode", "fig6_architecture.tex"], cwd=OUT, check=True)
    for ext in ("aux", "log"):
        (OUT / f"fig6_architecture.{ext}").unlink(missing_ok=True)


def export():
    """Individual files for submission: EPS (vector) and TIFF at 300 dpi."""
    if os.environ.get("NO_EXPORT") == "1":   # sin las copias EPS/TIFF (p. ej. sin poppler completo)
        return
    for f in sorted(OUT.glob("fig*.pdf")):
        # the PDF files are the figures of the paper; the EPS/TIFF copies are only for the journal's
        # production, so a missing or incompatible poppler only produces a warning
        for cmd in (["pdftops", "-eps", str(f), str(f.with_suffix(".eps"))],
                    ["pdftoppm", "-tiff", "-tiffcompression", "lzw", "-r", "300", "-singlefile",
                     str(f), str(f.with_suffix(""))]):
            try:
                subprocess.run(cmd, check=True, capture_output=True)
            except (OSError, subprocess.CalledProcessError) as e:
                print(f"warning: {cmd[0]} could not convert {f.name} ({e}); the PDF is unaffected")


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4(); fig5(); fig6(); export()
    print("figures written to", OUT)
