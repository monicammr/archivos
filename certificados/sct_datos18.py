#!/usr/bin/env python3
"""
SCT con datos reales (31 días) y el modelo de 18 parámetros de la estimación por evolución
diferencial del ETCM 2025 (sct_modelo18.py), con el método final.

  1. θ₀: evolución diferencial con la configuración del notebook original (límites β ∈ [0, 2],
     γ ∈ [0, 3000], τ ∈ [0,01; 10]; población inicial = valores del notebook + ruido 0,1;
     3 semillas). θ₀ = solución de la semilla 1, que reproduce el R² = 0,8505 de la corrida
     original. Las otras semillas se guardan para mostrar la no identificabilidad.
  2. σ = desviación estándar de los residuos en θ₀; salidas y/σ.
  3. Método final (J relativa, etapa 1/2, admisibilidad con e_ajuste ≤ 0,436 en 15 escenarios
     ±5 %, poda, patrones ±1…50 %). Los parámetros sin efecto sobre x4 (sensibilidad nula)
     no son candidatos (x1 no recibe entradas y ξ4 es constante).
  4. Validación: reducido (S) y completo (18) reajustados con los días 1–24 desde θ₀ dentro de
     los límites del notebook; χ²/n en los días 25–31.
"""
import json
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares, differential_evolution
import sct_modelo18 as M

HERE = Path(__file__).resolve().parent
OUT = HERE / "resultados" / "sct_bandura"; OUT.mkdir(parents=True, exist_ok=True)
P = len(M.NAMES); N = M.N; Y = M.Y
LO = np.array([b[0] for b in M.BOUNDS]); HI = np.array([b[1] for b in M.BOUNDS])
DELTA, ETA, TAU_R, TAU_K, EMAX, KMIN = 0.01, 0.1, 0.89, 10.0, float(np.sqrt(1 - 0.81)), 2
N_ESC, SEED, NIVELES = 15, 42, [0.01, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50]
N_TRAIN = 24

# ------------------------------------------------------------- 1. θ₀ por evolución diferencial
sols = []
for seed in (0, 1, 2):
    rng = np.random.default_rng(seed)
    init = np.clip(M.INI + 0.1 * rng.standard_normal((10, P)), LO, HI)
    r = differential_evolution(lambda p: float(np.mean((Y - M.sim(p)) ** 2)), M.BOUNDS, maxiter=1000,
                               popsize=15, polish=False, tol=1e-8, init=init, seed=seed)
    sols.append(r.x)
th0 = sols[1]
y0 = M.sim(th0)
r2_0 = M.r2(y0)
sigma = float(np.std(Y - y0, ddof=1))
print(f"θ₀ (semilla 1): R² = {r2_0:.4f}; otras semillas: " +
      ", ".join(f"{M.r2(M.sim(s)):.4f}" for i, s in enumerate(sols) if i != 1), flush=True)

F = lambda th: M.sim(th) / sigma
f0 = F(th0)
J = np.zeros((N, P))
for j in range(P):
    if th0[j] == 0: continue
    tp, tm = th0.copy(), th0.copy(); tp[j] *= 1 + DELTA; tm[j] *= 1 - DELTA
    J[:, j] = (F(tp) - F(tm)) / (2 * DELTA)
E = (J ** 2).sum(0); act = [j for j in range(P) if E[j] > 1e-20 * E.max()]
rvar = lambda S: float(E[S].sum() / E.sum())


def ncol(idx):
    Z = J[:, idx]; n = np.linalg.norm(Z, axis=0); return Z / np.where(n > 0, n, 1)


def kappa(idx):
    if len(idx) < 2: return 1.0
    s = np.linalg.svd(ncol(idx), compute_uv=False); return float("inf") if s[-1] < 1e-12 else float(s[0] / s[-1])


def vif(idx):
    if len(idx) < 2: return 1.0
    try: return float(np.max(np.diag(np.linalg.inv(ncol(idx).T @ ncol(idx)))))
    except np.linalg.LinAlgError: return float("inf")


def escen(nivel):
    r = np.random.default_rng(SEED)
    return [th0 * (1 + nivel * r.uniform(-1, 1, P)) for _ in range(N_ESC)]


