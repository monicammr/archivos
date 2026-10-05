#!/usr/bin/env python3
"""
Traductor SBML (PEtab) → Lean 4 (`KExpr`), para verificar con Lean, modelo por modelo, las
hipótesis de `KineticCheck.checked_model_hasFDerivAt`:

  * el campo es un `KExpr` (luego C¹ en su dominio);
  * los denominadores son > 0 en el ortante (dominio ⊇ ortante ≥ 0) para θ > 0;
  * el modelo es cuasi-positivo (los términos de consumo de cada especie contienen su factor).

Para cada sistema genera `../lean/Models/<Sistema>.lean` con
    def F : Fin n → KExpr n p := ![...]
    theorem check : checkModel F = true := by decide
    theorem diff ... := checked_model_hasFDerivAt F check ...
y escribe un informe con lo que no se pudo traducir y las condiciones numéricas
(θ₀ > 0, x₀(0) ≥ 0) comprobadas en Python.

Convenciones (las de roadrunner/AMICI): estado = especies no frontera, no constantes y sin regla
de asignación; d[x]/dt = Σ_r s_{x,r} v_r / V(x) si la especie está en concentración; θ =
parámetros PEtab con estimate = 1 presentes en el modelo; los demás parámetros, compartimentos y
especies frontera son constantes con su valor nominal (PEtab, si existe, o SBML).

Uso:  python3 sbml_to_lean.py [Sistema ...]      (por defecto, los de certify_systems.SYSTEMS)
"""
import sys, json, math
from fractions import Fraction
from pathlib import Path
import pandas as pd
import libsbml

HERE = Path(__file__).resolve().parent
BENCH = HERE / "bench" / "problems"
OUTDIR = HERE.parent / "lean" / "Models"
REPORT = HERE / "resultados" / "sbml_lean"

MAX_TERMS = 256       # límite de la expansión en monomios con signo


class Unsupported(Exception):
    pass


class NotConst(Exception):
    """La expresión depende de estados o de parámetros estimados."""
    def __init__(self, kind):
        self.kind = kind


# ---------------------------------------------------------------- árbol intermedio
# ('num', Fraction) | ('var', i) | ('par', j) | ('add', a, b) | ('sub', a, b) | ('mul', a, b)
# ('div', a, b) | ('npow', a, k) | ('rpow', a, Fraction) | ('exp', a) | ('log', a)

def num(q):
    return ('num', Fraction(q))


def frac_of(x):
    if isinstance(x, Fraction):
        return x
    if isinstance(x, int):
        return Fraction(x)
    if not math.isfinite(x):
        raise Unsupported(f"valor no finito {x}")
    return Fraction(repr(float(x)))


