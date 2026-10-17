#!/usr/bin/env python3
"""
Tests of the subsets of the five criteria (our method, pivoted QR, Brun, Morris, profile
likelihood; all with the same k) that only our method had before (Supplementary Notes
"Admissibility of the subsets of other criteria" and "Comparison of selection criteria on
synthetic data"):

A. ADMISSIBILITY, replicating selection.py (validate + efit + final rule): 15 scenarios
   theta^(k) = theta0 (1 + ADM_NIVEL u), seed 42; the subset and the calibration parameters are
   re-estimated from two starting points; scenarios with non-finite outputs are discarded; the subset
   is admissible if min(median e_fit, median e_rel) <= 0.436 and |S| >= 2. The eight problems of
   config.FIRST_ORDER are treated to first order for every criterion. ADM_NIVEL=0.05 (default, the
   level of the method) writes results/criteria_tests/, ADM_NIVEL=0.20 results/criteria_tests_20pc/.
B. SYNTHETIC (no leakage): experiment B of external_validation.py with SINT_SEMILLAS (default 42-46;
   the paper uses 42-61) for the four other criteria (our method: synthetic_seeds.py).

Additions after the second audit (Supplementary Note "Null controls, standard QR and selection on
the training outputs"):
* further subsets ("methods"): "qr_gks" (Golub-Klema-Stewart QR, qr_selection.py with
  QR_VARIANT=gks), "train" (our method selected on the training outputs only,
  results/selection_train_fixedscen/), "empty" (k = 0, calibration parameters only) and "rand<i>",
  i = 0..19 (the random k-subsets of baselines.py, same seeds);
* CT_FIXED_SCEN=1 (default): a scenario in which the simulation with the subset at its scenario values
  fails counts as e_rel = inf instead of being discarded, and the first-order e_fit of a scenario
  is min(e_rel, projection); the results go to <folder>_fixedscen/. For k = 0 and for single
  parameters the rule |S| >= 2 is not applied ("admisible_sin_kmin");
* SINT_FAMILIA = uniforme (default, theta0 (1 + 0.2 u)), loguniforme (theta0 10^U(-0.3, 0.3)) or
  dispersa (a random 15 % of the estimable parameters changed by +-50 %, the rest at theta0):
  other families of synthetic truths than the one used to decide admissibility; results in
  results/criteria_tests_sint_<family>/;
* CT_METODOS (comma-separated) restricts the methods; CT_PRUEBAS = adm,sint,real (default adm,sint);
  "real" fits the subset to the real training data and reports the test chi2/n.

Usage:  NPROC=90 python criteria_tests.py
        SOLO_SINT=1 SINT_SEMILLAS=47,48,...,61 NPROC=100 python criteria_tests.py
        ADM_NIVEL=0.20 python criteria_tests.py     (admissibility only: see the README)
Output: results/criteria_tests/<problem>__<criterion>__adm.json and __sint_<seed>.json
"""
import sys, json, time, os, math, warnings
from pathlib import Path
from multiprocessing import Pool

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(v, "1")
import numpy as np

warnings.filterwarnings("ignore")
import petab_problem as PP
import external_validation as EV

import config as CFG
R = CFG.RESULTS
SUBS = CFG.SELECTION
NPROC = int(os.environ.get("NPROC", 4))
OMITIR = {"Chen_MSB2009", "Lang_PLOSComputBiol2024", "Blasi_CellSystems2016"}
LINEAL = {"Alkan_SciSignal2018", "Bachmann_MSB2011", "Beer_MolBioSystems2014", "Chen_MSB2009",
          "Isensee_JCB2018", "Lang_PLOSComputBiol2024", "Lucarelli_CellSystems2018", "Raimundez_PCB2020"}
N_ESC, SEED, TAU = 15, 42, math.sqrt(1 - 0.9 ** 2)
# nivel de perturbación de los escenarios de admisibilidad (el del método: ±5 %); con otro nivel
# los resultados van a una carpeta aparte, p. ej. control_admis_sint_nivel020
NIVEL = float(os.environ.get("ADM_NIVEL", 0.05))
FIXED = os.environ.get("CT_FIXED_SCEN", "1") == "1"
FAMILIA = os.environ.get("SINT_FAMILIA", "uniforme")
OUTD = CFG.CRITERIA_TESTS if NIVEL == 0.05 else R / f"criteria_tests_{round(NIVEL * 100)}pc"
if FAMILIA != "uniforme":
    OUTD = R / f"criteria_tests_sint_{FAMILIA}"
