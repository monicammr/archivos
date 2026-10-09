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

Con `--v3` (criterio por reestimación, el del artículo corregido):
  * admisible ⇔ |S| ≥ 2 y mediana de e_ajuste ≤ 0,436, donde e_ajuste es el error relativo tras
    reestimar los parámetros de S por mínimos cuadrados (mismo método que refit_systems.py);
    como e_ajuste ≤ e_rel, si e_rel ≤ 0,436 no hace falta reestimar para decidir;
  * Stage 1 no admisible → Stage 2, que para en cuanto el subconjunto es admisible;
  * se informan cos Δ y e_rel (sin reestimar) y e_ajuste (con reestimación).
Resultados en resultados/reclasificacion_v3/.

Con `--salidas` (junto con `--v3`; comentario 4 del revisor): en lugar de todos los estados x(t)
en [0, T], se usan las SALIDAS MEDIDAS de PEtab, y_i = h(g_i(x(t_i), θ))/σ_i, una por fila de
measurements.tsv (petab_outputs.PSys: condiciones experimentales, preequilibrio, observables,
transformación y ruido). J, R_var, el barrido, cos Δ, e_rel y e_ajuste se calculan sobre y.
Se procesan los 35 sistemas PEtab. Resultados en resultados/reclasificacion_salidas/.