class Model:
    def __init__(self, name):
        folder = BENCH / name / "v1"
        doc = libsbml.readSBML(str(folder / "model.xml"))
        for opt in ("expandFunctionDefinitions", "expandInitialAssignments"):
            props = libsbml.ConversionProperties()
            props.addOption(opt, True)
            doc.convert(props)
        self.m = m = doc.getModel()
        self.name = name
        pt = pd.read_csv(folder / "parameters.tsv", sep="\t")
        est = pt[pt.get("estimate", 1) == 1] if "estimate" in pt.columns else pt
        gp = {p.getId() for p in m.getListOfParameters()}
        self.theta = [str(r.parameterId) for _, r in est.iterrows() if str(r.parameterId) in gp]
        self.theta0 = {str(r.parameterId): float(r.nominalValue) for _, r in est.iterrows()
                       if str(r.parameterId) in gp}
        nominal = {str(r.parameterId): float(r.nominalValue) for _, r in pt.iterrows()
                   if pd.notna(r.nominalValue)}
        # condiciones: parámetros que cambian por condición (se avisa)
        self.cond_params = []
        try:
            ct = pd.read_csv(folder / "conditions.tsv", sep="\t")
            self.cond_params = [c for c in ct.columns if c in gp]
        except FileNotFoundError:
            pass
        self.rules = {r.getVariable(): r.getMath() for r in m.getListOfRules()
                      if r.isAssignment()}
        self.rate_rules = [r.getVariable() for r in m.getListOfRules() if r.isRate()]
        self.states = [s.getId() for s in m.getListOfSpecies()
                       if not s.getBoundaryCondition() and not s.getConstant()
                       and s.getId() not in self.rules]
        self.sidx = {s: i for i, s in enumerate(self.states)}
        self.pidx = {p: j for j, p in enumerate(self.theta)}
        self.consts = {}
        for c in m.getListOfCompartments():
            self.consts[c.getId()] = c.getSize()
        for p in m.getListOfParameters():
            self.consts[p.getId()] = nominal.get(p.getId(), p.getValue())
        for s in m.getListOfSpecies():
            if s.getId() not in self.sidx:
                v = s.getInitialConcentration() if s.isSetInitialConcentration() \
                    else s.getInitialAmount()
                self.consts[s.getId()] = v
        self.ops = set()
        self.t_now = None          # instante (dentro del tramo) para evaluar piecewise
        self.uses_time = False     # el tiempo aparece fuera de condiciones → estado τ
        self.tau = len(self.states)

    # -------------------------------------------------------------- evaluación numérica
    def evalnum(self, a, t, depth=0):
        """Valor numérico de una expresión que sólo depende del tiempo y de constantes."""
        T = libsbml
        ty = a.getType()
        if depth > 200:
            raise Unsupported("reglas cíclicas")
        if ty == T.AST_INTEGER:
            return float(a.getInteger())
        if ty in (T.AST_REAL, T.AST_REAL_E, T.AST_RATIONAL):
            return a.getReal()
        if ty == T.AST_NAME_TIME:
            return t
        if ty == T.AST_CONSTANT_PI:
            return math.pi
        if ty == T.AST_CONSTANT_TRUE:
            return 1.0
        if ty == T.AST_CONSTANT_FALSE:
            return 0.0
        if ty == T.AST_NAME:
            nm = a.getName()
            if nm in self.sidx:
                raise NotConst("estado")
            if nm in self.pidx:
                raise NotConst("θ")
            if nm in self.rules:
                return self.evalnum(self.rules[nm], t, depth + 1)
            if nm in self.consts:
                return float(self.consts[nm])
            raise Unsupported(f"símbolo desconocido {nm}")
        k = [a.getChild(i) for i in range(a.getNumChildren())]
        ev = lambda x: self.evalnum(x, t, depth)
        if ty == T.AST_FUNCTION_PIECEWISE:
            for i in range(0, len(k) - 1, 2):
                if ev(k[i + 1]):
                    return ev(k[i])
            return ev(k[-1]) if len(k) % 2 == 1 else 0.0
        v = [ev(x) for x in k]
        ops = {T.AST_PLUS: lambda: sum(v), T.AST_TIMES: lambda: math.prod(v),
               T.AST_MINUS: lambda: -v[0] if len(v) == 1 else v[0] - v[1],
               T.AST_DIVIDE: lambda: v[0] / v[1], T.AST_POWER: lambda: v[0] ** v[1],
               T.AST_FUNCTION_POWER: lambda: v[0] ** v[1],
               T.AST_FUNCTION_EXP: lambda: math.exp(v[0]), T.AST_FUNCTION_LN: lambda: math.log(v[0]),
               T.AST_FUNCTION_SIN: lambda: math.sin(v[0]), T.AST_FUNCTION_COS: lambda: math.cos(v[0]),
               T.AST_RELATIONAL_LT: lambda: float(v[0] < v[1]),
               T.AST_RELATIONAL_LEQ: lambda: float(v[0] <= v[1]),
               T.AST_RELATIONAL_GT: lambda: float(v[0] > v[1]),
               T.AST_RELATIONAL_GEQ: lambda: float(v[0] >= v[1]),
               T.AST_RELATIONAL_EQ: lambda: float(v[0] == v[1]),
               T.AST_RELATIONAL_NEQ: lambda: float(v[0] != v[1]),
               T.AST_LOGICAL_AND: lambda: float(all(v)), T.AST_LOGICAL_OR: lambda: float(any(v)),
               T.AST_LOGICAL_NOT: lambda: float(not v[0])}
        if ty in ops:
            return ops[ty]()
        raise Unsupported(f"operación no soportada en evaluación: {a.getName()}")

    def has_time(self, a, depth=0):
        if a is None or depth > 200:
            return False
        if a.getType() == libsbml.AST_NAME_TIME:
            return True
        if a.getType() == libsbml.AST_NAME and a.getName() in self.rules:
            return self.has_time(self.rules[a.getName()], depth + 1)
        return any(self.has_time(a.getChild(i), depth) for i in range(a.getNumChildren()))

    def breakpoints(self):
        """Instantes en que cambia alguna condición (relación que involucra al tiempo)."""
        T = libsbml
        rel = (T.AST_RELATIONAL_LT, T.AST_RELATIONAL_LEQ, T.AST_RELATIONAL_GT,
               T.AST_RELATIONAL_GEQ, T.AST_RELATIONAL_EQ, T.AST_RELATIONAL_NEQ)
        bps = set()

        def visit(a, depth=0):
            if a is None or depth > 200:
                return
            if a.getType() == T.AST_NAME and a.getName() in self.rules:
                visit(self.rules[a.getName()], depth + 1)
                return
            if a.getType() in rel:
                if self.has_time(a):
                    try:
                        diff = lambda t: self.evalnum(a.getChild(0), t) - self.evalnum(a.getChild(1), t)
                        f0, f1 = diff(0.0), diff(1.0)
                    except NotConst as e:
                        raise Unsupported(f"condición que depende del {e.kind} (evento no fijo)")
                    if f1 == f0:
                        return
                    bps.add(-f0 / (f1 - f0))
                else:
                    try:
                        self.evalnum(a, 0.0)
                    except NotConst as e:
                        raise Unsupported(f"condición que depende del {e.kind} (evento no fijo)")
                return
            for i in range(a.getNumChildren()):
                visit(a.getChild(i), depth)
        for r in self.m.getListOfReactions():
            if r.getKineticLaw():
                visit(r.getKineticLaw().getMath())
        return sorted(bps)

    # -------------------------------------------------------------- MathML → árbol
    def tr(self, a, depth=0):
        if depth > 200:
            raise Unsupported("reglas de asignación cíclicas o demasiado profundas")
        t = a.getType()
        T = libsbml
        if t in (T.AST_INTEGER,):
            return num(a.getInteger())
        if t in (T.AST_REAL, T.AST_REAL_E, T.AST_RATIONAL):
            return num(frac_of(a.getReal()))
        if t == T.AST_NAME_TIME:
            self.uses_time = True
            self.ops.add('t')
            return ('var', self.tau)
        if t == T.AST_FUNCTION_PIECEWISE:
            self.ops.add('piecewise')
            kids = [a.getChild(i) for i in range(a.getNumChildren())]
            for i in range(0, len(kids) - 1, 2):
                try:
                    c = self.evalnum(kids[i + 1], self.t_now)
                except NotConst as e:
                    raise Unsupported(f"piecewise que depende del {e.kind}")
                if c:
                    return self.tr(kids[i], depth)
            return self.tr(kids[-1], depth) if len(kids) % 2 == 1 else num(0)
        if t == T.AST_NAME:
            nm = a.getName()
            if nm in self.sidx:
                return ('var', self.sidx[nm])
            if nm in self.pidx:
                return ('par', self.pidx[nm])
            if nm in self.rules:
                return self.tr(self.rules[nm], depth + 1)
            if nm in self.consts:
                return num(frac_of(self.consts[nm]))
            raise Unsupported(f"símbolo desconocido {nm}")
        if t == T.AST_CONSTANT_E:
            raise Unsupported("constante e")
        if t == T.AST_CONSTANT_PI:
            return num(frac_of(math.pi))
        if t == T.AST_TIMES:
            k, err = [], None
            for i in range(a.getNumChildren()):
                try:
                    k.append(self.tr(a.getChild(i), depth))
                except Unsupported as e:
                    err = e
            if any(c == ('num', Fraction(0)) for c in k):
                return num(0)
            if err is not None:
                raise err
        else:
            k = [self.tr(a.getChild(i), depth) for i in range(a.getNumChildren())]
        if t == T.AST_PLUS:
            self.ops.add('+')
            k = [c for c in k if c != ('num', Fraction(0))]
            if not k:
                return num(0)
            r = k[0]
            for c in k[1:]:
                r = ('num', r[1] + c[1]) if r[0] == 'num' and c[0] == 'num' else ('add', r, c)
            return r
        if t == T.AST_MINUS:
            self.ops.add('-')
            if len(k) == 1:
                return num(-k[0][1]) if k[0][0] == 'num' else ('sub', num(0), k[0])
            if k[0][0] == 'num' and k[1][0] == 'num':
                return num(k[0][1] - k[1][1])
            if k[1] == ('num', Fraction(0)):
                return k[0]
            return ('sub', k[0], k[1])
        if t == T.AST_TIMES:
            self.ops.add('*')
            if not k:
                return num(1)
            r = k[0]
            for c in k[1:]:
                r = ('mul', r, c)
            return r
        if t == T.AST_DIVIDE:
            self.ops.add('/')
            if k[0] == ('num', Fraction(0)):
                return num(0)
            return ('div', k[0], k[1])
        if t in (T.AST_POWER, T.AST_FUNCTION_POWER):
            base, ex = k
            if ex[0] == 'num':
                q = ex[1]
                if q.denominator == 1 and q >= 0:
                    self.ops.add('^n')
                    return ('npow', base, int(q))
                if q.denominator == 1:
                    self.ops.add('^-n')
                    return ('div', num(1), ('npow', base, int(-q)))
                self.ops.add('^r')
                return ('rpow', base, q)
            self.ops.add('^θ')
            return ('exp', ('mul', ex, ('log', base)))   # a^b = exp(b log a), a > 0
        if t == T.AST_FUNCTION_EXP:
            self.ops.add('exp')
            return ('exp', k[0])
        if t in (T.AST_FUNCTION_LN,):
            self.ops.add('log')
            return ('log', k[0])
        if t == T.AST_FUNCTION_ROOT:
            self.ops.add('^r')
            if len(k) == 1:
                return ('rpow', k[0], Fraction(1, 2))
            if k[0][0] == 'num':
                return ('rpow', k[1], 1 / k[0][1])
        raise Unsupported(f"operación no soportada: {a.getName() or libsbml.formulaToL3String(a)}")

    # -------------------------------------------------------------- monomios con signo
    def expand(self, e):
        """Lista de (signo, término) cuya suma es e; distribuye × y / sobre ±."""
        tag = e[0]
        if tag == 'num':
            q = e[1]
            return [] if q == 0 else [(1 if q > 0 else -1, num(abs(q)))]
        if tag == 'add':
            return self.expand(e[1]) + self.expand(e[2])
        if tag == 'sub':
            return self.expand(e[1]) + [(-s, t) for s, t in self.expand(e[2])]
        if tag == 'mul':
            A, B = self.expand(e[1]), self.expand(e[2])
            if len(A) * len(B) > MAX_TERMS:
                return [(1, e)]
            return [(sa * sb, ('mul', ta, tb)) for sa, ta in A for sb, tb in B]
        if tag == 'div':
            return [(s, ('div', t, e[2])) for s, t in self.expand(e[1])]
        return [(1, e)]

    def species_rhs(self):
        """Lista, por especie, de (coef ∈ ℚ, término) con d[x]/dt = Σ coef·término."""
        m = self.m
        rhs = [[] for _ in self.states]
        if self.rate_rules:
            raise Unsupported(f"reglas de tasa: {self.rate_rules}")
        for r in m.getListOfReactions():
            kl = r.getKineticLaw()
            if kl is None:
                raise Unsupported(f"reacción sin ley cinética {r.getId()}")
            v = self.tr(kl.getMath())
            terms = self.expand(v)
            net = {}
            for sr in r.getListOfReactants():
                if not sr.getConstant() and sr.isSetId() and m.getRule(sr.getId()):
                    raise Unsupported("estequiometría variable")
                net[sr.getSpecies()] = net.get(sr.getSpecies(), 0) - frac_of(sr.getStoichiometry())
            for sr in r.getListOfProducts():
                net[sr.getSpecies()] = net.get(sr.getSpecies(), 0) + frac_of(sr.getStoichiometry())
            for sp, c in net.items():
                if sp not in self.sidx or c == 0:
                    continue
                s = m.getSpecies(sp)
                if not s.getHasOnlySubstanceUnits():
                    vol = frac_of(self.consts[s.getCompartment()])
                    if vol == 0:
                        raise Unsupported("compartimento de volumen 0")
                    c = c / vol
                for sg, t in terms:
                    rhs[self.sidx[sp]].append((c * sg, t))
        return rhs


