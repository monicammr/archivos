#!/usr/bin/env python3
"""Reclasificación v3 (admisible ⇔ |S| ≥ 2 y e_ajuste ≤ 0,436) para SCT Bandura.
Uso: python3 sct_reclass_v3.py ruta/a/sct_fim_greedy.py"""
import sys, json, importlib.util
import numpy as np
from scipy.optimize import least_squares
sys.argv.append("--v2")
import stage_reclass as R

spec = importlib.util.spec_from_file_location("sct", sys.argv[1])
sct = importlib.util.module_from_spec(spec); sys.modules["sct"] = sct; spec.loader.exec_module(sct)
th0 = sct.THETA_NOM.copy(); names = list(sct.PARAM_NAMES); p = len(th0)
F = lambda th: np.asarray(sct.simulate_all(th), dtype=float).ravel()
y0 = F(th0)
J = np.zeros((y0.size, p))
for j in range(p):
    tp, tm = th0.copy(), th0.copy(); tp[j] *= 1 + R.DELTA; tm[j] *= 1 - R.DELTA
    J[:, j] = (F(tp) - F(tm)) / (2 * R.DELTA)
E = (J ** 2).sum(0); tot = E.sum()
rvar = lambda S: float(E[S].sum() / tot)
rng = np.random.default_rng(R.SEED)
escen = [th0 * (1 + R.NIVEL * rng.uniform(-1, 1, size=p)) for _ in range(R.N_ESC)]
full = [F(th) for th in escen]

def valida(S):
    cs, es = [], []
    for th, yf in zip(escen, full):
        df_ = yf - y0; ts = th0.copy(); ts[S] = th[S]; ds_ = F(ts) - y0
        nf, ns = np.linalg.norm(df_), np.linalg.norm(ds_)
        if nf == 0 or ns == 0: continue
        cs.append(float(df_ @ ds_ / (nf * ns))); es.append(float(np.linalg.norm(df_ - ds_) / nf))
    return float(np.median(cs)), float(np.median(es))

def ajuste(S):
    sgn = np.where(th0[S] < 0, -1.0, 1.0); mag0 = np.abs(th0[S])
    lo, hi = np.log(mag0 / 10), np.log(mag0 * 10); out = []
    for th, yf in zip(escen, full):
        nf = np.linalg.norm(yf - y0)
        def resid(u):
            ts = th0.copy(); ts[S] = sgn * np.exp(u); return (F(ts) - yf) / nf
        ts = th0.copy(); ts[S] = th[S]; best = float(np.linalg.norm(F(ts) - yf) / nf)
        for x0 in (np.log(mag0), np.clip(np.log(np.abs(th[S])), lo, hi)):
            r = least_squares(resid, x0, bounds=(lo, hi), method="trf", diff_step=1e-3,
                              max_nfev=100 * (len(S) + 1))
            best = min(best, float(np.linalg.norm(r.fun)))
        out.append(best)
    return float(np.median(out))

def admisible3(S):
    if len(S) < 2: return False
    c, e = valida(S)
    return e <= R.EREL_MAX or ajuste(S) <= R.EREL_MAX

res = {"sistema": "SCT_Bandura", "p": p, "etapa_paper": "Stage 1 (FIM, VIF relajado)",
       "S_paper": ["beta43", "beta54", "beta34", "beta14", "gamma33"]}
orden1 = [int(j) for j in np.argsort(-E) if E[j] > 0]
S1, ok1 = R.greedy(J, orden1, lambda S: rvar(S) >= R.RVAR_MIN and len(S) >= 2)
res.update({"S1": [names[j] for j in S1], "Rvar_S1_%": 100 * rvar(S1) if S1 else 0.0})
if ok1 and admisible3(S1):
    S, etapa = S1, "Stage 1"
else:
    s = np.array([np.linalg.norm(F(np.where(np.arange(p) == j, th0 * 1.1, th0)) - y0) for j in range(p)])
    orden2 = [int(j) for j in np.argsort(-s) if s[j] > 0]
    S, _ = R.greedy(J, orden2, admisible3); etapa = "Stage 2"
c, e = valida(S); ea = ajuste(S)
res.update({"etapa": etapa, "S": [names[j] for j in S], "Rvar_%": 100 * rvar(S),
            "kappa": R.kappa(J, S), "VIF": R.vif(J, S), "cos_med": c, "erel_med": e,
            "eajuste_med": ea, "n_escenarios": len(escen),
            "admisible": bool(len(S) >= 2 and min(ea, e) <= R.EREL_MAX)})
print(json.dumps(res, indent=1))
d = R.OUT / "reclasificacion_v3"; d.mkdir(exist_ok=True)
(d / "SCT_Bandura.json").write_text(json.dumps(res, indent=1))
