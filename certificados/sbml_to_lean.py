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

def flatten_add(e):
    """Sumandos de un árbol de sumas."""
    if e[0] == 'add':
        return flatten_add(e[1]) + flatten_add(e[2])
    return [e]


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
        m0 = doc.getModel()
        # símbolos de los que depende cada asignación inicial (antes de expandirlas)
        rules0 = {r.getVariable(): r.getMath() for r in m0.getListOfRules() if r.isAssignment()}

        def names_in(a, depth=0):
            out = set()
            if a is None or depth > 50:
                return out
            if a.getType() == libsbml.AST_NAME:
                nm = a.getName()
                out.add(nm)
                if nm in rules0:
                    out |= names_in(rules0[nm], depth + 1)
            for i in range(a.getNumChildren()):
                out |= names_in(a.getChild(i), depth)
            return out
        self.ia_names = {ia.getSymbol(): names_in(ia.getMath())
                         for ia in m0.getListOfInitialAssignments()}
        self.ia_math = {ia.getSymbol(): ia.getMath().deepCopy()
                        for ia in m0.getListOfInitialAssignments()}
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
        # escala log/log10 ⇒ θ > 0 por construcción (un nominal 0 es un artefacto de PEtab)
        self.logscale = {str(r.parameterId): str(r.get("parameterScale", "lin")).startswith("log")
                         for _, r in est.iterrows() if str(r.parameterId) in gp}
        self.positive = {t: (self.theta0[t] > 0 or self.logscale[t]) for t in self.theta}
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
        thset = set(self.theta)
        self.x0_dep_theta = sorted(s for s in self.states
                                   if self.ia_names.get(s, set()) & thset)
        try:
            ct = pd.read_csv(folder / "conditions.tsv", sep="\t")
            self.x0_por_condicion = [c for c in ct.columns if c in self.sidx]
        except FileNotFoundError:
            self.x0_por_condicion = []
        # θ₀ numérico (nominal 0 en escala log → 1e-12, como en el pipeline)
        self.theta_vals = [self.theta0[t] if self.theta0[t] > 0 or not self.logscale[t]
                           else 1e-12 for t in self.theta]
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

    def fixed_time_events(self):
        """Eventos `time >= c` (c constante) que asignan valores constantes a símbolos que no son
        estados (entradas). Devuelve [(c, {símbolo: valor})]; si no es de ese tipo, Unsupported."""
        T = libsbml
        evs = []
        for ev in self.m.getListOfEvents():
            if ev.isSetDelay():
                raise Unsupported("evento con retardo")
            tr_ = ev.getTrigger().getMath()
            if tr_.getType() not in (T.AST_RELATIONAL_GEQ, T.AST_RELATIONAL_GT) or \
                    tr_.getChild(0).getType() != T.AST_NAME_TIME:
                raise Unsupported("evento no disparado por un tiempo fijo")
            try:
                c = self.evalnum(tr_.getChild(1), 0.0)
            except NotConst as e:
                raise Unsupported(f"tiempo de evento que depende del {e.kind}")
            asg = {}
            for ea in ev.getListOfEventAssignments():
                var = ea.getVariable()
                if var in self.sidx:
                    raise Unsupported("evento que reasigna un estado")
                try:
                    asg[var] = self.evalnum(ea.getMath(), c)
                except NotConst as e:
                    raise Unsupported(f"asignación de evento que depende del {e.kind}")
            evs.append((c, asg))
        return sorted(evs, key=lambda e: e[0])

    def apply_events(self, evs, t):
        """Fija los valores de las entradas vigentes en el instante t."""
        if not hasattr(self, "_consts0"):
            self._consts0 = dict(self.consts)
        self.consts = dict(self._consts0)
        for c, asg in evs:
            if c <= t:
                self.consts.update(asg)

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
            # (… + b + …) − b  →  (… + …)   (p. ej. N − detectados en Okuonghae)
            summ = flatten_add(k[0])
            if len(summ) > 1 and k[1] in summ:
                summ.remove(k[1])
                r = summ[0]
                for c_ in summ[1:]:
                    r = ('add', r, c_)
                return r
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
        if getattr(self, 'atomize', False) and tag in ('add', 'sub') and e[1][0] == 'num':
            b = e[2]
            if b[0] == 'mul' and b[1] == ('num', Fraction(1)):
                b = b[2]          # 1·θⱼ = θⱼ
            if b[0] == 'par':
                # q ± θⱼ: un único factor (su signo se comprueba con cotas en θ₀)
                return [(1, (tag, e[1], b))]
        if tag == 'num':
            q = e[1]
            return [] if q == 0 else [(1 if q > 0 else -1, num(abs(q)))]
        if tag == 'add':
            return self.expand(e[1]) + self.expand(e[2])
        if tag == 'sub':
            # q − e^x (q ≥ 1) es un único factor (≥ 0 si x ≤ 0): no se separa
            if e[1][0] == 'num' and e[1][1] >= 1 and e[2][0] == 'exp':
                return [(1, e)]
            # a − b·(c − 1) = a + b·(1 − c)
            q = e[2]
            if q[0] == 'mul' and q[2][0] == 'sub' and q[2][2] == ('num', Fraction(1)):
                return self.expand(('add', e[1], ('mul', q[1], ('sub', ('num', Fraction(1)), q[2][1]))))
            # represión de Hill: a − b·(a − c)/(b + d) = (a·d + b·c)/(b + d)  (si b + d ≠ 0,
            # que el dominio exige); deja la tasa como suma de términos no negativos
            a, q = e[1], e[2]
            if q[0] == 'div' and q[1][0] == 'mul' and q[1][2][0] == 'sub' and \
                    q[1][2][1] == a and q[2][0] == 'add' and q[2][1] == q[1][1]:
                b, c, d = q[1][1], q[1][2][2], q[2][2]
                return self.expand(('div', ('add', ('mul', a, d), ('mul', b, c)), q[2]))
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
        return f"(KExpr.qconst {lean_q(e[1])})"
    if tag == 'var':
        return f"(KExpr.var {e[1]})"
    if tag == 'par':
        return f"(KExpr.par {e[1]})"
    if tag in ('add', 'sub', 'mul', 'div'):
        return f"(KExpr.{tag} {lean_expr(e[1])} {lean_expr(e[2])})"
    if tag == 'npow':
        return f"(KExpr.npow {lean_expr(e[1])} {e[2]})"
    if tag == 'rpow':
        return f"(KExpr.rpow {lean_expr(e[1])} (({lean_q(e[2])} : ℚ) : ℝ))"
    if tag == 'exp':
        return f"(KExpr.exp {lean_expr(e[1])})"
    if tag == 'log':
        return f"(KExpr.log {lean_expr(e[1])})"
    raise ValueError(tag)


def balanced_sum(ts):
    """Suma en árbol balanceado (profundidad logarítmica)."""
    if not ts:
        return num(0)
    while len(ts) > 1:
        ts = [('add', ts[k], ts[k + 1]) if k + 1 < len(ts) else ts[k]
              for k in range(0, len(ts), 2)]
    return ts[0]


