#!/usr/bin/env python3
"""
Selecciones de QR pivotado, Brun y Morris para Chen (155 parámetros libres, unos 35 s por simulación),
con exactamente las mismas funciones de selección y el mismo protocolo que comparacion_brun.py (QR) y
control_morris_brun.py (Brun y Morris), pero con las simulaciones repartidas entre NPROC núcleos.

Esos dos programas reparten el trabajo ENTRE problemas, de modo que un solo problema corre en un
núcleo: para Chen serían unas 1.850 simulaciones de 35 s seguidas (unas 18 h). Aquí:

  1. Registro. Se ejecutan las funciones de selección originales (qr_selection, brun, morris) con un
     simulador falso que solo anota cada vector de parámetros pedido. Los puntos que piden dependen
     solo de θ₀ y de la semilla de Morris, no de las salidas, así que la lista es exacta.
  2. Simulación. Todos los puntos anotados se simulan en paralelo (NPROC procesos).
  3. Selección. Se vuelven a ejecutar las mismas funciones con un simulador que devuelve los
     resultados guardados: la selección es idéntica a la del código original.
  4. Validación externa. Para cada subconjunto (más los parámetros de calibración) se re-estima en el
     entrenamiento desde θ₀ con el mismo problema de mínimos cuadrados que VE.ajusta (log|θ|, límites
     [|θ₀|/10, 10|θ₀|], 'trf', a lo sumo 30(n+1) evaluaciones), con las columnas del Jacobiano en
     paralelo (control_perfil.ajusta_par, como en la validación anidada de Chen), y se mide χ²/n en
     la prueba. Los tres ajustes corren a la vez.

Salida (mismo formato que los programas originales):
  resultados/comparacion_brun/Chen_MSB2009.json     (S_qr, chi2_qr, ...)
  resultados/control_morris_brun/Chen_MSB2009.json  (S_brun, S_morris, chi2_brun, chi2_morris, ...)
Uso: NPROC=40 python3 chen_criterios.py
"""
import os, sys, json, time
for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(v, "1")
from multiprocessing import Pool, Process
from pathlib import Path
import numpy as np
import petab_outputs as PO
import validacion_externa as VE
import comparacion_brun as QRMOD
import control_morris_brun as MB
import control_perfil as CP

NAME = os.environ.get("CRIT_PROBLEMA", "Chen_MSB2009")   # otro problema: para comprobar el programa
NPROC = int(os.environ.get("NPROC", 40))
HERE = Path(__file__).resolve().parent
TMP = HERE / "resultados" / f"criterios_tmp_{os.environ.get('CRIT_PROBLEMA', 'Chen_MSB2009')}"
_S = None


class Grabadora:
    """Simulador falso: anota cada (θ, grupo) pedido y devuelve ceros del tamaño correcto."""
    def __init__(self, S):
        self._S, self.pedidos = S, []
        self._m = len(S.zdata())

    def __getattr__(self, a):
        return getattr(self._S, a)

    def z(self, th, gidx=None):
        self.pedidos.append((np.array(th, dtype=float).copy(), gidx))
        return np.zeros(self._m)


class Cache:
    """Simulador que devuelve los resultados ya calculados (y simula si falta alguno)."""
    def __init__(self, S, tabla):
        self._S, self.tabla, self.faltan = S, tabla, 0

    def __getattr__(self, a):
        return getattr(self._S, a)

    def z(self, th, gidx=None):
        k = clave(th, gidx)
        if k not in self.tabla:
            self.faltan += 1
            self.tabla[k] = self._S.z(th, gidx)
        return self.tabla[k]


def clave(th, gidx):
    g = None if gidx is None else tuple(np.asarray(gidx).ravel().tolist())
    return (np.asarray(th, dtype=float).tobytes(), g)


def _init(name):
    """Cada proceso carga su propio modelo (funciona también sin fork, por ejemplo en Windows)."""
    global _S
    _S = PO.PSys(name)


def _sim(arg):
    th, gidx = arg
    try:
        return _S.z(th, gidx)
    except Exception:
        return None


