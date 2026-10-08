#!/usr/bin/env python3
"""
Salidas MEDIDAS y = g(x, θ) de un problema PEtab (respuesta al comentario 4 del revisor).

En lugar de la trayectoria de todos los estados x(t) en una malla fija [0, T], la clase `PSys`
devuelve el vector de predicciones de las MEDICIONES del problema PEtab:

  * una entrada por fila de measurements.tsv (mismo observable, condición experimental,
    preequilibrio y tiempo que el dato real);
  * y_i = h(g_i(x(t_i), θ)) / σ_i, donde g_i es observableFormula (con los observableParameters
    de la fila), h la transformación de PEtab (lin, log, log10) y σ_i el ruido (noiseFormula con
    los noiseParameters de la fila) evaluado en θ₀ y fijo.

Dividir por σ hace adimensionales todas las salidas (residuos estandarizados), de modo que
‖Δy‖² es la suma de cuadrados que usa la verosimilitud gaussiana, y Jᵀ J es la matriz de
información de Fisher del diseño experimental real.

θ = parámetros con estimate = 1 en parameters.tsv (valores nominales en escala lineal),
incluidos los específicos de condición (overrides en conditions.tsv) y los de observable
(escalas, offsets). Los parámetros que sólo intervienen en el ruido no afectan a y: su columna
queda fuera (`in_model = False`).

Interfaz igual a `certify_systems.Sys` (names, theta0, in_model, sim), de modo que
`stage_reclass.py --salidas` reutiliza la selección, la validación y la reestimación sin cambios.

Comprobación: `python3 petab_outputs.py Sistema ...` compara las predicciones en θ₀ con
simulations.tsv del benchmark (cuando existe).
"""
import sys, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import sympy as sp

warnings.filterwarnings("ignore")
import roadrunner as rr
rr.Config.setValue(rr.Config.ROADRUNNER_DISABLE_WARNINGS, True)

import certify_systems as CS

T_INF = 1e5      # mediciones en estado estacionario (time = inf) y preequilibrio


def _isnum(v):
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False


def _split(v):
    if v is None or (isinstance(v, float) and np.isnan(v)) or str(v).strip() == "":
        return []
    return [s.strip() for s in str(v).split(";")]