def lean_rhs(terms):
    """Σ coef·término = (Σ producción) − (Σ consumo), cada suma balanceada."""
    prod, cons = [], []
    for c, t in terms:
        mag = abs(c)
        tt = t if mag == 1 else ('mul', num(mag), t)
        (prod if c > 0 else cons).append(tt)
    if not cons:
        return balanced_sum(prod)
    return ('sub', balanced_sum(prod), balanced_sum(cons))


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
    mask = ", ".join("true" if model.positive[t] else "false" for t in model.theta)
    body = ["/-- Máscara de parámetros con valor nominal > 0 (los demás: signo arbitrario). -/",
            f"def pos : Fin {p} → Bool := ![{mask}]", ""]
    names = []
    for k, (a, b, rhs) in enumerate(segs):
        nm = "F" if len(segs) == 1 else f"F{k}"
        names.append(nm)
        comps = [lean_expr(lean_rhs(t)) for t in rhs]
        body += [f"def {nm} : Fin {n} → KExpr {n} {p} := ![",
                 ",\n".join("  " + c for c in comps), "]", ""]
        sfx = '' if len(segs) == 1 else k
        if ok:
            body += [f"theorem check{sfx} : checkModel pos {nm} = true := by decide +kernel", ""]
        else:
            body += ["/-- La comprobación sintáctica FALLA para este modelo (ver el informe JSON). -/",
                     f"theorem check_falla{sfx} : checkModel pos {nm} = false := by decide +kernel", ""]
    init_exprs = None
    if ok and model.x0_dep_theta:
        try:
            model.t_now = 0.0
            init_exprs = []
            for s_, v in zip(model.states, model.x0_vals):
                if s_ in model.ia_math:
                    e = model.tr(model.ia_math[s_])
                    if 'var' in repr(e):
                        raise Unsupported("condición inicial que depende de otros estados")
                    init_exprs.append(e)
                else:
                    init_exprs.append(num(frac_of(v)))
            if model.uses_time:
                init_exprs.append(num(0))
        except Unsupported:
            init_exprs = None
    final_ok = ok and not model.x0_dep_theta and \
        all(math.isfinite(v) for v in model.x0_vals)
    init_ok = ok and init_exprs is not None and len(segs) == 1
    if init_ok:
        tq = ", ".join(lean_q(frac_of(v)) for v in model.theta_vals)
        body += ["/-- θ₀ nominal (PEtab), en racionales exactos. -/",
                 f"def θq : Fin {p} → ℚ := ![{tq}]", "",
                 "/-- Condición inicial x₀(θ) (asignaciones iniciales de SBML). -/",
                 f"def G : Fin {n} → KExpr {n} {p} := ![",
                 ",\n".join("  " + lean_expr(e) for e in init_exprs), "]", "",
                 "theorem theta_ok : checkPosParams pos θq = true := by decide +kernel", "",
                 "theorem init_ok : checkInit pos G = true := by decide +kernel", ""]
    if final_ok:
        tq = ", ".join(lean_q(frac_of(v)) for v in model.theta_vals)
        xq = ", ".join(lean_q(frac_of(v)) for v in model.x0_vals)
        body += ["/-- θ₀ nominal (PEtab), en racionales exactos. -/",
                 f"def θq : Fin {p} → ℚ := ![{tq}]", "",
                 "/-- Condiciones iniciales nominales (no dependen de θ). -/",
                 f"def xq : Fin {n} → ℚ := ![{xq}]", "",
                 "theorem theta_ok : checkPosParams pos θq = true := by decide +kernel", "",
                 "theorem x0_ok : checkNonneg xq = true := by decide +kernel", ""]
    if not ok and len(segs) == 1:
        body += ["/-- **Diferenciabilidad con condiciones explícitas.** El campo es C¹ en su dominio",
                 "(demostrado para todo `KExpr`); quedan como condiciones que la solución nominal",
                 "exista en [0, T] y permanezca en el dominio (para este modelo el comprobador",
                 "sintáctico no puede garantizarlo; ver `check_falla`). -/",
                 "def diff := @kinetic_hasFDerivAt _ _ F", ""]
    if not ok:
        pass
    elif len(segs) == 1:
        body += ["/-- Diferenciabilidad de la trayectoria (y positividad) para este modelo. -/",
                 "def diff := @checked_model_hasFDerivAt _ _ pos F check", ""]
        if final_ok:
            body += ["/-- Teorema final: la única condición restante es que la solución nominal",
                     "exista en [0, T]. -/",
                     "def final := @checked_model_final _ _ pos F check θq theta_ok xq x0_ok", ""]
        if init_ok:
            body += ["/-- Teorema final (condición inicial dependiente de θ): la única condición",
                     "restante es que la solución nominal exista en [0, T]. -/",
                     "def final := @checked_model_final_init _ _ pos F check G init_ok θq theta_ok",
                     ""]
    else:
        K = len(segs)
        body += [f"def Fseg : ℕ → Fin {n} → KExpr {n} {p}"]
        body += [f"  | {k} => F{k}" for k in range(K - 1)]
        body += [f"  | _ => F{K - 1}", ""]
        body += ["theorem check : ∀ k, checkModel pos (Fseg k) = true := by", "  intro k",
                 "  match k with"]
        body += [f"  | {k} => exact check{k}" for k in range(K - 1)]
        body += [f"  | _ + {K - 1} => exact check{K - 1}", ""]
        body += ["/-- Diferenciabilidad de la trayectoria en todos los tramos. -/",
                 "def diff := @checked_segments_hasFDerivAt _ _ pos Fseg check", ""]
        if final_ok:
            body += ["/-- Teorema final: la única condición restante es que la solución nominal",
                     "exista en cada tramo. -/",
                     "def final := @checked_segments_final _ _ pos Fseg check θq theta_ok xq x0_ok",
                     ""]
    tail = [f"end Models.{mod}", ""]
    if ok or len(segs) == 1:
        tail += [f"#print axioms Models.{mod}.diff", ""]
    if final_ok or init_ok:
        tail += [f"#print axioms Models.{mod}.final", ""]
    lines = head + body + tail
    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / f"{mod}.lean").write_text("\n".join(lines))
    return mod


# ---------------------------------------------------------------- comprobación previa en Python
def py_signs(model, rhs):
    """Réplica en Python de okOrth y qp (para el informe y para localizar fallos)."""
    posmask = [model.positive[t] for t in model.theta]
    def nonneg(e):
        t = e[0]
        if t == 'num': return e[1] >= 0
        if t == 'var': return True
        if t == 'par': return posmask[e[1]]
        if t in ('add', 'mul', 'div'): return nonneg(e[1]) and nonneg(e[2])
        if t in ('npow', 'rpow'): return nonneg(e[1])
        if t == 'exp': return True
        return False

    def pos(e):
        t = e[0]
        if t == 'num': return e[1] > 0
        if t == 'par': return posmask[e[1]]
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
        evs = model.fixed_time_events() if model.m.getNumEvents() else []
        rep["eventos_tiempo_fijo"] = [[c, {k: v for k, v in a.items()}] for c, a in evs]
        bps = sorted(set([b for b in model.breakpoints() if 0 < b < T] +
                         [c for c, _ in evs if 0 < c < T]))
        edges = [0.0] + bps + [T]
        segs = []
        for a, b in zip(edges[:-1], edges[1:]):
            model.t_now = (a + b) / 2
            if evs:
                model.apply_events(evs, model.t_now)
            segs.append((a, b, model.species_rhs()))
        if evs:
            model.apply_events(evs, -1.0)   # valores iniciales para el resto del informe
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
        rep["theta_signo_libre"] = [t for t in model.theta if not model.positive[t]]
        rep["theta_log_nominal_0"] = [t for t in model.theta
                                      if model.logscale[t] and not model.theta0[t] > 0]
        x0 = []
        for s_ in model.states:
            sp = model.m.getSpecies(s_)
            v = sp.getInitialConcentration() if sp.isSetInitialConcentration() \
                else sp.getInitialAmount()
            x0.append(v)
        model.x0_vals = list(x0) + ([0.0] if model.uses_time else [])
        rep["x0_depende_de_theta"] = model.x0_dep_theta
        rep["x0_por_condicion"] = model.x0_por_condicion
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
        rep["red"] = None
        init_exprs = None
        if len(segs) == 1 and all(math.isfinite(v) for v in model.x0_vals):
            if model.x0_dep_theta:
                model.t_now = 0.0
                init_exprs = []
                try:
                    for s_, v in zip(model.states, model.x0_vals):
                        if s_ in model.ia_math:
                            e = model.tr(model.ia_math[s_])
                            if 'var' in repr(e):
                                raise Unsupported("x0 depende de estados")
                            init_exprs.append(e)
                        else:
                            init_exprs.append(num(frac_of(v)))
                    if model.uses_time:
                        init_exprs.append(num(0))
                except Unsupported:
                    init_exprs = "no"
        if rep["prediccion_check"] and len(segs) == 1 and \
                all(math.isfinite(v) for v in model.x0_vals) and init_exprs != "no":
            big = len(model.names_ext) > 500 and init_exprs is None
            mod_, estado = (emit_network_split(model, segs[0][2]) if big
                            else emit_network(model, segs[0][2], init_exprs))
            rep["red"] = estado
        elif rep["prediccion_check"] and len(segs) > 1 and not model.x0_dep_theta and \
                all(math.isfinite(v) for v in model.x0_vals):
            mod_, estado = emit_network_segments(model, segs)
            rep["red"] = estado
        if rep["red"] == "crecimiento" and init_exprs is None and \
                all(math.isfinite(v) for v in model.x0_vals):
            # crecimiento cuadrático: existencia en un horizonte finito (Riccati)
            mod_, estado = emit_riccati(model, segs[0][2], T)
            if estado == "riccati":
                rep["red"] = "riccati"
        if rep["red"] not in ("ok", "riccati") and len(segs) == 1 and init_exprs != "no" and \
                all(math.isfinite(v) for v in model.x0_vals):
            # positividad estricta (Σ = especies con x₀ > 0)
            mod_, estado, bad = emit_strict(model, segs[0][2], init_exprs)
            if estado == "checkNetS":
                # reintento: factores q ± θⱼ enteros, con cotas comprobadas en θ₀
                model.atomize = True
                model.t_now = (segs[0][0] + segs[0][1]) / 2
                rhs2 = model.species_rhs()
                if model.uses_time:
                    rhs2.append([(Fraction(1), num(1))])
                mod2, estado2, bad2 = emit_strict(model, rhs2, init_exprs)
                model.atomize = False
                if estado2 == "estricta":
                    mod_, estado, bad = mod2, estado2, bad2
            rep["estricta"] = estado
            rep["estricta_fallos"] = [f"{k}: {show(t, model)}" for k, t in bad][:20]
            if estado == "estricta":
                rep["red"] = "estricta"
        rep["teorema_final"] = "def final" in (OUTDIR / rep["lean"].split("/")[1]).read_text()
        rep["traducido"] = True
    except Unsupported as e:
        rep["traducido"] = False
        rep["motivo"] = str(e)
    return rep


