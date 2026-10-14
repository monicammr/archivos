#!/usr/bin/env python3
"""
Tablas del suplemento para la comparación de métodos (14 de octubre de 2026), generadas a partir
de los resultados. Escribe un archivo .tex por tabla en paper/scirep/tables/.

Uso: python tablas_suplemento.py [carpeta_resultados] [carpeta_tablas]
"""
import sys, json, glob, math, collections
from pathlib import Path
import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
R = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "resultados"
T = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE.parent / "paper" / "scirep" / "tables"
TAU = math.sqrt(1 - 0.81)
M = ["ours", "qr", "brun", "morris", "perfil"]
NOM = {"ours": "Ours", "qr": "QR", "brun": "Brun", "morris": "Morris", "perfil": "Profile"}
ok = lambda x: isinstance(x, (int, float)) and math.isfinite(x)


def L(sub):
    out = {}
    for f in glob.glob(str(R / sub / "*.json")):
        try:
            out[Path(f).stem] = json.loads(Path(f).read_text(encoding="utf-8"))
        except Exception:
            pass
    return out


def corto(s):
    return s.split("_")[0].replace("SalazarCavazos", "Salazar-Cavazos")


def esc(s):
    return str(s).replace("_", "\\_\\allowbreak{}").replace(">", "$>$")


def num(x, d=3):
    if not ok(x):
        return "--"
    if x == 0:
        return "0"
    if 1e3 <= abs(x) < 1e4:
        return f"{x:,.0f}"
    if 1e-3 <= abs(x) < 1e3:
        return f"{x:.{d}g}"
    e = int(math.floor(math.log10(abs(x))))
    return f"${x / 10 ** e:.1f}\\times10^{{{e}}}$"


def escribe(nombre, texto):
    (T / nombre).write_text(texto, encoding="utf-8")
    print("escrita", nombre)


def longtable(spec, caption, label, cab, filas, nota=None, grupo=None):
    n = len(cab)
    g = [grupo] if grupo else []
    s = [f"\\begin{{longtable}}{{{spec}}}", f"\\caption{{{caption}}}\\label{{{label}}}\\\\", "\\toprule"] + g + [
         " & ".join(cab) + " \\\\", "\\midrule", "\\endfirsthead",
         f"\\multicolumn{{{n}}}{{@{{}}l}}{{\\emph{{(continued)}}}}\\\\", "\\toprule"] + g + [
         " & ".join(cab) + " \\\\", "\\midrule", "\\endhead"]
    s += [" & ".join(f) + " \\\\" for f in filas]
    s += ["\\bottomrule", "\\end{longtable}"]
    if nota:
        s += ["\\vspace{-0.6\\baselineskip}{\\footnotesize " + nota + "}\\par"]
    return "\n".join(s) + "\n"


pf, an, qr, mb = L("control_perfil"), L("validacion_anidada"), L("comparacion_brun"), L("control_morris_brun")
al, va, ref = L("control_aleatorio"), L("control_vacio"), L("reclasificacion_salidas_bio_poda")

# ── 1. verosimilitud perfilada ────────────────────────────────────────────────────
filas = []
for s, r in sorted(pf.items()):
    if "no_evaluable" in r:
        filas.append([corto(s), "\\multicolumn{8}{l}{\\emph{not evaluated: " + esc(r["no_evaluable"]).replace("parámetros libres", "free parameters").replace("sin división entrenamiento/prueba", "no training/test split") + "}}"])
        continue
    nota = []
    if r.get("rondas_reajuste"):
        nota.append(f"{r['rondas_reajuste']} re-fits")
    if (r.get("dchi2_minimo_perfiles") or 0) < -1:
        nota.append(f"res. {-r['dchi2_minimo_perfiles']:.2f}")
    filas.append([corto(s), str(r["k"]), str(r["n_bio"]), str(r["n_identificables"]),
                  str(r["n_no_identificables_practicos"]), str(r["n_planos"]),
                  ", ".join(esc(x) for x in r["S_perfil"]), str(r["overlap_perfil_ours"]),
                  "; ".join(nota) or "--"])
