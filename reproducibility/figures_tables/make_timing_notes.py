#!/usr/bin/env python3
"""
Computing time of every analysis of the paper (Supplementary Note "Computing time of the analyses"):

  tables/tableS_time_method.tex      selection, settings, robustness, single parameter (per problem)
  tables/tableS_time_validation.tex  validation, synthetic experiment, identifiability (per problem)
  tables/tableS_time_comparison.tex  other criteria, baselines, profile likelihood of the full model
  tables/tableS_time_summary.tex     summary per analysis (median, maximum, total)

Times are those recorded by each program for each problem (field "segundos" of the result files):
elapsed seconds of the computation of that problem, with the internal parallelism described in the
note; where an analysis consists of independent single-core tasks (seeds of the synthetic experiment,
scenarios and seeds of the admissibility test of the criteria, profile points), the time is their sum,
i.e. CPU time. Usage: python make_timing_notes.py   (prints the numbers quoted in the main text)
"""
import collections
import json
import math
import statistics

import numpy as np

from common import RESULTS as RES, TAB, load

SEL = load("selection")
NAMES = sorted(SEL)
ADM = [s for s in NAMES if SEL[s].get("admisible")]
ok = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) and x >= 0
short = lambda s: s.split("_")[0].replace("SalazarCavazos", "Salazar-Cavazos")


def fmt(t):
    if not ok(t):
        return "--"
    if t < 1:
        return "$<$1 s"
    if t < 60:
        return f"{t:.0f} s"
    if t < 3600:
        return f"{t / 60:.1f} min"
    return f"{t / 3600:.1f} h"


def seg(d, key="segundos"):
    return d.get(key) if isinstance(d, dict) and ok(d.get(key)) else None


def summed(sub, prefix=None):
    """{problem: sum of 'segundos' over the files of RES/sub/<problem>/ or RES/sub/<problem>__*.json}."""
    out = collections.defaultdict(float)
    d = RES / sub
    if not d.exists():
        return {}
    for f in d.rglob("*.json"):
        if "__single__" in f.name:        # test of k_min = 2: counted in T["kmin"]
            continue
        rel = f.relative_to(d).parts
        s = rel[0] if len(rel) > 1 else f.stem.split("__")[0]
        try:
            r = json.loads(f.read_text())
        except Exception:
            continue
        for k in ("segundos",):
            if isinstance(r, dict) and ok(r.get(k)):
                out[s] += r[k]
    return dict(out)


T = {}
# method
fx, tp, ts = load("timing_complete/parallel_corrected_code"), load("timing_complete/parallel"), load("timing_complete/single_core")
T["sel_par"] = {s: seg(fx.get(s)) or seg(tp.get(s)) for s in NAMES}
T["sel_1"] = {s: seg(ts.get(s)) for s in NAMES}
sets = collections.defaultdict(float)
for d in (RES / "settings").iterdir() if (RES / "settings").exists() else []:
    for f in d.glob("*.json"):
        r = json.loads(f.read_text())
        if ok(r.get("segundos")):
            sets[f.stem] += r["segundos"]
for d in (RES / "settings_extra").iterdir() if (RES / "settings_extra").exists() else []:
    if d.is_dir():
        for f in d.glob("*.json"):
            r = json.loads(f.read_text())
            if ok(r.get("segundos")):
                sets[f.stem] += r["segundos"]
T["settings"] = dict(sets)
T["rob"] = {s: seg(r) for s, r in load("robustness").items()}
T["rob_ind"] = {s: seg(r) for s, r in load("robustness_independent").items()}
T["single"] = {s: seg(r) for s, r in load("single_parameter").items()}
# validation and identifiability
T["ext"] = {s: seg(r) for s, r in load("external_validation").items()}
T["nest"] = {s: seg(r) for s, r in load("nested_validation").items()}
T["syn20"] = summed("synthetic_seeds")
T["syn5"] = summed("synthetic_seeds_a005")
T["syn50"] = summed("synthetic_seeds_a050")
sig = collections.defaultdict(float)
for a in ("a005", "a020", "a050"):
    for s, v in summed(f"synthetic_signal_{a}").items():
        sig[s] += v
T["signal"] = dict(sig)
idt = {}
for s in ADM:
    d = RES / "identifiability" / "profiles" / s
    if (d / "minimo.npz").exists():
        m = np.load(d / "minimo.npz")
        t = float(m["segundos"]) if "segundos" in m.files else 0.0
        t += sum(json.loads(f.read_text()).get("segundos", 0.0) for f in d.glob("p_*.json"))
        idt[s] = t
