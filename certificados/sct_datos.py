#!/usr/bin/env python3
"""
SCT Bandura con datos reales (31 días) y el método final, con el mismo esquema que los
problemas PEtab.

Modelo (ss_from_theta.m): ẋ = A(θ)x + B(θ)u, y = x₄ (conducta, pasos diarios); 22 parámetros
(τ1..τ6, β14..β54, γ33..γ68), 6 entradas ξ3..ξ8. Datos: datos_sct/datos_sct_31dias.csv
(no se publican). Entradas y salida normalizadas con puntaje z (como en los scripts de MATLAB);
simulación exacta con retenedor de orden cero y Ts = 1 día; estado inicial x(0) estimado
(6 parámetros "de calibración", siempre reestimados, como los offsets de PEtab).

Pasos
  1. θ₀ = ajuste de los 22 parámetros + x(0) a los 31 días (multiarranque; incluye la Tabla III
     del ETCM 2025 como punto de partida). Equivale a la estimación publicada de PEtab.
  2. σ = desviación estándar de los residuos en θ₀ (ruido de medición); salidas y_i / σ.
  3. Método final: J relativa, etapa 1 (E_j, κ/VIF ≤ 10, R_var ≥ 0,89), admisibilidad
     (|S| ≥ 2, mediana e_ajuste ≤ 0,436, 15 escenarios ±5 %), etapa 2 (s_j), poda, patrones.
  4. Validación externa: reducido (S + x0) y completo (22 + x0) reajustados con los días 1–24
     desde θ₀; χ²/n en los días 25–31.

Uso: python3 sct_datos.py  → resultados/sct_bandura/datos_reales.json y SCT_DATOS_REALES.md
"""
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.linalg import expm
from scipy.optimize import least_squares

HERE = Path(__file__).resolve().parent
OUT = HERE / "resultados" / "sct_bandura"; OUT.mkdir(parents=True, exist_ok=True)
NAMES = ["tau1", "tau2", "tau3", "tau4", "tau5", "tau6",
         "beta14", "beta21", "beta25", "beta31", "beta34", "beta42", "beta43", "beta45", "beta46", "beta54",
         "gamma33", "gamma35", "gamma36", "gamma57", "gamma64", "gamma68"]
P = len(NAMES)
ETCM = [0.8155, 5, 3.4696, 0.3655, 0.1636, 0.1, 0.8637, 0.2058, 0.6155, 0.6217, 0.2372, 0.2515,
        0.3709, 0.9084, 0.1, 0.6224, 0.1, 0.9999, 0.1, 0.9555, 0.5217, 0.1]
LO, HI = 1e-3, 50.0                 # límites (positivos) para el ajuste de θ₀, en log
DELTA, ETA, TAU_R, TAU_K, EMAX, KMIN = 0.01, 0.1, 0.89, 10.0, float(np.sqrt(1 - 0.81)), 2
N_ESC, SEED, NIVELES = 15, 42, [0.01, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50]
N_TRAIN = 24                         # días 1–24 entrenamiento, 25–31 prueba

d = pd.read_csv(HERE / "datos_sct" / "datos_sct_31dias.csv")
U_raw = d[["xi3", "xi4", "xi5", "xi6", "xi7", "xi8"]].to_numpy(float)
Y_raw = d["eta4"].to_numpy(float)
U = (U_raw - U_raw.mean(0)) / U_raw.std(0, ddof=1)
Y = (Y_raw - Y_raw.mean()) / Y_raw.std(ddof=1)
N = len(Y)


