#!/usr/bin/env python3
"""
Figuras del suplemento de la comparación de métodos (14 de octubre de 2026):
  figS_perfiles.pdf          — perfiles de verosimilitud de ejemplo (tres problemas)
  figS_admis_mapa.pdf        — admisibilidad por problema y criterio, a ±5 % y ±20 %
  figS_synth_semillas.pdf    — aciertos del sintético por semilla y criterio
  figS_anidada.pdf           — validación anidada: original, anidado y completo
Uso: python figuras_suplemento.py [carpeta_resultados] [carpeta_figuras]
"""
import sys, json, glob, math, collections
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

HERE = Path(__file__).resolve().parent
R = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "resultados"
FIG = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE.parent / "paper" / "scirep" / "figures"
TAU = math.sqrt(1 - 0.81)
COL = {"ours": "#2a78d6", "brun": "#eb6834", "morris": "#1baf7a", "perfil": "#eda100", "qr": "#e87ba4"}
NOM = {"ours": "Our method", "brun": "Brun", "morris": "Morris", "perfil": "Profile likelihood", "qr": "Pivoted QR"}
M = ["ours", "brun", "morris", "perfil", "qr"]
INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"], "font.size": 7,
                     "axes.titlesize": 8, "axes.edgecolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42})
ok = lambda x: isinstance(x, (int, float)) and math.isfinite(x)
corto = lambda s: s.split("_")[0].replace("SalazarCavazos", "Salazar-Cavazos")


def L(sub):
    return {Path(f).stem: json.loads(Path(f).read_text(encoding="utf-8")) for f in glob.glob(str(R / sub / "*.json"))}


# ── perfiles de ejemplo ───────────────────────────────────────────────────────────
ejemplos = ["Boehm_JProteomeRes2014", "Fiedler_BMCSystBiol2016", "Raia_CancerResearch2011"]
fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.6), gridspec_kw={"wspace": 0.35})
for ax, s in zip(axs, ejemplos):
    res = json.loads((R / "control_perfil" / f"{s}.json").read_text(encoding="utf-8"))
    clase = {p["parametro"]: p["clase"] for p in res["perfiles"]}
    sel = set(res["S_perfil"]); ours = set(res["S_ours"])
    pts = collections.defaultdict(list)
    for f in glob.glob(str(R / "control_perfil" / s / "perfil_*.json")):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        if d["dchi2"] <= 1e4:
            pts[d["parametro"]].append((d["lado"] * d["despl"], max(d["dchi2"], 1e-3)))
    estilo = {"identificable": ("#2a78d6", 1.4), "no identificable practico": ("#eda100", 1.0), "plano": ("#b0afaa", 0.8)}
    for par, v in pts.items():
        v = sorted(v + [(0.0, 1e-3)])
        c, lw = estilo[clase.get(par, "plano")]
        ax.plot([a for a, _ in v], [b for _, b in v], color=c, lw=lw, alpha=0.9)
        if (par in sel or par in ours) and not s.startswith("Raia"):
            a, b = max(v, key=lambda x: x[1])
            ax.text(a, b * 1.3, par + (" (P)" if par in sel else "") + (" (O)" if par in ours else ""),
                    fontsize=5, color=INK2, ha="center")
    ax.axhline(3.84, color=INK, lw=0.8, ls="--")
    ax.set_yscale("log"); ax.set_ylim(1e-3, 5e3)
    ax.set_xlabel("Displacement of log$|\\theta_j|$ from the optimum")
    ax.set_title(f"{corto(s)}: {res['n_identificables']} ident., {res['n_no_identificables_practicos']} one side, {res['n_planos']} flat",
                 loc="left", fontsize=7, color=INK)
axs[0].set_ylabel("$\\Delta\\chi^2$ (training data)")
from matplotlib.lines import Line2D
fig.legend(handles=[Line2D([], [], color="#2a78d6", lw=1.4, label="identifiable"),
                    Line2D([], [], color="#eda100", lw=1.0, label="bounded on one side"),
                    Line2D([], [], color="#b0afaa", lw=0.8, label="flat"),
                    Line2D([], [], color=INK, lw=0.8, ls="--", label="$\\Delta\\chi^2=3.84$")],
           loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, -0.12), fontsize=6)
fig.savefig(FIG / "figS_perfiles.pdf", bbox_inches="tight"); plt.close(fig)

# ── mapa de admisibilidad ─────────────────────────────────────────────────────────
def adm(sub):
    A = collections.defaultdict(dict)
    for f in glob.glob(str(R / sub / "*__adm.json")):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        if "eajuste_med" in d:
            A[d["sistema"]][d["metodo"]] = min(d["eajuste_med"], d["erel_med"])
    return A
