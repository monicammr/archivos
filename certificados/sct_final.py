#!/usr/bin/env python3
"""
SCT Bandura con el método final (mismo procedimiento que los problemas PEtab).

El modelo (sct_bandura_modelo.py) es lineal, ẋ = A(θ)x + B(θ)u, con 6 estados, 22 parámetros
(β_ij, γ_ij, τ_i), 3 condiciones de entrada y salida medida y = x₄. No hay datos experimentales
ni parámetros de calibración: todos los parámetros son "biológicos" (del modelo).

Se aplica en dos variantes:
  * salida  : y = x₄ en las 3 condiciones (lo que se mediría);
  * estados : los 6 estados en las 3 condiciones (como en el artículo original).

Pasos: J relativa (diferencias centradas, δ = 0,01) → etapa 1 (orden E_j, κ/VIF ≤ 10,
R_var ≥ 0,89) → admisible si |S| ≥ 2 y mediana de e_ajuste ≤ 0,436 (15 escenarios ±5 %,
semilla 42, reajuste en log θ dentro de [θ₀/10, 10θ₀]) → etapa 2 (orden s_j, η = 0,1) si hace
falta → poda → patrones de robustez (±1…50 %). Además, diagnóstico de colinealidad:
κ y VIF del conjunto completo, pares de columnas casi paralelas y candidatos descartados por
κ/VIF con el parámetro con el que son colineales.

Uso: python3 sct_final.py  → resultados/sct_bandura/{salida,estados}.json y SCT_BANDURA.md
"""
import sys, json
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import sct_bandura_modelo as M

OUT = HERE / "resultados" / "sct_bandura"
OUT.mkdir(parents=True, exist_ok=True)
DELTA, ETA, TAU_R, TAU_K, EMAX, KMIN = 0.01, 0.1, 0.89, 10.0, float(np.sqrt(1 - 0.81)), 2
N_ESC, SEED = 15, 42
NIVELES = [0.01, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50]
import os
names = list(M.PARAM_NAMES); p = len(names)
# Valores nominales: "codigo" = THETA_NOM del script original; "etcm" = Tabla III (estimación DE)
# de Miranda et al., ETCM 2025.
ETCM = dict(tau1=0.8155, tau2=5, tau3=3.4696, tau4=0.3655, tau5=0.1636, tau6=0.1,
            beta14=0.8637, beta21=0.2058, beta25=0.6155, beta31=0.6217, beta34=0.2372,
            beta42=0.2515, beta43=0.3709, beta45=0.9084, beta46=0.1, beta54=0.6224,
            gamma33=0.1, gamma35=0.9999, gamma36=0.1, gamma57=0.9555, gamma64=0.5217, gamma68=0.1)
VALORES = os.environ.get("SCT_VALORES", "codigo")
th0 = M.THETA_NOM.copy() if VALORES == "codigo" else np.array([ETCM[n] for n in names], float)
# Entradas: "codigo" = 3 condiciones con escalón en los canales 1 y 2 (script original);
# "seis" = 6 condiciones, escalón unitario en cada uno de los 6 canales de entrada ξ3–ξ8.
ENTRADAS = os.environ.get("SCT_ENTRADAS", "codigo")
if ENTRADAS == "seis":
    M.INPUTS = []
    for k in range(6):
        u = np.zeros((M.N_PTS, 6)); u[:, k] = 1.0; M.INPUTS.append(u)
SUF = "" if (VALORES, ENTRADAS) == ("codigo", "codigo") else f"_{VALORES}_{ENTRADAS}"


def salida_x4(theta):
    return np.concatenate([M.rk4(theta, u, M.T_GRID)[:, 3] for u in M.INPUTS])


VARIANTES = {"salida": salida_x4, "estados": M.simulate_all}


def norm_cols(J, idx):
    F = J[:, idx]
    n = np.linalg.norm(F, axis=0)
    return F / np.where(n > 0, n, 1.0)


def kappa(J, idx):
    if len(idx) <= 1:
        return 1.0
    s = np.linalg.svd(norm_cols(J, idx), compute_uv=False)
    return float("inf") if s[-1] < 1e-12 else float(s[0] / s[-1])


def vif(J, idx):
    if len(idx) <= 1:
        return 1.0
    Z = norm_cols(J, idx)
    G = Z.T @ Z
    try:
        return float(np.max(np.diag(np.linalg.inv(G))))
    except np.linalg.LinAlgError:
        return float("inf")