def contexto():
    S = PO.PSys(NAME)
    info = json.loads((MB.SUBS / f"{NAME}.json").read_text())
    cal = set(info.get("calibracion", []))
    k = len(info["S"])
    train, test, ftest, tipo = VE.division(S)
    zd = S.zdata()
    ftr = ~ftest & np.isfinite(zd)
    fte = ftest & np.isfinite(zd)
    loc = VE.locales_de_prueba(S, train, test)
    # QR (comparacion_brun.uno): candidatos = parámetros del modelo que no son de calibración
    bio_qr = [j for j in np.nonzero(S.in_model)[0] if S.names[j] not in cal]
    cal_qr = [S.names.index(q) for q in info.get("calibracion", []) if q in S.names]
    # Brun y Morris (control_morris_brun.uno): libres sin los parámetros locales de la prueba
    libres = [int(j) for j in np.nonzero(S.in_model)[0] if j not in loc]
    bio = [j for j in libres if S.names[j] not in cal]
    cal_idx = [S.names.index(q) for q in cal if q in S.names and S.names.index(q) not in loc]
    return dict(S=S, info=info, k=k, train=train, test=test, ftest=ftest, tipo=tipo, zd=zd, ftr=ftr,
                fte=fte, loc=loc, bio_qr=bio_qr, cal_qr=cal_qr, bio=bio, cal_idx=cal_idx)


def selecciones(Sx, c):
    sel_qr = QRMOD.qr_selection(Sx, c["bio_qr"], c["k"], c["train"], c["zd"], c["ftr"])
    sel_b, ext_b = MB.brun(Sx, c["bio"], c["train"], c["ftr"], c["k"])
    sel_m, ext_m = MB.morris(Sx, c["bio"], c["train"], c["ftr"], c["k"])
    return sel_qr, (sel_b, ext_b), (sel_m, ext_m)


def ajuste(metodo, libres_sel, nproc):
    """Re-estimación en el entrenamiento y χ²/n en la prueba (proceso aparte)."""
    c = contexto()
    S = c["S"]
    t0 = time.time()
    th, nfev = CP.ajusta_par(S, libres_sel, S.theta0, c["train"], c["zd"], c["ftr"],
                             30 * (len(libres_sel) + 1), nproc)
    r = {"metodo": metodo, "chi2": float(VE.chi2(S.z(th), c["zd"], c["fte"])), "nfev": int(nfev),
         "segundos": round(time.time() - t0, 1), "theta": [float(x) for x in th]}
    (TMP / f"ajuste_{metodo}.json").write_text(json.dumps(r), encoding="utf-8")
    print(json.dumps({k: r[k] for k in ("metodo", "chi2", "nfev", "segundos")}), flush=True)