def AB(th):
    t1, t2, t3, t4, t5, t6 = np.maximum(th[:6], 1e-9)
    b14, b21, b25, b31, b34, b42, b43, b45, b46, b54 = th[6:16]
    g33, g35, g36, g57, g64, g68 = th[16:22]
    A = np.array([[-1 / t1, 0, 0, b14 / t1, 0, 0],
                  [b21 / t2, -1 / t2, 0, 0, b25 / t2, 0],
                  [b31 / t3, 0, -1 / t3, b34 / t3, 0, 0],
                  [0, b42 / t4, b43 / t4, -1 / t4, b45 / t4, b46 / t4],
                  [0, 0, 0, b54 / t5, -1 / t5, 0],
                  [0, 0, 0, 0, 0, -1 / t6]])
    B = np.zeros((6, 6))
    B[2, 0], B[2, 2], B[2, 3] = g33 / t3, -g35 / t3, g36 / t3
    B[4, 4] = g57 / t5
    B[5, 1], B[5, 5] = g64 / t6, g68 / t6
    return A, B


def sim(th, x0, n=N):
    """Salida y = x₄ en los días 0..n-1 (ZOH, Ts = 1); None si A es inestable."""
    A, B = AB(th)
    if np.max(np.linalg.eigvals(A).real) >= 0:
        return None
    M = np.zeros((12, 12)); M[:6, :6] = A; M[:6, 6:] = B
    E = expm(M); Ad, Bd = E[:6, :6], E[:6, 6:]
    x = np.array(x0, float); y = np.empty(n)
    for k in range(n):
        y[k] = x[3]
        x = Ad @ x + Bd @ U[k]
    return y


def fit(free, th_ini, x0_ini, dias, starts=()):
    """Reajusta θ[free] (en log, dentro de [LO, HI]) y x(0) con los días `dias`."""
    free = list(free)
    lo = np.r_[np.full(len(free), np.log(LO)), np.full(6, -50.0)]
    hi = np.r_[np.full(len(free), np.log(HI)), np.full(6, 50.0)]

    def unpack(v):
        th = np.array(th_ini, float); th[free] = np.exp(v[:len(free)]); return th, v[len(free):]

    def res(v):
        th, x0 = unpack(v)
        y = sim(th, x0)
        return np.full(len(dias), 1e3) if y is None else y[dias] - Y[dias]
    best = None
    inis = [np.r_[np.log(np.clip(np.asarray(th_ini, float)[free], LO, HI)), x0_ini]] + list(starts)
    for v0 in inis:
        try:
            r = least_squares(res, np.clip(v0, lo + 1e-9, hi - 1e-9), bounds=(lo, hi), method="trf",
                              max_nfev=200 * (len(free) + 7), x_scale="jac")
        except Exception:
            continue
        if best is None or r.cost < best.cost:
            best = r
    th, x0 = unpack(best.x)
    return th, x0, float(2 * best.cost)


# ---------------------------------------------------------------- 1. θ₀ con los 31 días
rng = np.random.default_rng(SEED)
todos = np.arange(N)
starts = [np.r_[np.log(np.clip(rng.uniform(0.1, 5, P), LO, HI)), np.zeros(6)] for _ in range(20)]
th0, x00, sse0 = fit(range(P), ETCM, np.zeros(6), todos, starts)
y0 = sim(th0, x00)
fit_pct = 100 * (1 - np.linalg.norm(Y - y0) / np.linalg.norm(Y - Y.mean()))
r2 = 1 - np.sum((Y - y0) ** 2) / np.sum((Y - Y.mean()) ** 2)
sigma = float(np.std(Y - y0, ddof=1))
y_etcm = None
try:
    _, _, sse_etcm = fit([], ETCM, np.zeros(6), todos)
    fit_etcm = 100 * (1 - np.sqrt(sse_etcm) / np.linalg.norm(Y - Y.mean()))
except Exception:
    fit_etcm = float("nan")
print(f"θ₀: fit {fit_pct:.1f} %, R² {r2:.3f} (Tabla III ETCM con x0 estimado: fit {fit_etcm:.1f} %)", flush=True)


# ---------------------------------------------------------------- 2–3. método final
def F(th):
    y = sim(th, x00)
    return None if y is None else y / sigma


f0 = F(th0)
J = np.zeros((N, P))
for j in range(P):
    tp, tm = th0.copy(), th0.copy(); tp[j] *= 1 + DELTA; tm[j] *= 1 - DELTA
    a, b = F(tp), F(tm)
    if a is not None and b is not None:
        J[:, j] = (a - b) / (2 * DELTA)