def greedy(J, orden, parar):
    S, descartes = [], []
    for j in orden:
        k, v = kappa(J, S + [j]), vif(J, S + [j])
        if k <= TAU_K and v <= TAU_K:
            S.append(j)
            if parar(S):
                return S, True, descartes
        else:
            Z = norm_cols(J, S + [j])
            cosmax = np.abs(Z[:, :-1].T @ Z[:, -1]) if S else np.array([0.0])
            socio = S[int(np.argmax(cosmax))] if S else None
            descartes.append({"parametro": names[j], "kappa": k, "VIF": v,
                              "mas_colineal_con": names[socio] if socio is not None else None,
                              "cos": float(cosmax.max()) if S else None})
    return S, False, descartes


def escenarios(nivel):
    rng = np.random.default_rng(SEED)
    return [th0 * (1 + nivel * rng.uniform(-1, 1, size=p)) for _ in range(N_ESC)]


def evalua(F, y0, S, nivel):
    """Medianas de cos Δ, e_rel y e_ajuste (reajuste de θ_S) en 15 escenarios."""
    cs, es, fs = [], [], []
    lo, hi = np.log(th0[S] / 10), np.log(th0[S] * 10)
    for th in escenarios(nivel):
        yf = F(th); d = yf - y0; nf = np.linalg.norm(d)
        if nf < 1e-12:
            continue
        ts = th0.copy(); ts[S] = th[S]; ds = F(ts) - y0; ns = np.linalg.norm(ds)
        cs.append(float(d @ ds / (nf * ns)) if ns > 0 else 0.0)
        er = float(np.linalg.norm(d - ds) / nf); es.append(er)

        def resid(u):
            t = th0.copy(); t[S] = np.exp(u)
            return (F(t) - yf) / nf
        mejor = er
        for x0 in (np.clip(np.log(th[S]), lo, hi), np.log(th0[S])):
            r = least_squares(resid, x0, bounds=(lo, hi), method="trf", diff_step=1e-3,
                              max_nfev=100 * (len(S) + 1))
            mejor = min(mejor, float(np.linalg.norm(r.fun)))
        fs.append(mejor)
    med = lambda v: float(np.median(v)) if v else float("nan")
    return med(cs), med(es), med(fs), len(fs)


