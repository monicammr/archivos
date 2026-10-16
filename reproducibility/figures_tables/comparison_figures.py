#!/usr/bin/env python3
"""
Main-text figures of the comparison with other criteria, from the stored results:
  figures/fig3_validation_v2.pdf  Fig. 3: a) reduced versus full model on real data (theta0 anchor);
                                  b) synthetic data, 20 seeds: fraction of seeds in which the reduced
                                     model predicts at least as well as the full model, per problem.
  figures/fig4_comparison.pdf     Fig. 4: comparison with pivoted QR, Brun, Morris and profile
                                  likelihood: a) admissibility at +-5 % and +-20 %; b) synthetic success
                                  with 95 % CI from resampling problems; c) real data, chi2 ratio to our
                                  method; d) run time versus profile likelihood.
Usage: python comparison_figures.py
"""
import sys, json, glob, math, collections
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
from common import RESULTS as R, FIG, TAB, OUT as _OUT, EXCLUDE_ADMISSIBILITY

TAU = math.sqrt(1 - 0.81)
# paleta categórica validada (orden fijo; un color por criterio en todas las figuras)
COL = {"ours": "#2a78d6", "brun": "#eb6834", "morris": "#1baf7a", "perfil": "#eda100", "qr": "#e87ba4"}
NOM = {"ours": "Our method", "brun": "Brun", "morris": "Morris", "perfil": "Profile likelihood",
       "qr": "Pivoted QR"}
M = ["ours", "brun", "morris", "perfil", "qr"]
INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"],
                     "font.size": 7, "axes.titlesize": 8, "axes.labelsize": 7, "axes.edgecolor": INK2,
                     "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42})
ok = lambda x: isinstance(x, (int, float)) and math.isfinite(x)


def L(sub):
    return {Path(f).stem: json.loads(Path(f).read_text(encoding="utf-8")) for f in glob.glob(str(R / sub / "*.json"))}


def corto(s):
    return s.split("_")[0].replace("SalazarCavazos", "Salazar-Cavazos")


def letra(ax, c):
    ax.text(-0.16, 1.04, c, transform=ax.transAxes, fontsize=9, fontweight="bold", color=INK, va="bottom")


# ── Figura 3 ──────────────────────────────────────────────────────────────────────
from common import load_validation
ext = load_validation()
filas = []
for s, d in ext.items():
    r, f, t0 = d.get("A_chi2_test_red"), d.get("A_chi2_test_full"), d.get("A_chi2_test_theta0")
    if ok(r) and ok(f) and f > 0 and ok(t0) and t0 >= 0.01:
        filas.append((corto(s), r / f, r > 10))
filas.sort(key=lambda x: x[1])
S = collections.defaultdict(dict)
for f in glob.glob(str(R / "synthetic_seeds" / "*" / "s*.json")):
    d = json.loads(Path(f).read_text(encoding="utf-8"))
    if ok(d.get("B_epred_red")) and ok(d.get("B_epred_full")) and ok(d.get("B_chi2_test_theta0")) \
            and d["B_chi2_test_theta0"] >= 2:
        S[d["sistema"]][d["semilla"]] = d["B_epred_red"] <= d["B_epred_full"]
sint = sorted(((corto(s), np.mean(list(v.values())), len(v), sum(v.values())) for s, v in S.items() if len(v) >= 3),
              key=lambda x: x[1])

# c) leakage through theta0: theta0 alone and the nested reduced model, relative to the reduced model
#    (same 5 % criterion as Supplementary Table tab:wilcoxonreal)
nest = {Path(f).stem: json.loads(Path(f).read_text(encoding="utf-8"))
        for f in glob.glob(str(R / "nested_validation" / "*.json"))}
rc = [("$\\theta_0$ alone / reduced", "chi2_test_theta0"), ("Nested reduced / reduced", "chi2_test_red_nested")]
lc = {k: [d[k] / d["chi2_test_red_original"] for d in nest.values()
          if ok(d.get(k)) and ok(d.get("chi2_test_red_original")) and d[k] > 0 and d["chi2_test_red_original"] > 0]
      for _, k in rc}

fig = plt.figure(figsize=(7.2, 6.0))
gs = fig.add_gridspec(2, 2, height_ratios=[4.6, 1.15], wspace=0.55, hspace=0.62)
a1, a2, a3 = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, :])
y = np.arange(len(filas))
for i, (n, q, alto) in enumerate(filas):
    c = COL["ours"] if q < 0.95 else ("#8a8984" if q <= 1.05 else "#e34948")
    mk = "o" if q < 0.95 else ("s" if q <= 1.05 else "^")
    a1.plot([1, q], [i, i], color=GRID, lw=1, zorder=1)
    a1.scatter(q, i, s=22, marker=mk, color=c, edgecolor="white", linewidth=0.8, zorder=3)
    if alto:
        a1.text(q * 1.25, i, "◆", fontsize=5, color=INK2, va="center", fontfamily="DejaVu Sans")
