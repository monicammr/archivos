#!/usr/bin/env python3
"""
Controles de selección con dos métodos de la literatura, con el mismo protocolo que
comparacion_brun.py (QR pivotado) y control_perfil.py: mismo k = |S| de nuestro método, mismos
datos de entrenamiento, y validación externa idéntica (re-estimar S_x ∪ Θ_C en el entrenamiento
desde θ₀, resto fijo en θ₀, χ²/n en la prueba).

1. BRUN et al. (2001), índice de colinealidad. Sensibilidades adimensionales sobre las salidas de
   entrenamiento (ya divididas por σ): s_ij = θ_j ∂y_i/∂θ_j (diferencias hacia delante, paso
   relativo 1e-4, como el control QR). Importancia δ^msqr_j = ‖s_j‖/√n. Entre los M = 15
   parámetros más importantes se enumeran todos los subconjuntos de tamaño k; índice de
   colinealidad γ_K = 1/√λ_min(S̃_Kᵀ S̃_K) (columnas normalizadas) y medida de determinante
   ρ_K = det(S_Kᵀ S_K)^(1/2k). Se elige el subconjunto con γ_K ≤ 10 y mayor ρ_K (si ninguno cumple
   γ ≤ 10, el de menor γ).
2. MORRIS (1991), cribado por efectos elementales. Espacio de entrada: log θ_j en
   [log|θ₀,j| − ln 10, log|θ₀,j| + ln 10] (los mismos límites de los ajustes), rejilla de 4 niveles,
   Δ = 2/3 del rango, R = 10 trayectorias (semilla 42), sólo parámetros biológicos (los de
   calibración quedan en θ₀). Efecto elemental EE_j = ‖y(x + Δe_j) − y(x)‖ / Δ sobre las salidas
   de entrenamiento; se ordena por μ*_j = media de |EE_j| y se toman los k primeros.

Uso:   NPROC=40 python3 control_morris_brun.py [Problema ...]
Salida: resultados/control_morris_brun/<problema>.json
"""
import sys, json, time, os, math, itertools, warnings
from pathlib import Path
from multiprocessing import Pool

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(v, "1")
import numpy as np

warnings.filterwarnings("ignore")
import petab_outputs as PO
import validacion_externa as VE

HERE = Path(__file__).resolve().parent
SUBS = HERE / "resultados" / "reclasificacion_salidas_bio_poda"
OUTD = HERE / "resultados" / "control_morris_brun"
PREV = {"ours": (HERE / "resultados" / "validacion_anidada", "chi2_test_red_original"),
        "qr": (HERE / "resultados" / "comparacion_brun", "chi2_qr"),
        "perfil": (HERE / "resultados" / "control_perfil", "chi2_perfil")}
NPROC = int(os.environ.get("NPROC", 4))
OMITIR = {"Chen_MSB2009", "Lang_PLOSComputBiol2024"}     # igual que comparacion_brun.py
M_BRUN, GAMMA_MAX = 15, 10.0
R_MORRIS, NIVELES, SEED = 10, 4, 42
VE.CKDIR["dir"] = None


def salidas(S, th, gidx, ftr):
    z = S.z(th, gidx)
    if z is None:
        return None
    v = z[ftr]
    return np.where(np.isfinite(v), v, 0.0)


def brun(S, bio, gidx, ftr, k):
    th0 = S.theta0
    y0 = salidas(S, th0, gidx, ftr)
    Sm = np.zeros((len(y0), len(bio)))
    for c, j in enumerate(bio):
        eps = max(abs(th0[j]) * 1e-4, 1e-12)
        th = th0.copy(); th[j] += eps
        y = salidas(S, th, gidx, ftr)
        if y is not None:
            Sm[:, c] = (y - y0) / eps * th0[j]
    nrm = np.linalg.norm(Sm, axis=0)
    dmsqr = nrm / math.sqrt(len(y0))
    pool = [c for c in np.argsort(-dmsqr)[:M_BRUN] if nrm[c] > 1e-12]
    mejor, mejor_g = None, None
    for K in itertools.combinations(pool, k):
        K = list(K)
        Sn = Sm[:, K] / nrm[K]
        lam = np.linalg.eigvalsh(Sn.T @ Sn)
        g = 1 / math.sqrt(max(lam[0], 1e-300))
        rho = float(np.linalg.det(Sm[:, K].T @ Sm[:, K])) ** (1 / (2 * k))
        cand = (g <= GAMMA_MAX, rho if g <= GAMMA_MAX else -g)
        if mejor is None or cand > mejor[0]:
            mejor, mejor_g = (cand, K), g
    if mejor is None:
        return [], {}
    K = mejor[1]
    return [bio[c] for c in K], {"gamma": mejor_g, "cumple_gamma": bool(mejor_g <= GAMMA_MAX),
                                 "dmsqr_top": {S.names[bio[c]]: float(dmsqr[c]) for c in pool}}


