#!/usr/bin/env python3
"""Supplementary Note 4 and Table S6: the benchmark models verified in Lean, with the data contained in
each file of lean_proofs/Models/ (states, parameters and nominal values, reactions, positivity masks,
weights, initial values, horizon), the checks executed by the Lean kernel and the final theorem applied.
All information is read from the Lean files and from lean_proofs/BUILD_LOG.md."""
import re
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
LP = HERE.parent.parent / "lean_proofs"
MD = LP / "Models"
RAT = re.compile(r"\((-?\d+)(?: / (\d+))? : ℚ\)")

times = {}
for l in (LP / "BUILD_LOG.md").read_text(encoding="utf-8").splitlines():
    m = re.match(r"\| `Models\.([^`.]+)(?:\.[^`]+)?` \| ([\d.]+) \|", l)
    m = m or re.match(r"\| `Models\.([^`.]+)` \| `\w+` \| ([\d.]+) \|", l)
    if m:
        times[m.group(1)] = times.get(m.group(1), 0.0) + float(m.group(2))
import json, sys
FID = {d["sistema"]: d for d in json.loads((HERE.parent.parent / "certificados" / "resultados" / "sbml_lean" /
                                            "fidelidad.json").read_text(encoding="utf-8"))}
sys.path.insert(0, str(HERE.parent.parent / "certificados"))

CHECK = {
    "net_ok": "rate laws well defined on the non-negative orthant and quasi-positive (\\texttt{checkNet})",
    "net_okS": "rate laws well defined on the strict region $P_\\Sigma$, quasi-positive, and consumption of species in $\\Sigma$ at most proportional to their concentration (\\texttt{checkNetS})",
    "growth_ok": "linear growth bound $\\sum_iw_if_i\\le a+b\\sum_iw_ix_i$ with the weights $w$ (\\texttt{checkGrowth})",
    "growth_okS": "linear growth bound on $P_\\Sigma$ (\\texttt{checkGrowthS})",
    "theta_ok": "nominal parameters positive where declared (\\texttt{checkPosParams})",
    "x0_ok": "initial values non-negative (\\texttt{checkNonneg})",
    "init_ok": "parameter-dependent initial values $G(\\theta)$ well defined and non-negative at $\\theta_0$ (\\texttt{checkInit})",
    "init_okS": "parameter-dependent initial values $G(\\theta_0)\\in P_\\Sigma$ (\\texttt{checkInitS})",
    "init_okI": "initial values $G(\\theta_0)\\in P_\\Sigma$ certified by rational interval arithmetic (\\texttt{checkInitI})",
    "ub_ok": "declared parameter bounds hold at $\\theta_0$ (\\texttt{checkUB})",
    "half_ok": "the real powers in $G$ are square roots",
    "riccati_ok": "quadratic growth bound $\\sum_iw_if_i\\le Q(\\varphi+1)^2$ and $1.1\\,Q(\\varphi(x_q)+1)T_q<1$ (\\texttt{checkRiccati})",
    "Lq_nonneg": "segment lengths are non-negative",
}
FINAL = {
    "network_final": "for every $T\\ge0$ the nominal solution from $x_q$ exists on $[0,T]$, is non-negative and stays in the domain of the rate laws; solutions exist for all $\\theta$ near $\\theta_0$, and $x(t;\\theta)$ is differentiable in $\\theta$ with sensitivity $S(t)$, $S(0)=0$",
    "network_final_init": "same as \\texttt{network\\_final}, with initial value $x(0)=G(\\theta)$ and $S(0)=\\partial_\\theta G(\\theta_0)$",
    "network_segments_final": "the same conclusions on each segment of the piecewise-defined model, with continuity across segment boundaries",
    "strict_final_init": "for every $T\\ge0$ the nominal solution exists on $[0,T]$ and stays in $P_\\Sigma$ (species in $\\Sigma$ strictly positive) and in the domain; solutions near $\\theta_0$ exist and are differentiable, $S(0)=\\partial_\\theta G(\\theta_0)$",
    "strict_final_initI": "same as \\texttt{strict\\_final\\_init}, with the initial values certified by interval arithmetic",
    "riccati_final": "for every $T\\le T_q$ the nominal solution exists on $[0,T]$, is non-negative and stays in the domain; solutions near $\\theta_0$ exist and are differentiable, $S(0)=0$",
}


