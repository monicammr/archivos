#!/usr/bin/env python3
"""
Validación EXTERNA del modelo reducido (comentario 5 del revisor): ¿el subconjunto S, ajustado
con una parte de los experimentos, predice experimentos que NO se usaron para ajustar?

Datos: mediciones de PEtab en la escala de la verosimilitud, z_i = h(dato_i)/σ_i, y predicciones
ẑ_i(θ) = h(g_i(x(t_i), θ))/σ_i (petab_outputs.PSys). S = subconjunto seleccionado sobre las
salidas medidas (resultados/reclasificacion_salidas/, `stage_reclass.py --v3 --salidas`).

División entrenamiento / prueba (determinista):
  * sistemas con ≥ 2 condiciones experimentales: condiciones ordenadas por identificador; la de
    posición 3k+2 va a prueba (con 2 condiciones: la segunda) → predicción de condiciones nuevas;
  * sistemas con 1 condición: los tiempos posteriores al percentil 2/3 van a prueba →
    extrapolación temporal.

Ajustes (scipy least_squares, 'trf', en log|θ| con signo, límites [|θ₀|/10, 10|θ₀|], desde θ₀):
  * modelo REDUCIDO: sólo θ_S libre, el resto fijo en θ₀;
  * modelo COMPLETO: todos los parámetros que afectan a y libres (si son ≤ P_MAX_COMPLETO).
Parámetros exclusivos de las condiciones de prueba (p. ej. R0_NY al predecir Nueva York desde
California) no se pueden estimar con el entrenamiento: se excluyen de ambos ajustes y en el
experimento B su valor verdadero es θ₀. Si S sólo contiene parámetros así, el sistema se marca
"no evaluable" para esta división; también si hay una sola condición y un solo tiempo.

Experimento A (datos reales): ajuste a los datos reales de entrenamiento; métrica en prueba
  χ²/n = media de (ẑ − z)² (≈ 1 si el error es del tamaño del ruido). θ₀ (estimado por los autores
  con TODOS los datos, también los de prueba) se informa como referencia optimista.
Experimento B (sintético con ruido, sin fuga de información): verdad θ* = θ₀(1 + 0,2·u),
  u ~ U(−1, 1) (semilla 42), datos z* + ε, ε ~ N(0, 1) (ruido del tamaño de σ). Los parámetros no
  seleccionados quedan en θ₀ ≠ θ* (situación real). Métricas en prueba: χ²/n frente a los datos
  con ruido y e_pred = ‖ẑ − z*‖ / ‖z* − ẑ(θ₀)‖ (error relativo de predicción frente a la verdad,
  comparable con el umbral 0,436 de e_ajuste).

Uso: python3 validacion_externa.py [Sistema ...]   (por defecto, todos los admisibles)
Resultados: resultados/validacion_externa/<sistema>.json y RESUMEN_VALIDACION.md
"""
import sys, json, time, os, warnings
from pathlib import Path
from multiprocessing import Pool
import numpy as np
from scipy.optimize import least_squares

warnings.filterwarnings("ignore")
import petab_outputs as PO

HERE = Path(__file__).resolve().parent
SUBS = HERE / "resultados" / "reclasificacion_salidas"
OUTD = HERE / "resultados" / "validacion_externa"
# --bio: subconjuntos de la selección biológica con poda; los parámetros de calibración
# (escalas, offsets) del JSON se reajustan siempre junto con S
BIO = "--bio" in sys.argv
if BIO:
    SUBS = HERE / "resultados" / "reclasificacion_salidas_bio_poda"
    OUTD = HERE / "resultados" / "validacion_externa_bio"
P_MAX_COMPLETO = 60          # ajuste del modelo completo sólo hasta este número de parámetros
SEED, NIVEL_VERDAD = 42, 0.20
EMAX = float(np.sqrt(1 - 0.9 ** 2))


