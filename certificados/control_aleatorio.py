#!/usr/bin/env python3
"""
Control subconjuntos aleatorios del mismo tamaño k.

Para cada problema admisible, selecciona aleatoriamente k parámetros biológicos
(mismo k que nuestro método) con N_SEEDS semillas distintas, ajusta cada subconjunto
en datos de entrenamiento y evalúa en prueba. Reporta la mediana del chi2/n sobre
semillas y la compara con nuestro método.

Esto demuestra que la selección específica importa: un subconjunto aleatorio del
mismo tamaño no reproduce el rendimiento del método.

Uso:
    python3 control_aleatorio.py [Problema ...]
    N_SEEDS=20 NPROC=3 python3 control_aleatorio.py

Salida: resultados/control_aleatorio/<problema>.json
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

HERE    = Path(__file__).resolve().parent
SUBS    = HERE / "resultados" / "reclasificacion_salidas_bio_poda"
NESTED  = HERE / "resultados" / "validacion_anidada"
OUTD    = HERE / "resultados" / "control_aleatorio"
NPROC   = int(os.environ.get("NPROC", 3))
N_SEEDS = int(os.environ.get("N_SEEDS", 20))


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

    cal_set = set(cal)
    bio_idx = [
        j for j in np.nonzero(S.in_model)[0]
        if S.names[j] not in cal_set
    ]
    cal_idx = [S.names.index(q) for q in cal if q in S.names]

    train, test, ftest, tipo = division(S)
    ftrain = ~ftest
    zd = S.zdata()
    ftr = ftrain & np.isfinite(zd)
    fte = ftest  & np.isfinite(zd)

    if not ftr.any() or not fte.any():
        return {"sistema": name, "no_evaluable": "single condition/time"}
    if len(bio_idx) < k:
        return {"sistema": name, "no_evaluable":
                f"solo {len(bio_idx)} parámetros bio < k={k}"}

    loc = locales_de_prueba(S, train, test)

    chi2_por_semilla = []
    for seed in range(N_SEEDS):
        rng = np.random.default_rng(seed)
        sel_rand = list(rng.choice(bio_idx, size=k, replace=False))
        libres = [j for j in (sel_rand + cal_idx) if j not in loc]

        if not libres:
            chi2_por_semilla.append(float("nan"))
            continue

        nf = 30 * (len(libres) + 1)
        ckpt = str(ckdir / f"seed{seed:03d}.npz")
        th_rand, _ = ajusta(S, libres, th0, train, zd, ftr, nf, ckpt=ckpt)
        chi2_por_semilla.append(chi2n(S, th_rand, zd, fte))

    vals = [v for v in chi2_por_semilla if np.isfinite(v)]
    chi2_rand_median = float(np.median(vals)) if vals else float("nan")
    chi2_rand_q1     = float(np.percentile(vals, 25)) if vals else float("nan")
    chi2_rand_q3     = float(np.percentile(vals, 75)) if vals else float("nan")

    chi2_ours = None
    nested_path = NESTED / f"{name}.json"
    if nested_path.exists():
        nested = json.loads(nested_path.read_text())
        chi2_ours = nested.get("chi2_test_red_original")

    ratio = (chi2_rand_median / chi2_ours
             if chi2_ours and chi2_ours > 0 else None)

    res = {
        "sistema": name,
        "k": k,
        "n_seeds": N_SEEDS,
        "n_validas": len(vals),
        "chi2_ours": chi2_ours,
        "chi2_rand_median": chi2_rand_median,
        "chi2_rand_q1": chi2_rand_q1,
        "chi2_rand_q3": chi2_rand_q3,
        "ratio_rand_vs_ours": ratio,
        "chi2_por_semilla": chi2_por_semilla,
        "segundos": round(time.time() - t0, 1),
    }
    (OUTD / f"{name}.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({k2: res[k2] for k2 in
                      ("sistema", "k", "chi2_ours", "chi2_rand_median",
                       "ratio_rand_vs_ours", "segundos")},
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
    print(f"Control aleatorio: {len(nombres)} problemas, "
          f"N_SEEDS={N_SEEDS}, NPROC={NPROC}", flush=True)
    with Pool(NPROC) as pool:
        list(pool.imap_unordered(_seguro, nombres))
    print("Listo.", flush=True)