if __name__ == "__main__":
    global_t0 = time.time()
    TMP.mkdir(parents=True, exist_ok=True)
    c = contexto()
    S = c["S"]
    print(f"Chen: k={c['k']}, {len(c['bio'])} biológicos (Brun/Morris), {len(c['bio_qr'])} candidatos QR, NPROC={NPROC}", flush=True)

    # 1. registro de los puntos que piden las tres selecciones
    g = Grabadora(S)
    selecciones(g, c)
    pedidos, vistos = [], set()
    for th, gidx in g.pedidos:
        k = clave(th, gidx)
        if k not in vistos:
            vistos.add(k); pedidos.append((th, gidx))
    print(f"1. registro: {len(g.pedidos)} simulaciones pedidas, {len(pedidos)} distintas", flush=True)

    # 2. simulación en paralelo (los hijos heredan el modelo cargado)
    t1 = time.time()
    with Pool(NPROC, initializer=_init, initargs=(NAME,)) as pool:
        salidas = pool.map(_sim, pedidos, chunksize=1)
    tabla = {clave(th, gidx): z for (th, gidx), z in zip(pedidos, salidas)}
    fallos = sum(z is None for z in salidas)
    t_sim = time.time() - t1
    print(f"2. simulación: {len(pedidos)} puntos en {t_sim:.0f} s, {fallos} fallidos", flush=True)

    # 3. selección con las funciones originales sobre los resultados guardados
    cache = Cache(S, tabla)
    sel_qr, (sel_b, ext_b), (sel_m, ext_m) = selecciones(cache, c)
    print(f"3. selección: QR {[S.names[j] for j in sel_qr]}, Brun {[S.names[j] for j in sel_b]}, "
          f"Morris {[S.names[j] for j in sel_m]} (simulaciones fuera de la tabla: {cache.faltan})", flush=True)

    if os.environ.get("CRIT_SOLO_SELECCION") == "1":       # comprobación local de la selección
        print(json.dumps({"S_qr": [S.names[j] for j in sel_qr], "S_brun": [S.names[j] for j in sel_b],
                          "S_morris": [S.names[j] for j in sel_m]}), flush=True)
        sys.exit(0)

    # 4. validación externa de los tres subconjuntos, a la vez
    libres_qr = [j for j in (sel_qr + c["cal_qr"]) if j not in c["loc"]]
    libres_b = sel_b + [j for j in c["cal_idx"] if j not in sel_b]
    libres_m = sel_m + [j for j in c["cal_idx"] if j not in sel_m]
    nfit = max(2, NPROC // 3)
    procs = [Process(target=ajuste, args=(m, l, nfit)) for m, l in (("qr", libres_qr), ("brun", libres_b), ("morris", libres_m))]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    aj = {m: json.loads((TMP / f"ajuste_{m}.json").read_text()) for m in ("qr", "brun", "morris")}

    # 5. resultados con el formato de los programas originales
    S_ours = c["info"]["S"]
    nested = HERE / "resultados" / "validacion_anidada" / f"{NAME}.json"
    chi2_ours = json.loads(nested.read_text()).get("chi2_test_red_original") if nested.exists() else None
    S_qr = [S.names[j] for j in sel_qr]
    res_qr = {"sistema": NAME, "k": c["k"], "S_ours": S_ours, "S_qr": S_qr,
              "overlap": len(set(S_ours) & set(S_qr)), "chi2_ours": chi2_ours, "chi2_qr": aj["qr"]["chi2"],
              "ratio_qr_vs_ours": aj["qr"]["chi2"] / chi2_ours if chi2_ours else None, "tipo": c["tipo"],
              "segundos": round(t_sim + aj["qr"]["segundos"], 1),
              "nota": "chen_criterios.py: simulaciones de la selección y columnas del Jacobiano del ajuste en paralelo"}
    OUT_QR = Path(os.environ.get("CRIT_SALIDA_QR", QRMOD.OUTD))
    OUT_MB = Path(os.environ.get("CRIT_SALIDA_MB", MB.OUTD))
    OUT_QR.mkdir(parents=True, exist_ok=True)
    (OUT_QR / f"{NAME}.json").write_text(json.dumps(res_qr, indent=1, default=str))
    res = {"sistema": NAME, "k": c["k"], "division": c["tipo"], "n_bio": len(c["bio"]), "S_ours": S_ours}
    for m, sel, ext in (("brun", sel_b, ext_b), ("morris", sel_m, ext_m)):
        res[f"S_{m}"] = [S.names[j] for j in sel]
        res[f"chi2_{m}"] = aj[m]["chi2"]
        res[f"overlap_{m}_ours"] = len(set(res[f"S_{m}"]) & set(S_ours))
        res[f"segundos_{m}"] = aj[m]["segundos"]
        res[f"detalle_{m}"] = ext
    for clave_, (d, campo) in MB.PREV.items():
        f = d / f"{NAME}.json"
        res[f"chi2_{clave_}"] = json.loads(f.read_text()).get(campo) if f.exists() else None
    res["segundos"] = round(time.time() - global_t0, 1)
    res["segundos_simulacion_paralela"] = round(t_sim, 1)
    res["nota"] = "chen_criterios.py: mismas funciones brun() y morris(); simulaciones en paralelo"
    OUT_MB.mkdir(parents=True, exist_ok=True)
    (OUT_MB / f"{NAME}.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: res.get(k) for k in ("sistema", "S_brun", "S_morris", "chi2_ours", "chi2_qr", "chi2_brun", "chi2_morris", "segundos")}, default=str), flush=True)
    print("Done.", flush=True)
