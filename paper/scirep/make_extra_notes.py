#!/usr/bin/env python3
"""Supplementary Notes on the numerical analyses cited in the main text, generated from the result files:

  suppl_simulator.tex  Verification of the simulator          (certificados/resultados/salidas/VERIFICACION_SIMULADOR.md)
  suppl_synthetic.tex  Synthetic prediction experiment        (certificados/resultados/validacion_externa_bio/*.json, B_*)
  suppl_single.tex     Single-parameter subsets               (certificados/resultados/un_parametro_final/*.json)
  suppl_settings.tex   Sensitivity to the method settings     (certificados/resultados/reclasificacion_salidas_bio_poda_<tag>/)
  suppl_cost.tex       Computational cost                     (certificados/resultados/costo/tiempos_simulacion.json)

A note whose data are incomplete states so instead of showing partial numbers. Counts quoted in the main text
are printed so that they can be compared.
Usage: python3 make_extra_notes.py
"""
import json
import math
import re
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
RES = HERE.parent.parent / "certificados" / "resultados"
TAU = math.sqrt(1 - 0.9 ** 2)
DISPLAY = {"SalazarCavazos": "Salazar-Cavazos"}


def short(p):
    s = p.split("_")[0]
    return DISPLAY.get(s, s)


def tex(s):
    return s.replace("_", r"\_")


def ldir(d):
    return {f.stem: json.loads(f.read_text()) for f in sorted((RES / d).glob("*.json"))} if (RES / d).exists() else {}


SEL = ldir("reclasificacion_salidas_bio_poda")
ADM = sorted((p for p, d in SEL.items() if d["admisible"]), key=str.lower)
VAL = ldir("validacion_externa_bio")
PAT = ldir("patrones")


def num(x, d=2):
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "--"
    if abs(x) >= 1e4:
        m, e = f"{x:.1e}".split("e")
        return f"${m}\\times10^{{{int(e)}}}$"
    if abs(x) >= 100:
        return f"{x:,.0f}"
    if abs(x) < 0.01 and x != 0:
        m, e = f"{x:.1e}".split("e")
        return f"${m}\\times10^{{{int(e)}}}$"
    return f"{x:.{d}f}"


# ------------------------------------------------------------------ simulator
NOTE_EN = {
    "Blasi_CellSystems2016": "reference file has 288 rows for 252 measurements",
    "Crauste_CellSystems2017": "median difference below 1\\% (very stiff model)",
    "Fujita_SciSignal2010": "reference uses other condition identifiers",
    "Isensee_JCB2018": "reference uses other condition identifiers",
    "Raia_CancerResearch2011": "reference uses other condition identifiers",
    "Lang_PLOSComputBiol2024": "oscillator simulated to $t=136{,}472$: medians agree, peaks differ by an accumulated phase shift",
    "Okuonghae_ChaosSolitonsFractals2020": "no reference file in the benchmark",
    "Oliveira_NatCommun2021": "no reference file in the benchmark",
    "Perelson_Science1996": "discrepancy; the initial state is stationary ($\\dot V(0)=0$) and our simulation respects it, so the reference was probably generated with other values",
    "Sneyd_PNAS2002": "median exact; the maximum comes from duplicated rows at the same time",
    "Zhao_QuantBiol2020": "reference file has 169 rows",
    "Zheng_PNAS2012": "reference file contains the measured data, not a simulation",
}