escribe("tableS_perfil.tex", longtable(
    "@{}lrrrrr>{\\raggedright}p{4.0cm}rl@{}",
    "Profile likelihood of the biological parameters (training data). Ident.: profile above $\\Delta\\chi^2=3.84$ on both sides; one side: only on one side; flat: on neither side. Selected: the $k$ parameters with the narrowest profile confidence interval. Common: parameters shared with the subset of our method. Re-fits: times the full model was re-estimated because a profile point improved the optimum; residual: remaining improvement (in units of $\\chi^2$) after the last re-fit.",
    "tab:perfil", ["Problem", "$k$", "Bio", "Ident.", "One side", "Flat", "Selected by profile likelihood", "Common", "Note"], filas))

# ── 2. selecciones de los cinco criterios ─────────────────────────────────────────
filas = []
for s in sorted(set(qr) | set(mb) | set(pf)):
    if s not in ref or not ref[s].get("admisible"):
        continue
    sel = {"ours": ref[s].get("S"), "qr": qr.get(s, {}).get("S_qr"), "brun": mb.get(s, {}).get("S_brun"),
           "morris": mb.get(s, {}).get("S_morris"), "perfil": pf.get(s, {}).get("S_perfil")}
    filas.append([corto(s)] + [(", ".join(esc(x) for x in v) if v else "--") for v in sel.values()])
escribe("tableS_selecciones.tex", longtable(
    "@{}l>{\\raggedright}p{2.6cm}>{\\raggedright}p{2.6cm}>{\\raggedright}p{2.6cm}>{\\raggedright}p{2.6cm}>{\\raggedright\\arraybackslash}p{2.6cm}@{}",
    "Biological parameters selected by each criterion (same number $k$ for all). --, criterion not computed for the problem.",
    "tab:selecciones", ["Problem", "Ours", "Pivoted QR", "Brun", "Morris", "Profile likelihood"], filas))

# ── 3. datos reales: χ² de prueba de todas las variantes ─────────────────────────
cols = [("ours", lambda s: an.get(s, {}).get("chi2_test_red_original")),
        ("vac", lambda s: va.get(s, {}).get("chi2_vacio")),
        ("rand", lambda s: al.get(s, {}).get("chi2_rand_median")),
        ("qr", lambda s: qr.get(s, {}).get("chi2_qr")),
        ("brun", lambda s: mb.get(s, {}).get("chi2_brun")),
        ("morris", lambda s: mb.get(s, {}).get("chi2_morris")),
        ("perfil", lambda s: pf.get(s, {}).get("chi2_perfil")),
        ("full", lambda s: an.get(s, {}).get("chi2_test_full_train")),
        ("th0", lambda s: an.get(s, {}).get("chi2_test_theta0"))]
filas = []
for s in sorted(an):
    v = [f(s) for _, f in cols]
    sel = [x for x in v[:7] if ok(x)]
    mejor = min(sel) if sel else None
    filas.append([corto(s)] + [("\\textbf{" + num(x) + "}" if i < 7 and ok(x) and x == mejor and not x == 0 else num(x))
                               for i, x in enumerate(v)])
escribe("tableS_realdata.tex", longtable(
    "@{}lrrrrrrrrr@{}",
    "Test $\\chi^2/n$ on the held-out experiments (real data) of every selection criterion and baseline. All variants keep the non-selected parameters at $\\theta_0$ except the full model, which re-estimates all parameters on the training data. Bold: lowest value among the seven selection variants. $\\theta_0$, published estimate, obtained using all data including the test experiments.",
    "tab:realdata", ["Problem", "Ours", "Calib. only", "Random", "QR", "Brun", "Morris", "Profile", "Full", "$\\theta_0$"], filas))

