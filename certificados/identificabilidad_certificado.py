#!/usr/bin/env python3
"""
Hipótesis del teorema ProfileIdentifiability.practically_identifiable_grad (lean/) evaluadas en
cada problema, y certificado de identificabilidad práctica de cada parámetro seleccionado.

En el mínimo θ̂ del problema reducido (resultados/identificabilidad/perfil/<p>/minimo.npz), con
r(θ) = y(θ)/σ − dato/σ sobre todas las mediciones y δ = desplazamiento en log|θ| de los
parámetros libres S ∪ Θ_C:
  A      — ∂r/∂δ en θ̂ (diferencias centradas, paso 0,01 en log);
  ‖r₀‖   — norma del residuo en θ̂;
  γ      — ‖P r₀‖, proyección ortogonal de r₀ sobre la imagen de A (stat_of_projection);
  I_j    — 1/((AᵀA)⁻¹)_jj, información perfilada (info_of_matrix); 0 si AᵀA es singular;
  ε_j    — máx. de ‖r(θ̂+δ) − r₀ − Aδ‖ sobre los puntos calculados del perfil de θ_j dentro de los
           límites (el resto no lineal; estimado en esos puntos, no acotado en todo el dominio);
  t*_j   — tstarGrad(I_j, ε_j, γ, 3,84, ‖r₀‖) = (ε+γ+√(γ²+c+2‖r₀‖ε+2γε))/√I_j;
  d₋, d₊ — distancias de log|θ̂_j| a los límites log(|θ₀|/10) y log(10|θ₀|).
Certificado: t*_j < d₋ y t*_j < d₊ (hipótesis hlo, hhi del teorema).

Uso: python identificabilidad_certificado.py [Problema ...]
Salida: resultados/identificabilidad/certificado.csv
"""
import sys, json, math, os
from multiprocessing import Pool

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(v, "1")
import numpy as np
import pandas as pd
import identificabilidad_perfil as P

D = 0.01
C = P.UMBRAL


def tstar_grad(I, eps, gam, c, r0):
    if not I > 0:
        return math.inf
    return (eps + gam + math.sqrt(gam ** 2 + c + 2 * r0 * eps + 2 * gam * eps)) / math.sqrt(I)


def tstar_rel(I, eta, gam, c, r0):
    """Resto relativo ‖ρ‖ ≤ η‖Aδ‖ (η < 1): Δχ² ≥ (1−η)²a² − 2(γ+ηr₀)a con a = ‖Aδ‖, que
    supera c si a ≥ a* = (b + √(b² + (1−η)²c))/(1−η)², b = γ + ηr₀; t* = a*/√I."""
    if not I > 0 or not eta < 1:
        return math.inf
    b = gam + eta * r0
    q = (1 - eta) ** 2
    return (b + math.sqrt(b * b + q * c)) / q / math.sqrt(I)


