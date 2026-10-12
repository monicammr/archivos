#!/usr/bin/env python3
"""Supplementary Note "Statements of the formal theorems" (statement and meaning of every Lean theorem) and lean_proofs/FORMULAS.md,
both generated from lean_proofs/formulas.py. Checks that every declaration found by
lean_proofs/catalogo.py has exactly one entry, and lists the benchmark models that use each final
theorem (found in lean_proofs/Models/)."""
import importlib.util
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
LP = HERE.parent.parent / "lean_proofs"


def load(name):
    spec = importlib.util.spec_from_file_location(name, LP / f"{name}.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


cat, fo = load("catalogo"), load("formulas")
decl = {p.stem: [n.split(".", 1)[1] for _, n, _, _ in cat.decls(p)] for p in cat.TEORIA}
ent = {m: [e[0] for e in ents] for m, _, _, _, ents in fo.M}
assert set(decl) == set(ent), set(decl) ^ set(ent)
for m in decl:
    assert sorted(decl[m]) == sorted(ent[m]), (m, set(decl[m]) ^ set(ent[m]))
tot = sum(len(v) for v in decl.values())

uses = {}
for p in sorted((LP / "Models").glob("*.lean")):
    txt = p.read_text(encoding="utf-8")
    for th in ("strict_final_initI", "strict_final_init", "riccati_final", "network_final_init",
               "network_segments_final", "network_final"):
        if re.search(rf"\b{th}\b", txt):
            uses.setdefault(th, []).append(p.stem.split("_")[0]); break


def tt(s):  # Lean identifier in \texttt with break points
    s = s.replace("\\", r"\textbackslash{}").replace("_", r"\_").replace("'", r"\textquotesingle{}")
    return r"\texttt{" + s.replace(r"\_", r"\_\allowbreak{}").replace(".", r".\allowbreak{}") + "}"


def tx(s):  # plain text (meanings) with Unicode math symbols mapped to LaTeX
    rep = {"θ₀": r"$\theta_0$", "θ": r"$\theta$", "≤": r"$\le$", "≥": r"$\ge$", "‖": r"$\|$", "∈": r"$\in$",
           "∉": r"$\notin$", "Σ": r"$\Sigma$", "√": r"$\surd$", "Δ": r"$\Delta$", "²": r"$^2$", "¹": r"$^1$",
           "⁻¹": r"$^{-1}$", "ᵀ": r"$^\top$", "ⁿ": r"$^n$", "𝒮₀": r"$\mathcal S_0$", "𝒮": r"$\mathcal S$",
           "𝓑": r"$\mathcal B$", "B̄": r"$\bar B$", "ρ₀": r"$\rho_0$", "ρ": r"$\rho$", "κ₀": r"$\kappa_0$",
           "κ": r"$\kappa$", "τ_e": r"$\tau_e$", "τ_κ": r"$\tau_\kappa$", "τ_VIF": r"$\tau_{\mathrm{VIF}}$", "τ": r"$\tau$",
           "σ_min": r"$\sigma_{\min}$", "σ_max": r"$\sigma_{\max}$", "σ": r"$\sigma$", "δ₀": r"$\delta_0$",
           "δ": r"$\delta$", "ε_g": r"$\varepsilon_g$", "ε": r"$\varepsilon$", "η": r"$\eta$", "λ_min": r"$\lambda_{\min}$",
           "λ": r"$\lambda$", "α*": r"$\alpha^*$", "α": r"$\alpha$", "β": r"$\beta$", "φ": r"$\varphi$", "ν": r"$\nu$",
           "M₁": r"$M_1$", "M₂": r"$M_2$", "K₀": r"$K_0$", "x⁰": r"$x^0$", "θ₀_j": r"$\theta_{0,j}$",
           "→": r"$\to$", "⇔": r"$\Leftrightarrow$", "×": r"$\times$", "−": "--", "–": "--", "…": r"\dots{}",
           "∞": r"$\infty$", "⟨": r"$\langle$", "⟩": r"$\rangle$", "↦": r"$\mapsto$", "∪": r"$\cup$", "∩": r"$\cap$",
           "Π": r"$\Pi$", "ℝ": r"$\mathbb R$", "ℚ": r"$\mathbb Q$", "·": r"$\cdot$", "≠": r"$\ne$", "∃": r"$\exists$",
           "∀ᶠ": r"$\forall^{\mathrm f}$", "∀": r"$\forall$", "∘": r"$\circ$", "′": r"$'$", "ö": r'\"o', "÷": r"$\div$", "⊆": r"$\subseteq$", "₁": r"$_1$", "₂": r"$_2$", "⁰": r"$^0$", "⁻": r"$^-$", "𝓝": r"$\mathcal N$", "ℓ": r"$\ell$", "ι": r"$\iota$", "ᵢ": r"$_i$", "ⱼ": r"$_j$", "₀": r"$_0$", "_": r"\_", "{": r"\{", ">": r"$>$", "<": r"$<$", "}": r"\}", "&": r"\&", "%": r"\%", "#": r"\#"}
    keys = sorted(rep, key=len, reverse=True)
    out, i = [], 0
    while i < len(s):
        for k in keys:
            if s.startswith(k, i):
                out.append(rep[k]); i += len(k); break
        else:
            out.append(s[i]); i += 1
    return "".join(out).replace("$$", "")


def lean_tx(s):  # Lean identifiers in the glossary: verbatim-like
    return r"\texttt{" + tx(s).replace("--", "-") + "}" if s else "--"


# ------------------------------------------------------------------ LaTeX
L = [r"\snote{stmts}", r"\sloppy", "",
     r"This note states, in mathematical notation, every theorem and lemma of the Lean formalisation "
     rf"({len(decl)} modules, {tot} declarations) and explains what it means, so that the formal statements can be "
     r"read alongside the code. The Lean name is given as it appears in the source (prefixed by the module "
     r"namespace). Hypotheses are written before $\Rightarrow$; standing assumptions of each module are given in "
     r"its description. Supplementary Table~\ref{tab:leannot} explains the symbols used throughout; symbols specific to a module are explained "
     r"at the start of that module. Supplementary Table~\ref{tab:statements} gives the statements, in one block per module, in the "
     r"order of Supplementary Table~\ref{tab:modules}; the blocks are grouped as in \sref{seq}. The same content, with the Lean identifiers, is in \texttt{lean\_proofs/FORMULAS.md}.",
     "", r"{\small",
     r"\begin{longtable}{@{}>{\raggedright\arraybackslash}p{4.0cm}>{\raggedright\arraybackslash}p{4.6cm}>{\raggedright\arraybackslash}p{7.2cm}@{}}",
     r"\caption{Notation of the formalisation.}\label{tab:leannot}\\", r"\toprule",
     r"Symbol & Lean & Meaning \\", r"\midrule", r"\endhead"]
for sym, lean, mean in fo.GLOSSARY:
    L.append(f"${sym}$ & {lean_tx(lean)} & {tx(mean)} \\\\")
L += [r"\bottomrule", r"\end{longtable}", "}", ""]
MOD = {m: (grp, desc, loc, ents) for m, grp, desc, loc, ents in fo.M}
for part, title, mods in fo.PARTS:
    st = [fo.STEP[m] for m in mods]
    L += [r"\subsection*{Steps " + f"{min(st)}--{max(st)}. " + title + "}", ""]
    for m in mods:
        grp, desc, loc, ents = MOD[m]
        L += [r"\subsubsection*{Step " + str(fo.STEP[m]) + r". \texttt{" + m + "} (" + str(len(ents)) + ")}", tx(desc), ""]
        if loc:
            L += [r"{\small\raggedright Notation: " + "; ".join(f"${s}$ (\\texttt{{{tx(l).replace('--', '-')}}}): {tx(mm)}" if l else f"${s}$: {tx(mm)}"
                                               for s, l, mm in loc) + ".}", ""]
        first = fo.STEP[m] == 1
        cap = (r"\caption{Statements of the formal theorems and lemmas, one block per module. Step~1: \texttt{" + m + r"}.}\label{tab:statements}\\"
               if first else r"\caption[]{(continued). Step~" + str(fo.STEP[m]) + r": \texttt{" + m + r"}.}\\")
        L += ([] if first else [r"\addtocounter{table}{-1}"]) + [r"{\small", r"\begin{longtable}{@{}>{\raggedright\arraybackslash}p{3.6cm}>{\raggedright\arraybackslash}p{6.6cm}>{\raggedright\arraybackslash}p{5.6cm}@{}}",
              cap, r"\toprule", r"Lean name & Statement & Meaning \\", r"\midrule", r"\endhead"]
        for name, stmt, mean in ents:
            extra = ""
            if name in uses:
                extra = " Used by the models " + ", ".join(uses[name]) + "."
            L.append(f"{tt(name)} & $\\displaystyle {stmt}$ & {tx(mean + extra)} \\\\[3pt]")
        L += [r"\bottomrule", r"\end{longtable}", "}", ""]

bad = sorted({ch for l in L for ch in l if ord(ch) > 127})
assert not bad, bad
(HERE / "suppl_formulas.tex").write_text("\n".join(L) + "\n", encoding="utf-8")

# ------------------------------------------------------------------ Markdown
D = ["# Statements of the formal theorems", "",
     "Generated by `paper/scirep/make_formulas.py` from `formulas.py`. Every theorem and lemma of this folder "
     f"({len(decl)} modules, {tot} declarations) with its statement in mathematical notation and its meaning. "
     "The same content is the Supplementary Note \"Statements of the formal theorems\" of the paper.", "", "## Notation", "",
     "| Symbol | Lean | Meaning |", "|---|---|---|"]
pipe = lambda t: t.replace(r"\|", r"\Vert ").replace("|", r"\vert ")
D += [f"| ${pipe(s)}$ | `{l}` | {mm} |" if l else f"| ${pipe(s)}$ | | {mm} |" for s, l, mm in fo.GLOSSARY]
D += ["", "## Logical order", "", "Every module only imports modules with a smaller step number (the Supplementary Note \"Logical sequence of the formal proofs\" of the paper explains the sequence).", "",
      "| Step | Module | Uses steps |", "|---|---|---|"]
for m in fo.ORDER:
    us = [l.split()[1] for l in (LP / f"{m}.lean").read_text(encoding="utf-8").splitlines()
          if l.startswith("import ") and not l.startswith("import Mathlib")]
    D.append(f"| {fo.STEP[m]} | `{m}` | {', '.join(str(fo.STEP[u]) for u in sorted(us, key=fo.STEP.get)) or '—'} |")
for part, title, mods in fo.PARTS:
    st = [fo.STEP[m] for m in mods]
    D += ["", f"## Steps {min(st)}-{max(st)}. {title}"]
    for m in mods:
        grp, desc, loc, ents = MOD[m]
        D += ["", f"### Step {fo.STEP[m]}. `{m}` ({len(ents)})", "", desc, ""]
        if loc:
            D += ["Notation: " + "; ".join(f"${s}$ (`{l}`): {mm}" if l else f"${s}$: {mm}" for s, l, mm in loc) + ".", ""]
        D += ["| Lean name | Statement | Meaning |", "|---|---|---|"]
        for name, stmt, mean in ents:
            extra = f" Used by the models {', '.join(uses[name])}." if name in uses else ""
            st = stmt.replace(r"\|", r"\Vert ").replace("|", r"\vert ")
            D.append(f"| `{m}.{name}` | ${st}$ | {mean}{extra} |")
(LP / "FORMULAS.md").write_text("\n".join(D) + "\n", encoding="utf-8")
print(len(decl), "modules,", tot, "declarations; models:", {k: len(v) for k, v in uses.items()})