GREEK = {"α": "alpha", "β": "beta", "γ": "gamma", "δ": "delta", "ε": "varepsilon", "θ": "theta", "κ": "kappa",
         "λ": "lambda", "μ": "mu", "ρ": "rho", "σ": "sigma", "τ": "tau", "φ": "varphi", "ω": "omega"}


def esc(s):
    s = s.replace("_", r"\_").replace("&", r"\&").replace("%", r"\%").replace("#", r"\#")
    for g, t in GREEK.items():
        s = s.replace(g, f"$\\{t}$")
    return s


def fmt(q):
    x = float(q)
    if x == 0:
        return "0"
    s = f"{x:.4g}"
    if "e" in s:
        a, b = s.split("e")
        return f"${a}\\times10^{{{int(b)}}}$"
    return s


models = []
for main in sorted(MD.glob("*.lean")):
    name = main.stem
    files = [main] + sorted((MD / name).glob("*.lean")) if (MD / name).is_dir() else [main]
    txt = "\n".join(f.read_text(encoding="utf-8") for f in files)
    head = main.read_text(encoding="utf-8").split("-/")[0]
    if (MD / name / "Base.lean").exists():
        head += (MD / name / "Base.lean").read_text(encoding="utf-8").split("-/")[0]
    n, p = map(int, re.search(r"KExpr (\d+) (\d+)", txt).groups())
    states = re.search(r"Estados \((\d+)\): (.*)", head)
    params = re.search(r"Parámetros estimados θ \((\d+)\): (.*)", head)
    sigma = re.search(r"Σ \([^)]*\): (.*)", head)
    segs = re.search(r"Tramos: (.*)", head)
    hor = re.search(r"def Tq : ℚ := \((\d+) : ℚ\)", txt)
    nterms = len(re.findall(r"^\s*\(\(KExpr", txt, re.M))
    pos = re.search(r"def pos : Fin \d+ → Bool := (.*)", txt).group(1)
    npos = p if "fun _ => true" in pos else pos.count("true")
    cdef = re.findall(r"def c\d* : Fin \d+ → ℚ := (.*)", txt)
    wts = sorted({Fraction(int(a), int(b or 1)) for c in cdef for a, b in RAT.findall(c)}) if not all("fun _ => (1 : ℚ)" in c for c in cdef) else [Fraction(1)]
    tq = re.search(r"def θq(?:L)? : [^=]*:= !?\[(.*)\]", txt).group(1)
    theta = [Fraction(int(a), int(b or 1)) for a, b in RAT.findall(tq)]
    assert len(theta) == p, (name, len(theta), p)
    final = re.search(r"def final := @(\w+)", txt).group(1)
    checks = re.findall(r"^theorem (\w+_ok\w*|Lq_nonneg)\b", txt, re.M)
    checks = sorted({re.sub(r"(_\d+|\d+)$", "", c) for c in checks}, key=lambda c: list(CHECK).index(c) if c in CHECK else 99)
    strict = "Strict" in final or final.startswith("strict")
    ck = []
    for c in checks:
        k = c + ("S" if strict and c in ("net_ok", "growth_ok") else "")
        if c == "init_ok":
            k = "init_okI" if final == "strict_final_initI" else ("init_okS" if strict else "init_ok")
        ck.append(k)
    init = "G(θ)" if re.search(r"def G :", txt) else "x_q"
    nnz = None
    if init == "x_q":
        xm = re.search(r"def xqL : [^=]*:= \[(.*)\]", txt) or re.search(r"def xq : [^=]*:= !\[(.*)\]", txt)
        xs = [Fraction(int(a), int(b or 1)) for a, b in RAT.findall(xm.group(1))] if xm else []
        nnz = sum(1 for v in xs if v != 0)
    sig_names = [s.strip() for s in sigma.group(1).split(",")] if sigma else []
    models.append(dict(name=name, n=n, p=p, states=states.group(2).split(", ") if states else None,
                       pnames=params.group(2).split(", ") if params else None, sigma=sig_names, segs=segs.group(1) if segs else None,
                       Tq=hor.group(1) if hor else None, nterms=nterms, npos=npos, wts=wts, theta=theta, final=final,
                       checks=ck, init=init, nnz=nnz, parts=len(files) - 1 if len(files) > 1 else 0,
                       time=times.get(name)))

