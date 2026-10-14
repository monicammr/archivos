#!/usr/bin/env python3
"""
Selection by PROFILE LIKELIHOOD (Raue et al. 2009; reduction in the sense of Maiwald et al. 2016),
with the same protocol as qr_selection.py (Supplementary Note "Profile likelihood").

For each admissible problem:
  1. fit of the full model to the TRAINING data from theta0 -> theta_train (minimum of the profile);
  2. profile of each biological parameter j: log|theta_j| is fixed at theta_train +- DESPL (log units,
     within the bounds [|theta0|/10, 10|theta0|] of all other fits) and all other free parameters are
     re-estimated from theta_train; every point is an independent task, so all points of a problem
     are computed at once; Delta chi2 = chi2(theta_j fixed) - chi2(theta_train);
  3. if a profile point improves the minimum by more than MEJORA_MIN, the full model is re-estimated
     from that point and the profiles are repeated (at most PL_RONDAS times, default 3);
  4. classification with Delta chi2 = 3.84 (95 %, 1 d.f.): identifiable (above on both sides),
     practically non-identifiable (one side), flat (neither); failed fits (Delta chi2 > 1e4) are
     excluded;
  5. the k = |S| parameters with the narrowest profile confidence interval are selected, and the
     external validation is the same as for the other criteria.
Only problems with at most PL_PMAX free parameters (default 60) are profiled. Problems are
processed one at a time with all NPROC cores (the full-model fits distribute the columns of their
Jacobian); this needs Linux (fork).

Usage:  PL_PMAX=60 NPROC=120 python profile_likelihood.py [Problem ...]
        PL_RONDAS=10 NPROC=40 python profile_likelihood.py Raia_CancerResearch2011
Output: results/profile_likelihood/<problem>.json (+ <problem>/ with the full fit and every profile
        point; finished points are reused when the program is restarted)
"""
import sys, json, time, os, math, warnings
from pathlib import Path
from multiprocessing import Pool

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(v, "1")
import numpy as np

warnings.filterwarnings("ignore")
import petab_problem as PP
import external_validation as EV    # fit(): bounds always relative to theta0, free start point

import config as CFG
SUBS = CFG.SELECTION
NESTED = CFG.NESTED
BRUN = CFG.QR_SELECTION
OUTD = CFG.PROFILE
NPROC = int(os.environ.get("NPROC", 4))
PL_PMAX = int(os.environ.get("PL_PMAX", 60))
DESPL = [0.1, 0.3, 0.6, 1.2, 2.3]     # desplazamientos en log|θ_j| (2,3 ≈ factor 10, el límite)
UMBRAL = 3.84                         # χ²(1 g.l.) al 95 %
EV.CKDIR["dir"] = None                # sin puntos de control dentro de cada ajuste

_CACHE = {}


def preparar(name):
    """Datos comunes de un problema (se guardan en caché por proceso)."""
    if name in _CACHE:
        return _CACHE[name]
    info = json.loads((SUBS / f"{name}.json").read_text())
    S = PP.PetabProblem(name)
    cal = info.get("calibracion", [])
    cal_set = set(cal)
    train, test, ftest, tipo = EV.split(S)
    zd = S.zdata()
    ftr = ~ftest & np.isfinite(zd)
    fte = ftest & np.isfinite(zd)
    loc = EV.test_only_parameters(S, train, test)
    libres = [int(j) for j in np.nonzero(S.in_model)[0] if j not in loc]
    bio = [j for j in libres if S.names[j] not in cal_set]
    cal_idx = [S.names.index(q) for q in cal if q in S.names and S.names.index(q) not in loc]
    d = dict(S=S, info=info, train=train, ftr=ftr, fte=fte, zd=zd, libres=libres, bio=bio,
             cal_idx=cal_idx, tipo=tipo, nf_full=15 * (len(libres) + 1))
    _CACHE[name] = d
    return d


def coste(d, th):
    """χ² de entrenamiento (suma de residuos al cuadrado, misma escala que el ajuste)."""
    z = d["S"].z(th, d["train"])
    if z is None:
        return float("inf")
    r = z[d["ftr"]] - d["zd"][d["ftr"]]
    r = np.where(np.isfinite(r), r, 1e3)
    return float(r @ r)


