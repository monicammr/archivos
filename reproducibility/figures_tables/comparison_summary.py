#!/usr/bin/env python3
"""
Summary tables (Markdown) of the comparison of selection criteria: profile likelihood,
admissibility, synthetic experiment with 20 seeds (rates, binomial test, Wilcoxon), Wilcoxon on real
data and run times. They contain the counts quoted in the Results and Discussion.
Output: output/comparison/1_... .md to 5_... .md
Usage: python comparison_summary.py
"""
import sys, json, glob, os, math, re, collections
from pathlib import Path
import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
from common import RESULTS as R, FIG, TAB, OUT as _OUT
OUT = _OUT / "comparison"
OUT.mkdir(parents=True, exist_ok=True)
TAU = math.sqrt(1 - 0.9 ** 2)
METODOS = ["ours", "qr", "brun", "morris", "perfil"]
NOMBRE = {"ours": "Nuestro método", "qr": "QR pivotado", "brun": "Brun", "morris": "Morris",
          "perfil": "Verosimilitud perfilada"}
NO_FIABLE_PERFIL = set()        # Raia convergió con 4 re-ajustes (antes de esto se excluía)
PROVISIONAL_PERFIL = set()      # Isensee terminó sus 3 rondas (mejora residual 1,16)


def L(sub):
    out = {}
    for f in glob.glob(str(R / sub / "*.json")):
        try:
            out[Path(f).stem] = json.loads(Path(f).read_text(encoding="utf-8"))
        except Exception:
            pass
    return out


def ok(x):
    return isinstance(x, (int, float)) and math.isfinite(x)


def g(x, d=3):
    return "–" if not ok(x) else (f"{x:.{d}g}" if abs(x) < 1e4 and abs(x) >= 1e-3 or x == 0 else f"{x:.2e}")


def corto(s):
    return s.split("_")[0]


def escribe(nombre, lineas):
    (OUT / nombre).write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print("\n".join(lineas) + "\n")


# ── 1. verosimilitud perfilada ────────────────────────────────────────────────────
pf = L("profile_likelihood")
an = L("nested_validation")
qr = L("qr_selection")
mb = L("brun_morris")
lin = ["# Verosimilitud perfilada por sistema", "",
       "Ident.: el perfil supera Δχ² = 3,84 a ambos lados; 1 lado: sólo a uno; planos: a ninguno. "
       "χ²/n en la prueba con los k parámetros de cada método (datos reales, ancla θ₀).", "",
       "| Sistema | k | Bio | Ident. | 1 lado | Planos | χ²/n nuestro | χ²/n QR | χ²/n perfilada | En común con el nuestro | Nota |",
       "|---|---|---|---|---|---|---|---|---|---|---|"]
ids = []
for s, r in sorted(pf.items()):
    if "no_evaluable" in r:
        lin.append(f"| {corto(s)} | | | | | | | | | | No evaluable: {r['no_evaluable']} |")
        continue
    nota = ("No fiable: el mínimo no convergió tras 3 re-ajustes" if s in NO_FIABLE_PERFIL else
            "Provisional: sólo terminó la primera ronda" if s in PROVISIONAL_PERFIL else
            (f"{r.get('rondas_reajuste', 0)} re-ajustes del mínimo" if r.get("rondas_reajuste") else "")
            + (f"; mejora residual {-r['dchi2_minimo_perfiles']:.2f} sin re-ajustar" if (r.get("dchi2_minimo_perfiles") or 0) < -1 else ""))
    lin.append(f"| {corto(s)} | {r['k']} | {r['n_bio']} | {r['n_identificables']} | "
               f"{r['n_no_identificables_practicos']} | {r['n_planos']} | {g(r.get('chi2_ours'))} | "
               f"{g(r.get('chi2_qr'))} | {g(r.get('chi2_perfil'))} | {r['overlap_perfil_ours']} | {nota} |")
    if s not in NO_FIABLE_PERFIL | PROVISIONAL_PERFIL:
        ids.append((r["n_identificables"], r["n_bio"]))
if ids:
    n_id = [a for a, _ in ids]
    lin += ["", f"Parámetros identificables (sin los no fiables ni provisionales, {len(ids)} sistemas): "
            f"mediana {np.median(n_id):g} por sistema (fracción mediana {np.median([a / b for a, b in ids]):.0%}); "
            f"{sum(a == 0 for a in n_id)} sistemas sin ninguno; {sum(a <= 2 for a in n_id)} con 2 o menos."]
escribe("1_verosimilitud_perfilada.md", lin)

# ── 2. admisibilidad ──────────────────────────────────────────────────────────────
A = collections.defaultdict(dict)
for f in glob.glob(str(R / "criteria_tests" / "*__adm.json")):
    d = json.loads(Path(f).read_text(encoding="utf-8"))
    A[d["sistema"]][d["metodo"]] = d
