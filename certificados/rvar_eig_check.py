import sys, numpy as np, pandas as pd, warnings, json
from pathlib import Path
warnings.filterwarnings("ignore")
import roadrunner as rr
rr.Config.setValue(rr.Config.ROADRUNNER_DISABLE_WARNINGS, True)
BENCH = Path(sys.argv[1])
DELTA, N_PTS = 0.01, 60
OBS = ("scale_","sd_","sigma_","offset_","noise_","Noise","Scale","Offset","noiseParameter")
# (k = |S| de la Tabla 1, Var.% de la Tabla 1 del PDF, subconjunto)
CASES = {
 "Raimundez_PCB2020": (1, 99.9, ["d_ksyn_EGFR__fm_2_hm"]),
 "Crauste_CellSystems2017": (2, 96.6, ["mu_N","rho_E"]),
 "Armistead_CellDeathDis2024": (2, 99.9, ["alpha_cer","k_d"]),
 "SalazarCavazos_MBoC2020": (4, 95.0, ["ratio_kpkd_Y1068__FREE","kdephosY1068__FREE","kdephosYN__FREE","ratio_kpkd_YN__FREE"]),
 "Chen_MSB2009": (2, 100.0, ["k35","k103"]),
 "Blasi_CellSystems2016": (2, 100.0, ["a_k8","a_basal"]),
 "Borghans_BiophysChem1997": (7, 91.4, ["Kz","Vm2","Vm3","beta_par","v1","v0","K_par"]),
 "Okuonghae_ChaosSolitonsFractals2020": (6, 88.2, ["transmission_rate_effective","gamma_0","gamma_a","sigma","nu","d_0"]),
 "Zheng_PNAS2012": (4, 96.3, ["k13_12","k12_13","k13_03","k12_22"]),
 "Sneyd_PNAS2002": (2, 99.5, ["k1","k2"]),
 "Elowitz_Nature2000": (2, 99.4, ["tps_active","tau_prot"]),
 "Fiedler_BMCSystBiol2016": (2, 100.0, ["K_1","tau2"]),
 "Bachmann_MSB2011": (2, 99.7, ["SHP1ActEpoR","STAT5Imp"]),
 "Boehm_JProteomeRes2014": (3, 97.9, ["k_exp_homo","k_imp_hetero","k_phos"]),
 "Lang_PLOSComputBiol2024": (6, 89.1, ["kCdc25_1","kPhEnsa","kPhRbD","kDeCb2","kDeCDKN1A_2","kPhCDKN1AByCe"]),
 "Smith_BMCSystBiol2013": (2, 53.2, ["k30f","kminus7b"]),
 "Giordano_Nature2020": (6, 83.7, ["alpha_4","alpha_28","zeta_22","rho_38","rho_22","tau"]),
 "Rahman_MBS2016": (3, 44.5, ["infected_moderate_transmission_rate","infected_moderate_worsen_rate","treated_moderate_improve_rate"]),
 "Weber_BMC2015": (4, 99.9, ["s31","a31","p31","p22"]),
}
TROB = {"Sneyd_PNAS2002":5.0,"Elowitz_Nature2000":5.0,"Borghans_BiophysChem1997":5.0,
        "Crauste_CellSystems2017":1.0,"Zhao_QuantBiol2020":1.0,"SalazarCavazos_MBoC2020":0.01}
def load(name):
    df = pd.read_csv(BENCH/name/"v1"/"parameters.tsv", sep="\t"); df = df[df["estimate"]==1]
    n = df["parameterId"].astype(str).tolist(); t = df["nominalValue"].astype(float).to_numpy()
    t = np.where(np.isfinite(t), t, 1e-6); t = np.where(t==0, 1e-12, t)
    dyn = [x for x in n if not any(x.startswith(p) for p in OBS)]
    return n, t, dyn
def sim(m, th, names, T):
    try:
        m.resetAll()
        for a, v in zip(names, th):
            try: m[str(a)] = float(v)
            except: pass
        r = np.asarray(m.simulate(1e-6, T, N_PTS), float)
        y = r[:,1:]
        return y if np.all(np.isfinite(y)) else None
    except: return None
def jac(name, T):
    names, th, dyn = load(name)
    m = rr.RoadRunner(str(BENCH/name/"v1"/"model.xml"))
    ig = m.getIntegrator()
    for k,v in [("relative_tolerance",1e-7),("absolute_tolerance",1e-10),("maximum_num_steps",200000),("stiff",True)]:
        try: ig.setValue(k,v)
        except: pass
    y0 = sim(m, th, names, T); cols=[]; used=[]
    for p in dyn:
        i = names.index(p); tp = th.copy(); tp[i] = max(th[i]*(1+DELTA), 1e-12)
        y = sim(m, tp, names, T)
        cols.append((y-y0).ravel()/(th[i]*DELTA+1e-15) if y is not None and y.shape==y0.shape else np.zeros(y0.size))
        used.append(p)
    return np.column_stack(cols), used, th, names
out = {}
for name, (k, paper, sel) in CASES.items():
    row = {"paper": paper, "k": k}
    for lab, T in (("T50", 50.0), ("Trob", TROB.get(name, 50.0))):
        if lab == "Trob" and T == 50.0: continue
        J, used, th, names = jac(name, T)
        lam = np.linalg.svd(J, compute_uv=False)**2
        row[f"eig_topk_{lab}"] = round(100*lam[:k].sum()/lam.sum(), 2)
        E = (J**2).sum(0); idx = [used.index(p) for p in sel if p in used]
        row[f"energia_S_{lab}"] = round(100*E[idx].sum()/E.sum(), 2)
    out[name] = row
    print(name, row, flush=True)
json.dump(out, open("eig_out.json", "w"), indent=1)
