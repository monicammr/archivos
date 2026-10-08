#!/usr/bin/env python3
"""
Evaluación del certificado formal de cos Δ (Lean: CertifiedFiniteODE.certified_cos_ode)
para los 24 sistemas admisibles del artículo.

Para cada sistema:
  1. θ₀ = nominalValue de PEtab (parámetros con estimate=1), mismo pre-proceso que los scripts
     de robustez (04_robustez/robustez_sweep_*.py).
  2. Trayectoria muestreada F(θ) = simulación con 60 puntos en [1e-6, T] (igual que el artículo).
  3. J = ∂F/∂θ en θ₀ por diferencias centradas.
  4. Escenarios: semilla 42, 15 escenarios por nivel, θ = θ₀ (1 + nivel·d), d ~ U(-1,1)
     (misma secuencia aleatoria que los scripts de robustez).
  5. Cotas INFERIORES (optimistas) de M₁ = sup‖Df‖ y M₂ = Lip(Df), evaluando Df por diferencias
     finitas del campo f(x,θ) en puntos de las trayectorias nominal y perturbadas (±5 %).
  6. Lc_opt = √N · M₂ · e² (e − 1) / M₁, e = exp(M₁ T)  (≤ Lc verdadero, porque Lc es creciente
     en M₁ y M₂).
  7. Condición del certificado con c = 0.9:
        (√R ‖h_{Sᶜ}‖ + 2 Lc ‖h‖²)² ≤ (1 − c²)(‖J h‖ − Lc ‖h‖²)²,  ‖J h‖ > Lc ‖h‖².
     Variante con el término lineal exacto ‖J h_{Sᶜ}‖ en lugar de √R ‖h_{Sᶜ}‖
     (Lean: ExactLinearCertificate.finite_cos_certificate_exact): columnas *_certexacto_*.
  8. Certificado LOCAL sin Lc (Lean: ExactLinearCertificate.eventually_cos_delta_gt): si el
     coseno lineal cos(J h, J h_S) > c, entonces cos Δ(s h) > c para s > 0 suficientemente
     pequeño. Columnas local_cos_lin>c_* y cos_lin_mediana_*.

Interpretación: como Lc_opt ≤ Lc, si la condición FALLA con Lc_opt, falla con el Lc verdadero
(conclusión negativa robusta). Si PASA con Lc_opt, el escenario es candidato a certificación,
pero falta acotar M₁, M₂ rigurosamente (aritmética de intervalos sobre la región K).
"""
import sys, json, math, time, warnings
from pathlib import Path
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
import roadrunner as rr
rr.Config.setValue(rr.Config.ROADRUNNER_DISABLE_WARNINGS, True)

BENCH = Path(__file__).resolve().parent / "bench" / "problems"
OUT = Path(__file__).resolve().parent / "resultados"
OUT.mkdir(exist_ok=True)

import os as _os
N_PTS, N_ESCEN, SEED, C = 60, 15, 42, 0.9
# malla temporal (análisis de sensibilidad): CS_NPTS puntos y horizonte T × CS_TFACTOR
N_PTS = int(_os.environ.get("CS_NPTS", N_PTS))
T_FACTOR = float(_os.environ.get("CS_TFACTOR", 1.0))
NIV_FIM = [0.01, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50]
NIV_SCAN = [0.01, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.80, 0.90, 1.00, 1.10]
T_END_OVERRIDE = {"Sneyd_PNAS2002": 5.0, "Elowitz_Nature2000": 5.0,
                  "Borghans_BiophysChem1997": 5.0, "Crauste_CellSystems2017": 1.0,
                  "Zhao_QuantBiol2020": 1.0, "SalazarCavazos_MBoC2020": 0.01}