T["ident"] = idt
# comparison
T["qr"] = {s: seg(r) for s, r in load("qr_selection").items()}
T["bm"] = {s: (seg(r) or 0) for s, r in load("brun_morris").items() if seg(r) is not None}
T["rand"] = {s: seg(r) for s, r in load("random_subsets").items()}
T["cal"] = {s: seg(r) for s, r in load("calibration_only").items()}
T["crit5"] = summed("criteria_tests")
T["crit20"] = summed("criteria_tests_20pc")
t1, tc = {}, collections.defaultdict(float)
if True:
    for line in [l for n in ("round0.log", "large_problems.log") if (RES / "profile_likelihood" / "logs" / n).exists() for l in (RES / "profile_likelihood" / "logs" / n).read_text(encoding="utf-8", errors="ignore").splitlines()]:
        if '"terminado": true' in line:
            d = json.loads(line); t1[d["sistema"]] = d["seg_total"]
seen = set()
for name in ("refits.log", "refits_remaining.log", "refits_final.log", "raia_10_rounds.log"):
    lg = RES / "profile_likelihood" / "logs" / name
    if lg.exists():
        for line in lg.read_text(encoding="utf-8", errors="ignore").splitlines():
            if '"terminado": true' in line:
                d = json.loads(line)
                if d["puntos"] > 0 and (d["sistema"], d["seg_total"]) not in seen:
                    seen.add((d["sistema"], d["seg_total"])); tc[d["sistema"]] += d["seg_total"]
T["pl"] = {s: t1[s] + tc.get(s, 0.0) for s in t1}
# profile likelihood of the full model: the logs give elapsed time with the points in parallel; the
# processor time is the sum over the profile points (all rounds), and is the one added to the totals
T["pl_cpu"] = {d.name: sum(json.loads(f.read_text()).get("segundos", 0.0) for f in d.glob("perfil_*.json"))
               for d in (RES / "profile_likelihood").iterdir() if d.is_dir() and d.name != "logs"}
# nonlinear re-estimation of the final subset of the problems selected with the first-order e_fit
T["nl"] = {s: r.get("segundos_total") for s, r in load("efit_nonlinear").items()}
# analyses added in the second review
T["sel_fix"] = {s: seg(r) for s, r in load("selection_fixedscen").items()}
T["sel_train"] = {s: seg(r) for s, r in load("selection_train_fixedscen").items()}
T["gks"] = {s: seg(r) for s, r in load("qr_selection_gks").items()}
T["crit5f"] = summed("criteria_tests_fixedscen")
T["crit20f"] = summed("criteria_tests_20pc_fixedscen")
T["synlog"] = summed("criteria_tests_sint_loguniforme")
T["synsp"] = summed("criteria_tests_sint_dispersa")


def profile_points(folder):
    out = {}
    base = RES / "identifiability" / folder
    for d in sorted(base.iterdir()) if base.exists() else []:
        if d.is_dir():
            t = sum(json.loads(f.read_text()).get("segundos", 0.0) for f in d.glob("p_*.json"))
            if (d / "minimo.npz").exists():
                m = np.load(d / "minimo.npz")
                t += float(m["segundos"]) if "segundos" in m.files else 0.0
            out[d.name] = t
    return out


T["ident_dense"] = profile_points("profiles_dense")
T["ident_train"] = profile_points("profiles_selection_train_fixedscen")
# identifiability of the subsets of the other criteria (scripts/identificabilidad_criterios.sh)
_ic = collections.defaultdict(float)
for _c in ("brun", "morris", "qr_gks", "perfil"):
    for _s, _t in profile_points(f"profiles_subsets_{_c}").items():
        _ic[_s] += _t
T["ident_crit"] = dict(_ic)
# test of the minimum subset size k_min = 2 (analysis/kmin_times.py: recorded task times, and checkpoint
# times for the robustness of Smith and Schwen, which was split into one process per size)
_kt = RES / "kmin_times.json"
T["kmin"] = json.loads(_kt.read_text())["per_problem_s"] if _kt.exists() else {}

