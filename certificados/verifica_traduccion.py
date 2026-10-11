#!/usr/bin/env python3
"""
Comprobación independiente de la traducción SBML → Lean (fidelidad de los 22 modelos verificados).

Lee las leyes de velocidad y la estequiometría directamente de los archivos de lean_proofs/Models/
(sin usar sbml_to_lean.py), evalúa el campo f(x, θ) = Σ_r ν_r · v_r(x, θ) en aritmética de coma
flotante y lo compara con las derivadas que calcula libRoadRunner a partir del SBML original del
benchmark, con los mismos valores de parámetros (θ₀ de PEtab y parámetros fijos), en el estado
inicial y en estados aleatorios positivos.

Convenciones de la traducción (documentadas en sbml_to_lean.py): estado = especies flotantes en
concentración (en cantidad si hasOnlySubstanceUnits) y, si hace falta, el tiempo τ como estado
(dτ/dt = 1). Los modelos por tramos se comparan en el primer tramo.

Resultado: resultados/sbml_lean/fidelidad.json y FIDELIDAD_TRADUCCION.md
"""
import json
import re
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
MD = HERE.parent / "lean_proofs" / "Models"
OUT = HERE / "resultados" / "sbml_lean"
sys.path.insert(0, str(HERE))
import petab_outputs as PO  # noqa: E402
import certify_systems as CS  # noqa: E402

TOK = re.compile(r"\(|\)|\[|\]|,|KExpr\.\w+|-?\d+(?:\.\d+)?(?:[eE]-?\d+)?|/|:|ℚ|ℝ")


class P:
    def __init__(self, s):
        self.t = TOK.findall(s)
        self.i = 0

    def peek(self):
        return self.t[self.i]

    def eat(self, x=None):
        v = self.t[self.i]
        if x is not None and v != x:
            raise ValueError(f"esperaba {x}, hay {v} en {self.i}")
        self.i += 1
        return v

    def num(self):
        """(a / b : ℚ) | (a : ℚ) | (a : ℝ) | a"""
        if self.peek() != "(":
            return float(self.eat())
        self.eat("(")
        if self.peek() == "(":                 # coerción anidada, p. ej. (((1 / 2 : ℚ) : ℚ) : ℝ)
            a = self.num()
        else:
            a = Fraction(self.eat())
            if self.peek() == "/":
                self.eat("/"); a = a / Fraction(self.eat())
        self.eat(":"); self.eat(); self.eat(")")
        return float(a)

    def expr(self):
        self.eat("(")
        k = self.eat()[6:]
        if k in ("qconst", "const"):
            node = (k, self.num())
        elif k in ("var", "par"):
            node = (k, int(self.eat()))
        elif k in ("add", "sub", "mul", "div"):
            node = (k, self.expr(), self.expr())
        elif k == "npow":
            node = (k, self.expr(), int(self.eat()))
        elif k == "rpow":
            node = (k, self.expr(), self.num())
        elif k in ("exp", "log"):
            node = (k, self.expr())
        else:
            raise ValueError(k)
        self.eat(")")
        return node


def ev(e, x, th):
    k = e[0]
    if k in ("qconst", "const"): return e[1]
    if k == "var": return x[e[1]]
    if k == "par": return th[e[1]]
    if k == "add": return ev(e[1], x, th) + ev(e[2], x, th)
    if k == "sub": return ev(e[1], x, th) - ev(e[2], x, th)
    if k == "mul": return ev(e[1], x, th) * ev(e[2], x, th)
    if k == "div": return ev(e[1], x, th) / ev(e[2], x, th)
    if k == "npow": return ev(e[1], x, th) ** e[2]
    if k == "rpow": return ev(e[1], x, th) ** e[2]
    if k == "exp": return np.exp(ev(e[1], x, th))
    if k == "log": return np.log(ev(e[1], x, th))


def rx_list(txt, var):
    """Lista de (expresión, [(i, coef)]) de `def <var> : List (...) := [ ... ]`."""
    m = re.search(rf"^def {var} : List [^\n]*:= \[\n(.*?)\n\]", txt, re.S | re.M)
    out = []
    for line in m.group(1).splitlines():
        line = line.strip().rstrip(",")
        if not line:
            continue
        p = P(line)
        p.eat("(")
        e = p.expr()
        p.eat(",")
        p.eat("[")
        col = []
        while p.peek() != "]":
            if p.peek() == ",":
                p.eat(","); continue
            p.eat("("); i = int(p.eat()); p.eat(","); c = p.num(); p.eat(")")
            col.append((i, c))
        out.append((e, col))
    return out


