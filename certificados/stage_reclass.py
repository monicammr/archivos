#!/usr/bin/env python3
"""
Reclasificación Stage 1 / Stage 2 con la regla escrita en el artículo (secciones 2.3–2.5) y
sensibilidad RELATIVA (J_rel = θ·∂x/∂θ = ∂x/∂log θ).

Selección secuencial (2.3): candidatos en orden descendente; para cada candidato j se calcula
κ y VIF de S ∪ {j} (columnas estandarizadas, mismas funciones que el pipeline
`petab_V9_todos35.py`); si ambos ≤ 10 se acepta, si no se descarta para siempre; se para al
cumplir el criterio de la etapa o al agotar candidatos.

Stage 1 (2.4): orden por E_j = ‖J_rel,j‖²; criterio R_var(S) = Σ_{j∈S} E_j / tr(J_relᵀJ_rel) ≥ 0,89
y |S| ≥ 2.
Stage 2 (2.5): se activa si Stage 1 falla. Orden por s_j = ‖x(θ₀ + 0,1 θ₀ⱼ eⱼ) − x(θ₀)‖; mismo
filtro κ/VIF; criterio: mediana de cos Δ ≥ 0,90 en 15 escenarios a ±5 %.
Validación (ambas etapas): admisible si mediana cos Δ ≥ 0,90. Se informa también e_rel.

Simulación: igual que la validación de cos Δ (RoadRunner, 60 puntos en [1e-6, T]).

Con `--v2` (reglas completas propuestas):
  * admisible ⇔ mediana cos Δ ≥ 0,90 **y** mediana e_rel ≤ √(1 − 0,9²) ≈ 0,436;
  * si el subconjunto de Stage 1 cumple R_var pero no es admisible, se pasa a Stage 2;
  * Stage 2 para cuando |S| ≥ 2 y el subconjunto es admisible.
Resultados en resultados/reclasificacion_v2/.
"""
import sys, json, time
import numpy as np
import pandas as pd
from certify_systems import Sys, SYSTEMS, T_END_OVERRIDE, OUT

DELTA = 0.01          # paso de la linealización (artículo: δ = 0,01)
RVAR_MIN, KAPPA_MAX, VIF_MAX, COS_MIN = 0.89, 10.0, 10.0, 0.90
N_ESC, NIVEL, SEED = 15, 0.05, 42
EREL_MAX = float(np.sqrt(1 - COS_MIN ** 2))   # 0,436: e_rel ≤ esto ⇒ cos Δ ≥ 0,90 (Lean)
V2 = "--v2" in sys.argv


# --- κ y VIF: mismas definiciones que petab_V9_todos35.py --------------------------------------
def _standardize(X):
    mu = X.mean(axis=0, keepdims=True)
    sd = X.std(axis=0, ddof=1, keepdims=True)
    sd = np.where(~np.isfinite(sd) | (sd < 1e-12), 1.0, sd)
    return np.nan_to_num((X - mu) / sd)


def kappa(J, idx):
    if len(idx) <= 1:
        return 1.0
    F = _standardize(J[:, idx])
    if np.allclose(F, 0):
        return float("inf")
    s = np.linalg.svd(F, compute_uv=False)
    return float("inf") if s[-1] < 1e-12 else float(s[0] / s[-1])


def vif(J, idx):
    if len(idx) <= 1:
        return 1.0
    F = _standardize(J[:, idx])
    C = np.nan_to_num(np.corrcoef(F, rowvar=False))
    np.fill_diagonal(C, 1.0)
    try:
        inv = np.linalg.inv(C)
    except np.linalg.LinAlgError:
        inv = np.linalg.pinv(C)
    v = np.diag(inv)
    return float(np.max(np.where(np.isfinite(v), v, np.inf)))


def greedy(J, order, stop):
    """Selección secuencial con descarte permanente; `stop(S)` es el criterio de la etapa."""
    S, hist = [], []
    for j in order:
        k, v = kappa(J, S + [j]), vif(J, S + [j])
        if k <= KAPPA_MAX and v <= VIF_MAX:
            S.append(j)
            hist.append(j)
            if stop(S):
                return S, True
    return S, False


# Los 12 sistemas PEtab restantes del artículo (35 en total; más SCT Bandura = 36)
EXTRA = [
    ("Isensee_JCB2018", "Parcial"), ("Alkan_SciSignal2018", "No admisible"),
    ("Bruno_JExpBot2016", "No admisible"), ("Beer_MolBioSystems2014", "Técnico"),
    ("Bertozzi_PNAS2020", "Técnico"), ("Fujita_SciSignal2010", "Técnico"),
    ("Laske_PLOSComputBiol2019", "Técnico"), ("Liu_IFACPapersOnLine2025", "Técnico"),
    ("Lucarelli_CellSystems2018", "Técnico"), ("Oliveira_NatCommun2021", "Técnico"),
    ("Perelson_Science1996", "Técnico"), ("Schwen_PONE2014", "Técnico"),
]


def admisible(c, e):
    ok = np.isfinite(c) and c >= COS_MIN
    if V2:
        ok = ok and np.isfinite(e) and e <= EREL_MAX
    return bool(ok)


