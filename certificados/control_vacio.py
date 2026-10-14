#!/usr/bin/env python3
"""
Control |S|=0: solo calibración (baseline natural).

Para cada problema admisible, ajusta ÚNICAMENTE los parámetros de calibración
(sin ningún parámetro biológico seleccionado) y evalúa en el conjunto de prueba.
Compara chi2/n con nuestro método para verificar que la selección biológica aporta.

Uso:
    python3 control_vacio.py [Problema ...]
    NPROC=3 python3 control_vacio.py

Salida: resultados/control_vacio/<problema>.json
"""
import sys
import json
import time
import os
import warnings
from pathlib import Path
from multiprocessing import Pool

import numpy as np

warnings.filterwarnings("ignore")
import petab_outputs as PO

from validacion_anidada import (
    division, locales_de_prueba, ajusta, chi2n, CKPT_INTERVAL,
)

HERE = Path(__file__).resolve().parent
SUBS   = HERE / "resultados" / "reclasificacion_salidas_bio_poda"
NESTED = HERE / "resultados" / "validacion_anidada"
OUTD   = HERE / "resultados" / "control_vacio"
NPROC  = int(os.environ.get("NPROC", 3))


def uno(name):
    t0 = time.time()
    OUTD.mkdir(parents=True, exist_ok=True)
    ckdir = OUTD / "checkpoints" / name
    ckdir.mkdir(parents=True, exist_ok=True)

    info_path = SUBS / f"{name}.json"
    if not info_path.exists():
        return {"sistema": name, "error": "no selection result"}
    info = json.loads(info_path.read_text())
    if not info.get("admisible"):
        return {"sistema": name, "error": "not admissible"}

    S = PO.PSys(name)
    th0 = S.theta0.copy()

    cal = info.get("calibracion", [])
    S_ours = info["S"]
    k = len(S_ours)

    cal_idx = [S.names.index(q) for q in cal if q in S.names]

    train, test, ftest, tipo = division(S)
    ftrain = ~ftest
    zd = S.zdata()
    ftr = ftrain & np.isfinite(zd)
    fte = ftest  & np.isfinite(zd)

    if not ftr.any() or not fte.any():
        return {"sistema": name, "no_evaluable": "single condition/time"}

    # |S|=0: solo calibración, sin parámetros biológicos
    loc = locales_de_prueba(S, train, test)
    libres_cal = [j for j in cal_idx if j not in loc]

    if not libres_cal:
        # Si no hay calibración, el modelo vacío es theta0 directo
        chi2_vacio = chi2n(S, th0, zd, fte)
        chi2_ours = None
        nested_path = NESTED / f"{name}.json"
        if nested_path.exists():
            nested = json.loads(nested_path.read_text())
            chi2_ours = nested.get("chi2_test_red_original")
        ratio = (chi2_vacio / chi2_ours
                 if chi2_ours and chi2_ours > 0 else None)
        res = {
            "sistema": name, "k": k,
            "chi2_ours": chi2_ours, "chi2_vacio": chi2_vacio,
            "ratio_vacio_vs_ours": ratio, "nota": "sin calibracion, th0 directo",
            "segundos": round(time.time() - t0, 1),
        }
        (OUTD / f"{name}.json").write_text(json.dumps(res, indent=1, default=str))
        print(json.dumps({k2: res[k2] for k2 in
                          ("sistema", "k", "chi2_ours", "chi2_vacio",
                           "ratio_vacio_vs_ours", "segundos")},
                         default=str), flush=True)
        return res

    nf = 30 * (len(libres_cal) + 1)
    th_cal, _ = ajusta(S, libres_cal, th0, train, zd, ftr, nf,
                       ckpt=str(ckdir / "cal.npz"))
    chi2_vacio = chi2n(S, th_cal, zd, fte)

    # chi2 de nuestro método desde validación anidada
    chi2_ours = None
    nested_path = NESTED / f"{name}.json"
    if nested_path.exists():
        nested = json.loads(nested_path.read_text())
        chi2_ours = nested.get("chi2_test_red_original")

    ratio = (chi2_vacio / chi2_ours
             if chi2_ours and chi2_ours > 0 else None)

    res = {
        "sistema": name,
        "k": k,
        "n_cal": len(libres_cal),
        "chi2_ours": chi2_ours,
        "chi2_vacio": chi2_vacio,
        "ratio_vacio_vs_ours": ratio,
        "segundos": round(time.time() - t0, 1),
    }
    (OUTD / f"{name}.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({k2: res[k2] for k2 in
                      ("sistema", "k", "chi2_ours", "chi2_vacio",
                       "ratio_vacio_vs_ours", "segundos")},
                     default=str), flush=True)
    return res


def _seguro(name):
    try:
        return uno(name)
    except Exception as e:
        r = {"sistema": name, "error": repr(e)}
        (OUTD / f"{name}.json").write_text(json.dumps(r, indent=1))
        print(json.dumps(r), flush=True)
        return r


if __name__ == "__main__":
    nombres = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not nombres:
        SKIP = {"Chen_MSB2009", "Lang_PLOSComputBiol2024"}
        nombres = sorted(
            f.stem for f in SUBS.glob("*.json")
            if json.loads(f.read_text()).get("admisible") and f.stem not in SKIP
        )
    print(f"Control vacío (|S|=0): {len(nombres)} problemas, NPROC={NPROC}", flush=True)
    with Pool(NPROC) as pool:
        list(pool.imap_unordered(_seguro, nombres))
    print("Listo.", flush=True)