E = (J ** 2).sum(0); rvar = lambda S: float(E[S].sum() / E.sum())


def ncol(idx):
    Z = J[:, idx]; n = np.linalg.norm(Z, axis=0); return Z / np.where(n > 0, n, 1)


def kappa(idx):
    if len(idx) < 2: return 1.0
    s = np.linalg.svd(ncol(idx), compute_uv=False); return float("inf") if s[-1] < 1e-12 else float(s[0] / s[-1])


def vif(idx):
    if len(idx) < 2: return 1.0
    G = ncol(idx).T @ ncol(idx)
    try: return float(np.max(np.diag(np.linalg.inv(G))))
    except np.linalg.LinAlgError: return float("inf")


def escen(nivel):
    r = np.random.default_rng(SEED)
    return [th0 * (1 + nivel * r.uniform(-1, 1, P)) for _ in range(N_ESC)]


def evalua(S, nivel):
    """Medianas de cos Δ, e_rel y e_ajuste (reajuste de θ_S y x0) en 15 escenarios."""
    cs, es, fs = [], [], []
    for th in escen(nivel):
        yf = F(th)
        if yf is None: continue
        dlt = yf - f0; nf = np.linalg.norm(dlt)
        if nf < 1e-10: continue
        ts = th0.copy(); ts[S] = th[S]; ys = F(ts)
        if ys is None: continue
        ds = ys - f0; ns = np.linalg.norm(ds)
        cs.append(float(dlt @ ds / (nf * ns)) if ns > 0 else 0.0)
        er = float(np.linalg.norm(dlt - ds) / nf); es.append(er)
        lo_, hi_ = np.log(th0[S] / 10), np.log(th0[S] * 10)

        def res(v):
            t = th0.copy(); t[S] = np.exp(v[:len(S)])
            y = sim(t, x00 + v[len(S):])
            return np.full(N, 10.0) if y is None else (y / sigma - yf) / nf
        mejor = er
        for v0 in (np.r_[np.clip(np.log(th[S]), lo_, hi_), np.zeros(6)], np.r_[np.log(th0[S]), np.zeros(6)]):
            try:
                r = least_squares(res, v0, bounds=(np.r_[lo_, np.full(6, -50)], np.r_[hi_, np.full(6, 50)]),
                                  method="trf", max_nfev=100 * (len(S) + 7), diff_step=1e-3)
                mejor = min(mejor, float(np.linalg.norm(r.fun)))
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
            desc.append({"parametro": NAMES[j], "mas_colineal_con": NAMES[S[int(np.argmax(c))]] if S else None,
                         "cos": float(c.max())})
    return S, False, desc


Zall = ncol(list(range(P))); C = Zall.T @ Zall
pares = sorted([(abs(C[i, j]), NAMES[i], NAMES[j]) for i in range(P) for j in range(i + 1, P) if abs(C[i, j]) >= 0.95], reverse=True)
orden1 = [int(j) for j in np.argsort(-E) if E[j] > 0]
S1, ok1, desc1 = greedy(orden1, lambda S: rvar(S) >= TAU_R and len(S) >= KMIN)
if ok1 and adm(S1):
    S, etapa, desc2 = S1, "Stage 1", []
else:
    s = np.zeros(P)
    for j in range(P):
        tp = th0.copy(); tp[j] *= 1 + ETA; a = F(tp)
        s[j] = np.inf if a is None else np.linalg.norm(a - f0)
    orden2 = [int(j) for j in np.argsort(-s) if s[j] > 0 and np.isfinite(s[j])]
    S, ok2, desc2 = greedy(orden2, adm)
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
print(f"S = {[NAMES[j] for j in S]} ({etapa}); e_ajuste ±5 % = {100 * f5:.1f} %", flush=True)

