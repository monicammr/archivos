#!/usr/bin/env python3
"""Supplementary Note 4 and Table S5: the 22 benchmark models verified in Lean, with the data contained in
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
    if m:
        times[m.group(1)] = times.get(m.group(1), 0.0) + float(m.group(2))

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

assert len(models) == 22, len(models)

# ------------------------------------------------------------------ LaTeX
L = [r"\section*{Supplementary Note 4. The verified benchmark models}", r"\sloppy", "",
     r"This note lists, for each of the 22 benchmark models verified in Lean, the data contained in its file in "
     r"\texttt{lean\_proofs/Models/}, the checks executed by the Lean kernel on those data and the final theorem "
     r"that results. Each file was generated from the SBML model and the PEtab parameter table of the benchmark by "
     r"\texttt{certificados/sbml\_to\_lean.py}, with every number written as an exact rational. The checks are "
     r"Boolean functions proved sound in steps 27--31 of Supplementary Note~2; each is evaluated by the Lean kernel "
     r"(\texttt{decide +kernel}), so its value \texttt{true} is part of the proof. The final theorem "
     r"\texttt{Models.<model>.final} then has no pending hypotheses: it states that the model satisfies the "
     r"assumptions of Parts~II--III (smooth vector field on a domain containing the trajectory, existence of the "
     r"nominal solution on the horizon, non-negativity, and differentiability of the solution with respect to the "
     r"parameters). \texttt{\#print axioms} for every final theorem reports only \texttt{propext}, "
     r"\texttt{Classical.choice} and \texttt{Quot.sound} (\texttt{CheckModelAxioms.lean}). Table~S5 summarises the "
     r"models; the paragraphs below give the data of each one.", "",
     r"{\small", r"\begin{longtable}{@{}>{\raggedright\arraybackslash}p{3.6cm}rrrr>{\raggedright\arraybackslash}p{1.6cm}>{\raggedright\arraybackslash}p{2.9cm}r@{}}",
     r"\caption*{\textbf{Supplementary Table S5.} Benchmark models verified in Lean. $n$: species (states); $p$: "
     r"parameters; $R$: rate terms (reactions after splitting reversible ones); $|\Sigma|$: species proved strictly "
     r"positive; time: compilation time of the model files (s).}\\",
     r"\toprule", r"Model & $n$ & $p$ & $R$ & $|\Sigma|$ & Horizon & Final theorem & Time \\", r"\midrule", r"\endhead"]
for m in models:
    hz = (r"$T\le" + m["Tq"] + "$") if m["Tq"] else ("6 segments" if m["segs"] else r"all $T\ge0$")
    t = f"{m['time']:.0f}" if m["time"] else "--"
    br = lambda x: re.sub(r"([a-z])([A-Z])", r"\1\\allowbreak{}\2", esc(x).replace(r"\_", r"\_\allowbreak{}"))
    L.append(f"{br(m['name'])} & {m['n']:,} & {m['p']:,} & {m['nterms']:,} & {len(m['sigma']) or '--'} & {hz} & "
             f"\\texttt{{{br(m['final'])}}} & {t} \\\\".replace(",", "{,}"))
L += [r"\bottomrule", r"\end{longtable}", "}", ""]

for m in models:
    nm = esc(m["name"])
    L += [r"\subsection*{" + nm + "}", ""]
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
    items.append(f"\\textbf{{Final theorem}} (\\texttt{{Models.{nm}.final}} $:=$ \\texttt{{{esc(m['final'])}}}): " + FINAL[m["final"]] + ".")
    L += [r"\begin{itemize}\itemsep0pt\small"] + [r"\item " + it for it in items] + [r"\end{itemize}", ""]

bad = sorted({ch for l in L for ch in l if ord(ch) > 127})
assert not bad, bad
p = HERE / "supplementary.tex"
s = p.read_text(encoding="utf-8")
key = r"\section*{Supplementary Note 4."
a = s.index(key) if key in s else s.index(r"\end{document}")
p.write_text(s[:a] + "\n".join(L) + "\n" + r"\input{suppl_conclusion}" + "\n\n" + r"\end{document}" + "\n", encoding="utf-8")
print(len(models), "models;", {m["name"]: (m["n"], m["p"], m["nterms"]) for m in models})
