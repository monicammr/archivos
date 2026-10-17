#!/usr/bin/env python3
"""
Tables and figures of the additional analyses requested in the review (Supplementary Notes on
robustness, synthetic experiment, method settings and "Random scenarios and large problems"):

  tables/tableS_robust_indep.tex   patterns with paired and with independent directions (B5)
  figures/figS_robust_indep.pdf    median e_fit with paired and independent directions (B5)
  tables/tableS_signal.tex         true signal and success per problem at +-5, +-20 and +-50 % (C3)
  figures/figS_signal.pdf          success against the true signal and against the amplitude (C3)
  tables/tableS_abs.tex            reproduction error in units of the noise (C1)
  tables/tableS_settings_extra.tex settings variants of Lang and Raimundez

Data: results/robustness, robustness_independent, synthetic_seeds, synthetic_seeds_a005/_a050,
synthetic_signal_a005/_a020/_a050, absolute_error, settings_extra, selection.
Usage: python make_review_notes.py   (prints the numbers quoted in the text)
"""
import json
import math
from collections import Counter

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import RESULTS as RES, FIG, TAB, load

plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans"],
                     "font.size": 8, "axes.linewidth": 0.8, "pdf.fonttype": 42})
TAU = float(np.sqrt(1 - 0.81))
INK, MUTED, GRID = "#222222", "#6b6b6b", "#e6e6e6"
COL = {"A": "#2a78d6", "B": "#eb6834", "C": "#1baf7a", "D": "#555555"}
LEVELS = ["1", "5", "10", "20", "30", "40", "50"]
SEL = load("selection")
ADM = sorted(s for s, d in SEL.items() if d.get("admisible"))
ok = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)
short = lambda s: s.split("_")[0].replace("SalazarCavazos", "Salazar-Cavazos")
tt = lambda s: r"\texttt{" + s.replace("_", r"\_") + "}"


def longtable(spec, caption, label, head, rows):
    h = " & ".join(head) + r" \\"
    s = [rf"\begin{{longtable}}{{{spec}}}", rf"\caption{{{caption}}}\label{{{label}}}\\", r"\toprule", h, r"\midrule",
         r"\endfirsthead", r"\toprule", h, r"\midrule", r"\endhead"]
    s += [" & ".join(r) + r" \\" for r in rows] + [r"\bottomrule", r"\end{longtable}"]
    return "\n".join(s) + "\n"


def write(name, text):
    (TAB / name).write_text(text, encoding="utf-8"); print("written", name)


# ── B5: paired and independent directions ─────────────────────────────────────────
PAI, IND = load("robustness"), load("robustness_independent")
rows, trans, maxdiff = [], Counter(), (0.0, "")
for s in ADM:
    if s not in PAI or s not in IND:
        continue
    a, b = PAI[s], IND[s]
    trans[(a["patron"], b["patron"])] += 1
    for k in LEVELS:
        if k != "5" and ok(a["niveles"][k]["eaj_med"]) and ok(b["niveles"][k]["eaj_med"]):
            d = abs(a["niveles"][k]["eaj_med"] - b["niveles"][k]["eaj_med"])
            if d > maxdiff[0]:
                maxdiff = (d, f"{short(s)} at +-{k}%")
    med = [("--" if not ok(b["niveles"][k]["eaj_med"]) else f"{100 * b['niveles'][k]['eaj_med']:.0f}") for k in LEVELS]
    e50 = b["niveles"]["50"]["eaj"]
    rows.append([short(s), a["patron"], (r"\textbf{" + b["patron"] + "}") if b["patron"] != a["patron"] else b["patron"]] + med +
                [f"{round(100 * sum(e <= TAU for e in e50) / len(e50))}" if e50 else "--"])
write("tableS_robust_indep.tex", longtable(
    "@{}lcc" + "r" * 7 + "r@{}",
    r"Robustness with independent directions at each perturbation size. Pattern with the paired design (the same fifteen directions rescaled at every size, as in the main text) and with independent directions (new directions at every size; in bold when the pattern changes); median $e_{\mathrm{fit}}$ (\%) over the valid scenarios at each size with independent directions; and pass rate $\pi$ (\%) at $\pm50\%$. At $\pm5\%$ both designs use the scenarios of the selection.",
    "tab:robindep", ["Problem", "Paired", "Indep."] + [rf"$\pm${k}\%" for k in LEVELS] + [r"$\pi_{50}$"], rows))
