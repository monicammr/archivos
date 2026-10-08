#!/usr/bin/env python3
"""
Minimalidad del subconjunto seleccionado (comentario 2 del revisor), sobre SALIDAS MEDIDAS.

Para cada sistema admisible de resultados/reclasificacion_salidas/ (S, |S| ≥ 2):
  1. Quitar uno: para cada j ∈ S, ¿es admisible S \\ {j}? (mismo criterio: mediana de
     e_ajuste ≤ 0,436, sin exigir |S| ≥ 2). Si ninguno lo es, S es mínimo por inclusión
     (1-mínimo): no sobra ningún parámetro.
  2. Un solo parámetro: para los K = 10 parámetros de mayor energía E_j = ‖J_rel,j‖² y los
     K de mayor efecto en el barrido s_j, ¿es admisible {j}? Si ninguno lo es, no hay un
     subconjunto de un parámetro (entre los más influyentes) que reproduzca la respuesta.
Mismo protocolo que stage_reclass.py --v3 --salidas: 15 escenarios a ±5 % (semilla 42),
reestimación por mínimos cuadrados en log|θ| con límites [|θ₀|/10, 10|θ₀|] desde dos puntos de
partida; si e_rel ≤ 0,436 no hace falta reestimar.

Nota: el algoritmo voraz no garantiza el mínimo global (problema combinatorio); estas pruebas
establecen minimalidad por inclusión y descartan subconjuntos de tamaño 1 entre los candidatos
más influyentes.

Uso: python3 minimalidad.py [Sistema ...]   → resultados/minimalidad/<sistema>.json, RESUMEN.md
"""
import sys, json, time, os, warnings
from pathlib import Path
from multiprocessing import Pool
import numpy as np
from scipy.optimize import least_squares

warnings.filterwarnings("ignore")
import petab_outputs as PO

HERE = Path(__file__).resolve().parent
SUBS = HERE / "resultados" / "reclasificacion_salidas"
OUTD = HERE / "resultados" / "minimalidad"
EMAX = float(np.sqrt(1 - 0.9 ** 2))
N_ESC, NIVEL, SEED, DELTA, K = 15, 0.05, 42, 0.01, 10


class Evaluador:
    def __init__(self, name):
        self.S = PO.PSys(name)
        th0 = self.th0 = self.S.theta0
        self.y0 = self.S.sim(th0).ravel()
        p = len(th0)
        rng = np.random.default_rng(SEED)
        self.escen = [np.maximum(th0 * (1 + NIVEL * rng.uniform(-1, 1, size=p)), 1e-12)
                      for _ in range(N_ESC)]
        umbral = max(1e-10 * np.linalg.norm(self.y0), 1e-6)
        self.full = []
        for th in self.escen:
            yf = self.S.sim(th)
            d = None if yf is None else yf.ravel() - self.y0
            self.full.append(d if d is not None and np.linalg.norm(d) >= umbral else None)

    def erel(self, idx):
        es = []
        for th, d in zip(self.escen, self.full):
            if d is None:
                continue
            ts = self.th0.copy(); ts[idx] = th[idx]
            ys = self.S.sim(ts)
            if ys is None:
                continue
            es.append(np.linalg.norm(d - (ys.ravel() - self.y0)) / np.linalg.norm(d))
        return float(np.median(es)) if es else float("nan")

    def eajuste(self, idx):
        th0 = self.th0
        sgn = np.where(th0[idx] < 0, -1.0, 1.0)
        mag0 = np.maximum(np.abs(th0[idx]), 1e-12)
        lo, hi = np.log(mag0 / 10), np.log(mag0 * 10)
        es = []
        for th, d in zip(self.escen, self.full):
            if d is None:
                continue
            nf = np.linalg.norm(d)
            yf = self.y0 + d

            def resid(u):
                ts = th0.copy(); ts[idx] = sgn * np.exp(u)
                ys = self.S.sim(ts)
                return np.full(yf.size, 10.0) if ys is None else (ys.ravel() - yf) / nf

            mejor = float(np.linalg.norm(resid(np.log(np.maximum(np.abs(th[idx]), 1e-12)))))
            for x0 in (np.log(mag0), np.clip(np.log(np.maximum(np.abs(th[idx]), 1e-12)), lo, hi)):
                try:
                    r = least_squares(resid, x0, bounds=(lo, hi), method="trf",
                                      max_nfev=100 * (len(idx) + 1), diff_step=1e-3)
                    mejor = min(mejor, float(np.linalg.norm(r.fun)))
                except Exception:
                    pass
            es.append(mejor)
        return float(np.median(es)) if es else float("nan")

    def admisible(self, idx):
        """(admisible, e_rel, e_ajuste) con el criterio e_ajuste ≤ 0,436."""
        e = self.erel(idx)
        if np.isfinite(e) and e <= EMAX:
            return True, e, None
        a = self.eajuste(idx)
        return bool(np.isfinite(a) and a <= EMAX), e, a