def simulator():
    rows = []
    for line in (RES / "salidas" / "VERIFICACION_SIMULADOR.md").read_text().splitlines():
        c = [x.strip() for x in line.split("|")]
        if len(c) > 9 and c[1].endswith(tuple("0123456789")) and "_" in c[1]:
            rows.append(c[1:9])
    assert len(rows) == 34, len(rows)
    L = [r"\snote{sim}", "",
         r"Our simulation of the measured outputs (\texttt{certificados/petab\_outputs.py}, libRoadRunner with CVODE, relative and absolute "
         r"tolerances $10^{-7}$ and $10^{-10}$) was compared, at the nominal parameters $\theta_0$, with the reference simulations "
         r"distributed with the benchmark (file \texttt{simulations.tsv} of each problem), matching every measurement by observable, "
         r"experimental condition and time. For measurement $i$ the relative difference is $|\hat y_i-y^{\mathrm{ref}}_i|/\max(|y^{\mathrm{ref}}_i|,10^{-12})$; "
         r"Supplementary Table~\ref{tab:simulator} gives its median and maximum for every problem.", "",
         r"In all problems with a comparable reference the median difference is below $10^{-5}$ except Chen ($1.1\times10^{-4}$), "
         r"Crauste (0.8\%, a very stiff model), Lang, Perelson and Zheng. In Lang, an oscillating cell-cycle model simulated to $t=136{,}472$, "
         r"the median difference is 2.8\% and the peaks differ by an accumulated phase shift. In Perelson the difference is 17\%; the "
         r"initial state of the SBML model is stationary and our simulation respects it, so the discrepancy most likely lies in the "
         r"reference. In Zheng the reference file contains the measured data rather than a simulation. Lang and Perelson were kept in the "
         r"analysis, and their results should be read with this caveat. Problems without a comparable reference have no file in the "
         r"benchmark or use different condition identifiers.", "",
         r"{\small",
         r"\begin{longtable}{@{}>{\raggedright\arraybackslash}p{2.6cm}rrrrrr>{\raggedright\arraybackslash}p{5.3cm}@{}}",
         r"\caption{Agreement of our simulation of the measured outputs with the reference simulations of the benchmark at $\theta_0$: "
         r"number of measurements and conditions, estimated parameters $p$ and those that affect the outputs, and median and maximum "
         r"relative difference.}\label{tab:simulator}\\",
         r"\toprule Problem & Meas. & Cond. & $p$ & $p_y$ & Median & Max & Note \\ \midrule \endfirsthead",
         r"\toprule Problem & Meas. & Cond. & $p$ & $p_y$ & Median & Max & Note \\ \midrule \endhead"]
    for c in rows:
        sci = lambda v: "--" if not v else (r"$0$" if float(v) == 0 else
                                             "${:.1f}\\times10^{{{}}}$".format(float(v.split("e")[0]), int(v.split("e")[1])))
        L.append(f"{tex(short(c[0]))} & {c[1]} & {c[2]} & {c[3]} & {c[4]} & {sci(c[5])} & {sci(c[6])} & "
                 f"{NOTE_EN.get(c[0], 'agrees')} \\\\")
    L += [r"\bottomrule \end{longtable}}", "",
          r"Froehlich is not included: its 9,169 experimental conditions, each requiring a simulation of a model with 1,228 species, "
          r"made the analysis of its measured outputs infeasible with the resources available (Supplementary Note~\emph{Computational cost}).", ""]
    (HERE / "suppl_simulator.tex").write_text("\n".join(L) + "\n")


