#!/usr/bin/env python3
"""Supplementary Note "Robustness to the size of parameter changes" (suppl_robustness.tex) and
Supplementary Figure figures/figS_robustness_scenarios.pdf.

Data: results/robustness/<problem>.json, written by analysis/robustness.py, which stores for every
perturbation size the error of each of the 15 scenarios and the 15 random directions u(k).

Usage: python make_robustness_note.py            (all admissible problems must be present)
       python make_robustness_note.py --partial  (test with the problems available so far)
"""
import json
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import OUT as HERE, FIG, RESULTS as RES  # noqa: E402

NEW, SEL = RES / "robustness", RES / "selection"
TAU = float(np.sqrt(1 - 0.9 ** 2))
LEVELS = ["1", "5", "10", "20", "30", "40", "50"]
LIN = {"Alkan_SciSignal2018", "Bachmann_MSB2011", "Chen_MSB2009", "Isensee_JCB2018",
       "Lang_PLOSComputBiol2024", "Lucarelli_CellSystems2018", "Raimundez_PCB2020"}
DISPLAY = {"SalazarCavazos": "Salazar-Cavazos"}


def short(p):
    s = p.split("_")[0]
    return DISPLAY.get(s, s)


def tex(s):
    return s.replace("_", r"\_")


def load(partial):
    adm = sorted((f.stem for f in SEL.glob("*.json") if json.loads(f.read_text())["admisible"]), key=str.lower)
    have = {f.stem for f in NEW.glob("*.json")}
    missing = [p for p in adm if p not in have]
    if missing and not partial:
        sys.exit(f"missing per-scenario results for {len(missing)} problems: {', '.join(missing)}")
    D = {}
    for p in adm:
        if p not in have:
            continue
        d = json.loads((NEW / f"{p}.json").read_text())
        if "error" in d:
            sys.exit(f"{p}: {d['error']}")
        for L in LEVELS:
            a = d["niveles"][L]["eaj_med"]
            e = np.array(d["niveles"][L]["eaj"], float)
            assert len(e) == d["niveles"][L]["n"]          # stored scenarios and summaries are consistent
            assert abs(np.median(e) - a) < 1e-12 if len(e) else True
        D[p] = d
    return adm, D, missing


def stats(e):
    e = np.asarray(e, float)
    if len(e) == 0:
        return None
    q = lambda k: float(np.percentile(e, k))
    return dict(n=len(e), med=q(50), q1=q(25), q3=q(75), p5=q(5), p95=q(95), mx=float(e.max()),
                rate=float(np.mean(e <= TAU)))


def pct(x):
    return "--" if x is None or not np.isfinite(x) else f"{100 * x:.0f}"


def figure(D, order):
    n = len(order)
    ncol = 4
    nrow = int(np.ceil(n / ncol))
    fig, axs = plt.subplots(nrow, ncol, figsize=(7.0, 1.12 * nrow + 0.5), sharex=True)
    axs = np.atleast_2d(axs)
    x = np.array([int(L) for L in LEVELS])
    for ax in axs.ravel():
        ax.set_visible(False)
    for i, p in enumerate(order):
        ax = axs.ravel()[i]; ax.set_visible(True)
        S = [stats(D[p]["niveles"][L]["eaj"]) for L in LEVELS]
        ok = [s is not None for s in S]
        xx = x[ok]; S = [s for s in S if s]
        g = lambda k: 100 * np.array([s[k] for s in S])
        ax.fill_between(xx, g("p5"), g("p95"), color="#cfe0f3", lw=0)
        ax.fill_between(xx, g("q1"), g("q3"), color="#8fb7e3", lw=0)
        ax.plot(xx, g("med"), color="#1f4e8c", lw=1.1)
        ax.plot(xx, g("mx"), ls="", marker="_", ms=5, color="#c0392b", mew=1.0)
        ax.axhline(100 * TAU, color="k", ls="--", lw=0.6)
        ax.set_xscale("log"); ax.set_xticks([1, 5, 10, 20, 50]); ax.set_xticklabels(["1", "5", "10", "20", "50"], fontsize=5.5)
        top = max(100 * TAU * 1.25, float(g("mx").max()) * 1.08)
        ax.set_ylim(0, min(top, 150)); ax.tick_params(labelsize=5.5, length=2)
        if g("mx").max() > 150:
            ax.text(0.97, 0.94, "max off scale", transform=ax.transAxes, fontsize=4.8, ha="right", va="top", color="#c0392b")
        ax.set_title(f"{short(p)} ({D[p]['patron']})", fontsize=6.5, pad=2)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    fig.supxlabel("Perturbation size $\\pm\\varepsilon$ (%)", fontsize=7, y=0.012)
    fig.supylabel("$e_{\\mathrm{fit}}$ (%)", fontsize=7, x=0.008)
    fig.tight_layout(rect=(0.015, 0.02, 1, 1), h_pad=0.6, w_pad=0.5)
    fig.savefig(FIG / "figS_robustness_scenarios.pdf")
    plt.close(fig)