def uno(name):
    t0 = time.time()
    info = json.loads((SUBS / f"{name}.json").read_text())
    ev = Evaluador(name)
    Sy = ev.S
    S = [Sy.names.index(q) for q in info["S"] if q in Sy.names]
    res = {"sistema": name, "S": info["S"], "etapa": info.get("etapa")}
    # 1. quitar uno
    quitar = []
    for j in S:
        sub = [k for k in S if k != j]
        ok, e, a = ev.admisible(sub)
        quitar.append({"sin": Sy.names[j], "admisible": ok, "e_rel": e, "e_ajuste": a})
    res["quitar_uno"] = quitar
    res["minimo_por_inclusion"] = not any(q["admisible"] for q in quitar)
    # 2. un solo parámetro: K de mayor energía y K de mayor barrido
    act = [int(j) for j in np.nonzero(Sy.in_model)[0]]
    E, s = np.zeros(len(ev.th0)), np.zeros(len(ev.th0))
    for j in act:
        tp, tm = ev.th0.copy(), ev.th0.copy()
        tp[j] *= 1 + DELTA; tm[j] *= 1 - DELTA
        yp, ym = Sy.sim(tp), Sy.sim(tm)
        if yp is not None and ym is not None:
            E[j] = float(np.sum(((yp - ym).ravel() / (2 * DELTA)) ** 2))
        t1 = ev.th0.copy(); t1[j] *= 1.1
        y1 = Sy.sim(t1)
        s[j] = float(np.linalg.norm(y1.ravel() - ev.y0)) if y1 is not None else 0.0
    cand = []
    for orden in (np.argsort(-E), np.argsort(-s)):
        for j in orden[:K]:
            if int(j) in act and int(j) not in cand and (E[j] > 0 or s[j] > 0):
                cand.append(int(j))
    solos = []
    for j in cand:
        ok, e, a = ev.admisible([j])
        solos.append({"parametro": Sy.names[j], "admisible": ok, "e_rel": e, "e_ajuste": a})
    res["un_parametro"] = solos
    res["algun_parametro_solo_basta"] = any(x["admisible"] for x in solos)
    res["segundos"] = round(time.time() - t0, 1)
    return res


def _seguro(name):
    try:
        r = uno(name)
    except Exception as e:
        r = {"sistema": name, "error": repr(e)}
    OUTD.mkdir(parents=True, exist_ok=True)
    (OUTD / f"{name}.json").write_text(json.dumps(r, indent=1, default=str))
    print(json.dumps({k: r.get(k) for k in ("sistema", "minimo_por_inclusion",
                                            "algun_parametro_solo_basta", "error",
                                            "segundos")}), flush=True)
    return r


def resumen():
    rs = [json.loads(p.read_text()) for p in sorted(OUTD.glob("*.json"))]
    ok = [r for r in rs if "error" not in r]
    pct = lambda x: "—" if x is None or not np.isfinite(x) else f"{100 * x:.1f} %"
    L = ["# Minimalidad del subconjunto (comentario 2)", "",
         "Criterio en todas las pruebas: mediana de e_ajuste ≤ 43,6 % (equivale a cos Δ ≥ 0,9 "
         "tras reajustar, demostrado en Lean). Sobre las salidas medidas de PEtab.", "",
         "| Sistema | |S| | ¿Sobra algún parámetro? (quitar uno) | Mejor e_ajuste al quitar uno | "
         "¿Basta un solo parámetro? (de los más influyentes) | Mejor e_ajuste con uno solo |",
         "|---|---|---|---|---|---|"]
    n_min = n_uno = 0
    for r in ok:
        best = lambda xs: min([x["e_ajuste"] if x["e_ajuste"] is not None else x["e_rel"]
                               for x in xs] or [np.nan])
        n_min += r["minimo_por_inclusion"]
        n_uno += r["algun_parametro_solo_basta"]
        sobra = [q["sin"] for q in r["quitar_uno"] if q["admisible"]]
        basta = [x["parametro"] for x in r["un_parametro"] if x["admisible"]]
        L.append(f"| {r['sistema']} | {len(r['S'])} | "
                 f"{'no' if not sobra else 'sí: ' + ', '.join(sobra)} | "
                 f"{pct(best(r['quitar_uno']))} | "
                 f"{'no' if not basta else 'sí: ' + ', '.join(basta)} | "
                 f"{pct(best(r['un_parametro']))} |")
    L += ["", f"* Mínimos por inclusión (no sobra ningún parámetro): {n_min} de {len(ok)}.",
          f"* Sistemas donde un solo parámetro bastaría: {n_uno} de {len(ok)}."]
    if len(rs) > len(ok):
        L += [f"* Errores: {', '.join(r['sistema'] for r in rs if 'error' in r)}."]
    (OUTD / "RESUMEN_MINIMALIDAD.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    if "--resumen" in sys.argv:
        resumen(); sys.exit()
    nombres = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not nombres:
        for f in sorted(SUBS.glob("*.json")):
            d = json.loads(f.read_text())
            if d.get("admisible") and len(d.get("S", [])) >= 2:
                nombres.append(f.stem)
    with Pool(int(os.environ.get("NPROC", 2))) as pool:
        list(pool.imap_unordered(_seguro, nombres))
    resumen()