# ------------------------------------------------------------------ synthetic experiment
def synthetic():
    R = []
    for p in ADM:
        v = VAL.get(p, {})
        R.append(dict(p=p, t0=v.get("B_chi2_test_theta0"), red=v.get("B_chi2_test_red"), full=v.get("B_chi2_test_full"),
                      er=v.get("B_epred_red"), ef=v.get("B_epred_full"),
                      why=("no training/test split" if v.get("no_evaluable") else
                           "simulation of $\\theta^\\ast$ failed" if v.get("B_error") else "")))
    ev = [r for r in R if r["t0"] is not None]
    low = [r for r in ev if r["t0"] < 2]
    high = [r for r in ev if r["t0"] >= 2]
    low_ok = [r for r in low if r["red"] <= 2]
    hi_ok = [r for r in high if r["er"] <= TAU]
    comp = [r for r in high if r["ef"] is not None]
    comp_ok = [r for r in comp if r["er"] <= r["ef"]]
    C = dict(evaluable=len(ev), low=len(low), low_ok=len(low_ok), high=len(high), hi_ok=len(hi_ok), comp=len(comp), comp_ok=len(comp_ok))
    L = [r"\snote{synth}", "",
         r"With real data the true parameters are unknown, so the test $\chi^2/n$ of Figure~3 measures agreement with noisy data, not "
         r"with the true response. To measure the prediction error itself we repeated the external validation with synthetic data "
         r"generated from a known truth.", "",
         r"\subsection*{Design}",
         r"\begin{enumerate}\itemsep0pt",
         r"\item \emph{Truth.} With a fixed seed (NumPy \texttt{default\_rng(42)}) a vector $u\in[-1,1]^p$ with components $u_j\sim\mathcal U(-1,1)$ "
         r"is drawn and $\theta^\ast_j=\theta_{0,j}(1+0.2\,u_j)$ for every parameter that can be estimated from the training data "
         r"(parameters acting only in test conditions stay at $\theta_{0,j}$, since no method could learn them).",
         r"\item \emph{Data.} $\tilde y_i=y_i(\theta^\ast)+\epsilon_i$ with $\epsilon_i\sim\mathcal N(0,1)$ in noise-scaled units, i.e.\ Gaussian noise "
         r"with the standard deviation $\sigma_i$ recorded in the benchmark, for every measurement of every condition.",
         r"\item \emph{Split and fits.} The same training/test split as for the real data (main text, Methods). The reduced model "
         r"(re-estimating $S\cup\Theta_C$) and the full model (re-estimating all parameters, except for Chen and Lang) are fitted to the "
         r"synthetic training data starting from $\theta_0$, with the same least-squares method and bounds.",
         r"\item \emph{Prediction error.} On the test measurements,",
         r"\[ e_{\mathrm{pred}}=\frac{\|y_{\mathrm{test}}(\hat\theta)-y_{\mathrm{test}}(\theta^\ast)\|}{\|y_{\mathrm{test}}(\theta^\ast)-y_{\mathrm{test}}(\theta_0)\|}, \]",
         r"the error of the prediction relative to the change of the true response; $e_{\mathrm{pred}}=1$ for the published estimate $\theta_0$, "
         r"and $e_{\mathrm{pred}}\le\tau_e=0.436$ is used as the success criterion.",
         r"\item \emph{Signal and noise.} When the change from $\theta_0$ to $\theta^\ast$ moves the test outputs less than the noise, "
         r"$e_{\mathrm{pred}}$ measures only noise. The signal is considered larger than the noise when the test $\chi^2/n$ of $\theta_0$ on "
         r"the synthetic data is at least 2.",
         r"\end{enumerate}", "",
         r"\subsection*{Results}",
         rf"The experiment could be evaluated in {C['evaluable']} of the {len(ADM)} admissible problems (Bertozzi and Blasi have no "
         r"training/test split; for Isensee the simulation of $\theta^\ast$ failed). "
         rf"In {C['low']} problems the signal was below the noise; in {C['low_ok']} of these the reduced model predicted at the noise level "
         r"(test $\chi^2/n\le2$). "
         rf"In the {C['high']} problems where the signal exceeded the noise, the reduced model reached $e_{{\mathrm{{pred}}}}\le\tau_e$ in "
         rf"{C['hi_ok']}, and its $e_{{\mathrm{{pred}}}}$ was no larger than that of the full model in {C['comp_ok']} of the {C['comp']} "
         r"problems where the full model was also fitted (Supplementary Table~\ref{tab:synthetic}).", "",
         r"{\small",
         r"\begin{longtable}{@{}lrrrrrc@{}}",
         r"\caption{Synthetic prediction experiment: test $\chi^2/n$ of $\theta_0$ (signal-to-noise indicator), of the reduced and of the "
         r"full model, and prediction error $e_{\mathrm{pred}}$ of the reduced and full models. Signal, test $\chi^2/n$ of $\theta_0\ge2$.}\label{tab:synthetic}\\",
         r"\toprule & \multicolumn{3}{c}{Test $\chi^2/n$} & \multicolumn{2}{c}{$e_{\mathrm{pred}}$} & \\ \cmidrule(lr){2-4}\cmidrule(lr){5-6}",
         r"Problem & $\theta_0$ & Reduced & Full & Reduced & Full & Signal \\ \midrule \endfirsthead",
         r"\toprule Problem & $\theta_0$ & Reduced & Full & Reduced & Full & Signal \\ \midrule \endhead"]
    for r in sorted(R, key=lambda r: (r["t0"] is None, not (r["t0"] or 0) >= 2, short(r["p"]).lower())):
        if r["t0"] is None:
            L.append(f"{tex(short(r['p']))} & \\multicolumn{{6}}{{l}}{{\\textit{{not evaluable: {r['why']}}}}} \\\\")
            continue
        L.append(f"{tex(short(r['p']))} & {num(r['t0'])} & {num(r['red'])} & {num(r['full'])} & {num(r['er'])} & {num(r['ef'])} & "
                 f"{'yes' if r['t0'] >= 2 else 'no'} \\\\")
    L += [r"\bottomrule \end{longtable}}", ""]
    (HERE / "suppl_synthetic.tex").write_text("\n".join(L) + "\n")
    return C


# ------------------------------------------------------------------ single-parameter subsets
SLOW = {"Bachmann_MSB2011", "Chen_MSB2009", "Isensee_JCB2018", "Lang_PLOSComputBiol2024", "Raimundez_PCB2020"}