def main():
    partial = "--partial" in sys.argv
    adm, D, missing = load(partial)
    order = sorted(D, key=lambda p: (D[p]["patron"], short(p).lower()))
    nc = [D["Chen_MSB2009"]["niveles"][L]["n"] for L in LEVELS] if "Chen_MSB2009" in D else [0]
    chen_n = f"{min(nc)} to {max(nc)}"
    figure(D, order)
    Lx = []
    w = Lx.append
    w(r"\snote{robust}")
    w("")
    w(r"This note describes in detail how the robustness of the selected subsets to the size of the parameter changes was assessed "
      r"(Fig.~4 of the main text) and gives, for every admissible problem, the full distribution of the fitting error over the "
      r"random scenarios, not only its median.")
    w("")
    w(r"\subsection*{Random scenarios}")
    w(r"For a problem with $p$ estimated parameters, fifteen random directions $u^{(1)},\dots,u^{(15)}\in[-1,1]^p$ are drawn once, "
      r"with independent components $u^{(k)}_j\sim\mathcal U(-1,1)$, from a pseudo-random generator with fixed seed (NumPy "
      r"\texttt{default\_rng(42)}). For a perturbation size $\varepsilon$, scenario $k$ changes all parameters simultaneously:")
    w(r"\[ \theta^{(k)}(\varepsilon)=\theta_0\odot\bigl(\mathbf 1+\varepsilon\,u^{(k)}\bigr),\qquad "
      r"\theta^{(k)}_j(\varepsilon)=\theta_{0,j}\,\bigl(1+\varepsilon\,u^{(k)}_j\bigr),\quad j=1,\dots,p, \]")
    w(r"so that every parameter is multiplied by a factor between $1-\varepsilon$ and $1+\varepsilon$. The same fifteen directions are "
      r"used at every size $\varepsilon\in\{0.01,0.05,0.10,0.20,0.30,0.40,0.50\}$; only $\varepsilon$ changes (paired design). "
      r"Differences between sizes are therefore due to the size of the change and not to different random draws, and the scenarios "
      r"at $\varepsilon=0.05$ are exactly those used to select the subset. The directions of every problem are stored in the result "
      r"files (\texttt{results/robustness/<problem>.json} of the reproducibility package, key \texttt{u}), and the script checks that "
      r"they are identical at every size.")
    w("")
    w(r"\subsection*{Errors in each scenario}")
    w(r"Let $y(\theta)\in\mathbb R^m$ be the vector of noise-scaled measured outputs (main text, Methods) and $S$ the selected "
      r"biological parameters together with the calibration parameters $\Theta_C$. For scenario $k$,")
    w(r"\[ \Delta y^{(k)}_{\mathrm{full}}=y\bigl(\theta^{(k)}\bigr)-y(\theta_0),\qquad "
      r"\Delta y^{(k)}_{S}=y\bigl(\theta^{(k)}_S\bigr)-y(\theta_0),\qquad "
      r"\bigl(\theta^{(k)}_S\bigr)_j=\begin{cases}\theta^{(k)}_j,& j\in S\\ \theta_{0,j},& j\notin S,\end{cases} \]")
    w(r"that is, $\Delta y_S$ is the output change when only the retained parameters take their scenario values. The error "
      r"without re-estimation and the cosine are")
    w(r"\[ e^{(k)}_{\mathrm{rel}}=\frac{\|\Delta y^{(k)}_{\mathrm{full}}-\Delta y^{(k)}_{S}\|}{\|\Delta y^{(k)}_{\mathrm{full}}\|},\qquad "
      r"\cos\Delta^{(k)}=\frac{\langle\Delta y^{(k)}_{\mathrm{full}},\Delta y^{(k)}_{S}\rangle}{\|\Delta y^{(k)}_{\mathrm{full}}\|\,\|\Delta y^{(k)}_{S}\|}. \]")
    w(r"The error after re-estimation is the smallest relative distance between the reduced model and the output of the full "
      r"model in the scenario, when the retained parameters are free and all others are fixed at $\theta_0$:")
    w(r"\[ e^{(k)}_{\mathrm{fit}}=\min\Bigl\{e^{(k)}_{\mathrm{rel}},\ \min_{v\in B}\frac{\|y(\theta_0[S\leftarrow v])-y(\theta^{(k)})\|}"
      r"{\|\Delta y^{(k)}_{\mathrm{full}}\|}\Bigr\},\qquad B=\prod_{j\in S}\Bigl[\tfrac{|\theta_{0,j}|}{10},\,10\,|\theta_{0,j}|\Bigr], \]")
    w(r"where $\theta_0[S\leftarrow v]$ is $\theta_0$ with the components in $S$ replaced by $v$. The inner minimisation is a "
      r"bounded nonlinear least-squares problem in $\log|v|$ (trust-region reflective method, at most $100(|S|+1)$ function "
      r"evaluations, finite-difference step $10^{-3}$), started from the scenario values (clipped to $B$) and from $\theta_0$; "
      r"the smaller result is kept. Since $v=\theta^{(k)}_S$ is admissible when it lies in $B$, $e_{\mathrm{fit}}\le e_{\mathrm{rel}}$ "
      r"always holds (this is also proved in Lean, step~5). For the problems whose simulations are too slow for repeated nonlinear "
      r"fits (" + ", ".join(sorted(short(p) for p in LIN)) + r"), the first-order version is used,")
    w(r"\[ e^{(k)}_{\mathrm{fit,lin}}=\min\Bigl\{e^{(k)}_{\mathrm{rel}},\ \min_{c\in\mathbb R^{|S|}}\frac{\|\Delta y^{(k)}_{\mathrm{full}}-J_S\,c\|}{\|\Delta y^{(k)}_{\mathrm{full}}\|}\Bigr\}, \]")
    w(r"with $J_S$ the columns of the relative sensitivity matrix for $S$ (central differences, step 1\%); it differs from the "
      r"exact value by a second-order term (Lean, step~12).")
    w(r"A scenario is discarded when the simulation fails or when the full-model change is negligible, "
      r"$\|\Delta y^{(k)}_{\mathrm{full}}\|<\max(10^{-10}\|y(\theta_0)\|,10^{-6})$, because the relative errors are then undefined; "
      r"the number $n\le15$ of valid scenarios is reported for every problem and size. For Chen some simulations fail to "
      r"integrate, so only " + chen_n + r" of the 15 scenarios are valid at each size; which scenarios fail can change slightly "
      r"between runs.")
    w("")
    w(r"\subsection*{Summaries over the scenarios}")
    w(r"For each problem and size $\varepsilon$, with $e^{(1)},\dots,e^{(n)}$ the values of $e_{\mathrm{fit}}$ in the valid scenarios:")
    w(r"\begin{itemize}\itemsep0pt")
    w(r"\item median $\tilde e_{\mathrm{fit}}$, first and third quartiles $Q_1,Q_3$ (interquartile range $Q_3-Q_1$), and the 5th and "
      r"95th percentiles $P_5,P_{95}$, computed by linear interpolation between order statistics (with $n=15$, $P_5$ and $P_{95}$ lie "
      r"between the two smallest and the two largest values);")
    w(r"\item maximum $\max_k e^{(k)}_{\mathrm{fit}}$, the worst scenario;")
    w(r"\item pass rate, the fraction of scenarios in which the reduced model reproduces the full one,")
    w(r"\[ \pi(\varepsilon)=\frac{\#\{k:\ e^{(k)}_{\mathrm{fit}}\le\tau_e\}}{n},\qquad \tau_e=\sqrt{1-0.9^2}=0.436. \]")
    w(r"\end{itemize}")
    w(r"Admissibility at $\pm5\%$ and the robustness patterns of the main text use the median: pattern A, $\tilde e_{\mathrm{fit}}\le\tau_e$ "
      r"at every size; B, admissible up to at least $\pm20\%$ and not beyond; C, irregular (fails and is admissible again at a larger "
      r"size); D, not admissible at $\pm10\%$ or less. The median requires that at least half of the scenarios are reproduced; the pass "
      r"rate and the maximum show how many, and how badly the others fail.")
    w("")
    w(r"\subsection*{Results}")
    if missing:
        w(r"\textit{Per-scenario results are being computed for " + str(len(missing)) + r" problems; this section is generated "
          r"automatically when they are complete.}")
    else:
        rates5 = {p: stats(D[p]["niveles"]["5"]["eaj"])["rate"] for p in order}
        full5 = sum(1 for v in rates5.values() if v == 1.0)
        rates50 = {p: (stats(D[p]["niveles"]["50"]["eaj"]) or {}).get("rate", np.nan) for p in order}
        w(rf"At $\pm5\%$, the size used for selection, all {len(order)} admissible problems reproduce the full model in at least half "
          rf"of the scenarios by construction, and {full5} of them in all scenarios. Supplementary Fig.~\ref{{fig:robscen}} shows, for "
          r"every problem, the median, the interquartile range, the 5--95\% range and the worst scenario at each size; Supplementary "
          r"Table~\ref{tab:passrate} gives the pass rate and Supplementary Table~\ref{tab:robstats} the full summary at $\pm5\%$ and "
          r"$\pm50\%$.")
        w("")
        w(r"\begin{figure}[!htb]\centering")
        w(r"\includegraphics[width=\textwidth]{figures/figS_robustness_scenarios.pdf}")
        w(r"\caption{\textbf{Fitting error over the fifteen scenarios at each perturbation size.} For every admissible problem (pattern in "
          r"parentheses): median $\tilde e_{\mathrm{fit}}$ (line), interquartile range (dark band), 5--95\% range (light band) and worst "
          r"scenario (red marks); dashed line, $\tau_e=43.6\%$. The same fifteen directions are used at every size.}\label{fig:robscen}")
        w(r"\end{figure}")
        w("")
        # pass-rate table
        w(r"{\small")
        w(r"\begin{longtable}{@{}l" + "r" * len(LEVELS) + r"c@{}}")
        w(r"\caption{Pass rate $\pi(\varepsilon)$: percentage of valid scenarios with $e_{\mathrm{fit}}\le\tau_e$, and number of valid "
          r"scenarios when it is below 15 (in parentheses).}\label{tab:passrate}\\")
        hdr = r"Problem & " + " & ".join(rf"$\pm${L}\%" for L in LEVELS) + r" & Pattern \\"
        w(r"\toprule " + hdr + r" \midrule \endfirsthead \toprule " + hdr + r" \midrule \endhead")
        for p in order:
            cells = []
            for L in LEVELS:
                s = stats(D[p]["niveles"][L]["eaj"])
                cells.append("--" if s is None else pct(s["rate"]) + ("" if s["n"] == 15 else f" ({s['n']})"))
            w(tex(short(p)) + " & " + " & ".join(cells) + f" & {D[p]['patron']} \\\\")
        w(r"\bottomrule \end{longtable}}")
        w("")
        # detailed stats table
        w(r"{\small")
        w(r"\begin{longtable}{@{}l" + "rrrrr" * 2 + r"@{}}")
        w(r"\caption{Summary of $e_{\mathrm{fit}}$ (\%) over the scenarios at $\pm5\%$ and $\pm50\%$: median, interquartile range "
          r"$[Q_1,Q_3]$, 5--95\% range $[P_5,P_{95}]$, maximum and pass rate $\pi$.}\label{tab:robstats}\\")
        h1 = r" & \multicolumn{5}{c}{$\pm5\%$} & \multicolumn{5}{c@{}}{$\pm50\%$} \\ \cmidrule(lr){2-6}\cmidrule(l){7-11}"
        h2 = r"Problem & Median & $[Q_1,Q_3]$ & $[P_5,P_{95}]$ & Max & $\pi$ & Median & $[Q_1,Q_3]$ & $[P_5,P_{95}]$ & Max & $\pi$ \\"
        w(r"\toprule" + h1 + h2 + r" \midrule \endfirsthead \toprule" + h1 + h2 + r" \midrule \endhead")
        for p in order:
            row = [tex(short(p))]
            for L in ("5", "50"):
                s = stats(D[p]["niveles"][L]["eaj"])
                if s is None:
                    row += ["--"] * 5
                else:
                    row += [pct(s["med"]), f"[{pct(s['q1'])}, {pct(s['q3'])}]", f"[{pct(s['p5'])}, {pct(s['p95'])}]",
                            pct(s["mx"]), pct(s["rate"])]
            w(" & ".join(row) + r" \\")
        w(r"\bottomrule \end{longtable}}")
    txt = "\n".join(Lx) + "\n"
    (HERE / "suppl_robustness.tex").write_text(txt)
    print(f"suppl_robustness.tex: {len(D)} problems with per-scenario data, {len(missing)} missing")


if __name__ == "__main__":
    main()