# ---------------------------------------------------------------- emisión Lean
def lean_q(q):
    q = Fraction(q)
    if q.denominator == 1:
        return f"({q.numerator} : ℚ)"
    return f"({q.numerator} / {q.denominator} : ℚ)"


def lean_expr(e):
    tag = e[0]
    if tag == 'num':
        return f"(.qconst {lean_q(e[1])})"
    if tag == 'var':
        return f"(.var {e[1]})"
    if tag == 'par':
        return f"(.par {e[1]})"
    if tag in ('add', 'sub', 'mul', 'div'):
        return f"(.{tag} {lean_expr(e[1])} {lean_expr(e[2])})"
    if tag == 'npow':
        return f"(.npow {lean_expr(e[1])} {e[2]})"
    if tag == 'rpow':
        return f"(.rpow {lean_expr(e[1])} (({lean_q(e[2])} : ℚ) : ℝ))"
    if tag == 'exp':
        return f"(.exp {lean_expr(e[1])})"
    if tag == 'log':
        return f"(.log {lean_expr(e[1])})"
    raise ValueError(tag)


def lean_rhs(terms):
    """Σ coef·término como cadena add/sub: producción con add, consumo con sub."""
    acc = None
    for c, t in terms:
        mag = abs(c)
        tt = t if mag == 1 else ('mul', num(mag), t)
        if acc is None:
            acc = tt if c > 0 else ('sub', num(0), tt)
        else:
            acc = ('add', acc, tt) if c > 0 else ('sub', acc, tt)
    return acc if acc is not None else num(0)