LAB = {"sel_par": "Selection, parallel", "sel_1": "Selection, 1 core", "settings": "Settings (15 variants)",
       "rob": "Robustness, paired", "rob_ind": "Robustness, independent", "single": "Single parameter",
       "ext": "External validation", "nest": "Nested validation", "syn20": r"Synthetic, $\pm$20\%, 20 seeds",
       "syn5": r"Synthetic, $\pm$5\%, 10 seeds", "syn50": r"Synthetic, $\pm$50\%, 10 seeds", "signal": "True signal, 3 amplitudes",
       "ident": "Identifiability of $S$", "qr": "Pivoted QR", "bm": "Brun and Morris", "rand": "Random subsets (20)",
       "cal": "Calibration only", "crit5": r"Criteria test, $\pm$5\%", "crit20": r"Criteria test, $\pm$20\%",
       "pl": "Profile likelihood, full model (elapsed)", "pl_cpu": "Profile likelihood, full model (processor)",
       "nl": "Nonlinear check of $S$",
       "sel_fix": "Selection, fixed scen.", "sel_train": "Selection, training",
       "gks": "Pivoted QR (GKS)", "crit5f": r"Criteria, $\pm$5\%, fixed",
       "crit20f": r"Criteria, $\pm$20\%, fixed", "synlog": "Synthetic, log-uniform",
       "synsp": "Synthetic, sparse", "ident_dense": "Profiles, 20 per side",
       "ident_train": "Profiles, training $S$", "ident_crit": "Profiles, other criteria", "kmin": "Test of $k_{\\min}=2$"}
ELAPSED = {"sel_1", "pl"}      # not added to the totals (the same computation is counted elsewhere)


def table(keys, name, caption, label):
    head = ["Problem"] + [LAB[k] for k in keys]
    rows = [[short(s)] + [fmt(T[k].get(s)) for k in keys] for s in NAMES]
    spec = "@{}l" + "r" * len(keys) + "@{}"
    h = " & ".join(rf"\rotatebox{{70}}{{{x}}}" if i else x for i, x in enumerate(head)) + r" \\"
    s = [rf"\begin{{longtable}}{{{spec}}}", rf"\caption{{{caption}}}\label{{{label}}}\\", r"\toprule", h, r"\midrule",
         r"\endfirsthead", r"\toprule", h, r"\midrule", r"\endhead"]
    s += [" & ".join(r) + r" \\" for r in rows] + [r"\bottomrule", r"\end{longtable}"]
    (TAB / name).write_text("\n".join(s) + "\n", encoding="utf-8"); print("written", name)


COMMON = (r" Times recorded by each program for each problem: elapsed time of the computation of that problem with the parallelism described in the text; where an analysis consists of independent single-core tasks (seeds, scenarios, profile points) the time is their sum, i.e.\ processor time. "
          r"--, not computed (problem not admissible, not applicable or not run). Large problems were computed on shared servers with 128 or 256 cores, the others on an 8-core workstation; times on shared servers may be inflated by resource contention.")
table(["sel_par", "sel_1", "settings", "rob", "rob_ind", "single"], "tableS_time_method.tex",
      r"Computing time of the method and of the analyses of its behaviour, for every problem. Selection: complete method (sensitivities, stages 1 and 2, admissibility test and backward elimination) run from scratch, with the sensitivities in parallel or on one core; Settings: the 15 variants of Supplementary Note \emph{Sensitivity to the method settings} together; Robustness: seven perturbation sizes with paired or independent directions; Single parameter: Supplementary Note \emph{Single-parameter subsets}." + COMMON,
      "tab:timemethod")
table(["ext", "nest", "syn20", "syn5", "syn50", "signal", "ident"], "tableS_time_validation.tex",
      r"Computing time of the validation and identifiability analyses, for every problem: external and nested validation on real data, synthetic experiment (20 seeds at $\pm$20\%, 10 seeds at $\pm$5\% and $\pm$50\%), true signal $y(\theta^\ast)-y(\theta_0)$ at the three amplitudes, and the identifiability of the selected parameters (fit of the reduced problem and all profile points)." + COMMON,
      "tab:timevalidation")
table(["qr", "bm", "rand", "cal", "crit5", "crit20", "pl", "pl_cpu"], "tableS_time_comparison.tex",
      r"Computing time of the comparison with other criteria, for every problem: selection and validation by pivoted QR, Brun and Morris, the random and calibration-only baselines, the admissibility and synthetic tests of the subsets of all criteria ($\pm$5\%, including the synthetic seeds, and $\pm$20\%), and profile likelihood of every biological parameter of the full model (all rounds), as elapsed time with the profile points in parallel and as processor time, the sum over the points." + COMMON,
      "tab:timecomparison")
