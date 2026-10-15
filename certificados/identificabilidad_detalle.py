#!/usr/bin/env python3
"""
Resultados por sistema de la nota «Identifiability of the selected parameters»:
  * figS_identif_perfiles.pdf — perfil Δχ² de cada parámetro seleccionado en los 32 problemas
    (un panel por problema; color según la clase del perfil; umbral 3,84);
  * tableS_identif_param.tex — una fila por parámetro: clase, intervalo de confianza (log),
    información perfilada I_j, semiancho de Wald, γ, ε, t* y distancias a los límites.
Fuentes: resultados/identificabilidad/perfil/ y certificado*.csv.
Uso: python identificabilidad_detalle.py [--paper DIR]  (por defecto ../paper/scirep)
"""
import json, math, sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve().parent
R = HERE / "resultados" / "identificabilidad"
PAPER = Path(sys.argv[sys.argv.index("--paper") + 1]) if "--paper" in sys.argv else HERE.parent / "paper" / "scirep"
UMBRAL = 3.84
LN10 = math.log(10)

INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
COL = {"identificable": "#2a78d6", "no identificable practico": "#eb6834", "plano": "#8a8984"}
NOMBRE = {"identificable": "identifiable", "no identificable practico": "practically non-identifiable",
          "plano": "flat"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 6, "axes.titlesize": 6.5,
                     "axes.edgecolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False})


def corto(s):
    return s.split("_")[0].replace("SalazarCavazos", "Salazar-Cavazos")


def esc(s):
    return str(s).replace("_", "\\_\\allowbreak{}")


cert = pd.concat([pd.read_csv(f) for f in sorted(R.glob("certificado*.csv"))], ignore_index=True)
if "error" in cert:
    cert = cert[cert["error"].isna()]
cert = cert.drop_duplicates(["sistema", "parametro"], keep="last").set_index(["sistema", "parametro"])

problemas = sorted(json.loads(f.read_text(encoding="utf-8"))["sistema"] for f in (R / "perfil").glob("*.json"))

# ── figura ────────────────────────────────────────────────────────────────────────
nc = 4
nr = math.ceil(len(problemas) / nc)
fig, axs = plt.subplots(nr, nc, figsize=(7.1, 1.35 * nr))
for ax, s in zip(axs.flat, problemas):
    d = json.loads((R / "perfil" / f"{s}.json").read_text(encoding="utf-8"))
    ymax = 0.0
    for p in d["perfiles"]:
        nom = p["parametro"]
        pts = []
        for f in (R / "perfil" / s).glob(f"p_{nom}_*.json"):
            q = json.loads(f.read_text(encoding="utf-8"))
            if q["dchi2"] > 1e4:
                continue
            key = (s, nom)
            if key in cert.index:
                lo, hi = float(cert.loc[key, "d_menos"]), float(cert.loc[key, "d_mas"])
                x = q["lado"] * q["despl"]
                if (x < 0 and -x > lo + 1e-6) or (x > 0 and x > hi + 1e-6):
                    continue          # fuera de los límites del estudio
            pts.append((q["lado"] * q["despl"], max(q["dchi2"], 0.0)))
        pts = sorted(pts + [(0.0, 0.0)])
        if len(pts) < 2:
            continue
        x, y = zip(*pts)
        ymax = max(ymax, max(y))
        ax.plot(np.array(x) / LN10, y, "-o", color=COL[p["clase"]], lw=0.9, ms=1.8, zorder=3)
    ax.axhline(UMBRAL, color=INK2, lw=0.6, ls="--", zorder=2)
    ax.set_yscale("symlog", linthresh=10)
    ax.set_ylim(0, max(30.0, 1.5 * ymax))
    ax.set_title(corto(s), loc="left", color=INK, pad=2)
    ax.grid(True, color=GRID, lw=0.3, zorder=0)
    ax.tick_params(length=2, pad=1)
for ax in list(axs.flat)[len(problemas):]:
    ax.axis("off")
for ax in axs[-1]:
    ax.set_xlabel(r"$\log_{10}\theta_j-\log_{10}\hat\theta_j$")
for ax in axs[:, 0]:
    ax.set_ylabel(r"$\Delta\chi^2$")
fig.legend(handles=[Line2D([], [], color=c, marker="o", ms=3, lw=1, label=NOMBRE[k]) for k, c in COL.items()]
           + [Line2D([], [], color=INK2, ls="--", lw=0.8, label=r"$\Delta\chi^2=3.84$")],
           loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, -0.005))
fig.tight_layout(rect=(0, 0.025, 1, 1), h_pad=0.6, w_pad=0.4)
(PAPER / "figures").mkdir(parents=True, exist_ok=True)
fig.savefig(PAPER / "figures" / "figS_identif_perfiles.pdf")
plt.close(fig)

# ── tabla por parámetro ───────────────────────────────────────────────────────────
CL = {"identificable": "I", "no identificable practico": "N", "plano": "F"}


