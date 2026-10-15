#!/usr/bin/env python3
"""
SCT model with real data (31 days of one participant) and the 22-parameter Bandura model
(sct_model.py), analysed with the method of the paper (Supplementary Note "The social cognitive
theory model", Supplementary Table S16, Supplementary Fig. S3).

  1. theta0: differential evolution with the settings of the original estimation (best1bin,
     popsize 4, 60 generations, Latin hypercube initialisation, no polishing) and the 100 seeds
     2026-2125; theta0 = the solution of seed 2026 (R^2 = 0.8806). The 100 solutions measure the
     spread of the parameters among equally good fits (non-identifiability).
  2. sigma = standard deviation of the residuals at theta0; outputs y/sigma.
  3. Method of the paper: relative J, stage 1/2, admissibility with e_fit <= 0.436 over 15
     scenarios at +-5 %, backward elimination, robustness patterns at +-1 ... 50 %. The beta can be
     negative: the re-estimation uses theta_j = sign * exp(v). (In this model, kappa and VIF are
     computed on unit-norm columns of J.)
  4. Validation: reduced (S) and full (22 parameters) models re-fitted to days 1-24 from theta0
     within the bounds; chi2/n and R^2 on days 25-31. The full model is also re-fitted with the
     differential evolution of step 1 restricted to days 1-24.

Requires the participant data (see sct_model.py). Usage: python sct_analysis.py
Output: results/sct/sct_analysis.json
"""
import json

import numpy as np
from scipy.optimize import least_squares, differential_evolution

import config as CFG
import sct_model as M

OUT = CFG.RESULTS / "sct"; OUT.mkdir(parents=True, exist_ok=True)
P = len(M.NAMES); N = M.N; Y = M.Y
LO = np.array([b[0] for b in M.BOUNDS]); HI = np.array([b[1] for b in M.BOUNDS])
DELTA, ETA, TAU_R, TAU_K, EMAX, KMIN = 0.01, 0.1, 0.89, 10.0, float(np.sqrt(1 - 0.81)), 2
N_SCEN, SEED, LEVELS = 15, 42, [0.01, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50]
N_TRAIN = 24

# ------------------------------------------------------------- 1. theta0 by differential evolution
SEEDS = list(range(2026, 2126))
sols, r2s = [], []
for seed in SEEDS:
    r = differential_evolution(M.cost, M.BOUNDS, strategy="best1bin", popsize=4, maxiter=60, seed=seed,
                               polish=False, init="latinhypercube")
    sols.append(r.x); r2s.append(M.r2(M.sim(r.x)))
sols, r2s = np.array(sols), np.array(r2s)
th0 = sols[0]
y0 = M.sim(th0)
r2_0 = M.r2(y0)
sigma = float(np.std(Y - y0, ddof=1))
good = sols[r2s >= 0.87]
spread = {n: {"min": float(good[:, j].min()), "max": float(good[:, j].max()),
              "cambia_signo": bool(good[:, j].min() < 0 < good[:, j].max())} for j, n in enumerate(M.NAMES)}
print(f"theta0 (seed 2026): R2 = {r2_0:.4f}; 100 seeds: R2 {r2s.min():.4f}-{r2s.max():.4f}, "
      f"{len(good)} with R2 >= 0.87", flush=True)

F = lambda th: M.sim(th) / sigma  # noqa: E731
f0 = F(th0)
J = np.zeros((N, P))
for j in range(P):
    if th0[j] == 0: continue
    tp, tm = th0.copy(), th0.copy(); tp[j] *= 1 + DELTA; tm[j] *= 1 - DELTA
    J[:, j] = (F(tp) - F(tm)) / (2 * DELTA)
E = (J ** 2).sum(0); act = [j for j in range(P) if E[j] > 1e-20 * E.max()]
rvar = lambda S: float(E[S].sum() / E.sum())  # noqa: E731


def ncol(idx):
    Z = J[:, idx]; n = np.linalg.norm(Z, axis=0); return Z / np.where(n > 0, n, 1)