def leanid(name):
    return "".join(ch if ch.isalnum() else "_" for ch in name)


def emit(model, segs, ok):
    """segs: lista de (t_ini, t_fin, rhs). Un tramo → `F`; varios → `Fseg k`."""
    n, p = len(model.names_ext), len(model.theta)
    mod = leanid(model.name)
    head = [
        "import KineticCheck",
        "",
        f"/-! Modelo `{model.name}` traducido automáticamente de SBML por",
        "`certificados/sbml_to_lean.py`. No editar a mano.",
        "",
        f"Estados ({n}): " + ", ".join(model.names_ext),
        "",
        f"Parámetros estimados θ ({p}): " + ", ".join(model.theta),
    ]
    if len(segs) > 1:
        head.append("")
        head.append("Tramos (entradas por escalones en tiempos fijos): " +
                    ", ".join(f"[{a:g}, {b:g}]" for a, b, _ in segs))
    head += ["-/", "", "set_option maxRecDepth 100000", "set_option maxHeartbeats 0", "",
             "open KineticRegularity KineticCheck", "", f"namespace Models.{mod}", ""]
    body = []
    names = []
    for k, (a, b, rhs) in enumerate(segs):
        nm = "F" if len(segs) == 1 else f"F{k}"
        names.append(nm)
        comps = [lean_expr(lean_rhs(t)) for t in rhs]
        body += [f"def {nm} : Fin {n} → KExpr {n} {p} := ![",
                 ",\n".join("  " + c for c in comps), "]", ""]
        sfx = '' if len(segs) == 1 else k
        if ok:
            body += [f"theorem check{sfx} : checkModel {nm} = true := by decide +kernel", ""]
        else:
            body += ["/-- La comprobación sintáctica FALLA para este modelo (ver el informe JSON). -/",
                     f"theorem check_falla{sfx} : checkModel {nm} = false := by decide +kernel", ""]
    if not ok:
        pass
    elif len(segs) == 1:
        body += ["/-- Diferenciabilidad de la trayectoria (y positividad) para este modelo. -/",
                 "def diff := @checked_model_hasFDerivAt _ _ F check", ""]
    else:
        K = len(segs)
        body += [f"def Fseg : ℕ → Fin {n} → KExpr {n} {p}"]
        body += [f"  | {k} => F{k}" for k in range(K - 1)]
        body += [f"  | _ => F{K - 1}", ""]
        body += ["theorem check : ∀ k, checkModel (Fseg k) = true := by", "  intro k",
                 "  match k with"]
        body += [f"  | {k} => exact check{k}" for k in range(K - 1)]
        body += [f"  | _ + {K - 1} => exact check{K - 1}", ""]
        body += ["/-- Diferenciabilidad de la trayectoria en todos los tramos. -/",
                 "def diff := @checked_segments_hasFDerivAt _ _ Fseg check", ""]
    tail = [f"end Models.{mod}", ""]
    if ok:
        tail += [f"#print axioms Models.{mod}.diff", ""]
    lines = head + body + tail
    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / f"{mod}.lean").write_text("\n".join(lines))
    return mod