def corre(var):
    F = VARIANTES[var]
    y0 = F(th0)
    J = np.zeros((y0.size, p))
    for j in range(p):
        tp, tm = th0.copy(), th0.copy(); tp[j] *= 1 + DELTA; tm[j] *= 1 - DELTA
        J[:, j] = (F(tp) - F(tm)) / (2 * DELTA)
    E = (J ** 2).sum(0); tot = E.sum()
    rvar = lambda S: float(E[S].sum() / tot)
    memo = {}

    def adm(S):
        key = tuple(sorted(S))
        if key not in memo:
            memo[key] = evalua(F, y0, list(key), 0.05)
        return len(S) >= KMIN and memo[key][2] <= EMAX

    # colinealidad del conjunto completo
    Z = norm_cols(J, list(range(p)))
    C = Z.T @ Z
    pares = sorted([(abs(C[i, j]), names[i], names[j]) for i in range(p) for j in range(i + 1, p)
                    if abs(C[i, j]) >= 0.95], reverse=True)
    nulos = [names[j] for j in range(p) if E[j] < 1e-20 * E.max()]
    vivos = [j for j in range(p) if names[j] not in nulos]
    col = {"sin_efecto": nulos, "kappa_con_efecto": kappa(J, vivos), "VIF_max_con_efecto": vif(J, vivos),
           "kappa_todos": kappa(J, list(range(p))), "VIF_max_todos": vif(J, list(range(p))),
           "pares_cos_ge_0.95": [{"a": a, "b": b, "cos": float(c)} for c, a, b in pares]}

    orden1 = [int(j) for j in np.argsort(-E) if E[j] > 0]
    S1, ok1, desc1 = greedy(J, orden1, lambda S: rvar(S) >= TAU_R and len(S) >= KMIN)
    res = {"variante": var, "p": p, "n_salidas": int(y0.size), "colinealidad": col,
           "S1": [names[j] for j in S1], "Rvar_S1_%": 100 * rvar(S1), "descartes_etapa1": desc1}
    if ok1 and adm(S1):
        S, etapa = S1, "Stage 1"
    else:
        s = np.zeros(p)
        for j in range(p):
            tp = th0.copy(); tp[j] *= 1 + ETA
            s[j] = np.linalg.norm(F(tp) - y0)
        orden2 = [int(j) for j in np.argsort(-s) if s[j] > 0]
        S, ok2, desc2 = greedy(J, orden2, adm)
        res["descartes_etapa2"] = desc2
        etapa = "Stage 2" if ok2 else "no admisible"
    antes = list(S)
    if etapa != "no admisible":            # poda: quitar en orden creciente de energía
        cambio = True
        while cambio:
            cambio = False
            for j in sorted(S, key=lambda j: E[j]):
                T = [x for x in S if x != j]
                if adm(T):
                    S = T; cambio = True; break
    c, e, f, n = evalua(F, y0, S, 0.05)
    res.update({"etapa": etapa, "S_antes_poda": [names[j] for j in antes], "S": [names[j] for j in S],
                "podados": [names[j] for j in antes if j not in S], "Rvar_%": 100 * rvar(S),
                "kappa": kappa(J, S), "VIF": vif(J, S), "cos_med": c, "erel_med": e,
                "eajuste_med": f, "n_escenarios": n, "admisible": etapa != "no admisible"})
    if res["admisible"]:
        niv = {}
        for nv in NIVELES:
            c, e, f, n = evalua(F, y0, S, nv)
            niv[str(int(round(100 * nv)))] = {"cos_med": c, "erel_med": e, "eaj_med": f, "n": n}
        ok = [niv[k]["eaj_med"] <= EMAX for k in niv]
        if all(ok):
            pat = "A"
        else:
            i = ok.index(False)
            pat = "C" if any(ok[i:]) else ("B" if NIVELES[i] >= 0.20 else "D")
        res.update({"niveles": niv, "patron": pat})
    (OUT / f"{var}{SUF}.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    return res


def resumen(rs):
    L = [f"# SCT Bandura con el método final (valores: {VALORES}; entradas: {ENTRADAS})", "",
         f"Modelo lineal de 6 estados, 22 parámetros, {len(M.INPUTS)} condiciones de entrada; salida medida y = x₄. "
         "Sin datos experimentales ni parámetros de calibración.", "",
         "| Variante | Salidas | Sin efecto | κ (con efecto) | VIF máx (con efecto) | Pares con cos ≥ 0,95 | Etapa | S | e_rel ±5 % | e_ajuste ±5 % | Patrón |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rs:
        c = r["colinealidad"]
        L.append(f"| {r['variante']} | {r['n_salidas']} | {', '.join(c['sin_efecto']) or '—'} | {c['kappa_con_efecto']:.3g} | {c['VIF_max_con_efecto']:.3g} | "
                 f"{len(c['pares_cos_ge_0.95'])} | {r['etapa']} | {', '.join(r['S'])} | "
                 f"{100 * r['erel_med']:.1f} % | {100 * r['eajuste_med']:.1f} % | {r.get('patron', '—')} |")
    for r in rs:
        L += ["", f"## {r['variante']}", "",
              f"* Etapa 1: {', '.join(r['S1'])} (R_var = {r['Rvar_S1_%']:.1f} %).",
              f"* Antes de la poda: {', '.join(r['S_antes_poda'])}; podados: {', '.join(r['podados']) or '—'}.",
              "* Pares casi colineales (cos ≥ 0,95): " + (", ".join(
                  f"{q['a']}–{q['b']} ({q['cos']:.3f})" for q in r["colinealidad"]["pares_cos_ge_0.95"][:12]) or "—") + "."]
        d = r.get("descartes_etapa1", []) + r.get("descartes_etapa2", [])
        if d:
            L += ["* Candidatos descartados por κ/VIF: " + ", ".join(
                f"{x['parametro']} (con {x['mas_colineal_con']}, cos = {x['cos']:.3f})" for x in d[:15]) + "."]
        if "niveles" in r:
            L += ["* e_ajuste por nivel: " + ", ".join(
                f"±{k} %: {100 * v['eaj_med']:.1f} %" for k, v in r["niveles"].items()) + "."]
    (OUT / f"SCT_BANDURA{SUF}.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    resumen([corre(v) for v in ("salida", "estados")])