def uno(name):
    try:
        d = P.prep(name)
        S = d["S"]
        th = np.load(P.f_min(name))["theta"]
        fil = d["filas"]
        lib = d["libres"]

        def r(t):
            z = S.z(t)
            return None if z is None else np.where(np.isfinite(z[fil] - d["zd"][fil]),
                                                   z[fil] - d["zd"][fil], 1e3)
        r0 = r(th)
        A = np.zeros((r0.size, len(lib)))
        for k, j in enumerate(lib):
            tp, tm = th.copy(), th.copy()
            tp[j] *= math.exp(D); tm[j] *= math.exp(-D)
            rp, rm = r(tp), r(tm)
            if rp is not None and rm is not None:
                A[:, k] = (rp - rm) / (2 * D)
        nz = np.linalg.norm(A, axis=0) > 1e-10 * max(np.linalg.norm(A, axis=0).max(), 1e-300)
        nulos = [S.names[j] for j, z in zip(lib, nz) if not z]
        A = A[:, nz]
        lib_nz = [j for j, z in zip(lib, nz) if z]
        coef, *_ = np.linalg.lstsq(A, r0, rcond=None)
        gam = float(np.linalg.norm(A @ coef))                 # ‖P r₀‖
        G = A.T @ A
        try:
            Ginv = np.linalg.inv(G)
            sing = not np.all(np.isfinite(Ginv)) or np.linalg.cond(G) > 1e14
        except np.linalg.LinAlgError:
            Ginv, sing = None, True
        u_hat = np.log(np.abs(th[lib_nz]))
        filas = []
        perf = {p["parametro"]: p for p in json.loads((P.OUTD / f"{name}.json").read_text())["perfiles"]}
        for k, j in ((lib_nz.index(j) if j in lib_nz else None, j) for j in d["sel"]):
            nom = S.names[j]
            # información perfilada I_j = min_{δ_j=1} ‖Aδ‖² = ‖a_j − proyección de a_j sobre las demás
            # columnas‖² (= 1/((AᵀA)⁻¹)_jj si AᵀA es invertible; bien definida aunque otras columnas,
            # p. ej. dos parámetros de calibración, sean colineales entre sí)
            if k is None:
                I = 0.0
            else:
                otras = np.delete(A, k, axis=1)
                if otras.shape[1]:
                    cf, *_ = np.linalg.lstsq(otras, A[:, k], rcond=None)
                    I = float(np.sum((A[:, k] - otras @ cf) ** 2))
                else:
                    I = float(A[:, k] @ A[:, k])
                if I <= 1e-12 * float(A[:, k] @ A[:, k]):
                    I = 0.0
            # ε_j: resto no lineal en los puntos del perfil de θ_j (dentro de los límites)
            eps, eta, npts = 0.0, 0.0, 0
            por_lado = {-1: [], 1: []}
            for f in (P.OUTD / name).glob(f"p_{nom}_*.json"):
                p = json.loads(f.read_text(encoding="utf-8"))
                if not P.dentro(d, p) or p["dchi2"] > P.FALLO:
                    continue
                tp = np.array(p["theta"])
                rp = r(tp)
                if rp is None:
                    continue
                delta = np.log(np.abs(tp[lib_nz])) - u_hat
                rem = float(np.linalg.norm(rp - r0 - A @ delta))
                eps = max(eps, rem)
                nAd = float(np.linalg.norm(A @ delta))
                eta = max(eta, rem / nAd if nAd > 0 else math.inf)
                por_lado[p["lado"]].append((abs(delta[lib_nz.index(j)]), rem))
                npts += 1
            t0 = math.log(max(abs(S.theta0[j]), 1e-300)); u = math.log(max(abs(th[j]), 1e-300))
            dlo, dhi = u - (t0 - math.log(10)), (t0 + math.log(10)) - u
            ts = tstar_grad(I, eps, gam, C, float(np.linalg.norm(r0)))
            ts_lin = tstar_grad(I, 0.0, 0.0, C, 0.0)
            ts_rel = tstar_rel(I, eta, gam, C, float(np.linalg.norm(r0)))
            # certificado local por lado: primer punto t_k del perfil con t_k ≥ t*(ε_k), ε_k = máx.
            # del resto en los puntos de ese lado hasta t_k (y t_k dentro de los límites)
            cruce = {}
            for lado, pts in por_lado.items():
                epsk, cruce[lado] = 0.0, math.inf
                for tk, rk in sorted(pts):
                    epsk = max(epsk, rk)
                    if tk >= tstar_grad(I, epsk, gam, C, float(np.linalg.norm(r0))):
                        cruce[lado] = tk
                        break
            filas.append({"sistema": name, "parametro": nom, "n_libres": len(lib),
                          "norma_r0": float(np.linalg.norm(r0)), "gamma": gam, "I_j": I,
                          "eps_j": eps, "eta_j": eta, "puntos_eps": npts, "parametros_nulos": ";".join(nulos),
                          "tstar_rel": ts_rel, "cruce_cert_menos": cruce[-1], "cruce_cert_mas": cruce[1],
                          "certificado_local": bool(math.isfinite(cruce[-1]) and math.isfinite(cruce[1])),
                          "certificado_rel": bool(npts > 0 and ts_rel < dlo and ts_rel < dhi), "tstar": ts, "tstar_lineal": ts_lin,
                          "d_menos": dlo, "d_mas": dhi,
                          "certificado": bool(npts > 0 and ts < dlo and ts < dhi),
                          "certificado_lineal": bool(ts_lin < dlo and ts_lin < dhi),
                          "clase_perfil": perf[nom]["clase"],
                          "clase_perfil_robusto": perf[nom]["clase_robusto"]})
        return filas
    except Exception as e:
        return [{"sistema": name, "error": repr(e)}]


if __name__ == "__main__":
    which = [a for a in sys.argv[1:] if not a.startswith("--")]
    nombres = which or sorted(p.stem for p in P.OUTD.glob("*.json"))
    with Pool(int(os.environ.get("NPROC", os.cpu_count() or 1))) as pool:
        res = [f for fs in pool.map(uno, nombres, chunksize=1) for f in fs]
    df = pd.DataFrame(res)
    out = P.OUTD.parent / os.environ.get("CERT_OUT", "certificado.csv")
    df.to_csv(out, index=False)
    print(df.to_string())