def morris(S, bio, gidx, ftr, k):
    th0 = S.theta0
    rng = np.random.default_rng(SEED)
    p = len(bio)
    lo = np.log(np.maximum(np.abs(th0[bio]), 1e-12)) - math.log(10)
    ancho = 2 * math.log(10)
    sgn = np.where(th0[bio] < 0, -1.0, 1.0)
    delta = NIVELES / (2 * (NIVELES - 1))
    niveles = np.arange(NIVELES) / (NIVELES - 1)

    def y_de(x01):
        th = th0.copy()
        th[bio] = sgn * np.exp(lo + ancho * x01)
        return salidas(S, th, gidx, ftr)

    ee = [[] for _ in range(p)]
    fallos = 0
    for _ in range(R_MORRIS):
        x = rng.choice(niveles[niveles <= 1 - delta + 1e-12], size=p)
        y = y_de(x)
        for j in rng.permutation(p):
            xn = x.copy(); xn[j] += delta
            yn = y_de(xn)
            if y is not None and yn is not None:
                ee[j].append(float(np.linalg.norm(yn - y)) / delta)
            else:
                fallos += 1
            x, y = xn, yn
    mu = np.array([np.mean(e) if e else 0.0 for e in ee])
    orden = np.argsort(-mu)
    return [bio[c] for c in orden[:k]], {"mu_star_top": {S.names[bio[c]]: float(mu[c]) for c in orden[:10]},
                                         "fallos_simulacion": fallos}


def uno(name):
    t0 = time.time()
    info = json.loads((SUBS / f"{name}.json").read_text())
    S = PO.PSys(name)
    th0 = S.theta0
    cal = set(info.get("calibracion", []))
    train, test, ftest, tipo = VE.division(S)
    zd = S.zdata()
    ftr = ~ftest & np.isfinite(zd)
    fte = ftest & np.isfinite(zd)
    if not ftr.any() or not fte.any():
        return {"sistema": name, "no_evaluable": "sin división entrenamiento/prueba"}
    loc = VE.locales_de_prueba(S, train, test)
    libres = [int(j) for j in np.nonzero(S.in_model)[0] if j not in loc]
    bio = [j for j in libres if S.names[j] not in cal]
    cal_idx = [S.names.index(q) for q in cal if q in S.names and S.names.index(q) not in loc]
    k = len(info["S"])
    res = {"sistema": name, "k": k, "division": tipo, "n_bio": len(bio), "S_ours": info["S"]}
    for metodo, f in (("brun", brun), ("morris", morris)):
        t1 = time.time()
        sel, extra = f(S, bio, train, ftr, k)
        libres_sel = sel + [j for j in cal_idx if j not in sel]
        th, _ = VE.ajusta(S, libres_sel, th0, train, zd, ftr, 30 * (len(libres_sel) + 1))
        res[f"S_{metodo}"] = [S.names[j] for j in sel]
        res[f"chi2_{metodo}"] = VE.chi2(S.z(th), zd, fte)
        res[f"overlap_{metodo}_ours"] = len(set(res[f"S_{metodo}"]) & set(info["S"]))
        res[f"segundos_{metodo}"] = round(time.time() - t1, 1)
        res[f"detalle_{metodo}"] = extra
    for clave, (d, campo) in PREV.items():
        f = d / f"{name}.json"
        res[f"chi2_{clave}"] = json.loads(f.read_text()).get(campo) if f.exists() else None
    res["segundos"] = round(time.time() - t0, 1)
    return res


def _seguro(name):
    try:
        r = uno(name)
    except Exception as e:
        r = {"sistema": name, "error": repr(e)}
    OUTD.mkdir(parents=True, exist_ok=True)
    (OUTD / f"{name}.json").write_text(json.dumps(r, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: r.get(k) for k in ("sistema", "k", "chi2_ours", "chi2_qr", "chi2_perfil",
                                            "chi2_brun", "chi2_morris", "segundos", "error", "no_evaluable")
                      if r.get(k) is not None}, default=str), flush=True)


if __name__ == "__main__":
    nombres = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not nombres:
        nombres = sorted(f.stem for f in SUBS.glob("*.json")
                         if json.loads(f.read_text()).get("admisible") and f.stem not in OMITIR)
    # primero los lentos
    LENTOS = ["Raimundez_PCB2020", "Smith_BMCSystBiol2013", "Isensee_JCB2018", "Bachmann_MSB2011",
              "Alkan_SciSignal2018", "Lucarelli_CellSystems2018"]
    nombres.sort(key=lambda n: LENTOS.index(n) if n in LENTOS else len(LENTOS))
    print(f"Morris y Brun: {len(nombres)} problemas, NPROC={NPROC}", flush=True)
    with Pool(NPROC) as pool:
        list(pool.imap_unordered(_seguro, nombres, chunksize=1))
    print("Done.", flush=True)
