#!/usr/bin/env python3
"""Preview: Table 2 (sensitivity of the selection to the method settings) drawn as a figure.
Not included in the manuscript. Output: alternativas/fig_table2_settings_preview.{pdf,png}"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
RES = HERE.parent.parent.parent / "certificados" / "resultados"
plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans"], "font.size": 7,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.6,
                     "xtick.major.width": 0.6, "ytick.major.width": 0.6, "pdf.fonttype": 42})
BLUE, ORANGE, GREEN, GREY = "#2a78d6", "#eb6834", "#1baf7a", "#3d3d3d"


def ldir(d):
    return {f.stem: json.loads(f.read_text()) for f in sorted((RES / d).glob("*.json"))}


BASE = ldir("reclasificacion_salidas_bio_poda")
GROUPS = [("Finite-difference step", [("delta0001", r"$\delta=0.1\%$"), ("delta005", r"$\delta=5\%$")]),
          ("ODE tolerances", [("tolfina", r"$10^{-9}/10^{-12}$"), ("tolgruesa", r"$10^{-6}/10^{-8}$")]),
          ("Perturbation level", [("nivel001", r"$\pm1\%$"), ("nivel010", r"$\pm10\%$")]),
          (r"Variance threshold $\tau_R$", [("rvar080", "0.80"), ("rvar085", "0.85"), ("rvar095", "0.95")]),
          (r"Collinearity $\tau_\kappa=\tau_{\mathrm{VIF}}$", [("kv5", "5"), ("kv30", "30")]),
          (r"Admissibility $\tau_e$", [("emax010", "0.10"), ("emax020", "0.20"), ("emax030", "0.30"), ("emax050", "0.50")])]


def stats(t):
    V = ldir(f"reclasificacion_salidas_bio_poda_{t}")
    probs = sorted(V)
    adm = [p for p in probs if V[p]["admisible"]]
    return dict(n=len(probs), adm=len(adm), mean=float(np.mean([len(V[p]["S"]) for p in adm])),
                same=sum(1 for p in probs if sorted(V[p]["S"]) == sorted(BASE[p]["S"])))


T = {t: stats(t) for _, g in GROUPS for t, _ in g}
probs = sorted(ldir("reclasificacion_salidas_bio_poda_kv5"))
N = len(probs)
badm = [p for p in probs if BASE[p]["admisible"]]
B = dict(adm=len(badm), mean=float(np.mean([len(BASE[p]["S"]) for p in badm])), same=N)
for t, v in T.items():
    print(f"{t:10s} adm {v['adm']} mean {v['mean']:.2f} same {v['same']}/{v['n']}")
print("baseline", B)

fig = plt.figure(figsize=(7.0, 3.6))
gs = fig.add_gridspec(2, 2, width_ratios=[1.55, 1], hspace=0.55, wspace=0.55, left=0.24, right=0.98, top=0.83, bottom=0.12)
ax = fig.add_subplot(gs[:, 0])
y, ticks, labs, heads = 0, [], [], []
for gname, g in GROUPS:
    heads.append((y, gname)); y += 1
    for t, lab in g:
        v = T[t]
        ax.plot([v["same"], N], [y, y], color="#d0d0d0", lw=0.8, zorder=1)
        ax.scatter(v["adm"], y, s=22, marker="s", fc="white", ec=GREEN, lw=1.0, zorder=3)
        ax.scatter(v["same"], y, s=24, color=BLUE, zorder=4)
        ax.text(N + 0.6, y, f"{v['same']}/{N}  |S|={v['mean']:.2f}", va="center", fontsize=6, color=GREY)
        ticks.append(y); labs.append(lab); y += 1
    y += 0.3
for yy, gname in heads:
    ax.text(-0.02, yy, gname, transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=7, fontweight="bold")
ax.set_yticks(ticks, labs); ax.tick_params(axis="y", length=0)
ax.set_ylim(y - 0.5, -0.8)
ax.axvline(N, color=GREY, lw=0.6, ls=(0, (3, 2)))
ax.axvline(B["adm"], color=GREEN, lw=0.6, ls=(0, (1, 1.5)))
ax.set_xlim(10, N + 7.5); ax.set_xticks([10, 15, 20, N])
ax.set_xlabel(f"Number of problems (of {N})")
ax.scatter([], [], s=24, color=BLUE, label="same subset $S$ as baseline")
ax.scatter([], [], s=22, marker="s", fc="white", ec=GREEN, lw=1.0, label=f"admissible (baseline {B['adm']})")
ax.legend(loc="lower left", frameon=False, fontsize=6.3, ncol=2, bbox_to_anchor=(-0.02, 0.985), handletextpad=0.2, columnspacing=1.2)
fig.text(0.01, 0.95, "a", fontsize=9, fontweight="bold")
fig.text(0.035, 0.95, "One setting changed at a time", fontsize=8, fontweight="bold")

te = [0.10, 0.20, 0.30, 0.436, 0.50]
keys = ["emax010", "emax020", "emax030", None, "emax050"]
get = lambda k, f: B[f] if k is None else T[k][f]
for i, (f, lab, col) in enumerate([("adm", "Admissible problems", GREEN), ("mean", r"Mean $|S|$", ORANGE)]):
    a = fig.add_subplot(gs[i, 1])
    vals = [get(k, f) for k in keys]
    a.plot(te, vals, color=col, lw=1.2, marker="o", ms=3.5, zorder=3)
    a.scatter([0.436], [get(None, f)], s=46, fc="white", ec=GREY, lw=1.0, zorder=4)
    for x, v in zip(te, vals):
        a.annotate(f"{v:.0f}" if f == "adm" else f"{v:.2f}", (x, v), xytext=(0, 5) if f == "adm" else ((0, -10) if x == 0.5 else (6, 4)),
                   textcoords="offset points", ha="center" if f == "adm" or x == 0.5 else "left", fontsize=6, color=GREY)
    a.axvline(0.436, color=GREY, lw=0.6, ls=(0, (3, 2)))
    a.set_xlim(0.06, 0.54); a.set_xticks([0.1, 0.2, 0.3, 0.4, 0.5], ["0.10", "0.20", "0.30", "0.40", "0.50"])
    a.set_ylabel(lab)
    if f == "adm":
        a.set_ylim(20.5, 26.5); a.set_yticks([21, 23, 25])
        fig.text(0.6, 0.95, "b", fontsize=9, fontweight="bold")
        fig.text(0.625, 0.95, r"Effect of the admissibility threshold $\tau_e$", fontsize=8, fontweight="bold")
        a.text(0.43, 21.0, "baseline\n0.436", fontsize=6, color=GREY, ha="right")
    else:
        a.set_ylim(1.65, 4.0); a.set_xlabel(r"$\tau_e$")
fig.savefig(HERE / "fig_table2_settings_preview.pdf")
fig.savefig(HERE / "fig_table2_settings_preview.png", dpi=300)