# ---------------------------------------------------------------- comprobación previa en Python
def py_signs(model, rhs):
    """Réplica en Python de okOrth y qp (para el informe y para localizar fallos)."""
    def nonneg(e):
        t = e[0]
        if t == 'num': return e[1] >= 0
        if t in ('var', 'par'): return True
        if t in ('add', 'mul', 'div'): return nonneg(e[1]) and nonneg(e[2])
        if t in ('npow', 'rpow'): return nonneg(e[1])
        if t == 'exp': return True
        return False

    def pos(e):
        t = e[0]
        if t == 'num': return e[1] > 0
        if t == 'par': return True
        if t == 'add': return (pos(e[1]) and nonneg(e[2])) or (nonneg(e[1]) and pos(e[2]))
        if t in ('mul', 'div'): return pos(e[1]) and pos(e[2])
        if t in ('npow', 'rpow'): return pos(e[1])
        if t == 'exp': return True
        return False

    def okorth(e):
        t = e[0]
        if t in ('num', 'var', 'par'): return True
        if t in ('add', 'sub', 'mul'): return okorth(e[1]) and okorth(e[2])
        if t == 'div': return okorth(e[1]) and okorth(e[2]) and pos(e[2])
        if t == 'npow': return okorth(e[1])
        if t in ('rpow', 'log'): return okorth(e[1]) and pos(e[1])
        if t == 'exp': return okorth(e[1])
        return False

    def van(i, e):
        t = e[0]
        if t == 'num': return e[1] == 0
        if t == 'var': return e[1] == i
        if t in ('add', 'sub'): return van(i, e[1]) and van(i, e[2])
        if t == 'mul': return van(i, e[1]) or van(i, e[2])
        if t == 'div': return van(i, e[1])
        if t == 'npow': return van(i, e[1]) and e[2] > 0
        return False

    bad_dom, bad_qp = [], []
    for i, terms in enumerate(rhs):
        for c, t in terms:
            if not okorth(t):
                bad_dom.append((model.names_ext[i], t))
            if c < 0 and not van(i, t):
                bad_qp.append((model.names_ext[i], 'consumo sin factor', t))
            if c > 0 and not (nonneg(t) or van(i, t)):
                bad_qp.append((model.names_ext[i], 'producción de signo indefinido', t))
    return bad_dom, bad_qp


