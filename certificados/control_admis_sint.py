#!/usr/bin/env python3
"""
Compara los subconjuntos de los cinco selectores (nuestro método, QR pivotado, Brun, Morris y
verosimilitud perfilada; todos con el mismo k) en dos pruebas que antes sólo tenía nuestro método:

A. ADMISIBILIDAD (criterio del método): 15 escenarios θ^(k) = θ₀ ⊙ (1 + 0,05 u^(k)),
   u ~ U(−1, 1)^p (semilla 42), sobre todas las salidas medidas. Para cada escenario se re-estiman
   S ∪ Θ_C (resto fijo en θ₀) para reproducir y(θ^(k)), desde dos arranques (valores del escenario
   y θ₀), con los límites [|θ₀|/10, 10|θ₀|] y a lo sumo 100(|S|+|Θ_C|+1) evaluaciones;
   e_fit = ‖y(θ̂) − y(θ^(k))‖ / ‖y(θ^(k)) − y(θ₀)‖, y se incluye e_rel (sin re-estimar) para que
   e_fit ≤ e_rel. Admisible si la mediana de e_fit ≤ 0,436. En los 8 problemas grandes en que el
   artículo usa la aproximación de primer orden (LINEAL) se usa también aquí: mínimos cuadrados
   lineales con las columnas de la J relativa (diferencias centradas, δ = 0,01) de S ∪ Θ_C.
B. SINTÉTICO (sin fuga): experimento B de validacion_externa.py con semillas 42–46 (verdad
   θ* = θ₀(1 + 0,2u), datos con ruido N(0, 1)); se ajusta S_x ∪ Θ_C en el entrenamiento desde θ₀ y
   se mide e_pred en la prueba.

Uso:   NPROC=100 python3 control_admis_sint.py
Salida: resultados/control_admis_sint/<problema>__<metodo>__<prueba>[_<semilla>].json
"""
import sys, json, time, os, math, warnings
from pathlib import Path
from multiprocessing import Pool

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(v, "1")
import numpy as np

warnings.filterwarnings("ignore")
import petab_outputs as PO
import validacion_externa as VE

HERE = Path(__file__).resolve().parent
R = HERE / "resultados"
SUBS = R / "reclasificacion_salidas_bio_poda"
NPROC = int(os.environ.get("NPROC", 4))
OMITIR = {"Chen_MSB2009", "Lang_PLOSComputBiol2024", "Blasi_CellSystems2016"}
LINEAL = {"Alkan_SciSignal2018", "Bachmann_MSB2011", "Beer_MolBioSystems2014", "Chen_MSB2009",
          "Isensee_JCB2018", "Lang_PLOSComputBiol2024", "Lucarelli_CellSystems2018", "Raimundez_PCB2020"}
N_ESC, SEED, TAU = 15, 42, math.sqrt(1 - 0.9 ** 2)
# nivel de perturbación de los escenarios de admisibilidad (el del método: ±5 %); con otro nivel
# los resultados van a una carpeta aparte, p. ej. control_admis_sint_nivel020
NIVEL = float(os.environ.get("ADM_NIVEL", 0.05))
OUTD = R / ("control_admis_sint" if NIVEL == 0.05 else f"control_admis_sint_nivel{round(NIVEL * 100):03d}")
SEMILLAS = [int(x) for x in os.environ.get("SINT_SEMILLAS", "42,43,44,45,46").split(",")]
SOLO_SINT = os.environ.get("SOLO_SINT") == "1"
SOLO_ADM = os.environ.get("SOLO_ADM") == "1"           # sólo admisibilidad (sin experimento sintético)
VE.CKDIR["dir"] = None
FUENTES = {"qr": (R / "comparacion_brun", "S_qr"), "brun": (R / "control_morris_brun", "S_brun"),
           "morris": (R / "control_morris_brun", "S_morris"), "perfil": (R / "control_perfil", "S_perfil")}
_C = {}


def sistema(name):
    if name not in _C:
        _C[name] = PO.PSys(name)
    return _C[name]


def subconjunto(name, metodo):
    info = json.loads((SUBS / f"{name}.json").read_text())
    if metodo == "ours":
        nombres = info["S"]
    else:
        d, campo = FUENTES[metodo]
        f = d / f"{name}.json"
        if not f.exists():
            return None, info
        nombres = json.loads(f.read_text(encoding="utf-8")).get(campo)
        if not nombres:
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
        ys = S.sim(ts)
        if ys is None:
            continue
        erel.append(float(np.linalg.norm(df_ - (ys.ravel() - y0)) / np.linalg.norm(df_)))
    lineal = name in LINEAL
    efit = []
    if lineal:
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
    return {"S": nombres, "eajuste_med": med, "erel_med": med_r,
            "admisible": bool(len(nombres) >= 2 and min(med, med_r) <= TAU),
            "n_escenarios": len(efit), "lineal": lineal}


