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


def load_model_ia(sbml_path, overridden=()):
    """Carga el modelo convirtiendo las asignaciones iniciales de PARÁMETROS y COMPARTIMENTOS
    (constantes que dependen de otras constantes, p. ej. β = R₀γ/N) en reglas de asignación.
    Así, al cambiar θ se recalculan (RoadRunner no reevalúa esas asignaciones iniciales al
    fijar un parámetro; las de especies sí se reevalúan en reset()). Sin efecto en la dinámica:
    los valores coinciden con los de la asignación inicial.
    Las asignaciones iniciales de símbolos fijados en conditions.tsv se eliminan: en PEtab el
    valor de la condición sustituye a la asignación inicial."""
    import libsbml
    doc = libsbml.readSBMLFromFile(str(sbml_path))
    mdl = doc.getModel()
    for ia in list(mdl.getListOfInitialAssignments()):
        sid = ia.getSymbol()
        if sid in overridden:
            p = mdl.getParameter(sid)
            if p is not None and not p.isSetValue():
                p.setValue(0.0)       # se fija en cada condición
            mdl.removeInitialAssignment(sid)
            continue
        obj = mdl.getParameter(sid) or mdl.getCompartment(sid)
        if obj is None or mdl.getRule(sid) is not None:
            continue
        r = mdl.createAssignmentRule()
        r.setVariable(sid)
        r.setMath(ia.getMath().deepCopy())
        obj.setConstant(False)
        mdl.removeInitialAssignment(sid)
    # especies con hasOnlySubstanceUnits: su símbolo en las fórmulas es la CANTIDAD
    hosu = {sp.getId() for sp in mdl.getListOfSpecies() if sp.getHasOnlySubstanceUnits()}
    m = rr.RoadRunner(libsbml.writeSBMLToString(doc))
    ig = m.getIntegrator()
    for k, v in [("relative_tolerance", 1e-7), ("absolute_tolerance", 1e-10),
                 ("maximum_num_steps", 200000), ("stiff", True)]:
        try:
            ig.setValue(k, v)
        except Exception:
            pass
    return m, hosu


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
        par = pd.read_csv(folder / "parameters.tsv", sep="\t", encoding="utf-8-sig")
        cond = pd.read_csv(folder / "conditions.tsv", sep="\t", encoding="utf-8-sig", dtype={"conditionId": str})
        obs = pd.read_csv(folder / "observables.tsv", sep="\t", encoding="utf-8-sig")
        mea = pd.read_csv(folder / "measurements.tsv", sep="\t",
                          dtype={"simulationConditionId": str, "preequilibrationConditionId": str})
        self.m, self.hosu = load_model_ia(folder / "model.xml",
                               set(cond.columns) - {"conditionId", "conditionName"})
        mdl = self.m.model
        self.species = list(mdl.getFloatingSpeciesIds())
        # especies de frontera (p. ej. definidas por reglas): se pueden observar y fijar
        self.bspecies = list(mdl.getBoundarySpeciesIds())
        self.gparams = set(mdl.getGlobalParameterIds())
        self.comps = set(mdl.getCompartmentIds())
        rules = set(self.m.getAssignmentRuleIds()) | set(self.m.getRateRuleIds())

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
        self.dyn = set(self.species) | set(self.bspecies) | (rules & (self.gparams | self.comps)) | self.comps
        allsym = set()
        for f, g, _ in self.obs.values():
            allsym |= {str(s) for s in f.free_symbols | g.free_symbols}
        self.sel_dyn = sorted(s for s in allsym if s in self.dyn)
        self.allsp = set(self.species) | set(self.bspecies)
        sel = ["time"] + [self._sid(s) for s in self.sel_dyn]
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
            if len(times) < 2:        # RoadRunner necesita al menos dos tiempos
                times = np.array([0.0, 1.0])
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
    def _sid(self, s):
        """Selector de RoadRunner del símbolo `s` (concentración salvo hasOnlySubstanceUnits)."""
        if s in self.allsp and s not in self.hosu:
            return "[" + s + "]"
        return s

    def _pval(self, theta):
        P = dict(self.fixed)
        P.update(zip(self.names, map(float, theta)))
        return P

    def _apply(self, ov, P):
        """Overrides de una condición: fija parámetros/compartimentos; devuelve las especies
        a fijar en t = 0."""
        sp_init = []
        for tgt, v in ov:
            val = v if isinstance(v, float) else P.get(v, np.nan)
            if not np.isfinite(val):
                continue
            if tgt in self.species or tgt in self.bspecies:
                sp_init.append((tgt, val))
            elif tgt in self.gparams or tgt in self.comps:
                try:
                    self.m[tgt] = float(val)
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
        primera = pre if pre else sim_c
        sp0 = self._apply(self.cond.get(primera, []), P)
        m.reset()        # especies a sus valores iniciales (reevalúa sus asignaciones iniciales)
        for s, v in sp0:
            m[self._sid(s)] = v
        if pre:
            m.simulate(0, T_INF, 2)
            x_ss = {"[" + s + "]": m["[" + s + "]"] for s in self.species}
            x_ss.update({r: m[r] for r in self.m.getRateRuleIds()})
            # reinicio (tiempo y eventos a cero) y estado estacionario como estado inicial
            m.reset()
            sp_sim = self._apply(self.cond.get(sim_c, []), P)
            for s, v in list(x_ss.items()) + [(self._sid(a), b) for a, b in sp_sim]:
                try:
                    m[s] = v
                except Exception:
                    pass
        x0 = np.array(m.model.getFloatingSpeciesConcentrations(), dtype=float)
        rr0 = {r: m[r] for r in m.getRateRuleIds()}
        try:
            traj = np.asarray(m.simulate(times=list(times)), dtype=float)
        except Exception:
            # respaldos: por tramos; además orden BDF ≤ 2; además tolerancias 1e-6 / 1e-8
            ig = m.getIntegrator()
            base = {"maximum_bdf_order": 5, "relative_tolerance": 1e-7, "absolute_tolerance": 1e-10}
            ajustes = [{}, {"maximum_bdf_order": 2},
                       {"maximum_bdf_order": 2, "relative_tolerance": 1e-6, "absolute_tolerance": 1e-8}]
            traj = None
            for k, aj in enumerate(ajustes):
                m.model.setTime(0.0)
                m.model.setFloatingSpeciesConcentrations(x0)
                for r, v in rr0.items():
                    m[r] = v
                for key, v in aj.items():
                    ig.setValue(key, v)
                try:
                    traj = self._piecewise(P, sim_c, times)
                    break
                except Exception:
                    if k == len(ajustes) - 1:
                        raise
                finally:
                    for key, v in base.items():
                        ig.setValue(key, v)
        # RoadRunner puede reordenar las columnas: se reordenan según self.sel_dyn
        cols = list(m.timeCourseSelections)
        orden = [cols.index("time")] + [cols.index(self._sid(s)) for s in self.sel_dyn]
        return traj[:, orden]

    def _piecewise(self, P, sim_c, times):
        """Respaldo si el integrador falla (discontinuidades, p. ej. adición de fármacos en
        Isensee): se reinicia el estado guardado y se integra por tramos, con cortes en los
        tiempos de salida y en los valores de la condición que caen dentro del intervalo."""
        m = self.m
        cortes = {float(v) for _, v in self.cond.get(sim_c, []) if isinstance(v, float)}
        cortes |= {float(P[v]) for _, v in self.cond.get(sim_c, []) if isinstance(v, str) and v in P}
        grid = np.unique(np.concatenate([times, [c for c in cortes if 0 < c < times[-1]]]))
        filas = []
        sel = list(m.timeCourseSelections)
        estado0 = {k: m[k] for k in sel if k != "time"}
        filas.append([0.0] + [estado0[k] for k in sel if k != "time"])
        cortes = {c for c in cortes if 0 < c < times[-1]}
        t = 0.0
        for b in grid[1:]:
            eps = 1e-6 * max(1.0, b)
            r = np.asarray(m.simulate(t, b - (eps if b in cortes else 0.0), 2), dtype=float)
            filas.append(r[-1].tolist())
            t = b
            if b in cortes:          # se salta la discontinuidad (estado continuo, error O(ε))
                t = b + eps
        filas = np.array(filas)
        keep = [i for i, tt in enumerate(grid) if np.any(np.isclose(times, tt))]
        out = filas[keep]
        out[:, sel.index("time")] = times
        return out

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

    def _raw(self, theta, gidx=None):
        """Predicciones g_i (sin transformar ni escalar), en el orden de measurements.tsv.
        Con `gidx` sólo se simulan esos grupos (condiciones); el resto queda en NaN."""
        P = self._pval(theta)
        y = np.full(self.n_meas, np.nan)
        grupos = self.groups if gidx is None else [self.groups[g] for g in gidx]
        try:
            for pre, sim_c, times, rows in grupos:
                traj = self._simulate_group(P, pre, sim_c, times)
                for i, oid, k, op, _ in rows:
                    f = self.obs[oid][0]
                    ph = self._ph("observableParameter", oid, op, P)
                    y[i] = self._eval(("o", oid), f, sorted(ph), ph, P, traj, int(k))
        except Exception:
            return None
        if gidx is not None:
            filas = [r[0] for g in gidx for r in self.groups[g][3]]
            return y if np.all(np.isfinite(y[filas])) else None
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

    def z(self, theta, gidx=None):
        """Vector completo h(g)/σ (NaN en las filas de grupos no simulados)."""
        y = self._raw(theta, gidx)
        return None if y is None else self._h(y) / self.sigma

    def zdata(self):
        """Datos medidos en la misma escala: h(medición)/σ (NaN si h no está definida)."""
        with np.errstate(all="ignore"):
            return self._h(self.mea["measurement"].astype(float).to_numpy()) / self.sigma

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
        ref = pd.read_csv(f, sep="\t", encoding="utf-8-sig")
        if len(ref) == S.n_meas:
            # emparejar por (observable, condiciones, tiempo, parámetros), no por posición
            def clave(d):
                d = d.copy()
                c = "preequilibrationConditionId"
                d[c] = d[c].fillna("").astype(str) if c in d.columns else ""
                d["time"] = d["time"].astype(float).round(9)
                k = ["observableId", c, "simulationConditionId", "time"]
                d["_n"] = d.groupby(k).cumcount()
                return d[k + ["_n"]].astype(str).agg("|".join, axis=1)
            ref = ref.rename(columns={"simulationCondition": "simulationConditionId",
                                      "preequilibrationCondition": "preequilibrationConditionId"})
            ref.index = clave(ref)
            r = ref["simulation"].astype(float).reindex(clave(S.mea)).to_numpy()
            ok = np.isfinite(r)
            if not ok.any():
                info["nota"] = "simulations.tsv no comparable (otros identificadores de condición)"
                return info
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