NM = len(models)
assert NM == 28, NM
missing = [m["name"] for m in models if FID.get(m["name"], {}).get("err_rel_max") is None]
assert len(missing) <= 1, missing      # (comprobación en curso, como mucho un modelo)


def fidv(nm):
    if nm not in FID:
        return None
    d = FID[nm]
    return max(d["err_rel_max"], d["err_theta"], d["err_x0"] or 0.0)


def fmte(x):
    if x is None:
        return "pending"
    if x == 0:
        return "0"
    a, b = f"{x:.0e}".split("e")
    return f"${a}\\times10^{{{int(b)}}}$"


FMAX = max(fidv(m["name"]) for m in models if fidv(m["name"]) is not None)

# ------------------------------------------------------------------ LaTeX
L = [r"\section*{Supplementary Note 4. The verified benchmark models}", r"\sloppy", "",
     r"This note lists, for each of the " + str(NM) + r" benchmark models verified in Lean, the data contained in its file in "
     r"\texttt{lean\_proofs/Models/}, the checks executed by the Lean kernel on those data and the final theorem "
     r"that results. Each file was generated from the SBML model and the PEtab parameter table of the benchmark by "
     r"\texttt{certificados/sbml\_to\_lean.py}, with every number written as an exact rational. The checks are "
     r"Boolean functions proved sound in steps 27--31 of Supplementary Note~2; each is evaluated by the Lean kernel "
     r"(\texttt{decide +kernel}), so its value \texttt{true} is part of the proof. The final theorem "
     r"\texttt{Models.<model>.final} then has no pending hypotheses: it states that the model satisfies the "
     r"assumptions of Parts~II--III (smooth vector field on a domain containing the trajectory, existence of the "
     r"nominal solution on the horizon, non-negativity, and differentiability of the solution with respect to the "
     r"parameters). \texttt{\#print axioms} for every final theorem reports only \texttt{propext}, "
     r"\texttt{Classical.choice} and \texttt{Quot.sound} (\texttt{CheckModelAxioms.lean}). Table~S6 summarises the "
     r"models, the next subsections describe the independent check of the translation, a complete example (Boehm) "
     r"and the benchmark problems that were not verified, and the last subsections give the data of each model.", "",
     r"{\small", r"\begin{longtable}{@{}>{\raggedright\arraybackslash}p{3.2cm}rrrr>{\raggedright\arraybackslash}p{1.5cm}>{\raggedright\arraybackslash}p{2.5cm}rr@{}}",
     r"\caption*{\textbf{Supplementary Table S6.} Benchmark models verified in Lean. $n$: states (species, plus "
     r"time when a rate law depends on it); $p$: parameters; $R$: rate terms (reactions after splitting reversible "
     r"ones); $|\Sigma|$: species proved strictly positive; time: compilation time of the model files (s); "
     r"fidelity: largest relative difference between the Lean translation and the SBML model evaluated by "
     r"libRoadRunner (vector field, parameter values and initial values).}\\",
     r"\toprule", r"Model & $n$ & $p$ & $R$ & $|\Sigma|$ & Horizon & Final theorem & Time & Fidelity \\", r"\midrule", r"\endhead"]
for m in models:
    hz = (r"$T\le" + m["Tq"] + "$") if m["Tq"] else ("6 segments" if m["segs"] else r"all $T\ge0$")
    t = f"{m['time']:.0f}" if m["time"] else "--"
    br = lambda x: re.sub(r"([a-z])([A-Z])", r"\1\\allowbreak{}\2", esc(x).replace(r"\_", r"\_\allowbreak{}"))
    L.append(f"{br(m['name'])} & {m['n']:,} & {m['p']:,} & {m['nterms']:,} & {len(m['sigma']) or '--'} & {hz} & "
             f"\\texttt{{{br(m['final'])}}} & {t} & {fmte(fidv(m['name']))} \\\\".replace(",", "{,}"))
L += [r"\bottomrule", r"\end{longtable}", "}", ""]