a1.axvspan(0.95, 1.05, color="#efeeea", zorder=0)
a1.axvline(1, color=INK2, lw=0.8)
a1.set_xscale("log"); a1.set_yticks(y); a1.set_yticklabels([n for n, _, _ in filas])
a1.set_xlabel("Test $\\chi^2/n$, reduced / full model")
a1.set_title("Real data (fixed parameters at $\\theta_0$)", loc="left", color=INK, pad=12)
a1.text(0.02, 1.0, "← reduced better", transform=a1.transAxes, color=INK2, fontsize=6, va="bottom")
letra(a1, "a")
y2 = np.arange(len(sint))
for i, (n, fr, k, w) in enumerate(sint):
    a2.barh(i, max(fr, 0.004), color=COL["ours"], height=0.62)
    a2.text(1.03, i, f"{w}/{k}", va="center", fontsize=6, color=INK2)
a2.axvline(0.5, color=INK2, lw=0.8, ls="--")
a2.set_yticks(y2); a2.set_yticklabels([n for n, *_ in sint]); a2.set_xlim(0, 1)
a2.set_xlabel("Fraction of seeds with reduced $e_{\\mathrm{pred}}\\leq$ full $e_{\\mathrm{pred}}$")
a2.set_title("Synthetic data, 20 seeds (truth unknown to $\\theta_0$)", loc="left", color=INK, pad=12)
a2.text(1.03, len(sint) - 0.2, "won/seeds", fontsize=6, color=INK2)
letra(a2, "b")
e5 = 1.05
for i, (lab, k) in enumerate(rc):
    v = np.array(lc[k]); yy = len(rc) - 1 - i
    jit = (np.arange(len(v)) % 3 - 1) * 0.12
    cc = np.where(v < 1 / e5, COL["ours"], np.where(v > e5, "#e34948", "#8a8984"))
    a3.scatter(np.clip(v, 0.1, 1e3), yy + jit, s=14, color=cc, edgecolor="white", linewidth=0.5, zorder=3)
    md = float(np.median(v))
    a3.plot([md, md], [yy - 0.32, yy + 0.32], color=INK, lw=1.4, zorder=4)
    a3.text(1.2e3, yy, f"lower in {int((v < 1 / e5).sum())}, higher in {int((v > e5).sum())} of {len(v)}; median {md:.2f}",
            va="center", fontsize=6, color=INK2)
