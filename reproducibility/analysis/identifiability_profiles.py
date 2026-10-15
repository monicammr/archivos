#!/usr/bin/env python3
"""
Prueba 2 de identificabilidad del problema reducido: verosimilitud perfilada del MODELO REDUCIDO.

Para cada problema con subconjunto admisible (resultados/reclasificacion_salidas_bio_poda):
  * parámetros libres: los biológicos seleccionados S y los de calibración Θ_C; todos los demás
    quedan fijos en θ₀ (el valor publicado), igual que en el método;
  * datos: todas las mediciones experimentales del problema (escaladas por el ruido, y_i/σ_i);
  * mismo ajuste que el resto del estudio (validacion_externa.ajusta: log|θ|, límites
    [|θ₀|/10, 10|θ₀|], 'trf');
  1. mínimo: ajuste de S ∪ Θ_C desde θ₀ → θ̂_red, coste c_min = χ²;
  2. perfil de cada j ∈ S: se fija log|θ_j| = log|θ̂_red,j| ± DESPL (dentro de los límites) y se
     re-ajustan los demás parámetros de S ∪ Θ_C desde θ̂_red; Δχ² = χ²(θ_j fijo) − c_min;
     si un punto mejora el mínimo en más de MEJORA_MIN se re-ajusta desde él y se repite el perfil
     (hasta RONDAS_MAX rondas);
  3. clasificación con el umbral puntual del 95 % (Δχ² = 3,84, 1 g.l.), como control_perfil.py:
       identificable — supera el umbral a ambos lados (intervalo de confianza finito);
       no identificable práctico — sólo a un lado;  plano — a ningún lado.
     Variante robusta al ruido mal registrado: umbral 3,84·max(1, c_min/(n − n_libres)), que
     equivale a reescalar σ para que el ajuste tenga χ²/g.l. = 1.

Uso:   NPROC=8 python identifiability_profiles.py [Problema ...]
       (PERFIL_OMITIR="A,B" para saltar problemas)
Salida: results/identifiability/perfil/<problema>.json (+ <problema>/ con cada punto; lo ya
        hecho se reutiliza al relanzar) y resumen_perfil.csv
"""
import sys, json, time, os, math, warnings
from pathlib import Path
from multiprocessing import Pool

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(v, "1")
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
import petab_problem as PP
import external_validation as VE

import config as CFG
# Segunda auditoría: ID_SUBSETS=<carpeta de results/> perfila otros subconjuntos (p. ej. los
# seleccionados con las salidas de entrenamiento, selection_train_fixedscen); ID_DENSE=1 usa 20
# desplazamientos por lado (0,02-4,6, espaciado geométrico) en lugar de 10. Cada variante escribe en
# su propia carpeta: identifiability/profiles[_<carpeta>][_dense].
SUBF = os.environ.get("ID_SUBSETS", "selection")
DENSE = os.environ.get("ID_DENSE") == "1"
SUBS = CFG.RESULTS / SUBF
OUTD = CFG.IDENTIFIABILITY / ("profiles" + ("" if SUBF == "selection" else "_" + SUBF)
                              + ("_dense" if DENSE else ""))
NPROC = int(os.environ.get("NPROC", os.cpu_count() or 1))
DESPL = [0.05, 0.1, 0.2, 0.4, 0.7, 1.1, 1.6, 2.3, 3.2, 4.6]   # en log|θ_j|; 4,6 = factor 100
if DENSE:
    DESPL = [round(float(x), 4) for x in np.geomspace(0.02, 4.6, 20)]
UMBRAL = 3.84
FALLO = 1e4
MEJORA_MIN = 1.0
RONDAS_MAX = 3
VE.CKDIR["dir"] = None
LENTOS = ["Lang_PLOSComputBiol2024", "Chen_MSB2009", "Raimundez_PCB2020", "Bachmann_MSB2011"]

_C = {}


def prep(name):
    if name in _C:
        return _C[name]
    info = json.loads((SUBS / f"{name}.json").read_text())
    S = PP.PetabProblem(name)
    zd = S.zdata()
    filas = np.isfinite(zd)
    sel = [S.names.index(q) for q in info["S"]]
    cal = [S.names.index(q) for q in info.get("calibracion", []) if q in S.names]
    libres = sel + [j for j in cal if j not in sel]
    d = dict(S=S, info=info, zd=zd, filas=filas, sel=sel, libres=libres,
             nf=30 * (len(libres) + 1))
    _C[name] = d
    return d


def coste(d, th):
    z = d["S"].z(th)
    if z is None:
        return float("inf")
    r = z[d["filas"]] - d["zd"][d["filas"]]
    r = np.where(np.isfinite(r), r, 1e3)
    return float(r @ r)