# ---------------- fidelity of the translation
L += [r"\subsection*{Agreement of the translation with the SBML models}", "",
      r"Lean checks the expressions it is given; whether these expressions are the model of the benchmark is a "
      r"separate question. The script \texttt{certificados/verifica\_traduccion.py} answers it without using the "
      r"translator: it reads the rate laws, the stoichiometry, the parameter values $\theta_q$ and the initial values "
      r"directly from the Lean files, evaluates the vector field in floating point, and compares it with the "
      r"derivatives computed by libRoadRunner from the original SBML model with the nominal parameters of the PEtab "
      r"table, at the initial state and at five random positive states. It also compares $\theta_q$ with the PEtab "
      r"nominal values and the initial values (or $G(\theta_q)$) with those of the SBML model. Over the " + str(NM - len(missing)) +
      r" models" + (f" checked so far (the check of {missing[0].split('_')[0]} is still running)," if missing else ",") + r" the largest relative difference is " + fmte(FMAX) + r", i.e.\ agreement to rounding error "
      r"(Table~S6, last column). As a control, changing one parameter value, one initial value or one stoichiometric "
      r"coefficient of the Lean file by 1\% is detected (relative differences of $10^{-2}$). The comparison covers the "
      r"model without condition-specific overrides, which is what the Lean files describe; for models defined by "
      r"segments it covers the first segment.", ""]

# ---------------- worked example
import verifica_traduccion as V
from fractions import Fraction as _F
B = "Boehm_JProteomeRes2014"
LB = V.load_lean(B)
bm = next(m for m in models if m["name"] == B)
snames = [s.split(" (")[0] for s in LB["states"]]


def tex(e, prec=0):
    k = e[0]
    def wrap(t, pr):
        return f"\\left({t}\\right)" if pr < prec else t
    if k in ("qconst", "const"):
        q = _F(e[1]).limit_denominator(10 ** 12)
        t = str(q.numerator) if q.denominator == 1 else f"\\tfrac{{{q.numerator}}}{{{q.denominator}}}"
        return wrap(t, 3) if q < 0 else t
    if k == "var":
        nm = snames[e[1]]
        return "\\tau" if "tiempo" in LB["states"][e[1]] else f"\\mathrm{{{esc(nm)}}}"
    if k == "par":
        return f"\\theta_{{{e[1] + 1}}}"
    if k == "add":
        return wrap(f"{tex(e[1], 1)}+{tex(e[2], 1)}", 1)
    if k == "sub":
        return wrap(f"{tex(e[1], 1)}-{tex(e[2], 2)}", 1)
    if k == "mul":
        a, b = e[1], e[2]
        if a[0] == "qconst" and a[1] == -1:
            return wrap(f"-{tex(b, 2)}", 1)
        return wrap(f"{tex(a, 2)}\\,{tex(b, 2)}", 2)
    if k == "div":
        return f"\\dfrac{{{tex(e[1])}}}{{{tex(e[2])}}}"
    if k == "npow":
        return f"{tex(e[1], 3)}^{{{e[2]}}}"
    if k == "rpow":
        return f"{tex(e[1], 3)}^{{{e[2]:g}}}"
    if k == "exp":
        return f"e^{{{tex(e[1])}}}"
    if k == "log":
        return f"\\log{tex(e[1], 3)}"


def col(c):
    return ", ".join(f"{snames[i] if 'tiempo' not in LB['states'][i] else 'tau'}: {_F(v).limit_denominator(10**9)}" for i, v in c)


L += [r"\subsection*{A complete example: Boehm\_JProteomeRes2014}", "",
      r"The model of STAT5 dimerisation by Boehm et al.\ is small enough to follow every step. Its file is "
      r"\texttt{lean\_proofs/Models/Boehm\_JProteomeRes2014.lean} (about 60 lines).", "",
      r"\textbf{1. Model.} The SBML model has 8 species, and the stimulus decays as $e^{-\theta_1\tau}$, where "
      r"$\tau$ is time; the translator therefore adds $\tau$ as a ninth state with $\dot\tau=1$. The six estimated "
      r"parameters are " + ", ".join(f"$\\theta_{{{j+1}}}=$ {esc(a)} ({fmt(v)})" for j, (a, v) in enumerate(zip(bm['pnames'], bm['theta']))) +
      r". The vector field is $f_i=\sum_k\nu_{ik}v_k$ with the following rate terms $v_k$ and stoichiometric "
      r"coefficients $\nu_{ik}$ (the constants come from compartment volumes and fixed parameters of the SBML model):", "",
      r"{\small", r"\begin{longtable}{@{}r>{\raggedright\arraybackslash}p{9.6cm}>{\raggedright\arraybackslash}p{5.2cm}@{}}",
      r"\toprule", r"$k$ & Rate term $v_k$ & Stoichiometry $\nu_{\cdot k}$ \\", r"\midrule"]
