#!/usr/bin/env python3
"""Figure 3 (prediction of held-out experiments) and Supplementary Fig. S1 (the same as a scatter plot).

Source of every number: results/external_validation/<problem>.json, written by
analysis/external_validation.py (keys A_chi2_test_red, A_chi2_test_full, A_chi2_test_theta0, n_test,
division, no_evaluable). The list of the 34 problems and their admissibility come from
results/selection/<problem>.json.

Outputs (folder figure3/ of the output folder):
  figure3_heldout_data.csv    consolidated table (one row per problem, reasons for exclusion)
  figure3_summary.txt         counts quoted in the text (pairs, panels, better/equivalent/worse, ...)
  figure3_ratio.{pdf,png}     Fig. 3 (also copied to figures/fig3_validation.pdf)
  figure3_scatter.{pdf,png}   Supplementary Fig. S1 (also copied to figures/figS1_validation_scatter.pdf)
  figure3_caption.tex         caption with the numbers of problems in each panel
Every plotted point is checked against the consolidated table.

Usage: python make_figure3.py
"""
import csv
import json
import math
import shutil
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from common import RESULTS, OUT as _OUT, FIG

HERE = _OUT / "figure3"
HERE.mkdir(parents=True, exist_ok=True)
VALD = RESULTS / "external_validation"
SELD = RESULTS / "selection"
NOISE_FREE = 1e-2          # test chi2/n of theta0 below this: data reproduced to well below the recorded noise
EQ = 0.05                  # equivalence band: ratio within [0.95, 1.05]
HIGH = 10.0                # reduced chi2/n above this is flagged as a poor absolute fit
LO, HI = math.log10(1 - EQ), math.log10(1 + EQ)

DISPLAY = {"SalazarCavazos": "Salazar-Cavazos"}


def disp(problem):
    s = problem.split("_")[0]
    return DISPLAY.get(s, s)


def num(x):
    return x is not None and isinstance(x, (int, float)) and math.isfinite(x) and x > 0


# ---------------------------------------------------------------- 1. consolidated table
def build_rows():
    sel = {f.stem: json.loads(f.read_text()) for f in sorted(SELD.glob("*.json"))}
    rows = []
    for prob in sorted(sel, key=str.lower):
        f = VALD / f"{prob}.json"
        v = json.loads(f.read_text()) if f.exists() else None
        r = dict(problem=prob, system=disp(prob), admissible=sel[prob]["admisible"])
        if v is None:
            r.update(reduced=None, full=None, theta0=None, n_test=None, split="",
                     reason_a="no admissible subset (not validated)", reason_b="no admissible subset (not validated)")
            rows.append(r); continue
        red, full, th0 = v.get("A_chi2_test_red"), v.get("A_chi2_test_full"), v.get("A_chi2_test_theta0")
        split = v.get("division", "")
        r.update(reduced=red if num(red) else None, full=full if num(full) else None,
                 theta0=th0 if num(th0) else None, n_test=v.get("n_test"),
                 split="conditions" if split.startswith("condiciones") else ("time" if split else ""))
        ne = v.get("no_evaluable")
        if ne:
            why = ("selected parameters act only in the test conditions" if "exclusivos" in ne
                   else "single condition and single time point: no training/test split")
            r.update(reason_a=why, reason_b=why)
        else:
            noise_free = r["theta0"] is not None and r["theta0"] < NOISE_FREE
            nf = "noise-free benchmark data (test chi2/n of theta0 < 0.01)"
            ra = ("full model not re-estimated (155/277 parameters, computation pending)" if r["full"] is None
                  else nf if noise_free else "")
            rb = nf if noise_free else ("" if r["theta0"] is not None else "theta0 chi2 missing")
            r.update(reason_a=ra, reason_b=rb)
        rows.append(r)
    return rows


