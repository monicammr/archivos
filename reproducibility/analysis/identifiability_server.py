#!/usr/bin/env python3
"""
Lanzador de identifiability_profiles.py para servidores Linux con muchos núcleos: cada tarea
(mínimo o punto del perfil) es un proceso independiente y, con NPROC > 1, el Jacobiano de cada
ajuste se reparte entre NPROC procesos hijos (control_perfil.ajusta_par, con 'fork'). Mismo
problema de optimización, mismos archivos de salida y misma clasificación que
identifiability_profiles.py.

Uso:
  python3 identifiability_server.py min    PROBLEMA NPROC
  python3 identifiability_server.py punto  PROBLEMA J LADO I NPROC
  python3 identifiability_server.py tareas PROBLEMA          # puntos pendientes, uno por línea
  python3 identifiability_server.py mejora PROBLEMA          # θ del mejor punto si mejora el mínimo
  python3 identifiability_server.py clasifica PROBLEMA [...]
"""
import sys, json, time, math
import numpy as np

import identifiability_profiles as P
import external_validation as VE
import profile_likelihood as CP


def ajusta(d, libres, th_ini, nf, nproc):
    if nproc > 1 and len(libres) > 1:
        return CP.ajusta_par(d["S"], libres, th_ini, None, d["zd"], d["filas"], nf, nproc)
    return VE.fit(d["S"], libres, th_ini, None, d["zd"], d["filas"], nf)


def cmd_min(name, nproc, desde=None):
    d = P.prep(name)
    t0 = time.time()
    th_ini = d["S"].theta0 if desde is None else np.array(desde)
    th, nfev = ajusta(d, d["libres"], th_ini, d["nf"], nproc)
    c = P.coste(d, th)
    rondas = 0
    if P.f_min(name).exists():
        ant = np.load(P.f_min(name))
        rondas = int(ant["rondas"]) if "rondas" in ant.files else 0
        if desde is not None:
            rondas += 1
            if float(ant["coste"]) < c:
                th, c = ant["theta"], float(ant["coste"])
    np.savez(P.f_min(name), theta=th, coste=c, nfev=nfev, segundos=time.time() - t0, rondas=rondas)
    print(json.dumps({"min": name, "coste": c, "seg": round(time.time() - t0, 1)}), flush=True)


def cmd_punto(name, j, lado, i, nproc):
    d = P.prep(name)
    S = d["S"]
    out = P.f_pto(name, S.names[j], lado, i)
    if out.exists():
        return
    t0 = time.time()
    m = np.load(P.f_min(name))
    th_min, c_min = m["theta"], float(m["coste"])
    sgn = -1.0 if S.theta0[j] < 0 else 1.0
    u = math.log(max(abs(th_min[j]), 1e-300)) + lado * P.DESPL[i]
    th_ini = th_min.copy(); th_ini[j] = sgn * math.exp(u)
    otros = [k for k in d["libres"] if k != j]
    th, nfev = ajusta(d, otros, th_ini, 30 * (len(otros) + 1), nproc) if otros else (th_ini, 0)
    c = P.coste(d, th)
    out.write_text(json.dumps({"parametro": S.names[j], "lado": lado, "despl": P.DESPL[i],
                               "log_theta": u, "dchi2": c - c_min, "nfev": nfev,
                               "segundos": round(time.time() - t0, 1),
                               "theta": [float(x) for x in th]}), encoding="utf-8")
    print(json.dumps({"punto": name, "par": S.names[j], "lado": lado, "i": i,
                      "dchi2": round(c - c_min, 3), "seg": round(time.time() - t0, 1)}), flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    (P.OUTD / a[1]).mkdir(parents=True, exist_ok=True) if len(a) > 1 else None
    if a[0] == "min":
        cmd_min(a[1], int(a[2]))
    elif a[0] == "punto":
        cmd_punto(a[1], int(a[2]), int(a[3]), int(a[4]), int(a[5]))
    elif a[0] == "tareas":
        for t in P.tareas_perfil(a[1]):
            print(*t)
    elif a[0] == "mejora":
        pts = [q for f in (P.OUTD / a[1]).glob("p_*.json")
               if P.dentro(P.prep(a[1]), q := json.loads(f.read_text(encoding="utf-8")))]
        mejor = min(pts, key=lambda p: p["dchi2"], default=None)
        if mejor is not None and mejor["dchi2"] < -P.MEJORA_MIN:
            print(json.dumps(mejor["theta"]))
    elif a[0] == "reajusta":          # reajusta PROBLEMA NPROC  (desde el mejor punto; borra el perfil)
        pts = [q for f in (P.OUTD / a[1]).glob("p_*.json")
               if P.dentro(P.prep(a[1]), q := json.loads(f.read_text(encoding="utf-8")))]
        mejor = min(pts, key=lambda p: p["dchi2"])
        c_punto = float(np.load(P.f_min(a[1]))["coste"]) + mejor["dchi2"]
        cmd_min(a[1], int(a[2]), desde=mejor["theta"])
        m = dict(np.load(P.f_min(a[1])))
        if c_punto < float(m["coste"]):        # el re-ajuste no alcanzó al punto: usar el punto
            m["theta"], m["coste"] = np.array(mejor["theta"]), c_punto
            np.savez(P.f_min(a[1]), **m)
        for f in (P.OUTD / a[1]).glob("p_*.json"):
            f.unlink()
    elif a[0] == "clasifica":
        for n in a[1:]:
            r = P.clasifica(n)
            print(n, [(p["parametro"], p["clase"], p["clase_robusto"]) for p in r["perfiles"]], flush=True)
