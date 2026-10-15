"""
Supplementary Figure (Pivoted QR selection): test chi2/n of pivoted-QR subsets against those of our
method on real data, one point per problem.

Source: results/qr_selection/<problem>.json (keys chi2_ours, chi2_qr), written by
analysis/qr_selection.py. Output: figures/fig_brun.pdf (file name kept for the LaTeX source).
"""
import json
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import RESULTS, FIG

INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
BLUE, ORANGE, GREY = "#2a78d6", "#eb6834", "#8a8984"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7, "axes.titlesize": 8,
                     "axes.labelsize": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False,
                     "axes.spines.right": False})
FLOOR = 1e-12          # values below: data reproduced far below the noise level; not drawn
# label offsets (points) for the cluster of problems near chi2/n = 1
OFFSET = {"Boehm": (14, -20), "Brannmark": (16, -10), "Lucarelli": (-14, 14), "Sneyd": (-6, 24),
          "Laske": (-16, 2), "Oliveira": (-6, 6), "Giordano": (6, 4)}

pts, omit = [], []
for f in sorted((RESULTS / "qr_selection").glob("*.json")):
    d = json.loads(f.read_text())
    o, q = d.get("chi2_ours"), d.get("chi2_qr")
    if not (isinstance(o, (int, float)) and isinstance(q, (int, float))):
        continue
    name = d["sistema"].split("_")[0].replace("SalazarCavazos", "Salazar-Cavazos")
    if o < FLOOR or q < FLOOR:
        omit.append(name); continue
    pts.append((name, o, q))

fig, ax = plt.subplots(figsize=(3.6, 3.5))
lo = 10 ** math.floor(math.log10(min(min(o, q) for _, o, q in pts)) - 0.3)
hi = 10 ** math.ceil(math.log10(max(max(o, q) for _, o, q in pts)) + 0.3)
xs = [lo, hi]
ax.fill_between(xs, [x / 1.05 for x in xs], [x * 1.05 for x in xs], color=GRID, lw=0, zorder=1)
ax.plot(xs, xs, color=INK2, lw=0.8, zorder=2)
for name, o, q in pts:
    r = q / o
    c = BLUE if r > 1.5 else (ORANGE if r < 1 / 1.5 else GREY)
    ax.scatter(o, q, s=22, color=c, edgecolor="white", linewidth=0.8, zorder=3)
    if r > 1.5 or r < 1 / 1.5:
        dx, dy = OFFSET.get(name, (5, -3))
        ax.annotate(name, (o, q), xytext=(dx, dy), textcoords="offset points", fontsize=6,
                    color=INK2, ha="left" if dx >= 0 else "right",
                    arrowprops=dict(arrowstyle="-", color=GRID, lw=0.5) if abs(dy) > 6 else None)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
ax.set_xlabel(r"Test $\chi^2/n$, our method")
ax.set_ylabel(r"Test $\chi^2/n$, pivoted QR")
ax.set_title("Pivoted QR versus our method", loc="left", color=INK)
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
ax.legend(handles=[Line2D([], [], marker="o", ls="", color=BLUE, label="Ours more than 1.5$\\times$ better"),
                   Line2D([], [], marker="o", ls="", color=GREY, label="Within a factor of 1.5"),
                   Line2D([], [], marker="o", ls="", color=ORANGE, label="QR more than 1.5$\\times$ better"),
                   Patch(color=GRID, label="Within 5%")],
          loc="upper left", frameon=False, fontsize=6, handletextpad=0.3)
ax.grid(True, which="major", color=GRID, lw=0.4, zorder=0)
fig.tight_layout()
fig.savefig(FIG / "fig_brun.pdf")
print(f"fig_brun.pdf: {len(pts)} problems drawn; omitted (chi2/n < {FLOOR:g}): {', '.join(omit) or 'none'}")
