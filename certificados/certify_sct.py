#!/usr/bin/env python3
"""Certificado de cos Δ para SCT Bandura (modelo lineal ẋ = A(θ)x + B(θ)u, 3 condiciones)."""
import sys, math, json, importlib.util
from pathlib import Path
import numpy as np
SCT = Path(sys.argv[1])  # ruta a sct_fim_greedy.py (con VIF_MAX2 corregido)
spec = importlib.util.spec_from_file_location("sct", SCT)
sct = importlib.util.module_from_spec(spec); sys.modules["sct"] = sct; spec.loader.exec_module(sct)
th0 = sct.THETA_NOM.copy(); names = sct.PARAM_NAMES; p = len(th0)
C = 0.9; k = math.sqrt(1 - C ** 2)
T = sct.T_END; N = len(sct.T_GRID)

def F(th): return sct.simulate_all(th)
def Df(X, th):
    """X: estados de las 3 condiciones (18,), devuelve (A_big, B_big)."""
    def f(Xv, t_):
        A, B = sct.build_AB(t_)
        return np.concatenate([A @ Xv[6*c:6*c+6] + B @ sct.INPUTS[c][0] for c in range(3)])
    A, _ = sct.build_AB(th)
    Abig = np.kron(np.eye(3), A)
    Bbig = np.zeros((18, p))
    for j in range(p):
        h = 1e-6 * abs(th[j]); tp = th.copy(); tm = th.copy(); tp[j] += h; tm[j] -= h
        Bbig[:, j] = (f(X, tp) - f(X, tm)) / (2 * h)
    return Abig, Bbig
spec_ = lambda M: float(np.linalg.norm(M, 2))

y0 = F(th0)
J = np.zeros((y0.size, p))
for j in range(p):
    h = 1e-5 * abs(th0[j]); tp = th0.copy(); tm = th0.copy(); tp[j] += h; tm[j] -= h
    J[:, j] = (F(tp) - F(tm)) / (2 * h)
Jrel = J * th0
out = {}
for label, S in {"4_params_script": ["beta43", "beta54", "beta34", "beta14"],
                 "5_params_+gamma33": ["beta43", "beta54", "beta34", "beta14", "gamma33"]}.items():
    idx = [names.index(s) for s in S]; rem = np.ones(p, bool); rem[idx] = False
    E = (J ** 2).sum(0); Er = (Jrel ** 2).sum(0)
    R, Rr = E[rem].sum(), Er[rem].sum()
    rng = np.random.default_rng(42)
    scen = [np.maximum(th0 * (1 + 0.05 * rng.uniform(-1, 1, p)), 1e-12) for _ in range(sct.N_ESCEN)]
    # puntos para M1, M2, μ: trayectoria nominal y 5 perturbadas
    def states(th): return F(th).reshape(3, N, 6).transpose(1, 0, 2).reshape(N, 18)
    X0 = states(th0); D0 = [Df(X0[i], th0) for i in range(N)]
    M1 = M1r = beta = 0.0; mu = -math.inf; M2 = M2r = 0.0
    def upd(A, B):
        global_ = None
        return B * th0
    for i in range(N):
        A, B = D0[i]; Br = B * th0
        M1 = max(M1, spec_(A), spec_(B)); M1r = max(M1r, spec_(A), spec_(Br))
        mu = max(mu, float(np.max(np.linalg.eigvalsh((A + A.T) / 2)))); beta = max(beta, spec_(Br))
    for i in range(N - 1):
        (A1, B1), (A2, B2) = D0[i], D0[i + 1]
        dz = np.linalg.norm(X0[i] - X0[i + 1])
        if dz > 0:
            M2 = max(M2, spec_(B1 - B2) / dz); M2r = max(M2r, spec_((B1 - B2) * th0) / dz)
    for th in scen[:5]:
        X = states(th); du = np.linalg.norm(th / th0 - 1); dth = np.linalg.norm(th - th0)
        for i in range(N):
            A, B = Df(X[i], th); Br = B * th0; A0, B0 = D0[i]
            M1 = max(M1, spec_(A), spec_(B)); M1r = max(M1r, spec_(A), spec_(Br))
            mu = max(mu, float(np.max(np.linalg.eigvalsh((A + A.T) / 2)))); beta = max(beta, spec_(Br))
            dx = np.linalg.norm(X[i] - X0[i])
            M2 = max(M2, max(spec_(A - A0), spec_(B - B0)) / max(dx, dth))
            M2r = max(M2r, max(spec_(A - A0), spec_(Br - B0 * th0)) / max(dx, du))
    def logLc_M1(M1, M2):
        x = M1 * T
        return 0.5 * math.log(N) + math.log(M2) + 2 * x + x + math.log1p(-math.exp(-x)) - math.log(M1)
    def logLc_mu(mu, beta, M2):
        x = mu * T
        logPhi = (x + math.log1p(-math.exp(-x)) - math.log(mu)) if x > 1e-8 else \
                 (math.log(T) if abs(x) <= 1e-8 else math.log(-math.expm1(x)) - math.log(-mu))
        bp1 = beta * math.exp(logPhi) + 1
        return 0.5 * math.log(N) + math.log(M2) + 2 * math.log(bp1) + logPhi
    res = {"S": S, "Rvar_%": 100 * (1 - R / E.sum()), "Rvar_rel_%": 100 * (1 - Rr / Er.sum()),
           "M1_inf": M1, "mu_inf": mu, "beta_rel_inf": beta, "M2_inf": M2, "M2_rel_inf": M2r}
    for vname, logLc, JJ, RR, rel in [("A_abs_M1", logLc_M1(M1, M2), J, R, False),
                                     ("B_rel_M1", logLc_M1(M1r, M2r), Jrel, Rr, True),
                                     ("C_rel_mu", logLc_mu(mu, beta, M2r), Jrel, Rr, True)]:
        Lc = math.exp(logLc) if logLc < 700 else math.inf
        lin = cert = 0; pm = []
        for th in scen:
            h = (th / th0 - 1) if rel else (th - th0); hc = np.where(rem, h, 0)
            a = math.sqrt(RR) * np.linalg.norm(hc); b = np.linalg.norm(JJ @ h); hn2 = h @ h
            lin += a <= k * b
            A_ = b - Lc * hn2; eB = a + 2 * Lc * hn2
            cert += (A_ > 0 and eB ** 2 <= (1 - C ** 2) * A_ ** 2)
            pm.append(min(max(0.0, (k * b - a) / ((2 + k) * Lc * hn2)), 1.0) * 0.05 if Lc < math.inf else 0.0)
        res[f"log10_Lc_{vname}"] = logLc / math.log(10)
        res[f"{vname}_lineal_5%"] = f"{lin}/{len(scen)}"; res[f"{vname}_cert_5%"] = f"{cert}/{len(scen)}"
        res[f"{vname}_pert_max_%"] = 100 * float(np.median(pm))
    cos = []
    for th in scen:
        ths = th0.copy(); ths[idx] = th[idx]
        df_, ds_ = F(th) - y0, F(ths) - y0
        cos.append(float(df_ @ ds_ / (np.linalg.norm(df_) * np.linalg.norm(ds_))))
    res["cos5_mediana"] = float(np.median(cos))
    out[label] = res
print(json.dumps(out, indent=1, default=str))
Path(__file__).resolve().parent.joinpath("resultados", "SCT_Bandura.json").write_text(json.dumps(out, indent=1, default=str))
