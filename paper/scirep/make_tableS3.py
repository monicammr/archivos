#!/usr/bin/env python3
"""Supplementary Table S3 (formal proofs): one row per Lean module of lean_proofs/, with the number of
theorems and lemmas counted by lean_proofs/catalogo.py. Rewrites that section of supplementary.tex."""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
spec = importlib.util.spec_from_file_location("cat", ROOT / "lean_proofs" / "catalogo.py")
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
        ("PatternMechanisms", r"Opposing effects imply rejection by $\kappa$ and non-identifiability; zero discarded energy implies exact first-order reduction", r"not\_okKappa\_of\_kernel, exact\_reduction\_of\_zero\_energy")]),
    ("Re-estimation, minimality and measured outputs", [
        ("RefitMonotone", r"Re-estimating more parameters never increases the fitting error; $e_{\mathrm{fit}}\le e_{\mathrm{rel}}$", r"fitErr\_anti, fitErr\_le\_erel, admissible\_mono"),
        ("Poda", r"Theorem 2: backward elimination returns an inclusion-minimal admissible subset", r"prune\_spec, exists\_minimal\_admissible"),
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

names = [m for _, g in G for m, _, _ in g]
assert sorted(names) == sorted(cnt), set(cnt) ^ set(names)
tot = sum(cnt.values())
L = [r"\section*{Supplementary Table S3. Formal proofs}", "",
     r"All formal proofs are collected in the folder \texttt{lean\_proofs/} of the repository, a self-contained "
     r"Lean~4 project (Lean 4.23.0, Mathlib v4.23.0) that compiles with a single command (\texttt{./verify.sh}). "
     f"It contains {len(names)} theory modules with {tot} theorems and lemmas, and 22 benchmark models translated from SBML. "
     r"No file contains \texttt{sorry} or \texttt{axiom}, and \texttt{\#print axioms} reports only \texttt{propext}, "
     r"\texttt{Classical.choice} and \texttt{Quot.sound} for every theorem. The file \texttt{THEOREMS.md} in that "
     r"folder lists every theorem and lemma; $n$ is the number of theorems and lemmas per module.", "",
     r"{\small", r"\begin{longtable}{@{}>{\raggedright\arraybackslash}p{3.7cm}>{\raggedleft\arraybackslash}p{0.6cm}>{\raggedright\arraybackslash}p{6.3cm}>{\raggedright\arraybackslash}p{4.9cm}@{}}",
     r"\toprule", r"Module & $n$ & Content & Main theorems \\", r"\midrule", r"\endhead"]
for g, mods in G:
    L.append(r"\multicolumn{4}{@{}l}{\textit{" + g + r"}} \\")
    for m, d, k in mods:
        brk = lambda t: t.replace(r"\_", r"\_\allowbreak{}").replace(", ", r", \allowbreak{}")
        kk = r"\texttt{" + brk(k) + "}" if k else "--"
        mm = r"\texttt{" + "\\allowbreak{}".join(__import__("re").findall(r"[A-Z][a-z]*|[A-Z]+(?![a-z])|\d+", m)) + "}"
        L.append(f"{mm} & {cnt[m]} & {d} & {kk} \\\\")
L += [r"\midrule", f"Total & {tot} & & \\\\", r"\bottomrule", r"\end{longtable}", "}", "",
      r"\textbf{Verified benchmark models.} Armistead, Bachmann, Blasi, Boehm, Borghans, Brannmark, Chen "
      r"(500 species, in four parts), Crauste (horizon $T\le 1$), Elowitz, Fiedler, Froehlich (1,228 species, "
      r"in twelve parts), Giordano, Lang, Okuonghae, Rahman, Raia, Raimundez, SalazarCavazos, Sneyd, Weber, Zhao "
      r"and Zheng (folder \texttt{lean\_proofs/Models/}). For each model, the final theorem establishes that the "
      r"vector field is smooth on its domain, that the solution exists on the simulated horizon and that "
      r"concentrations remain non-negative.", ""]

p = HERE / "supplementary.tex"
s = p.read_text()
a = s.index(r"\section*{Supplementary Table S3.")
b = s.index(r"\section*{Supplementary Note")
p.write_text(s[:a] + "\n".join(L) + "\n" + s[b:])
print(len(names), "modules,", tot, "theorems and lemmas")
