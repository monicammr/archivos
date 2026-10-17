#!/usr/bin/env python3
"""Cifras del texto principal calculadas a partir de results/ (para comprobar el texto tras cada cambio).

Uso: python main_text_numbers.py
"""
import json, math, glob, os, collections, statistics
from pathlib import Path
import numpy as np
from common import RESULTS as RES, load_validation, EXCLUDE_ADMISSIBILITY

T = float(np.sqrt(1 - 0.81))
J = lambda p: json.loads(Path(p).read_text(encoding="utf-8"))
ok = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)

SEL = {Path(f).stem: J(f) for f in glob.glob(str(RES / "selection" / "*.json"))}
ADM = sorted(s for s, d in SEL.items() if d.get("admisible"))
print(f"admisibles: {len(ADM)} de {len(SEL)}; no admisibles: {sorted(set(SEL) - set(ADM))}")
print("  |S| = 2:", sum(len(SEL[s]['S']) == 2 for s in ADM), "; etapa 1:", sum(SEL[s].get('etapa') == 'Stage 1' for s in ADM))
print("  e_rel > tau_e:", sum(SEL[s].get('erel_med', 0) > T for s in ADM))
print("  primer orden (linealizado):", sorted(s.split('_')[0] for s in ADM if 'linealizado' in SEL[s].get('eajuste_metodo', '')))

# identificabilidad del subconjunto (perfil del problema reducido)
PI = RES / "identifiability" / "profiles"
todos, npar, nid = 0, 0, 0
for s in ADM:
    f = PI / f"{s}.json"
    if not f.exists():
        print("  sin perfil de identificabilidad:", s); continue
    d = J(f); todos += bool(d.get("todos_identificables")); npar += len(SEL[s]["S"]); nid += d.get("n_identificables", 0)
print(f"identificabilidad: todos identificables en {todos} de {len(ADM)}; parámetros {nid} de {npar}")

# validación con datos reales (una sola ejecución: nested_validation)
V = load_validation()
comp = [s for s in ADM if s in V and ok(V[s].get("A_chi2_test_red")) and ok(V[s].get("A_chi2_test_full"))]
mejor = [s for s in comp if V[s]["A_chi2_test_red"] <= 1.05 * V[s]["A_chi2_test_full"]]
print(f"validación real: reducido <= 1,05 completo en {len(mejor)} de {len(comp)}; peores: {sorted(set(comp) - set(mejor))}")
t0 = [s for s in comp if ok(V[s].get("A_chi2_test_theta0")) and V[s]["A_chi2_test_theta0"] < V[s]["A_chi2_test_red"]]
print(f"  theta0 predice mejor que el reducido en {len(t0)} de {len(comp)}")
N = {Path(f).stem: J(f) for f in glob.glob(str(RES / "nested_validation" / "*.json"))}
nn = [s for s in comp if s in N and ok(N[s].get("chi2_test_red_nested"))]
print(f"  anidada peor que la anclada en {sum(N[s]['chi2_test_red_nested'] > N[s]['chi2_test_red_original'] for s in nn)} de {len(nn)}")
tipos = collections.Counter(V[s].get("division") for s in ADM if s in V)
print("  división:", dict(tipos))

# comparación de admisibilidad entre criterios
for d, nom in (("criteria_tests", "±5 %"), ("criteria_tests_20pc", "±20 %")):
    c = collections.Counter(); n = collections.Counter()
    for f in glob.glob(str(RES / d / "*__adm.json")):
        r = J(f); s = r["sistema"]
        if s not in ADM or s in EXCLUDE_ADMISSIBILITY or "no_evaluable" in r:
            continue
        n[r["metodo"]] += 1; c[r["metodo"]] += bool(r.get("admisible"))
    print(f"admisibilidad {nom}:", {m: f"{c[m]}/{n[m]}" for m in sorted(n)})

# robustez
R = {Path(f).stem: J(f) for f in glob.glob(str(RES / "robustness" / "*.json"))}
R = {s: r for s, r in R.items() if s in ADM}
pat = collections.Counter(r["patron"] for r in R.values())
print(f"robustez: {len(R)} problemas; patrones {dict(pat)}")
todo5 = [s for s, r in R.items() if all(e <= T for e in r["niveles"]["5"]["eaj"])]
print(f"  ±5 %: todos los escenarios válidos reproducidos en {len(todo5)}; con los 15 válidos: {sum(R[s]['niveles']['5']['n'] == 15 for s in todo5)}")
A = [s for s, r in R.items() if r["patron"] == "A"]
siempre = [s for s in A if all(all(e <= T for e in v["eaj"]) for v in R[s]["niveles"].values())]
tasa = {s: min(sum(e <= T for e in v["eaj"]) / max(len(v["eaj"]), 1) for v in R[s]["niveles"].values()) for s in A}
bajos = sorted(s.split('_')[0] for s in A if tasa[s] < 0.75)
print(f"  de los {len(A)} A: {len(siempre)} pasan todo; con tasa mínima < 75 %: {bajos} ({[round(100*tasa[s]) for s in A if tasa[s] < 0.75]})")
print("  patrón por problema:", {s.split('_')[0]: r['patron'] for s, r in sorted(R.items()) if r['patron'] != 'A'})
