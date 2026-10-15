#!/usr/bin/env python3
"""Supplementary Table S3 (formal proofs): one row per Lean module of lean_proofs/, with the number of
theorems and lemmas counted by lean_proofs/catalogo.py. Written to tables/tableS3.tex."""
import importlib.util

from common import TAB, LEAN
spec = importlib.util.spec_from_file_location("cat", LEAN / "catalogo.py")
cat = importlib.util.module_from_spec(spec); spec.loader.exec_module(cat)
cnt = {p.stem: len(cat.decls(p)) for p in cat.TEORIA}

G = [
    ("Sensitivity energy and trajectory error", [
        ("FirstOrderErrorBound", r"Energy $E_j=(J^\top J)_{jj}$, $R_{\mathrm{var}}$ and first-order output error when parameters are fixed", r"total\_eq\_kept\_add\_removed, first\_order\_error\_from\_Rvar"),
        ("TrajectoryErrorBound", r"From the Jacobian to the trajectory: error bound when discarded parameters are fixed", r"sqrt\_removedParamSq\_le"),
        ("CertifiedODEReduction", r"Local certificate: $R_{\mathrm{var}}(S)\ge r$ bounds the trajectory error of the reduced model", r"certified\_parameter\_reduction")]),
    ("Differential equations: existence and sensitivities", [
        ("GlobalLipschitzODE", r"Global existence on $[a,b]$ for globally Lipschitz vector fields", None),
        ("ParamDiffODE", r"Solutions depend differentiably on parameters and initial values; the derivative solves the variational equation", r"hasFDerivAt\_solution\_param\_init"),
        ("LocalExistence", r"Solutions exist for parameters near $\theta_0$ when the nominal solution exists", None),
        ("SensitivityLipschitz", r"Explicit Lipschitz constants of trajectories and sensitivities in $\theta$ (Gr\"onwall)", r"sens\_lipschitz, traj\_lipschitz")]),
    ("Finite perturbations and cosine certificates", [
        ("CosineCertificate", r"Non-asymptotic bounds for finite perturbations; per-scenario certificate of $\cos\Delta$", r"finite\_trajectory\_error, finite\_cos\_certificate"),
        ("CertifiedFiniteODE", r"Certificate of $\cos\Delta$ for the ODE with an explicitly bounded Lipschitz constant", r"certified\_cos\_ode"),
        ("ExactLinearCertificate", r"Certificates with the exact linear error; local version without Lipschitz constants", r"finite\_cos\_certificate\_exact, certified\_cos\_ode\_exact"),
        ("NominalCertificate", r"Local $\cos\Delta$ certificate from the nominal trajectory only", None),
        ("ScaledError", r"Theorem 1: the minimum relative error after rescaling equals $\sqrt{1-\cos^2\Delta}$", r"min\_rel\_error\_eq")]),
    ("Selection, conditioning and identifiability", [
        ("GreedySelection", r"Greedy selection returns a subset with $\kappa\le\tau_\kappa$ and $\mathrm{VIF}\le\tau_{\mathrm{VIF}}$; permanent discard is correct", r"greedy\_kappa\_vif\_guarantee"),
        ("IdentifiabilityConditioning", r"$\kappa$ and VIF bounds imply unique and stable least-squares estimates", r"ls\_unique, ls\_param\_kappa\_stability, ls\_vif\_inverse\_stability"),
        ("SpectralConditioning", r"$\kappa$ and VIF exactly as computed numerically (spectral theorem, matrix inverse)", None),
        ("NumericalRobustness", r"Finite-difference error; $R_{\mathrm{var}}$, $\kappa$ and VIF certified from approximate values with margins", r"fd\_column\_error, rvar\_certified\_from\_approx"),
        ("PatternMechanisms", r"Opposing effects imply rejection by $\kappa$ and non-identifiability; zero discarded energy implies exact first-order reduction", r"not\_okKappa\_of\_kernel, exact\_reduction\_of\_zero\_energy"),
        ("ProfileIdentifiability", r"Practical identifiability of the reduced problem: if the guaranteed half-width $t^{\ast}$ from the profiled information is smaller than the distance to the bounds, the profile likelihood exceeds the threshold on both sides", r"practically\_identifiable\_grad, tstar\_linear, local\_injective")]),
    ("Re-estimation, minimality and measured outputs", [
        ("RefitMonotone", r"Re-estimating more parameters never increases the fitting error; $e_{\mathrm{fit}}\le e_{\mathrm{rel}}$", r"fitErr\_anti, fitErr\_le\_erel, admissible\_mono"),
        ("Poda", r"Theorem 2: backward elimination returns an admissible subset from which no parameter can be removed; inclusion-minimal for a monotone criterion", r"prune\_spec, prune\_inclusion\_minimal"),
        ("OutputComposition", r"Error bounds transfer from states to measured outputs, including $\log$ and $\log_{10}$", r"output\_uniform\_bound, log10\_lipschitz"),
        ("LinearizedFit", r"The first-order $e_{\mathrm{fit}}$ differs from the exact one by a second-order term", r"lin\_le\_scaled, fit\_lower\_of\_lin")]),
    ("Model assumptions for kinetic models", [
        ("KineticRegularity", r"Rate laws (mass action, Michaelis--Menten, Hill, \dots) define smooth vector fields on their domain", None),
        ("EventSystems", r"Systems with events at fixed times: existence and differentiability across segments", None),
        ("PositivityInvariance", r"Quasi-positive models keep concentrations non-negative", None),
        ("KineticCheck", r"Verified automatic checkers for translated rate laws", None),
        ("GlobalExistence", r"Global existence under linear growth on the non-negative orthant", None),
        ("KineticNetwork", r"Reaction networks: complete check including global existence", r"network\_final"),
        ("StrictExistence", r"Global existence with strictly positive concentrations", r"exists\_global\_solution\_strict"),
        ("StrictNetwork", r"Networks with strictly positive domains (e.g.\ $\beta SI/N$, Hill with real exponent)", r"strict\_final\_init"),
        ("RiccatiNetwork", r"Existence on a finite horizon under quadratic growth (Riccati bound; used for Crauste)", r"riccati\_final"),
        ("IntervalInit", r"Parameter-dependent initial values certified with rational interval arithmetic", r"strict\_final\_initI")]),
]

