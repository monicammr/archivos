#!/usr/bin/env python3
"""Reclasificación v2 (misma regla que stage_reclass.py --v2) para SCT Bandura.
Uso: python3 sct_reclass.py ruta/a/sct_fim_greedy.py"""
import sys, json, importlib.util
from pathlib import Path
import numpy as np
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
def valida(S):
    cs, es = [], []
    for th in escen:
        df_ = F(th) - y0
        ts = th0.copy(); ts[S] = th[S]; ds_ = F(ts) - y0
        nf, ns = np.linalg.norm(df_), np.linalg.norm(ds_)
        if nf == 0 or ns == 0: continue
        cs.append(float(df_ @ ds_ / (nf * ns))); es.append(float(np.linalg.norm(df_ - ds_) / nf))
    return float(np.median(cs)), float(np.median(es)), len(cs)
res = {"sistema": "SCT_Bandura", "p": p, "etapa_paper": "Stage 1 (FIM, VIF relajado)",
       "S_paper": ["beta43", "beta54", "beta34", "beta14", "gamma33"]}
orden1 = [int(j) for j in np.argsort(-E) if E[j] > 0]
S1, ok1 = R.greedy(J, orden1, lambda S: rvar(S) >= R.RVAR_MIN and len(S) >= 2)
res.update({"S1": [names[j] for j in S1], "Rvar_S1_%": 100 * rvar(S1) if S1 else 0.0})
pasa = False
if ok1:
    c, e, n = valida(S1); pasa = R.admisible(c, e)
    res.update({"cos_S1": c, "erel_S1": e})
if pasa:
    S = S1; etapa = "Stage 1"
else:
    s = np.array([np.linalg.norm(F(np.where(np.arange(p) == j, th0 * 1.1, th0)) - y0) for j in range(p)])
    orden2 = [int(j) for j in np.argsort(-s) if s[j] > 0]
    S, _ = R.greedy(J, orden2, lambda S: len(S) >= 2 and R.admisible(*valida(S)[:2]))
    etapa = "Stage 2"
c, e, n = valida(S)
res.update({"etapa": etapa, "S": [names[j] for j in S], "Rvar_%": 100 * rvar(S),
            "kappa": R.kappa(J, S), "VIF": R.vif(J, S), "cos_med": c, "erel_med": e,
            "n_escenarios": n, "admisible": R.admisible(c, e) and len(S) >= 2})
print(json.dumps(res, indent=1))
d = R.OUT / "reclasificacion_v2"; d.mkdir(exist_ok=True)
(d / "SCT_Bandura.json").write_text(json.dumps(res, indent=1))