def ajusta(d, libres, th_ini, nf):
    """Como VE.ajusta pero con los límites del perfil: para el parámetro fijado no hay
    límites (está fuera de `libres`), así que el perfil puede ir más allá de un factor 10."""
    return VE.fit(d["S"], libres, th_ini, None, d["zd"], d["filas"], nf)


def f_min(name):
    return OUTD / name / "minimo.npz"


def f_pto(name, par, lado, i):
    return OUTD / name / f"p_{par}_{'+' if lado > 0 else '-'}_{i}.json"


def t_minimo(arg):
    name, th_ini = arg
    try:
        d = prep(name)
        t0 = time.time()
        th, nfev = ajusta(d, d["libres"], d["S"].theta0 if th_ini is None else np.array(th_ini), d["nf"])
        c = coste(d, th)
        if th_ini is not None and f_min(name).exists():          # re-ajuste desde un punto mejor
            ant = np.load(f_min(name))
            if float(ant["coste"]) < c:
                th, c = ant["theta"], float(ant["coste"])
        np.savez(f_min(name), theta=th, coste=c, nfev=nfev, segundos=time.time() - t0)
        print(json.dumps({"min": name, "coste": round(c, 3), "seg": round(time.time() - t0, 1)}), flush=True)
    except Exception as e:
        print(json.dumps({"min": name, "error": repr(e)}), flush=True)
    return name


def t_punto(arg):
    name, j, lado, i = arg
    try:
        d = prep(name)
        S = d["S"]
        out = f_pto(name, S.names[j], lado, i)
        if out.exists():
            return arg
        t0 = time.time()
        m = np.load(f_min(name))
        th_min, c_min = m["theta"], float(m["coste"])
        sgn = -1.0 if S.theta0[j] < 0 else 1.0
        u = math.log(max(abs(th_min[j]), 1e-300)) + lado * DESPL[i]
        th_ini = th_min.copy(); th_ini[j] = sgn * math.exp(u)
        otros = [k for k in d["libres"] if k != j]
        if otros:
            th, nfev = ajusta(d, otros, th_ini, 30 * (len(otros) + 1))
        else:
            th, nfev = th_ini, 0
        c = coste(d, th)
        r = {"parametro": S.names[j], "lado": lado, "despl": DESPL[i], "log_theta": u,
             "dchi2": c - c_min, "nfev": nfev, "segundos": round(time.time() - t0, 1),
             "theta": [float(x) for x in th]}
        out.write_text(json.dumps(r), encoding="utf-8")
    except Exception as e:
        print(json.dumps({"punto": str(arg), "error": repr(e)}), flush=True)
    return arg


def dentro(d, p):
    """¿El punto del perfil cae dentro de los límites [|θ₀|/10, 10|θ₀|] del parámetro perfilado,
    los mismos de todos los ajustes del estudio? Fuera de ellos el mínimo de referencia no es
    comparable (el ajuste del mínimo no puede llegar allí), así que esos puntos no se usan."""
    S = d["S"]
    t0 = math.log(max(abs(S.theta0[S.names.index(p["parametro"])]), 1e-300))
    return abs(p["log_theta"] - t0) <= math.log(10) + 1e-6


def cruce(pts, umbral):
    prev_d, prev_c = 0.0, 0.0
    for p in pts:
        if p["dchi2"] > FALLO:
            continue
        c = max(p["dchi2"], 0.0)
        if c > umbral:
            return prev_d + (p["despl"] - prev_d) * (umbral - prev_c) / max(c - prev_c, 1e-12)
        prev_d, prev_c = p["despl"], c
    return math.inf