def show(e, model):
    t = e[0]
    if t == 'num': return str(e[1])
    if t == 'var': return model.names_ext[e[1]]
    if t == 'par': return model.theta[e[1]]
    if t in ('add', 'sub', 'mul', 'div'):
        op = {'add': '+', 'sub': '-', 'mul': '*', 'div': '/'}[t]
        return f"({show(e[1], model)} {op} {show(e[2], model)})"
    if t == 'npow': return f"{show(e[1], model)}^{e[2]}"
    if t == 'rpow': return f"{show(e[1], model)}^{e[2]}"
    return f"{t}({show(e[1], model)})"


def process(name, T):
    rep = {"sistema": name, "T": T}
    try:
        model = Model(name)
        rep.update(n_estados=len(model.states), n_theta=len(model.theta),
                   reacciones=model.m.getNumReactions(), eventos=model.m.getNumEvents(),
                   parametros_por_condicion=model.cond_params)
        if model.m.getNumEvents():
            raise Unsupported("eventos SBML (se cubren con EventSystems, no con este traductor)")
        bps = [b for b in model.breakpoints() if 0 < b < T]
        edges = [0.0] + bps + [T]
        segs = []
        for a, b in zip(edges[:-1], edges[1:]):
            model.t_now = (a + b) / 2
            segs.append((a, b, model.species_rhs()))
        model.names_ext = list(model.states)
        if model.uses_time:
            model.names_ext.append("τ (tiempo)")
            for _, _, rhs in segs:
                rhs.append([(Fraction(1), num(1))])
        rep["tramos"] = [[a, b] for a, b, _ in segs]
        rep["tiempo_como_estado"] = model.uses_time
        rep["operaciones"] = sorted(model.ops)
        rep["theta0_positivo"] = all(v > 0 for v in model.theta0.values())
        rep["theta0_no_positivos"] = [k for k, v in model.theta0.items() if not v > 0]
        x0 = []
        for s_ in model.states:
            sp = model.m.getSpecies(s_)
            v = sp.getInitialConcentration() if sp.isSetInitialConcentration() \
                else sp.getInitialAmount()
            x0.append(v)
        rep["x0_no_negativo"] = all(v >= 0 for v in x0 if not math.isnan(v))
        rep["x0_nan"] = [s_ for s_, v in zip(model.states, x0) if math.isnan(v)]
        bad_dom, bad_qp = [], []
        for _, _, rhs in segs:
            d_, q_ = py_signs(model, rhs)
            bad_dom += d_; bad_qp += q_
        rep["fallos_dominio"] = [f"{s_}: {show(t, model)}" for s_, t in bad_dom][:20]
        rep["fallos_cuasipositividad"] = [f"{s_}: {k}: {show(t, model)}"
                                         for s_, k, t in bad_qp][:20]
        rep["n_fallos_dominio"] = len(bad_dom)
        rep["n_fallos_cuasipositividad"] = len(bad_qp)
        rep["prediccion_check"] = not bad_dom and not bad_qp
        rep["lean"] = f"Models/{emit(model, segs, rep['prediccion_check'])}.lean"
        rep["traducido"] = True
    except Unsupported as e:
        rep["traducido"] = False
        rep["motivo"] = str(e)
    return rep


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    from certify_systems import SYSTEMS, T_END_OVERRIDE
    tends = {nm: T_END_OVERRIDE.get(nm, t) for nm, _, t, _ in SYSTEMS}
    names = sys.argv[1:] or list(tends)
    REPORT.mkdir(parents=True, exist_ok=True)
    out = []
    for nm in names:
        r = process(nm, tends.get(nm, 50.0))
        out.append(r)
        print(json.dumps({k: r.get(k) for k in ("sistema", "traducido", "motivo", "n_estados",
                                                 "n_theta", "tramos", "operaciones", "n_fallos_dominio",
                                                 "n_fallos_cuasipositividad")},
                         ensure_ascii=False), flush=True)
        (REPORT / f"{nm}.json").write_text(json.dumps(r, indent=1, ensure_ascii=False,
                                                      default=str))