# Subconjuntos tomados de 04_robustez/robustez_sweep_gram.py y robustez_sweep_scan.py
SYSTEMS = [
    ("Blasi_CellSystems2016", ["a_k8", "a_basal"], 50.0, "FIM"),
    ("Chen_MSB2009", ["k35", "k103"], 50.0, "FIM"),
    ("Fiedler_BMCSystBiol2016", ["K_1", "tau2"], 50.0, "FIM"),
    ("Bachmann_MSB2011", ["SHP1ActEpoR", "STAT5Imp"], 50.0, "FIM"),
    ("Elowitz_Nature2000", ["tps_active", "tau_prot"], 5.0, "FIM"),
    ("Crauste_CellSystems2017", ["mu_N", "rho_E"], 1.0, "FIM"),
    ("Sneyd_PNAS2002", ["k1", "k2"], 5.0, "FIM"),
    ("Zheng_PNAS2012", ["k13_12", "k12_13", "k13_03", "k12_22"], 50.0, "FIM"),
    ("Raimundez_PCB2020", ["d_ksyn_EGFR__fm_2_hm"], 50.0, "FIM"),
    ("SalazarCavazos_MBoC2020", ["ratio_kpkd_Y1068__FREE", "kdephosY1068__FREE",
                                 "kdephosYN__FREE", "ratio_kpkd_YN__FREE"], 0.01, "FIM"),
    ("Okuonghae_ChaosSolitonsFractals2020", ["transmission_rate_effective", "gamma_0",
                                             "gamma_a", "sigma", "nu", "d_0"], 50.0, "FIM"),
    ("Borghans_BiophysChem1997", ["Kz", "Vm2", "Vm3", "beta_par", "v1", "v0", "K_par"], 5.0, "FIM"),
    ("Armistead_CellDeathDis2024", ["alpha_cer", "k_d"], 50.0, "FIM"),
    ("Boehm_JProteomeRes2014", ["k_exp_homo", "k_imp_hetero", "k_phos"], 50.0, "SCAN"),
    ("Raia_CancerResearch2011", ["Rec_recycle"], 50.0, "SCAN"),
    ("Weber_BMC2015", ["s31", "a31", "p31", "p22"], 50.0, "SCAN"),
    ("Zhao_QuantBiol2020", ["R_Stage_I_Wuhan"], 1.0, "SCAN"),
    ("Giordano_Nature2020", ["alpha_4", "alpha_28", "zeta_22", "rho_38", "rho_22", "tau"], 50.0, "SCAN"),
    ("Lang_PLOSComputBiol2024", ["kCdc25_1", "kPhEnsa", "kPhRbD", "kDeCb2", "kDeCDKN1A_2",
                                 "kPhCDKN1AByCe"], 50.0, "SCAN"),
    ("Smith_BMCSystBiol2013", ["k30f", "kminus7b"], 50.0, "SCAN"),
    ("Rahman_MBS2016", ["infected_moderate_transmission_rate", "infected_moderate_worsen_rate",
                        "treated_moderate_improve_rate"], 50.0, "SCAN"),
    ("Brannmark_JBC2010", ["k3", "k1aBasic", "k1c", "k1d", "k21", "k22"], 50.0, "SCAN"),
    ("Froehlich_CellSystems2018", ["r1628_k0", "r1683_k0", "r9421_k0", "r28447_k0", "r1881_k0",
                                   "r1622_k0", "r416_k0", "r23812_k0", "r20_k0", "r1669_k0",
                                   "r22_k0", "r1879_k0", "r2778_k0", "r419_k0", "r17298_k0",
                                   "r17296_k0", "r1671_k0", "r541_k0", "r2349_kE1", "r1616_k0",
                                   "r8344_k0", "r470_k0"], 50.0, "FIM"),
]


def load_theta(folder):
    df = pd.read_csv(folder / "parameters.tsv", sep="\t")
    if "estimate" in df.columns:
        df = df[df["estimate"] == 1]
    names = df["parameterId"].astype(str).tolist()
    t = df["nominalValue"].astype(float).to_numpy()
    t = np.where(np.isfinite(t), t, 1e-6)
    t = np.where(t == 0, 1e-12, t).astype(float)
    return names, t


def load_model(sbml):
    m = rr.RoadRunner(str(sbml))
    ig = m.getIntegrator()
    for k, v in [("relative_tolerance", 1e-7), ("absolute_tolerance", 1e-10),
                 ("maximum_num_steps", 200000), ("stiff", True)]:
        try:
            ig.setValue(k, v)
        except Exception:
            pass
    return m


