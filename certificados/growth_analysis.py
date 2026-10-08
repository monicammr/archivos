#!/usr/bin/env python3
"""
Análisis de la condición de crecimiento lineal (existencia global, Lean:
GlobalExistence.exists_global_solution): ¿existe c > 0 con c·F(z) ≤ a + b·c·z en el ortante?

Para cada modelo (traducido por sbml_to_lean) se forma la matriz S (especie × término) y se
clasifica cada término: 'const' (no depende de z), 'lin' (≤ α + β Σz), 'bnd' (acotado),
'sup' (posiblemente superlineal) o '?' (signo no garantizado). Basta encontrar c con
cᵢ ≥ 1 y w_r = Σᵢ cᵢ S_ir ≤ 0 para los términos 'sup' (programación lineal).
"""
import sys, json
from fractions import Fraction
import numpy as np
from scipy.optimize import linprog
from sbml_to_lean import Model, Unsupported, HERE

def varfree(e):
    return 'var' not in repr(e)

def nonneg(e, pos):
    t = e[0]
    if t == 'num': return e[1] >= 0
    if t == 'var': return True
    if t == 'par': return pos[e[1]]
    if t in ('add', 'mul', 'div'): return nonneg(e[1], pos) and nonneg(e[2], pos)
    if t in ('npow', 'rpow'): return nonneg(e[1], pos)
    if t == 'exp': return True
    return False

def lowerpos(e, pos):
    """e ≥ constante > 0 en el ortante."""
    t = e[0]
    if varfree(e):
        return ispos(e, pos)
    if t == 'add':
        return (lowerpos(e[1], pos) and nonneg(e[2], pos)) or \
               (nonneg(e[1], pos) and lowerpos(e[2], pos))
    return False

def ispos(e, pos):
    t = e[0]
    if t == 'num': return e[1] > 0
    if t == 'par': return pos[e[1]]
    if t == 'add': return (ispos(e[1], pos) and nonneg(e[2], pos)) or (nonneg(e[1], pos) and ispos(e[2], pos))
    if t in ('mul', 'div'): return ispos(e[1], pos) and ispos(e[2], pos)
    if t in ('npow', 'rpow'): return ispos(e[1], pos)
    if t == 'exp': return True
    return False

def cls(e, pos):
    """'const' | 'bnd' | 'lin' | 'sup'  (supone nonneg(e))."""
    t = e[0]
    if varfree(e): return 'const'
    if t == 'var': return 'lin'
    if t == 'add':
        a, b = cls(e[1], pos), cls(e[2], pos)
        return max(a, b, key=RANK.get)
    if t == 'mul':
        a, b = cls(e[1], pos), cls(e[2], pos)
        if a == 'const': return b
        if b == 'const': return a
        if a == 'bnd' and b == 'bnd': return 'bnd'
        if 'bnd' in (a, b) and 'lin' in (a, b): return 'lin'
        return 'sup'
    if t == 'div':
        num_, den = e[1], e[2]
        # Hill/MM saturante: A·P / (Q + P) ≤ A
        if den[0] == 'add':
            for P, Q in ((den[2], den[1]), (den[1], den[2])):
                if nonneg(Q, pos) and (num_ == P or (num_[0] == 'mul' and (num_[2] == P or num_[1] == P))):
                    A = num_[1] if num_[0] == 'mul' and num_[2] == P else (num_[2] if num_[0] == 'mul' else ('num', Fraction(1)))
                    ca = cls(A, pos)
                    return 'bnd' if ca in ('const', 'bnd') else ca
        if lowerpos(den, pos):
            return cls(num_, pos)
        return 'sup'
    if t == 'npow':
        if e[2] == 0: return 'const'
        if e[2] == 1: return cls(e[1], pos)
        c = cls(e[1], pos)
        return c if c in ('const', 'bnd') else 'sup'
    if t == 'exp':
        return 'sup'
    return 'sup'

RANK = {'const': 0, 'bnd': 1, 'lin': 2, 'sup': 3}

def analyze(name, T):
    m = Model(name)
    bps = [b for b in m.breakpoints() if 0 < b < T]
    edges = [0.0] + bps + [T]
    res = {"sistema": name, "tramos": len(edges) - 1}
    pos = [m.positive[t] for t in m.theta]
    feasible_all = True
    worst = []
    for a, b in zip(edges[:-1], edges[1:]):
        m.t_now = (a + b) / 2
        rhs = m.species_rhs()
        n = len(rhs)
        terms, idx = [], {}
        S = {}
        for i, lst in enumerate(rhs):
            for c, t in lst:
                k = repr(t)
                if k not in idx:
                    idx[k] = len(terms); terms.append(t)
                S[(i, idx[k])] = S.get((i, idx[k]), 0) + float(c)
        R = len(terms)
        klass = []
        for t in terms:
            klass.append(cls(t, pos) if nonneg(t, pos) else '?')
        # restricciones: términos 'sup' → w_r ≤ 0 ; términos '?' → w_r = 0
        A_ub, A_eq = [], []
        for r, k in enumerate(klass):
            row = np.zeros(n)
            for i in range(n):
                row[i] = S.get((i, r), 0.0)
            if not row.any():
                continue
            if k == 'sup':
                A_ub.append(row)
            elif k == '?':
                A_eq.append(row)
        nv = n + (1 if m.uses_time else 0)
        sol = linprog(np.ones(n), A_ub=np.array(A_ub) if A_ub else None,
                      b_ub=np.zeros(len(A_ub)) if A_ub else None,
                      A_eq=np.array(A_eq) if A_eq else None,
                      b_eq=np.zeros(len(A_eq)) if A_eq else None,
                      bounds=[(1, None)] * n, method="highs")
        ok = sol.status == 0
        feasible_all &= ok
        if not ok:
            worst += [f"{k}: {repr(t)[:120]}" for t, k in zip(terms, klass) if k in ('sup', '?')][:5]
        res.setdefault("clases", {})
        for k in klass:
            res["clases"][k] = res["clases"].get(k, 0) + 1
        if ok:
            res.setdefault("c", [float(x) for x in sol.x])
    res["crecimiento_lineal"] = feasible_all
    res["terminos_problema"] = worst
    return res

if __name__ == "__main__":
    from certify_systems import SYSTEMS, T_END_OVERRIDE
    tends = {nm: T_END_OVERRIDE.get(nm, t) for nm, _, t, _ in SYSTEMS}
    out = {}
    for f in sorted((HERE / "resultados" / "sbml_lean").glob("*.json")):
        d = json.loads(f.read_text())
        if not d.get("prediccion_check"):
            continue
        nm = d["sistema"]
        try:
            r = analyze(nm, tends.get(nm, 50.0))
        except Unsupported as e:
            r = {"sistema": nm, "error": str(e)}
        r.pop("c", None)
        print(json.dumps(r, ensure_ascii=False)[:400], flush=True)