def dir_sis(name):
    p = OUTD / name
    p.mkdir(parents=True, exist_ok=True)
    return p


# ── fase 1: mínimo del perfil (modelo completo en entrenamiento) ─────────────────

def fase1(name):
    f = dir_sis(name) / "full_train.npz"
    if f.exists():
        return
    d = preparar(name)
    t0 = time.time()
    th, nfev = EV.fit(d["S"], d["libres"], d["S"].theta0, d["train"], d["zd"], d["ftr"], d["nf_full"])
    np.savez(f, theta=th, coste=coste(d, th), nfev=nfev, segundos=time.time() - t0)
    print(json.dumps({"fase": 1, "sistema": name, "coste": coste(d, th), "nfev": nfev,
                      "seg": round(time.time() - t0, 1)}), flush=True)


# ── fase 2: un punto del perfil de un parámetro ───────────────────────────────────
# Cada punto de la rejilla es una tarea independiente (todas en paralelo): se fija θ_j y se
# re-ajustan los demás parámetros partiendo de θ̂_train.

def archivo_punto(name, parametro, lado, i):
    return OUTD / name / f"perfil_{parametro}_{'+' if lado > 0 else '-'}_{i}.json"


def puntos_validos(name, theta0_j, th_min_j):
    """Índices de DESPL que caen dentro de los límites [|θ₀|/10, 10|θ₀|], por lado."""
    lo = math.log(max(abs(theta0_j), 1e-12) / 10)
    hi = math.log(max(abs(theta0_j), 1e-12) * 10)
    u_min = math.log(max(abs(th_min_j), 1e-12))
    return [(lado, i) for lado in (-1, 1) for i, dl in enumerate(DESPL)
            if lo - 1e-9 <= u_min + lado * dl <= hi + 1e-9]


def fase2(tarea):
    name, j, lado, i = tarea
    d = preparar(name)
    S = d["S"]
    out = archivo_punto(name, S.names[j], lado, i)
    if out.exists():
        return
    t0 = time.time()
    base = np.load(dir_sis(name) / "full_train.npz")
    th_min, c_min = base["theta"], float(base["coste"])
    otros = [k for k in d["libres"] if k != j]
    sgn = -1.0 if S.theta0[j] < 0 else 1.0
    u = math.log(max(abs(th_min[j]), 1e-12)) + lado * DESPL[i]
    th_ini = th_min.copy()
    th_ini[j] = sgn * math.exp(u)
    th, nfev = EV.fit(S, otros, th_ini, d["train"], d["zd"], d["ftr"], d["nf_full"])
    c = coste(d, th)
    r = {"sistema": name, "parametro": S.names[j], "lado": lado, "despl": DESPL[i], "log_theta": u,
         "dchi2": c - c_min, "nfev": nfev, "segundos": round(time.time() - t0, 1),
         "theta": [float(x) for x in th]}       # para re-arrancar si este punto mejora el mínimo
    out.write_text(json.dumps(r, indent=1), encoding="utf-8")
    print(json.dumps({"fase": 2, "sistema": name, "parametro": S.names[j], "lado": lado,
                      "despl": DESPL[i], "dchi2": round(c - c_min, 3), "seg": r["segundos"]}), flush=True)


FALLO = 1e4          # Δχ² mayor: el ajuste del punto falló (simulación); no cuenta en el perfil
MEJORA_MIN = 1.0     # si un punto mejora el mínimo en más de esto, se re-ajusta y se repite
RONDAS_MAX = int(os.environ.get("PL_RONDAS", 3))


def cruce(puntos):
    """Distancia (en log) a la que Δχ² cruza UMBRAL, interpolando; ∞ si no cruza."""
    prev_d, prev_c = 0.0, 0.0
    for p in puntos:
        if p["dchi2"] > FALLO:
            continue
        c = max(p["dchi2"], 0.0)
        if c > UMBRAL:
            return prev_d + (p["despl"] - prev_d) * (UMBRAL - prev_c) / max(c - prev_c, 1e-12)
        prev_d, prev_c = p["despl"], c
    return math.inf