def kappa(idx):
    if len(idx) < 2: return 1.0
    s = np.linalg.svd(ncol(idx), compute_uv=False); return float("inf") if s[-1] < 1e-12 else float(s[0] / s[-1])


def vif(idx):
    if len(idx) < 2: return 1.0
    try: return float(np.max(np.diag(np.linalg.inv(ncol(idx).T @ ncol(idx)))))
    except np.linalg.LinAlgError: return float("inf")


def scenarios(level):
    r = np.random.default_rng(SEED)
    return [th0 * (1 + level * r.uniform(-1, 1, P)) for _ in range(N_SCEN)]


def evaluate(S, level):
    cs, es, fs = [], [], []
    sg = np.sign(th0[S]); lo_, hi_ = np.log(np.abs(th0[S]) / 10), np.log(np.abs(th0[S]) * 10)
    for th in scenarios(level):
        yf = F(th); dlt = yf - f0; nf = np.linalg.norm(dlt)
        if nf < 1e-10: continue
        ts = th0.copy(); ts[S] = th[S]; ds = F(ts) - f0; ns = np.linalg.norm(ds)
        cs.append(float(dlt @ ds / (nf * ns)) if ns > 0 else 0.0)
        er = float(np.linalg.norm(dlt - ds) / nf); es.append(er)

        def res(v):
            t = th0.copy(); t[S] = sg * np.exp(v); return (F(t) - yf) / nf
        best = er
        for v0 in (np.clip(np.log(np.abs(th[S])), lo_, hi_), np.log(np.abs(th0[S]))):
            try:
                rr = least_squares(res, v0, bounds=(lo_, hi_), method="trf", max_nfev=100 * (len(S) + 1), diff_step=1e-3)
                best = min(best, float(np.linalg.norm(rr.fun)))
            except Exception:
                pass
        fs.append(best)
    med = lambda v: float(np.median(v)) if v else float("nan")  # noqa: E731
    return med(cs), med(es), med(fs), len(fs)


memo = {}
def admissible(S):
    k = tuple(sorted(S))
    if k not in memo: memo[k] = evaluate(list(k), 0.05)
    return len(S) >= KMIN and memo[k][2] <= EMAX


def greedy(order, stop):
    S, rejected = [], []
    for j in order:
        if kappa(S + [j]) <= TAU_K and vif(S + [j]) <= TAU_K:
            S.append(j)
            if stop(S): return S, True, rejected
        else:
            Z = ncol(S + [j]); c = np.abs(Z[:, :-1].T @ Z[:, -1]) if S else np.array([0.0])
            rejected.append({"parametro": M.NAMES[j], "mas_colineal_con": M.NAMES[S[int(np.argmax(c))]] if S else None, "cos": float(c.max())})
    return S, False, rejected


C = ncol(act).T @ ncol(act)
pairs = sorted([(abs(C[a, b]), M.NAMES[act[a]], M.NAMES[act[b]]) for a in range(len(act)) for b in range(a + 1, len(act)) if abs(C[a, b]) >= 0.95], reverse=True)
order1 = sorted(act, key=lambda j: -E[j])
S1, ok1, rej1 = greedy(order1, lambda S: rvar(S) >= TAU_R and len(S) >= KMIN)
if ok1 and admissible(S1):
    S, stage, rej2 = S1, "Stage 1", []
else:
    s = np.zeros(P)
    for j in act:
        tp = th0.copy(); tp[j] *= 1 + ETA; s[j] = np.linalg.norm(F(tp) - f0)
    S, ok2, rej2 = greedy(sorted(act, key=lambda j: -s[j]), admissible)
    stage = "Stage 2" if ok2 else "no admisible"
before = list(S)
if stage != "no admisible":
    changed = True
    while changed:
        changed = False
        for j in sorted(S, key=lambda j: E[j]):
            T = [x for x in S if x != j]
            if admissible(T): S = T; changed = True; break
c5, e5, f5, n5 = evaluate(S, 0.05)
lev = {}
for nv in LEVELS:
    c, e, f, n = evaluate(S, nv); lev[str(int(round(100 * nv)))] = {"cos_med": c, "erel_med": e, "eaj_med": f, "n": n}