# ================================================================ forma de red (KineticNetwork)
def _varfree(e):
    return 'var' not in repr(e)


def _py_nonneg(e, pos):
    t = e[0]
    if t == 'num': return e[1] >= 0
    if t == 'var': return True
    if t == 'par': return pos[e[1]]
    if t in ('add', 'mul', 'div'): return _py_nonneg(e[1], pos) and _py_nonneg(e[2], pos)
    if t in ('npow', 'rpow'): return _py_nonneg(e[1], pos)
    if t == 'exp': return True
    return False


def _py_pos(e, pos):
    t = e[0]
    if t == 'num': return e[1] > 0
    if t == 'par': return pos[e[1]]
    if t == 'add': return (_py_pos(e[1], pos) and _py_nonneg(e[2], pos)) or \
        (_py_nonneg(e[1], pos) and _py_pos(e[2], pos))
    if t in ('mul', 'div'): return _py_pos(e[1], pos) and _py_pos(e[2], pos)
    if t in ('npow', 'rpow'): return _py_pos(e[1], pos)
    if t == 'exp': return True
    return False


def _py_okorth(e, pos):
    t = e[0]
    if t in ('num', 'var', 'par'): return True
    if t in ('add', 'sub', 'mul'): return _py_okorth(e[1], pos) and _py_okorth(e[2], pos)
    if t == 'div': return _py_okorth(e[1], pos) and _py_okorth(e[2], pos) and _py_pos(e[2], pos)
    if t == 'npow': return _py_okorth(e[1], pos)
    if t in ('rpow', 'log'): return _py_okorth(e[1], pos) and _py_pos(e[1], pos)
    if t == 'exp': return _py_okorth(e[1], pos)
    return False


def _py_van(i, e):
    t = e[0]
    if t == 'num': return e[1] == 0
    if t == 'var': return e[1] == i
    if t in ('add', 'sub'): return _py_van(i, e[1]) and _py_van(i, e[2])
    if t == 'mul': return _py_van(i, e[1]) or _py_van(i, e[2])
    if t == 'div': return _py_van(i, e[1])
    if t == 'npow': return _py_van(i, e[1]) and e[2] > 0
    return False


def _py_lowerpos(e, pos):
    if e[0] == 'add':
        a, b = e[1], e[2]
        return (_varfree(a) and _varfree(b) and _py_pos(e, pos)) or \
            (_py_lowerpos(a, pos) and _py_nonneg(b, pos)) or \
            (_py_nonneg(a, pos) and _py_lowerpos(b, pos))
    return _varfree(e) and _py_pos(e, pos)


def _py_linok(e, pos):
    t = e[0]
    if t == 'var': return True
    if t == 'add':
        return (_varfree(e[1]) and _varfree(e[2])) or (_py_linok(e[1], pos) and _py_linok(e[2], pos))
    if t == 'mul':
        a, b = e[1], e[2]
        return (_varfree(a) and _varfree(b)) or \
            (_varfree(a) and _py_nonneg(a, pos) and _py_linok(b, pos)) or \
            (_py_linok(a, pos) and _varfree(b) and _py_nonneg(b, pos))
    if t == 'div':
        a, b = e[1], e[2]
        return (_varfree(a) and _varfree(b)) or \
            (_py_linok(a, pos) and _py_nonneg(a, pos) and _py_lowerpos(b, pos))
    return _varfree(e)


def network_of(rhs):
    """rhs por especie → lista de (término, columna [(i, coef)])."""
    terms, idx = [], {}
    for i, lst in enumerate(rhs):
        for c, t in lst:
            k = repr(t)
            if k not in idx:
                idx[k] = len(terms)
                terms.append([t, {}])
            col = terms[idx[k]][1]
            col[i] = col.get(i, Fraction(0)) + Fraction(c)
    return [(t, [(i, s) for i, s in sorted(col.items()) if s != 0]) for t, col in terms]


def net_checks(Rx, pos):
    """Réplica de checkNet; devuelve la lista de fallos."""
    bad = []
    for V, col in Rx:
        if not _py_okorth(V, pos):
            bad.append(('dominio', V))
        for i, s in col:
            if s < 0 and not _py_van(i, V):
                bad.append(('consumo', V))
            if s >= 0 and not (_py_nonneg(V, pos) or _py_van(i, V)):
                bad.append(('produccion', V))
    return bad


def find_weights(Rx, n, pos):
    """c ∈ ℚⁿ, cᵢ ≥ 1, con checkGrowth = true (programación lineal + verificación exacta)."""
    import numpy as np
    from scipy.optimize import linprog
    A_ub, A_eq = [], []
    for V, col in Rx:
        row = np.zeros(n)
        for i, s in col:
            row[i] += float(s)
        if not row.any():
            continue
        nn, lin = _py_nonneg(V, pos), _py_linok(V, pos)
        if nn and lin:
            continue
        if nn and not lin:
            A_ub.append(row)          # w ≤ 0
        elif lin and not nn:
            A_ub.append(-row)         # w ≥ 0
        else:
            A_eq.append(row)          # w = 0
    sol = linprog(np.ones(n), A_ub=np.array(A_ub) if A_ub else None,
                  b_ub=np.zeros(len(A_ub)) if A_ub else None,
                  A_eq=np.array(A_eq) if A_eq else None,
                  b_eq=np.zeros(len(A_eq)) if A_eq else None,
                  bounds=[(1, None)] * n, method="highs")
    if sol.status != 0:
        return None
    for den in (1, 10, 100, 1000, 10000, 10 ** 6):
        c = [max(Fraction(1), Fraction(x).limit_denominator(den)) for x in sol.x]
        if growth_ok_exact(Rx, c, pos):
            return c
    return None


def growth_ok_exact(Rx, c, pos):
    for V, col in Rx:
        w = sum((c[i] * s for i, s in col), Fraction(0))
        if w == 0:
            continue
        if w < 0 and _py_nonneg(V, pos):
            continue
        if w > 0 and _py_linok(V, pos):
            continue
        return False
    return True


def lean_vec(name, m, typ, elems, default):
    """Vector `Fin m → typ`: notación ![…] si es corto; lista + getD si es largo
    (la notación ![…] desborda la pila del analizador para miles de elementos)."""
    if len(set(elems)) == 1 and m > 0:
        return [f"def {name} : Fin {m} → {typ} := fun _ => {elems[0]}"]
    if m <= 500:
        return [f"def {name} : Fin {m} → {typ} := ![{', '.join(elems)}]"]
    return [f"def {name}L : List {typ} := [{', '.join(elems)}]",
            f"def {name} : Fin {m} → {typ} := fun j => {name}L.getD j.val {default}"]