def write_csv(rows):
    p = HERE / "figure3_heldout_data.csv"
    with p.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["system", "reduced_chi2", "full_chi2", "theta0_chi2", "include_panel_a", "include_panel_b",
                    "exclusion_reason", "n_test", "split"])
        for r in rows:
            ia, ib = r["reason_a"] == "", r["reason_b"] == ""
            reason = "; ".join(x for x in dict.fromkeys([("a: " + r["reason_a"]) if not ia else "",
                                                          ("b: " + r["reason_b"]) if not ib else ""]) if x)
            f = lambda x: "" if x is None else repr(float(x))
            w.writerow([r["system"], f(r["reduced"]), f(r["full"]), f(r["theta0"]), int(ia), int(ib), reason,
                        "" if r["n_test"] is None else int(r["n_test"]), r["split"]])
    return p


def read_csv():
    with (HERE / "figure3_heldout_data.csv").open() as fh:
        return list(csv.DictReader(fh))


# ---------------------------------------------------------------- 2. counts and report
def classify(q):
    return "better" if q < 1 - EQ else ("equivalent" if q <= 1 + EQ else "worse")


def counts(rows):
    C = {}
    va = [r for r in rows if r["reduced"] is not None and r["full"] is not None]
    vb = [r for r in rows if r["reduced"] is not None and r["theta0"] is not None]
    pa = [r for r in rows if r["reason_a"] == ""]
    pb = [r for r in rows if r["reason_b"] == ""]
    for key, S, ref in (("valid_a", va, "full"), ("valid_b", vb, "theta0"), ("panel_a", pa, "full"), ("panel_b", pb, "theta0")):
        q = {r["system"]: r["reduced"] / r[ref] for r in S}
        C[key] = dict(n=len(S), names=[r["system"] for r in S], q=q,
                      better=sorted(s for s, x in q.items() if classify(x) == "better"),
                      equivalent=sorted(s for s, x in q.items() if classify(x) == "equivalent"),
                      worse=sorted(s for s, x in q.items() if classify(x) == "worse"),
                      le_twice=sorted(s for s, x in q.items() if x <= 2.0),
                      within_02pct=sorted(s for s, x in q.items() if abs(x - 1) < 0.002))
    return C