fig, axs = plt.subplots(1, 2, figsize=(7.0, 3.1))
for ax, k in zip(axs, ("20", "50")):
    for s in ADM:
        if s in PAI and s in IND:
            x, y = PAI[s]["niveles"][k]["eaj_med"], IND[s]["niveles"][k]["eaj_med"]
            if ok(x) and ok(y):
                ax.scatter(100 * x, 100 * y, s=18, color=COL[IND[s]["patron"]], edgecolor="none", zorder=3)
                if abs(x - y) > 0.08 or (x - TAU) * (y - TAU) < 0:
                    ax.annotate(short(s), (100 * x, 100 * y), fontsize=5.6, xytext=(3, 2), textcoords="offset points", color=INK)
    ax.plot([0, 70], [0, 70], color=MUTED, lw=0.7, ls="--")
    ax.axvline(100 * TAU, color=MUTED, lw=0.6, ls=":"); ax.axhline(100 * TAU, color=MUTED, lw=0.6, ls=":")
    ax.set_xlim(0, 70); ax.set_ylim(0, 70); ax.grid(color=GRID, lw=0.5)
    ax.set_xlabel(f"Median $e_{{fit}}$ (%), paired directions, ±{k}%")
    ax.set_ylabel(f"Median $e_{{fit}}$ (%), independent directions, ±{k}%")
    ax.set_title(f"±{k}%", fontsize=8, loc="left", fontweight="bold")
for p, c in COL.items():
    if p != "D":
        axs[1].scatter([], [], s=16, color=c, label=f"pattern {p} (independent)")
axs[1].legend(fontsize=6.2, frameon=False, loc="upper left")
fig.tight_layout(); fig.savefig(FIG / "figS_robust_indep.pdf"); plt.close(fig)
pi = Counter(r["patron"] for s, r in PAI.items() if s in ADM); ii = Counter(r["patron"] for s, r in IND.items() if s in ADM)
print("B5: paired", dict(pi), "independent", dict(ii), "transitions", dict(trans), "max diff", maxdiff)

# ── C3: signal and amplitudes ─────────────────────────────────────────────────────
def per_seed(sub, seeds):
    out = {}
    d = RES / sub
    for s in ADM:
        for f in sorted((d / s).glob("s*.json")) if (d / s).exists() else []:
            r = json.loads(f.read_text())
            if r.get("semilla") in seeds:
                out[(s, r["semilla"])] = r
    return out


S20, S10 = set(range(42, 62)), set(range(42, 52))


def sci(v):
    """Two significant digits; powers of ten outside [0.01, 100)."""
    if 0.01 <= abs(v) < 100:
        return f"{v:.2g}"
    m, e = f"{v:.1e}".split("e")
    return rf"${m}\times10^{{{int(e)}}}$"
SIG = {a: per_seed(f"synthetic_signal_a{a:03d}", S20 if a == 20 else S10) for a in (5, 20, 50)}
FIT = {5: per_seed("synthetic_seeds_a005", S10), 20: per_seed("synthetic_seeds", S20), 50: per_seed("synthetic_seeds_a050", S10)}


def counts(fit, seeds):
    c = [r for (s, k), r in fit.items() if k in seeds and ok(r.get("B_epred_red")) and r.get("B_chi2_test_theta0", 0) >= 2]
    succ = sum(r["B_epred_red"] <= TAU for r in c)
    comp = [r for r in c if ok(r.get("B_epred_full"))]
    le = sum(r["B_epred_red"] <= r["B_epred_full"] for r in comp)
    return len(c), succ, len(comp), le


amp = {a: counts(FIT[a], S10) for a in (5, 20, 50)}
for a in (5, 20, 50):
    v = [r["senal_rms_test"] for r in SIG[a].values() if ok(r.get("senal_rms_test"))]
    print(f"C3 +-{a}%: median signal {np.median(v):.3g} (IQR {np.percentile(v, 25):.3g}-{np.percentile(v, 75):.3g}), "
          f"signal cases {amp[a][0]}, success {amp[a][1]}, compared {amp[a][2]}, reduced<=full {amp[a][3]}")
bins = [(0, 0.3), (0.3, 1), (1, 3), (3, np.inf)]
pairs = [(SIG[20][k]["senal_rms_test"], r["B_epred_red"] <= TAU, r.get("B_chi2_test_theta0", 0) >= 2)
         for k, r in FIT[20].items() if k in SIG[20] and ok(r.get("B_epred_red")) and ok(SIG[20][k].get("senal_rms_test"))]
pairs = np.array(pairs, dtype=float)
binstat = []
for lo, hi in bins:
    m = (pairs[:, 0] >= lo) & (pairs[:, 0] < hi)
    binstat.append((lo, hi, int(m.sum()), 100 * pairs[m, 1].mean(), 100 * pairs[m, 2].mean()))
    print(f"C3 signal [{lo},{hi}): n={m.sum()} success {100 * pairs[m, 1].mean():.0f}% classified with signal {100 * pairs[m, 2].mean():.0f}%")
