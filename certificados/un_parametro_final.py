#!/usr/bin/env python3
"""
Single-parameter subsets with the FINAL method (justification of k_min = 2).

For every admissible problem of resultados/reclasificacion_salidas_bio_poda/ (final subsets), the
candidates are the K = 10 biological parameters of largest sensitivity energy E_j and the K of largest
finite effect s_j (the two orderings of the method). Each candidate j is tested ALONE as a subset, with
the calibration parameters re-estimated together with it (as in the final method): admissible if the
median of e_fit over the 15 scenarios at +-5 % (seed 42) is <= 0.436 (no k_min requirement).
For the best admissible candidate j*, the script also computes
  * the median e_fit at +-10 % for {j*} and for the final subset S (same scenarios, seed 42);
  * external validation of {j*} (real data: test chi2/n; synthetic: e_pred), with validacion_externa.uno.
Output: resultados/un_parametro_final/<problem>.json

Usage: python3 un_parametro_final.py [Problem ...]
"""
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

import minimalidad as M
import validacion_externa as VE

HERE = Path(__file__).resolve().parent
SEL = HERE / "resultados" / "reclasificacion_salidas_bio_poda"
OUTD = HERE / "resultados" / "un_parametro_final"
EMAX = float(np.sqrt(1 - 0.9 ** 2))
K, DELTA = 10, 0.01
SLOW = {"Bachmann_MSB2011", "Chen_MSB2009", "Isensee_JCB2018", "Lang_PLOSComputBiol2024", "Raimundez_PCB2020"}


def evaluar(name, nivel):
    M.NIVEL = nivel
    return M.Evaluador(name)


def uno(name):
    t0 = time.time()
    info = json.loads((SEL / f"{name}.json").read_text())
    ev = evaluar(name, 0.05)
    Sy = ev.S
    names = Sy.names
    cal = [names.index(q) for q in info.get("calibracion", []) if q in names]
    bio = [int(j) for j in np.nonzero(Sy.in_model)[0] if not Sy.calib[j]]
    E, s = np.zeros(len(ev.th0)), np.zeros(len(ev.th0))
    for j in bio:
        tp, tm = ev.th0.copy(), ev.th0.copy()
        tp[j] *= 1 + DELTA; tm[j] *= 1 - DELTA
        yp, ym = Sy.sim(tp), Sy.sim(tm)
        if yp is not None and ym is not None:
            E[j] = float(np.sum(((yp - ym).ravel() / (2 * DELTA)) ** 2))
        t1 = ev.th0.copy(); t1[j] *= 1.1
        y1 = Sy.sim(t1)
        s[j] = float(np.linalg.norm(y1.ravel() - ev.y0)) if y1 is not None else 0.0
    cand = []
    for orden in (np.argsort(-E), np.argsort(-s)):
        for j in orden[:K]:
            j = int(j)
            if j in bio and j not in cand and (E[j] > 0 or s[j] > 0):
                cand.append(j)
    solos = []
    for j in cand:
        idx = [j] + cal
        e = ev.erel(idx)
        a = ev.eajuste(idx) if not (np.isfinite(e) and e <= EMAX) else e
        solos.append({"parametro": names[j], "e_rel": e, "e_fit": min(a, e) if np.isfinite(e) else a,
                      "admisible": bool(np.isfinite(a) and min(a, e if np.isfinite(e) else a) <= EMAX)})
    res = {"sistema": name, "S": info["S"], "calibracion": info.get("calibracion", []),
           "candidatos": len(cand), "un_parametro": solos,
           "algun_parametro_solo_basta": any(x["admisible"] for x in solos)}
    ok = [x for x in solos if x["admisible"]]
    if ok:
        jbest = min(ok, key=lambda x: x["e_fit"])["parametro"]
        res["mejor"] = jbest
        ev10 = evaluar(name, 0.10)
        jb = [names.index(jbest)] + cal
        Sf = [names.index(q) for q in info["S"]] + cal
        res["mejor_efit_10"] = ev10.eajuste(jb)
        res["S_efit_10"] = ev10.eajuste(Sf)
        v = validar_uno(name, jbest)
        res["mejor_validacion"] = {k: v.get(k) for k in ("A_chi2_test_red", "B_chi2_test_theta0", "B_epred_red",
                                                         "no_evaluable", "B_error")}
    res["segundos"] = round(time.time() - t0, 1)
    return res


def validar_uno(name, jbest):
    """External validation of {j*} exactly as for the selected subset S: the subset file of the
    final selection is used, so the calibration parameters are re-estimated together with j*."""
    VE.SUBS = SEL
    VE.OUTD = HERE / "resultados" / "validacion_externa_bio"
    return VE.uno(name, S_nombres=[jbest])


def solo_validacion(name):
    """Recompute only the external validation of the best single parameter (keeps the rest)."""
    f = OUTD / f"{name}.json"
    r = json.loads(f.read_text())
    if "mejor" not in r:
        return
    t0 = time.time()
    v = validar_uno(name, r["mejor"])
    r["mejor_validacion"] = {k: v.get(k) for k in ("A_chi2_test_red", "B_chi2_test_theta0", "B_epred_red",
                                                    "no_evaluable", "B_error")}
    r["mejor_validacion_calibracion"] = len(json.loads((SEL / f"{name}.json").read_text()).get("calibracion", []))
    f.write_text(json.dumps(r, indent=1, default=str))
    print(json.dumps({"sistema": name, "mejor": r["mejor"], **r["mejor_validacion"],
                      "segundos": round(time.time() - t0, 1)}, default=str), flush=True)


def _seguro(name):
    try:
        r = uno(name)
    except Exception as e:
        r = {"sistema": name, "error": repr(e)}
    OUTD.mkdir(parents=True, exist_ok=True)
    (OUTD / f"{name}.json").write_text(json.dumps(r, indent=1, default=str))
    print(json.dumps({k: r.get(k) for k in ("sistema", "algun_parametro_solo_basta", "mejor", "error", "segundos")}), flush=True)


if __name__ == "__main__":
    nombres = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--solo-validacion" in sys.argv:
        with Pool(int(os.environ.get("NPROC", 2))) as pool:
            list(pool.imap_unordered(solo_validacion, nombres))
        sys.exit()
    if not nombres:
        nombres = sorted(f.stem for f in SEL.glob("*.json")
                         if json.loads(f.read_text())["admisible"] and f.stem not in SLOW)
    with Pool(int(os.environ.get("NPROC", 2))) as pool:
        list(pool.imap_unordered(_seguro, nombres))
