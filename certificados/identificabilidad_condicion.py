#!/usr/bin/env python3
"""
¿Predice una condición local calculable la identificabilidad práctica observada en los perfiles?

En el mínimo θ̂ del modelo reducido (resultados/identificabilidad/perfil/<p>/minimo.npz) se calcula
la matriz de sensibilidad J = ∂r/∂log θ de los residuos escalados por el ruido (r = y/σ − dato/σ)
respecto de los parámetros libres S ∪ Θ_C (diferencias centradas, δ = 0,01), y:
  * s       — menor valor singular de J (información en la dirección más débil, unidades de ruido);
  * w_j     — semiancho lineal (Wald) del intervalo del 95 % de log θ_j: √(3,84·[(JᵀJ)⁻¹]_jj);
  * ‖r₀‖    — √χ² en el mínimo;
  * no lin. — para cada j, cociente entre el Δχ² observado en el primer punto del perfil y el
              predicho por la aproximación cuadrática (δ²/[(JᵀJ)⁻¹]_jj).
Predicción lineal: j es identificable si su intervalo de Wald cabe dentro de los límites del
estudio a ambos lados (w_j < distancia de log θ̂_j a log(|θ₀|/10) y a log(10|θ₀|)).
Se compara con la clase observada en el perfil.

Uso: python identificabilidad_condicion.py [Problema ...]
Salida: resultados/identificabilidad/condicion.csv
"""
import sys, json, math, os
from multiprocessing import Pool

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(v, "1")
import numpy as np
import pandas as pd
import identificabilidad_perfil as P

D = 0.01


def uno(name):
    try:
        d = P.prep(name)
        S = d["S"]
        m = np.load(P.f_min(name))
        th = m["theta"]
        fil = d["filas"]

        def r(t):
            z = S.z(t)
            return None if z is None else z[fil] - d["zd"][fil]
        r0 = r(th)
        J = np.zeros((r0.size, len(d["libres"])))
        for k, j in enumerate(d["libres"]):
            tp, tm = th.copy(), th.copy()
            tp[j] *= math.exp(D); tm[j] *= math.exp(-D)
            rp, rm = r(tp), r(tm)
            J[:, k] = np.nan if rp is None or rm is None else (rp - rm) / (2 * D)
        J = np.nan_to_num(J)
        sv = np.linalg.svd(J, compute_uv=False)
        C = np.linalg.pinv(J.T @ J)
        perf = {p["parametro"]: p for p in json.loads((P.OUTD / f"{name}.json").read_text())["perfiles"]}
        filas = []
        for k, j in enumerate(d["sel"]):
            nom = S.names[j]
            var = max(C[k, k], 1e-300)
            w = math.sqrt(P.UMBRAL * var)
            t0 = math.log(max(abs(S.theta0[j]), 1e-300)); u = math.log(max(abs(th[j]), 1e-300))
            dist = min(u - (t0 - math.log(10)), (t0 + math.log(10)) - u)
            # no linealidad: primer punto válido del perfil (lado derecho e izquierdo)
            nl = []
            for lado in (-1, 1):
                for i in range(len(P.DESPL)):
                    f = P.f_pto(name, nom, lado, i)
                    if f.exists():
                        p = json.loads(f.read_text(encoding="utf-8"))
                        if P.dentro(d, p) and p["dchi2"] < P.FALLO:
                            pred = p["despl"] ** 2 / var
                            nl.append(p["dchi2"] / pred if pred > 0 else float("nan"))
                            break
            filas.append({"sistema": name, "parametro": nom, "n_libres": len(d["libres"]),
                          "s_min": float(sv[-1]), "s_max": float(sv[0]),
                          "norma_r0": float(np.linalg.norm(r0)), "chi2_por_gl": float(r0 @ r0) / max(r0.size - len(d["libres"]), 1),
                          "wald_semiancho_log": w, "dist_limite_log": dist,
                          "prediccion_lineal": "identificable" if w < dist else "no",
                          "cociente_no_lineal": float(np.nanmean(nl)) if nl else float("nan"),
                          "clase_perfil": perf[nom]["clase"], "clase_perfil_robusto": perf[nom]["clase_robusto"]})
        return filas
    except Exception as e:
        return [{"sistema": name, "error": repr(e)}]


if __name__ == "__main__":
    which = [a for a in sys.argv[1:] if not a.startswith("--")]
    nombres = which or sorted(p.stem for p in P.OUTD.glob("*.json"))
    with Pool(os.cpu_count()) as pool:
        res = [f for fs in pool.map(uno, nombres) for f in fs]
    df = pd.DataFrame(res)
    df.to_csv(P.OUTD.parent / "condicion.csv", index=False)
    print(df.to_string())
