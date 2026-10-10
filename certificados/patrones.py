#!/usr/bin/env python3
"""
Patrones de robustez A–D con el método final (salidas medidas, S biológico + calibración, poda).

Para cada sistema admisible de resultados/reclasificacion_salidas_bio_poda/, con su S FIJO
(más los parámetros de calibración, que se reajustan siempre), se evalúa la fidelidad al
aumentar la perturbación: niveles ±1, 5, 10, 20, 30, 40, 50 %, 15 escenarios por nivel
(semilla 42 en cada nivel, de modo que ±5 % reproduce los escenarios de la selección), θ = θ₀(1 + nivel·u), u ~ U(−1, 1). Por escenario: cos Δ, e_rel (sin reajuste) y
e_ajuste (reajuste no lineal de S ∪ C, mínimos cuadrados en log|θ|, límites [|θ₀|/10, 10|θ₀|],
partiendo del valor del escenario y de θ₀).

Clasificación (sobre la mediana de e_ajuste por nivel, umbral τ_e = 0,436):
  A  admisible en todos los niveles (robusto hasta ±50 %);
  B  admisible hasta un nivel ≥ ±20 % y después deja de serlo y no se recupera (colapso);
  C  irregular: deja de ser admisible y vuelve a serlo a un nivel mayor (no monótono);
  D  deja de ser admisible ya a ±10 % o menos (frágil / dependiente del escenario).
Se informa además la dispersión (rango intercuartílico) de e_ajuste por nivel.

Uso: python3 patrones.py [Sistema ...]  → resultados/patrones/<sistema>.json, PATRONES.md
"""
import sys, json, time, os, warnings
from pathlib import Path
from multiprocessing import Pool
import numpy as np
from scipy.optimize import least_squares

warnings.filterwarnings("ignore")
import petab_outputs as PO

HERE = Path(__file__).resolve().parent
SEL = HERE / "resultados" / "reclasificacion_salidas_bio_poda"
OUTD = HERE / "resultados" / "patrones"
NIVELES = [0.01, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50]
N_ESC, SEED = 15, 42
EMAX = float(np.sqrt(1 - 0.9 ** 2))
EXCLUIR = {"Chen_MSB2009"}          # 35 s por simulación: inviable para 7 × 15 reajustes


def uno(name):
    t0 = time.time()
    info = json.loads((SEL / f"{name}.json").read_text())
    Sy = PO.PSys(name)
    th0 = Sy.theta0
    p = len(th0)
    idx = [Sy.names.index(q) for q in info["S"] + info.get("calibracion", []) if q in Sy.names]
    y0 = Sy.sim(th0).ravel()
    umbral = max(1e-10 * np.linalg.norm(y0), 1e-6)
    sgn = np.where(th0[idx] < 0, -1.0, 1.0)
    mag0 = np.maximum(np.abs(th0[idx]), 1e-12)
    lo, hi = np.log(mag0 / 10), np.log(mag0 * 10)
    res = {"sistema": name, "S": info["S"], "n_calibracion": len(info.get("calibracion", [])),
           "niveles": {}}
    for nivel in NIVELES:
        cs, es, fs = [], [], []
        rng = np.random.default_rng(SEED)   # misma semilla por nivel: ±5 % = escenarios de la selección
        for _ in range(N_ESC):
            th = np.maximum(th0 * (1 + nivel * rng.uniform(-1, 1, size=p)), 1e-12)
            yf = Sy.sim(th)
            if yf is None:
                continue
            d = yf.ravel() - y0
            nf = np.linalg.norm(d)
            if nf < umbral:
                continue
            ts = th0.copy(); ts[idx] = th[idx]
            ys = Sy.sim(ts)
            if ys is None:
                continue
            ds = ys.ravel() - y0
            ns = np.linalg.norm(ds)
            cs.append(float(d @ ds / (nf * ns)) if ns > 0 else 0.0)
            er = float(np.linalg.norm(d - ds) / nf)
            es.append(er)

            def resid(u):
                t = th0.copy(); t[idx] = sgn * np.exp(u)
                y = Sy.sim(t)
                return np.full(d.size, 10.0) if y is None else (y.ravel() - yf.ravel()) / nf
            mejor = er
            for x0 in (np.clip(np.log(np.maximum(np.abs(th[idx]), 1e-12)), lo, hi), np.log(mag0)):
                try:
                    r = least_squares(resid, x0, bounds=(lo, hi), method="trf",
                                      max_nfev=100 * (len(idx) + 1), diff_step=1e-3)
                    mejor = min(mejor, float(np.linalg.norm(r.fun)))
                except Exception:
                    pass
            fs.append(mejor)
        q = lambda v, k: float(np.percentile(v, k)) if v else float("nan")
        res["niveles"][f"{int(round(100 * nivel))}"] = {
            "n": len(fs), "cos_med": q(cs, 50), "erel_med": q(es, 50),
            "eaj_med": q(fs, 50), "eaj_q25": q(fs, 25), "eaj_q75": q(fs, 75)}
    ok = [res["niveles"][k]["eaj_med"] <= EMAX for k in res["niveles"]
          if np.isfinite(res["niveles"][k]["eaj_med"])]
    niv = [NIVELES[i] for i in range(len(ok))]
    if all(ok):
        pat = "A"
    else:
        f = ok.index(False)
        recupera = any(ok[f:])
        if recupera:
            pat = "C"
        elif niv[f] >= 0.20:
            pat = "B"
        else:
            pat = "D"
    res["patron"] = pat
    res["segundos"] = round(time.time() - t0, 1)
    return res