for k, (e, c) in enumerate(LB["R"]):
    L.append(f"{k + 1} & ${tex(e)}$ & {esc(col(c))} \\\\")
L += [r"\bottomrule", r"\end{longtable}", "}", "",
      r"\textbf{2. Translation into Lean.} Each rate term is a \texttt{KExpr}, for example "
      r"\texttt{KExpr.npow (KExpr.var 0) 2} stands for $\mathrm{STAT5A}^2$; numbers are exact rationals, "
      r"and the list \texttt{Rx} pairs each term with its stoichiometric column. The initial value is the rational "
      r"vector \texttt{xq} (STAT5A and STAT5B positive, all other states 0), and \texttt{θq} holds the six parameters.".replace("θq", r"$\theta_q$"), "",
      r"\textbf{3. Checks.} Four Boolean checks are evaluated by the Lean kernel: \texttt{net\_ok} (every rate term is "
      r"well defined for $x\ge0$, and every term that consumes a species vanishes when that species is 0, so the field "
      r"is quasi-positive), \texttt{growth\_ok} (with weights $w_i=1$, $\sum_if_i\le a+b\sum_ix_i$: the stoichiometric "
      r"columns of six terms have a negative sum, and the remaining ones, the nuclear-import terms 7--9 and "
      r"$\dot\tau=1$, are at most linear in the states), \texttt{theta\_ok} "
      r"(all $\theta_j>0$) and \texttt{x0\_ok} ($x_q\ge0$).", "",
      r"\textbf{4. Final theorem.} \texttt{def final := network\_final pos Rx net\_ok c growth\_ok θq theta\_ok xq x0\_ok} "
      r"applies the end-to-end theorem of step~28 to these data. Its statement is: for every $T\ge0$ there is a "
      r"solution $x_0$ on $[0,T]$ with $x_0(0)=x_q$, $x_0(t)\ge0$ and $(x_0(t),\theta_q)$ in the domain; there is a "
      r"family $x(\cdot;\theta)$ of solutions for $\theta$ near $\theta_q$ with $x(\cdot;\theta_q)=x_0$; and "
      r"$x(t;\theta)$ is differentiable in $\theta$ at $\theta_q$ with derivative $S(t)$, $S(0)=0$, solving the "
      r"variational equation. These are the hypotheses of Parts~II--III for this model.".replace("θq", r"$\theta_q$"), "",
      r"\textbf{5. Reproduction.} From the folder \texttt{lean\_proofs/}, the command", "",
      r"\begin{quote}\small\raggedright\texttt{lake env lean Models/Boehm\_JProteomeRes2014.lean}\end{quote}", "",
      r"compiles the file in a few seconds and prints", "",
      r"\begin{quote}\small\raggedright\texttt{'Models.Boehm\_JProteomeRes2014.final' depends on axioms: [propext, Classical.choice, Quot.sound]}\end{quote}", "",
      r"and, from the folder \texttt{certificados/}, the command", "",
      r"\begin{quote}\small\raggedright\texttt{python3 verifica\_traduccion.py Boehm\_JProteomeRes2014}\end{quote}", "",
      r"compares the file with the SBML model (largest relative difference " + fmte(fidv(B)) + r").", ""]

# ---------------- benchmark problems without a verified model
L += [r"\subsection*{Benchmark problems without a verified model}", "",
      r"Of the 34 benchmark problems analysed in the paper, 27 have a verified model; Froehlich, which is verified in "
      r"Lean, is the further problem analysed only on its state trajectories. The remaining seven problems were not "
      r"verified, for the following reasons. They are not counted in any statement that relies on G5.", "",
      r"\begin{itemize}\itemsep0pt\small",
      r"\item \textbf{Smith}: two reactions use $\max(\mathrm{PIP3}-\mathrm{basal},0)$, which is not differentiable, so the "
      r"vector field is not $C^1$ and the sensitivity theorem does not apply.",
      r"\item \textbf{Liu} and \textbf{Oliveira}: they contain events triggered by the state or by a parameter-dependent "
      r"condition, not at fixed times; such events are outside Hypothesis~2 (step~18).",
      r"\item \textbf{Alkan}: the model translates, but the syntactic checkers cannot establish well-definedness for 22 "
      r"rate terms or quasi-positivity for 6 of them; this does not mean that the properties fail, only that the "
      r"automatic proof does not cover them.",
      r"\item \textbf{Perelson} and \textbf{Schwen}: the quasi-positivity check fails for two rate terms each, so "
      r"non-negativity of the solutions is not established by the checker.",
      r"\item \textbf{Beer}: smoothness and quasi-positivity are verified on both segments of the model, but the linear "
      r"growth check is not satisfied, so existence of the nominal solution on the horizon is not proved; only a "
      r"conditional theorem (assuming the solution exists) is available.",
      r"\end{itemize}", ""]