rows = []
for s in ADM:
    meds = []
    for a in (5, 20, 50):
        v = [r["senal_rms_test"] for (p, k), r in SIG[a].items() if p == s and ok(r.get("senal_rms_test"))]
        meds.append(sci(np.median(v)) if v else "--")
    sc = []
    for a in (5, 20, 50):
        n, su, _, _ = counts({k: r for k, r in FIT[a].items() if k[0] == s}, S10)
        sc.append(f"{su}/{n}" if n else "--")
    if all(m == "--" for m in meds):
        continue
    rows.append([short(s)] + meds + sc)
write("tableS_signal.tex", longtable(
    "@{}lrrrccc@{}",
    r"True signal and success of the reduced model in the synthetic experiment at three amplitudes of the truth, $\theta^\ast=\theta_0(1+a\,u)$. Signal: median over the seeds of the root mean square of $y(\theta^\ast)-y(\theta_0)$ per test measurement, in units of the recorded noise $\sigma$ (seeds 42--61 at $a=0.20$, 42--51 otherwise). Success: seeds with $e_{\mathrm{pred}}\le\tau_e$ among those with signal (test $\chi^2/n$ of $\theta_0\ge2$), seeds 42--51 at every amplitude.",
    "tab:signal", ["Problem", r"Signal $\pm$5\%", r"$\pm$20\%", r"$\pm$50\%", r"Success $\pm$5\%", r"$\pm$20\%", r"$\pm$50\%"], rows))
fig, axs = plt.subplots(1, 2, figsize=(7.0, 2.8))
x = np.arange(len(bins))
axs[0].bar(x - 0.18, [b[3] for b in binstat], 0.36, color="#2a78d6", label="reduced model reaches $e_{pred}\\leq\\tau_e$")
axs[0].bar(x + 0.18, [b[4] for b in binstat], 0.36, color="#bbbbbb", label="classified as signal ($\\chi^2/n$ of $\\theta_0\\geq2$)")
for i, b in enumerate(binstat):
    axs[0].text(i - 0.18, b[3] + 2, f"{b[3]:.0f}", ha="center", fontsize=6.2)
    axs[0].text(i, -12, f"n={b[2]}", ha="center", fontsize=6, color=MUTED)
axs[0].set_xticks(x); axs[0].set_xticklabels(["<0.3σ", "0.3–1σ", "1–3σ", ">3σ"])
axs[0].set_ylim(-16, 110); axs[0].set_ylabel("Cases (%)"); axs[0].set_xlabel("True signal (RMS per test measurement, ±20 %)")
axs[0].legend(fontsize=6, frameon=False, loc="upper left"); axs[0].grid(axis="y", color=GRID, lw=0.5)
axs[0].set_title("a", loc="left", fontweight="bold")
aa = [5, 20, 50]
axs[1].plot(aa, [100 * amp[a][1] / amp[a][0] for a in aa], "o-", color="#2a78d6", label="$e_{pred}\\leq\\tau_e$")
axs[1].plot(aa, [100 * amp[a][3] / amp[a][2] for a in aa], "s--", color="#eb6834", label="reduced at least as good as full")
for a in aa:
    axs[1].text(a, 30, f"{amp[a][0]} cases", ha="center", fontsize=6, color=MUTED)
axs[1].set_xticks(aa); axs[1].set_xticklabels(["±5%", "±20%", "±50%"]); axs[1].set_ylim(25, 80); axs[1].set_xlim(-1, 56)
axs[1].set_xlabel("Amplitude of the truth around $\\theta_0$"); axs[1].set_ylabel("Cases with signal (%)")
axs[1].legend(fontsize=6.2, frameon=False); axs[1].grid(color=GRID, lw=0.5); axs[1].set_title("b", loc="left", fontweight="bold")
fig.tight_layout(); fig.savefig(FIG / "figS_signal.pdf"); plt.close(fig)

# ── C1: error in units of the noise ───────────────────────────────────────────────
AB = load("absolute_error")


def fmt(v):
    if v == 0:
        return "0"
    if 0.01 <= abs(v) < 100:
        return f"{v:.2f}"
    m, e = f"{v:.1e}".split("e")
    return rf"${m}\times10^{{{int(e)}}}$"


rows = [[short(s), str(AB[s]["n"]), str(AB[s]["n_escenarios"]), f"{100 * AB[s]['e_fit_med']:.1f}", fmt(AB[s]["cambio_rms_sigma_med"]),
         fmt(AB[s]["error_rms_sigma_med"]), fmt(AB[s]["error_rms_sigma_max"])] for s in ADM if s in AB and "error" not in AB[s]]