def single():
    U = ldir("un_parametro_final")
    want = [p for p in ADM if p not in SLOW]
    missing = [p for p in want if p not in U]
    L = [r"\snote{single}", "",
         r"The method requires at least $k_{\min}=2$ biological parameters. This note examines whether a single parameter could suffice.", "",
         r"\subsection*{Design}",
         r"For every admissible problem the candidates are the ten biological parameters with the largest sensitivity energy $E_j$ and the "
         r"ten with the largest finite effect $s_j$ (the two orderings of the method). Each candidate $j$ is tested alone, with the "
         r"calibration parameters $\Theta_C$ re-estimated together with it as in the method: $\{j\}$ is admissible if the median $e_{\mathrm{fit}}$ "
         r"over the same 15 scenarios at $\pm5\%$ is at most $\tau_e$ (without the requirement $|S|\ge2$). For the best admissible "
         r"candidate $j^\ast$ (smallest median $e_{\mathrm{fit}}$) we also computed the median $e_{\mathrm{fit}}$ at $\pm10\%$ and its "
         r"external validation, real and synthetic, exactly as for the selected subset $S$ (Supplementary Note~\emph{Synthetic prediction "
         r"experiment}). " + ", ".join(sorted(short(p) for p in SLOW)) + r" were not included because the repeated nonlinear "
         r"re-estimations are too slow.", "",
         r"\subsection*{Results}"]
    C = {}
    if missing:
        L.append(r"\textit{Being computed for " + str(len(missing)) + r" problems; this section is generated automatically when complete.}")
    else:
        rows = [U[p] for p in want]
        ok = [r for r in rows if r.get("algun_parametro_solo_basta")]
        cmp_, Sbetter = [], []
        for r in ok:
            v = r.get("mejor_validacion", {})
            ej, es = v.get("B_epred_red"), VAL.get(r["sistema"], {}).get("B_epred_red")
            if ej is not None and es is not None and math.isfinite(ej) and math.isfinite(es):
                cmp_.append(r["sistema"])
                if es < ej:
                    Sbetter.append(r["sistema"])
        C = dict(tested=len(rows), ok=len(ok), comp=len(cmp_), Sbetter=len(Sbetter))
        L += [rf"A single parameter was admissible at $\pm5\%$ in {len(ok)} of the {len(rows)} problems examined. In the synthetic prediction "
              rf"experiment the selected subset $S$ predicted better than the best single parameter (smaller $e_{{\mathrm{{pred}}}}$) in "
              rf"{len(Sbetter)} of the {len(cmp_)} problems where both could be evaluated (Supplementary Table~\ref{{tab:single}}), which "
              r"supports the minimum size of two.", "",
              r"{\small",
              r"\begin{longtable}{@{}>{\raggedright\arraybackslash}p{2.2cm}>{\raggedright\arraybackslash}p{3.0cm}rrrrrrr@{}}",
              r"\caption{Problems in which a single biological parameter $j^\ast$ is admissible: median $e_{\mathrm{fit}}$ (\%) at $\pm5\%$ and "
              r"$\pm10\%$, test $\chi^2/n$ on real data and $e_{\mathrm{pred}}$ in the synthetic experiment, for $\{j^\ast\}$ and for the "
              r"selected subset $S$ (both with $\Theta_C$ re-estimated).}\label{tab:single}\\",
              r"\toprule & & \multicolumn{2}{c}{$e_{\mathrm{fit}}$ $\pm5\%$} & \multicolumn{2}{c}{$e_{\mathrm{fit}}$ $\pm10\%$} & "
              r"\multicolumn{2}{c}{Real $\chi^2/n$} & \\ \cmidrule(lr){3-4}\cmidrule(lr){5-6}\cmidrule(lr){7-8}",
              r"Problem & $j^\ast$ & $j^\ast$ & $S$ & $j^\ast$ & $S$ & $j^\ast$ & $S$ & $e_{\mathrm{pred}}$ $j^\ast$ / $S$ \\ \midrule \endfirsthead",
              r"\toprule Problem & $j^\ast$ & \multicolumn{7}{c}{(continued)} \\ \midrule \endhead"]
        for r in ok:
            p = r["sistema"]; j = r["mejor"]; v = r.get("mejor_validacion", {})
            ej5 = next(x["e_fit"] for x in r["un_parametro"] if x["parametro"] == j)
            pct = lambda x: "--" if x is None or not math.isfinite(x) else f"{100 * x:.0f}"
            ej, es = v.get("B_epred_red"), VAL.get(p, {}).get("B_epred_red")
            ep = "not evaluable" if v.get("no_evaluable") else f"{num(ej)} / {num(es)}"
            L.append(f"{tex(short(p))} & \\texttt{{{tex(j)}}} & {pct(ej5)} & {pct(SEL[p]['eajuste_med'])} & {pct(r.get('mejor_efit_10'))} & "
                     f"{pct(r.get('S_efit_10'))} & {num(v.get('A_chi2_test_red'))} & {num(VAL.get(p, {}).get('A_chi2_test_red'))} & {ep} \\\\")
        L += [r"\bottomrule \end{longtable}}", ""]
    (HERE / "suppl_single.tex").write_text("\n".join(L) + "\n")
    return C, missing