class Sys:
    def __init__(self, name, t_end):
        folder = BENCH / name / "v1"
        self.names, self.theta0 = load_theta(folder)
        self.m = load_model(folder / "model.xml")
        self.t_end = t_end * T_FACTOR
        gp = set(self.m.model.getGlobalParameterIds())
        self.in_model = np.array([n in gp for n in self.names])
        self.species = list(self.m.model.getFloatingSpeciesIds())
        # especies definidas por reglas de asignación (no son estados del EDO)
        self.ruled = set(self.m.getAssignmentRuleIds()) & set(self.species)
        self.state_idx = [i for i, sid in enumerate(self.species) if sid not in self.ruled]

    def set_params(self, theta):
        for n, v, ok in zip(self.names, theta, self.in_model):
            if ok:
                self.m[n] = float(v)

    def sim(self, theta):
        """Igual que los scripts del artículo: resetAll, fijar parámetros, simular."""
        try:
            self.m.resetAll()
            self.set_params(theta)
            arr = np.asarray(self.m.simulate(1e-6, self.t_end, N_PTS), dtype=float)
            y = arr[:, 1:]
            return y if np.all(np.isfinite(y)) else None
        except Exception:
            return None

    def rhs(self, x, theta, t, set_params=True):
        """Campo f(x, θ) (tasas de concentración) en el estado x."""
        em = self.m.model
        if set_params:
            self.set_params(theta)
        em.setTime(float(t))
        if self.ruled:
            for i, sid in enumerate(self.species):
                if sid not in self.ruled:
                    self.m["[" + sid + "]"] = float(x[i])
        else:
            em.setFloatingSpeciesConcentrations(np.asarray(x, dtype=float))
        return np.asarray(em.getFloatingSpeciesConcentrationRates(), dtype=float)

    def Df(self, x, theta, t, rel=1e-6):
        """A = ∂f/∂x, B = ∂f/∂θ por diferencias centradas (asignando θ una sola vez)."""
        n, p = len(self.state_idx), len(theta)
        A = np.zeros((n, n)); B = np.zeros((n, p))
        self.set_params(theta)
        for c, i in enumerate(self.state_idx):
            h = rel * max(abs(x[i]), 1e-8)
            xp = x.copy(); xm = x.copy(); xp[i] += h; xm[i] -= h
            A[:, c] = (self.rhs(xp, theta, t, False) - self.rhs(xm, theta, t, False)) / (2 * h)
        for j in np.nonzero(self.in_model)[0]:
            name = self.names[j]
            h = rel * max(abs(theta[j]), 1e-12)
            self.m[name] = float(theta[j] + h); fp = self.rhs(x, theta, t, False)
            self.m[name] = float(theta[j] - h); fm = self.rhs(x, theta, t, False)
            self.m[name] = float(theta[j])
            B[:, j] = (fp - fm) / (2 * h)
        return A, B


def spec(M):
    return float(np.linalg.norm(M, 2)) if M.size else 0.0