def _seguro(name):
    try:
        r = uno(name)
    except Exception as e:
        r = {"sistema": name, "error": repr(e)}
    OUTD.mkdir(parents=True, exist_ok=True)
    (OUTD / f"{name}.json").write_text(json.dumps(r, indent=1))
    print(json.dumps({k: r.get(k) for k in ("sistema", "patron", "error", "segundos")}),
          flush=True)


def resumen():
    rs = [json.loads(p.read_text()) for p in sorted(OUTD.glob("*.json"))]
    L = ["# Patrones de robustez con el método final", "",
         "Mediana de e_ajuste (S biológico + calibración, reajustados) frente al tamaño de la "
         "perturbación; ✓ = ≤ 0,436. A: robusto hasta ±50 %; B: colapso a partir de ±20 % o más; "
         "C: irregular (deja de cumplir y vuelve a cumplir); D: falla ya a ±10 % o menos.", "",
         "| Sistema | k | " + " | ".join(f"±{int(100 * n)}%" for n in NIVELES) + " | Patrón |",
         "|---|---|" + "---|" * len(NIVELES) + "---|"]
    cuenta = {}
    for r in rs:
        if "error" in r:
            continue
        celdas = []
        for n in NIVELES:
            v = r["niveles"].get(str(int(round(100 * n))), {}).get("eaj_med", float("nan"))
            celdas.append("—" if not np.isfinite(v) else f"{100 * v:.0f}%{' ✓' if v <= EMAX else ''}")
        cuenta[r["patron"]] = cuenta.get(r["patron"], 0) + 1
        L.append(f"| {r['sistema']} | {len(r['S'])} | " + " | ".join(celdas) +
                 f" | **{r['patron']}** |")
    L += ["", "Recuento: " + ", ".join(f"{k}: {v}" for k, v in sorted(cuenta.items())) + "."]
    (OUTD / "PATRONES.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    if "--resumen" in sys.argv:
        resumen(); sys.exit()
    nombres = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not nombres:
        for f in sorted(SEL.glob("*.json")):
            d = json.loads(f.read_text())
            if d.get("admisible") and f.stem not in EXCLUIR and \
                    not (OUTD / f"{f.stem}.json").exists():
                nombres.append(f.stem)
    with Pool(int(os.environ.get("NPROC", 3))) as pool:
        list(pool.imap_unordered(_seguro, nombres))
    resumen()
