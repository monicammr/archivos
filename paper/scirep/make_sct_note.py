#!/usr/bin/env python3
"""Supplementary Note 6 (the social cognitive theory model, the motivating case of the method) and
Supplementary Figure S2, from certificados/resultados/sct_bandura/datos_reales_modelo22.json and the model
of certificados/sct_modelo22.py. The validation refits are recomputed here (same procedure as
sct_datos22.py) and checked against the stored values."""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
CERT = HERE.parent.parent / "certificados"
sys.path.insert(0, str(CERT))
import sct_modelo22 as M  # noqa: E402

D = json.loads((CERT / "resultados" / "sct_bandura" / "datos_reales_modelo22.json").read_text(encoding="utf-8"))
th0 = np.array([D["theta0"][n] for n in M.NAMES])
P, N, NTR = len(th0), M.N, 24
LO = np.array([b[0] for b in M.BOUNDS]); HI = np.array([b[1] for b in M.BOUNDS])
sigma = D["sigma"]
tr, te = np.arange(NTR), np.arange(NTR, N)
S = [M.NAMES.index(q) for q in D["S"]]


def refit(free):
    def res(v):
        t = th0.copy(); t[free] = v
        if not M.estable(t):
            return np.full(len(tr), 1e3)
        return (M.sim(t)[tr] - M.Y[tr]) / sigma
    r = least_squares(res, np.clip(th0[free], LO[free], HI[free]), bounds=(LO[free], HI[free] + 1e-12),
                      method="trf", max_nfev=200 * (len(free) + 1), x_scale="jac")
    t = th0.copy(); t[free] = r.x
    return t


chi = lambda th, idx: float(np.mean(((M.sim(th)[idx] - M.Y[idx]) / sigma) ** 2))
th_r, th_f = refit(S), refit(list(range(P)))
V = D["validacion"]
assert abs(chi(th_r, te) - V["chi2_test_red"]) < 1e-6 * V["chi2_test_red"], (chi(th_r, te), V["chi2_test_red"])
assert abs(chi(th_f, te) - V["chi2_test_full"]) < 1e-6 * V["chi2_test_full"], (chi(th_f, te), V["chi2_test_full"])

# relative sensitivity energy and R_var of the selected subset
J = np.zeros((N, P))
for j in range(P):
    tp, tm = th0.copy(), th0.copy(); tp[j] *= 1.01; tm[j] *= 0.99
    J[:, j] = (M.sim(tp) - M.sim(tm)) / 0.02
E = (J ** 2).sum(0); share = E / E.sum(); rvar = float(share[S].sum())
cos5, ef5 = D["cos_med"], D["eajuste_med"]
level = 1 + (cos5 >= 0.9) + (cos5 >= 0.9 and rvar >= 0.89)

# ---------------- Figure S2
days = np.arange(1, N + 1)
fig, ax = plt.subplots(figsize=(7.0, 3.2))
ax.axvspan(NTR + 0.5, N + 0.5, color="0.92", lw=0)
ax.plot(days, M.Y, "o", ms=3.5, color="black", label="data (standardised daily steps)")
ax.plot(days, M.sim(th0), "-", color="0.55", lw=1.2, label=r"$\theta_0$ (all 31 days)")
ax.plot(days, M.sim(th_r), "-", color="#1f77b4", lw=1.6, label=r"reduced model, 2 parameters (days 1–24)")
ax.plot(days, M.sim(th_f), "--", color="#d62728", lw=1.2, label=r"full model, 22 parameters (days 1–24)")
ax.text(N + 0.3, ax.get_ylim()[0] + 0.1, "test days", fontsize=8, color="0.3", ha="right")
ax.set_xlabel("day"); ax.set_ylabel("behaviour $x_4$ (z-score)")
ax.legend(fontsize=7, frameon=False, ncol=2, loc="lower center", bbox_to_anchor=(0.5, 1.02))
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
(HERE / "figures").mkdir(exist_ok=True)
fig.savefig(HERE / "figures" / "figS2_sct.pdf")