def analyze(name, sel, t_def, group, max_points=None):
    t0 = time.time()
    t_end = T_END_OVERRIDE.get(name, t_def)
    S = Sys(name, t_end)
    sel_idx = [S.names.index(p) for p in sel if p in S.names]
    res = {"sistema": name, "etapa": group, "p": len(S.names), "n_estados": len(S.species),
           "sel_encontrados": f"{len(sel_idx)}/{len(sel)}", "T": t_end,
           "eventos": int(S.m.model.getNumEvents()),
           "reglas_tasa": int(S.m.model.getNumRateRules())}
    y0 = S.sim(S.theta0)
    if y0 is None:
        res["error"] = "simulación nominal falló"; return res
    # --- J por diferencias centradas
    p = len(S.names)
    J = np.zeros((y0.size, p))
    for j in np.nonzero(S.in_model)[0]:
        h = 1e-4 * abs(S.theta0[j])
        tp = S.theta0.copy(); tm = S.theta0.copy(); tp[j] += h; tm[j] -= h
        yp, ym = S.sim(tp), S.sim(tm)
        if yp is not None and ym is not None:
            J[:, j] = (yp - ym).ravel() / (2 * h)
    colE = np.sum(J ** 2, axis=0)
    mask_rem = np.ones(p, bool); mask_rem[sel_idx] = False
    R = float(colE[mask_rem].sum()); tot = float(colE.sum())
    res["Rvar_%"] = 100 * (1 - R / tot) if tot > 0 else float("nan")
    # --- escenarios (misma secuencia aleatoria)
    niveles = NIV_FIM if group == "FIM" else NIV_SCAN
    rng = np.random.default_rng(SEED)
    scen = []
    for nivel in niveles:
        for _ in range(N_ESCEN):
            d = rng.uniform(-1, 1, size=p)
            th_f = np.maximum(S.theta0 * (1 + nivel * d), 1e-12)
            scen.append((nivel, th_f))
    # --- J relativo (coordenadas u, θ = θ₀(1+u)): J_rel = J · diag(θ₀)
    Jrel = J * S.theta0.reshape(1, -1)
    colEr = np.sum(Jrel ** 2, axis=0)
    Rr = float(colEr[mask_rem].sum()); totr = float(colEr.sum())
    res["Rvar_rel_%"] = 100 * (1 - Rr / totr) if totr > 0 else float("nan")
    # --- trayectorias para estimar M1, M2, μ (nominal + perturbadas al 5 %)
    tgrid = np.linspace(1e-6, t_end, N_PTS)
    pert = [th for (nv, th) in scen if nv == 0.05][:5]
    pert_traj = [(th, S.sim(th)) for th in pert]
    if max_points is None and len(S.species) + p > 150:
        max_points = 12
    stride = 1 if max_points is None else max(1, N_PTS // max_points)
    ks = list(range(0, N_PTS, stride))
    st = {"M1": 0.0, "M1r": 0.0, "mu": -math.inf, "beta": 0.0, "M2": 0.0, "M2r": 0.0}
    t_dep = 0.0
    Dnom = {}
    def upd(A, B):
        Br = B * S.theta0.reshape(1, -1)
        st["M1"] = max(st["M1"], spec(A), spec(B))
        st["M1r"] = max(st["M1r"], spec(A), spec(Br))
        st["mu"] = max(st["mu"], float(np.max(np.linalg.eigvalsh((A + A.T) / 2))))
        st["beta"] = max(st["beta"], spec(Br))
        return Br
    for k in ks:
        x, th, t = y0[k], S.theta0, tgrid[k]
        A, B = S.Df(x.copy(), th.copy(), t)
        Dnom[k] = (A, B, upd(A, B))
        r1 = S.rhs(x.copy(), th, t); r2 = S.rhs(x.copy(), th, t + 0.37 * t_end + 1e-3)
        t_dep = max(t_dep, float(np.linalg.norm(r1 - r2) / (np.linalg.norm(r1) + 1e-30)))
    def upd2(A, B, Br, A0, B0, Br0, dx, dth, du):
        dz = max(dx, dth); dzr = max(dx, du)
        if dz > 0:
            st["M2"] = max(st["M2"], max(spec(A - A0), spec(B - B0)) / dz)
        if dzr > 0:
            st["M2r"] = max(st["M2r"], max(spec(A - A0), spec(Br - Br0)) / dzr)
    for a, b in zip(ks[:-1], ks[1:]):
        (A1, B1, Br1), (A2, B2, Br2) = Dnom[a], Dnom[b]
        upd2(A1, B1, Br1, A2, B2, Br2, float(np.linalg.norm(y0[a] - y0[b])), 0.0, 0.0)
    for th, yt in pert_traj:
        if yt is None:
            continue
        du = float(np.linalg.norm(th / S.theta0 - 1)); dth = float(np.linalg.norm(th - S.theta0))
        for k in ks:
            A, B = S.Df(yt[k].copy(), th.copy(), tgrid[k])
            Br = upd(A, B)
            A0, B0, Br0 = Dnom[k]
            upd2(A, B, Br, A0, B0, Br0, float(np.linalg.norm(yt[k] - y0[k])), dth, du)
    res.update({"M1_inf": st["M1"], "M1_rel_inf": st["M1r"], "mu_inf": st["mu"],
                "beta_rel_inf": st["beta"], "M2_inf": st["M2"], "M2_rel_inf": st["M2r"],
                "dep_tiempo": t_dep})
    N = N_PTS
    def log_lc_M1(M1, M2):
        if M1 <= 0 or M2 <= 0:
            return -math.inf
        x = M1 * t_end
        return 0.5 * math.log(N) + math.log(M2) + 2 * x + (x + math.log1p(-math.exp(-x))) - math.log(M1)
    def log_lc_mu(mu, beta, M2):
        # Variante con norma logarítmica (requiere extender el teorema en Lean):
        # Φ = (e^{μT} − 1)/μ,  Lc = √N · M2 · (βΦ + 1)² · Φ
        if M2 <= 0:
            return -math.inf
        x = mu * t_end
        if abs(x) < 1e-8:
            logPhi = math.log(t_end)
        elif x > 0:
            logPhi = x + math.log1p(-math.exp(-x)) - math.log(mu)
        else:
            logPhi = math.log(-math.expm1(x)) - math.log(-mu)
        lb = math.log(beta) + logPhi if beta > 0 else -math.inf
        log_bp1 = max(lb, 0.0) + math.log1p(math.exp(-abs(lb))) if lb > -math.inf else 0.0
        return 0.5 * math.log(N) + math.log(M2) + 2 * log_bp1 + logPhi
    variants = {
        "A_abs_M1": (log_lc_M1(st["M1"], st["M2"]), J, R, False),
        "B_rel_M1": (log_lc_M1(st["M1r"], st["M2r"]), Jrel, Rr, True),
        "C_rel_mu": (log_lc_mu(st["mu"], st["beta"], st["M2r"]), Jrel, Rr, True),
    }
    k = math.sqrt(1 - C ** 2)
    for vname, (logLc, JJ, RR, rel) in variants.items():
        res[f"log10_Lc_{vname}"] = logLc / math.log(10)
        Lc = math.exp(logLc) if logLc < 700 else math.inf
        rows = []
        for nivel, th_f in scen:
            h = (th_f / S.theta0 - 1) if rel else (th_f - S.theta0)
            hc = np.where(mask_rem, h, 0.0)
            a = math.sqrt(RR) * float(np.linalg.norm(hc))
            b = float(np.linalg.norm(JJ @ h)); hn2 = float(np.dot(h, h))
            lin_ok = a <= k * b
            # Término lineal exacto ‖J(h − h_S)‖ = ‖J h_{Sᶜ}‖ (Lean: finite_cos_certificate_exact)
            Jh = JJ @ h; JhS = JJ @ (h - hc)
            ae = float(np.linalg.norm(JJ @ hc))
            linex_ok = ae <= k * b
            # Coseno lineal cos(J h, J h_S) (Lean: tendsto_cos_delta / eventually_cos_delta_gt)
            nJh, nJhS = float(np.linalg.norm(Jh)), float(np.linalg.norm(JhS))
            cos_lin = float(Jh @ JhS / (nJh * nJhS)) if nJh > 0 and nJhS > 0 else float("nan")
            local_ok = bool(cos_lin > C)
            if math.isinf(Lc):
                cert, certex, tmax = False, False, 0.0
            else:
                A_ = b - Lc * hn2; eB = a + 2 * Lc * hn2; eBx = ae + 2 * Lc * hn2
                cert = A_ > 0 and eB ** 2 <= (1 - C ** 2) * A_ ** 2
                certex = A_ > 0 and eBx ** 2 <= (1 - C ** 2) * A_ ** 2
                tmax = max(0.0, (k * b - a) / ((2 + k) * Lc * hn2)) if Lc * hn2 > 0 else 1.0
            rows.append({"nivel": nivel, "lin_ok": lin_ok, "cert": cert,
                         "linex_ok": linex_ok, "certex": certex, "local_ok": local_ok,
                         "cos_lin": cos_lin, "pmax": min(tmax, 1.0) * nivel})
        df = pd.DataFrame(rows)
        for nv in (0.01, 0.05):
            sub = df[df.nivel == nv]
            res[f"{vname}_lineal_{int(nv*100)}%"] = f"{int(sub.lin_ok.sum())}/{len(sub)}"
            res[f"{vname}_cert_{int(nv*100)}%"] = f"{int(sub.cert.sum())}/{len(sub)}"
            res[f"{vname}_linexacto_{int(nv*100)}%"] = f"{int(sub.linex_ok.sum())}/{len(sub)}"
            res[f"{vname}_certexacto_{int(nv*100)}%"] = f"{int(sub.certex.sum())}/{len(sub)}"
            if vname == "A_abs_M1":
                res[f"local_cos_lin>c_{int(nv*100)}%"] = f"{int(sub.local_ok.sum())}/{len(sub)}"
                res[f"cos_lin_mediana_{int(nv*100)}%"] = float(sub.cos_lin.median())
        res[f"{vname}_pert_max_%"] = 100 * float(df[df.nivel == 0.05].pmax.median())
    # cos Δ real al 5 % (para comparar con la Tabla 1)
    cos5 = []
    for nivel, th_f in scen:
        if nivel != 0.05:
            continue
        th_s = S.theta0.copy(); th_s[sel_idx] = th_f[sel_idx]
        yf, ys = S.sim(th_f), S.sim(th_s)
        if yf is None or ys is None:
            continue
        df_, ds_ = (yf - y0).ravel(), (ys - y0).ravel()
        nf = np.linalg.norm(df_) + 1e-15; ns = np.linalg.norm(ds_) + 1e-15
        if nf < max(1e-10 * np.linalg.norm(y0), 1e-6):
            continue
        cos5.append(float(df_ @ ds_ / (nf * ns)))
    res["cos5_mediana"] = float(np.median(cos5)) if cos5 else float("nan")
    res["segundos"] = round(time.time() - t0, 1)
    return res


if __name__ == "__main__":
    which = sys.argv[1:]
    out = []
    for name, sel, t_def, group in SYSTEMS:
        if which and name not in which:
            continue
        print(f"== {name}", flush=True)
        try:
            r = analyze(name, sel, t_def, group,
                        max_points=None)
        except Exception as e:
            r = {"sistema": name, "error": repr(e)}
        print(json.dumps(r, default=str), flush=True)
        out.append(r)
        with open(OUT / f"{name}.json", "w") as fh:
            json.dump(r, fh, default=str, indent=1)
    if out:
        pd.DataFrame(out).to_csv(OUT / ("resumen.csv" if not which else "resumen_parcial.csv"),
                                 index=False)
