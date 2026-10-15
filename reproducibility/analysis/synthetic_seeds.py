#!/usr/bin/env python3
"""
Synthetic prediction experiment repeated with 20 seeds (Supplementary Note "Synthetic prediction
experiment"; main-text Fig. 3b): experiment B of external_validation.py, with the truth
theta* = theta0 (1 + 0.2 u) and the noise drawn from default_rng(s) for s = 42..61 (s = 42 reproduces
external_validation.py). Same split, fits and metrics. The full model is fitted only if it has at
most SINT_PMAX free parameters (default 100).

Usage:  SINT_SEEDS="42-61" SINT_PMAX=100 NPROC=100 python synthetic_seeds.py [Problem ...]
Output: results/synthetic_seeds/<problem>/s<seed>.json (finished tasks are skipped);
        figures_tables/comparison_tables.py summarises them.
"""
import sys, json, time, os
from pathlib import Path
from multiprocessing import Pool

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(v, "1")
import numpy as np
import external_validation as EV
import petab_problem as PP

import config as CFG
# SINT_AMPLITUD: amplitude a of the truth theta* = theta0 (1 + a u) (default 0.20, the one of the paper);
# with another amplitude the results go to results/synthetic_seeds_a<100 a>/. SINT_SOLO_SENAL=1: only the
# signal y(theta*) - y(theta0) in noise units (no fits), in results/synthetic_signal_a<100 a>/ (point C3).
AMPL = float(os.environ.get("SINT_AMPLITUD", EV.TRUTH_LEVEL))
SOLO_SENAL = os.environ.get("SINT_SOLO_SENAL") == "1"
_tag = f"a{round(100 * AMPL):03d}"
OUTD = (CFG.RESULTS / f"synthetic_signal_{_tag}" if SOLO_SENAL else
        CFG.SYNTHETIC_SEEDS if AMPL == EV.TRUTH_LEVEL else CFG.RESULTS / f"synthetic_seeds_{_tag}")
P_MAX = int(os.environ.get("SINT_PMAX", 100))
a, b = os.environ.get("SINT_SEEDS", "42-61").split("-")
SEEDS = list(range(int(a), int(b) + 1))
# sistemas de simulación lenta: se lanzan primero para que no queden al final de la cola
LENTOS = ["Raimundez_PCB2020", "Smith_BMCSystBiol2013", "Isensee_JCB2018", "Chen_MSB2009",
          "Lang_PLOSComputBiol2024", "Bachmann_MSB2011", "Alkan_SciSignal2018",
          "Lucarelli_CellSystems2018"]


def uno(name, seed):
    t0 = time.time()
    info = json.loads((CFG.SELECTION / f"{name}.json").read_text())
    S = PP.PetabProblem(name)
    th0 = S.theta0
    EV.CKDIR["dir"] = None          # sin puntos de control (cada tarea es un ajuste nuevo)
    Ssel = [S.names.index(q) for q in info["S"] if q in S.names]
    Ssel += [S.names.index(q) for q in info.get("calibracion", []) if q in S.names]
    libres_full = [int(j) for j in np.nonzero(S.in_model)[0]]
    train, test, ftest, tipo = EV.split(S)
    ftrain = ~ftest
    res = {"sistema": name, "semilla": seed, "p_y": len(libres_full)}
    if not ftrain.any() or not ftest.any():
        return dict(res, no_evaluable="sin división entrenamiento/prueba")
    loc = EV.test_only_parameters(S, train, test)
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
    th_true[libres_full] = th0[libres_full] * (1 + AMPL * u[libres_full])
    zt = S.z(th_true)
    if zt is None or z0 is None:
        return dict(res, B_error="la simulación de la verdad θ* falla")
    datos = zt + rng.standard_normal(len(zt))
    den = np.linalg.norm((zt - z0)[ftest])
    # signal y(theta*) - y(theta0) in noise units (z is scaled by sigma): RMS per measurement and norm
    res.update(amplitud=AMPL,
               senal_rms_train=float(np.linalg.norm((zt - z0)[ftrain]) / np.sqrt(ftrain.sum())),
               senal_rms_test=float(den / np.sqrt(ftest.sum())), senal_norma_test=float(den),
               ruido_norma_test=float(np.sqrt(ftest.sum())))
    if SOLO_SENAL:
        res["segundos"] = round(time.time() - t0, 1)
        return res

    def epred(z):
        return float(np.linalg.norm((z - zt)[ftest]) / den) if z is not None and den > 0 else float("nan")

    th_r, nr = EV.fit(S, Ssel, th0, train, datos, ftrain, nf_red)
    zr = S.z(th_r)
    res.update(B_chi2_test_theta0=EV.chi2(z0, datos, ftest), B_chi2_test_red=EV.chi2(zr, datos, ftest),
               B_epred_red=epred(zr), nfev_red=nr, seg_red=round(time.time() - t0, 1))
    if hacer_full:
        th_f, nf = EV.fit(S, libres_full, th0, train, datos, ftrain, nf_full)
        zf = S.z(th_f)
        res.update(B_chi2_test_full=EV.chi2(zf, datos, ftest), B_epred_full=epred(zf), nfev_full=nf)
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
        nombres = [f.stem for f in sorted(CFG.SELECTION.glob("*.json"))
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