elif FIXED:
    OUTD = OUTD.parent / (OUTD.name + "_fixedscen")
SEMILLAS = [int(x) for x in os.environ.get("SINT_SEMILLAS", "42,43,44,45,46").split(",")]
SOLO_SINT = os.environ.get("SOLO_SINT") == "1"
PRUEBAS = os.environ.get("CT_PRUEBAS", "sint" if SOLO_SINT else "adm,sint").split(",")
EV.CKDIR["dir"] = None
FUENTES = {"qr": (CFG.QR_SELECTION, "S_qr"), "brun": (CFG.BRUN_MORRIS, "S_brun"),
           "morris": (CFG.BRUN_MORRIS, "S_morris"), "perfil": (CFG.PROFILE, "S_perfil"),
           "qr_gks": (R / "qr_selection_gks", "S_qr"), "train": (R / "selection_train_fixedscen", "S"),
           "single": (R / "subsets_single", "S")}   # best single parameter (test of k_min = 2)
METODOS = os.environ.get("CT_METODOS", "ours,qr,brun,morris,perfil").split(",")
_C = {}


def aleatorio(name, i, k):
    """Random k-subset number i of baselines.py (seed i, biological parameters that affect y)."""
    S = sistema(name)
    info = json.loads((SUBS / f"{name}.json").read_text())
    cal = set(info.get("calibracion", []))
    bio = [j for j in np.nonzero(S.in_model)[0] if S.names[j] not in cal]
    rng = np.random.default_rng(i)
    return [S.names[j] for j in rng.choice(bio, size=k, replace=False)]


def sistema(name):
    if name not in _C:
        _C[name] = PP.PetabProblem(name)
    return _C[name]


def subconjunto(name, metodo):
    info = json.loads((SUBS / f"{name}.json").read_text())
    if metodo == "ours":
        nombres = info["S"]
    elif metodo == "empty":
        nombres = []
    elif metodo.startswith("rand"):
        nombres = aleatorio(name, int(metodo[4:]), len(info["S"]))
    else:
        d, campo = FUENTES[metodo]
        f = d / f"{name}.json"
        if not f.exists():
            return None, info
        d = json.loads(f.read_text(encoding="utf-8"))
        nombres = d.get(campo)
        if not nombres or (metodo == "train" and not d.get("admisible")):
            return None, info
    return list(nombres), info