class PSys:
    def __init__(self, name, t_end=None):
        self.name = name
        folder = CS.BENCH / name / "v1"
        par = pd.read_csv(folder / "parameters.tsv", sep="\t")
        cond = pd.read_csv(folder / "conditions.tsv", sep="\t", dtype={"conditionId": str})
        obs = pd.read_csv(folder / "observables.tsv", sep="\t")
        mea = pd.read_csv(folder / "measurements.tsv", sep="\t",
                          dtype={"simulationConditionId": str, "preequilibrationConditionId": str})
        self.m = CS.load_model(folder / "model.xml")
        mdl = self.m.model
        self.species = list(mdl.getFloatingSpeciesIds())
        self.gparams = set(mdl.getGlobalParameterIds())
        self.comps = set(mdl.getCompartmentIds())
        rules = set(self.m.getAssignmentRuleIds())

        # --- parámetros
        par["nominalValue"] = par["nominalValue"].astype(float)
        est = par["estimate"] == 1 if "estimate" in par.columns else np.ones(len(par), bool)
        self.names = par.loc[est, "parameterId"].astype(str).tolist()
        t = par.loc[est, "nominalValue"].to_numpy(float)
        t = np.where(np.isfinite(t), t, 1e-6)
        self.theta0 = np.where(t == 0, 1e-12, t).astype(float)
        self.fixed = {str(r.parameterId): float(r.nominalValue)
                      for r in par.loc[~est].itertuples()}
        self.idx = {n: j for j, n in enumerate(self.names)}

        # --- condiciones: {conditionId: [(destino, valor o id de parámetro)]}
        self.cond = {}
        cols = [c for c in cond.columns if c not in ("conditionId", "conditionName")]
        for _, r in cond.iterrows():
            ov = []
            for c in cols:
                v = r[c]
                if isinstance(v, float) and np.isnan(v):
                    continue
                ov.append((c, float(v) if _isnum(v) else str(v).strip()))
            self.cond[str(r["conditionId"])] = ov

        # --- observables
        loc = {}
        self.obs = {}
        for r in obs.itertuples(index=False):
            f = sp.sympify(str(r.observableFormula).replace("^", "**"), locals=loc)
            nf = r.noiseFormula if "noiseFormula" in obs.columns else 1.0
            g = sp.sympify(str(nf).replace("^", "**"), locals=loc)
            tr = getattr(r, "observableTransformation", "lin") if "observableTransformation" in obs.columns else "lin"
            tr = "lin" if (not isinstance(tr, str)) else tr.strip() or "lin"
            self.obs[str(r.observableId)] = (f, g, tr)

        # símbolos que dependen del tiempo (especies, parámetros con reglas, compartimentos)
        self.dyn = set(self.species) | (rules & (self.gparams | self.comps)) | self.comps
        allsym = set()
        for f, g, _ in self.obs.values():
            allsym |= {str(s) for s in f.free_symbols | g.free_symbols}
        self.sel_dyn = sorted(s for s in allsym if s in self.dyn)
        sel = ["time"] + [("[" + s + "]") if s in self.species else s for s in self.sel_dyn]
        self.m.timeCourseSelections = sel

        # --- mediciones agrupadas por (preequilibrio, condición)
        mea = mea.reset_index(drop=True)
        if "preequilibrationConditionId" not in mea.columns:
            mea["preequilibrationConditionId"] = np.nan
        mea["time"] = mea["time"].astype(float)
        self.n_meas = len(mea)
        self.mea = mea
        self.groups = []
        for (pre, sim_c), sub in mea.groupby(
                [mea.preequilibrationConditionId.fillna(""), mea.simulationConditionId], sort=False):
            tfin = sub.time.replace(np.inf, T_INF).to_numpy()
            times = np.unique(np.concatenate([[0.0], tfin]))
            rows = []
            for i, r in sub.iterrows():
                op = _split(r.get("observableParameters"))
                npar = _split(r.get("noiseParameters"))
                rows.append((i, str(r.observableId), float(np.searchsorted(times, min(r.time, T_INF))),
                             op, npar))
            self.groups.append((pre, sim_c, times, rows))

        # funciones compiladas por (observable, nombres de placeholders)
        self._fn = {}
        # parámetros que sólo afectan al ruido
        usados = set()
        for c in self.cond.values():
            usados |= {v for _, v in c if isinstance(v, str)}
        for _, _, _, rows in self.groups:
            for _, oid, _, op, _ in rows:
                usados |= {v for v in op if not _isnum(v)}
                usados |= {str(s) for s in self.obs[oid][0].free_symbols}
        self.in_model = np.array([(n in self.gparams) or (n in usados) or (n in self.comps)
                                  for n in self.names])
        self.sigma = None
        y0 = self._raw(self.theta0)
        if y0 is None:
            self.sigma = np.ones(self.n_meas)
        else:
            self.sigma = self._noise(self.theta0, y0)

    # ---------------------------------------------------------------------------------------
    def _pval(self, theta):
        P = dict(self.fixed)
        P.update(zip(self.names, map(float, theta)))
        return P

    def _apply(self, ov, P, species_too=True):
        m = self.m
        sp_init = []
        for tgt, v in ov:
            val = v if isinstance(v, float) else P.get(v, np.nan)
            if not np.isfinite(val):
                continue
            if tgt in self.species:
                sp_init.append((tgt, val))
            elif tgt in self.gparams or tgt in self.comps:
                try:
                    m[tgt] = float(val)
                except Exception:
                    pass
        return sp_init

    def _simulate_group(self, P, pre, sim_c, times):
        m = self.m
        m.resetAll()
        for k, v in P.items():
            if k in self.gparams:
                try:
                    m[k] = float(v)
                except Exception:
                    pass
        # condiciones (preequilibrio primero)
        if pre:
            sp_pre = self._apply(self.cond.get(pre, []), P)
            for s, v in sp_pre:
                m["init([" + s + "])"] = v
            m.reset()
            m.simulate(0, T_INF, 2)
            x_ss = {s: m["[" + s + "]"] for s in self.species}
            sp_sim = self._apply(self.cond.get(sim_c, []), P)
            for s, v in x_ss.items():
                try:
                    m["[" + s + "]"] = v
                except Exception:
                    pass
            for s, v in sp_sim:
                m["[" + s + "]"] = v
        else:
            sp_sim = self._apply(self.cond.get(sim_c, []), P)
            for s, v in sp_sim:
                m["init([" + s + "])"] = v
            m.reset()
        return np.asarray(m.simulate(times=list(times)), dtype=float)

    def _eval(self, expr_key, expr, ph_names, ph_vals, P, traj, k):
        """Evalúa `expr` en el instante k de la trayectoria, con los placeholders de la fila."""
        key = (expr_key, tuple(ph_names))
        if key not in self._fn:
            syms = sorted(expr.free_symbols, key=str)
            self._fn[key] = (syms, sp.lambdify(syms, expr, "numpy"))
        syms, fn = self._fn[key]
        args = []
        for s in syms:
            n = str(s)
            if n in ph_vals:
                args.append(ph_vals[n])
            elif n in self.sel_dyn:
                args.append(traj[k, 1 + self.sel_dyn.index(n)])
            elif n == "t" or n == "time":
                args.append(traj[k, 0])
            elif n in P:
                args.append(P[n])
            elif n in self.gparams or n in self.comps:
                args.append(float(self.m[n]))
            else:
                args.append(np.nan)
        return float(fn(*args))

    def _ph(self, prefix, oid, vals, P):
        out = {}
        for i, v in enumerate(vals, 1):
            out[f"{prefix}{i}_{oid}"] = float(v) if _isnum(v) else P.get(v, np.nan)
        return out

    def _raw(self, theta):
        """Predicciones g_i (sin transformar ni escalar), en el orden de measurements.tsv."""
        P = self._pval(theta)
        y = np.full(self.n_meas, np.nan)
        try:
            for pre, sim_c, times, rows in self.groups:
                traj = self._simulate_group(P, pre, sim_c, times)
                for i, oid, k, op, _ in rows:
                    f = self.obs[oid][0]
                    ph = self._ph("observableParameter", oid, op, P)
                    y[i] = self._eval(("o", oid), f, sorted(ph), ph, P, traj, int(k))
        except Exception:
            return None
        return y if np.all(np.isfinite(y)) else None

    def _noise(self, theta, yraw):
        P = self._pval(theta)
        s = np.ones(self.n_meas)
        for pre, sim_c, times, rows in self.groups:
            traj = None
            for i, oid, k, op, npar in rows:
                g = self.obs[oid][1]
                ph = self._ph("noiseParameter", oid, npar, P)
                ph[oid] = yraw[i]
                if g.free_symbols - {sp.Symbol(n) for n in ph}:
                    if traj is None:
                        traj = self._simulate_group(P, pre, sim_c, times)
                    v = self._eval(("n", oid), g, sorted(ph), ph, P, traj, int(k))
                else:
                    v = float(g.subs({sp.Symbol(n): x for n, x in ph.items()}))
                s[i] = v if np.isfinite(v) and v > 0 else 1.0
        return s

    def _h(self, y):
        out = y.copy()
        for i, oid in enumerate(self.mea.observableId.astype(str)):
            tr = self.obs[oid][2]
            if tr == "log":
                out[i] = np.log(y[i]) if y[i] > 0 else np.nan
            elif tr == "log10":
                out[i] = np.log10(y[i]) if y[i] > 0 else np.nan
        return out

    def sim(self, theta):
        """y_i = h(g_i(x(t_i), θ)) / σ_i, como matriz columna (n_mediciones × 1)."""
        y = self._raw(theta)
        if y is None:
            return None
        z = self._h(y) / self.sigma
        return z.reshape(-1, 1) if np.all(np.isfinite(z)) else None