A5, A20 = adm("control_admis_sint"), adm("control_admis_sint_nivel020")
sis = sorted(A5, key=lambda s: corto(s))
fig, axs = plt.subplots(1, 2, figsize=(7.2, 6.4), gridspec_kw={"wspace": 0.08})
cmap = plt.get_cmap("Blues_r")
for ax, A, tit in ((axs[0], A5, "$\\pm$5% (level used by our method)"), (axs[1], A20, "$\\pm$20% (used by none)")):
    Z = np.full((len(sis), len(M)), np.nan)
    for i, s in enumerate(sis):
        for j, m in enumerate(M):
            if m in A.get(s, {}):
                Z[i, j] = A[s][m]
    ax.imshow(np.where(Z <= TAU, 0.2, 0.92), cmap=ListedColormap(["#2a78d6", "#f1f0ec"]), vmin=0, vmax=1, aspect="auto")
    for i in range(len(sis)):
        for j in range(len(M)):
            z = Z[i, j]
            ax.text(j, i, "--" if not ok(z) else f"{z:.2f}", ha="center", va="center", fontsize=5.2,
                    color=("white" if ok(z) and z <= TAU else INK2))
    ax.set_xticks(range(len(M))); ax.set_xticklabels([NOM[m].replace(" ", "\n") for m in M], fontsize=6)
    ax.xaxis.tick_top()
    ax.set_yticks(range(len(sis))); ax.set_yticklabels([corto(s) for s in sis] if ax is axs[0] else [])
    ax.set_title(tit, fontsize=7, pad=24, color=INK)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0)
fig.text(0.5, 0.06, "Blue: admissible (smaller of median $e_{\\mathrm{fit}}$ and median $e_{\\mathrm{rel}}$ at most $\\tau_e=0.436$); value shown in each cell",
         ha="center", fontsize=6, color=INK2)
fig.savefig(FIG / "figS_admis_mapa.pdf", bbox_inches="tight"); plt.close(fig)

# ── aciertos del sintético por semilla ───────────────────────────────────────────
SS = collections.defaultdict(lambda: collections.defaultdict(dict))
for f in glob.glob(str(R / "control_admis_sint" / "*__sint_*.json")):
    d = json.loads(Path(f).read_text(encoding="utf-8"))
    if ok(d.get("B_epred_red")):
        SS[d["sistema"]][d["metodo"]][d["semilla"]] = d
for f in glob.glob(str(R / "sintetico_semillas" / "*" / "s*.json")):
    d = json.loads(Path(f).read_text(encoding="utf-8"))
    if ok(d.get("B_epred_red")):
        SS[d["sistema"]]["ours"][d["semilla"]] = d
sem = list(range(42, 62))
tasa = {m: [] for m in M}
for k in sem:
    c = {m: [0, 0] for m in M}
    for s in SS:
        ds = [SS[s][m].get(k) for m in M]
        if all(ds) and ds[0]["B_chi2_test_theta0"] >= 2:
            for m, d in zip(M, ds):
                c[m][0] += d["B_epred_red"] <= TAU; c[m][1] += 1
    for m in M:
        tasa[m].append(c[m][0] / c[m][1] if c[m][1] else np.nan)
fig, ax = plt.subplots(figsize=(7.2, 2.8))
# marcador y tipo de línea propios por criterio, para no distinguir las series sólo por el color
MARC = ["o", "s", "^", "D", "v"]
LINEA = ["-", "--", ":", "-.", (0, (5, 1, 1, 1))]
for j, m in enumerate(M):
    x = np.arange(len(sem)) + (j - 2) * 0.13
    ax.scatter(x, tasa[m], s=16, marker=MARC[j], color=COL[m], edgecolor="white", linewidth=0.5,
               label=NOM[m], zorder=3)
    ax.plot([-0.5, len(sem) - 0.5], [np.nanmean(tasa[m])] * 2, color=COL[m], lw=0.9, ls=LINEA[j], alpha=0.8)
ax.set_xticks(range(len(sem))); ax.set_xticklabels(sem, fontsize=6); ax.set_xlabel("Seed")
ax.set_ylabel("Fraction of cases with $e_{\\mathrm{pred}}\\leq\\tau_e$")
ax.set_ylim(0, 1); ax.grid(axis="y", color=GRID, lw=0.5)
ax.legend(ncol=5, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.15), fontsize=6)
fig.savefig(FIG / "figS_synth_semillas.pdf", bbox_inches="tight"); plt.close(fig)

# ── validación anidada ────────────────────────────────────────────────────────────
an = L("validacion_anidada")
fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.2), gridspec_kw={"wspace": 0.35})
o = np.array([an[s]["chi2_test_red_original"] for s in an]); ne = np.array([an[s]["chi2_test_red_nested"] for s in an])
fu = np.array([an[s]["chi2_test_full_train"] for s in an]); nm = [corto(s) for s in an]
for ax, x, xl, tit in ((axs[0], fu, "Full model re-estimated on training data", "Nested reduced = full training fit"),
                       (axs[1], o, "Reduced model anchored at $\\theta_0$ (original)", "Removing the $\\theta_0$ anchor worsens prediction")):
    lo, hi = 1e-8, max(x.max(), ne.max()) * 3
    ax.plot([lo, hi], [lo, hi], color=INK2, lw=0.8, ls="--")
    ax.scatter(x, ne, s=16, color="#2a78d6", edgecolor="white", linewidth=0.6, zorder=3)
    for xi, yi, n in zip(x, ne, nm):
        if yi / xi > 3 or xi / yi > 3:
            ax.text(xi * 1.3, yi, n, fontsize=5.5, color=INK2, va="center")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
    ax.set_xlabel(f"Test $\\chi^2/n$, {xl}"); ax.set_ylabel("Test $\\chi^2/n$, nested reduced model")
    ax.set_title(tit, loc="left", fontsize=7, color=INK)
fig.savefig(FIG / "figS_anidada.pdf", bbox_inches="tight"); plt.close(fig)
print("ok")
