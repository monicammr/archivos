#!/usr/bin/env python3
"""
Error relativo de la respuesta reducida (e_rel), junto a cos Δ, para los sistemas del artículo.

Mismo protocolo que la validación de cos Δ (certify_systems.py, scripts 04_robustez):
θ₀ = nominal de PEtab, 60 puntos en [1e-6, T], semilla 42, 15 escenarios por nivel,
θ = θ₀(1 + nivel·d), d ~ U(−1, 1); el modelo reducido sólo perturba los parámetros
seleccionados S (los demás quedan en θ₀).

Por escenario:
  Δx_full = x(θ) − x(θ₀),  Δx_sel = x(θ_S) − x(θ₀)
  cos Δ  = ⟨Δx_full, Δx_sel⟩ / (‖Δx_full‖ ‖Δx_sel‖)        (dirección)
  e_rel  = ‖Δx_full − Δx_sel‖ / ‖Δx_full‖                   (error relativo: dirección y tamaño)
  amp    = ‖Δx_sel‖ / ‖Δx_full‖                              (relación de amplitudes)

Relación demostrada en Lean (CosineCertificate.cos_lower_of_rel_error):
  e_rel ≤ ε  ⇒  cos Δ ≥ √(1 − ε²);  en particular e_rel ≤ 0.436 ⇒ cos Δ ≥ 0.90.
Lo contrario no vale: cos Δ alto no implica e_rel pequeño (la amplitud puede diferir).
"""
import sys, json, time
import numpy as np
import pandas as pd
from certify_systems import Sys, SYSTEMS, T_END_OVERRIDE, NIV_FIM, NIV_SCAN, N_ESCEN, SEED, OUT

NIVELES_INFORME = [0.01, 0.05, 0.10, 0.20, 0.50]
E_COS90 = float(np.sqrt(1 - 0.9 ** 2))      # 0.4359: e_rel ≤ esto ⇒ cos Δ ≥ 0.90


def analyze(name, sel, t_def, group):
    t0 = time.time()
    t_end = T_END_OVERRIDE.get(name, t_def)
    S = Sys(name, t_end)
    sel_idx = [S.names.index(q) for q in sel if q in S.names]
    y0 = S.sim(S.theta0)
    if y0 is None:
        return {"sistema": name, "error": "simulación nominal falló"}, []
    p = len(S.names)
    niveles = NIV_FIM if group == "FIM" else NIV_SCAN
    rng = np.random.default_rng(SEED)          # misma secuencia que la validación de cos Δ
    filas = []
    for nivel in niveles:
        for k in range(N_ESCEN):
            d = rng.uniform(-1, 1, size=p)
            if nivel not in NIVELES_INFORME:
                continue
            th_f = np.maximum(S.theta0 * (1 + nivel * d), 1e-12)
            th_s = S.theta0.copy(); th_s[sel_idx] = th_f[sel_idx]
            yf, ys = S.sim(th_f), S.sim(th_s)
            if yf is None or ys is None:
                continue
            df_, ds_ = (yf - y0).ravel(), (ys - y0).ravel()
            nf, ns = np.linalg.norm(df_), np.linalg.norm(ds_)
            if nf < max(1e-10 * np.linalg.norm(y0), 1e-6) or ns == 0:
                continue
            filas.append({"sistema": name, "nivel_%": int(round(100 * nivel)), "escenario": k,
                          "cos": float(df_ @ ds_ / (nf * ns)),
                          "e_rel": float(np.linalg.norm(df_ - ds_) / nf),
                          "amp": float(ns / nf)})
    res = {"sistema": name, "etapa": group, "T": t_end, "|S|": len(sel_idx), "p": p}
    df = pd.DataFrame(filas)
    for nv in NIVELES_INFORME:
        sub = df[df["nivel_%"] == int(round(100 * nv))] if len(df) else df
        if len(sub) == 0:
            continue
        tag = f"{int(round(100 * nv))}%"
        res[f"cos_med_{tag}"] = float(sub.cos.median())
        res[f"erel_med_{tag}"] = float(sub.e_rel.median())
        res[f"erel_p90_{tag}"] = float(sub.e_rel.quantile(0.9))
        res[f"amp_med_{tag}"] = float(sub.amp.median())
        res[f"erel<=0.10_{tag}"] = f"{int((sub.e_rel <= 0.10).sum())}/{len(sub)}"
        res[f"erel<=0.436_{tag}"] = f"{int((sub.e_rel <= E_COS90).sum())}/{len(sub)}"
    res["segundos"] = round(time.time() - t0, 1)
    return res, filas


if __name__ == "__main__":
    which = sys.argv[1:]
    out, todas = [], []
    for name, sel, t_def, group in SYSTEMS:
        if which and name not in which:
            continue
        print(f"== {name}", flush=True)
        try:
            r, filas = analyze(name, sel, t_def, group)
        except Exception as e:
            r, filas = {"sistema": name, "error": repr(e)}, []
        print(json.dumps(r, default=str), flush=True)
        out.append(r); todas += filas
        d = OUT / "erel"; d.mkdir(exist_ok=True)
        (d / f"{name}.json").write_text(json.dumps(r, default=str, indent=1))
        pd.DataFrame(filas).to_csv(d / f"{name}_escenarios.csv", index=False)
    if out and not which:
        pd.DataFrame(out).to_csv(OUT / "erel" / "resumen_erel.csv", index=False)