# ── fase 3: clasificación, selección de k y validación externa ────────────────────

def fase3(name):
    d = preparar(name)
    S, info = d["S"], d["info"]
    t0 = time.time()
    k = len(info["S"])
    filas = []
    for j in d["bio"]:
        lados = {}
        for lado in (-1, 1):
            ps = [json.loads(f.read_text(encoding="utf-8"))
                  for i in range(len(DESPL)) if (f := archivo_punto(name, S.names[j], lado, i)).exists()]
            lados[lado] = sorted(ps, key=lambda p: p["despl"])
        n_fallos = sum(q["dchi2"] > FALLO for p in lados.values() for q in p)
        lados = {l: [q for q in p if q["dchi2"] <= FALLO] for l, p in lados.items()}
        cr = {l: cruce(p) for l, p in lados.items()}
        mx = {l: max([max(q["dchi2"], 0.0) for q in p] or [0.0]) for l, p in lados.items()}
        n_lados = sum(math.isfinite(c) for c in cr.values())
        filas.append({"parametro": S.names[j], "j": j,
                      "clase": ["plano", "no identificable practico", "identificable"][n_lados],
                      "ancho_ic_log": cr[-1] + cr[1], "dchi2_max_izq": mx[-1], "dchi2_max_der": mx[1],
                      "dchi2_min_lado": min(mx.values()), "puntos_fallidos": n_fallos,
                      "dchi2_negativo": min([q["dchi2"] for p in lados.values() for q in p] or [0.0])})
    orden = sorted(filas, key=lambda r: (r["ancho_ic_log"], -r["dchi2_min_lado"]))
    sel = [r["j"] for r in orden[:k]]
    S_pl = [S.names[j] for j in sel]
    libres_pl = sel + [j for j in d["cal_idx"] if j not in sel]
    th_pl, _ = EV.fit(S, libres_pl, S.theta0, d["train"], d["zd"], d["ftr"], 30 * (len(libres_pl) + 1))
    chi2_pl = EV.chi2(S.z(th_pl), d["zd"], d["fte"])

    def leer(p, clave):
        p = p / f"{name}.json"
        return json.loads(p.read_text()).get(clave) if p.exists() else None
    chi2_ours = leer(NESTED, "chi2_test_red_original")
    chi2_qr = leer(BRUN, "chi2_qr")
    S_qr = leer(BRUN, "S_qr") or []
    base = np.load(dir_sis(name) / "full_train.npz")
    cls = [r["clase"] for r in filas]
    res = {
        "sistema": name, "k": k, "division": d["tipo"],
        "p_libres": len(d["libres"]), "n_bio": len(d["bio"]),
        "n_identificables": cls.count("identificable"),
        "n_no_identificables_practicos": cls.count("no identificable practico"),
        "n_planos": cls.count("plano"),
        "S_ours": info["S"], "S_perfil": S_pl, "S_qr": S_qr,
        "overlap_perfil_ours": len(set(S_pl) & set(info["S"])),
        "overlap_perfil_qr": len(set(S_pl) & set(S_qr)),
        "chi2_ours": chi2_ours, "chi2_qr": chi2_qr, "chi2_perfil": chi2_pl,
        "ratio_perfil_vs_ours": chi2_pl / chi2_ours if chi2_ours else None,
        "coste_min_train": float(base["coste"]),
        "dchi2_minimo_perfiles": min([r["dchi2_negativo"] for r in filas] or [0.0]),
        "puntos_fallidos": sum(r["puntos_fallidos"] for r in filas),
        "rondas_reajuste": int(base["rondas"]) if "rondas" in base else 0,
        "perfiles": [{k2: v for k2, v in r.items() if k2 != "j"} for r in orden],
        "segundos_fase3": round(time.time() - t0, 1),
    }
    (OUTD / f"{name}.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k2: res[k2] for k2 in ("sistema", "k", "n_bio", "n_identificables", "n_planos",
                                             "S_perfil", "chi2_ours", "chi2_qr", "chi2_perfil")},
                     default=str), flush=True)