def division(S):
    """Devuelve (grupos de entrenamiento, grupos de prueba, máscara filas prueba, tipo)."""
    G = list(range(len(S.groups)))
    if len(G) >= 2:
        orden = sorted(G, key=lambda g: (S.groups[g][1], S.groups[g][0]))
        test = [orden[1]] if len(orden) == 2 else [g for i, g in enumerate(orden) if i % 3 == 2]
        train = [g for g in G if g not in test]
        filas_test = np.zeros(S.n_meas, bool)
        for g in test:
            filas_test[[r[0] for r in S.groups[g][3]]] = True
        return train, test, filas_test, "condiciones nuevas"
    t = S.mea["time"].astype(float).to_numpy()
    tu = np.unique(t[np.isfinite(t)])
    corte = tu[int(np.floor(2 * len(tu) / 3))] if len(tu) >= 3 else np.inf
    return G, G, t >= corte, f"extrapolación temporal (t ≥ {corte:g})"


def refs_grupo(S, g):
    """Identificadores de parámetros que usa el grupo g (overrides de su condición y de su
    preequilibrio, y parámetros de observable/ruido de sus filas)."""
    pre, sim_c, _, rows = S.groups[g]
    out = set()
    for c in (pre, sim_c):
        out |= {v for _, v in S.cond.get(c, []) if isinstance(v, str)}
    for _, _, _, op, npar in rows:
        out |= {v for v in op + npar if not PO._isnum(v)}
    return out


def locales_de_prueba(S, train, test):
    """Parámetros que sólo intervienen en las condiciones de prueba (p. ej. R0_NY si se
    predice Nueva York desde California): ningún ajuste con los datos de entrenamiento puede
    estimarlos, ni con el modelo reducido ni con el completo."""
    if set(train) == set(test):
        return set()
    rt = set().union(*[refs_grupo(S, g) for g in test]) if test else set()
    rr = set().union(*[refs_grupo(S, g) for g in train]) if train else set()
    compartidos = set(S.gparams)
    for f, g, _ in S.obs.values():
        compartidos |= {str(x) for x in f.free_symbols | g.free_symbols}
    return {S.idx[n] for n in rt - rr - compartidos if n in S.idx}


def ajusta(S, libres, th_ini, gidx, objetivo, filas, max_nfev):
    th0 = S.theta0
    sgn = np.where(th0[libres] < 0, -1.0, 1.0)
    mag0 = np.maximum(np.abs(th0[libres]), 1e-12)
    lo, hi = np.log(mag0 / 10), np.log(mag0 * 10)
    x0 = np.clip(np.log(np.maximum(np.abs(th_ini[libres]), 1e-12)), lo + 1e-9, hi - 1e-9)

    def theta(u):
        t = th_ini.copy(); t[libres] = sgn * np.exp(u)
        return t

    def res(u):
        z = S.z(theta(u), gidx)
        if z is None:
            return np.full(int(filas.sum()), 1e3)
        r = z[filas] - objetivo[filas]
        return np.where(np.isfinite(r), r, 1e3)

    try:
        r = least_squares(res, x0, bounds=(lo, hi), method="trf", max_nfev=max_nfev,
                          diff_step=1e-3)
        return theta(r.x), int(r.nfev)
    except Exception:
        return th_ini.copy(), 0


def chi2(z, objetivo, filas):
    if z is None:
        return float("nan")
    r = z[filas] - objetivo[filas]
    r = r[np.isfinite(r)]
    return float(np.mean(r ** 2)) if len(r) else float("nan")