def emit_network(model, rhs, init_exprs):
    """Archivo Lean en forma de red con el teorema final sin condiciones pendientes."""
    n, p = len(model.names_ext), len(model.theta)
    pos = [model.positive[t] for t in model.theta]
    Rx = network_of(rhs)
    if net_checks(Rx, pos):
        return None, "checkNet"
    c = find_weights(Rx, n, pos)
    if c is None:
        return None, "crecimiento"
    mod = leanid(model.name)
    mask = ", ".join("true" if b else "false" for b in pos)
    tq = ", ".join(lean_q(frac_of(v)) for v in model.theta_vals)
    lines = [
        "import KineticNetwork", "",
        f"/-! Modelo `{model.name}` (forma de red), traducido automáticamente de SBML por",
        "`certificados/sbml_to_lean.py`. No editar a mano.", "",
        f"Estados ({n}): " + ", ".join(model.names_ext), "",
        f"Parámetros estimados θ ({p}): " + ", ".join(model.theta),
        "-/", "", "set_option maxRecDepth 100000", "set_option maxHeartbeats 0", "",
        "open KineticRegularity KineticCheck KineticNetwork", "",
        f"namespace Models.{mod}", "",
        "/-- Máscara de parámetros positivos (nominal > 0 o escala log). -/",
        *lean_vec("pos", p, "Bool", [("true" if b else "false") for b in pos], "false"), "",
        f"/-- Términos de velocidad con su columna estequiométrica ({len(Rx)} términos). -/",
        f"def Rx : List (KExpr {n} {p} × List (Fin {n} × ℚ)) := ["]
    def item(V, col):
        cs = ", ".join(f"({i}, {lean_q(s)})" for i, s in col)
        return f"  ({lean_expr(V)}, [{cs}])"
    CH = 400
    cvec = "\n".join(lean_vec("c", n, "ℚ", [lean_q(x) for x in c], "1"))
    if len(Rx) <= CH:
        lines += [",\n".join(item(V, col) for V, col in Rx), "]", "",
                  "/-- El campo del modelo: `Fᵢ = Σ_r coef_r(i) · V_r`. -/",
                  f"def F : Fin {n} → KExpr {n} {p} := netF Rx", "",
                  "/-- Dominio ⊇ ortante y cuasi-positividad (Lean ejecuta el comprobador). -/",
                  "theorem net_ok : checkNet pos Rx = true := by decide +kernel", "",
                  "/-- Pesos de la combinación con crecimiento lineal (cᵢ ≥ 1). -/",
                  cvec, "",
                  "theorem growth_ok : checkGrowth pos c Rx = true := by decide +kernel", ""]
    else:
        del lines[-2:]       # quitar el docstring y la apertura de la lista única
        lines += ["/-- Pesos de la combinación con crecimiento lineal (cᵢ ≥ 1). -/", cvec, ""]
        chunks = [Rx[k:k + CH] for k in range(0, len(Rx), CH)]
        for k, ch in enumerate(chunks):
            lines += [f"def Rx_{k} : List (KExpr {n} {p} × List (Fin {n} × ℚ)) := [",
                      ",\n".join(item(V, col) for V, col in ch), "]", "",
                      f"theorem net_ok_{k} : checkNet pos Rx_{k} = true := by decide +kernel", "",
                      f"theorem growth_ok_{k} : checkGrowth pos c Rx_{k} = true := by decide +kernel", ""]
        K = len(chunks)
        lines += [f"/-- Red completa ({len(Rx)} términos en {K} bloques). -/",
                  f"def Rx : List (KExpr {n} {p} × List (Fin {n} × ℚ)) := " +
                  " ++ ".join(f"Rx_{k}" for k in range(K)), "",
                  f"def F : Fin {n} → KExpr {n} {p} := netF Rx", "",
                  "theorem net_ok : checkNet pos Rx = true := by",
                  "  simp only [Rx, checkNet_append, " +
                  ", ".join(f"net_ok_{k}" for k in range(K)) + ", Bool.and_self]", "",
                  "theorem growth_ok : checkGrowth pos c Rx = true := by",
                  "  simp only [Rx, checkGrowth_append, " +
                  ", ".join(f"growth_ok_{k}" for k in range(K)) + ", Bool.and_self]", ""]
    lines += ["/-- θ₀ nominal (PEtab), en racionales exactos. -/",
              *lean_vec("θq", p, "ℚ", [lean_q(frac_of(v)) for v in model.theta_vals], "1"), "",
              "theorem theta_ok : checkPosParams pos θq = true := by decide +kernel", ""]
    if init_exprs is None:
        xq = ", ".join(lean_q(frac_of(v)) for v in model.x0_vals)
        lines += ["/-- Condiciones iniciales nominales. -/",
                  *lean_vec("xq", n, "ℚ", [lean_q(frac_of(v)) for v in model.x0_vals], "0"), "",
                  "theorem x0_ok : checkNonneg xq = true := by decide +kernel", "",
                  "/-- **Teorema final, sin condiciones pendientes**: para todo T ≥ 0 la solución",
                  "nominal existe en [0, T], es ≥ 0, queda en el dominio, y la trayectoria es",
                  "diferenciable respecto a θ en θ₀. -/",
                  "def final := @network_final _ _ pos Rx net_ok c growth_ok θq theta_ok xq x0_ok", ""]
    else:
        lines += ["/-- Condición inicial x₀(θ) (asignaciones iniciales de SBML). -/",
                  f"def G : Fin {n} → KExpr {n} {p} := ![",
                  ",\n".join("  " + lean_expr(e) for e in init_exprs), "]", "",
                  "theorem init_ok : checkInit pos G = true := by decide +kernel", "",
                  "/-- **Teorema final, sin condiciones pendientes** (condición inicial x₀(θ)). -/",
                  "def final := @network_final_init _ _ pos Rx net_ok c growth_ok G init_ok θq theta_ok",
                  ""]
    lines += [f"end Models.{mod}", "", f"#print axioms Models.{mod}.final", ""]
    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / f"{mod}.lean").write_text("\n".join(lines))
    return mod, "ok"


def emit_network_segments(model, segs):
    """Forma de red por tramos (escalones en tiempos fijos), teorema final sin condiciones."""
    n, p = len(model.names_ext), len(model.theta)
    pos = [model.positive[t] for t in model.theta]
    Rxs, cs = [], []
    for _, _, rhs in segs:
        Rx = network_of(rhs)
        if net_checks(Rx, pos):
            return None, "checkNet"
        c = find_weights(Rx, n, pos)
        if c is None:
            return None, "crecimiento"
        Rxs.append(Rx); cs.append(c)
    K = len(segs)
    mod = leanid(model.name)
    mask = ", ".join("true" if b else "false" for b in pos)
    tq = ", ".join(lean_q(frac_of(v)) for v in model.theta_vals)
    xq = ", ".join(lean_q(frac_of(v)) for v in model.x0_vals)
    lines = [
        "import KineticNetwork", "",
        f"/-! Modelo `{model.name}` (forma de red, {K} tramos), traducido automáticamente de",
        "SBML por `certificados/sbml_to_lean.py`. No editar a mano.", "",
        f"Estados ({n}): " + ", ".join(model.names_ext), "",
        f"Parámetros estimados θ ({p}): " + ", ".join(model.theta), "",
        "Tramos: " + ", ".join(f"[{a:g}, {b:g}]" for a, b, _ in segs),
        "-/", "", "set_option maxRecDepth 100000", "set_option maxHeartbeats 0", "",
        "open KineticRegularity KineticCheck KineticNetwork", "",
        f"namespace Models.{mod}", "",
        f"def pos : Fin {p} → Bool := ![{mask}]", ""]
    for k, (Rx, c) in enumerate(zip(Rxs, cs)):
        items = []
        for V, col in Rx:
            cols = ", ".join(f"({i}, {lean_q(s_)})" for i, s_ in col)
            items.append(f"  ({lean_expr(V)}, [{cols}])")
        lines += [f"def Rx{k} : List (KExpr {n} {p} × List (Fin {n} × ℚ)) := [",
                  ",\n".join(items), "]", "",
                  f"theorem net_ok{k} : checkNet pos Rx{k} = true := by decide +kernel", "",
                  f"def c{k} : Fin {n} → ℚ := ![{', '.join(lean_q(x) for x in c)}]", "",
                  f"theorem growth_ok{k} : checkGrowth pos c{k} Rx{k} = true := by decide +kernel", ""]
    def by_seg(name, pref):
        out = [name] + [f"  | {k} => {pref}{k}" for k in range(K - 1)] + [f"  | _ => {pref}{K - 1}", ""]
        return out
    lines += by_seg(f"def Rxs : ℕ → List (KExpr {n} {p} × List (Fin {n} × ℚ))", "Rx")
    lines += by_seg(f"def cs : ℕ → Fin {n} → ℚ", "c")
    for nm, fam, arg in (("net_ok", "checkNet pos (Rxs k)", "net_ok"),
                         ("growth_ok", "checkGrowth pos (cs k) (Rxs k)", "growth_ok")):
        lines += [f"theorem {nm} : ∀ k, {fam} = true := by", "  intro k", "  match k with"]
        lines += [f"  | {k} => exact {arg}{k}" for k in range(K - 1)]
        lines += [f"  | _ + {K - 1} => exact {arg}{K - 1}", ""]
    lq = [Fraction(b) - Fraction(a) for a, b, _ in segs]
    lq = [frac_of(b) - frac_of(a) for a, b, _ in segs]
    lines += ["/-- Duración de cada tramo. -/", "def Lq : ℕ → ℚ"]
    lines += [f"  | {k} => {lean_q(lq[k])}" for k in range(K - 1)] + [f"  | _ => {lean_q(lq[-1])}", ""]
    lines += ["theorem Lq_nonneg : ∀ k, 0 ≤ Lq k := by", "  intro k", "  match k with"]
    lines += [f"  | {k} => decide +kernel" for k in range(K - 1)] + \
        [f"  | _ + {K - 1} => exact (show (0 : ℚ) ≤ {lean_q(lq[-1])} by decide +kernel)", ""]
    lines += ["noncomputable def Lseg (k : ℕ) : ℝ := (Lq k : ℝ)", "",
              "theorem Lseg_nonneg : ∀ k, 0 ≤ Lseg k := fun k => by",
              "  unfold Lseg; exact_mod_cast Lq_nonneg k", "",
              f"def θq : Fin {p} → ℚ := ![{tq}]", "",
              "theorem theta_ok : checkPosParams pos θq = true := by decide +kernel", "",
              f"def xq : Fin {n} → ℚ := ![{xq}]", "",
              "theorem x0_ok : checkNonneg xq = true := by decide +kernel", "",
              "/-- **Teorema final por tramos, sin condiciones pendientes.** -/",
              "def final := @network_segments_final _ _ pos Rxs net_ok cs growth_ok θq theta_ok xq",
              "  x0_ok Lseg Lseg_nonneg", "",
              f"end Models.{mod}", "", f"#print axioms Models.{mod}.final", ""]
    (OUTDIR / f"{mod}.lean").write_text("\n".join(lines))
    return mod, "ok"


