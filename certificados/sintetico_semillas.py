#!/usr/bin/env python3
"""
Experimento sintético de predicción (experimento B de validacion_externa.py) repetido con
VARIAS SEMILLAS, para dar dispersión a los recuentos que el artículo informa con una sola (42).

Para cada sistema admisible y cada semilla s:
  verdad θ* = θ₀(1 + 0,2·u), u ~ U(−1, 1); datos z* + ε, ε ~ N(0, 1)   (default_rng(s), mismo
  orden de extracción que validacion_externa.py, de modo que s = 42 reproduce el artículo);
  misma división entrenamiento/prueba, mismos ajustes (reducido S ∪ Θ_C y completo, desde θ₀)
  y mismas métricas (χ²/n en prueba y e_pred).
El modelo completo sólo se ajusta si tiene ≤ SINT_PMAX parámetros libres (por defecto 100): con
más, cada ajuste en serie tarda de horas a días.

Uso: python3 sintetico_semillas.py [Sistema ...]      (por defecto, todos los admisibles)
     SINT_SEEDS="42-61"  SINT_PMAX=100  NPROC=100
Resultados: resultados/sintetico_semillas/<sistema>/s<semilla>.json (se omiten los ya hechos)
"""
import sys, json, time, os
from pathlib import Path
from multiprocessing import Pool

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(v, "1")
if "--bio" not in sys.argv:
    sys.argv.append("--bio")       # subconjuntos de la selección biológica con poda
import numpy as np
import validacion_externa as VE
import petab_outputs as PO

OUTD = VE.HERE / "resultados" / "sintetico_semillas"
P_MAX = int(os.environ.get("SINT_PMAX", 100))
a, b = os.environ.get("SINT_SEEDS", "42-61").split("-")
SEEDS = list(range(int(a), int(b) + 1))
# sistemas de simulación lenta: se lanzan primero para que no queden al final de la cola
LENTOS = ["Raimundez_PCB2020", "Smith_BMCSystBiol2013", "Isensee_JCB2018", "Chen_MSB2009",
          "Lang_PLOSComputBiol2024", "Bachmann_MSB2011", "Alkan_SciSignal2018",
          "Lucarelli_CellSystems2018"]


def uno(name, seed):
    t0 = time.time()
    info = json.loads((VE.SUBS / f"{name}.json").read_text())
    S = PO.PSys(name)
    th0 = S.theta0
    VE.CKDIR["dir"] = None          # sin puntos de control (cada tarea es un ajuste nuevo)
    Ssel = [S.names.index(q) for q in info["S"] if q in S.names]
    Ssel += [S.names.index(q) for q in info.get("calibracion", []) if q in S.names]
    libres_full = [int(j) for j in np.nonzero(S.in_model)[0]]
    train, test, ftest, tipo = VE.division(S)
    ftrain = ~ftest
    res = {"sistema": name, "semilla": seed, "p_y": len(libres_full)}
    if not ftrain.any() or not ftest.any():
        return dict(res, no_evaluable="sin división entrenamiento/prueba")
    loc = VE.locales_de_prueba(S, train, test)
    Ssel = [j for j in Ssel if j not in loc]
    libres_full = [j for j in libres_full if j not in loc]
    if len(Ssel) == 0:
        return dict(res, no_evaluable="S exclusivo de las condiciones de prueba")
    hacer_full = len(libres_full) <= P_MAX
    nf_red, nf_full = 30 * (len(Ssel) + 1), 15 * (len(libres_full) + 1)

    z0 = S.z(th0)
    rng = np.random.default_rng(seed)
    u = rng.uniform(-1, 1, size=len(th0))
    th_true = th0.copy()
    th_true[libres_full] = th0[libres_full] * (1 + VE.NIVEL_VERDAD * u[libres_full])
    zt = S.z(th_true)
    if zt is None or z0 is None:
        return dict(res, B_error="la simulación de la verdad θ* falla")
    datos = zt + rng.standard_normal(len(zt))
    den = np.linalg.norm((zt - z0)[ftest])

    def epred(z):
        return float(np.linalg.norm((z - zt)[ftest]) / den) if z is not None and den > 0 else float("nan")

    th_r, nr = VE.ajusta(S, Ssel, th0, train, datos, ftrain, nf_red)
    zr = S.z(th_r)
    res.update(B_chi2_test_theta0=VE.chi2(z0, datos, ftest), B_chi2_test_red=VE.chi2(zr, datos, ftest),
               B_epred_red=epred(zr), nfev_red=nr, seg_red=round(time.time() - t0, 1))
    if hacer_full:
        th_f, nf = VE.ajusta(S, libres_full, th0, train, datos, ftrain, nf_full)
        zf = S.z(th_f)
        res.update(B_chi2_test_full=VE.chi2(zf, datos, ftest), B_epred_full=epred(zf), nfev_full=nf)
    res["segundos"] = round(time.time() - t0, 1)
    return res


def _seguro(tarea):
    name, seed = tarea
    out = OUTD / name / f"s{seed}.json"
    if out.exists():
        return
    try:
        r = uno(name, seed)
    except Exception as e:
        r = {"sistema": name, "semilla": seed, "error": repr(e)}
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".tmp")
    tmp.write_text(json.dumps(r, indent=1, default=str), encoding="utf-8")
    os.replace(tmp, out)
    print(json.dumps({k: r.get(k) for k in ("sistema", "semilla", "B_epred_red", "B_epred_full",
                                            "segundos", "B_error", "no_evaluable", "error")
                      if r.get(k) is not None}, default=str), flush=True)


if __name__ == "__main__":
    nombres = [x for x in sys.argv[1:] if not x.startswith("--")]
    if not nombres:
        nombres = [f.stem for f in sorted(VE.SUBS.glob("*.json"))
                   if json.loads(f.read_text()).get("admisible")
                   and len(json.loads(f.read_text()).get("S", [])) >= 2]
    nombres.sort(key=lambda n: LENTOS.index(n) if n in LENTOS else len(LENTOS))
    tareas = [(n, s) for n in nombres for s in SEEDS]
    nproc = int(os.environ.get("NPROC", 100))
    print(f"{len(nombres)} sistemas x {len(SEEDS)} semillas = {len(tareas)} tareas, NPROC={nproc}, "
          f"completo si p <= {P_MAX}", flush=True)
    with Pool(nproc, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(_seguro, tareas, chunksize=1))
    print("Done.", flush=True)
