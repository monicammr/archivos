import sys, importlib, json, warnings
from pathlib import Path
import numpy as np
warnings.filterwarnings("ignore")
sys.path.insert(0, sys.argv[1])           # carpeta 01_pipeline_principal
P = importlib.import_module("petab_V9_todos35")
BENCH = Path(sys.argv[2])
CASES = {"Sneyd_PNAS2002": (["k1", "k2"], 99.5, 5.0),
         "Elowitz_Nature2000": (["tps_active", "tau_prot"], 99.4, 5.0),
         "Crauste_CellSystems2017": (["mu_N", "rho_E"], 96.6, 1.0)}
VARIANTS = {
    "A pipeline tal cual (abs, T=50, 200 pts, eps=1e-5)": dict(rel=False, T=50.0, N=200, eps=1e-5),
    "B pipeline con J relativa":                            dict(rel=True,  T=50.0, N=200, eps=1e-5),
    "C ajustes del paper (abs, 60 pts, δ=0.01, T robustez)": dict(rel=False, T=None, N=60, eps=1e-2),
    "D paper + J relativa":                                  dict(rel=True,  T=None, N=60, eps=1e-2),
}
out = {}
for name, (sel, paper, Trob) in CASES.items():
    folder = BENCH / name / "v1"
    df = P.load_parameters(folder, name)
    theta, names = P.get_nominal_theta(df)
    out[name] = {"paper": paper}
    for vn, v in VARIANTS.items():
        P.USE_RELATIVE_SENSITIVITY = v["rel"]
        T = v["T"] if v["T"] is not None else Trob
        m = P.load_roadrunner(folder / "model.xml")
        J = P.sensitivity_jacobian(m, theta, names, t_end=T, n_points=v["N"], eps=v["eps"])
        r = P.variance_retention(J, names, sel)
        E = (J ** 2).sum(axis=0); order = np.argsort(-E)
        top = [(names[i], round(float(E[i] / E.sum() * 100), 2)) for i in order[:4]]
        out[name][vn] = {"Rvar_%": round(100 * r, 3), "top_energia_%": top}
print(json.dumps(out, indent=1, ensure_ascii=False))