def admisibilidad(name, metodo):
    S = sistema(name)
    nombres, info = subconjunto(name, metodo)
    if nombres is None:
        return {"no_evaluable": "sin subconjunto"}
    # Réplica de stage_reclass.py (valida + ajuste + regla final): S.sim devuelve None si alguna
    # salida no es finita, y entonces el escenario se descarta (e_rel) o el residuo vale 10.
    from scipy.optimize import least_squares
    th0 = S.theta0
    p = len(th0)
    Sl = [S.names.index(q) for q in nombres if q in S.names]
    Sl += [S.names.index(q) for q in info.get("calibracion", []) if q in S.names and S.names.index(q) not in Sl]
    y0 = S.sim(th0)
    if y0 is None:
        return {"no_evaluable": "falla la simulación nominal"}
    y0 = y0.ravel()
    rng = np.random.default_rng(SEED)
    escen = [th0 * (1 + NIVEL * rng.uniform(-1, 1, size=p)) for _ in range(N_ESC)]
    full = []
    for th in escen:
        yf = S.sim(th)
        full.append(None if yf is None else yf.ravel() - y0)
    umbral = max(1e-10 * np.linalg.norm(y0), 1e-6)
    # e_rel (valida)
    erel = []
    for th, df_ in zip(escen, full):
        if df_ is None or np.linalg.norm(df_) < umbral:
            continue
        ts = th0.copy(); ts[Sl] = th[Sl]
        ys = S.sim(ts) if Sl else y0.reshape(-1, 1)
        if ys is None:
            if FIXED:
                erel.append(float("inf"))
            continue
        erel.append(float(np.linalg.norm(df_ - (ys.ravel() - y0)) / np.linalg.norm(df_)))
    lineal = name in LINEAL
    efit = []
    if not Sl:
        # k = 0 and no calibration parameters: nothing is re-estimated, e_fit = e_rel = 1
        efit = [1.0 for df_ in full if df_ is not None and np.linalg.norm(df_) >= umbral]
    elif lineal:
        cols = []
        for j in Sl:
            tp, tm = th0.copy(), th0.copy()
            tp[j] *= 1.01; tm[j] *= 0.99
            yp, ym = S.sim(tp), S.sim(tm)
            cols.append((yp - ym).ravel() / 0.02 if yp is not None and ym is not None else np.zeros_like(y0))
        Js = np.column_stack(cols)
        for df_ in full:
            if df_ is None or np.linalg.norm(df_) < umbral:
                continue
            c_, *_ = np.linalg.lstsq(Js, df_, rcond=None)
            efit.append(float(np.linalg.norm(df_ - Js @ c_) / np.linalg.norm(df_)))
        if FIXED and len(efit) == len(erel):
            efit = [min(a, b) for a, b in zip(efit, erel)]     # e_fit,lin = min(e_rel, projection)
    else:
        sgn = np.where(th0[Sl] < 0, -1.0, 1.0)
        mag0 = np.maximum(np.abs(th0[Sl]), 1e-12)
        lo, hi = np.log(mag0 / 10), np.log(mag0 * 10)
        for th, df_ in zip(escen, full):
            if df_ is None or np.linalg.norm(df_) < umbral:
                continue
            nf = np.linalg.norm(df_)
            yf = y0 + df_

            def resid(u):
                ts = th0.copy(); ts[Sl] = sgn * np.exp(u)
                ys = S.sim(ts)
                return np.full(yf.size, 10.0) if ys is None else (ys.ravel() - yf) / nf
            mejor = float(np.linalg.norm(resid(np.log(np.maximum(np.abs(th[Sl]), 1e-12)))))
            x_esc = np.clip(np.log(np.maximum(np.abs(th[Sl]), 1e-12)), lo, hi)
            for x0 in (np.log(mag0), x_esc):
                try:
                    r = least_squares(resid, x0, bounds=(lo, hi), method="trf",
                                      max_nfev=100 * (len(Sl) + 1), diff_step=1e-3)
                    mejor = min(mejor, float(np.linalg.norm(r.fun)))
                except Exception:
                    pass
            efit.append(mejor)
    if not efit or not erel:
        return {"no_evaluable": "sin escenarios válidos"}
    med, med_r = float(np.median(efit)), float(np.median(erel))
    # regla de stage_reclass.py: admisible si min(e_ajuste, e_rel) ≤ τ (con |S| ≥ 2)
    return {"S": nombres, "k": len(nombres), "n_calibracion": len(Sl) - len(nombres),
            "eajuste_med": med, "erel_med": med_r,
            "admisible": bool(len(nombres) >= 2 and min(med, med_r) <= TAU),
            "admisible_sin_kmin": bool(min(med, med_r) <= TAU),
            "tasa_paso": float(np.mean(np.asarray(efit) <= TAU)),
            "n_escenarios": len(efit), "lineal": lineal, "escenarios_fijos": FIXED}


def real(name, metodo):
    """Fit the subset (with the calibration parameters) to the real training data, test chi2/n."""
    S = sistema(name)
    nombres, info = subconjunto(name, metodo)
    if nombres is None:
        return {"no_evaluable": "sin subconjunto"}
    train, test, ftest, tipo = EV.split(S)
    zd = S.zdata()
    ftr, fte = ~ftest & np.isfinite(zd), ftest & np.isfinite(zd)
    if not ftr.any() or not fte.any():
        return {"no_evaluable": "sin división"}
    loc = EV.test_only_parameters(S, train, test)
    sel = [S.names.index(q) for q in nombres if q in S.names]
    sel += [S.names.index(q) for q in info.get("calibracion", []) if q in S.names]
    sel = [j for j in dict.fromkeys(sel) if j not in loc]
    th0 = S.theta0
    th = EV.fit(S, sel, th0, train, zd, ftr, 30 * (len(sel) + 1))[0] if sel else th0
    f = CFG.NESTED / f"{name}.json"
    c_ours = json.loads(f.read_text()).get("chi2_test_red_original") if f.exists() else None
    c = EV.chi2(S.z(th), zd, fte)
    return {"S": nombres, "chi2_test": c, "chi2_ours": c_ours,
            "ratio_vs_ours": c / c_ours if c_ours else None}


def verdad(S, th0, libres, rng):
    """Synthetic truth of the family SINT_FAMILIA (the draws of the uniform family are those of
    external_validation.py and synthetic_seeds.py)."""
    th = th0.copy()
    if FAMILIA == "uniforme":
        u = rng.uniform(-1, 1, size=len(th0))
        th[libres] = th0[libres] * (1 + EV.TRUTH_LEVEL * u[libres])
    elif FAMILIA == "loguniforme":
        u = rng.uniform(-0.3, 0.3, size=len(th0))
        th[libres] = th0[libres] * 10.0 ** u[libres]
    elif FAMILIA == "dispersa":
        n = max(1, int(round(0.15 * len(libres))))
        cambia = rng.choice(libres, size=n, replace=False)
        th[cambia] = th0[cambia] * (1 + 0.5 * rng.choice([-1.0, 1.0], size=n))
    else:
        raise ValueError(FAMILIA)
    return th