# ---------------- LaTeX
G = {"beta": r"\beta", "gamma": r"\gamma", "tau": r"\tau"}
sym = lambda n: next(f"${v}_{{{n[len(k):]}}}$" for k, v in G.items() if n.startswith(k))
disp = D["DE_100"]["dispersion_R2_ge_0.87"]
nsign = sum(1 for n in M.NAMES if disp[n]["cambia_signo"])
r2 = D["DE_100"]["R2"]
f3 = lambda x: f"{x:.3g}" if abs(x) >= 1e-3 else f"{x:.1e}"
L = [r"\section*{Supplementary Note 6. The social cognitive theory model: the motivating case}", "",
     r"The method was conceived while estimating a dynamical model of Bandura's social cognitive theory (SCT) of "
     r"physical activity from the daily records of one participant (Miranda et al., 2025 IEEE Ecuador Technical Chapters Meeting, "
     r"doi:10.1109/ETCM67548.2025.11304524; cited in the main text). This note documents that case. It is "
     r"not part of the PEtab benchmark (it is not an SBML/PEtab problem and its data are not public), it is not "
     r"counted in any benchmark statistic, and its model was not translated into Lean; it is reported because it "
     r"shows, on a small model with real data, the problem that the method addresses.", "",
     r"\subsection*{Model and data}",
     r"Six psychosocial constructs $x_1,\dots,x_6$, of which $x_4$ is behaviour (daily steps), evolve as a linear system "
     r"$\tau_i\dot x_i=-x_i+\sum_j\beta_{ij}x_j+\sum_k\gamma_{ik}u_k$, i.e.\ $\dot x=A(\theta)x+B(\theta)u$, $y=x_4$, "
     r"with ten couplings $\beta_{14},\beta_{21},\beta_{25},\beta_{31},\beta_{34},\beta_{42},\beta_{43},\beta_{45},"
     r"\beta_{46},\beta_{54}$, six input gains $\gamma_{33},\gamma_{35},\gamma_{36},\gamma_{57},\gamma_{64},\gamma_{68}$ "
     r"($\gamma_{35}$ with negative sign) and six time constants $\tau_1,\dots,\tau_6$: 22 parameters. The data are 31 "
     r"days of six measured inputs and daily steps, each standardised (z-score). The model is simulated from $x(0)=0$ "
     r"with inputs held constant over each day (exact discretisation with the matrix exponential), and the output of "
     r"day $k$ is $x_4$ at the end of that day. Bounds are $\beta\in[-1.5,1.5]$, $\gamma\in[0,3]$, $\tau\in[0.3,12]$, "
     r"and only parameter values with stable dynamics ($\max\operatorname{Re}\lambda(A)\le-10^{-3}$) are admitted.", "",
     r"\subsection*{The problem that motivated the method}",
     r"In that study, differential evolution reached $R^2=86.11\%$, but local refinement from that "
     r"estimate with a Levenberg--Marquardt grey-box method reached only 11\% and, after 20 recursive iterations, "
     r"41.17\%: different parameter sets fitted the data with very different quality, and gradient-based refinement "
     r"was unreliable. The estimate used here as $\theta_0$ was obtained with the same differential-evolution "
     r"framework, with stability enforced and couplings of either sign (seed 2026, $R^2=" + f"{D['R2_theta0']:.3f}" + r"$). "
     r"Repeating the search with 100 seeds gave fits of essentially the same quality ($R^2$ between "
     + f"{min(r2):.3f} and {max(r2):.3f}" + r") with very different parameters: " + str(nsign) + r" of the ten couplings "
     r"change sign between runs, and most parameters span almost their whole admissible range (Table~S7). The data "
     r"cannot separate the parameters, and fitting all 22 of them is ill-posed. Deciding which few parameters the "
     r"data can inform, before fitting, is the question that the method answers.", "",
     r"{\small", r"\begin{longtable}{@{}lrrrrc@{}}",
     r"\caption*{\textbf{Supplementary Table S7.} Parameters of the SCT model: value at $\theta_0$, range over the 100 "
     r"differential-evolution runs (all with $R^2\ge0.87$), sign change between runs, and share of the sensitivity "
     r"energy $E_j/\sum_kE_k$ of behaviour at $\theta_0$.}\\",
     r"\toprule", r"Parameter & $\theta_0$ & min & max & Energy share & Sign change \\", r"\midrule", r"\endhead"]
for j, n in enumerate(M.NAMES):
    L.append(f"{sym(n)} & {f3(th0[j])} & {f3(disp[n]['min'])} & {f3(disp[n]['max'])} & {100 * share[j]:.1f}\\% & "
             f"{'yes' if disp[n]['cambia_signo'] else '--'} \\\\")