# ── 4. Wilcoxon en datos reales ───────────────────────────────────────────────────
ours = {s: an[s].get("chi2_test_red_original") for s in an}
otros = [("Pivoted QR", {s: qr[s].get("chi2_qr") for s in qr}),
         ("Brun", {s: mb[s].get("chi2_brun") for s in mb}),
         ("Morris", {s: mb[s].get("chi2_morris") for s in mb}),
         ("Profile likelihood", {s: pf[s].get("chi2_perfil") for s in pf}),
         ("Random subsets (median of 20)", {s: al[s].get("chi2_rand_median") for s in al}),
         ("Calibration only ($k=0$)", {s: va[s].get("chi2_vacio") for s in va}),
         ("Full model re-estimated on training data", {s: an[s].get("chi2_test_full_train") for s in an}),
         ("Reduced model, leakage-free nested", {s: an[s].get("chi2_test_red_nested") for s in an}),
         ("Published estimate $\\theta_0$", {s: an[s].get("chi2_test_theta0") for s in an})]
filas, e5 = [], math.log(1.05)
for nom, d in otros:
    v = np.array([math.log(d[s] / ours[s]) for s in ours if s in d and ok(d[s]) and ok(ours[s]) and d[s] > 0 and ours[s] > 0])
    nz = v[np.abs(v) > 1e-12]
    p = stats.wilcoxon(nz).pvalue
    filas.append([nom, str(len(v)), str(int((v > e5).sum())), str(int((v < -e5).sum())),
                  str(int((np.abs(v) <= e5).sum())), f"{math.exp(np.median(v)):.2f}", f"{p:.2g}"])
escribe("tableS_wilcoxon_real.tex", longtable(
    "@{}lrrrrrr@{}",
    "Real data: paired comparison of the test $\\chi^2/n$ of our method with each alternative over problems. Better/worse: our method lower/higher by more than 5\\%; equal: within 5\\%. Median ratio: alternative over ours (below 1, the alternative predicts better). $p$: two-sided Wilcoxon signed-rank test on the log ratios.",
    "tab:wilcoxonreal", ["Our method compared with", "Problems", "Ours better", "Ours worse", "Equal", "Median ratio", "$p$"], filas))

# ── 5. admisibilidad ±5 % y ±20 % ─────────────────────────────────────────────────
def adm(sub):
    A = collections.defaultdict(dict)
    for f in glob.glob(str(R / sub / "*__adm.json")):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        if "eajuste_med" in d:
            A[d["sistema"]][d["metodo"]] = d
    return A
A5, A20 = adm("control_admis_sint"), adm("control_admis_sint_nivel020")
filas = []
for s in sorted(A5):
    f = [corto(s)]
    for A in (A5, A20):
        for m in M:
            d = A.get(s, {}).get(m)
            f.append("--" if not d else (f"{min(d['eajuste_med'], d['erel_med']):.2f}" + ("$^{\\checkmark}$" if d["admisible"] else "")))
    filas.append(f)
cuenta = []
for A in (A5, A20):
    for m in M:
        v = [A[s][m]["admisible"] for s in A if m in A[s]]
        cuenta.append(f"{sum(v)}/{len(v)}")
filas.append(["\\midrule Admissible"] + cuenta)
escribe("tableS_admis.tex", longtable(
    "@{}lrrrrr|rrrrr@{}",
    "Admissibility of the subsets of every criterion: smaller of the median $e_{\\mathrm{fit}}$ and the median $e_{\\mathrm{rel}}$ over 15 scenarios (the quantity compared with $\\tau_e=0.436$ by the method), for parameter changes of $\\pm$5\\% (left) and $\\pm$20\\% (right). $\\checkmark$, admissible. The eight problems that the method treats to first order are treated in the same way for every criterion.",
    "tab:admis", ["Problem"] + [NOM[m] for m in M] * 2, filas,
    grupo="& \\multicolumn{5}{c|}{$\\pm$5\\%} & \\multicolumn{5}{c}{$\\pm$20\\%} \\\\"))