a3.axvspan(1 / e5, e5, color="#efeeea", zorder=0)
a3.axvline(1, color=INK2, lw=0.8)
a3.set_xscale("log"); a3.set_xlim(0.1, 1e3); a3.set_ylim(-0.6, len(rc) - 0.4)
a3.set_yticks(range(len(rc))); a3.set_yticklabels([lab for lab, _ in rc][::-1])
a3.set_xlabel("Test $\\chi^2/n$ relative to the reduced model anchored at $\\theta_0$ (values beyond the axis at its edge)")
a3.set_title("Real data: information inherited from $\\theta_0$", loc="left", color=INK, pad=6)
letra(a3, "c")
fig.savefig(FIG / "fig3_validation_v2.pdf", bbox_inches="tight")
fig.savefig(FIG / "fig3_validation_v2.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# ── Figura 4 ──────────────────────────────────────────────────────────────────────
# Second audit: fixed scenario set, our method also selected on the training outputs, standard
# (Golub-Klema-Stewart) pivoted QR, null controls, three families of synthetic truths; the numbers
# come from audit2_stats.py (results/audit2_stats.json).
ST = json.loads((R / "audit2_stats.json").read_text(encoding="utf-8"))
COL.update({"train": "#7aa7e6", "qr_gks": "#e87ba4", "random": "#9a9893", "empty": "#c9c7c1"})
NOM.update({"ours": "Our method", "train": "Our method (training outputs)", "qr_gks": "Pivoted QR (GKS)",
            "random": "Random (median of 20)", "empty": "Calibration only"})
MA = ["ours", "train", "brun", "morris", "perfil", "qr_gks", "random", "empty"]
MS = ["ours", "train", "brun", "morris", "perfil", "qr_gks"]

# datos reales: cocientes con el nuestro
an = L("nested_validation"); mb = L("brun_morris")
pf = L("profile_likelihood"); al = L("random_subsets"); va = L("calibration_only"); gk = L("qr_selection_gks")
tr = {}
for f in glob.glob(str(R / "criteria_tests_fixedscen" / "*__train__real.json")):
    d = json.loads(Path(f).read_text(encoding="utf-8")); tr[d["sistema"]] = d.get("chi2_test")
ours = {s: d.get("chi2_test_red_original") for s, d in an.items()}
otros = [("train", "Our method (training outputs)", tr),
         ("brun", "Brun", {s: d.get("chi2_brun") for s, d in mb.items()}),
         ("morris", "Morris", {s: d.get("chi2_morris") for s, d in mb.items()}),
         ("perfil", "Profile likelihood", {s: d.get("chi2_perfil") for s, d in pf.items()}),
         ("qr_gks", "Pivoted QR (GKS)", {s: d.get("chi2_qr") for s, d in gk.items()}),
         ("rand", "Random (median of 20)", {s: d.get("chi2_rand_median") for s, d in al.items()}),
         ("vac", "Calibration only", {s: d.get("chi2_vacio") for s, d in va.items()})]
rng = np.random.default_rng(0)

# tiempos
tp = L("timing_complete/parallel"); tp.update(L("timing_complete/parallel_corrected_code"))
tpf, nopf = {}, []
for line in [l for n in ("round0.log", "large_problems.log") if (R / "profile_likelihood" / "logs" / n).exists() for l in (R / "profile_likelihood" / "logs" / n).read_text(encoding="utf-8", errors="ignore").splitlines()]:
    if '"terminado": true' in line:
        d = json.loads(line); tpf[d["sistema"]] = d["seg_total"]
for s, d in pf.items():
    if "no_evaluable" in d and "PL_PMAX" in d["no_evaluable"]:
        nopf.append(s)

fig, axs = plt.subplots(2, 2, figsize=(7.2, 6.6), gridspec_kw={"hspace": 0.62, "wspace": 0.75})
# a) admisibilidad, con controles nulos
ax = axs[0, 0]
yy = np.arange(len(MA))[::-1]
for j, m in enumerate(MA):
    for off, lvl, alpha, hatch in ((0.19, "5", 1.0, None), (-0.19, "20", 0.55, "////")):
        r = ST["admissibility"][lvl][m]
        k = r.get("admissible", r.get("median_admissible")); n = r["n"]
        ax.barh(yy[j] + off, k / n, height=0.34, color=COL[m], alpha=alpha, hatch=hatch, edgecolor="white", lw=0.5)
        ax.text(k / n + 0.015, yy[j] + off, f"{k:.0f}/{n}", va="center", fontsize=5.5, color=INK)
ax.set_yticks(yy); ax.set_yticklabels([NOM[m] for m in MA]); ax.set_xlim(0, 1.2)
ax.set_xticks([0, 0.25, 0.5, 0.75, 1]); ax.set_xticklabels(["0", "25", "50", "75", "100"])
ax.set_xlabel("Problems with an admissible subset (%)")
ax.set_title("Reproduces the full model", loc="left", color=INK, pad=12)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color="#8a8984", label="±5% (level used by our method)"),
                   Patch(facecolor="#8a8984", alpha=0.55, hatch="////", edgecolor="white", label="±20% (used by none)")],
          loc="upper center", bbox_to_anchor=(0.3, -0.16), frameon=False, fontsize=6, ncol=2)
letra(ax, "a")
# b) sintético: tres familias de verdades (uniforme con IC 95 %)
ax = axs[0, 1]
ys = np.arange(len(MS))[::-1]
fams = [("uniforme", "o", "Uniform ±20%"), ("loguniforme", "s", "Log-uniform"), ("dispersa", "^", "Sparse")]
for j, m in enumerate(MS):
    for k, (fam, mk, lab) in enumerate(fams):
        ref = "ref_train" if m == "train" else "ref_ours"
        r = ST["synthetic"][fam][ref][m]
        yv = ys[j] + (0.22, 0, -0.22)[k]
        if fam == "uniforme":
            ax.plot(r["ci"], [yv] * 2, color=COL[m], lw=1.6, solid_capstyle="round")
        ax.scatter(r["rate"], yv, s=26 if k == 0 else 18, marker=mk, color=COL[m] if k == 0 else "white",
                   edgecolor=COL[m], linewidth=1, zorder=3)