def evalua(S, nivel):
    cs, es, fs = [], [], []
    lo_, hi_ = np.log(th0[S] / 10), np.log(th0[S] * 10)
    for th in escen(nivel):
        yf = F(th); dlt = yf - f0; nf = np.linalg.norm(dlt)
        if nf < 1e-10: continue
        ts = th0.copy(); ts[S] = th[S]; ds = F(ts) - f0; ns = np.linalg.norm(ds)
        cs.append(float(dlt @ ds / (nf * ns)) if ns > 0 else 0.0)
        er = float(np.linalg.norm(dlt - ds) / nf); es.append(er)

        def res(v):
            t = th0.copy(); t[S] = np.exp(v); return (F(t) - yf) / nf
        mejor = er
        for v0 in (np.clip(np.log(th[S]), lo_, hi_), np.log(th0[S])):
            try:
                rr = least_squares(res, v0, bounds=(lo_, hi_), method="trf", max_nfev=100 * (len(S) + 1), diff_step=1e-3)
                mejor = min(mejor, float(np.linalg.norm(rr.fun)))
            except Exception:
                pass
        fs.append(mejor)
    med = lambda v: float(np.median(v)) if v else float("nan")
    return med(cs), med(es), med(fs), len(fs)


memo = {}
def adm(S):
    k = tuple(sorted(S))
    if k not in memo: memo[k] = evalua(list(k), 0.05)
    return len(S) >= KMIN and memo[k][2] <= EMAX


def greedy(orden, parar):
    S, desc = [], []
    for j in orden:
        if kappa(S + [j]) <= TAU_K and vif(S + [j]) <= TAU_K:
            S.append(j)
            if parar(S): return S, True, desc
        else:
            Z = ncol(S + [j]); c = np.abs(Z[:, :-1].T @ Z[:, -1]) if S else np.array([0.0])
            desc.append({"parametro": M.NAMES[j], "mas_colineal_con": M.NAMES[S[int(np.argmax(c))]] if S else None, "cos": float(c.max())})
    return S, False, desc


C = ncol(act).T @ ncol(act)
pares = sorted([(abs(C[a, b]), M.NAMES[act[a]], M.NAMES[act[b]]) for a in range(len(act)) for b in range(a + 1, len(act)) if abs(C[a, b]) >= 0.95], reverse=True)
orden1 = sorted(act, key=lambda j: -E[j])
S1, ok1, desc1 = greedy(orden1, lambda S: rvar(S) >= TAU_R and len(S) >= KMIN)
if ok1 and adm(S1):
    S, etapa, desc2 = S1, "Stage 1", []
else:
    s = np.zeros(P)
    for j in act:
        tp = th0.copy(); tp[j] *= 1 + ETA; s[j] = np.linalg.norm(F(tp) - f0)
    S, ok2, desc2 = greedy(sorted(act, key=lambda j: -s[j]), adm)
    etapa = "Stage 2" if ok2 else "no admisible"
antes = list(S)
if etapa != "no admisible":
    cambio = True
    while cambio:
        cambio = False
        for j in sorted(S, key=lambda j: E[j]):
            T = [x for x in S if x != j]
            if adm(T): S = T; cambio = True; break
c5, e5, f5, n5 = evalua(S, 0.05)
niv = {}
for nv in NIVELES:
    c, e, f, n = evalua(S, nv); niv[str(int(round(100 * nv)))] = {"cos_med": c, "erel_med": e, "eaj_med": f, "n": n}
ok = [niv[k]["eaj_med"] <= EMAX for k in niv]
pat = "A" if all(ok) else ("C" if any(ok[ok.index(False):]) else ("B" if NIVELES[ok.index(False)] >= 0.2 else "D"))
print(f"S = {[M.NAMES[j] for j in S]} ({etapa}); e_ajuste ±5 % = {100 * f5:.1f} %; patrón {pat}", flush=True)

# ------------------------------------------------------------- 4. validación externa (días 1–24 → 25–31)
tr, te = np.arange(N_TRAIN), np.arange(N_TRAIN, N)