ref = L("selection")
lin = ["# Admisibilidad de los subconjuntos de cada método", "",
       f"Mediana de e_fit en 15 escenarios a ±5 % (semilla 42); admisible si ≤ {TAU:.3f} (marcado con ✓). "
       "Los 8 sistemas grandes usan la aproximación de primer orden, como en el artículo.", "",
       "| Sistema | " + " | ".join(NOMBRE[m] for m in METODOS) + " | e_fit del artículo (nuestro) |",
       "|---|" + "---|" * (len(METODOS) + 1)]
cuenta = {m: [0, 0] for m in METODOS}
for s in sorted(A):
    fila = []
    for m in METODOS:
        d = A[s].get(m)
        if not d or "eajuste_med" not in d:
            fila.append("–"); continue
        fila.append(f"{d['eajuste_med']:.3f}{' ✓' if d['admisible'] else ''}")
        cuenta[m][0] += bool(d["admisible"]); cuenta[m][1] += 1
    lin.append(f"| {corto(s)} | " + " | ".join(fila) + f" | {g(ref.get(s, {}).get('eajuste_med'))} |")
lin += ["", "| Método | Admisibles |", "|---|---|"] + \
       [f"| {NOMBRE[m]} | {a} de {b} |" for m, (a, b) in cuenta.items()]
escribe("2_admisibilidad.md", lin)

# ── 3. sintético (20 semillas) ────────────────────────────────────────────────────
S = collections.defaultdict(lambda: collections.defaultdict(dict))
for f in glob.glob(str(R / "criteria_tests" / "*__sint_*.json")):
    d = json.loads(Path(f).read_text(encoding="utf-8"))
    if "B_epred_red" in d:
        S[d["sistema"]][d["metodo"]][d["semilla"]] = d
for f in glob.glob(str(R / "synthetic_seeds" / "*" / "s*.json")):
    d = json.loads(Path(f).read_text(encoding="utf-8"))
    if "B_epred_red" in d:
        S[d["sistema"]]["ours"][d["semilla"]] = d
SEM = range(42, 62)
casos, sist = [], set()
for s in S:
    for k in SEM:
        ds = [S[s][m].get(k) for m in METODOS]
        if all(d and ok(d["B_epred_red"]) for d in ds) and ds[0]["B_chi2_test_theta0"] >= 2:
            casos.append({m: d["B_epred_red"] for m, d in zip(METODOS, ds)} | {"s": s, "k": k}); sist.add(s)
lin = ["# Experimento sintético sin fuga: cinco métodos, 20 semillas (42–61)", "",
       f"Casos comunes a los cinco métodos y con señal (χ²/n de θ₀ ≥ 2): {len(casos)} ({len(sist)} sistemas). "
       f"Acierto: e_pred ≤ {TAU:.3f}.", "",
       "| Método | Aciertos | Mediana por semilla | Rango por semilla |", "|---|---|---|---|"]
for m in METODOS:
    a = sum(c[m] <= TAU for c in casos)
    fr = [np.mean([c[m] <= TAU for c in casos if c["k"] == k]) for k in SEM if any(c["k"] == k for c in casos)]
    lin.append(f"| {NOMBRE[m]} | {a} de {len(casos)} ({a / len(casos):.0%}) | {np.median(fr):.0%} | "
               f"{min(fr):.0%}–{max(fr):.0%} |")
lin += ["", "## Acierto: casos en que sólo uno de los dos acierta (prueba binomial exacta)", "",
        "Las 20 semillas de un mismo sistema no son independientes: estos valores de p son optimistas.", "",
        "| Nuestro método contra | Sólo el nuestro acierta | Sólo el otro acierta | p |", "|---|---|---|---|"]
for m in METODOS[1:]:
    b = sum(c["ours"] <= TAU < c[m] for c in casos)
    cc = sum(c[m] <= TAU < c["ours"] for c in casos)
    lin.append(f"| {NOMBRE[m]} | {b} | {cc} | {stats.binomtest(b, b + cc).pvalue:.2g} |")
lin += ["", "## Error de predicción por sistema (Wilcoxon pareado)", "",
        "Estadístico por sistema: mediana, sobre las semillas, de log(e_pred del otro / e_pred nuestro); "
        "todas las semillas con al menos 10 pares. Mayor que 0: nuestro método con menor error.", "",
        "| Nuestro método contra | Sistemas | Nuestro mejor | Peor | Igual | Cociente mediano | p |",
        "|---|---|---|---|---|---|---|"]
for m in METODOS[1:]:
    v = []
    for s in S:
        r = [math.log(S[s][m][k]["B_epred_red"] / S[s]["ours"][k]["B_epred_red"]) for k in SEM
             if k in S[s][m] and k in S[s]["ours"] and ok(S[s][m][k]["B_epred_red"])
             and ok(S[s]["ours"][k]["B_epred_red"]) and S[s][m][k]["B_epred_red"] > 0
             and S[s]["ours"][k]["B_epred_red"] > 0]
        if len(r) >= 10:
            v.append(np.median(r))
    v = np.array(v)
    nz = v[np.abs(v) > 1e-9]
    p = stats.wilcoxon(nz).pvalue if len(nz) >= 5 else float("nan")
    lin.append(f"| {NOMBRE[m]} | {len(v)} | {int((v > 1e-9).sum())} | {int((v < -1e-9).sum())} | "
               f"{int((np.abs(v) <= 1e-9).sum())} | {math.exp(np.median(v)):.2f} | {p:.2g} |")