ax.axvline(ST["synthetic"]["uniforme"]["ref_ours"]["ours"]["rate"], color=COL["ours"], lw=0.8, ls=":")
ax.set_yticks(ys); ax.set_yticklabels([NOM[m] for m in MS]); ax.set_xlim(0.1, 0.8)
ax.set_xticks([0.2, 0.4, 0.6, 0.8]); ax.set_xticklabels(["20", "40", "60", "80"])
ax.set_xlabel(r"Synthetic cases with $e_{\mathrm{pred}}\leq\tau_e$ (%)")
U = ST["synthetic"]["uniforme"]["ref_ours"]
ax.set_title(r"Predicts data unseen by $\theta_0$", loc="left", color=INK, pad=12)
from matplotlib.lines import Line2D
ax.legend(handles=[Line2D([], [], marker=mk, ls="", color="#52514e", markerfacecolor="#52514e" if k == 0 else "white", label=lab)
                   for k, (_, mk, lab) in enumerate(fams)], loc="upper center", bbox_to_anchor=(0.35, -0.16),
          frameon=False, fontsize=6, ncol=3)
letra(ax, "b")
# c) datos reales
ax = axs[1, 0]
for j, (k, nom, dic) in enumerate(otros):
    v = [dic[s] / ours[s] for s in ours if s in dic and ok(dic[s]) and ok(ours[s]) and dic[s] > 0 and ours[s] > 0]
    yj = len(otros) - 1 - j
    jit = (rng.random(len(v)) - 0.5) * 0.35
    ax.scatter(np.clip(v, 0.05, 20), yj + jit, s=9, color={"rand": COL["random"], "vac": COL["empty"]}.get(k, COL.get(k, "#8a8984")), edgecolor="white", linewidth=0.4)
    ax.plot([np.median(v)] * 2, [yj - 0.3, yj + 0.3], color=INK, lw=1.2)
ax.axvspan(0.95, 1.05, color="#efeeea", zorder=0); ax.axvline(1, color=INK2, lw=0.8)
ax.set_xscale("log"); ax.set_xlim(0.05, 20)
ax.set_yticks(range(len(otros))); ax.set_yticklabels([o[1] for o in otros][::-1])
ax.set_xlabel("Test $\\chi^2/n$, criterion / our method (one point per problem)")
ax.set_title("Real data: all criteria cluster around 1", loc="left", color=INK, pad=12)
ax.text(0.02, 1.0, "← better than ours", transform=ax.transAxes, color=INK2, fontsize=6, va="bottom")
ax.text(0.98, 1.0, "worse than ours →", transform=ax.transAxes, color=INK2, fontsize=6, ha="right", va="bottom")
letra(ax, "c")
# d) tiempos
ax = axs[1, 1]
xs, ys, nombres = [], [], []
for s, t in tpf.items():
    if s in tp and ok(tp[s].get("segundos")):
        xs.append(tp[s]["segundos"]); ys.append(max(t, 0.1)); nombres.append(corto(s))
techo = 3e4
ax.plot([0.1, techo], [0.1, techo], color=INK2, lw=0.8, ls="--")
ax.scatter(xs, ys, s=16, color=COL["perfil"], edgecolor="white", linewidth=0.6, zorder=3, label="Profile likelihood")
for x, yv, n in zip(xs, ys, nombres):
    if n in ("Alkan", "Isensee", "Zheng", "Smith", "Bachmann", "Lucarelli"):
        ax.text(x * 1.18, yv, n, fontsize=5.5, color=INK2, va="center")
xi = [tp[s]["segundos"] for s in nopf if s in tp]
ax.scatter(xi, [techo] * len(xi), s=22, marker="^", color=INK2, zorder=3)
ax.text(1.1, techo * 22, "▲ profile likelihood not run (> 60 free parameters):\n   " +
        ", ".join(corto(s) for s in sorted(nopf, key=lambda s: tp.get(s, {}).get("segundos", 0))),
        fontsize=5.5, color=INK2, va="top", fontfamily="DejaVu Sans")
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(1, 5e3); ax.set_ylim(0.1, techo * 30)
ax.set_xlabel("Our complete method (s)"); ax.set_ylabel("Profile likelihood (s)")
ax.set_title("Computation time per problem", loc="left", color=INK, pad=12)
ax.text(0.97, 0.06, "above the diagonal:\nour method faster", transform=ax.transAxes, ha="right", fontsize=6, color=INK2)
letra(ax, "d")
fig.savefig(FIG / "fig4_comparison.pdf", bbox_inches="tight")
fig.savefig(FIG / "fig4_comparison.png", dpi=200, bbox_inches="tight")
plt.close(fig)
print("ok", len(filas), len(sint))
