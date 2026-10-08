#!/usr/bin/env python3
"""
Prototipo de las comprobaciones de POSITIVIDAD ESTRICTA (antes de formalizarlas en Lean).

Σ = especies con condición inicial > 0. Se comprueba, término a término de la red:
  * dominio: el término está bien definido si y ≥ 0 e y_j > 0 para j ∈ Σ;
  * consumo de una especie i ∉ Σ: el término se anula si y_i = 0 (cuasi-positividad);
  * consumo de una especie i ∈ Σ: el término es ≤ K·y_i en la caja [0, B]ⁿ ∩ región estricta
    (factor y_i por algo acotado), lo que da y_i(t) ≥ y_i(0)·e^{−Ct} > 0;
  * producción: término ≥ 0;
  * crecimiento lineal con pesos c (programación lineal).
"""
import sys, json
from fractions import Fraction
from sbml_to_lean import (Model, Unsupported, network_of, flatten_add, _varfree, _py_linok,
                          HERE)
import numpy as np
from scipy.optimize import linprog


def flatten_mul(e):
    if e[0] == 'mul':
        return flatten_mul(e[1]) + flatten_mul(e[2])
    return [e]


class Strict:
    def __init__(self, pos, sx):
        self.pos, self.sx = pos, sx

    def nonneg(self, e):
        t = e[0]
        if t == 'num': return e[1] >= 0
        if t == 'var': return True
        if t == 'par': return self.pos[e[1]]
        if t in ('add', 'mul', 'div'): return self.nonneg(e[1]) and self.nonneg(e[2])
        if t in ('npow', 'rpow'): return self.nonneg(e[1])
        if t == 'exp': return True
        return False

    def ispos(self, e):
        t = e[0]
        if t == 'num': return e[1] > 0
        if t == 'var': return self.sx[e[1]]
        if t == 'par': return self.pos[e[1]]
        if t == 'add': return (self.ispos(e[1]) and self.nonneg(e[2])) or \
            (self.nonneg(e[1]) and self.ispos(e[2]))
        if t in ('mul', 'div'): return self.ispos(e[1]) and self.ispos(e[2])
        if t in ('npow', 'rpow'): return self.ispos(e[1])
        if t == 'exp': return True
        return False

    def okdom(self, e):
        t = e[0]
        if t in ('num', 'var', 'par'): return True
        if t in ('add', 'sub', 'mul'): return self.okdom(e[1]) and self.okdom(e[2])
        if t == 'div': return self.okdom(e[1]) and self.okdom(e[2]) and self.ispos(e[2])
        if t == 'npow': return self.okdom(e[1])
        if t in ('rpow', 'log'): return self.okdom(e[1]) and self.ispos(e[1])
        if t == 'exp': return self.okdom(e[1])
        return False

    def lowerpos(self, e):
        """≥ constante > 0 (sin usar la positividad estricta, que no da cota uniforme)."""
        if e[0] == 'add':
            return (_varfree(e) and self.ispos(e)) or \
                (self.lowerpos(e[1]) and self.nonneg(e[2])) or \
                (self.nonneg(e[1]) and self.lowerpos(e[2]))
        return _varfree(e) and self.ispos(e)

    def bnd(self, e):
        """Acotado superiormente en la caja [0, B]ⁿ ∩ región estricta (y ≥ 0)."""
        t = e[0]
        if _varfree(e): return self.nonneg(e)
        if t == 'var': return True
        if t in ('add', 'mul'): return self.bnd(e[1]) and self.bnd(e[2]) and \
            self.nonneg(e[1]) and self.nonneg(e[2])
        if t == 'npow': return self.bnd(e[1]) and self.nonneg(e[1])
        if t == 'div':
            a, b = e[1], e[2]
            if self.bnd(a) and self.nonneg(a) and self.lowerpos(b):
                return True
            # saturante: (k·X)/(… + X + …) ≤ k
            if b[0] == 'add' and self.nonneg(a) and self.nonneg(b):
                fa, sb = flatten_mul(a), flatten_add(b)
                for X in fa:
                    if X in sb:
                        rest = list(fa); rest.remove(X)
                        if all(self.bnd(r) and self.nonneg(r) for r in rest):
                            return True
            return False
        return False

    def cons(self, i, e):
        """e ≤ K·y_i en la caja (factor y_i por algo acotado)."""
        t = e[0]
        if t == 'var': return e[1] == i
        if t == 'mul':
            a, b = e[1], e[2]
            return (self.cons(i, a) and self.bnd(b) and self.nonneg(b) and self.nonneg(a)) or \
                (self.cons(i, b) and self.bnd(a) and self.nonneg(a) and self.nonneg(b))
        if t == 'div':
            a, b = e[1], e[2]
            if self.cons(i, a) and self.nonneg(a) and self.lowerpos(b):
                return True
            # saturante con el factor y_i en el numerador: (y_i·k·X)/(…+X+…)
            if b[0] == 'add' and self.nonneg(a) and self.nonneg(b):
                fa, sb = flatten_mul(a), flatten_add(b)
                if ('var', i) in fa:
                    rest = list(fa); rest.remove(('var', i))
                    for X in rest:
                        if X in sb:
                            r2 = list(rest); r2.remove(X)
                            if all(self.bnd(r) and self.nonneg(r) for r in r2):
                                return True
                    if all(self.bnd(r) and self.nonneg(r) for r in rest) and self.lowerpos(b):
                        return True
            return False
        if t == 'npow':
            return e[2] >= 1 and self.cons(i, e[1]) and self.bnd(e[1])
        return False

    def van(self, i, e):
        t = e[0]
        if t == 'num': return e[1] == 0
        if t == 'var': return e[1] == i
        if t in ('add', 'sub'): return self.van(i, e[1]) and self.van(i, e[2])
        if t == 'mul': return self.van(i, e[1]) or self.van(i, e[2])
        if t == 'div': return self.van(i, e[1])
        if t == 'npow': return self.van(i, e[1]) and e[2] > 0
        return False