filas = []
for nivel, A in (("$\\pm$5\\%", A5), ("$\\pm$20\\%", A20)):
    for m in M[1:]:
        pares = [(A[s]["ours"]["admisible"], A[s][m]["admisible"]) for s in A if "ours" in A[s] and m in A[s]]
        b = sum(o and not x for o, x in pares); c = sum(x and not o for o, x in pares)
        p = stats.binomtest(b, b + c).pvalue if b + c else float("nan")
        filas.append([nivel, {"qr": "Pivoted QR", "brun": "Brun", "morris": "Morris", "perfil": "Profile likelihood"}[m],
                      str(len(pares)), str(b), str(c), f"{p:.2g}"])
escribe("tableS_mcnemar.tex", longtable(
    "@{}llrrrr@{}",
    "Admissibility of our subsets compared with those of each criterion: exact McNemar test over problems (problems in which only one of the two subsets is admissible).",
    "tab:mcnemar", ["Level", "Criterion", "Problems", "Only ours admissible", "Only the other", "$p$"], filas))

# ── 6. sintético: cinco criterios ─────────────────────────────────────────────────
SS = collections.defaultdict(lambda: collections.defaultdict(dict))
for f in glob.glob(str(R / "control_admis_sint" / "*__sint_*.json")):
    d = json.loads(Path(f).read_text(encoding="utf-8"))
    if ok(d.get("B_epred_red")):
        SS[d["sistema"]][d["metodo"]][d["semilla"]] = d
for f in glob.glob(str(R / "sintetico_semillas" / "*" / "s*.json")):
    d = json.loads(Path(f).read_text(encoding="utf-8"))
    if ok(d.get("B_epred_red")):
        SS[d["sistema"]]["ours"][d["semilla"]] = d
filas, cnt = [], {}
for s in sorted(SS):
    c = {m: [0, 0] for m in M}; med = {m: [] for m in M}
    for k in range(42, 62):
        ds = [SS[s][m].get(k) for m in M]
        if all(ds) and ds[0]["B_chi2_test_theta0"] >= 2:
            for m, d in zip(M, ds):
                c[m][0] += d["B_epred_red"] <= TAU; c[m][1] += 1; med[m].append(d["B_epred_red"])
    if c["ours"][1]:
        cnt[s] = c
        filas.append([corto(s), str(c["ours"][1])] + [f"{c[m][0]} ({np.median(med[m]):.2f})" for m in M])
tot = {m: sum(cnt[s][m][0] for s in cnt) for m in M}; n = sum(cnt[s]["ours"][1] for s in cnt)
filas.append(["\\midrule Total", str(n)] + [f"{tot[m]} ({tot[m] / n:.0%})".replace("%", "\\%") for m in M])
escribe("tableS_synth_methods.tex", longtable(
    "@{}lrrrrrr@{}",
    "Synthetic prediction experiment for the five criteria (20 seeds, cases common to all criteria in which the parameter change exceeded the noise). Each entry: number of cases with $e_{\\mathrm{pred}}\\le\\tau_e$ and, in parentheses, the median $e_{\\mathrm{pred}}$.",
    "tab:synthmethods", ["Problem", "Cases", "Ours", "Pivoted QR", "Brun", "Morris", "Profile"], filas))

sis = sorted(cnt); rng = np.random.default_rng(0)
idx = rng.integers(0, len(sis), size=(10000, len(sis)))
A = {m: np.array([cnt[s][m][0] for s in sis], float) for m in M}; N = np.array([cnt[s][m][1] for s in sis], float)
filas = []
for m in M[1:]:
    dif = A["ours"][idx].sum(1) / N[idx].sum(1) - A[m][idx].sum(1) / N[idx].sum(1)
    obs = (A["ours"].sum() - A[m].sum()) / N.sum()
    lo, hi = np.percentile(dif, [2.5, 97.5]); p = max(min(1, 2 * min((dif <= 0).mean(), (dif >= 0).mean())), 1e-4)
    v = []
    for s in SS:
        r = [math.log(SS[s][m][k]["B_epred_red"] / SS[s]["ours"][k]["B_epred_red"]) for k in range(42, 62)
             if k in SS[s][m] and k in SS[s]["ours"] and SS[s][m][k]["B_epred_red"] > 0 and SS[s]["ours"][k]["B_epred_red"] > 0]
        if len(r) >= 10:
            v.append(np.median(r))
    v = np.array(v); nz = v[np.abs(v) > 1e-9]
    filas.append([{"qr": "Pivoted QR", "brun": "Brun", "morris": "Morris", "perfil": "Profile likelihood"}[m],
                  f"{100 * obs:+.1f}", f"{100 * lo:+.1f} to {100 * hi:+.1f}", f"{p:.2g}",
                  str(len(v)), f"{math.exp(np.median(v)):.2f}", f"{stats.wilcoxon(nz).pvalue:.2g}"])