THETA_OK_LIST = [
    "/-- θ₀ > 0: se comprueba la lista una vez (tiempo lineal) en vez de acceder a cada",
    "componente por índice (tiempo cuadrático). -/",
    "theorem theta_ok : checkPosParams pos θq = true := by",
    "  have hL : θqL.all (fun q => decide (0 < q)) = true := by decide +kernel",
    "  rw [List.all_eq_true] at hL",
    "  simp only [checkPosParams, List.all_eq_true, List.mem_finRange, true_implies,",
    "    Bool.or_eq_true, decide_eq_true_eq]",
    "  intro j",
    "  right",
    "  simp only [θq]",
    "  rw [List.getD_eq_getElem?_getD]",
    "  cases h : θqL[j.val]? with",
    "  | none => simp",
    "  | some x => simpa using hL x (List.mem_of_getElem? h)"]


def emit_network_split(model, rhs):
    """Modelos enormes: un módulo Lean por bloque de términos (memoria acotada por proceso)."""
    n, p = len(model.names_ext), len(model.theta)
    pos = [model.positive[t] for t in model.theta]
    Rx = network_of(rhs)
    if net_checks(Rx, pos):
        return None, "checkNet"
    c = find_weights(Rx, n, pos)
    if c is None:
        return None, "crecimiento"
    mod = leanid(model.name)
    base = OUTDIR / mod
    base.mkdir(parents=True, exist_ok=True)
    hdr = ["set_option maxRecDepth 100000", "set_option maxHeartbeats 0", "",
           "open KineticRegularity KineticCheck KineticNetwork", ""]
    # módulo base: datos vectoriales
    b = ["import KineticNetwork", "",
         f"/-! Datos de `{model.name}` (forma de red dividida en módulos). Generado por",
         "`certificados/sbml_to_lean.py`. -/", ""] + hdr + [f"namespace Models.{mod}", ""]
    b += lean_vec("pos", p, "Bool", [("true" if x else "false") for x in pos], "false") + [""]
    b += lean_vec("c", n, "ℚ", [lean_q(x) for x in c], "1") + [""]
    b += lean_vec("θq", p, "ℚ", [lean_q(frac_of(v)) for v in model.theta_vals], "1") + [""]
    b += lean_vec("xq", n, "ℚ", [lean_q(frac_of(v)) for v in model.x0_vals], "0") + [""]
    b += [f"end Models.{mod}", ""]
    (base / "Base.lean").write_text("\n".join(b))
    CH = 400
    chunks = [Rx[k:k + CH] for k in range(0, len(Rx), CH)]
    for k, ch in enumerate(chunks):
        items = []
        for V, col in ch:
            cs = ", ".join(f"({i}, {lean_q(s_)})" for i, s_ in col)
            items.append(f"  ({lean_expr(V)}, [{cs}])")
        t = [f"import Models.{mod}.Base", ""] + hdr + [f"namespace Models.{mod}", "",
             f"def Rx_{k} : List (KExpr {n} {p} × List (Fin {n} × ℚ)) := [",
             ",\n".join(items), "]", "",
             f"theorem net_ok_{k} : checkNet pos Rx_{k} = true := by decide +kernel", "",
             f"theorem growth_ok_{k} : checkGrowth pos c Rx_{k} = true := by decide +kernel", "",
             f"end Models.{mod}", ""]
        (base / f"Part{k}.lean").write_text("\n".join(t))
    K = len(chunks)
    m = [f"import Models.{mod}.Part{k}" for k in range(K)] + ["",
         f"/-! Modelo `{model.name}` (forma de red, {len(Rx)} términos en {K} módulos).",
         f"Estados: {n}; parámetros estimados θ: {p}. Generado por `certificados/sbml_to_lean.py`. -/",
         ""] + hdr + [f"namespace Models.{mod}", "",
         f"def Rx : List (KExpr {n} {p} × List (Fin {n} × ℚ)) := " +
         " ++ ".join(f"Rx_{k}" for k in range(K)), "",
         f"def F : Fin {n} → KExpr {n} {p} := netF Rx", "",
         "theorem net_ok : checkNet pos Rx = true := by",
         "  simp only [Rx, checkNet_append, " + ", ".join(f"net_ok_{k}" for k in range(K)) +
         ", Bool.and_self]", "",
         "theorem growth_ok : checkGrowth pos c Rx = true := by",
         "  simp only [Rx, checkGrowth_append, " + ", ".join(f"growth_ok_{k}" for k in range(K)) +
         ", Bool.and_self]", "",
         *(THETA_OK_LIST if p > 500 else
           ["theorem theta_ok : checkPosParams pos θq = true := by decide +kernel"]), "",
         "theorem x0_ok : checkNonneg xq = true := by decide +kernel", "",
         "/-- **Teorema final, sin condiciones pendientes.** -/",
         "def final := @network_final _ _ pos Rx net_ok c growth_ok θq theta_ok xq x0_ok", "",
         f"end Models.{mod}", "", f"#print axioms Models.{mod}.final", ""]
    (OUTDIR / f"{mod}.lean").write_text("\n".join(m))
    return mod, "ok"



# ================================================================ forma estricta (StrictNetwork)
# Réplica exacta de los comprobadores de lean/StrictNetwork.lean (Σ = especies con x₀ > 0).
def _keq(a, b):
    if a[0] != b[0] or a[0] in ('rpow',):
        return False
    t = a[0]
    if t in ('num', 'var', 'par'):
        return a[1] == b[1]
    if t in ('add', 'sub', 'mul', 'div'):
        return _keq(a[1], b[1]) and _keq(a[2], b[2])
    if t == 'npow':
        return _keq(a[1], b[1]) and a[2] == b[2]
    if t in ('exp', 'log'):
        return _keq(a[1], b[1])
    return False


_UB = {}   # cotas de parámetros j → [inf, sup] (θⱼ ≥ inf, θⱼ ≤ sup), comprobadas en θ₀ (checkUB)


def _subub(a, b, pos):
    return a[0] == 'num' and b[0] == 'par' and pos[b[1]] and \
        _UB.get(b[1], [None, None])[1] is not None and _UB[b[1]][1] <= a[1]


def _addlb(a, b):
    return a[0] == 'num' and b[0] == 'par' and \
        _UB.get(b[1], [None, None])[0] is not None and 0 <= a[1] + _UB[b[1]][0]


def _qge1(e): return e[0] == 'num' and e[1] >= 1
def _qgt1(e): return e[0] == 'num' and e[1] > 1


def _s_nonneg(e, pos):
    t = e[0]
    if t == 'num': return e[1] >= 0
    if t == 'var': return True
    if t == 'par': return pos[e[1]]
    if t == 'add': return (_s_nonneg(e[1], pos) and _s_nonneg(e[2], pos)) or _addlb(e[1], e[2])
    if t in ('mul', 'div'): return _s_nonneg(e[1], pos) and _s_nonneg(e[2], pos)
    if t in ('npow', 'rpow'): return _s_nonneg(e[1], pos)
    if t == 'exp': return True
    if t == 'log': return _qge1(e[1])
    if t == 'sub': return (_qge1(e[1]) and _exple1(e[2], pos)) or _subub(e[1], e[2], pos)
    return False


def _exple1(e, pos): return e[0] == 'exp' and _s_np(e[1], pos)


def _s_pos(e, pos, sx):
    t = e[0]
    if t == 'num': return e[1] > 0
    if t == 'var': return sx[e[1]]
    if t == 'par': return pos[e[1]]
    if t == 'add': return (_s_pos(e[1], pos, sx) and _s_nonneg(e[2], pos)) or \
        (_s_nonneg(e[1], pos) and _s_pos(e[2], pos, sx))
    if t in ('mul', 'div'): return _s_pos(e[1], pos, sx) and _s_pos(e[2], pos, sx)
    if t in ('npow', 'rpow'): return _s_pos(e[1], pos, sx)
    if t == 'exp': return True
    if t == 'log': return _qgt1(e[1])
    return False


def _s_ok(e, pos, sx):
    t = e[0]
    if t in ('num', 'var', 'par'): return True
    if t in ('add', 'sub', 'mul'): return _s_ok(e[1], pos, sx) and _s_ok(e[2], pos, sx)
    if t == 'div': return _s_ok(e[1], pos, sx) and _s_ok(e[2], pos, sx) and _s_pos(e[2], pos, sx)
    if t == 'npow': return _s_ok(e[1], pos, sx)
    if t in ('rpow', 'log'): return _s_ok(e[1], pos, sx) and _s_pos(e[1], pos, sx)
    if t == 'exp': return _s_ok(e[1], pos, sx)
    return False