# ------------------------------------------------------------------ sensitivity to settings
SETTINGS = [("delta0001", r"$\delta=0.1\%$"), ("delta005", r"$\delta=5\%$"), ("tolfina", r"tolerances $10^{-9}/10^{-12}$"),
            ("tolgruesa", r"tolerances $10^{-6}/10^{-8}$"), ("nivel001", r"perturbation $\pm1\%$"), ("nivel010", r"perturbation $\pm10\%$"),
            ("rvar080", r"$\tau_R=0.80$"), ("rvar085", r"$\tau_R=0.85$"), ("rvar095", r"$\tau_R=0.95$"),
            ("kv5", r"$\tau_\kappa=\tau_{\mathrm{VIF}}=5$"), ("kv30", r"$\tau_\kappa=\tau_{\mathrm{VIF}}=30$"),
            ("emax010", r"$\tau_e=0.10$"), ("emax020", r"$\tau_e=0.20$"), ("emax030", r"$\tau_e=0.30$"), ("emax050", r"$\tau_e=0.50$")]


def settings():
    V = {t: ldir(f"reclasificacion_salidas_bio_poda_{t}") for t, _ in SETTINGS}
    probs = sorted(V["kv5"], key=str.lower)
    missing = [t for t, _ in SETTINGS if sorted(V[t]) != sorted(probs) or any("error" in d for d in V[t].values())]
    excl = sorted(short(p) for p in SEL if p not in probs)
    L = [r"\snote{settings}", "",
         r"The method depends on a finite-difference step $\delta$, the integrator tolerances, the perturbation size used for "
         r"admissibility and four thresholds ($\tau_R$, $\tau_\kappa=\tau_{\mathrm{VIF}}$, $\tau_e$). The complete method (selection, "
         r"admissibility and backward elimination, with the calibration parameters always re-estimated) was re-run changing one setting "
         r"at a time, with all others at their baseline values ($\delta=1\%$, relative/absolute tolerances $10^{-7}/10^{-10}$, "
         r"perturbation $\pm5\%$, $\tau_R=0.89$, $\tau_\kappa=\tau_{\mathrm{VIF}}=10$, $\tau_e=0.436$). "
         rf"The {len(probs)} problems whose complete method could be re-run fifteen times in reasonable time were used; the other "
         rf"{len(excl)} ({', '.join(excl)}) need hours per run. For each setting and problem we record whether the selected subset is "
         r"identical to the baseline and whether the problem is admissible.", ""]
    T = {}
    if missing:
        L.append(r"\textit{Being re-computed with the final method for " + str(len(missing)) + r" settings; this section is generated "
                 r"automatically when complete.}")
    else:
        B = {p: SEL[p] for p in probs}
        L += [r"{\footnotesize",
              r"\begin{longtable}{@{}l" + "c" * len(SETTINGS) + r"@{}}",
              r"\caption{Effect of each setting on every problem: $=$, same subset and admissibility as the baseline; $\neq$, different "
              r"subset (still admissible); $\times$, not admissible; $\circ$, not admissible in the baseline either. Columns in the order of "
              r"Table~2 of the main text.}\label{tab:settings}\\",
              r"\toprule Problem & " + " & ".join(f"\\rotatebox{{90}}{{{lab}}}" for _, lab in SETTINGS) + r" \\ \midrule \endfirsthead",
              r"\toprule Problem & " + " & ".join(f"\\rotatebox{{90}}{{{lab}}}" for _, lab in SETTINGS) + r" \\ \midrule \endhead"]
        for p in probs:
            cells = []
            for t, _ in SETTINGS:
                d = V[t][p]
                if not d["admisible"]:
                    cells.append(r"$\circ$" if not B[p]["admisible"] else r"$\times$")
                elif sorted(d["S"]) == sorted(B[p]["S"]) and B[p]["admisible"]:
                    cells.append("$=$")
                else:
                    cells.append(r"$\neq$")
            L.append(tex(short(p)) + " & " + " & ".join(cells) + r" \\")
        L += [r"\midrule"]
        for t, lab in SETTINGS:
            adm = [p for p in probs if V[t][p]["admisible"]]
            T[t] = dict(adm=len(adm), mean=float(np.mean([len(V[t][p]["S"]) for p in adm])),
                        same=sum(1 for p in probs if sorted(V[t][p]["S"]) == sorted(B[p]["S"])))
        L.append(r"Admissible & " + " & ".join(str(T[t]["adm"]) for t, _ in SETTINGS) + r" \\")
        L.append(r"Same $S$ & " + " & ".join(str(T[t]["same"]) for t, _ in SETTINGS) + r" \\")
        L += [r"\bottomrule \end{longtable}}", ""]
    (HERE / "suppl_settings.tex").write_text("\n".join(L) + "\n")
    return T, missing