def report(rows, C):
    L = []
    w = L.append
    a, b, va, vb = C["panel_a"], C["panel_b"], C["valid_a"], C["valid_b"]
    w("FIGURE 3 - SUMMARY OF THE COUNTS")
    w("=" * 78)
    w("Source: results/external_validation/<problem>.json (analysis/external_validation.py),")
    w("keys A_chi2_test_red / A_chi2_test_full / A_chi2_test_theta0 / n_test / division / no_evaluable.")
    w("All three chi2 columns exist (A_chi2_test_theta0 included), so both panels can be built.")
    w("")
    w("1. PROBLEMS")
    w(f"   34 benchmark problems; {sum(r['admissible'] for r in rows)} admissible; external validation was run for the admissible ones.")
    w("   Not validated (no admissible subset): Beer, Crauste.")
    nsplit = [r for r in rows if r["reduced"] is not None]
    w(f"   Validation possible (train/test split): {len(nsplit)}  "
      f"(by condition {sum(r['split']=='conditions' for r in nsplit)}, by time {sum(r['split']=='time' for r in nsplit)})")
    w("   No valid split: Bertozzi (selected parameters act only in the test conditions),")
    w("                   Blasi (single condition and single time point).")
    w("")
    w("2. VALID PAIRS")
    w(f"   reduced_chi2 and full_chi2 both valid:   {va['n']}  (missing full: Chen, Lang - full re-estimation not run)")
    w(f"   reduced_chi2 and theta0_chi2 both valid: {vb['n']}")
    nf = sorted(r["system"] for r in rows if r["theta0"] is not None and r["theta0"] < NOISE_FREE)
    w(f"   Noise-free data (test chi2/n of theta0 < {NOISE_FREE}): {', '.join(nf)}")
    for r in rows:
        if r["system"] in nf:
            w(f"      {r['system']:10s} reduced {r['reduced']:.3g}  full {r['full']:.3g}  theta0 {r['theta0']:.3g}")
    w("   For these, chi2/n is far below 1 for every fit: the recorded noise is much larger than the scatter,")
    w("   so ratios of tiny numbers are not informative; they are excluded from the figure (as in the current one).")
    w("")
    w("3. PANELS OF THE FIGURE")
    w(f"   Panel a (reduced vs full):   n = {a['n']}   excluded: Bertozzi, Blasi (no split); Chen, Lang (no full refit);")
    w(f"                                         {', '.join(nf)} (noise-free); Beer, Crauste (not admissible)")
    w(f"   Panel b (reduced vs theta0): n = {b['n']}   excluded: Bertozzi, Blasi (no split); {', '.join(nf)} (noise-free);")
    w("                                         Beer, Crauste (not admissible)")
    w("")
    w("4. COUNTS (ratio q = reduced/reference; equivalent if 0.95 <= q <= 1.05)")
    for key, title in (("valid_a", "all valid pairs, reduced vs full"), ("panel_a", "panel a, reduced vs full"),
                       ("valid_b", "all valid pairs, reduced vs theta0"), ("panel_b", "panel b, reduced vs theta0")):
        c = C[key]
        w(f"   {title} (n = {c['n']}):")
        w(f"      better (q < 0.95):              {len(c['better']):2d}")
        w(f"      equivalent (0.95 <= q <= 1.05): {len(c['equivalent']):2d}  {', '.join(c['equivalent'])}")
        w(f"      worse (q > 1.05):               {len(c['worse']):2d}  {', '.join(c['worse'])}")
        w(f"      equivalent or better:           {len(c['better']) + len(c['equivalent']):2d} of {c['n']}")
        w(f"      q <= 2:                         {len(c['le_twice']):2d} of {c['n']}")
        w(f"      |q - 1| < 0.2 %:                {', '.join(c['within_02pct'])}")
    w("")
    hi_red = sorted((r["system"], r["reduced"]) for r in rows if r["reduced"] is not None and r["reduced"] > HIGH and r["reason_b"] == "")
    w(f"5. POOR ABSOLUTE FIT (reduced chi2/n > {HIGH:g}, shown with a marker in the figure)")
    for s, x in hi_red:
        rr = next(r for r in rows if r["system"] == s)
        w(f"   {s:16s} reduced {x:.4g}   theta0 {rr['theta0']:.4g}" + (f"   full {rr['full']:.4g}" if rr['full'] else ""))
    th_hi = sorted(r["system"] for r in rows if r["theta0"] is not None and r["theta0"] > HIGH)
    w(f"   theta0 itself has chi2/n > {HIGH:g} in: {', '.join(th_hi)}")
    w("")
    (HERE / "figure3_summary.txt").write_text("\n".join(L) + "\n")
    return L


# ---------------------------------------------------------------- 3. figures
INK, MUTED, GRID = "#222222", "#666666", "#e3e3e3"
C_BETTER, C_EQ, C_WORSE = "#0f7c8c", "#3d3d3d", "#e8590c"
MK = {"better": "o", "equivalent": "s", "worse": "^"}
COL = {"better": C_BETTER, "equivalent": C_EQ, "worse": C_WORSE}
plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans"], "font.size": 7.5,
                     "axes.linewidth": 0.7, "pdf.fonttype": 42, "ps.fonttype": 42})


def fmt_ratio(q):
    if q >= 10:
        return f"×{q:.0f}"
    if q >= 0.995:
        return f"×{q:.2f}"
    if q >= 0.1:
        return f"×{q:.2f}"
    return f"×{q:.2g}"


def fmt_chi(x):
    if x >= 1e4:
        m, e = f"{x:.1e}".split("e")
        return f"{m}×10$^{{{int(e)}}}$"
    return f"{x:,.0f}" if x >= 100 else f"{x:.1f}"