def refit(free):
    free = list(free)
    def res(v):
        t = th0.copy(); t[free] = v; return (M.sim(t)[tr] - Y[tr]) / sigma
    rr = least_squares(res, np.clip(th0[free], LO[free], HI[free]), bounds=(LO[free], HI[free] + 1e-12),
                       method="trf", max_nfev=200 * (len(free) + 1), x_scale="jac")
    t = th0.copy(); t[free] = rr.x; return t


chi = lambda th, idx: float(np.mean(((M.sim(th)[idx] - Y[idx]) / sigma) ** 2))
th_r, th_f = refit(S), refit(range(P))
val = {"chi2_test_red": chi(th_r, te), "chi2_test_full": chi(th_f, te), "chi2_test_theta0": chi(th0, te),
       "chi2_train_red": chi(th_r, tr), "chi2_train_full": chi(th_f, tr),
       "R2_test_red": M.r2(M.sim(th_r), te), "R2_test_full": M.r2(M.sim(th_f), te)}
print("validación χ²/n días 25–31: reducido %.2f | completo %.2f | θ₀ %.2f" %
      (val["chi2_test_red"], val["chi2_test_full"], val["chi2_test_theta0"]), flush=True)

res = {"modelo": "SCT 18 parámetros (DE, ETCM 2025)", "p": P, "n_dias": N,
       "theta0": dict(zip(M.NAMES, th0.tolist())), "R2_theta0": r2_0,
       "soluciones_DE": [{"semilla": i, "R2": M.r2(M.sim(s_)), "theta": dict(zip(M.NAMES, s_.tolist()))} for i, s_ in enumerate(sols)],
       "sigma": sigma, "parametros_sin_efecto_en_x4": [M.NAMES[j] for j in range(P) if j not in act],
       "kappa_activos": kappa(act), "VIF_activos": vif(act),
       "pares_cos_ge_0.95": [{"a": a, "b": b, "cos": float(c)} for c, a, b in pares],
       "S1": [M.NAMES[j] for j in S1], "Rvar_S1_%": 100 * rvar(S1), "etapa": etapa,
       "S_antes_poda": [M.NAMES[j] for j in antes], "S": [M.NAMES[j] for j in S],
       "podados": [M.NAMES[j] for j in antes if j not in S], "kappa": kappa(S), "VIF": vif(S),
       "cos_med": c5, "erel_med": e5, "eajuste_med": f5, "n_escenarios": n5, "admisible": etapa != "no admisible",
       "descartes": desc1 + desc2, "niveles": niv, "patron": pat, "validacion": val}
(OUT / "datos_reales_modelo18.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
L = ["# SCT con datos reales y el modelo de 18 parámetros (evolución diferencial, ETCM 2025)", "",
     f"* θ₀ (semilla 1, reproduce la corrida original): R² = {r2_0:.4f}. Otras semillas: " +
     ", ".join(f"R² = {M.r2(M.sim(s_)):.4f}" for i, s_ in enumerate(sols) if i != 1) + " con parámetros muy distintos (no identificabilidad).",
     f"* Parámetros sin efecto sobre x4 (sensibilidad nula): {', '.join(res['parametros_sin_efecto_en_x4']) or '—'}.",
     f"* κ (activos) = {res['kappa_activos']:.3g}; VIF máx = {res['VIF_activos']:.3g}; pares con cos ≥ 0,95: {len(pares)}.",
     f"* Selección: {etapa}; S = {', '.join(res['S'])}; podados: {', '.join(res['podados']) or '—'}.",
     f"* ±5 %: cos Δ = {c5:.3f}, e_rel = {100 * e5:.1f} %, e_ajuste = {100 * f5:.1f} %; patrón {pat}.",
     "* e_ajuste por nivel: " + ", ".join(f"±{k} %: {100 * v['eaj_med']:.1f} %" for k, v in niv.items()) + ".",
     f"* Validación (entrenamiento días 1–24, prueba 25–31), χ²/n: reducido {val['chi2_test_red']:.2f}, "
     f"completo {val['chi2_test_full']:.2f}, θ₀ {val['chi2_test_theta0']:.2f}; R² de prueba: reducido "
     f"{val['R2_test_red']:.3f}, completo {val['R2_test_full']:.3f}."]
(OUT / "SCT_DATOS_REALES_MODELO18.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