pairs = D["pares_cos_ge_0.95"]
pr = ", ".join(f"{sym(p['a'])}--{sym(p['b'])} ({p['cos']:.3f})" for p in pairs[:4])
L += [r"\bottomrule", r"\end{longtable}", "}", "",
      r"\subsection*{What the method finds}",
      r"\textbf{Collinearity.} The sensitivity matrix of behaviour at $\theta_0$ is exactly rank-deficient (infinite "
      r"condition number, largest VIF $" + f"{D['VIF_activos']:.1e}".replace("e+", r"\times10^{") + r"}$), and "
      + str(len(pairs)) + r" pairs of parameters have sensitivity vectors with cosine $\ge0.95$, for example " + pr + r".", "",
      r"\textbf{Selection.} Stage~1 reached $R_{\mathrm{var}}=" + f"{D['Rvar_S1_%']:.0f}" + r"\%$ with "
      + str(len(D["S1"])) + r" parameters, below the threshold of 89\% because the remaining candidates failed the conditioning test; "
      r"stage~2 selected two parameters, $\gamma_{57}$ and $\beta_{45}$ (condition number "
      + f"{D['kappa']:.1f}" + r", VIF " + f"{D['VIF']:.1f}" + r"), which form the path from the external input "
      r"through construct $x_5$ to behaviour and together carry " + f"{100 * rvar:.0f}" + r"\% of the sensitivity "
      r"energy. The conditioning test rejected redundant candidates such as $\tau_4$ and $\tau_5$, strongly "
      r"collinear with $\beta_{45}$ (cosine about 0.8). Backward elimination removed nothing.", "",
      r"\textbf{Admissibility and robustness.} Re-estimating only these two parameters reproduces the output of the "
      r"full model with a median $e_{\mathrm{fit}}$ of " + f"{100 * ef5:.1f}" + r"\% at $\pm5\%$, and between "
      + f"{100 * min(v['eaj_med'] for v in D['niveles'].values()):.1f}" + r"\% and "
      + f"{100 * max(v['eaj_med'] for v in D['niveles'].values()):.1f}" + r"\% for perturbations up to $\pm50\%$ "
      r"(pattern " + D["patron"] + r"). The median $\cos\Delta$ is " + f"{cos5:.2f}" + r" and $R_{\mathrm{var}}="
      + f"{rvar:.2f}" + r"$, so the subset reaches level " + str(level) + r" of the guarantees defined in "
      r"Supplementary Table~S1.", "",
      r"\textbf{Prediction of unseen days.} Both models were refitted to days 1--24 (by least squares from $\theta_0$, "
      r"within the bounds and with the stability constraint) and used to predict days 25--31 (Figure~S2). The reduced "
      r"model predicted the held-out week with $R^2=" + f"{V['R2_test_red']:.2f}" + r"$ (test $\chi^2/n$ "
      + f"{V['chi2_test_red']:.2f}" + r"), better than the full 22-parameter model ($R^2=" + f"{V['R2_test_full']:.2f}"
      + r"$, $\chi^2/n$ " + f"{V['chi2_test_full']:.2f}" + r"; refitted with the same differential-evolution search: "
      r"$R^2=" + f"{V['R2_test_full_DE']:.2f}" + r"$, $\chi^2/n$ " + f"{V['chi2_test_full_DE']:.2f}" + r"), even though "
      r"the full model fits the training days more closely ($\chi^2/n$ " + f"{V['chi2_train_full']:.2f}" + r" versus "
      + f"{V['chi2_train_red']:.2f}" + r"). All refitted models are stable.", "",
      r"\begin{figure}[!htb]", r"\centering", r"\includegraphics[width=\textwidth]{figures/figS2_sct.pdf}",
      r"\caption*{\textbf{Supplementary Figure S2. SCT model of one participant.} Standardised daily steps (dots), "
      r"the fit of $\theta_0$ to all 31 days (grey), and the reduced (two parameters, blue) and full (22 parameters, "
      r"red dashed) models refitted to days 1--24; the shaded region contains the seven test days.}",
      r"\end{figure}", "",
      r"\subsection*{Relation with the formal results}",
      r"The SCT model is linear with constant inputs on each day, so its vector field is globally Lipschitz and the "
      r"existence and differentiability results of Part~II of Supplementary Note~2 apply directly; the model was not "
      r"translated into Lean, so this is a mathematical observation rather than a machine-checked statement. The "
      r"model shows on a small, transparent example the situation that the method is designed for: a good fit of the "
      r"data, parameters that the data cannot determine, and a reduced set of two parameters that reproduces and "
      r"predicts the measured behaviour.", ""]
out = HERE / "suppl_sct.tex"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print("SCT note written; level", level, "Rvar", round(rvar, 3), "pairs", len(pairs))