def _s_np(e, pos):
    t = e[0]
    if t == 'num': return e[1] <= 0
    if t == 'add': return _s_np(e[1], pos) and _s_np(e[2], pos)
    if t in ('sub', 'div'): return _s_np(e[1], pos) and _s_nonneg(e[2], pos)
    if t == 'mul': return (_s_np(e[1], pos) and _s_nonneg(e[2], pos)) or \
        (_s_nonneg(e[1], pos) and _s_np(e[2], pos))
    return False


def _summand(X, d, pos):
    if d[0] == 'add':
        return (_keq(d, X) and _s_nonneg(X, pos)) or \
            (_summand(X, d[1], pos) and _s_nonneg(d[2], pos)) or \
            (_s_nonneg(d[1], pos) and _summand(X, d[2], pos))
    return _keq(d, X) and _s_nonneg(X, pos)


def _bnd(e, pos, bx):
    t = e[0]
    if t == 'num': return e[1] >= 0
    if t == 'var': return bx
    if t == 'par': return pos[e[1]]
    if t == 'add': return (_bnd(e[1], pos, bx) and _bnd(e[2], pos, bx)) or \
        (_varfree(e) and _s_nonneg(e, pos))
    if t == 'mul': return _bnd(e[1], pos, bx) and _bnd(e[2], pos, bx)
    if t == 'div':
        a, d = e[1], e[2]
        return (_varfree(e) and _s_nonneg(e, pos)) or \
            (_bnd(a, pos, bx) and _py_lowerpos(d, pos)) or _satb(d, a, pos, bx) or \
            _bpair(a, d, pos, bx)
    if t == 'npow': return _bnd(e[1], pos, bx)
    if t == 'rpow': return _varfree(e) and _s_nonneg(e, pos)
    if t == 'exp': return _varfree(e[1]) or _s_np(e[1], pos)
    if t == 'log': return _qge1(e[1])
    if t == 'sub': return (_qge1(e[1]) and _exple1(e[2], pos)) or _subub(e[1], e[2], pos)
    return False


def _satb(d, a, pos, bx):
    if a[0] == 'mul':
        u, v = a[1], a[2]
        return _summand(a, d, pos) or (_satb(d, u, pos, bx) and _bnd(v, pos, bx)) or \
            (_bnd(u, pos, bx) and _satb(d, v, pos, bx))
    return _summand(a, d, pos)


def _bq(a, d, pos, bx):
    return (_bnd(a, pos, bx) and _py_lowerpos(d, pos)) or _satb(d, a, pos, bx) or \
        _bpair(a, d, pos, bx)


def _bpair(a, d, pos, bx):
    if a[0] == 'mul' and d[0] == 'mul':
        a1, a2, d1, d2 = a[1], a[2], d[1], d[2]
        return (_bq(a1, d1, pos, bx) and _bq(a2, d2, pos, bx)) or \
            (_bq(a1, d2, pos, bx) and _bq(a2, d1, pos, bx))
    return False


def _cons(i, e, pos):
    t = e[0]
    if t == 'var': return e[1] == i
    if t == 'mul': return (_cons(i, e[1], pos) and _bnd(e[2], pos, True)) or \
        (_bnd(e[1], pos, True) and _cons(i, e[2], pos))
    if t == 'npow': return e[2] >= 1 and _cons(i, e[1], pos) and _bnd(e[1], pos, True)
    if t == 'div': return (_cons(i, e[1], pos) and _py_lowerpos(e[2], pos)) or \
        _cpair(i, e[1], e[2], pos)
    return False


def _cq(i, a, d, pos):
    return (_cons(i, a, pos) and _py_lowerpos(d, pos)) or _cpair(i, a, d, pos)


def _cpair(i, a, d, pos):
    if a[0] == 'mul' and d[0] == 'mul':
        a1, a2, d1, d2 = a[1], a[2], d[1], d[2]
        B = lambda x, y: _bq(x, y, pos, True)
        C = lambda x, y: _cq(i, x, y, pos)
        return (C(a1, d1) and B(a2, d2)) or (B(a1, d1) and C(a2, d2)) or \
            (C(a1, d2) and B(a2, d1)) or (B(a1, d2) and C(a2, d1))
    return False


def strict_checks(Rx, pos, sx):
    """Réplica de checkNetS; devuelve la lista de fallos."""
    bad = []
    for V, col in Rx:
        if not _s_ok(V, pos, sx):
            bad.append(('dominio', V))
        for i, s in col:
            if s < 0:
                ok = _cons(i, V, pos) if sx[i] else _py_van(i, V)
            else:
                ok = _s_nonneg(V, pos) or (not sx[i] and _py_van(i, V))
            if not ok:
                bad.append((f'especie {i} ({"Σ" if sx[i] else "no Σ"}), coef {s}', V))
    return bad


def _growth_cls(V, pos):
    return _s_nonneg(V, pos), (_py_linok(V, pos) or _bnd(V, pos, False))


def growth_ok_strict(Rx, c, pos):
    for V, col in Rx:
        w = sum((c[i] * s for i, s in col), Fraction(0))
        nn, lin = _growth_cls(V, pos)
        if w == 0 or (w < 0 and nn) or (w > 0 and lin):
            continue
        return False
    return True


def find_weights_strict(Rx, n, pos):
    import numpy as np
    from scipy.optimize import linprog
    A_ub, A_eq = [], []
    for V, col in Rx:
        row = np.zeros(n)
        for i, s in col:
            row[i] += float(s)
        if not row.any():
            continue
        nn, lin = _growth_cls(V, pos)
        if nn and lin:
            continue
        if nn:
            A_ub.append(row)
        elif lin:
            A_ub.append(-row)
        else:
            A_eq.append(row)
    sol = linprog(np.ones(n), A_ub=np.array(A_ub) if A_ub else None,
                  b_ub=np.zeros(len(A_ub)) if A_ub else None,
                  A_eq=np.array(A_eq) if A_eq else None,
                  b_eq=np.zeros(len(A_eq)) if A_eq else None,
                  bounds=[(1, None)] * n, method="highs")
    if sol.status != 0:
        return None
    for den in (1, 10, 100, 1000, 10000, 10 ** 6):
        c = [max(Fraction(1), Fraction(x).limit_denominator(den)) for x in sol.x]
        if growth_ok_strict(Rx, c, pos):
            return c
    return None



# ---------------------------------------------------------------- dato inicial por intervalos
# Réplica exacta de lean/IntervalInit.lean (ival, sqLo, sqHi, checkInitI).
_DQ = Fraction(10) ** 30


def _bsqrt(f, m, lo, hi):
    while True:
        if f == 0:
            return lo
        f -= 1
        if hi <= lo + 1:
            return lo
        mid = (lo + hi) // 2
        if mid * mid <= m:
            lo = mid
        else:
            hi = mid


def _sqlo(x):
    N = max(0, math.floor(x * _DQ ** 2))
    return Fraction(_bsqrt(400, N, 0, N + 1)) / _DQ


def _sqhi(x): return _sqlo(x) + 1 / _DQ


def _imul(a, b):
    ps = (a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1])
    return (min(min(ps[0], ps[1]), min(ps[2], ps[3])), max(max(ps[0], ps[1]), max(ps[2], ps[3])))


def _ival(e, tq):
    t = e[0]
    if t == 'num': return (Fraction(e[1]), Fraction(e[1]))
    if t == 'par': return (tq[e[1]], tq[e[1]])
    if t in ('add', 'sub', 'mul', 'div'):
        x, z = _ival(e[1], tq), _ival(e[2], tq)
        if x is None or z is None: return None
        if t == 'add': return (x[0] + z[0], x[1] + z[1])
        if t == 'sub': return (x[0] - z[1], x[1] - z[0])
        if t == 'mul': return _imul(x, z)
        if 0 < z[0] or z[1] < 0: return _imul(x, (1 / z[1], 1 / z[0]))
        return None
    if t == 'npow':
        x = _ival(e[1], tq)
        if x is None or not 0 <= x[0]: return None
        return (x[0] ** e[2], x[1] ** e[2])
    if t == 'rpow':
        x = _ival(e[1], tq)
        if x is None: return None
        lo, hi = _sqlo(x[0]), _sqhi(x[1])
        if 0 < x[0] and 0 <= lo and lo * lo <= x[0] and 0 <= hi and x[1] <= hi * hi:
            return (lo, hi)
        return None
    return None


def _rpow_exps(e):
    if not isinstance(e, tuple): return []
    out = [e[2]] if e[0] == 'rpow' else []
    for a in e[1:]:
        if isinstance(a, tuple): out += _rpow_exps(a)
    return out