def sintetico(name, metodo, seed):
    S = sistema(name)
    nombres, info = subconjunto(name, metodo)
    if nombres is None:
        return {"no_evaluable": "sin subconjunto"}
    th0 = S.theta0
    train, test, ftest, tipo = VE.division(S)
    ftrain = ~ftest
    if not ftrain.any() or not ftest.any():
        return {"no_evaluable": "sin división"}
    loc = VE.locales_de_prueba(S, train, test)
    libres_full = [int(j) for j in np.nonzero(S.in_model)[0] if j not in loc]
    sel = [S.names.index(q) for q in nombres if q in S.names]
    sel += [S.names.index(q) for q in info.get("calibracion", []) if q in S.names]
    sel = [j for j in dict.fromkeys(sel) if j not in loc]
    if not sel:
        return {"no_evaluable": "subconjunto exclusivo de la prueba"}
    z0 = S.z(th0)
    rng = np.random.default_rng(seed)
    u = rng.uniform(-1, 1, size=len(th0))
    th_true = th0.copy()
    th_true[libres_full] = th0[libres_full] * (1 + VE.NIVEL_VERDAD * u[libres_full])
    zt = S.z(th_true)
    if zt is None or z0 is None:
        return {"no_evaluable": "falla la simulación de la verdad"}
    datos = zt + rng.standard_normal(len(zt))
    den = np.linalg.norm((zt - z0)[ftest])
    th, _ = VE.ajusta(S, sel, th0, train, datos, ftrain, 30 * (len(sel) + 1))
    z = S.z(th)
    return {"S": nombres, "semilla": seed, "B_chi2_test_theta0": VE.chi2(z0, datos, ftest),
            "B_chi2_test_red": VE.chi2(z, datos, ftest),
            "B_epred_red": float(np.linalg.norm((z - zt)[ftest]) / den) if z is not None and den > 0 else float("nan")}


def tarea(t):
    name, metodo, prueba, seed = t
    out = OUTD / f"{name}__{metodo}__{prueba}{'' if seed is None else '_' + str(seed)}.json"
    if out.exists():
        return
    t0 = time.time()
    try:
        r = admisibilidad(name, metodo) if prueba == "adm" else sintetico(name, metodo, seed)
    except Exception as e:
        r = {"error": repr(e)}
    r.update(sistema=name, metodo=metodo, prueba=prueba, segundos=round(time.time() - t0, 1))
    OUTD.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(r, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: r.get(k) for k in ("sistema", "metodo", "prueba", "semilla", "eajuste_med",
                                            "admisible", "B_epred_red", "segundos", "error", "no_evaluable")
                      if r.get(k) is not None}, default=str), flush=True)


if __name__ == "__main__":
    admisibles = sorted(f.stem for f in SUBS.glob("*.json") if json.loads(f.read_text()).get("admisible"))
    nombres = [n for n in admisibles if n not in OMITIR]
    pedidos = [a for a in sys.argv[1:] if not a.startswith("--")]
    if pedidos:                                   # sólo los problemas indicados (también los de OMITIR)
        nombres = [n for n in admisibles if n in pedidos]
    LENTOS = ["Smith_BMCSystBiol2013", "Isensee_JCB2018", "Raimundez_PCB2020", "Bachmann_MSB2011",
              "Alkan_SciSignal2018", "Lucarelli_CellSystems2018", "Schwen_PONE2014", "Weber_BMC2015"]
    nombres.sort(key=lambda n: LENTOS.index(n) if n in LENTOS else len(LENTOS))
    tareas = []
    for n in nombres:
        for m in ("ours", "qr", "brun", "morris", "perfil"):
            if not SOLO_SINT:
                tareas.append((n, m, "adm", None))
            if m != "ours" and not SOLO_ADM:      # nuestro método ya tiene 20 semillas
                tareas += [(n, m, "sint", s) for s in SEMILLAS]
    print(f"Admisibilidad y sintético: {len(nombres)} problemas, {len(tareas)} tareas, NPROC={NPROC}", flush=True)
    with Pool(NPROC) as pool:
        list(pool.imap_unordered(tarea, tareas, chunksize=1))
    print("Done.", flush=True)