niv = {}
for nv in NIVELES:
    c, e, f, n = evalua(S, nv); niv[str(int(round(100 * nv)))] = {"cos_med": c, "erel_med": e, "eaj_med": f, "n": n}
ok = [niv[k]["eaj_med"] <= EMAX for k in niv]
pat = "A" if all(ok) else ("C" if any(ok[ok.index(False):]) else ("B" if NIVELES[ok.index(False)] >= 0.2 else "D"))

# ---------------------------------------------------------------- 4. validación externa
tr, te = np.arange(N_TRAIN), np.arange(N_TRAIN, N)
chi = lambda y: float(np.mean(((y[te] - Y[te]) / sigma) ** 2))
th_r, x0_r, _ = fit(S, th0, x00, tr)
th_f, x0_f, _ = fit(range(P), th0, x00, tr)
val = {"chi2_test_red": chi(sim(th_r, x0_r)), "chi2_test_full": chi(sim(th_f, x0_f)), "chi2_test_theta0": chi(y0),
       "chi2_train_red": float(np.mean(((sim(th_r, x0_r)[tr] - Y[tr]) / sigma) ** 2)),
       "chi2_train_full": float(np.mean(((sim(th_f, x0_f)[tr] - Y[tr]) / sigma) ** 2))}
print("validación (χ²/n días 25–31): reducido %.2f | completo %.2f | θ₀ %.2f" %
      (val["chi2_test_red"], val["chi2_test_full"], val["chi2_test_theta0"]), flush=True)

res = {"sistema": "SCT_Bandura_datos_reales", "p": P, "n_dias": N, "theta0": dict(zip(NAMES, th0.tolist())),
       "x0": x00.tolist(), "fit_theta0_pct": fit_pct, "R2_theta0": r2, "fit_tablaIII_ETCM_pct": fit_etcm,
       "sigma": sigma, "kappa_todos": kappa(list(range(P))), "VIF_todos": vif(list(range(P))),
       "pares_cos_ge_0.95": [{"a": a, "b": b, "cos": float(c)} for c, a, b in pares],
       "S1": [NAMES[j] for j in S1], "Rvar_S1_%": 100 * rvar(S1), "etapa": etapa,
       "S_antes_poda": [NAMES[j] for j in antes], "S": [NAMES[j] for j in S],
       "podados": [NAMES[j] for j in antes if j not in S], "kappa": kappa(S), "VIF": vif(S),
       "cos_med": c5, "erel_med": e5, "eajuste_med": f5, "n_escenarios": n5, "admisible": etapa != "no admisible",
       "descartes": desc1 + desc2, "niveles": niv, "patron": pat, "validacion": val}
(OUT / "datos_reales.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
L = ["# SCT Bandura con datos reales (31 días) y el método final", "",
     f"* θ₀ (22 parámetros + x(0), ajustados a los 31 días): fit {fit_pct:.1f} %, R² = {r2:.3f}. "
     f"Con los parámetros de la Tabla III del ETCM 2025 (sólo x(0) estimado): fit {fit_etcm:.1f} %.",
     f"* κ (22 parámetros) = {res['kappa_todos']:.3g}; VIF máx = {res['VIF_todos']:.3g}; pares con cos ≥ 0,95: {len(pares)}.",
     f"* Selección: {etapa}; S = {', '.join(res['S'])}; podados: {', '.join(res['podados']) or '—'}.",
     f"* ±5 %: cos Δ = {c5:.3f}, e_rel = {100 * e5:.1f} %, e_ajuste = {100 * f5:.1f} %; patrón {pat}.",
     "* e_ajuste por nivel: " + ", ".join(f"±{k} %: {100 * v['eaj_med']:.1f} %" for k, v in niv.items()) + ".",
     f"* Validación externa (entrenamiento días 1–24, prueba 25–31), χ²/n de prueba: reducido "
     f"{val['chi2_test_red']:.2f}, completo {val['chi2_test_full']:.2f}, θ₀ (vio los 31 días) {val['chi2_test_theta0']:.2f}."]
(OUT / "SCT_DATOS_REALES.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
