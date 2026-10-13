#!/usr/bin/env python3
"""Preview: Table 2 (sensitivity of the selection to the method settings) drawn as a figure.
Not included in the manuscript. Single-panel version. Output: alternativas/fig_table2_settings_single.{pdf,png}"""
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

fig, ax = plt.subplots(figsize=(4.7, 3.9))
fig.subplots_adjust(left=0.36, right=0.97, top=0.93, bottom=0.11)
y, ticks, labs, heads = 0, [], [], []
for gname, g in GROUPS:
    y0 = y
    heads.append((y, gname)); y += 1
    for t, lab in g:
        v = T[t]
        ax.plot([v["same"], N], [y, y], color="#d0d0d0", lw=0.8, zorder=1)
        ax.scatter(v["same"], y, s=20, color=BLUE, zorder=4)
        ax.scatter(v["adm"], y, s=55, marker="s", fc="none", ec=GREEN, lw=1.0, zorder=5)
        txt = f"{v['same']}/{N}"
        if abs(v["mean"] - B["mean"]) > 0.005:
            txt += f"   |S| {v['mean']:.2f}"
        ax.text(N + 0.7, y, txt, va="center", fontsize=6, color=GREY)
        ticks.append(y); labs.append(lab); y += 1
    if gname.startswith("Admissibility"):
        ax.axhspan(y0 - 0.5, y - 0.5, xmin=-0.55, xmax=1.13, color="#fdf0ea", zorder=0, clip_on=False)
    y += 0.3
for yy, gname in heads:
    ax.text(-0.03, yy, gname, transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=7, fontweight="bold",
            color=ORANGE if gname.startswith("Admissibility") else "black")
ax.set_yticks(ticks, labs); ax.tick_params(axis="y", length=0)
ax.set_ylim(y - 0.5, -0.8)
ax.axvline(N, color=GREY, lw=0.6, ls=(0, (3, 2)))
ax.set_xlim(10, N + 6.5); ax.set_xticks([10, 15, 20, 25])
ax.spines["bottom"].set_bounds(10, N)
ax.set_xlabel(f"Number of problems (of {N})")
ax.scatter([], [], s=20, color=BLUE, label="same subset $S$ as baseline")
ax.scatter([], [], s=55, marker="s", fc="none", ec=GREEN, lw=1.0, label=f"admissible (baseline {B['adm']})")
ax.legend(loc="lower center", frameon=False, fontsize=6.3, ncol=2, bbox_to_anchor=(0.5, 1.0), handletextpad=0.2, columnspacing=1.2)
fig.savefig(HERE / "fig_table2_settings_single.pdf")
fig.savefig(HERE / "fig_table2_settings_single.png", dpi=300)