def analyze(name, T):
    m = Model(name)
    bps = [b for b in m.breakpoints() if 0 < b < T]
    if bps:
        return {"sistema": name, "nota": "tiene tramos (no analizado aquí)"}
    m.t_now = T / 2
    rhs = m.species_rhs()
    x0 = []
    for s_ in m.states:
        sp = m.m.getSpecies(s_)
        x0.append(sp.getInitialConcentration() if sp.isSetInitialConcentration() else sp.getInitialAmount())
    n = len(rhs)
    sx = [v > 0 for v in x0]
    pos = [m.positive[t] for t in m.theta]
    S = Strict(pos, sx)
    Rx = network_of(rhs)
    fallos = []
    for V, col in Rx:
        if not S.okdom(V):
            fallos.append(("dominio", repr(V)[:150]))
        for i, s in col:
            if s < 0:
                ok = S.cons(i, V) if sx[i] else S.van(i, V)
                if not ok:
                    fallos.append((f"consumo de {m.states[i]} ({'Σ' if sx[i] else 'no Σ'})",
                                   repr(V)[:150]))
            elif not (S.nonneg(V) or S.van(i, V)):
                fallos.append((f"producción de {m.states[i]}", repr(V)[:150]))
    # crecimiento (programación lineal), con signos de la región estricta
    A_ub, A_eq = [], []
    for V, col in Rx:
        row = np.zeros(n)
        for i, s in col:
            row[i] += float(s)
        if not row.any():
            continue
        nn, lin = S.nonneg(V), _py_linok(V, pos)
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
    return {"sistema": name, "Σ": [s for s, b in zip(m.states, sx) if b],
            "no Σ": [s for s, b in zip(m.states, sx) if not b],
            "fallos": fallos[:8], "n_fallos": len(fallos),
            "crecimiento_lineal": sol.status == 0}


if __name__ == "__main__":
    from certify_systems import SYSTEMS, T_END_OVERRIDE
    tends = {nm: T_END_OVERRIDE.get(nm, t) for nm, _, t, _ in SYSTEMS}
    for nm in sys.argv[1:]:
        try:
            r = analyze(nm, tends.get(nm, 50.0))
        except Unsupported as e:
            r = {"sistema": nm, "error": str(e)}
        print(json.dumps(r, ensure_ascii=False, indent=1))