write("tableS_abs.tex", longtable(
    "@{}lrrrrrr@{}",
    r"Reproduction error of the selected subsets in units of the recorded noise, over the scenarios at $\pm5\%$. $n$: number of measurements; Valid: valid scenarios. Change: root mean square of $\Delta y_{\mathrm{full}}$ per measurement, in units of $\sigma$ (median over the scenarios); Error: root mean square of the remaining error after re-estimation, $e_{\mathrm{fit}}\|\Delta y_{\mathrm{full}}\|/\sqrt n$ (median and maximum over the scenarios). A value below one means that the reduced model reproduces the perturbed full model to within the noise of the measurements; a change below one means that the perturbation itself is smaller than the noise (25 of the 31 problems). For the six problems decided to first order (Alkan, Bachmann, Chen, Isensee, Lucarelli, Raimundez) the median $e_{\mathrm{fit}}$ is the first-order value of this run; Table~1 of the main text gives the nonlinear re-estimation of the final subset.",
    "tab:abs", ["Problem", "$n$", "Valid", r"Median $e_{\mathrm{fit}}$ (\%)", r"Change (RMS, $\sigma$)", r"Error (RMS, $\sigma$)", "Max error"], rows))
e = np.array([AB[s]["error_rms_sigma_med"] for s in ADM if s in AB and "error" not in AB[s]])
mx = np.array([AB[s]["error_rms_sigma_max"] for s in ADM if s in AB and "error" not in AB[s]])
print(f"C1: {len(e)} problems; median error < 0.1 sigma in {(e < 0.1).sum()}, < 1 sigma in {(e < 1).sum()}; maximum < 1 sigma in {(mx < 1).sum()}")

# ── settings variants of Lang and Raimundez ───────────────────────────────────────
NAME = {"delta_0.001": r"$\delta=0.1\%$", "delta_0.05": r"$\delta=5\%$", "tolerances_1e-9_1e-12": r"tolerances $10^{-9}/10^{-12}$",
        "tolerances_1e-6_1e-8": r"tolerances $10^{-6}/10^{-8}$", "perturbation_0.01": r"perturbation $\pm1\%$",
        "perturbation_0.10": r"perturbation $\pm10\%$", "tauR_0.80": r"$\tau_R=0.80$", "tauR_0.85": r"$\tau_R=0.85$",
        "tauR_0.95": r"$\tau_R=0.95$", "tauK_5": r"$\tau_\kappa=\tau_{\mathrm{VIF}}=5$", "tauK_30": r"$\tau_\kappa=\tau_{\mathrm{VIF}}=30$",
        "tauE_0.10": r"$\tau_e=0.10$", "tauE_0.20": r"$\tau_e=0.20$", "tauE_0.30": r"$\tau_e=0.30$", "tauE_0.50": r"$\tau_e=0.50$"}
rows = []


def cell(r, base):
    if r is None:
        return "not computed"
    if not r.get("admisible"):
        return rf"$\times$ ({len(r['S'])} par., {100 * r['eajuste_med']:.0f}\%)"
    if r["S"] == base["S"]:
        return rf"$=$ ({100 * r['eajuste_med']:.0f}\%)"
    return ", ".join(tt(x) for x in r["S"]) + rf" ({100 * r['eajuste_med']:.0f}\%)"


bL, bR = SEL["Lang_PLOSComputBiol2024"], SEL["Raimundez_PCB2020"]
rows.append(["Baseline", cell(bL, {"S": []}), cell(bR, {"S": []})])
for k, lab in NAME.items():
    get = lambda p: json.loads((RES / "settings_extra" / k / f"{p}.json").read_text()) if (RES / "settings_extra" / k / f"{p}.json").exists() else None
    rows.append([lab, cell(get("Lang_PLOSComputBiol2024"), bL), cell(get("Raimundez_PCB2020"), bR)])
write("tableS_settings_extra.tex", longtable(
    r"@{}>{\raggedright}p{3.2cm}>{\raggedright}p{6.2cm}>{\raggedright\arraybackslash}p{5.2cm}@{}",
    r"Settings variants of Lang and Raimundez, computed as in Supplementary Table~\ref{tab:settings} (one setting changed at a time, all others at their baseline values, the same scenarios). Cell: selected subset and median $e_{\mathrm{fit}}$; $=$, the same subset as the baseline; $\times$, not admissible (number of parameters at which the search stopped and its $e_{\mathrm{fit}}$). Not computed: variants that did not finish in the available computing time.",
    "tab:settingsextra", ["Setting", "Lang", "Raimundez"], rows))