def uno(name, S_nombres=None):
    t0 = time.time()
    info = json.loads((SUBS / f"{name}.json").read_text())
    if S_nombres is not None:          # subconjunto alternativo (p. ej. un solo parámetro)
        info = dict(info, S=list(S_nombres))
    S = PO.PSys(name)
    th0 = S.theta0
    Ssel = [S.names.index(q) for q in info["S"] if q in S.names]
    n_bio = len(Ssel)
    Ssel += [S.names.index(q) for q in info.get("calibracion", []) if q in S.names]
    libres_full = [int(j) for j in np.nonzero(S.in_model)[0]]
    train, test, ftest, tipo = division(S)
    ftrain_all = ~ftest
    if not ftrain_all.any() or not ftest.any():
        return {"sistema": name, "division": tipo, "n_condiciones": len(S.groups),
                "no_evaluable": "una sola condición y un solo tiempo de medición "
                                "(no se puede separar entrenamiento y prueba)"}
    loc = locales_de_prueba(S, train, test)
    G_all = list(range(len(S.groups)))
    res = {"sistema": name, "division": tipo, "n_condiciones": len(S.groups),
           "n_train": int(ftrain_all.sum()), "n_test": int(ftest.sum()),
           "S": info["S"], "|S|": n_bio, "n_calibracion": len(Ssel) - n_bio,
           "p_y": len(libres_full),
           "locales_prueba": [S.names[j] for j in sorted(loc)],
           "S_locales_prueba": [S.names[j] for j in Ssel if j in loc]}
    # los parámetros exclusivos de la prueba no se pueden estimar con el entrenamiento
    Ssel = [j for j in Ssel if j not in loc]
    libres_full = [j for j in libres_full if j not in loc]
    if len(Ssel) == 0:
        res["no_evaluable"] = ("todos los parámetros de S son exclusivos de las condiciones de "
                               "prueba")
        return res
    hacer_full = len(libres_full) <= P_MAX_COMPLETO
    nf_red, nf_full = 30 * (len(Ssel) + 1), 15 * (len(libres_full) + 1)

    # ---------------- A: datos reales
    zd = S.zdata()
    ftr = ftrain_all & np.isfinite(zd)
    fte = ftest & np.isfinite(zd)
    z0 = S.z(th0)
    res["A_chi2_test_theta0"] = chi2(z0, zd, fte)
    th_r, _ = ajusta(S, Ssel, th0, train, zd, ftr, nf_red)
    zr = S.z(th_r)
    res["A_chi2_train_red"] = chi2(zr, zd, ftr)
    res["A_chi2_test_red"] = chi2(zr, zd, fte)
    if hacer_full:
        th_f, _ = ajusta(S, libres_full, th0, train, zd, ftr, nf_full)
        zf = S.z(th_f)
        res["A_chi2_train_full"] = chi2(zf, zd, ftr)
        res["A_chi2_test_full"] = chi2(zf, zd, fte)

    # ---------------- B: sintético con ruido (verdad desconocida para el ajuste)
    rng = np.random.default_rng(SEED)
    u = rng.uniform(-1, 1, size=len(th0))
    th_true = th0.copy()
    th_true[libres_full] = th0[libres_full] * (1 + NIVEL_VERDAD * u[libres_full])
    # (los parámetros exclusivos de la prueba quedan en θ₀ en la verdad: nadie puede
    #  aprenderlos de otras condiciones)
    zt = S.z(th_true)
    if zt is None:
        res["B_error"] = "la simulación de la verdad θ* falla"
    else:
        datos = zt + rng.standard_normal(len(zt))
        ftr_b, fte_b = ftrain_all.copy(), ftest.copy()
        th_rb, _ = ajusta(S, Ssel, th0, train, datos, ftr_b, nf_red)
        zrb = S.z(th_rb)
        den = np.linalg.norm((zt - z0)[fte_b])
        res["B_chi2_test_theta0"] = chi2(z0, datos, fte_b)
        res["B_chi2_test_red"] = chi2(zrb, datos, fte_b)
        res["B_epred_red"] = (float(np.linalg.norm((zrb - zt)[fte_b]) / den)
                              if zrb is not None and den > 0 else float("nan"))
        res["B_epred_theta0"] = 1.0
        if hacer_full:
            th_fb, _ = ajusta(S, libres_full, th0, train, datos, ftr_b, nf_full)
            zfb = S.z(th_fb)
            res["B_chi2_test_full"] = chi2(zfb, datos, fte_b)
            res["B_epred_full"] = (float(np.linalg.norm((zfb - zt)[fte_b]) / den)
                                   if zfb is not None and den > 0 else float("nan"))
    res["segundos"] = round(time.time() - t0, 1)
    return res


def _seguro(name):
    try:
        r = uno(name)
    except Exception as e:
        r = {"sistema": name, "error": repr(e)}
    OUTD.mkdir(parents=True, exist_ok=True)
    (OUTD / f"{name}.json").write_text(json.dumps(r, indent=1, default=str))
    print(json.dumps(r, default=str), flush=True)
    return r


if __name__ == "__main__":
    nombres = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not nombres:
        nombres = []
        for f in sorted(SUBS.glob("*.json")):
            d = json.loads(f.read_text())
            if d.get("admisible") and len(d.get("S", [])) >= 2:
                nombres.append(f.stem)
    nproc = int(os.environ.get("NPROC", 2))
    with Pool(nproc) as pool:
        list(pool.imap_unordered(_seguro, nombres))