def num(x, nd=2):
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "$\\infty$" if x is not None and x > 0 else "--"
    if x == 0:
        return "0"
    if abs(x) >= 1e4 or abs(x) < 1e-2:
        e = int(math.floor(math.log10(abs(x))))
        return f"${x / 10 ** e:.1f}\\times10^{{{e}}}$"
    return f"{x:.{nd}f}"


filas = []
for s in problemas:
    d = json.loads((R / "perfil" / f"{s}.json").read_text(encoding="utf-8"))
    for i, p in enumerate(d["perfiles"]):
        nom = p["parametro"]
        c = cert.loc[(s, nom)] if (s, nom) in cert.index else None
        cls = CL[p["clase"]]
        if cls == "F" and p["dchi2_max_izq"] == 0 and p["dchi2_max_der"] == 0 and p.get("puntos_fallidos", 0):
            cls = "--"
        # cruce del umbral interpolando linealmente √Δχ² (exacto si el perfil es una parábola)
        cr = {}
        for lado in (-1, 1):
            pts = []
            for f in (R / "perfil" / s).glob(f"p_{nom}_{'+' if lado > 0 else '-'}_*.json"):
                q = json.loads(f.read_text(encoding="utf-8"))
                lim = float(c["d_menos"] if lado < 0 else c["d_mas"]) if c is not None else math.inf
                if q["dchi2"] <= 1e4 and q["despl"] <= lim + 1e-6:
                    pts.append((q["despl"], math.sqrt(max(q["dchi2"], 0.0))))
            prev_t, prev_v, cr[lado] = 0.0, 0.0, math.inf
            for tq, vq in sorted(pts):
                if vq > math.sqrt(UMBRAL):
                    cr[lado] = prev_t + (tq - prev_t) * (math.sqrt(UMBRAL) - prev_v) / max(vq - prev_v, 1e-12)
                    break
                prev_t, prev_v = tq, vq
        ic = f"[$-${num(cr[-1] / LN10)}, {num(cr[1] / LN10)}]" if cls != "--" else "--"
        filas.append([corto(s) if i == 0 else "", "\\texttt{" + esc(nom) + "}",
                      cls + "/" + (CL[p["clase_robusto"]] if cls != "--" else "--"), ic,
                      num(None if c is None else float(c["I_j"]), 1),
                      num(None if c is None else float(c["tstar_lineal"]) / LN10),
                      num(None if c is None else float(c["gamma"])),
                      num(None if c is None else float(c["eps_j"]), 1),
                      num(None if c is None else float(c["d_menos"]) / LN10),
                      num(None if c is None else float(c["d_mas"]) / LN10),
                      "\\checkmark" if c is not None and bool(c["certificado_local"]) else ""])
L = [r"\begin{longtable}{@{}l>{\raggedright\arraybackslash}p{1.4cm}clrrrrrrc@{}}",
     r"\caption{Identifiability of every selected parameter in the reduced problem. Class: profile-likelihood class with the threshold 3.84 / with the robust threshold (I, identifiable; N, practically non-identifiable; F, flat; --, the profile could not be simulated). CI: 95\% profile-likelihood interval of $\log_{10}\theta_j-\log_{10}\hat\theta_j$, interpolated between profile points ($\infty$, the profile does not cross the threshold on that side within the bounds). $I_j$: profiled information $1/[(A^{\top}A)^{-1}]_{jj}$ (computed by projection); Wald: half-width $\sqrt{3.84/I_j}$ in $\log_{10}$ units; $\gamma=\|Pr_0\|$; $\varepsilon$: largest nonlinear remainder at the profile points; $d_-$, $d_+$: distances from $\log_{10}\hat\theta_j$ to $\log_{10}(|\theta_0|/10)$ and $\log_{10}(10|\theta_0|)$; Lean: hypotheses of \texttt{practically\_identifiable\_grad} satisfied at the profile points up to the first crossing.}\label{tab:identifparam}\\",
     r"\toprule",
     r"Problem & Parameter & Class & CI ($\log_{10}$) & $I_j$ & Wald & $\gamma$ & $\varepsilon$ & $d_-$ & $d_+$ & Lean \\",
     r"\midrule", r"\endfirsthead",
     r"\toprule",
     r"Problem & Parameter & Class & CI ($\log_{10}$) & $I_j$ & Wald & $\gamma$ & $\varepsilon$ & $d_-$ & $d_+$ & Lean \\",
     r"\midrule", r"\endhead"]
L += [" & ".join(f) + r" \\" for f in filas]
L += [r"\bottomrule", r"\end{longtable}"]
(PAPER / "tables").mkdir(parents=True, exist_ok=True)
(PAPER / "tables" / "tableS_identif_param.tex").write_text("\n".join(L) + "\n", encoding="utf-8")
print(f"{len(problemas)} problemas, {len(filas)} parámetros")
