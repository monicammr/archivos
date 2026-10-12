#!/usr/bin/env python3
"""Datos de la Figura 1 del artículo: cada paso del método aplicado al problema Boehm_JProteomeRes2014
(salidas medidas de PEtab, mismas definiciones que stage_reclass.py --v3 --salidas --poda y
validacion_externa.py). Resultado: resultados/fig1/boehm.json."""
import json
import numpy as np
from scipy.optimize import least_squares
from petab_outputs import PSys
from stage_reclass import kappa, vif

NAME = "Boehm_JProteomeRes2014"
DELTA, NIVEL, N_ESC, SEED, T_SPLIT = 0.01, 0.05, 15, 42, 80.0
S = PSys(NAME)
th0, names = S.theta0, S.names
p = len(th0)
bio = [j for j in range(p) if S.in_model[j] and not S.calib[j]]
y0 = S.sim(th0).ravel()

# 1. sensibilidad relativa J = dy/dlog(theta) (diferencias centradas)
J = np.zeros((y0.size, p))
for j in bio:
    tp, tm = th0.copy(), th0.copy(); tp[j] *= 1 + DELTA; tm[j] *= 1 - DELTA
    J[:, j] = (S.sim(tp).ravel() - S.sim(tm).ravel()) / (2 * DELTA)
E = (J ** 2).sum(0); Etot = E[bio].sum()

# 2. etapa 1: orden por E, filtro kappa/VIF, hasta R_var >= 0.89
order1 = sorted(bio, key=lambda j: -E[j])
S1, rej1 = [], []
for j in order1:
    c = S1 + [j]
    if len(c) == 1 or (kappa(J, c) <= 10 and vif(J, c) <= 10):
        S1 = c
    else:
        rej1.append(j)
    if len(S1) >= 2 and E[S1].sum() / Etot >= 0.89:
        break

# 3. etapa 2: efecto finito s_j
s = np.zeros(p)
for j in bio:
    t = th0.copy(); t[j] *= 1.1
    s[j] = np.linalg.norm(S.sim(t).ravel() - y0)

# etapa 2: mismo filtro kappa/VIF en el orden de s_j (para mostrar los rechazados)
S2, rej2 = [], {}
for j in sorted(bio, key=lambda j: -s[j]):
    if len(S2) == len(json.load(open("resultados/reclasificacion_salidas_bio_poda/" + NAME + ".json"))["S"]):
        break
    c = S2 + [j]
    if len(c) == 1 or (kappa(J, c) <= 10 and vif(J, c) <= 10):
        S2 = c
    else:
        rej2[j] = kappa(J, c)

# 4. escenarios a +-5 % y error con / sin reestimacion
rng = np.random.default_rng(SEED)
esc = [np.maximum(th0 * (1 + NIVEL * rng.uniform(-1, 1, size=p)), 1e-12) for _ in range(N_ESC)]
full = [S.sim(t).ravel() - y0 for t in esc]


def errores(Ssel):
    lo, hi = np.log(th0[Ssel] / 10), np.log(th0[Ssel] * 10)
    erel, efit = [], []
    for th, df in zip(esc, full):
        nf = np.linalg.norm(df); yf = y0 + df
        ts = th0.copy(); ts[Ssel] = th[Ssel]
        erel.append(float(np.linalg.norm(S.sim(ts).ravel() - yf) / nf))

        def resid(u):
            t = th0.copy(); t[Ssel] = np.exp(u)
            ys = S.sim(t)
            return np.full(yf.size, 10.0) if ys is None else (ys.ravel() - yf) / nf
        best = erel[-1]
        for x0 in (np.log(th0[Ssel]), np.clip(np.log(th[Ssel]), lo, hi)):
            r = least_squares(resid, x0, bounds=(lo, hi), method="trf", max_nfev=100 * (len(Ssel) + 1), diff_step=1e-3)
            best = min(best, float(np.linalg.norm(r.fun)))
        efit.append(best)
    return erel, efit


SF = [names.index(n) for n in json.load(open("resultados/reclasificacion_salidas_bio_poda/" + NAME + ".json"))["S"]]
e1_rel, e1_fit = errores(S1)
e2_rel, e2_fit = errores(SF)

# 5. validacion externa con la rutina de validacion_externa.py (misma division y reajuste)
import validacion_externa as VE
zd = S.zdata(); tt = S.mea["time"].to_numpy(float)
train, test, ftest, tipo = VE.division(S)
ftr, fte = ~ftest & np.isfinite(zd), ftest & np.isfinite(zd)
libres_full = [int(j) for j in np.nonzero(S.in_model)[0]]
VE.CKDIR["dir"] = None
tred, _ = VE.ajusta(S, SF, th0, train, zd, ftr, 30 * (len(SF) + 1))
tfull, _ = VE.ajusta(S, libres_full, th0, train, zd, ftr, 15 * (len(libres_full) + 1))
pred = {k: S.z(t) for k, t in (("theta0", th0), ("red", tred), ("full", tfull))}
chi = {k: VE.chi2(v, zd, fte) for k, v in pred.items()}
T_SPLIT = float(tt[ftest].min())
te = fte

# curvas densas (sin escala de ruido) para dibujar
out = dict(names=names, bio=bio, theta0=th0.tolist(), sigma=S.sigma.tolist(), obs=S.mea["observableId"].tolist(), time=tt.tolist(),
           data=zd.tolist(), y0=y0.tolist(), J=J[:, bio].tolist(), E=E[bio].tolist(), order1=order1, S1=S1, rej1=rej1,
           s=s[bio].tolist(), SF=SF, S2=S2, rej2={str(k): v for k, v in rej2.items()}, e1_rel=e1_rel, e1_fit=e1_fit, e2_rel=e2_rel, e2_fit=e2_fit,
           pred={k: v.tolist() for k, v in pred.items()}, chi_test=chi, t_split=T_SPLIT,
           kappa_SF=kappa(J, SF), vif_SF=vif(J, SF), rvar_S1=float(E[S1].sum() / Etot), rvar_SF=float(E[SF].sum() / Etot))
json.dump(out, open("resultados/fig1/boehm.json", "w"), indent=1)
print("S1", [names[j] for j in S1], "rej", [names[j] for j in rej1], "Rvar", out["rvar_S1"])
print("SF", [names[j] for j in SF], "Rvar", out["rvar_SF"])
print("median efit S1", np.median(e1_fit), "SF", np.median(e2_fit), "erel SF", np.median(e2_rel))
print("chi test", chi)