escribe("tableS_synth_stats.tex", longtable(
    "@{}lrrrrrr@{}",
    "Synthetic experiment, statistics over problems. Left: difference in the fraction of cases with $e_{\\mathrm{pred}}\\le\\tau_e$ (ours minus criterion, percentage points) with a 95\\% confidence interval and $p$-value from resampling whole problems with all their seeds (10,000 replicates). Right: per-problem median over seeds of the ratio $e_{\\mathrm{pred}}$(criterion)/$e_{\\mathrm{pred}}$(ours) (problems with at least 10 seeds), its median and the two-sided Wilcoxon $p$-value.",
    "tab:synthstats", ["Criterion", "Difference", "95\\% CI", "$p$", "Problems", "Median ratio", "$p$"], filas))

# ── 7. sintético con 20 semillas: reducido frente a completo ─────────────────────
res = json.loads((R / "sintetico_semillas" / "RESUMEN.json").read_text(encoding="utf-8"))
filas = []
for r in res["por_sistema"]:
    if not r.get("validas"):
        filas.append([corto(r["sistema"]), "\\multicolumn{6}{l}{\\emph{not evaluable}}"]); continue
    g = lambda x: "--" if x is None else f"{x:.3g}"
    filas.append([corto(r["sistema"]), str(r["validas"]), str(r["con_senal"]), g(r["epred_red_med"]), g(r["epred_full_med"]),
                  f"{r['red_ok_senal']}/{r['con_senal']}", f"{r['red_le_full_senal']}/{r['comparadas_senal']}" if r["comparadas_senal"] else "--"])
escribe("tableS_synth20.tex", longtable(
    "@{}lrrrrrr@{}",
    "Synthetic prediction experiment, reduced and full model, 20 seeds (42--61). Seeds: valid seeds; signal: seeds in which the test $\\chi^2/n$ of $\\theta_0$ on the synthetic data is at least 2. Median $e_{\\mathrm{pred}}$ over valid seeds. Last two columns, over the seeds with signal: reduced model with $e_{\\mathrm{pred}}\\le\\tau_e$, and reduced $e_{\\mathrm{pred}}$ no larger than that of the full model (--, full model not re-estimated: more than 100 free parameters).",
    "tab:synth20", ["Problem", "Seeds", "Signal", "Reduced $e_{\\mathrm{pred}}$", "Full $e_{\\mathrm{pred}}$", "Reduced $\\le\\tau_e$", "Reduced $\\le$ full"], filas))
filas = [[str(c["semilla"]), str(c["evaluables"]), str(c["senal"]), str(c["red_ok"]), str(c["comp"]), str(c["red_le_full"])] for c in res["por_semilla"]]
escribe("tableS_synth20_seeds.tex", longtable(
    "@{}rrrrrr@{}",
    "Synthetic prediction experiment, reduced and full model: counts per seed (seed 42 is the experiment of the earlier version of this study).",
    "tab:synth20seeds", ["Seed", "Problems", "With signal", "Reduced $\\le\\tau_e$", "Compared with full", "Reduced $\\le$ full"], filas))

# ── 8. validación anidada (29 problemas) ─────────────────────────────────────────
filas = []
for s, d in sorted(an.items()):
    o, f, ne, t0 = d["chi2_test_red_original"], d["chi2_test_full_train"], d["chi2_test_red_nested"], d["chi2_test_theta0"]
    filas.append([corto(s) + ("$^\\dagger$" if s.startswith("Chen") else ""), num(o), num(f), num(ne), num(t0),
                  (f"{100 * (ne - f) / f:+.1f}" if ok(f) and f > 0 else "--"), (f"{ne / o:.2f}" if ok(o) and o > 0 else "--")])