def clasifica(name):
    d = prep(name)
    S = d["S"]
    m = np.load(f_min(name))
    c_min = float(m["coste"])
    n = int(d["filas"].sum())
    gl = max(n - len(d["libres"]), 1)
    umbral_r = UMBRAL * max(1.0, c_min / gl)
    filas = []
    for j in d["sel"]:
        lados = {l: sorted([p for i in range(len(DESPL))
                            if (f := f_pto(name, S.names[j], l, i)).exists()
                            and dentro(d, p := json.loads(f.read_text(encoding="utf-8")))],
                           key=lambda p: p["despl"])
                 for l in (-1, 1)}
        # el mínimo está en el límite del parámetro si a un lado no queda ningún punto válido
        en_limite = [l for l in (-1, 1) if not lados[l]]
        fallos = sum(q["dchi2"] > FALLO for p in lados.values() for q in p)
        fila = {"parametro": S.names[j], "puntos_fallidos": fallos, "minimo_en_limite": en_limite,
                "dchi2_max_izq": max([q["dchi2"] for q in lados[-1] if q["dchi2"] <= FALLO] or [0.0]),
                "dchi2_max_der": max([q["dchi2"] for q in lados[1] if q["dchi2"] <= FALLO] or [0.0])}
        for tag, u in (("", UMBRAL), ("_robusto", umbral_r)):
            cr = {l: cruce(p, u) for l, p in lados.items()}
            nl = sum(math.isfinite(x) for x in cr.values())
            fila["clase" + tag] = ["plano", "no identificable practico", "identificable"][nl]
            fila["ic_izq_log" + tag], fila["ic_der_log" + tag] = cr[-1], cr[1]
        filas.append(fila)
    res = {"sistema": name, "S": d["info"]["S"], "n_calibracion": len(d["libres"]) - len(d["sel"]),
           "n_datos": n, "coste_min": c_min, "chi2_por_gl": c_min / gl, "umbral_robusto": umbral_r,
           "rondas": int(m["rondas"]) if "rondas" in m.files else 0,
           "dchi2_minimo": min([q["dchi2"] for f in (OUTD / name).glob("p_*.json")
                                if dentro(d, q := json.loads(f.read_text(encoding="utf-8")))] or [0.0]),
           "perfiles": filas}
    for tag in ("", "_robusto"):
        cl = [f["clase" + tag] for f in filas]
        res["n_identificables" + tag] = cl.count("identificable")
        res["todos_identificables" + tag] = cl.count("identificable") == len(cl)
    (OUTD / f"{name}.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    return res


def tareas_perfil(name):
    d = prep(name)
    return [(name, j, l, i) for j in d["sel"] for l in (-1, 1) for i in range(len(DESPL))
            if not f_pto(name, d["S"].names[j], l, i).exists()]


if __name__ == "__main__":
    OUTD.mkdir(parents=True, exist_ok=True)
    which = [a for a in sys.argv[1:] if not a.startswith("--")]
    omit = set(filter(None, os.environ.get("PERFIL_OMITIR", "").split(",")))
    todos = sorted(f.stem for f in SUBS.glob("*.json") if json.loads(f.read_text()).get("admisible"))
    if SUBF != "selection" and os.environ.get("ID_SOLO_CAMBIADOS") == "1":
        # sólo los problemas cuyo subconjunto difiere del de la selección principal
        todos = [n for n in todos if set(json.loads((SUBS / f"{n}.json").read_text())["S"])
                 != set(json.loads((CFG.SELECTION / f"{n}.json").read_text()).get("S", []))]
    lista = [n for n in todos if (not which or n in which) and n not in omit]
    lista = [n for n in lista if n not in LENTOS] + [n for n in LENTOS if n in lista]
    for n in lista:
        (OUTD / n).mkdir(exist_ok=True)
    t0 = time.time()
    with Pool(NPROC) as pool:
        # 1. mínimos
        list(pool.imap_unordered(t_minimo, [(n, None) for n in lista if not f_min(n).exists()], chunksize=1))
        pend = [n for n in lista if f_min(n).exists()]
        for ronda in range(RONDAS_MAX + 1):
            tareas = [t for n in pend for t in tareas_perfil(n)]
            print(f"ronda {ronda}: {len(pend)} problemas, {len(tareas)} puntos", flush=True)
            k = 0
            for _ in pool.imap_unordered(t_punto, tareas, chunksize=1):
                k += 1
                if k % 50 == 0:
                    print(f"  {k}/{len(tareas)} puntos ({time.time() - t0:.0f} s)", flush=True)
            # ¿algún punto mejora el mínimo? → re-ajustar desde él y repetir ese perfil
            rehacer = []
            for n in pend:
                pts = [q for f in (OUTD / n).glob("p_*.json")
                       if dentro(prep(n), q := json.loads(f.read_text(encoding="utf-8")))]
                mejor = min(pts, key=lambda p: p["dchi2"], default=None)
                if mejor is not None and mejor["dchi2"] < -MEJORA_MIN and ronda < RONDAS_MAX:
                    rehacer.append((n, mejor["theta"]))
            if not rehacer:
                break
            list(pool.imap_unordered(t_minimo, rehacer, chunksize=1))
            for n, _ in rehacer:
                m = dict(np.load(f_min(n))); m["rondas"] = ronda + 1
                np.savez(f_min(n), **m)
                for f in (OUTD / n).glob("p_*.json"):
                    f.unlink()
            pend = [n for n, _ in rehacer]
    res = []
    for n in lista:
        if f_min(n).exists():
            try:
                res.append(clasifica(n))
            except Exception as e:
                print(json.dumps({"clasifica": n, "error": repr(e)}), flush=True)
    pd.DataFrame([{k: v for k, v in r.items() if not isinstance(v, (list, dict))} for r in res]) \
        .to_csv(OUTD / "resumen_perfil.csv", index=False)
    print(f"Done ({time.time() - t0:.0f} s)", flush=True)