def excluded_text(rows, key):
    groups = {}
    for r in rows:
        why = r[key]
        if why:
            groups.setdefault(why, []).append(r["system"])
    short = {"no admissible subset (not validated)": "no admissible subset",
             "selected parameters act only in the test conditions": "selected parameters act only in test conditions",
             "single condition and single time point: no training/test split": "no training/test split possible",
             "full model not re-estimated (155/277 parameters, computation pending)": "full model not re-estimated",
             "noise-free benchmark data (test chi2/n of theta0 < 0.01)": "noise-free data ($\\theta_0$ test $\\chi^2/n<0.01$)"}
    return "Not shown: " + "; ".join(f"{', '.join(v)} ({short.get(k, k)})" for k, v in groups.items()) + "."


def ratio_panel(ax, rows, ref, letter, title, plotted):
    P = [r for r in rows if r["reason_a" if ref == "full" else "reason_b"] == ""]
    for r in P:
        r["_q"] = r["reduced"] / r[ref]
    P.sort(key=lambda r: math.log10(r["_q"]))
    n = len(P); y = np.arange(n)[::-1]
    lq = np.array([math.log10(r["_q"]) for r in P])
    xmin, xmax = -3.2, 1.75
    ax.axvspan(xmin, LO, color="#e6f2f4", lw=0, zorder=0)
    ax.axvspan(HI, xmax, color="#fdeee4", lw=0, zorder=0)
    ax.axvspan(LO, HI, color="#d9d9d9", lw=0, zorder=0)
    ax.axvline(0, color=INK, lw=0.9, zorder=1)
    for yi, r, x in zip(y, P, lq):
        cl = classify(r["_q"])
        ax.plot([0, x], [yi, yi], color=COL[cl], lw=0.8, alpha=0.45, zorder=2)
        ax.scatter(x, yi, s=26, marker=MK[cl], color=COL[cl], edgecolor="white", linewidth=0.5, zorder=4)
        lab = fmt_ratio(r["_q"])
        flag = r["reduced"] > HIGH
        txt = lab + (f"   ◆ $\\chi^2/n$ = {fmt_chi(r['reduced'])}" if flag else "")
        if x >= 0:
            ax.text(x + 0.07, yi, txt, va="center", ha="left", fontsize=6.0, color=INK if not flag else "#7a2e00")
        else:
            ax.text(x - 0.07, yi, lab, va="center", ha="right", fontsize=6.0, color=INK)
            if flag:
                ax.text(0.07, yi, f"◆ $\\chi^2/n$ = {fmt_chi(r['reduced'])}", va="center", ha="left", fontsize=6.0, color="#7a2e00")
        plotted.append((letter, r["system"], r["reduced"], r[ref], float(x)))
    ax.set_yticks(y); ax.set_yticklabels([r["system"] for r in P], fontsize=6.9)
    ax.set_ylim(-0.7, n - 0.3); ax.set_xlim(xmin, xmax)
    ticks = [-3, -2, -1, 0, 1]
    ax.set_xticks(ticks); ax.set_xticklabels(["×0.001", "×0.01", "×0.1", "×1", "×10"], fontsize=6.6)
    ax.grid(axis="x", color=GRID, lw=0.5, zorder=0); ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(length=2.5, color=MUTED)
    ax.text(-0.205, 1.075, letter, transform=ax.transAxes, fontsize=10.5, fontweight="bold", va="bottom")
    ax.text(-0.16, 1.075, title, transform=ax.transAxes, fontsize=8.2, fontweight="bold", va="bottom")
    xr = (0 - xmin) / (xmax - xmin)
    ax.text(xr - 0.012, 1.012, "\u2190 reduced model predicts better", transform=ax.transAxes, fontsize=6.2,
            color=C_BETTER, va="bottom", ha="right", fontweight="bold")
    ax.text(xr + 0.012, 1.012, "predicts worse \u2192", transform=ax.transAxes, fontsize=6.2, color=C_WORSE,
            va="bottom", ha="left", fontweight="bold")
    return P