table(["nl", "sel_fix", "sel_train", "gks", "crit5f", "crit20f", "synlog", "synsp", "ident_dense", "ident_train", "ident_crit", "kmin"], "tableS_time_review.tex",
      r"Computing time of the additional analyses, for every problem: nonlinear re-estimation of the final subset in the 15 scenarios for the problems selected with the first-order $e_{\mathrm{fit}}$; the complete selection repeated with the fixed scenario set and on the training outputs; standard pivoted QR; the admissibility tests of all criteria with the fixed scenario set at $\pm$5\% (including the synthetic seeds) and $\pm$20\%; the synthetic comparison with log-uniform and sparse truths (all criteria, ten seeds); and the identifiability profiles with 20 points per side and of the subsets selected on the training outputs; the identifiability profiles of the subsets of Brun, Morris, pivoted QR and profile likelihood (sum over the four criteria); and the test of the minimum subset size $k_{\min}=2$ (all its tests for the best single parameters; for Smith and Schwen the robustness was split into one process per perturbation size and its time is taken from the checkpoint files, \texttt{analysis/kmin\_times.py}). The check of the identifiability hypotheses over the admissible set (512 Sobol points and adversarial search for five radii) did not record times per problem and is not included; it took about 3~h of elapsed time on an 88-core server." + COMMON,
      "tab:timereview")

# summary per analysis
rows, tot_all = [], 0.0
for k, lab in LAB.items():
    v = {s: t for s, t in T[k].items() if ok(t) and t > 0}
    if not v:
        continue
    vals = list(v.values()); smax = max(v, key=v.get)
    tot_all += sum(vals) if k not in ELAPSED else 0
    rows.append([lab, str(len(v)), fmt(statistics.median(vals)), f"{fmt(v[smax])} ({short(smax)})", f"{sum(vals) / 3600:.1f}"])
head = ["Analysis", "Problems", "Median", "Maximum (problem)", "Total (h)"]
s = [r"\begin{longtable}{@{}lrrlr@{}}",
     r"\caption{Summary of the computing time per analysis over the problems of Supplementary Tables~\ref{tab:timemethod}--\ref{tab:timereview}: number of problems, median and maximum time per problem and total time, in processor time where an analysis consists of independent tasks; the elapsed time of profile likelihood and the selection on one core are listed but not added to the total.}\label{tab:timesummary}\\",
     r"\toprule", " & ".join(head) + r" \\", r"\midrule", r"\endfirsthead", r"\toprule", " & ".join(head) + r" \\", r"\midrule", r"\endhead"]
s += [" & ".join(r) + r" \\" for r in rows] + [r"\midrule", rf"All analyses & & & & {tot_all / 3600:.0f} \\", r"\bottomrule", r"\end{longtable}"]
(TAB / "tableS_time_summary.tex").write_text("\n".join(s) + "\n", encoding="utf-8"); print("written tableS_time_summary.tex")

