#!/usr/bin/env python3
"""
Figuras del texto principal generadas a partir de los resultados (14 de octubre de 2026):
  fig3_validation_v2.pdf — a) reducido frente a completo en datos reales (ancla θ₀);
                           b) sintético con 20 semillas: fracción de semillas en que el reducido
                              predice al menos tan bien como el completo, por problema.
  fig4_comparison.pdf    — comparación con QR, Brun, Morris y verosimilitud perfilada:
                           a) admisibilidad a ±5 % y ±20 %; b) aciertos en el sintético con IC 95 %
                           por bootstrap de problemas; c) datos reales, cociente de χ² con el
                           nuestro; d) tiempo de cómputo frente a la verosimilitud perfilada.
Uso: python figuras_comparacion.py [carpeta_resultados] [carpeta_figuras]
"""
import sys, json, glob, math, collections
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
R = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "resultados"
FIG = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE.parent / "paper" / "scirep" / "figures"
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
ext = L("validacion_externa_bio")
filas = []
for s, d in ext.items():
    r, f, t0 = d.get("A_chi2_test_red"), d.get("A_chi2_test_full"), d.get("A_chi2_test_theta0")
    if ok(r) and ok(f) and f > 0 and ok(t0) and t0 >= 0.01:
        filas.append((corto(s), r / f, r > 10))
filas.sort(key=lambda x: x[1])
S = collections.defaultdict(dict)
for f in glob.glob(str(R / "sintetico_semillas" / "*" / "s*.json")):
    d = json.loads(Path(f).read_text(encoding="utf-8"))
    if ok(d.get("B_epred_red")) and ok(d.get("B_epred_full")) and ok(d.get("B_chi2_test_theta0")) \
            and d["B_chi2_test_theta0"] >= 2:
        S[d["sistema"]][d["semilla"]] = d["B_epred_red"] <= d["B_epred_full"]
sint = sorted(((corto(s), np.mean(list(v.values())), len(v), sum(v.values())) for s, v in S.items() if len(v) >= 3),
              key=lambda x: x[1])

fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 4.6), gridspec_kw={"wspace": 0.55})
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
fig.savefig(FIG / "fig3_validation_v2.pdf", bbox_inches="tight")
fig.savefig(FIG / "fig3_validation_v2.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# ── Figura 4 ──────────────────────────────────────────────────────────────────────
def adm(sub):
    A = collections.defaultdict(dict)
    for f in glob.glob(str(R / sub / "*__adm.json")):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        if "admisible" in d:
            A[d["metodo"]][d["sistema"]] = bool(d["admisible"])
    return A
A5, A20 = adm("control_admis_sint"), adm("control_admis_sint_nivel020")

# sintético: casos comunes con señal, bootstrap por problemas
SS = collections.defaultdict(lambda: collections.defaultdict(dict))
for f in glob.glob(str(R / "control_admis_sint" / "*__sint_*.json")):
    d = json.loads(Path(f).read_text(encoding="utf-8"))
    if ok(d.get("B_epred_red")):
        SS[d["sistema"]][d["metodo"]][d["semilla"]] = d
for f in glob.glob(str(R / "sintetico_semillas" / "*" / "s*.json")):
    d = json.loads(Path(f).read_text(encoding="utf-8"))
    if ok(d.get("B_epred_red")):
        SS[d["sistema"]]["ours"][d["semilla"]] = d
cnt = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
for s in SS:
    for k in range(42, 62):
        ds = [SS[s][m].get(k) for m in M]
        if all(ds) and ds[0]["B_chi2_test_theta0"] >= 2:
            for m, d in zip(M, ds):
                cnt[s][m][0] += d["B_epred_red"] <= TAU; cnt[s][m][1] += 1
sis = sorted(cnt)
rng = np.random.default_rng(0)
idx = rng.integers(0, len(sis), size=(10000, len(sis)))
tasa, ic = {}, {}
for m in M:
    a = np.array([cnt[s][m][0] for s in sis], float); n = np.array([cnt[s][m][1] for s in sis], float)
    tasa[m] = a.sum() / n.sum()
    bt = a[idx].sum(1) / n[idx].sum(1)
    ic[m] = np.percentile(bt, [2.5, 97.5])

# datos reales: cocientes con el nuestro
an = L("validacion_anidada"); qr = L("comparacion_brun"); mb = L("control_morris_brun")
pf = L("control_perfil"); al = L("control_aleatorio"); va = L("control_vacio")
ours = {s: d.get("chi2_test_red_original") for s, d in an.items()}
otros = [("brun", "Brun", {s: d.get("chi2_brun") for s, d in mb.items()}),
         ("morris", "Morris", {s: d.get("chi2_morris") for s, d in mb.items()}),
         ("perfil", "Profile likelihood", {s: d.get("chi2_perfil") for s, d in pf.items()}),
         ("qr", "Pivoted QR", {s: d.get("chi2_qr") for s, d in qr.items()}),
         ("rand", "Random (median of 20)", {s: d.get("chi2_rand_median") for s, d in al.items()}),
         ("vac", "Calibration only", {s: d.get("chi2_vacio") for s, d in va.items()})]

# tiempos
tp = L("reclasificacion_salidas_bio_poda_tiempopar"); tp.update(L("reclasificacion_salidas_bio_poda_fixcal"))
tpf, nopf = {}, []
for line in (R / "control_perfil_ronda0" / "control_perfil.log").read_text(encoding="utf-8", errors="ignore").splitlines():
    if '"terminado": true' in line:
        d = json.loads(line); tpf[d["sistema"]] = d["seg_total"]
for s, d in pf.items():
    if "no_evaluable" in d and "PL_PMAX" in d["no_evaluable"]:
        nopf.append(s)

fig, axs = plt.subplots(2, 2, figsize=(7.2, 6.2), gridspec_kw={"hspace": 0.6, "wspace": 0.6})
# a) admisibilidad
ax = axs[0, 0]
yy = np.arange(len(M))[::-1]
for j, m in enumerate(M):
    for off, A, alpha, hatch, lab in ((0.19, A5, 1.0, None, "±5%"), (-0.19, A20, 0.55, "////", "±20%")):
        v = list(A[m].values()); fr = np.mean(v)
        ax.barh(yy[j] + off, fr, height=0.34, color=COL[m], alpha=alpha, hatch=hatch, edgecolor="white", lw=0.5)
        ax.text(fr + 0.015, yy[j] + off, f"{sum(v)}/{len(v)}", va="center", fontsize=6, color=INK)
ax.set_yticks(yy); ax.set_yticklabels([NOM[m] for m in M]); ax.set_xlim(0, 1.18)
ax.set_xticks([0, 0.25, 0.5, 0.75, 1]); ax.set_xticklabels(["0", "25", "50", "75", "100"])
ax.set_xlabel("Problems with an admissible subset (%)")
ax.set_title("Reproduces the full model", loc="left", color=INK, pad=12)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color="#8a8984", label="±5% (level used by our method)"),
                   Patch(facecolor="#8a8984", alpha=0.55, hatch="////", edgecolor="white", label="±20% (used by none)")],
          loc="upper center", bbox_to_anchor=(0.42, -0.2), frameon=False, fontsize=6, ncol=2)