def check(name):
    folder = CS.BENCH / name / "v1"
    S = PSys(name)
    y = S._raw(S.theta0)
    f = folder / "simulations.tsv"
    info = {"sistema": name, "p": len(S.names), "p_y": int(S.in_model.sum()),
            "mediciones": S.n_meas, "condiciones": len(S.groups)}
    if y is None:
        info["error"] = "simulación falla"
        return info
    if f.exists():
        ref = pd.read_csv(f, sep="\t")
        if len(ref) == S.n_meas:
            # emparejar por (observable, condiciones, tiempo, parámetros), no por posición
            def clave(d):
                d = d.copy()
                for c in ("preequilibrationConditionId", "observableParameters"):
                    d[c] = d[c].fillna("").astype(str) if c in d.columns else ""
                d["time"] = d["time"].astype(float).round(9)
                k = ["observableId", "preequilibrationConditionId", "simulationConditionId",
                     "time", "observableParameters"]
                d["_n"] = d.groupby(k).cumcount()
                return d[k + ["_n"]].astype(str).agg("|".join, axis=1)
            ref.index = clave(ref)
            r = ref["simulation"].astype(float).reindex(clave(S.mea)).to_numpy()
            ok = np.isfinite(r)
            rel = np.abs(y[ok] - r[ok]) / np.maximum(np.abs(r[ok]), 1e-6 * np.max(np.abs(r[ok])) + 1e-12)
            info["err_rel_max_vs_simulations"] = float(np.max(rel))
            info["err_rel_mediana"] = float(np.median(rel))
        else:
            info["nota"] = f"simulations.tsv tiene {len(ref)} filas"
    return info


if __name__ == "__main__":
    import json
    for n in sys.argv[1:]:
        try:
            print(json.dumps(check(n)), flush=True)
        except Exception as e:
            print(json.dumps({"sistema": n, "error": repr(e)}), flush=True)
