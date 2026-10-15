"""
Measured outputs of a PEtab problem as a function of the parameters.

``PetabProblem(name).sim(theta)`` returns the vector of model predictions of all measurements of
the PEtab problem, in the scale of the likelihood:

* one entry per row of ``measurements.tsv`` (same observable, experimental condition,
  pre-equilibration and time as the measured value);
* ``y_i = h(g_i(x(t_i), theta)) / sigma_i``, where ``g_i`` is the ``observableFormula`` (with the
  ``observableParameters`` of the row), ``h`` the PEtab transformation (lin, log, log10) and
  ``sigma_i`` the noise standard deviation (``noiseFormula`` with the ``noiseParameters`` of the
  row) evaluated at the nominal parameters ``theta0`` and kept fixed.

Dividing by sigma makes all outputs dimensionless, so ``||Delta y||^2`` is the sum of squares of the
Gaussian likelihood and ``J^T J`` is the Fisher information matrix of the actual experimental design.

``theta`` = parameters with ``estimate = 1`` in ``parameters.tsv`` (nominal values, linear scale),
including condition-specific parameters (overrides in ``conditions.tsv``) and observable parameters
(scalings, offsets). Parameters that only enter the noise model do not affect y
(``in_model = False``). Calibration parameters (``calib = True``) are those that are neither SBML
parameters or compartments nor referenced in ``conditions.tsv``: they only enter the observation
or noise model.

Simulation: libRoadRunner (CVODE, relative and absolute tolerances 1e-7 and 1e-10, which can be
changed with ``REPRO_RTOL`` and ``REPRO_ATOL`` for the sensitivity analysis of Fig. 5).
"""
import os
import warnings

import numpy as np
import pandas as pd
import sympy as sp

warnings.filterwarnings("ignore")
import roadrunner as rr  # noqa: E402

rr.Config.setValue(rr.Config.ROADRUNNER_DISABLE_WARNINGS, True)

from config import BENCHMARK  # noqa: E402

T_INF = 1e5      # time used for steady-state measurements (time = inf) and pre-equilibration
RTOL = float(os.environ.get("REPRO_RTOL", 1e-7))
ATOL = float(os.environ.get("REPRO_ATOL", 1e-10))


def load_model(sbml_path, overridden=()):
    """Load the SBML model, turning the initial assignments of PARAMETERS and COMPARTMENTS
    (constants that depend on other constants, e.g. beta = R0*gamma/N) into assignment rules, so
    that they are recomputed when theta changes (RoadRunner does not re-evaluate such initial
    assignments when a parameter is set; those of species are re-evaluated by reset()). This does
    not change the dynamics: the values coincide with those of the initial assignment.
    Initial assignments of symbols set in conditions.tsv are removed: in PEtab the value of the
    condition replaces the initial assignment."""
    import libsbml
    doc = libsbml.readSBMLFromFile(str(sbml_path))
    mdl = doc.getModel()
    for ia in list(mdl.getListOfInitialAssignments()):
        sid = ia.getSymbol()
        if sid in overridden:
            p = mdl.getParameter(sid)
            if p is not None and not p.isSetValue():
                p.setValue(0.0)       # set by each condition
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
    # species with hasOnlySubstanceUnits: their symbol in formulas is the AMOUNT
    hosu = {s.getId() for s in mdl.getListOfSpecies() if s.getHasOnlySubstanceUnits()}
    m = rr.RoadRunner(libsbml.writeSBMLToString(doc))
    ig = m.getIntegrator()
    for k, v in [("relative_tolerance", RTOL), ("absolute_tolerance", ATOL),
                 ("maximum_num_steps", 200000), ("stiff", True)]:
        try:
            ig.setValue(k, v)
        except Exception:
            pass
    return m, hosu


def is_number(v):
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False


def _split(v):
    if v is None or (isinstance(v, float) and np.isnan(v)) or str(v).strip() == "":
        return []
    return [s.strip() for s in str(v).split(";")]