escribe("tableS_nested.tex", longtable(
    "@{}lrrrrrr@{}",
    "Leakage-free nested validation (29 problems). $\\chi^2_{\\mathrm{orig}}$: reduced model with the non-selected parameters at $\\theta_0$; $\\chi^2_{\\mathrm{full,train}}$: full model re-estimated on the training data; $\\chi^2_{\\mathrm{nested}}$: reduced model with the non-selected parameters at $\\hat\\theta_{\\mathrm{train}}$; $\\theta_0$: published estimate. $\\Delta$\\%: nested relative to full; last column: nested over original (above 1, the nested reduced model predicts worse).",
    "tab:nested", ["Problem", "$\\chi^2_{\\mathrm{orig}}$", "$\\chi^2_{\\mathrm{full,train}}$", "$\\chi^2_{\\mathrm{nested}}$", "$\\theta_0$", "$\\Delta$\\%", "nested/orig"], filas,
    nota="$^\\dagger$Chen: full-model re-estimation with the finite-difference Jacobian evaluated in parallel and integrator tolerances $10^{-6}/10^{-8}$."))

# ── 9. tiempos ────────────────────────────────────────────────────────────────────
tp, ts, fx = L("reclasificacion_salidas_bio_poda_tiempopar"), L("reclasificacion_salidas_bio_poda_tiemposerie"), L("reclasificacion_salidas_bio_poda_fixcal")
t1, tc = {}, collections.defaultdict(float)
for line in (R / "control_perfil_ronda0" / "control_perfil.log").read_text(encoding="utf-8", errors="ignore").splitlines():
    if '"terminado": true' in line:
        d = json.loads(line); t1[d["sistema"]] = d["seg_total"]
vistos = set()
for lg in [R / "logs_servidor_2026-10-14" / "control_perfil_r.log", R / "logs_servidor_2026-10-14" / "control_perfil_resto.log",
           R / "logs_servidor_2026-10-14" / "correcciones" / "control_perfil_r.log", R / "logs_servidor_2026-10-14" / "correcciones" / "perfil_raia.log"]:
    if not lg.exists():
        continue
    for line in lg.read_text(encoding="utf-8", errors="ignore").splitlines():
        if '"terminado": true' in line:
            d = json.loads(line)
            if d["puntos"] > 0 and (d["sistema"], d["seg_total"]) not in vistos:
                vistos.add((d["sistema"], d["seg_total"])); tc[d["sistema"]] += d["seg_total"]
seg = lambda x: "--" if not ok(x) else (f"{x:.1f}" if x < 100 else f"{x:,.0f}")
filas = []
for s in sorted(ref):
    par = (fx.get(s) or tp.get(s) or {}).get("segundos")
    filas.append([corto(s), str(ref[s].get("p", "--")), seg(par), seg(ts.get(s, {}).get("segundos")),
                  seg(t1.get(s)), seg(t1[s] + tc[s]) if s in t1 and tc.get(s) else ("--" if s not in t1 else seg(t1[s])),
                  "infeasible" if pf.get(s, {}).get("no_evaluable", "").count("PL_PMAX") else ""])
escribe("tableS_tiempos.tex", longtable(
    "@{}lrrrrrl@{}",
    "Computation time (seconds of wall-clock time) of our complete method (selection, admissibility test and backward elimination, run from scratch without cached results) with the sensitivity computations in parallel and on a single core, and of profile likelihood with all profile points of a problem computed in parallel on 120 cores (first round, and including the re-estimations of the optimum). All runs shared a 128-core server with other computations, so the times are upper bounds. For the eight problems treated to first order the parallel time is that of the corrected code (Supplementary Note \\textit{Reproducibility package}).",
    "tab:tiempos", ["Problem", "$p$", "Ours, parallel", "Ours, 1 core", "Profile, 1st round", "Profile, total", ""], filas))
