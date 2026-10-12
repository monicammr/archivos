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
    box(cols[4] + 1.2, yM, h, "Backward\nelimination:\ninclusion-minimal $S$;\nexternal validation", 7, GREEN, w=W - 0.4)
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


def fig1_example():
    """Alternative overview (not in the paper): the six steps illustrated with the real computation for Boehm."""
    from matplotlib.gridspec import GridSpec
    from matplotlib.colors import TwoSlopeNorm
    D = json.loads((RES / "fig1" / "boehm.json").read_text())
    nm = D["names"]; bio = D["bio"]
    lab = {"Epo_degradation_BaF3": "$k_{\\mathrm{Epo}}$", "k_exp_hetero": "$k_{\\mathrm{exp,het}}$",
           "k_exp_homo": "$k_{\\mathrm{exp,hom}}$", "k_imp_hetero": "$k_{\\mathrm{imp,het}}$",
           "k_imp_homo": "$k_{\\mathrm{imp,hom}}$", "k_phos": "$k_{\\mathrm{phos}}$"}
    RED, BLUE, GREY, INK, MUTED = "#c0392b", "#2a78d6", "#9a9a9a", "#222222", "#6b6b6b"
    OBS = {"pSTAT5A_rel": ("pSTAT5A", "#2a78d6"), "pSTAT5B_rel": ("pSTAT5B", "#eb6834"), "rSTAT5A_rel": ("rSTAT5A", "#1baf7a")}
    t = np.array(D["time"]); obs = np.array(D["obs"]); y = np.array(D["data"]); y0 = np.array(D["y0"])

    fig = plt.figure(figsize=(7.2, 5.3))
    gs = GridSpec(2, 3, figure=fig, hspace=0.62, wspace=0.45, left=0.075, right=0.985, top=0.855, bottom=0.08)
    # ---- flow ribbon
    rib = fig.add_axes([0.01, 0.925, 0.98, 0.07]); rib.axis("off"); rib.set_xlim(0, 6); rib.set_ylim(0, 1)
    steps = [("Data", "divided by noise $\\sigma_i$"), ("Sensitivity", "matrix $J$"),
             ("Stage 1", "greedy by $E_j$"), ("Stage 2", "greedy by $s_j$"),
             ("Admissibility", "re-estimate $\\theta_S$"), ("Validation", "predict new data")]
    for i, (t1, t2) in enumerate(steps):
        x = i + 0.02
        ec = RED if i == 4 else BLUE
        rib.add_patch(FancyBboxPatch((x, 0.04), 0.88, 0.92, boxstyle="round,pad=0,rounding_size=0.06",
                                     fc="#fbeae8" if i == 4 else "#eef3fb", ec=ec, lw=0.9, mutation_aspect=0.12))
        rib.text(x + 0.11, 0.5, str(i + 1), ha="center", va="center", color="white", fontsize=7, fontweight="bold",
                 bbox=dict(boxstyle="circle,pad=0.25", fc=ec, ec="none"))
        rib.text(x + 0.22, 0.68, t1, ha="left", va="center", fontsize=6.9, fontweight="bold", color=INK)
        rib.text(x + 0.22, 0.28, t2, ha="left", va="center", fontsize=5.7, color=MUTED)
        if i < 5:
            rib.annotate("", (x + 0.99, 0.5), (x + 0.9, 0.5), arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=0.9))

    def tag(ax, letter, title):
        ax.text(-0.02, 1.07, letter, transform=ax.transAxes, fontweight="bold", fontsize=10, ha="right", va="bottom")
        ax.text(0.0, 1.07, title, transform=ax.transAxes, fontsize=7.4, ha="left", va="bottom", color=INK)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.tick_params(labelsize=6.5, length=2.5, color=MUTED)
        for sp in ("left", "bottom"):
            ax.spines[sp].set_color(MUTED)

    # ---- a: data and model at theta0
    a = fig.add_subplot(gs[0, 0])
    for o, (txt, c) in OBS.items():
        m = obs == o; k = np.argsort(t[m])
        a.plot(t[m][k], y0[m][k], color=c, lw=1.2)
        a.scatter(t[m], y[m], s=9, color=c, edgecolor="white", linewidth=0.4, zorder=3)
        a.text(t[m][k][-1] + 6, y0[m][k][-1] + {"pSTAT5A": 1.2, "pSTAT5B": -1.0, "rSTAT5A": 0.0}[txt], txt, color=c, fontsize=6.2, va="center")
    a.set_xlim(-5, 300); a.set_xlabel("time (min)", fontsize=6.8); a.set_ylabel("measurement $/\\,\\sigma_i$", fontsize=6.8)
    tag(a, "a", "Measured data and model at $\\theta_0$")

    # ---- b: sensitivity matrix
    b = fig.add_subplot(gs[0, 1])
    J = np.array(D["J"]); ordr = np.lexsort((t, obs)); Jo = J[ordr]
    v = np.abs(Jo).max()
    im = b.imshow(Jo, aspect="auto", cmap="RdBu_r", norm=TwoSlopeNorm(0, -v, v), interpolation="nearest")
    b.set_xticks(range(len(bio))); b.set_xticklabels([lab[nm[j]] for j in bio], rotation=55, fontsize=6.2, ha="right")
    ob = obs[ordr]; cuts = [i for i in range(1, len(ob)) if ob[i] != ob[i - 1]]
    for c_ in cuts:
        b.axhline(c_ - 0.5, color="white", lw=1.2)
    mids = [0] + cuts + [len(ob)]
    b.set_yticks([(mids[i] + mids[i + 1]) / 2 - 0.5 for i in range(3)])
    b.set_yticklabels([OBS[ob[mids[i]]][0] for i in range(3)], fontsize=6.2)
    cb = fig.colorbar(im, ax=b, fraction=0.05, pad=0.03); cb.ax.tick_params(labelsize=5.8); cb.outline.set_visible(False)
    tag(b, "b", "Relative sensitivity $J$ (48 outputs)")
    b.spines["left"].set_visible(False); b.spines["bottom"].set_visible(False)

    # ---- c: stage 1
    c = fig.add_subplot(gs[0, 2])
    E = np.array(D["E"]); Es = 100 * E / E.sum()
    o1 = [bio.index(j) for j in D["order1"]]
    S1 = set(D["S1"]); rej = set(D["rej1"])
    yy = np.arange(len(o1))[::-1]
    for yk, k in zip(yy, o1):
        j = bio[k]
        if j in rej:
            c.barh(yk, Es[k], color="white", edgecolor=GREY, hatch="////", lw=0.6, height=0.62)
            c.text(Es[k] + 1, yk, f"rejected: $\\kappa={D['rej2'][str(j)]:.0f}$", fontsize=5.8, va="center", color=MUTED)
        else:
            c.barh(yk, Es[k], color=BLUE, height=0.62)
    c.set_yticks(yy); c.set_yticklabels([lab[nm[bio[k]]] for k in o1], fontsize=6.4)
    c.set_xlabel("share of energy $E_j/E$ (%)", fontsize=6.8)
    c.text(0.98, 0.04, f"$R_{{\\mathrm{{var}}}}={100 * D['rvar_S1']:.0f}\\%<\\tau_R=89\\%$\n$\\Rightarrow$ go to stage 2",
           transform=c.transAxes, ha="right", va="bottom", fontsize=6.2, color=RED)
    tag(c, "c", "Stage 1: greedy by energy")

    # ---- d: stage 2
    d = fig.add_subplot(gs[1, 0])
    sj = np.array(D["s"]); o2 = list(np.argsort(-sj)); yy = np.arange(len(o2))[::-1]
    SF = set(D["SF"])
    rej2 = {int(kk): vv for kk, vv in D["rej2"].items()}
    for yk, k in zip(yy, o2):
        j = bio[k]
        if j in rej2:
            d.barh(yk, sj[k], color="white", edgecolor=GREY, hatch="////", lw=0.6, height=0.62)
            d.text(sj[k] + 0.05, yk, f"rejected: $\\kappa={rej2[j]:.0f}$", fontsize=5.8, va="center", color=MUTED)
        else:
            d.barh(yk, sj[k], color=RED if j in SF else "#e3e3e3", height=0.62)
    d.set_yticks(yy); d.set_yticklabels([lab[nm[bio[k]]] for k in o2], fontsize=6.4)
    d.set_xlabel("effect of a 10% change, $s_j$", fontsize=6.8)
    d.text(0.98, 0.04, f"selected $S$: $\\kappa={D['kappa_SF']:.1f}$, VIF $={D['vif_SF']:.1f}$", transform=d.transAxes, ha="right", va="bottom", fontsize=6.2, color=RED)
    tag(d, "d", "Stage 2: greedy by finite effect")

    # ---- e: admissibility
    e = fig.add_subplot(gs[1, 1])
    rng = np.random.default_rng(1)
    er, ef = 100 * np.array(D["e2_rel"]), 100 * np.array(D["e2_fit"])
    jit = rng.uniform(-0.12, 0.12, len(er))
    e.scatter(np.zeros_like(er) + jit, er, s=12, facecolor="white", edgecolor=MUTED, lw=0.7, zorder=3)
    e.scatter(np.ones_like(ef) + jit, ef, s=12, color=RED, edgecolor="white", lw=0.4, zorder=3)
    for x_, v_ in ((0, er), (1, ef)):
        e.plot([x_ - 0.25, x_ + 0.25], [np.median(v_)] * 2, color=INK, lw=1.2)
    e.set_yscale("log")
    e.axhline(100 * TAU, color=INK, ls="--", lw=0.8)
    e.text(1.72, 100 * TAU * 1.1, "$\\tau_e=43.6\\%$", fontsize=6.0, ha="right", va="bottom")
    e.set_xticks([0, 1]); e.set_xticklabels(["$\\theta_S$ fixed\n($e_{\\mathrm{rel}}$)", "$\\theta_S$ re-estimated\n($e_{\\mathrm{fit}}$)"], fontsize=6.4)
    e.set_xlim(-0.55, 1.75); e.set_ylim(1, 900)
    from matplotlib.ticker import FuncFormatter
    e.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    e.set_ylabel("relative error (%)", fontsize=6.8)
    e.text(1.3, np.median(ef), "median\n" + f"{np.median(ef):.1f}%", fontsize=6.0, ha="left", va="center", color=RED)
    tag(e, "e", "15 random $\\pm$5% scenarios")

    # ---- f: validation
    f = fig.add_subplot(gs[1, 2])
    o = "pSTAT5A_rel"; m = obs == o; k = np.argsort(t[m])
    ts = D["t_split"]
    f.axvspan(ts, 260, color="#f1f1f1", lw=0)
    f.text((ts + 260) / 2, 0.97, "held out", transform=f.get_xaxis_transform(), ha="center", va="top", fontsize=6, color=MUTED)
    f.scatter(t[m], y[m], s=9, color=INK, zorder=3, label="data")
    pr = {kk: np.array(vv) for kk, vv in D["pred"].items()}
    f.plot(t[m][k], pr["full"][m][k], color=GREY, ls="--", lw=1.1, label=f"full model ($\\chi^2/n$ {D['chi_test']['full']:.1f})")
    f.plot(t[m][k], pr["red"][m][k], color=RED, lw=1.4, label=f"reduced, 2 parameters ({D['chi_test']['red']:.1f})")
    f.set_xlim(-5, 260); f.set_xlabel("time (min)", fontsize=6.8); f.set_ylabel("pSTAT5A $/\\,\\sigma_i$", fontsize=6.8)
    f.legend(fontsize=5.8, frameon=False, loc="lower right", handlelength=1.6)
    tag(f, "f", "Refit to $t<80$, predict $t\\geq80$")
    fig.savefig(HERE / "alternativas" / "fig1_example_boehm.pdf"); plt.close(fig)


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
    fig.subplots_adjust(left=0.14, right=0.985, top=0.885, bottom=0.115, wspace=0.16)
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
        er, ef = 100 * d.get("erel_med", np.nan), 100 * d["eajuste_med"]
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
    fig.text(0.5, 0.982, "Parameter reduction and recovery of the full-model output in 34 benchmark problems",
             ha="center", va="top", fontsize=9.6, fontweight="bold", color=INK)
    # ---- legend, below both panels
    h = [Line2D([], [], marker="o", ls="", color=GREY, ms=4.5, label="full model, $p$"),
         Line2D([], [], marker="o", ls="", color=BLUE, ms=4.8, label="retained, $|S|+|\\Theta_C|$"),
         Line2D([], [], marker="o", ls="", mfc="white", mec=GREY, ms=4.8, label="before, $e_{\\mathrm{rel}}$"),
         Line2D([], [], marker="o", ls="", color=GREEN, ms=4.8, label="after, $e_{\\mathrm{fit}}$"),
         Line2D([], [], marker="*", ls="", color=GREEN, ms=7, label="after, first-order estimate"),
         Line2D([], [], marker="D", ls="", mfc="white", mec=ORANGE, ms=4.8, label="not admissible"),
         Patch(fc="#e8f6f0", ec="none", label="admissible region, $e_{\\mathrm{fit}}\\leq\\tau_e$")]
    fig.legend(handles=h, loc="lower center", ncol=4, fontsize=6.8, frameon=False, bbox_to_anchor=(0.56, 0.005),
               columnspacing=1.6, handletextpad=0.4)
    fig.savefig(OUT / "fig2_benchmark.pdf"); plt.close(fig)


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