escribe("3_sintetico_20_semillas.md", lin)

# ── 4. Wilcoxon en datos reales ───────────────────────────────────────────────────
al, va = L("random_subsets"), L("calibration_only")
ours = {s: d.get("chi2_test_red_original") for s, d in an.items()}
otros = {"QR pivotado": {s: d.get("chi2_qr") for s, d in qr.items()},
         "Brun": {s: d.get("chi2_brun") for s, d in mb.items()},
         "Morris": {s: d.get("chi2_morris") for s, d in mb.items()},
         "Verosimilitud perfilada": {s: d.get("chi2_perfil") for s, d in pf.items() if s not in NO_FIABLE_PERFIL},
         "Subconjunto aleatorio (mediana de 20)": {s: d.get("chi2_rand_median") for s, d in al.items()},
         "Conjunto vacío (sólo calibración)": {s: d.get("chi2_vacio") for s, d in va.items()},
         "Modelo completo (entrenamiento)": {s: d.get("chi2_test_full_train") for s, d in an.items()},
         "Reducido anidado (sin fuga)": {s: d.get("chi2_test_red_nested") for s, d in an.items()},
         "θ₀ publicado": {s: d.get("chi2_test_theta0") for s, d in an.items()}}
lin = ["# Datos reales: Wilcoxon pareado sobre el χ²/n de prueba", "",
       "Estadístico por sistema: log(χ²_otro / χ²_nuestro). Empate: diferencia menor del 5 %. "
       "Cociente mediano menor que 1: el otro método tiene menor χ² (predice mejor). "
       "Todas las variantes salvo el anidado usan θ₀ (estimado con todos los datos) como ancla.", "",
       "| Nuestro método contra | Sistemas | Nuestro mejor | Peor | Empate | Cociente mediano | p |",
       "|---|---|---|---|---|---|---|"]
e5 = math.log(1.05)
for nom, dic in otros.items():
    v = np.array([math.log(dic[s] / ours[s]) for s in ours
                  if s in dic and ok(dic[s]) and ok(ours[s]) and dic[s] > 0 and ours[s] > 0])
    nz = v[np.abs(v) > 1e-12]
    p = stats.wilcoxon(nz).pvalue if len(nz) >= 5 else float("nan")
    lin.append(f"| {nom} | {len(v)} | {int((v > e5).sum())} | {int((v < -e5).sum())} | "
               f"{int((np.abs(v) <= e5).sum())} | {math.exp(np.median(v)):.2f} | {p:.2g} |")
escribe("4_wilcoxon_datos_reales.md", lin)

# ── 5. tiempos ────────────────────────────────────────────────────────────────────
tp, ts = L("timing_complete/parallel"), L("timing_complete/single_core")
fx = L("timing_complete/parallel_corrected_code")
t_pf = {}
if True:
    for line in [l for n in ("round0.log", "large_problems.log") if (R / "profile_likelihood" / "logs" / n).exists() for l in (R / "profile_likelihood" / "logs" / n).read_text(encoding="utf-8", errors="ignore").splitlines()]:
        if '"terminado": true' in line:
            d = json.loads(line); t_pf[d["sistema"]] = d["seg_total"]
lin = ["# Tiempo de cómputo (segundos de reloj)", "",
       "Servidor de 128 núcleos, compartido por varios cálculos a la vez (los tiempos están inflados, "
       "nunca subestimados). Nuestro método completo = selección + admisibilidad + poda, desde cero.", "",
       "Los 8 sistemas linealizados se repitieron con el código corregido (columnas de calibración "
       "en J); la última columna indica si esa corrida reproduce la selección publicada.", "",
       "| Sistema | p | Nuestro método, paralelo | Nuestro método, 1 núcleo | Verosimilitud perfilada (1.ª ronda, 120 núcleos) | ¿Misma selección que el artículo? (código anterior) | Código corregido |",
       "|---|---|---|---|---|---|---|"]
for s in sorted(set(tp) | set(ts) | set(ref)):
    d = tp.get(s) or ts.get(s) or {}
    igual = ("sí" if d.get("S") == ref.get(s, {}).get("S") else "**no**") if d else "–"
    lin.append(f"| {corto(s)} | {ref.get(s, {}).get('p', '–')} | {g(tp.get(s, {}).get('segundos'))} | "
               f"{g(ts.get(s, {}).get('segundos'))} | {g(t_pf.get(s))} | {igual} | "
               + (("sí" if fx[s].get("S") == ref.get(s, {}).get("S") else "**no**") + f" ({g(fx[s].get('segundos'))} s)" if s in fx else "–") + " |")
lin += ["", "Los tiempos de la verosimilitud perfilada no incluyen el primer ajuste completo de los "
        "sistemas que ya lo tenían de un intento anterior ni las rondas de corrección del mínimo."]
escribe("5_tiempos.md", lin)