def init_interval_ok(init_exprs, tq, sx):
    for i, e in enumerate(init_exprs):
        if any(r != Fraction(1, 2) for r in _rpow_exps(e)):
            return False
        x = _ival(e, tq)
        if x is None or not (0 <= x[0] and (not sx[i] or 0 < x[0])):
            return False
    return True


def _one_diff(a, b, path=()):
    """Posiciones donde a y b difieren (lista de (ruta, sub_a, sub_b))."""
    if a == b:
        return []
    if isinstance(a, tuple) and isinstance(b, tuple) and len(a) == len(b) and a[0] == b[0] \
            and a[0] not in ('num', 'par', 'var'):
        out = []
        for k in range(1, len(a)):
            out += _one_diff(a[k], b[k], path + (k,))
        return out
    return [(path, a, b)]


def _replace_at(e, path, new):
    if not path:
        return new
    k = path[0]
    return e[:k] + (_replace_at(e[k], path[1:], new),) + e[k + 1:]


def refactor_fractions(Rx, tq):
    """Refactorización exacta de la red: si V₂ = V₁ con un factor 1 sustituido por θⱼ (V₂ = θⱼ·V₁)
    y col₁ + col₂ es una columna válida, se reescribe
        col₁·V₁ + col₂·V₂ = col₁·(1 − θⱼ)·V₁ + (col₁ + col₂)·V₂,
    válido para todo θ. El término (1 − θⱼ)·V₁ es ≥ 0 si θⱼ ≤ 1, lo que se comprueba en θ₀."""
    Rx = [(V, dict(col)) for V, col in Rx]
    ub, changed = {}, False
    for a in range(len(Rx)):
        for b in range(len(Rx)):
            if a == b:
                continue
            V1, c1 = Rx[a]
            V2, c2 = Rx[b]
            d = _one_diff(V1, V2)
            if len(d) != 1:
                continue
            path, x, y = d[0]
            if x != ('num', Fraction(1)) or y[0] != 'par' or not (0 < tq[y[1]] <= 1):
                continue
            # sólo si V₂ consume una especie que V₁ produce (el caso que falla)
            if not any(s_ < 0 and c1.get(i, 0) > 0 for i, s_ in c2.items()):
                continue
            j = y[1]
            newV1 = _replace_at(V1, path, ('sub', ('num', Fraction(1)), ('par', j)))
            newc2 = dict(c2)
            for i, s_ in c1.items():
                newc2[i] = newc2.get(i, 0) + s_
            Rx[a] = (newV1, c1)
            Rx[b] = (V2, {i: s_ for i, s_ in newc2.items() if s_ != 0})
            ub[j] = [None, Fraction(1)]
            changed = True
    if not changed:
        return None, {}
    return [(V, sorted(col.items())) for V, col in Rx], ub


def param_bounds(Rx, tq):
    """Cotas de parámetros para los factores q ± θⱼ: θⱼ ≤ q (si q − θⱼ) o θⱼ ≥ −q (si q + θⱼ),
    sólo si se cumplen en θ₀ (Lean lo comprueba con checkUB)."""
    ub = {}
    def walk(e):
        if not isinstance(e, tuple):
            return
        if e[0] in ('add', 'sub') and e[1][0] == 'num' and e[2][0] == 'par':
            j, q = e[2][1], Fraction(e[1][1])
            b = ub.setdefault(j, [None, None])
            if e[0] == 'sub' and tq[j] <= q:
                b[1] = q if b[1] is None else min(b[1], q)
            if e[0] == 'add' and tq[j] >= -q:
                b[0] = -q if b[0] is None else max(b[0], -q)
        for a in e[1:]:
            walk(a)
    for V, _ in Rx:
        walk(V)
    return {j: b for j, b in ub.items() if b != [None, None]}

def emit_strict(model, rhs, init_exprs):
    """Forma de red con positividad estricta (Σ = especies con x₀ nominal > 0)."""
    n, p = len(model.names_ext), len(model.theta)
    pos = [model.positive[t] for t in model.theta]
    sx = [v > 0 for v in model.x0_vals]
    Rx = network_of(rhs)
    tq = [frac_of(v) for v in model.theta_vals]
    _UB.clear()
    if getattr(model, 'atomize', False):
        _UB.update(param_bounds(Rx, tq))
    bad = strict_checks(Rx, pos, sx)
    if bad:
        Rx2, ub2 = refactor_fractions(Rx, tq)
        if Rx2 is not None:
            saved = dict(_UB)
            _UB.update(ub2)
            if not strict_checks(Rx2, pos, sx):
                Rx, bad = Rx2, []
            else:
                _UB.clear(); _UB.update(saved)
    if bad:
        return None, "checkNetS", bad
    c = find_weights_strict(Rx, n, pos)
    if c is None:
        return None, "crecimiento", []
    if init_exprs is None:
        init_exprs = [num(frac_of(v)) for v in model.x0_vals]
    interval = False
    for i, e in enumerate(init_exprs):
        if not (_py_okorth(e, pos) and _py_nonneg(e, pos) and (not sx[i] or _py_pos(e, pos))):
            if init_interval_ok(init_exprs, [frac_of(v) for v in model.theta_vals], sx):
                interval = True
                break
            return None, "init", [(f"x0 {i}", e)]
    mod = leanid(model.name)
    lines = [
        "import IntervalInit" if interval else "import StrictNetwork", "",
        f"/-! Modelo `{model.name}` (forma de red, positividad estricta), traducido",
        "automáticamente de SBML por `certificados/sbml_to_lean.py`. No editar a mano.", "",
        f"Estados ({n}): " + ", ".join(model.names_ext), "",
        "Σ (dato inicial > 0, permanecen estrictamente positivas): " +
        ", ".join(s_ for s_, b in zip(model.names_ext, sx) if b), "",
        f"Parámetros estimados θ ({p}): " + ", ".join(model.theta),
        "-/", "", "set_option maxRecDepth 100000", "set_option maxHeartbeats 0", "",
        "open KineticRegularity KineticCheck KineticNetwork StrictNetwork" +
        (" IntervalInit" if interval else ""), "",
        f"namespace Models.{mod}", "",
        "/-- Máscara de parámetros positivos (nominal > 0 o escala log). -/",
        *lean_vec("pos", p, "Bool", [("true" if b else "false") for b in pos], "false"), "",
        "/-- Cotas superiores de parámetros usadas (θⱼ ≤ q), comprobadas en θ₀ (`ub_ok`). -/",
        *lean_vec("ub", p, "Option ℚ × Option ℚ",
                  [(f"({'none' if _UB[j][0] is None else 'some ' + lean_q(_UB[j][0])}, "
                    f"{'none' if _UB[j][1] is None else 'some ' + lean_q(_UB[j][1])})")
                   if j in _UB else "(none, none)" for j in range(p)], "(none, none)"), "",
        "/-- Σ: especies con dato inicial nominal > 0. -/",
        *lean_vec("sx", n, "Bool", [("true" if b else "false") for b in sx], "false"), "",
        f"/-- Términos de velocidad con su columna estequiométrica ({len(Rx)} términos). -/",
        f"def Rx : List (KExpr {n} {p} × List (Fin {n} × ℚ)) := ["]
    lines.append(",\n".join(
        f"  ({lean_expr(V)}, [{', '.join(f'({i}, {lean_q(s_)})' for i, s_ in col)}])"
        for V, col in Rx))
    lines += ["]", "",
              "/-- El campo del modelo: `Fᵢ = Σ_r coef_r(i) · V_r`. -/",
              f"def F : Fin {n} → KExpr {n} {p} := netF Rx", "",
              "/-- Dominio ⊇ región estricta, cuasi-positividad fuera de Σ y consumo proporcional",
              "en Σ (Lean ejecuta el comprobador). -/",
              "theorem net_ok : checkNetS pos ub sx Rx = true := by decide +kernel", "",
              "/-- Pesos de la combinación con crecimiento lineal (cᵢ ≥ 1). -/",
              *lean_vec("c", n, "ℚ", [lean_q(x) for x in c], "1"), "",
              "theorem growth_ok : checkGrowthS pos ub c Rx = true := by decide +kernel", "",
              "/-- θ₀ nominal (PEtab), en racionales exactos. -/",
              *lean_vec("θq", p, "ℚ", [lean_q(frac_of(v)) for v in model.theta_vals], "1"), "",
              "theorem theta_ok : checkPosParams pos θq = true := by decide +kernel", "",
              "theorem ub_ok : checkUB ub θq = true := by decide +kernel", "",
              "/-- Condición inicial x₀(θ). -/",
              f"def G : Fin {n} → KExpr {n} {p} := ![",
              ",\n".join("  " + lean_expr(e) for e in init_exprs), "]", "",
              *(["theorem init_ok : checkInitS pos sx G = true := by decide +kernel", ""]
                if not interval else
                ["/-- G(θ₀) ≥ 0 (> 0 en Σ), certificado por aritmética de intervalos en ℚ. -/",
                 "theorem init_ok : checkInitI sx θq G = true := by decide +kernel", "",
                 "/-- Las potencias reales de G son raíces cuadradas. -/",
                 "theorem half_ok : ∀ i, ∀ r ∈ rpowExps (G i), r = 1 / 2 := by",
                 "  intro i; fin_cases i <;> simp [rpowExps, G]", ""]),
              "/-- **Teorema final, sin condiciones pendientes**: para todo T ≥ 0 la solución",
              "nominal existe en [0, T], las especies de Σ permanecen > 0 y las demás ≥ 0, queda",
              "en el dominio, y la trayectoria es diferenciable respecto a θ en θ₀. -/",
              ("def final := @strict_final_init _ _ pos ub sx Rx net_ok c growth_ok G init_ok θq theta_ok ub_ok"
               if not interval else
               "def final := @strict_final_initI _ _ pos ub sx Rx net_ok c growth_ok G θq init_ok half_ok theta_ok ub_ok"),
              "", f"end Models.{mod}", "", f"#print axioms Models.{mod}.final", ""]
    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / f"{mod}.lean").write_text("\n".join(lines))
    return mod, "estricta", []