def rationals(s):
    return [float(Fraction(int(a), int(b or 1))) for a, b in re.findall(r"\((-?\d+)(?: / (\d+))? : ℚ\)", s)]


def names_from_sbml(name, n):
    """Orden de estados y θ según la convención del traductor, reconstruido con libsbml/PEtab."""
    import libsbml
    import pandas as pd
    folder = CS.BENCH / name / "v1"
    m = libsbml.readSBMLFromFile(str(folder / "model.xml")).getModel()
    rules = {r.getVariable() for r in m.getListOfRules() if r.isAssignment()}
    st = [s.getId() for s in m.getListOfSpecies()
          if not s.getBoundaryCondition() and not s.getConstant() and s.getId() not in rules]
    if len(st) == n - 1:
        st.append("τ (tiempo)")
    pt = pd.read_csv(folder / "parameters.tsv", sep="\t")
    gp = {q.getId() for q in m.getListOfParameters()}
    est = pt[pt["estimate"] == 1] if "estimate" in pt.columns else pt
    return st, [str(r) for r in est.parameterId if str(r) in gp]


def load_lean(name):
    main = MD / f"{name}.lean"
    files = [main] + (sorted((MD / name).glob("*.lean")) if (MD / name).is_dir() else [])
    txt = "\n".join(f.read_text(encoding="utf-8") for f in files)
    head = "\n".join(f.read_text(encoding="utf-8").split("-/")[0] for f in files)
    states = re.search(r"Estados(?: \(\d+\))?: (.*)", head)
    if states is None:   # modelos divididos: nombres en el comentario de Base
        states = re.search(r"Estados[^:]*: (.*)", head)
    st = [s.strip() for s in states.group(1).split(",")] if states else None
    pn = re.search(r"Parámetros estimados θ \(\d+\): (.*)", head)
    pnames = [s.strip() for s in pn.group(1).split(",") if s.strip()] if pn else None
    n, p = map(int, re.search(r"KExpr (\d+) (\d+)", txt).groups())
    if st is None or pnames is None:     # modelos divididos sin nombres en el archivo: del SBML
        st, pnames = names_from_sbml(name, n)
    vars_ = re.findall(r"^def (Rx\w*) : List [^\n]*:= \[$", txt, re.M)
    first = "Rx0" if "Rx0" in vars_ else None
    if first:
        R = rx_list(txt, first)
    else:
        R = [t for v in vars_ for t in rx_list(txt, v)]
    tq = re.search(r"def θq(?:L)? : [^=]*:= !?\[(.*)\]", txt).group(1)
    th = rationals(tq)
    xm = re.search(r"def xqL : [^=]*:= \[(.*)\]", txt) or re.search(r"def xq : [^=]*:= !\[(.*)\]", txt)
    xq = rationals(xm.group(1)) if xm else None
    G = None
    gm = re.search(r"^def G : [^\n]*:= !\[\n(.*?)\n\]", txt, re.S | re.M)
    if gm:
        pg = P("[" + gm.group(1) + "]")
        pg.eat("[")
        G = []
        while pg.peek() != "]":
            if pg.peek() == ",":
                pg.eat(","); continue
            G.append(pg.expr())
    return dict(n=n, p=p, states=st, pnames=pnames, R=R, theta=th, xq=xq, G=G)


def field(L, x):
    f = np.zeros(L["n"])
    for e, col in L["R"]:
        v = ev(e, x, L["theta"])
        for i, c in col:
            f[i] += c * v
    return f