def fig_ratio(rows):
    plotted = []
    na = sum(r["reason_a"] == "" for r in rows); nb = sum(r["reason_b"] == "" for r in rows)
    import textwrap
    fig = plt.figure(figsize=(7.0, 9.8))
    top, bot, gap = 0.945, 0.15, 0.13
    h_all = top - bot - gap
    ha, hb = h_all * na / (na + nb), h_all * nb / (na + nb)
    axa = fig.add_axes([0.2, top - ha, 0.77, ha])
    axb = fig.add_axes([0.2, bot, 0.77, hb])
    ratio_panel(axa, rows, "full", "a", "Reduced model vs full model re-estimated on training data", plotted)
    ratio_panel(axb, rows, "theta0", "b", "Reduced model vs published estimate $\\theta_0$", plotted)
    axa.set_xlabel("Test $\\chi^2/n$ ratio, reduced / full (log scale)", fontsize=7.2, labelpad=3)
    axb.set_xlabel("Test $\\chi^2/n$ ratio, reduced / $\\theta_0$ (log scale)", fontsize=7.2, labelpad=3)
    for ax, key in ((axa, "reason_a"), (axb, "reason_b")):
        y0 = ax.get_position().y0
        fig.text(0.2, y0 - 0.042, "\n".join(textwrap.wrap(excluded_text(rows, key), 128)), fontsize=5.9,
                 color=MUTED, va="top", ha="left", linespacing=1.3)
    h = [Line2D([], [], marker="o", ls="", color=C_BETTER, ms=5, label="better (ratio < 0.95)"),
         Line2D([], [], marker="s", ls="", color=C_EQ, ms=4.6, label="equivalent within 5%"),
         Line2D([], [], marker="^", ls="", color=C_WORSE, ms=5, label="worse (ratio > 1.05)"),
         Patch(fc="#d9d9d9", ec="none", label="±5% equivalence band"),
         Line2D([], [], marker="$◆$", ls="", color="#7a2e00", ms=5, label="reduced $\\chi^2/n$ > 10: poor absolute fit")]
    fig.legend(handles=h, loc="lower center", ncol=3, fontsize=6.4, frameon=False, bbox_to_anchor=(0.55, 0.0),
               columnspacing=1.4, handletextpad=0.4)
    fig.text(0.55, 0.06, "$\\chi^2/n\\approx1$ indicates residuals comparable to the reported measurement noise.",
             ha="center", fontsize=6.4, color=MUTED, style="italic")
    for ext in ("pdf", "png"):
        fig.savefig(HERE / f"figure3_ratio.{ext}", dpi=600)
    plt.close(fig)
    return plotted