def _seguro(fn, arg):
    try:
        fn(arg)
    except Exception as e:
        name = arg if isinstance(arg, str) else arg[0]
        print(json.dumps({"sistema": name, "tarea": str(arg), "error": repr(e)}), flush=True)
    return arg


def _f1(a): return _seguro(fase1, a)
def _f2(a): return _seguro(fase2, a)
def _f3(a): return _seguro(fase3, a)


# ── ajuste con Jacobiano en paralelo (para el ajuste completo de la fase 1) ──────────
# Mismo problema que VE.ajusta (log|θ|, límites [|θ₀|/10, 10|θ₀|], 'trf', diff_step=1e-3) y los
# mismos pasos de diferencias finitas que scipy; sólo las columnas del Jacobiano se evalúan en
# paralelo, en procesos hijos que heredan (fork) el modelo ya cargado.
_RESID = None


def _resid_hijo(u):
    return _RESID(u)


def ajusta_par(S, libres, th_ini, gidx, objetivo, filas, max_nfev, nproc):
    from scipy.optimize import least_squares
    from scipy.optimize._numdiff import _compute_absolute_step, _adjust_scheme_to_bounds
    global _RESID
    th0 = S.theta0
    sgn = np.where(th0[libres] < 0, -1.0, 1.0)
    mag0 = np.maximum(np.abs(th0[libres]), 1e-12)
    lo, hi = np.log(mag0 / 10), np.log(mag0 * 10)
    x0 = np.clip(np.log(np.maximum(np.abs(th_ini[libres]), 1e-12)), lo + 1e-9, hi - 1e-9)

    def theta(u):
        t = th_ini.copy(); t[libres] = sgn * np.exp(u)
        return t

    def resid(u):
        z = S.z(theta(u), gidx)
        r = np.full(int(filas.sum()), 1e3) if z is None else z[filas] - objetivo[filas]
        return np.where(np.isfinite(r), r, 1e3)

    ultimo = {"u": None, "r": None}

    def res(u):
        r = resid(u)
        ultimo["u"], ultimo["r"] = np.array(u, copy=True), r
        return r

    _RESID = resid
    pool = Pool(min(nproc, len(libres)))

    def jac(u):
        u = np.asarray(u, dtype=float)
        f0 = ultimo["r"] if ultimo["u"] is not None and np.array_equal(ultimo["u"], u) else resid(u)
        h = _compute_absolute_step(1e-3, u, f0, "2-point")
        h, _ = _adjust_scheme_to_bounds(u, h, 1, "1-sided", lo, hi)
        pts = []
        for k in range(len(u)):
            x = u.copy(); x[k] += h[k]
            pts.append(x)
        cols = pool.map(_resid_hijo, pts, chunksize=1)
        J = np.empty((len(f0), len(u)))
        for k, fk in enumerate(cols):
            J[:, k] = (fk - f0) / (pts[k][k] - u[k])
        return J

    try:
        r = least_squares(res, x0, jac=jac, bounds=(lo, hi), method="trf", max_nfev=max_nfev,
                          diff_step=1e-3)
        return theta(r.x), int(r.nfev)
    except Exception:
        return th_ini.copy(), 0
    finally:
        pool.terminate(); pool.join()


def fase1_paralela(name):
    """Fase 1 de un problema usando todos los núcleos para su Jacobiano."""
    f = dir_sis(name) / "full_train.npz"
    if f.exists():
        return
    d = preparar(name)
    t0 = time.time()
    th, nfev = ajusta_par(d["S"], d["libres"], d["S"].theta0, d["train"], d["zd"], d["ftr"],
                          d["nf_full"], NPROC)
    np.savez(f, theta=th, coste=coste(d, th), nfev=nfev, segundos=time.time() - t0)
    print(json.dumps({"fase": 1, "sistema": name, "coste": coste(d, th), "nfev": nfev,
                      "seg": round(time.time() - t0, 1)}), flush=True)