ok = [lev[k]["eaj_med"] <= EMAX for k in lev]
pat = "A" if all(ok) else ("C" if any(ok[ok.index(False):]) else ("B" if LEVELS[ok.index(False)] >= 0.2 else "D"))
print(f"S = {[M.NAMES[j] for j in S]} ({stage}); e_fit +-5 % = {100 * f5:.1f} %; pattern {pat}", flush=True)

# ------------------------------------------------------------- 4. external validation (days 1-24 -> 25-31)
tr, te = np.arange(N_TRAIN), np.arange(N_TRAIN, N)


def refit(free):
    free = list(free)
    def res(v):
        t = th0.copy(); t[free] = v
        if not M.stable(t): return np.full(len(tr), 1e3)
        return (M.sim(t)[tr] - Y[tr]) / sigma
    rr = least_squares(res, np.clip(th0[free], LO[free], HI[free]), bounds=(LO[free], HI[free] + 1e-12),
                       method="trf", max_nfev=200 * (len(free) + 1), x_scale="jac")
    t = th0.copy(); t[free] = rr.x; return t


chi = lambda th, idx: float(np.mean(((M.sim(th)[idx] - Y[idx]) / sigma) ** 2))  # noqa: E731
th_r, th_f = refit(S), refit(range(P))
# full model also re-fitted with the differential evolution of step 1 on days 1-24 (same seed)
def cost_tr(th):
    if not M.stable(th): return 1e6
    y = M.sim(th); return float(np.mean((Y[tr] - y[tr]) ** 2)) if np.max(np.abs(y)) <= 10 else 1e6
th_de = differential_evolution(cost_tr, M.BOUNDS, strategy="best1bin", popsize=4, maxiter=60, seed=SEEDS[0],
                               polish=False, init="latinhypercube").x
val = {"chi2_test_red": chi(th_r, te), "chi2_test_full": chi(th_f, te), "chi2_test_theta0": chi(th0, te),
       "chi2_train_red": chi(th_r, tr), "chi2_train_full": chi(th_f, tr),
       "R2_test_red": M.r2(M.sim(th_r), te), "R2_test_full": M.r2(M.sim(th_f), te),
       "estable_red": M.stable(th_r), "estable_full": M.stable(th_f),
       "chi2_test_full_DE": chi(th_de, te), "R2_test_full_DE": M.r2(M.sim(th_de), te), "chi2_train_full_DE": chi(th_de, tr)}
print("validation chi2/n days 25-31: reduced %.2f | full LS %.2f | full DE %.2f | theta0 %.2f" %
      (val["chi2_test_red"], val["chi2_test_full"], val["chi2_test_full_DE"], val["chi2_test_theta0"]), flush=True)

res = {"modelo": "SCT 22 parámetros (Bandura, pipeline z-score)", "p": P, "n_dias": N,
       "theta0": dict(zip(M.NAMES, th0.tolist())), "R2_theta0": r2_0,
       "DE_100": {"semillas": SEEDS, "R2": r2s.tolist(), "n_R2_ge_0.87": int(len(good)),
                  "dispersion_R2_ge_0.87": spread, "theta": [dict(zip(M.NAMES, s_.tolist())) for s_ in sols]},
       "sigma": sigma, "parametros_sin_efecto_en_x4": [M.NAMES[j] for j in range(P) if j not in act],
       "kappa_activos": kappa(act), "VIF_activos": vif(act),
       "pares_cos_ge_0.95": [{"a": a, "b": b, "cos": float(c)} for c, a, b in pairs],
       "S1": [M.NAMES[j] for j in S1], "Rvar_S1_%": 100 * rvar(S1), "etapa": stage,
       "S_antes_poda": [M.NAMES[j] for j in before], "S": [M.NAMES[j] for j in S],
       "podados": [M.NAMES[j] for j in before if j not in S], "kappa": kappa(S), "VIF": vif(S),
       "cos_med": c5, "erel_med": e5, "eajuste_med": f5, "n_escenarios": n5, "admisible": stage != "no admisible",
       "descartes": rej1 + rej2, "niveles": lev, "patron": pat, "validacion": val}
(OUT / "sct_analysis.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
