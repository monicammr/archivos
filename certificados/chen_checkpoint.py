#!/usr/bin/env python3
"""
Wrapper de validacion_externa.py para Chen_MSB2009 con checkpointing.
Guarda el resultado parcial tras cada ajuste costoso.
Si se interrumpe, al relanzar retoma desde el último checkpoint.
"""
import json, time, os, warnings, sys
from pathlib import Path
import numpy as np

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import petab_outputs as PO
from scipy.optimize import least_squares
# Importar solo funciones puras, NO variables de módulo (dependen de sys.argv al importar)
from validacion_externa import division, locales_de_prueba, ajusta, chi2

HERE = Path(__file__).resolve().parent
SUBS = HERE / "resultados" / "reclasificacion_salidas_bio_poda"
OUTD = HERE / "resultados" / "validacion_externa_bio"
P_MAX_COMPLETO = int(os.environ.get("VAL_PMAX", 60))
SEED, NIVEL_VERDAD = 42, 0.20

NAME = "Chen_MSB2009"
CKPT = OUTD / f"{NAME}_ckpt.json"
OUT  = OUTD / f"{NAME}.json"


def save(d):
    OUTD.mkdir(parents=True, exist_ok=True)
    CKPT.write_text(json.dumps(d, indent=1, default=str), encoding="utf-8")
    print(f"[checkpoint] {list(d.keys())}", flush=True)


def load():
    if CKPT.exists():
        d = json.loads(CKPT.read_text())
        print(f"[checkpoint] Reanudando desde: {list(d.keys())}", flush=True)
        return d
    return None


def run():
    t0 = time.time()
    ckpt = load()

    info = json.loads((SUBS / f"{NAME}.json").read_text())
    S = PO.PSys(NAME)
    th0 = S.theta0
    Ssel = [S.names.index(q) for q in info["S"] if q in S.names]
    n_bio = len(Ssel)
    Ssel += [S.names.index(q) for q in info.get("calibracion", []) if q in S.names]
    libres_full = [int(j) for j in np.nonzero(S.in_model)[0]]
    train, test, ftest, tipo = division(S)
    ftrain_all = ~ftest
    loc = locales_de_prueba(S, train, test)
    Ssel = [j for j in Ssel if j not in loc]
    libres_full = [j for j in libres_full if j not in loc]
    hacer_full = len(libres_full) <= P_MAX_COMPLETO
    nf_red  = 30 * (len(Ssel) + 1)
    nf_full = 15 * (len(libres_full) + 1)

    res = ckpt or {
        "sistema": NAME, "division": tipo,
        "n_condiciones": len(S.groups),
        "n_train": int(ftrain_all.sum()), "n_test": int(ftest.sum()),
        "S": info["S"], "|S|": n_bio,
        "n_calibracion": len(Ssel) - n_bio,
        "p_y": len(libres_full),
        "locales_prueba": [S.names[j] for j in sorted(loc)],
        "S_locales_prueba": [S.names[j] for j in Ssel if j in loc],
    }

    # ── A: datos reales ──────────────────────────────────────────────
    zd = S.zdata()
    ftr = ftrain_all & np.isfinite(zd)
    fte = ftest & np.isfinite(zd)
    z0  = S.z(th0)
    if "A_chi2_test_theta0" not in res:
        res["A_chi2_test_theta0"] = chi2(z0, zd, fte)
        save(res)

    if "A_chi2_test_red" not in res:
        print(f"[{time.strftime('%H:%M:%S')}] Ajuste A reducido...", flush=True)
        th_r, _ = ajusta(S, Ssel, th0, train, zd, ftr, nf_red)
        zr = S.z(th_r)
        res["A_chi2_train_red"] = chi2(zr, zd, ftr)
        res["A_chi2_test_red"]  = chi2(zr, zd, fte)
        res["_th_r"] = th_r.tolist()
        save(res)
    else:
        th_r = np.array(res.pop("_th_r", th0.tolist()))
        zr   = S.z(th_r)

    if hacer_full and "A_chi2_test_full" not in res:
        print(f"[{time.strftime('%H:%M:%S')}] Ajuste A completo ({len(libres_full)} params)...", flush=True)
        th_f, _ = ajusta(S, libres_full, th0, train, zd, ftr, nf_full)
        zf = S.z(th_f)
        res["A_chi2_train_full"] = chi2(zf, zd, ftr)
        res["A_chi2_test_full"]  = chi2(zf, zd, fte)
        save(res)

    # ── B: sintético con ruido ────────────────────────────────────────
    rng    = np.random.default_rng(SEED)
    u      = rng.uniform(-1, 1, size=len(th0))
    th_true = th0.copy()
    th_true[libres_full] = th0[libres_full] * (1 + NIVEL_VERDAD * u[libres_full])
    zt = S.z(th_true)

    if zt is None:
        res["B_error"] = "la simulación de la verdad θ* falla"
    else:
        datos   = zt + rng.standard_normal(len(zt))
        ftr_b, fte_b = ftrain_all.copy(), ftest.copy()
        den     = np.linalg.norm((zt - z0)[fte_b])

        if "B_chi2_test_red" not in res:
            print(f"[{time.strftime('%H:%M:%S')}] Ajuste B reducido...", flush=True)
            th_rb, _ = ajusta(S, Ssel, th0, train, datos, ftr_b, nf_red)
            zrb = S.z(th_rb)
            res["B_chi2_test_theta0"] = chi2(z0, datos, fte_b)
            res["B_chi2_test_red"]    = chi2(zrb, datos, fte_b)
            res["B_epred_red"]        = (float(np.linalg.norm((zrb - zt)[fte_b]) / den)
                                         if zrb is not None and den > 0 else float("nan"))
            res["B_epred_theta0"]     = 1.0
            res["_th_rb"] = th_rb.tolist()
            save(res)

        if hacer_full and "B_chi2_test_full" not in res:
            print(f"[{time.strftime('%H:%M:%S')}] Ajuste B completo...", flush=True)
            th_rb = np.array(res.pop("_th_rb", th0.tolist()))
            th_fb, _ = ajusta(S, libres_full, th0, train, datos, ftr_b, nf_full)
            zfb = S.z(th_fb)
            res["B_chi2_test_full"] = chi2(zfb, datos, fte_b)
            res["B_epred_full"]     = (float(np.linalg.norm((zfb - zt)[fte_b]) / den)
                                       if zfb is not None and den > 0 else float("nan"))
            save(res)

    # ── Finalizar ────────────────────────────────────────────────────
    for k in list(res.keys()):
        if k.startswith("_"):
            del res[k]
    res["segundos"] = round(time.time() - t0, 1)
    OUT.write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    if CKPT.exists():
        CKPT.unlink()
    print(json.dumps(res, default=str), flush=True)
    print(f"Terminado Chen - {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)


if __name__ == "__main__":
    run()