class PetabProblem:
    def __init__(self, name, simulate=True):
        self.name = name
        folder = BENCHMARK / name / "v1"
        par = pd.read_csv(folder / "parameters.tsv", sep="\t", encoding="utf-8-sig")
        cond = pd.read_csv(folder / "conditions.tsv", sep="\t", encoding="utf-8-sig",
                           dtype={"conditionId": str})
        obs = pd.read_csv(folder / "observables.tsv", sep="\t", encoding="utf-8-sig")
        mea = pd.read_csv(folder / "measurements.tsv", sep="\t",
                          dtype={"simulationConditionId": str, "preequilibrationConditionId": str})
        self.m, self.hosu = load_model(folder / "model.xml",
                                       set(cond.columns) - {"conditionId", "conditionName"})
        mdl = self.m.model
        self.species = list(mdl.getFloatingSpeciesIds())
        # boundary species (e.g. defined by rules): they can be observed and set
        self.bspecies = list(mdl.getBoundarySpeciesIds())
        self.gparams = set(mdl.getGlobalParameterIds())
        self.comps = set(mdl.getCompartmentIds())
        rules = set(self.m.getAssignmentRuleIds()) | set(self.m.getRateRuleIds())

        # --- parameters
        par["nominalValue"] = par["nominalValue"].astype(float)
        est = par["estimate"] == 1 if "estimate" in par.columns else np.ones(len(par), bool)
        self.names = par.loc[est, "parameterId"].astype(str).tolist()
        t = par.loc[est, "nominalValue"].to_numpy(float)
        t = np.where(np.isfinite(t), t, 1e-6)
        self.theta0 = np.where(t == 0, 1e-12, t).astype(float)
        self.fixed = {str(r.parameterId): float(r.nominalValue)
                      for r in par.loc[~est].itertuples()}
        self.idx = {n: j for j, n in enumerate(self.names)}

        # --- conditions: {conditionId: [(target, value or parameter id)]}
        self.cond = {}
        cols = [c for c in cond.columns if c not in ("conditionId", "conditionName")]
        for _, r in cond.iterrows():
            ov = []
            for c in cols:
                v = r[c]
                if isinstance(v, float) and np.isnan(v):
                    continue
                ov.append((c, float(v) if is_number(v) else str(v).strip()))
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

        # time-dependent symbols (species, parameters with rules, compartments)
        self.dyn = set(self.species) | set(self.bspecies) | (rules & (self.gparams | self.comps)) | self.comps
        allsym = set()
        for f, g, _ in self.obs.values():
            allsym |= {str(s) for s in f.free_symbols | g.free_symbols}
        self.sel_dyn = sorted(s for s in allsym if s in self.dyn)
        self.allsp = set(self.species) | set(self.bspecies)
        sel = ["time"] + [self._sid(s) for s in self.sel_dyn]
        self.m.timeCourseSelections = sel

        # --- measurements grouped by (pre-equilibration, simulation condition)
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
            if len(times) < 2:        # RoadRunner needs at least two output times
                times = np.array([0.0, 1.0])
            rows = []
            for i, r in sub.iterrows():
                op = _split(r.get("observableParameters"))
                npar = _split(r.get("noiseParameters"))
                rows.append((i, str(r.observableId), float(np.searchsorted(times, min(r.time, T_INF))),
                             op, npar))
            self.groups.append((pre, sim_c, times, rows))

        # compiled functions per (observable, placeholder names)
        self._fn = {}
        # parameters that only affect the noise model
        used = set()
        for c in self.cond.values():
            used |= {v for _, v in c if isinstance(v, str)}
        for _, _, _, rows in self.groups:
            for _, oid, _, op, _ in rows:
                used |= {v for v in op if not is_number(v)}
                used |= {str(s) for s in self.obs[oid][0].free_symbols}
        self.in_model = np.array([(n in self.gparams) or (n in used) or (n in self.comps)
                                  for n in self.names])
        # CALIBRATION parameters (scalings, offsets, noise): not parameters of the biological
        # (SBML) model and not set in conditions.tsv; they only enter g or sigma
        refs_cond = set()
        for c in self.cond.values():
            refs_cond |= {v for _, v in c if isinstance(v, str)}
        self.calib = np.array([(n not in self.gparams) and (n not in self.comps)
                               and (n not in refs_cond) for n in self.names])
        self.sigma = None
        if not simulate:       # only the loaded model is needed (e.g. translation check)
            return
        y0 = self._raw(self.theta0)
        if y0 is None:
            self.sigma = np.ones(self.n_meas)
        else:
            self.sigma = self._noise(self.theta0, y0)

    # ---------------------------------------------------------------------------------------
    def _sid(self, s):
        """RoadRunner selector of symbol `s` (concentration unless hasOnlySubstanceUnits)."""
        if s in self.allsp and s not in self.hosu:
            return "[" + s + "]"
        return s

    def _pval(self, theta):
        P = dict(self.fixed)
        P.update(zip(self.names, map(float, theta)))
        return P

    def _apply(self, ov, P):
        """Overrides of a condition: sets parameters/compartments; returns the species to be set
        at t = 0."""
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
        first = pre if pre else sim_c
        sp0 = self._apply(self.cond.get(first, []), P)
        m.reset()        # species to their initial values (re-evaluates their initial assignments)
        for s, v in sp0:
            m[self._sid(s)] = v
        if pre:
            m.simulate(0, T_INF, 2)
            x_ss = {"[" + s + "]": m["[" + s + "]"] for s in self.species}
            x_ss.update({r: m[r] for r in self.m.getRateRuleIds()})
            # restart (time and events at zero) with the steady state as initial state
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
            # fallbacks: piecewise integration; then BDF order <= 2; then tolerances 1e-6 / 1e-8
            ig = m.getIntegrator()
            base = {"maximum_bdf_order": 5, "relative_tolerance": RTOL, "absolute_tolerance": ATOL}
            settings = [{}, {"maximum_bdf_order": 2},
                        {"maximum_bdf_order": 2, "relative_tolerance": 1e-6, "absolute_tolerance": 1e-8}]
            traj = None
            for k, st in enumerate(settings):
                m.model.setTime(0.0)
                m.model.setFloatingSpeciesConcentrations(x0)
                for r, v in rr0.items():
                    m[r] = v
                for key, v in st.items():
                    ig.setValue(key, v)
                try:
                    traj = self._piecewise(P, sim_c, times)
                    break
                except Exception:
                    if k == len(settings) - 1:
                        raise
                finally:
                    for key, v in base.items():
                        ig.setValue(key, v)
        # RoadRunner may reorder the columns: reorder them as self.sel_dyn
        cols = list(m.timeCourseSelections)
        order = [cols.index("time")] + [cols.index(self._sid(s)) for s in self.sel_dyn]
        return traj[:, order]

    def _piecewise(self, P, sim_c, times):
        """Fallback when the integrator fails (discontinuities, e.g. drug additions in Isensee):
        restart from the saved state and integrate piecewise, with breakpoints at the output
        times and at the condition values that fall inside the interval."""
        m = self.m
        cuts = {float(v) for _, v in self.cond.get(sim_c, []) if isinstance(v, float)}
        cuts |= {float(P[v]) for _, v in self.cond.get(sim_c, []) if isinstance(v, str) and v in P}
        grid = np.unique(np.concatenate([times, [c for c in cuts if 0 < c < times[-1]]]))
        rows = []
        sel = list(m.timeCourseSelections)
        state0 = {k: m[k] for k in sel if k != "time"}
        rows.append([0.0] + [state0[k] for k in sel if k != "time"])
        cuts = {c for c in cuts if 0 < c < times[-1]}
        t = 0.0
        for b in grid[1:]:
            eps = 1e-6 * max(1.0, b)
            r = np.asarray(m.simulate(t, b - (eps if b in cuts else 0.0), 2), dtype=float)
            rows.append(r[-1].tolist())
            t = b
            if b in cuts:          # step over the discontinuity (continuous state, error O(eps))
                t = b + eps
        rows = np.array(rows)
        keep = [i for i, tt in enumerate(grid) if np.any(np.isclose(times, tt))]
        out = rows[keep]
        out[:, sel.index("time")] = times
        return out

    def _eval(self, expr_key, expr, ph_names, ph_vals, P, traj, k):
        """Evaluate `expr` at time index k of the trajectory, with the placeholders of the row."""
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
            out[f"{prefix}{i}_{oid}"] = float(v) if is_number(v) else P.get(v, np.nan)
        return out

    def _raw(self, theta, gidx=None):
        """Predictions g_i (not transformed or scaled), in the order of measurements.tsv.
        With `gidx` only those groups (conditions) are simulated; the rest are NaN."""
        P = self._pval(theta)
        y = np.full(self.n_meas, np.nan)
        groups = self.groups if gidx is None else [self.groups[g] for g in gidx]
        try:
            for pre, sim_c, times, rows in groups:
                traj = self._simulate_group(P, pre, sim_c, times)
                for i, oid, k, op, _ in rows:
                    f = self.obs[oid][0]
                    ph = self._ph("observableParameter", oid, op, P)
                    y[i] = self._eval(("o", oid), f, sorted(ph), ph, P, traj, int(k))
        except Exception:
            return None
        if gidx is not None:
            rows_g = [r[0] for g in gidx for r in self.groups[g][3]]
            return y if np.all(np.isfinite(y[rows_g])) else None
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
        """Full vector h(g)/sigma (NaN in the rows of groups that were not simulated)."""
        y = self._raw(theta, gidx)
        return None if y is None else self._h(y) / self.sigma

    def zdata(self):
        """Measured data in the same scale: h(measurement)/sigma (NaN where h is undefined)."""
        with np.errstate(all="ignore"):
            return self._h(self.mea["measurement"].astype(float).to_numpy()) / self.sigma

    def sim(self, theta):
        """y_i = h(g_i(x(t_i), theta)) / sigma_i as a column matrix (n_measurements x 1)."""
        y = self._raw(theta)
        if y is None:
            return None
        z = self._h(y) / self.sigma
        return z.reshape(-1, 1) if np.all(np.isfinite(z)) else None