# ------------------------------------------------------------------ computational cost
def cost():
    c = json.loads((RES / "costo" / "tiempos_simulacion.json").read_text())
    rows = sorted(c.items(), key=lambda kv: kv[1]["p"])
    L = [r"\snote{cost}", "",
         r"The dominant cost of the selection is the number of model simulations: the relative sensitivity matrix $J$ by central "
         r"differences needs $2p$ simulations and the stage-2 ordering by finite effects $p$ more, $3p$ in total; all of them are "
         r"independent and can run in parallel. The greedy selection, the conditioning tests, backward elimination and the first-order "
         r"$e_{\mathrm{fit}}$ use only $J$ (linear algebra, negligible in comparison). The admissibility test adds, for each candidate "
         r"subset, 15 scenario simulations and the re-estimations, whose cost depends on the number of retained parameters rather than "
         r"on $p$. Supplementary Table~\ref{tab:cost} gives the measured time of one simulation of all measured outputs (all experimental "
         r"conditions) at $\theta_0$ and the resulting time for the $3p$ simulations, in series and on four cores, for the problems timed.", "",
         r"{\small",
         r"\begin{longtable}{@{}lrlrrrr@{}}",
         r"\caption{Computational cost of the sensitivity computations: estimated parameters $p$, outputs used, time of one simulation, "
         r"number of simulations for $J$ and the stage-2 ordering ($3p$), and total time in series and on four cores.}\label{tab:cost}\\",
         r"\toprule Problem & $p$ & Outputs & $t_{\mathrm{sim}}$ (s) & $3p$ & Series & 4 cores \\ \midrule \endfirsthead",
         r"\toprule Problem & $p$ & Outputs & $t_{\mathrm{sim}}$ (s) & $3p$ & Series & 4 cores \\ \midrule \endhead"]
    fmt = lambda s: f"{s:.0f} s" if s < 90 else (f"{s / 60:.0f} min" if s < 5400 else f"{s / 3600:.1f} h")
    four = {}
    for p, d in rows:
        n = 3 * d["p"]; tot = n * d["t_sim"]; four[p] = tot / 4
        L.append(f"{tex(short(p))} & {d['p']:,} & {'measured' if d['modo'] == 'salidas' else 'states'} & "
                 f"{d['t_sim']:.3g} & {n:,} & {fmt(tot)} & {fmt(tot / 4)} \\\\")
    L += [r"\bottomrule \end{longtable}}", "",
          r"For Froehlich (4,231 parameters, 1,228 species) the analysis was carried out on the state trajectories; on its measured "
          r"outputs each evaluation requires about 9,000 simulations (one per experimental condition), which was infeasible with the "
          r"resources available.", ""]
    (HERE / "suppl_cost.tex").write_text("\n".join(L) + "\n")
    slow = sorted(short(p) for p, t in four.items() if t >= 40 and c[p]["modo"] == "salidas")
    return dict(timed=sum(1 for p in c if c[p]["modo"] == "salidas"), over40=slow)


if __name__ == "__main__":
    simulator()
    Cs = synthetic(); print("synthetic:", Cs, "(main text: 15, 13, 13 signal, 8 e_pred<=tau, 6 of 11)")
    Cu, mu = single(); print("single:", Cu, "missing", len(mu), "(main text: ten problems; six of nine)")
    Ts, ms = settings(); print("settings: missing", ms)
    for t, v in Ts.items():
        print(f"   {t:10s} adm {v['adm']} mean|S| {v['mean']:.2f} same {v['same']}")
    print("cost:", cost())