def rr_rates(S, L, x, tau):
    """Derivadas de las especies (en las unidades del estado de Lean) según libRoadRunner."""
    m = S.m
    m.resetAll()
    for nm, v in S.fixed.items():
        if nm in S.gparams:
            try: m[nm] = v
            except Exception: pass
    for nm in L["pnames"]:                 # θ₀ de PEtab (independiente de los valores del archivo Lean)
        if nm in S.gparams and nm in S.idx:
            m[nm] = S.theta0[S.idx[nm]]
    mdl = m.model
    ids = list(mdl.getFloatingSpeciesIds())
    for j, nm in enumerate(L["states"]):
        if nm in ids:
            if nm in S.hosu:
                m[nm] = x[j]
            else:
                m[f"[{nm}]"] = x[j]
    if tau is not None:
        mdl.setTime(tau)
    na = m.getRatesOfChangeNamedArray()
    rates = dict(zip([c.strip("[]'") for c in na.colnames], np.asarray(na).ravel()))
    vol = {}
    import libsbml
    doc = libsbml.readSBMLFromString(m.getCurrentSBML())
    for sp in doc.getModel().getListOfSpecies():
        vol[sp.getId()] = m[sp.getCompartment()]
    out = np.full(L["n"], np.nan)
    for j, nm in enumerate(L["states"]):
        if nm in rates:
            out[j] = rates[nm] if nm in S.hosu else rates[nm] / vol[nm]
    return out


def uno(name, n_rand=5, seed=0):
    L = load_lean(name)
    S = PO.PSys(name)
    names = [s.split(" (")[0] for s in L["states"]]
    tau_j = [j for j, s in enumerate(L["states"]) if "tiempo" in s]
    L["states"] = names
    rng = np.random.default_rng(seed)
    x0 = np.array(L["xq"]) if L["xq"] is not None else np.ones(L["n"])
    pts = []
    for r in range(n_rand + 1):
        x = x0.copy() if r == 0 else np.abs(x0) * rng.uniform(0.5, 1.5, L["n"]) + rng.uniform(0.05, 1.0, L["n"]) * (np.abs(x0).mean() + 1e-3)
        for j in tau_j:
            x[j] = 0.0 if r == 0 else rng.uniform(0, 1)
        pts.append(x)
    errs, nst = [], 0
    for x in pts:
        fl = field(L, x)
        fr = rr_rates(S, L, x, x[tau_j[0]] if tau_j else None)
        ok = np.isfinite(fr)
        nst = int(ok.sum())
        scale = np.maximum(np.abs(fr[ok]), np.abs(fl[ok])) + 1e-9 * (np.abs(fr[ok]).max() + 1e-300)
        errs.append(float(np.max(np.abs(fl[ok] - fr[ok]) / scale)) if ok.any() else np.nan)
    # θ y x(0) del archivo Lean frente a PEtab/SBML
    th_petab = np.array([S.theta0[S.idx[nm]] for nm in L["pnames"]])
    th_lean = np.array(L["theta"])
    err_theta = float(np.max(np.abs(th_lean - th_petab) / np.maximum(np.abs(th_petab), 1e-300))) if len(th_lean) else 0.0
    err_x0 = None
    if L["xq"] is None and L.get("G") is not None:     # x(0) = G(θ): se evalúa G en θ del archivo
        L["xq"] = [float(ev(g, np.zeros(L["n"]), L["theta"])) for g in L["G"]]
    if L["xq"] is not None:
        m = S.m; m.resetAll()
        for nm, v in S.fixed.items():
            if nm in S.gparams:
                try: m[nm] = v
                except Exception: pass
        for nm in L["pnames"]:
            if nm in S.gparams and nm in S.idx:
                m[nm] = S.theta0[S.idx[nm]]
        m.reset()
        ids = set(m.model.getFloatingSpeciesIds())
        e = []
        for j, nm in enumerate(L["states"]):
            if nm in ids:
                v = m[nm] if nm in S.hosu else m[f"[{nm}]"]
                e.append(abs(L["xq"][j] - v) / max(abs(v), abs(L["xq"][j]), 1e-12))
        err_x0 = float(max(e)) if e else 0.0
    return dict(sistema=name, n_lean=L["n"], n_comparados=nst, puntos=len(pts),
                err_rel_max=float(np.nanmax(errs)), err_por_punto=errs,
                err_theta=err_theta, err_x0=err_x0, x0_de_theta=L.get("G") is not None)


if __name__ == "__main__":
    names = sys.argv[1:] or sorted(p.stem for p in MD.glob("*.lean"))
    res = []
    for nm in names:
        try:
            r = uno(nm)
        except Exception as e:
            r = dict(sistema=nm, error=repr(e))
        print(json.dumps(r), flush=True)
        res.append(r)
    if len(sys.argv) == 1:
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "fidelidad.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