# ================================================================ crecimiento cuadrático (RiccatiNetwork)
# Réplica exacta (en ℚ) de lean/RiccatiNetwork.lean.
def _qc(e):
    t = e[0]
    if t in ('num', 'par'): return True
    if t in ('add', 'sub', 'mul', 'div'): return _qc(e[1]) and _qc(e[2])
    if t == 'npow': return _qc(e[1])
    return False


def _qval(e, tq):
    t = e[0]
    if t == 'num': return Fraction(e[1])
    if t == 'par': return tq[e[1]]
    if t == 'add': return _qval(e[1], tq) + _qval(e[2], tq)
    if t == 'sub': return _qval(e[1], tq) - _qval(e[2], tq)
    if t == 'mul': return _qval(e[1], tq) * _qval(e[2], tq)
    if t == 'div':
        b = _qval(e[2], tq)
        return Fraction(0) if b == 0 else _qval(e[1], tq) / b
    if t == 'npow': return _qval(e[1], tq) ** e[2]
    return Fraction(0)


def _qnn(e, tq): return _qc(e) and _qval(e, tq) >= 0


def _linC(e, tq):
    t = e[0]
    if t == 'var': return True
    if t == 'add': return _linC(e[1], tq) and _linC(e[2], tq)
    if t == 'mul': return (_qnn(e[1], tq) and _linC(e[2], tq)) or (_linC(e[1], tq) and _qnn(e[2], tq))
    return _qnn(e, tq)


def _linV(e, c, tq):
    t = e[0]
    if t == 'var': return (Fraction(0), 1 / Fraction(c[e[1]]))
    if t == 'add':
        a, b = _linV(e[1], c, tq), _linV(e[2], c, tq)
        return (a[0] + b[0], a[1] + b[1])
    if t == 'mul':
        if _qnn(e[1], tq) and _linC(e[2], tq):
            r, v = _qval(e[1], tq), _linV(e[2], c, tq)
            return (r * v[0], r * v[1])
        r, v = _qval(e[2], tq), _linV(e[1], c, tq)
        return (v[0] * r, v[1] * r)
    return (_qval(e, tq), Fraction(0))


def _quadC(e, tq):
    t = e[0]
    if t == 'mul':
        return (_linC(e[1], tq) and _linC(e[2], tq)) or (_quadC(e[1], tq) and _qnn(e[2], tq)) or \
            (_qnn(e[1], tq) and _quadC(e[2], tq))
    if t == 'npow': return e[2] == 2 and _linC(e[1], tq)
    return _linC(e, tq)


def _prodV(u, v): return (u[0] * v[0], u[0] * v[1] + v[0] * u[1], u[1] * v[1])


def _quadV(e, c, tq):
    t = e[0]
    if t == 'mul':
        if _linC(e[1], tq) and _linC(e[2], tq):
            return _prodV(_linV(e[1], c, tq), _linV(e[2], c, tq))
        if _quadC(e[1], tq) and _qnn(e[2], tq):
            r = _qval(e[2], tq); q = _quadV(e[1], c, tq)
            return (q[0] * r, q[1] * r, q[2] * r)
        r = _qval(e[1], tq); q = _quadV(e[2], c, tq)
        return (r * q[0], r * q[1], r * q[2])
    if t == 'npow':
        v = _linV(e[1], c, tq)
        return _prodV(v, v)
    v = _linV(e, c, tq)
    return (v[0], v[1], Fraction(0))


def riccati_ok(Rx, c, tq, xq, Tq, pos):
    A = B = C = Fraction(0)
    for V, col in Rx:
        w = sum((c[i] * s for i, s in col), Fraction(0))
        if w == 0:
            continue
        if w < 0:
            if not _py_nonneg(V, pos):
                return False
            continue
        if not _quadC(V, tq):
            return False
        q = _quadV(V, c, tq)
        A, B, C = A + w * q[0], B + w * q[1], C + w * q[2]
    Q = max(A, B / 2, C)
    phi0 = sum((ci * xi for ci, xi in zip(c, xq)), Fraction(0))
    return Q > 0 and Fraction(11, 10) * Q * (phi0 + 1) * Tq < 1


def emit_riccati(model, rhs, T):
    n, p = len(model.names_ext), len(model.theta)
    pos = [model.positive[t] for t in model.theta]
    Rx = network_of(rhs)
    if net_checks(Rx, pos):
        return None, "checkNet"
    tq = [frac_of(v) for v in model.theta_vals]
    xq = [frac_of(v) for v in model.x0_vals]
    Tq = frac_of(T)
    cands = [[Fraction(1)] * n]
    for j in range(n):
        for k in range(1, 8):
            cc = [Fraction(1)] * n
            cc[j] = Fraction(10) ** k
            cands.append(cc)
    c = next((cc for cc in cands if riccati_ok(Rx, cc, tq, xq, Tq, pos)), None)
    if c is None:
        return None, "riccati"
    mod = leanid(model.name)
    lines = [
        "import RiccatiNetwork", "",
        f"/-! Modelo `{model.name}` (forma de red, crecimiento cuadrático), traducido",
        "automáticamente de SBML por `certificados/sbml_to_lean.py`. No editar a mano.", "",
        f"Estados ({n}): " + ", ".join(model.names_ext), "",
        f"Parámetros estimados θ ({p}): " + ", ".join(model.theta), "",
        f"Horizonte: T ≤ {lean_q(Tq)} (la cota de Riccati no da existencia global).",
        "-/", "", "set_option maxRecDepth 100000", "set_option maxHeartbeats 0", "",
        "open KineticRegularity KineticCheck KineticNetwork RiccatiNetwork", "",
        f"namespace Models.{mod}", "",
        *lean_vec("pos", p, "Bool", [("true" if b else "false") for b in pos], "false"), "",
        f"def Rx : List (KExpr {n} {p} × List (Fin {n} × ℚ)) := ["]
    lines.append(",\n".join(
        f"  ({lean_expr(V)}, [{', '.join(f'({i}, {lean_q(s_)})' for i, s_ in col)}])"
        for V, col in Rx))
    lines += ["]", "",
              f"def F : Fin {n} → KExpr {n} {p} := netF Rx", "",
              "theorem net_ok : checkNet pos Rx = true := by decide +kernel", "",
              *lean_vec("θq", p, "ℚ", [lean_q(v) for v in tq], "1"), "",
              "theorem theta_ok : checkPosParams pos θq = true := by decide +kernel", "",
              *lean_vec("xq", n, "ℚ", [lean_q(v) for v in xq], "0"), "",
              "theorem x0_ok : checkNonneg xq = true := by decide +kernel", "",
              "/-- Pesos de la combinación `φ = Σ cᵢ xᵢ`. -/",
              *lean_vec("c", n, "ℚ", [lean_q(x) for x in c], "1"), "",
              f"/-- Horizonte `T_q = {lean_q(Tq)}`. -/",
              f"def Tq : ℚ := {lean_q(Tq)}", "",
              "/-- Cota de Riccati `Σ cᵢ Fᵢ ≤ Q (φ + 1)²` y `1.1·Q·(φ₀ + 1)·T_q < 1`. -/",
              "theorem riccati_ok : checkRiccati pos c θq xq Tq Rx = true := by decide +kernel", "",
              "/-- **Teorema final, sin condiciones pendientes** para `0 ≤ T ≤ T_q`: la solución",
              "nominal existe en [0, T], es ≥ 0, queda en el dominio, y la trayectoria es",
              "diferenciable respecto a θ en θ₀. -/",
              "def final := @riccati_final _ _ pos Rx net_ok c θq theta_ok xq x0_ok Tq riccati_ok", "",
              f"end Models.{mod}", "", f"#print axioms Models.{mod}.final", ""]
    (OUTDIR / f"{mod}.lean").write_text("\n".join(lines))
    return mod, "riccati"

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