L += [r"\subsection*{Data of each model}", ""]

for m in models:
    nm = esc(m["name"])
    L += [r"\subsubsection*{" + nm + "}", ""]
    items = []
    fl = f"\\texttt{{Models/{nm}.lean}}" + (f" and {m['parts']} part files in \\texttt{{Models/{nm}/}}" if m["parts"] else "")
    items.append(f"\\textbf{{File:}} {fl}.")
    if m["states"] and m["n"] <= 60:
        items.append(f"\\textbf{{States ($n={m['n']}$):}} " + ", ".join(esc(s) for s in m["states"]) + ".")
    else:
        items.append(f"\\textbf{{States:}} $n={m['n']:,}$".replace(",", "{,}") + " species (listed in the file).")
    if m["sigma"]:
        items.append(f"\\textbf{{Strictly positive species $\\Sigma$ ({len(m['sigma'])}):}} " + ", ".join(esc(s) for s in m["sigma"]) + ".")
    if m["pnames"] and m["p"] <= 60:
        items.append(f"\\textbf{{Parameters and nominal values $\\theta_0$ ($p={m['p']}$):}} "
                     + "; ".join(f"{esc(a)} $=$ {fmt(v)}" for a, v in zip(m["pnames"], m["theta"])) + ".")
    else:
        items.append(f"\\textbf{{Parameters:}} $p={m['p']}$, with nominal values in \\texttt{{θq}} (exact rationals) in the file.".replace("θq", r"$\theta_q$"))
    items.append(f"\\textbf{{Parameters declared positive:}} {m['npos']} of {m['p']}.")
    items.append(f"\\textbf{{Rate terms:}} {m['nterms']:,}".replace(",", "{,}") + ", each with its stoichiometric column.")
    if m["init"] == "x_q":
        items.append(f"\\textbf{{Initial values:}} constant rational vector $x_q$ ({m['nnz']} non-zero entries).")
    else:
        items.append(r"\textbf{Initial values:} expressions $G(\theta)$ in the parameters (SBML initial assignments).")
    w = m["wts"]
    items.append(r"\textbf{Weights $w_i$ of the growth bound:} " + ("all equal to 1." if w == [Fraction(1)] else "values " + ", ".join(fmt(v) for v in w) + "."))
    if m["segs"]:
        items.append(r"\textbf{Segments:} " + esc(m["segs"]) + ".")
    if m["Tq"]:
        items.append(f"\\textbf{{Horizon:}} $T\\le T_q={m['Tq']}$ (quadratic growth; Riccati bound).")
    items.append(r"\textbf{Checks executed by the kernel:} " + "; ".join(CHECK[c] for c in m["checks"]) + ".")
    items.append(r"\textbf{Fidelity of the translation:} largest relative difference " + fmte(fidv(m["name"])) + ".")
    items.append(f"\\textbf{{Final theorem}} (\\texttt{{Models.{nm}.final}} $:=$ \\texttt{{{esc(m['final'])}}}): " + FINAL[m["final"]] + ".")
    L += [r"\begin{itemize}\itemsep0pt\small"] + [r"\item " + it for it in items] + [r"\end{itemize}", ""]

bad = sorted({ch for l in L for ch in l if ord(ch) > 127})
assert not bad, bad
p = HERE / "supplementary.tex"
s = p.read_text(encoding="utf-8")
key = r"\section*{Supplementary Note 4."
a = s.index(key) if key in s else s.index(r"\end{document}")
p.write_text(s[:a] + "\n".join(L) + "\n" + r"\input{suppl_reproduction}" + "\n\n" + r"\input{suppl_conclusion}" + "\n\n" + r"\end{document}" + "\n", encoding="utf-8")
print(len(models), "models;", {m["name"]: (m["n"], m["p"], m["nterms"]) for m in models})