# breakdown in hours by purpose: the method itself, its evaluation, the comparison with other criteria
hours = lambda keys: sum(t for k in keys for t in T[k].values() if ok(t) and t > 0) / 3600
GROUPS = [
    ("The method itself", [
        ("Selection of the subset (34 problems, sensitivities in parallel)", ["sel_par"]),
        ("Nonlinear verification of the final subset (six problems selected to first order)", ["nl"])]),
    ("Evaluation of the method", [
        ("Selection repeated with fixed scenarios and on the training outputs", ["sel_fix", "sel_train"]),
        ("Sensitivity to the method settings (15 variants)", ["settings"]),
        (r"Robustness to the size of parameter changes ($\pm$1\% to $\pm$50\%, paired and independent directions)", ["rob", "rob_ind"]),
        ("Single-parameter subsets", ["single"]),
        ("Validation on real data (external and nested)", ["ext", "nest"]),
        (r"Synthetic experiments ($\pm$5\%, $\pm$20\%, $\pm$50\%) and true signal", ["syn20", "syn5", "syn50", "signal"]),
        ("Identifiability of the selected parameters: profiles (10 points per side)", ["ident"]),
        ("Identifiability: profiles with 20 points per side", ["ident_dense"]),
        ("Identifiability: subsets selected on the training outputs", ["ident_train"]),
        ("Minimum subset size: best single parameters through robustness, admissibility at $\\pm$20\\%, synthetic and identifiability tests", ["kmin"])]),
    ("Comparison with other criteria", [
        ("Profile likelihood of the full model (processor time)", ["pl_cpu"]),
        (r"Admissibility and synthetic tests of the subsets of all criteria ($\pm$5\% and $\pm$20\%, both scenario sets)", ["crit5", "crit20", "crit5f", "crit20f"]),
        ("Synthetic comparison with log-uniform and sparse truths (all criteria)", ["synlog", "synsp"]),
        ("Identifiability of the subsets of Brun, Morris, pivoted QR and profile likelihood (profiles)", ["ident_crit"]),
        ("Selection by pivoted QR (both variants), Brun, Morris, random subsets and calibration only", ["qr", "gks", "bm", "rand", "cal"])]),
]
used = {k for _, items in GROUPS for _, ks in items for k in ks}
assert used | ELAPSED == set(LAB), set(LAB) - used - ELAPSED      # every analysis is in exactly one row
s = [r"\begin{longtable}{@{}>{\raggedright\arraybackslash}p{11.2cm}rr@{}}",
     r"\caption{Processor time of all the analyses reported in the paper, in hours, grouped by purpose. Processor time is the sum over all cores of the times recorded by each task in the final runs (Supplementary Tables~\ref{tab:timemethod}--\ref{tab:timereview}); because the analyses ran in parallel on servers with 88 to 256 cores and on an 8-core workstation, the elapsed time was much shorter. Earlier runs superseded by corrections of the code, repeated runs, the compilation of the Lean proofs and the check of the identifiability hypotheses over the admissible set (about 3~h of elapsed time on an 88-core server, not recorded per task) are not included.}\label{tab:timebreakdown}\\",
     r"\toprule", r"Analysis & Hours & Share \\", r"\midrule", r"\endfirsthead",
     r"\toprule", r"Analysis & Hours & Share \\", r"\midrule", r"\endhead"]
for g, items in GROUPS:
    sub = sum(hours(ks) for _, ks in items)
    s.append(rf"\multicolumn{{3}}{{@{{}}l}}{{\textbf{{{g}}}}} \\")
    for lab, ks in items:
        h = hours(ks)
        s.append(rf"\quad {lab} & {h:.1f} & {100 * h / (tot_all / 3600):.1f}\% \\")
    s.append(rf"\quad \emph{{Subtotal}} & \emph{{{sub:.1f}}} & \emph{{{100 * sub / (tot_all / 3600):.1f}\%}} \\")
    s.append(r"\addlinespace")
    print(f"  group {g}: {sub:.1f} h")
s += [r"\midrule", rf"\textbf{{All analyses}} & \textbf{{{tot_all / 3600:.1f}}} & 100\% \\", r"\bottomrule", r"\end{longtable}"]
(TAB / "tableS_time_breakdown.tex").write_text("\n".join(s) + "\n", encoding="utf-8"); print("written tableS_time_breakdown.tex")

# numbers for the main text
med = lambda k, ss=None: statistics.median([t for s, t in T[k].items() if ok(t) and t > 0 and (ss is None or s in ss)])
sel = {s: t for s, t in T["sel_par"].items() if ok(t)}
pl = {s: t for s, t in T["pl"].items() if ok(t) and t > 0}
both = [s for s in pl if s in sel]
print(f"selection (parallel): median {fmt(med('sel_par'))}, under 10 min in {sum(t < 600 for t in sel.values())} of {len(sel)}, max {fmt(max(sel.values()))} ({short(max(sel, key=sel.get))})")
print(f"identifiability: median {fmt(med('ident'))} over {len(T['ident'])}")
print(f"profile likelihood full model: {len(pl)} problems, median {fmt(statistics.median(pl.values()))}; "
      f"ours faster in {sum(sel[s] < pl[s] for s in both)} of {len(both)}; median ratio PL/ours {statistics.median([pl[s] / sel[s] for s in both]):.0f}")
print(f"total of all analyses: {tot_all / 3600:.0f} h")
for k in LAB:
    v = [t for t in T[k].values() if ok(t) and t > 0]
    if v:
        print(f"  {k}: total {sum(v) / 3600:.1f} h over {len(v)}")
per = collections.defaultdict(float)
for k in LAB:
    if k in ELAPSED:
        continue
    for s, t in T[k].items():
        if ok(t):
            per[s] += t
top = sorted(per.items(), key=lambda x: -x[1])[:5]
print("per problem (top 5):", [(short(s), round(t / 3600, 1)) for s, t in top],
      f"share {100 * sum(t for _, t in top) / sum(per.values()):.0f}%; median per problem {fmt(statistics.median(per.values()))}")