letra(ax, "a")
# b) sintético
ax = axs[0, 1]
for j, m in enumerate(M):
    ax.plot(ic[m], [yy[j]] * 2, color=COL[m], lw=2, solid_capstyle="round")
    ax.scatter(tasa[m], yy[j], s=40, color=COL[m], edgecolor="white", linewidth=1, zorder=3)
    ax.text(ic[m][1] + 0.015, yy[j], f"{tasa[m]:.0%}", va="center", fontsize=6, color=INK)
ax.axvline(tasa["ours"], color=COL["ours"], lw=0.8, ls=":")
ax.set_yticks(yy); ax.set_yticklabels([NOM[m] for m in M]); ax.set_xlim(0.15, 0.85)
ax.set_xticks([0.2, 0.4, 0.6, 0.8]); ax.set_xticklabels(["20", "40", "60", "80"])
ax.set_xlabel(f"Synthetic cases with $e_{{\\mathrm{{pred}}}}\\leq\\tau_e$ (%), 95% CI")
ax.set_title(f"Predicts unseen data ({int(sum(cnt[s]['ours'][1] for s in sis))} cases, {len(sis)} problems)", loc="left", color=INK, pad=12)
letra(ax, "b")
# c) datos reales
ax = axs[1, 0]
for j, (k, nom, dic) in enumerate(otros):
    v = [dic[s] / ours[s] for s in ours if s in dic and ok(dic[s]) and ok(ours[s]) and dic[s] > 0 and ours[s] > 0]
    yj = len(otros) - 1 - j
    jit = (rng.random(len(v)) - 0.5) * 0.35
    ax.scatter(np.clip(v, 0.05, 20), yj + jit, s=9, color=COL.get(k, "#8a8984"), edgecolor="white", linewidth=0.4)
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
    if n in ("Alkan", "Isensee", "Zheng", "Smith"):
        ax.text(x * 1.18, yv, n, fontsize=5.5, color=INK2, va="center")
xi = [tp[s]["segundos"] for s in nopf if s in tp]
ax.scatter(xi, [techo] * len(xi), s=22, marker="^", color=INK2, zorder=3)
ax.text(1.1, techo * 22, "▲ infeasible for profile likelihood (> 60 free parameters):\n   " +
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
print("ok", {m: f"{tasa[m]:.3f}" for m in M}, len(filas), len(sint))