Con `--poda` (junto con `--v3`; comentario 2): tras la selección voraz, eliminación hacia atrás
— se quita cada parámetro (del de menor E_j al de mayor) mientras el subconjunto siga siendo
admisible, hasta que no se pueda quitar ninguno. El subconjunto final es mínimo por inclusión
(ningún parámetro sobra), aunque no necesariamente de cardinalidad mínima global. Carpeta con
sufijo `_poda`.
"""
import sys, json, time
import numpy as np
import pandas as pd
from certify_systems import Sys, SYSTEMS, T_END_OVERRIDE, OUT

import os as _os
# Valores del artículo; se pueden cambiar por variables de entorno para el análisis de
# sensibilidad (comentario 6): RECL_DELTA, RECL_NIVEL y RECL_TAG (sufijo de la carpeta).
DELTA = float(_os.environ.get("RECL_DELTA", 0.01))   # paso de la linealización (δ = 0,01)
RVAR_MIN, KAPPA_MAX, VIF_MAX, COS_MIN = 0.89, 10.0, 10.0, 0.90
N_ESC, SEED = 15, 42
NIVEL = float(_os.environ.get("RECL_NIVEL", 0.05))   # perturbación de los escenarios (±5 %)
TAG = _os.environ.get("RECL_TAG", "")
EREL_MAX = float(np.sqrt(1 - COS_MIN ** 2))   # 0,436: e_rel ≤ esto ⇒ cos Δ ≥ 0,90 (Lean)
V3 = "--v3" in sys.argv          # criterio por reestimación (e_ajuste); implica las reglas de v2
V2 = ("--v2" in sys.argv) or V3
SALIDAS = "--salidas" in sys.argv
PODA = "--poda" in sys.argv       # eliminación hacia atrás tras la selección (comentario 2)
if SALIDAS:
    from petab_outputs import PSys as Sys   # misma interfaz; salidas medidas y = g(x, θ)


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


# --- paralelización (sistemas grandes): cada proceso carga su propia copia del modelo
import os
from multiprocessing import Pool
NPROC = int(os.environ.get("NPROC", os.cpu_count() or 1))
# paralelizar también sistemas con p ≤ 200 cuyas simulaciones son lentas (RECL_PARALELO=1)
PARALELO = os.environ.get("RECL_PARALELO") == "1"
_SY = None


_Y0 = None


def _w_init(name, t_end):
    global _SY, _Y0
    _SY = Sys(name, t_end)
    _Y0 = _SY.sim(_SY.theta0)


def _w_col(j):
    th0 = _SY.theta0
    tp, tm = th0.copy(), th0.copy()
    tp[j] *= 1 + DELTA; tm[j] *= 1 - DELTA
    yp, ym = _SY.sim(tp), _SY.sim(tm)
    if yp is None or ym is None:
        return j, None
    return j, (yp - ym).ravel() / (2 * DELTA)


def _w_scan(j):
    th0, y0 = _SY.theta0, _Y0
    tp = th0.copy(); tp[j] *= 1.1
    yp = _SY.sim(tp)
    return j, (float(np.linalg.norm((yp - y0).ravel())) if yp is not None and y0 is not None
               else 0.0)


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
    if (p > 200 or PARALELO) and NPROC > 1:
        # sistemas grandes: J en disco (float32) con registro de columnas hechas, para poder
        # reanudar tras una interrupción
        cdir = OUT / "cache"; cdir.mkdir(exist_ok=True)
        fJ, fm = cdir / f"{name}_J.npy", cdir / f"{name}_J_hechas.npy"
        if fJ.exists() and fm.exists():
            J = np.load(fJ, mmap_mode="r+"); hechas = np.load(fm)
        else:
            J = np.lib.format.open_memmap(fJ, mode="w+", dtype=np.float32, shape=(y0.size, p))
            hechas = np.zeros(p, dtype=bool)
        pend = [int(j) for j in act if not hechas[j]]
        print(f"  J: {int(hechas.sum())} columnas ya hechas, faltan {len(pend)}", flush=True)
        with Pool(NPROC, initializer=_w_init, initargs=(name, t_end)) as pool:
            for k, (j, col) in enumerate(pool.imap_unordered(_w_col, pend, chunksize=8)):
                if col is not None:
                    J[:, j] = col
                hechas[j] = True
                if k % 10 == 0:
                    J.flush(); np.save(fm, hechas)
                    print(f"  J: {int(hechas.sum())}/{len(act)} columnas", flush=True)
        J.flush(); np.save(fm, hechas)
        J = np.asarray(J, dtype=float) if J.nbytes < 4e9 else J
    else:
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
                "motivo": "Jacobiano nulo (ningún parámetro dinámico afecta a "
                          + ("las salidas medidas)" if SALIDAS else "los estados)"),
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

    from scipy.optimize import least_squares

    def ajuste(S):
        """Mediana de e_ajuste (reestimación de θ_S), como en refit_systems.py."""
        sgn = np.where(th0[S] < 0, -1.0, 1.0)
        mag0 = np.maximum(np.abs(th0[S]), 1e-12)
        lo, hi = np.log(mag0 / 10), np.log(mag0 * 10)
        es = []
        for th, df_ in zip(escen, full):
            if df_ is None or np.linalg.norm(df_) < umbral:
                continue
            nf = np.linalg.norm(df_)
            yf = y0.ravel() + df_

            def resid(u):
                ts = th0.copy(); ts[S] = sgn * np.exp(u)
                ys = Sy.sim(ts)
                return np.full(yf.size, 10.0) if ys is None else (ys.ravel() - yf) / nf
            ts = th0.copy(); ts[S] = th[S]
            r0 = resid(np.log(np.maximum(np.abs(th[S]), 1e-12)))
            mejor = float(np.linalg.norm(r0))
            x_esc = np.clip(np.log(np.maximum(np.abs(th[S]), 1e-12)), lo, hi)
            for x0 in (np.log(mag0), x_esc):
                try:
                    r = least_squares(resid, x0, bounds=(lo, hi), method="trf",
                                      max_nfev=100 * (len(S) + 1), diff_step=1e-3)
                    mejor = min(mejor, float(np.linalg.norm(r.fun)))
                except Exception:
                    pass
            es.append(mejor)
        return float(np.median(es)) if es else float("nan")

    memo_aj = {}

    def admisible3(S):
        """|S| ≥ 2 y e_ajuste ≤ 0,436 (sin reestimar si ya e_rel ≤ 0,436)."""
        if len(S) < 2:
            return False
        c, e, n = valida(S)
        if np.isfinite(e) and e <= EREL_MAX:
            return True
        key = tuple(S)
        if key not in memo_aj:
            memo_aj[key] = ajuste(S)
        return bool(np.isfinite(memo_aj[key]) and memo_aj[key] <= EREL_MAX)

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
        pasa1 = admisible3(S1) if V3 else ((not V2) or admisible(c, e))
    if pasa1:
        res.update({"etapa": "Stage 1", "S": res["S1"], "Rvar_%": 100 * rvar(S1),
                    "kappa": kappa(J, S1), "VIF": vif(J, S1), "cos_med": c, "erel_med": e,
                    "n_escenarios": n})
    else:
        if ok1:
            res["motivo_stage2"] = "Stage 1 cumple R_var pero no es admisible"
        # --- Stage 2: barrido empírico
        s = np.zeros(p)
        if (p > 200 or PARALELO) and NPROC > 1:
            cdir = OUT / "cache"; cdir.mkdir(exist_ok=True)
            fs, fsm = cdir / f"{name}_s.npy", cdir / f"{name}_s_hechas.npy"
            hs = np.zeros(p, dtype=bool)
            if fs.exists() and fsm.exists():
                s, hs = np.load(fs), np.load(fsm)
            pend = [int(j) for j in act if not hs[j]]
            with Pool(NPROC, initializer=_w_init, initargs=(name, t_end)) as pool:
                for k, (j, v) in enumerate(pool.imap_unordered(_w_scan, pend, chunksize=8)):
                    s[j] = v; hs[j] = True
                    if k % 10 == 0:
                        np.save(fs, s); np.save(fsm, hs)
                        print(f"  barrido: {int(hs.sum())}/{len(act)}", flush=True)
            np.save(fs, s); np.save(fsm, hs)
        else:
            for j in act:
                tp = th0.copy(); tp[j] *= 1.1
                yp = Sy.sim(tp)
                s[j] = np.linalg.norm((yp - y0).ravel()) if yp is not None else 0.0
        orden2 = [int(j) for j in act[np.argsort(-s[act])] if s[j] > 0]
        memo = {}
        def stop2(S):
            key = tuple(S)
            if V3:
                return admisible3(S)
            if key not in memo:
                memo[key] = valida(S)
            if V2:
                return len(S) >= 2 and admisible(memo[key][0], memo[key][1])
            return memo[key][0] >= COS_MIN
        S2, ok2 = greedy(J, orden2, stop2)
        c, e, n = (memo.get(tuple(S2)) or valida(S2)) if S2 else (float("nan"), float("nan"), 0)
        res.update({"etapa": "Stage 2", "S": [names[j] for j in S2],
                    "Rvar_%": 100 * rvar(S2) if S2 else 0.0,
                    "kappa": kappa(J, S2) if S2 else float("nan"),
                    "VIF": vif(J, S2) if S2 else float("nan"),
                    "cos_med": c, "erel_med": e, "n_escenarios": n})
    if PODA and V3:
        # --- poda (eliminación hacia atrás): se intenta quitar cada parámetro, del menos al
        # más influyente (E_j), mientras el subconjunto siga siendo admisible (|S| ≥ 2 y
        # e_ajuste ≤ 0,436); se repite hasta que no se pueda quitar ninguno. Resultado:
        # subconjunto mínimo por inclusión (Lean: Poda.prune_minimal).
        Sp = [names.index(q) for q in res["S"]]
        res["S_antes_poda"] = list(res["S"])
        if admisible3(Sp):
            cambio = True
            while cambio:
                cambio = False
                for j in sorted(Sp, key=lambda k: E[k]):
                    sub = [k for k in Sp if k != j]
                    if admisible3(sub):
                        Sp = sub
                        cambio = True
                        break
            c, e, n = valida(Sp)
            res.update({"S": [names[j] for j in Sp], "Rvar_%": 100 * rvar(Sp),
                        "kappa": kappa(J, Sp), "VIF": vif(J, Sp),
                        "cos_med": c, "erel_med": e, "n_escenarios": n})
        res["podados"] = [q for q in res["S_antes_poda"] if q not in res["S"]]
    res["admisible"] = admisible(res["cos_med"], res["erel_med"]) and \
        (not V2 or len(res["S"]) >= 2)
    if V3:
        Sf = [names.index(q) for q in res["S"]]
        if tuple(Sf) in memo_aj:
            # ya calculado al decidir la parada (también en sistemas grandes)
            res["eajuste_med"] = memo_aj[tuple(Sf)]
        elif len(Sf) >= 1 and (p <= 200 or len(Sf) <= 10):
            res["eajuste_med"] = ajuste(Sf)
        else:
            # sistemas muy grandes: cota e_ajuste ≤ e_rel (el punto sin reestimar es candidato)
            res["eajuste_med"] = None
            res["eajuste_cota"] = res["erel_med"]
        e_aj = res["eajuste_med"] if res["eajuste_med"] is not None else res["erel_med"]
        res["admisible"] = bool(len(Sf) >= 2 and np.isfinite(e_aj) and
                                min(e_aj, res["erel_med"]) <= EREL_MAX)
    res["segundos"] = round(time.time() - t0, 1)
    return res


if __name__ == "__main__":
    if "--bench" in sys.argv:
        import certify_systems as _CS
        from pathlib import Path as _P
        _i = sys.argv.index("--bench")
        _CS.BENCH = _P(sys.argv[_i + 1])
        del sys.argv[_i:_i + 2]
    which = [a for a in sys.argv[1:] if not a.startswith("--")]
    d = OUT / (("reclasificacion_salidas" if SALIDAS else "reclasificacion_v3" if V3 else "reclasificacion_v2" if V2 else "reclasificacion")
               + ("_poda" if PODA else "") + (f"_{TAG}" if TAG else ""))
    d.mkdir(exist_ok=True)
    out = []
    lista = [(n, sel, t, "FIM" if g == "FIM" else "SCAN", None) for n, sel, t, g in SYSTEMS]
    if "--extra" in sys.argv:
        lista = [(n, [], 50.0, None, cat) for n, cat in EXTRA]
    elif SALIDAS:
        lista += [(n, [], 50.0, None, cat) for n, cat in EXTRA]
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