def fig_scatter(rows):
    plotted = []
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 3.75))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.88, bottom=0.25, wspace=0.28)
    vals = [r[k] for r in rows for k in ("reduced", "full", "theta0") if r[k] is not None and r["reason_b"] == ""]
    lo, hi = 10 ** math.floor(math.log10(min(vals)) - 0.3), 10 ** math.ceil(math.log10(max(vals)) + 0.3)
    xx = np.logspace(math.log10(lo), math.log10(hi), 200)
    for ax, ref, key, letter, title, xl in ((axs[0], "full", "reason_a", "a", "Reduced vs full model (training refit)", "Test $\\chi^2/n$, full model"),
                                            (axs[1], "theta0", "reason_b", "b", "Reduced vs published $\\theta_0$", "Test $\\chi^2/n$, published $\\theta_0$")):
        ax.fill_between(xx, lo, xx, color="#e6f2f4", lw=0, zorder=0)
        ax.fill_between(xx, xx * (1 - EQ), xx * (1 + EQ), color="#cfcfcf", lw=0, zorder=1)
        ax.plot(xx, xx, color=INK, lw=0.8, zorder=2)
        P = [r for r in rows if r[key] == ""]
        for r in P:
            q = r["reduced"] / r[ref]; cl = classify(q)
            if cl == "worse":
                ax.scatter(r[ref], r["reduced"], s=26, marker="^", facecolor="white", edgecolor=C_WORSE, lw=1.0, zorder=4)
            else:
                ax.scatter(r[ref], r["reduced"], s=24, marker=MK[cl], color=COL[cl], edgecolor="white", lw=0.4, zorder=4)
            plotted.append((letter, r["system"], r["reduced"], r[ref], math.log10(q)))
        ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(lo, hi); ax.set_ylim(lo, hi); ax.set_aspect("equal")
        ax._lab = [r for r in P if abs(math.log10(r["reduced"] / r[ref])) > 0.3]
        ax._ref = ref
        ax.text(0.97, 0.05, "reduced model\npredicts better", transform=ax.transAxes, ha="right", va="bottom", fontsize=6.1, color=C_BETTER)
        ax.set_xlabel(xl, fontsize=7.2); ax.set_ylabel("Test $\\chi^2/n$, reduced model", fontsize=7.2)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.tick_params(labelsize=6.4, length=2.5, color=MUTED)
        ax.text(-0.2, 1.06, letter, transform=ax.transAxes, fontsize=10.5, fontweight="bold", va="bottom")
        ax.text(-0.11, 1.06, title + f"  (n = {len(P)})", transform=ax.transAxes, fontsize=7.6, fontweight="bold", va="bottom")
    place_labels(fig, axs)
    h = [Line2D([], [], marker="o", ls="", color=C_BETTER, ms=5, label="better"),
         Line2D([], [], marker="s", ls="", color=C_EQ, ms=4.6, label="equivalent (±5%)"),
         Line2D([], [], marker="^", ls="", mfc="white", mec=C_WORSE, ms=5, label="worse"),
         Line2D([], [], color=INK, lw=0.8, label="$y=x$"),
         Patch(fc="#cfcfcf", ec="none", label="±5% band")]
    fig.legend(handles=h, loc="lower center", ncol=5, fontsize=6.4, frameon=False, bbox_to_anchor=(0.53, 0.0), columnspacing=1.3)
    fig.text(0.53, 0.075, "$\\chi^2/n\\approx1$ indicates residuals comparable to the reported measurement noise.",
             ha="center", fontsize=6.3, color=MUTED, style="italic")
    for ext in ("pdf", "png"):
        fig.savefig(HERE / f"figure3_scatter.{ext}", dpi=600)
    plt.close(fig)
    return plotted


def place_labels(fig, axs, pad=1.5):
    """Labels next to the points away from the diagonal, then pushed apart (display units) until no two overlap."""
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    for ax in axs:
        T = []
        for r in ax._lab:
            x, y = r[ax._ref], r["reduced"]
            below = y < x
            t = ax.text(x, y, r["system"], fontsize=5.7, color=MUTED, ha="left" if below else "right", va="center", zorder=5)
            px, py = ax.transData.transform((x, y))
            T.append([t, px, py, px + (6 if below else -4), py + (0 if below else 22), below])
        for _ in range(400):
            moved = False
            boxes = []
            for t, px, py, tx, ty, below in T:
                t.set_position(ax.transData.inverted().transform((tx, ty)))
                boxes.append(t.get_window_extent(rend).expanded(1.0, 1.0))
            for a_ in range(len(T)):
                for b_ in range(a_ + 1, len(T)):
                    A, B = boxes[a_], boxes[b_]
                    if A.x1 + pad > B.x0 and B.x1 + pad > A.x0 and A.y1 + pad > B.y0 and B.y1 + pad > A.y0:
                        d = 1.2 if T[a_][4] >= T[b_][4] else -1.2
                        T[a_][4] += d; T[b_][4] -= d; moved = True
            if not moved:
                break
        for t, px, py, tx, ty, below in T:
            t.set_position(ax.transData.inverted().transform((tx, ty)))
            if abs(ty - py) > 3:
                ax.plot(*zip(ax.transData.inverted().transform((px, py)),
                             ax.transData.inverted().transform((tx - (2 if below else -2), ty))),
                        color="#b5b5b5", lw=0.4, zorder=3)