if __name__ == "__main__":
    nombres = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not nombres:
        nombres = sorted(f.stem for f in SUBS.glob("*.json") if json.loads(f.read_text()).get("admisible"))
    OUTD.mkdir(parents=True, exist_ok=True)
    validos, omitidos, meta = [], {}, {}
    for n in nombres:
        try:
            d = preparar(n)
        except Exception as e:
            omitidos[n] = f"error al cargar: {e!r}"
            continue
        if not d["ftr"].any() or not d["fte"].any():
            omitidos[n] = "sin división entrenamiento/prueba"
        elif len(d["libres"]) > PL_PMAX:
            omitidos[n] = f"{len(d['libres'])} parámetros libres > PL_PMAX={PL_PMAX}"
        else:
            validos.append(n)
            meta[n] = [(j, d["S"].names[j], float(d["S"].theta0[j])) for j in d["bio"]]
    for n, motivo in omitidos.items():
        (OUTD / f"{n}.json").write_text(json.dumps({"sistema": n, "no_evaluable": motivo}, indent=1),
                                        encoding="utf-8")
    _CACHE.clear()      # cada proceso hijo carga sus propios modelos
    print(f"Verosimilitud perfilada: {len(validos)} problemas, {len(omitidos)} omitidos, "
          f"NPROC={NPROC}, PL_PMAX={PL_PMAX}", flush=True)
    for n, m in omitidos.items():
        print(f"  omitido {n}: {m}", flush=True)
    # Un problema cada vez, con TODOS los núcleos: fase 1 con el Jacobiano repartido, fase 2 con
    # todos los puntos del perfil a la vez, fase 3 en el proceso principal.
    for n in validos:
        t0 = time.time()
        try:
            fase1_paralela(n)
        except Exception as e:
            print(json.dumps({"sistema": n, "fase": 1, "error": repr(e)}), flush=True)
            continue
        if not (OUTD / n / "full_train.npz").exists():
            continue
        for ronda in range(RONDAS_MAX + 1):
            th = np.load(OUTD / n / "full_train.npz")["theta"]
            tareas = [(n, j, lado, i) for j, nom, t0j in meta[n]
                      for lado, i in puntos_validos(n, t0j, th[j])
                      if not archivo_punto(n, nom, lado, i).exists()]
            if tareas:
                preparar(n)            # los hijos heredan (fork) el modelo ya cargado
                with Pool(min(NPROC, len(tareas))) as pool:
                    list(pool.imap_unordered(_f2, tareas, chunksize=1))
            # ¿algún punto del perfil mejora el mínimo? → re-ajustar desde él y repetir el perfil
            pts = [json.loads(f.read_text(encoding="utf-8")) for f in (OUTD / n).glob("perfil_*.json")]
            mejor = min(pts, key=lambda p: p["dchi2"], default=None)
            if mejor is None or mejor["dchi2"] >= -MEJORA_MIN or ronda == RONDAS_MAX:
                break
            if "theta" not in mejor:      # punto de una versión anterior sin θ guardado: repetir
                for f in (OUTD / n).glob("perfil_*.json"):
                    f.unlink()
                continue
            d = preparar(n)
            th_b, nfev = ajusta_par(d["S"], d["libres"], np.array(mejor["theta"]), d["train"], d["zd"],
                                    d["ftr"], d["nf_full"], NPROC)
            c_b = coste(d, th_b)
            c_p = float(np.load(OUTD / n / "full_train.npz")["coste"]) + mejor["dchi2"]
            if c_p < c_b:                 # el re-ajuste no mejoró el punto: quedarse con el punto
                th_b, c_b = np.array(mejor["theta"]), c_p
            np.savez(OUTD / n / "full_train.npz", theta=th_b, coste=c_b, nfev=nfev, rondas=ronda + 1)
            print(json.dumps({"sistema": n, "reajuste": ronda + 1, "mejora": mejor["dchi2"],
                              "coste": c_b}), flush=True)
            for f in (OUTD / n).glob("perfil_*.json"):
                f.unlink()
        _f3(n)
        _CACHE.pop(n, None)
        print(json.dumps({"sistema": n, "terminado": True, "puntos": len(tareas),
                          "seg_total": round(time.time() - t0, 1)}), flush=True)
    print("Done.", flush=True)