spec2 = importlib.util.spec_from_file_location("fo", LEAN / "formulas.py")
fo = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(fo)
info = {m: (d, k) for _, g in G for m, d, k in g}
names = fo.ORDER
assert sorted(names) == sorted(cnt) == sorted(info), set(cnt) ^ set(names)
deps = {m: [l.split()[1] for l in (LEAN / f"{m}.lean").read_text(encoding="utf-8").splitlines()
            if l.startswith("import ") and not l.startswith("import Mathlib")] for m in names}
tot = sum(cnt.values())
L = [r"All formal proofs are collected in the folder \texttt{lean\_proofs/} of the reproducibility package, a self-contained "
     r"Lean~4 project (Lean 4.23.0, Mathlib v4.23.0) that compiles with a single command (\texttt{./verify.sh}). "
     f"It contains {len(names)} theory modules with {tot} theorems and lemmas, and 28 benchmark models translated from SBML. "
     r"No file contains \texttt{sorry} or \texttt{axiom}, and \texttt{\#print axioms} reports only \texttt{propext}, "
     r"\texttt{Classical.choice} and \texttt{Quot.sound} for every theorem. Supplementary Table~\ref{tab:modules} lists the modules in the "
     r"logical order of the proofs: \# is the step number, and every module only uses modules with a smaller "
     r"number (column `Uses'). $n$ is the number of theorems and lemmas in the module (its size, not an index). "
     r"\sref{stmts} gives the statement and meaning of every theorem and lemma; the file \texttt{THEOREMS.md} "
     r"in the folder lists them as well.", "",
     r"{\footnotesize\setlength{\tabcolsep}{4pt}", r"\begin{longtable}{@{}>{\raggedleft\arraybackslash}p{0.45cm}>{\raggedright\arraybackslash}p{3.6cm}>{\raggedleft\arraybackslash}p{0.55cm}>{\raggedright\arraybackslash}p{1.3cm}>{\raggedright\arraybackslash}p{4.6cm}>{\raggedright\arraybackslash}p{3.9cm}@{}}",
     r"\caption{Modules of the Lean formalisation in the logical order of the proofs.}\label{tab:modules}\\",
     r"\toprule", r"\# & Module & $n$ & Uses & Content & Main theorems \\", r"\midrule", r"\endfirsthead",
     r"\toprule", r"\# & Module & $n$ & Uses & Content & Main theorems \\", r"\midrule", r"\endhead"]
for part, title, mods in fo.PARTS:
    st = [fo.STEP[m] for m in mods]
    steps = f"Step {min(st)}" if min(st) == max(st) else f"Steps {min(st)}--{max(st)}"
    L.append(r"\multicolumn{6}{@{}l}{\textit{" + steps + ". " + title + r"}} \\")
    for m in mods:
        d, k = info[m]
        brk = lambda t: t.replace(r"\_", r"\_\allowbreak{}").replace(", ", r", \allowbreak{}")
        kk = r"\texttt{" + brk(k) + "}" if k else "--"
        mm = r"\texttt{" + "\\allowbreak{}".join(__import__("re").findall(r"[A-Z][a-z]*|[A-Z]+(?![a-z])|\d+", m)) + "}"
        uu = ", ".join(str(fo.STEP[x]) for x in sorted(deps[m], key=fo.STEP.get)) or "--"
        L.append(f"{fo.STEP[m]} & {mm} & {cnt[m]} & {uu} & {d} & {kk} \\\\")
L += [r"\midrule", f" & Total & {tot} & & & \\\\", r"\bottomrule", r"\end{longtable}", "}", "",
      r"\textbf{Verified benchmark models (28).} Armistead, Bachmann, Bertozzi, Blasi, Boehm, Borghans, Brannmark, "
      r"Bruno, Chen (501 states, in four parts), Crauste (horizon $T\le 1$), Elowitz, Fiedler, Froehlich (1,228 states, "
      r"in twelve parts), Fujita, Giordano, Isensee, Lang, Laske, Lucarelli, Okuonghae, Rahman, Raia, Raimundez, "
      r"SalazarCavazos, Sneyd, Weber, Zhao and Zheng (folder \texttt{lean\_proofs/Models/}). For each model, the final theorem establishes that the "
      r"vector field is smooth on its domain, that the solution exists on the simulated horizon and that "
      r"concentrations remain non-negative. The data of each model and the checks executed are given in \sref{models} and Supplementary Table~\ref{tab:models}, which also explain why the remaining seven benchmark problems were not verified.", ""]

(TAB / "tableS3.tex").write_text("\n".join(L) + "\n")
print(len(names), "modules,", tot, "theorems and lemmas")