def main_one(name, t_def):
    t0 = time.time()
    t_end = T_END_OVERRIDE.get(name, t_def)
    Sy = Sys(name, t_end)
    names, th0 = Sy.names, Sy.theta0
    p = len(names)
    y0 = Sy.sim(th0)
    if y0 is None:
        return {"sistema": name, "etapa": "Técnico", "motivo": "la simulación nominal falla",
                "admisible": False}
    act = np.nonzero(Sy.in_model)[0]
    # --- J relativa por diferencias centradas en log θ
    J = np.zeros((y0.size, p))
    for j in act:
        tp, tm = th0.copy(), th0.copy()
        tp[j] *= 1 + DELTA; tm[j] *= 1 - DELTA
        yp, ym = Sy.sim(tp), Sy.sim(tm)
        if yp is not None and ym is not None:
            J[:, j] = (yp - ym).ravel() / (2 * DELTA)
    E = np.sum(J ** 2, axis=0)
    tot = float(E.sum())
    if not tot > 0:
        return {"sistema": name, "p": p, "T": t_end, "etapa": "Técnico",
                "motivo": "Jacobiano nulo (ningún parámetro dinámico afecta a los estados)",
                "admisible": False}
    rvar = lambda S: float(E[S].sum() / tot) if tot > 0 else float("nan")
    # --- escenarios de validación (±5 %)
    rng = np.random.default_rng(SEED)
    escen = [np.maximum(th0 * (1 + NIVEL * rng.uniform(-1, 1, size=p)), 1e-12)
             for _ in range(N_ESC)]
    full = []
    for th in escen:
        yf = Sy.sim(th)
        full.append(None if yf is None else (yf - y0).ravel())
    umbral = max(1e-10 * np.linalg.norm(y0), 1e-6)

    def valida(S):
        cs, es = [], []
        for th, df_ in zip(escen, full):
            if df_ is None or np.linalg.norm(df_) < umbral:
                continue
            ts = th0.copy(); ts[S] = th[S]
            ys = Sy.sim(ts)
            if ys is None:
                continue
            ds_ = (ys - y0).ravel()
            nf, ns = np.linalg.norm(df_), np.linalg.norm(ds_)
            if ns == 0:
                cs.append(0.0); es.append(1.0); continue
            cs.append(float(df_ @ ds_ / (nf * ns)))
            es.append(float(np.linalg.norm(df_ - ds_) / nf))
        if not cs:
            return float("nan"), float("nan"), 0
        return float(np.median(cs)), float(np.median(es)), len(cs)

    res = {"sistema": name, "p": p, "T": t_end}
    # --- Stage 1
    orden1 = [int(j) for j in act[np.argsort(-E[act])] if E[j] > 0]
    S1, ok1 = greedy(J, orden1, lambda S: rvar(S) >= RVAR_MIN and len(S) >= 2)
    res.update({"S1": [names[j] for j in S1], "Rvar_S1_%": 100 * rvar(S1) if S1 else 0.0,
                "S1_cumple": ok1})
    pasa1 = False
    if ok1:
        c, e, n = valida(S1)
        res.update({"cos_S1": c, "erel_S1": e})
        pasa1 = (not V2) or admisible(c, e)
    if pasa1:
        res.update({"etapa": "Stage 1", "S": res["S1"], "Rvar_%": 100 * rvar(S1),
                    "kappa": kappa(J, S1), "VIF": vif(J, S1), "cos_med": c, "erel_med": e,
                    "n_escenarios": n})
    else:
        if ok1:
            res["motivo_stage2"] = "Stage 1 cumple R_var pero no es admisible"
        # --- Stage 2: barrido empírico
        s = np.zeros(p)
        for j in act:
            tp = th0.copy(); tp[j] *= 1.1
            yp = Sy.sim(tp)
            s[j] = np.linalg.norm((yp - y0).ravel()) if yp is not None else 0.0
        orden2 = [int(j) for j in act[np.argsort(-s[act])] if s[j] > 0]
        memo = {}
        def stop2(S):
            key = tuple(S)
            if key not in memo:
                memo[key] = valida(S)
            if V2:
                return len(S) >= 2 and admisible(memo[key][0], memo[key][1])
            return memo[key][0] >= COS_MIN
        S2, ok2 = greedy(J, orden2, stop2)
        c, e, n = memo.get(tuple(S2), valida(S2)) if S2 else (float("nan"), float("nan"), 0)
        res.update({"etapa": "Stage 2", "S": [names[j] for j in S2],
                    "Rvar_%": 100 * rvar(S2) if S2 else 0.0,
                    "kappa": kappa(J, S2) if S2 else float("nan"),
                    "VIF": vif(J, S2) if S2 else float("nan"),
                    "cos_med": c, "erel_med": e, "n_escenarios": n})
    res["admisible"] = admisible(res["cos_med"], res["erel_med"]) and \
        (not V2 or len(res["S"]) >= 2)
    res["segundos"] = round(time.time() - t0, 1)
    return res


if __name__ == "__main__":
    which = [a for a in sys.argv[1:] if not a.startswith("--")]
    d = OUT / ("reclasificacion_v2" if V2 else "reclasificacion"); d.mkdir(exist_ok=True)
    out = []
    lista = [(n, sel, t, "FIM" if g == "FIM" else "SCAN", None) for n, sel, t, g in SYSTEMS]
    if "--extra" in sys.argv:
        lista = [(n, [], 50.0, None, cat) for n, cat in EXTRA]
    for name, sel, t_def, group, cat in lista:
        if which and name not in which:
            continue
        print(f"== {name}", flush=True)
        try:
            r = main_one(name, t_def)
        except Exception as ex:
            r = {"sistema": name, "error": repr(ex)}
        r["etapa_paper"] = cat if cat else ("Stage 1" if group == "FIM" else "Stage 2")
        r["S_paper"] = sel
        print(json.dumps(r, default=str), flush=True)
        (d / f"{name}.json").write_text(json.dumps(r, default=str, indent=1))
        out.append(r)
    if out and not which:
        nombre = "resumen_extra.csv" if "--extra" in sys.argv else "resumen_reclasificacion.csv"
        pd.DataFrame(out).to_csv(d / nombre, index=False)