def verify(plotted, tag):
    """Every plotted point must equal the consolidated CSV (reduced and reference chi2, panel membership)."""
    tab = {r["system"]: r for r in read_csv()}
    for letter, sysname, red, ref, x in plotted:
        r = tab[sysname]
        col = "full_chi2" if letter == "a" else "theta0_chi2"
        inc = "include_panel_a" if letter == "a" else "include_panel_b"
        assert r[inc] == "1", (tag, sysname, letter)
        assert float(r["reduced_chi2"]) == red and float(r[col]) == ref, (tag, sysname)
        assert abs(x - math.log10(float(r["reduced_chi2"]) / float(r[col]))) < 1e-12, (tag, sysname)
    for letter, inc in (("a", "include_panel_a"), ("b", "include_panel_b")):
        shown = sorted(s for l_, s, *_ in plotted if l_ == letter)
        assert shown == sorted(s for s, r in tab.items() if r[inc] == "1"), (tag, letter)
    return {l_: sum(1 for p in plotted if p[0] == l_) for l_ in ("a", "b")}


# ---------------------------------------------------------------- 4. texts
def cap_tex(rows, C, nf):
    a, b = C["panel_a"], C["panel_b"]
    return (r"\caption{\textbf{Prediction of held-out experiments with real data.} Ratio of the test $\chi^2/n$ (mean squared "
            r"noise-scaled residual on the held-out experiments) of the reduced model to that of a reference, on a logarithmic scale. "
            rf"\textbf{{a}}, Reference: the full model re-estimated on the same training data ($n={a['n']}$ problems). "
            rf"\textbf{{b}}, Reference: the published estimate $\theta_0$, obtained using all data including the test experiments ($n={b['n']}$). "
            r"Left of the vertical line (circles) the reduced model predicts better; the grey band marks equivalence within 5\% (squares); "
            r"triangles mark worse predictions. Labels give the ratio; $\blacklozenge$ flags a reduced test $\chi^2/n$ above 10, where a "
            r"favourable ratio does not imply a good absolute fit. Problems without a training/test split (Bertozzi, Blasi), without a full "
            rf"re-estimation (Chen, Lang; \textbf{{a}} only) or with noise-free data (test $\chi^2/n$ of $\theta_0$ below 0.01: {nf}) are not shown.}}")


def write_texts(rows, C):
    nf = ", ".join(sorted(r["system"] for r in rows if r["theta0"] is not None and r["theta0"] < NOISE_FREE))
    (HERE / "figure3_caption.tex").write_text(cap_tex(rows, C, nf) + "\n")


# ---------------------------------------------------------------- main
def check_files():
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    out = {}
    for f in ["figure3_ratio.png", "figure3_scatter.png"]:
        with Image.open(HERE / f) as im:
            dpi = im.info.get("dpi", (0, 0))
            out[f] = f"{im.size[0]}x{im.size[1]} px, {round(dpi[0])} dpi"
            assert round(dpi[0]) >= 600
    return out


def main():
    rows = build_rows()
    write_csv(rows)
    C = counts(rows)
    report(rows, C)
    if not all(r["theta0"] is not None for r in rows if r["reduced"] is not None):
        sys.exit("theta0 chi2 missing for some validated problem: A_chi2_test_theta0 in external_validation/*.json")
    pr = fig_ratio(rows); ps = fig_scatter(rows)
    na_r = verify(pr, "ratio"); na_s = verify(ps, "scatter")
    write_texts(rows, C)
    shutil.copy(HERE / "figure3_ratio.pdf", FIG / "fig3_validation.pdf")
    shutil.copy(HERE / "figure3_scatter.pdf", FIG / "figS1_validation_scatter.pdf")
    print("panel a:", na_r["a"], "problems (ratio) /", na_s["a"], "(scatter);  panel b:", na_r["b"], "/", na_s["b"])
    print("all plotted points match figure3_heldout_data.csv")
    for k, v in check_files().items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