def sintetico(name, metodo, seed):
    S = sistema(name)
    nombres, info = subconjunto(name, metodo)
    if nombres is None:
        return {"no_evaluable": "sin subconjunto"}
    th0 = S.theta0
    train, test, ftest, tipo = EV.split(S)
    ftrain = ~ftest
    if not ftrain.any() or not ftest.any():
        return {"no_evaluable": "sin división"}
    loc = EV.test_only_parameters(S, train, test)
    libres_full = [int(j) for j in np.nonzero(S.in_model)[0] if j not in loc]
    sel = [S.names.index(q) for q in nombres if q in S.names]
    sel += [S.names.index(q) for q in info.get("calibracion", []) if q in S.names]
    sel = [j for j in dict.fromkeys(sel) if j not in loc]
    if not sel:
        return {"no_evaluable": "subconjunto exclusivo de la prueba"}
    z0 = S.z(th0)
    rng = np.random.default_rng(seed)
    th_true = verdad(S, th0, libres_full, rng)
    zt = S.z(th_true)
    if zt is None or z0 is None:
        return {"no_evaluable": "falla la simulación de la verdad"}
    datos = zt + rng.standard_normal(len(zt))
    den = np.linalg.norm((zt - z0)[ftest])
    th, _ = EV.fit(S, sel, th0, train, datos, ftrain, 30 * (len(sel) + 1))
    z = S.z(th)
    return {"S": nombres, "semilla": seed, "familia": FAMILIA,
            "senal_rms_test": float(den / np.sqrt(ftest.sum())),
            "B_chi2_test_theta0": EV.chi2(z0, datos, ftest),
            "B_chi2_test_red": EV.chi2(z, datos, ftest),
            "B_epred_red": float(np.linalg.norm((z - zt)[ftest]) / den) if z is not None and den > 0 else float("nan")}


def tarea(t):
    name, metodo, prueba, seed = t
    out = OUTD / f"{name}__{metodo}__{prueba}{'' if seed is None else '_' + str(seed)}.json"
    if out.exists():
        return
    t0 = time.time()
    try:
        r = (admisibilidad(name, metodo) if prueba == "adm" else
             real(name, metodo) if prueba == "real" else sintetico(name, metodo, seed))
    except Exception as e:
        r = {"error": repr(e)}
    r.update(sistema=name, metodo=metodo, prueba=prueba, segundos=round(time.time() - t0, 1))
    OUTD.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(r, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: r.get(k) for k in ("sistema", "metodo", "prueba", "semilla", "eajuste_med",
                                            "admisible", "B_epred_red", "segundos", "error", "no_evaluable")
                      if r.get(k) is not None}, default=str), flush=True)


if __name__ == "__main__":
    nombres = sorted(f.stem for f in SUBS.glob("*.json")
                     if json.loads(f.read_text()).get("admisible") and f.stem not in OMITIR)
    LENTOS = ["Smith_BMCSystBiol2013", "Isensee_JCB2018", "Raimundez_PCB2020", "Bachmann_MSB2011",
              "Alkan_SciSignal2018", "Lucarelli_CellSystems2018", "Schwen_PONE2014", "Weber_BMC2015"]
    nombres.sort(key=lambda n: LENTOS.index(n) if n in LENTOS else len(LENTOS))
    sel = [x for x in sys.argv[1:] if not x.startswith("--")]
    if sel:
        nombres = [n for n in nombres if n in sel]
    tareas = []
    for n in nombres:
        for m in METODOS:
            if "adm" in PRUEBAS:
                tareas.append((n, m, "adm", None))
            if "real" in PRUEBAS:
                tareas.append((n, m, "real", None))
            # con la familia uniforme nuestro método ya tiene 20 semillas (synthetic_seeds.py)
            if "sint" in PRUEBAS and (m != "ours" or FAMILIA != "uniforme"):
                tareas += [(n, m, "sint", s) for s in SEMILLAS]
    print(f"Admisibilidad y sintético: {len(nombres)} problemas, {len(tareas)} tareas, NPROC={NPROC}", flush=True)
    with Pool(NPROC) as pool:
        list(pool.imap_unordered(tarea, tareas, chunksize=1))
    print("Done.", flush=True)
