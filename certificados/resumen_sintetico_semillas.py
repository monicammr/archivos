#!/usr/bin/env python3
"""
Resumen del experimento sintético con varias semillas (sintetico_semillas.py).

Criterios del artículo (Supplementary Note «Synthetic prediction experiment»):
  señal  : χ²/n en prueba de θ₀ sobre los datos sintéticos ≥ 2;
  éxito  : e_pred del reducido ≤ τ_e = 0,436;
  empate o mejor que el completo: e_pred reducido ≤ e_pred completo.
Se informa (i) por semilla, los mismos recuentos que el artículo da para la semilla 42, y
(ii) por sistema, la mediana de e_pred y la fracción de semillas en que se cumple cada criterio.

Uso: python3 resumen_sintetico_semillas.py      → resultados/sintetico_semillas/RESUMEN.md y .json
"""
import json
from pathlib import Path
import numpy as np

D = Path(__file__).resolve().parent / "resultados" / "sintetico_semillas"
TAU = float(np.sqrt(1 - 0.9 ** 2))
ok = lambda x: isinstance(x, (int, float)) and np.isfinite(x)

R = {}
for f in sorted(D.glob("*/s*.json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    R.setdefault(d["sistema"], {})[d["semilla"]] = d
seeds = sorted({s for v in R.values() for s in v})

# ---- por semilla: recuentos del artículo
por_semilla = []
for s in seeds:
    c = dict(semilla=s, evaluables=0, senal=0, red_ok=0, comp=0, red_le_full=0, ruido=0, ruido_ok=0)
    for n, v in R.items():
        d = v.get(s)
        if not d or not ok(d.get("B_epred_red")) or not ok(d.get("B_chi2_test_theta0")):
            continue
        c["evaluables"] += 1
        if d["B_chi2_test_theta0"] >= 2:
            c["senal"] += 1
            c["red_ok"] += d["B_epred_red"] <= TAU
            if ok(d.get("B_epred_full")):
                c["comp"] += 1
                c["red_le_full"] += d["B_epred_red"] <= d["B_epred_full"]
        else:
            c["ruido"] += 1
            c["ruido_ok"] += ok(d.get("B_chi2_test_red")) and d["B_chi2_test_red"] <= 2
    por_semilla.append(c)

# ---- por sistema
por_sistema = []
for n, v in sorted(R.items()):
    ds = [d for d in v.values() if ok(d.get("B_epred_red")) and ok(d.get("B_chi2_test_theta0"))]
    if not ds:
        por_sistema.append(dict(sistema=n, validas=0, nota=next(
            (d.get("no_evaluable") or d.get("B_error") or d.get("error") for d in v.values()), "")))
        continue
    sen = [d for d in ds if d["B_chi2_test_theta0"] >= 2]
    par = [d for d in ds if ok(d.get("B_epred_full"))]
    psen = [d for d in sen if ok(d.get("B_epred_full"))]
    por_sistema.append(dict(
        sistema=n, validas=len(ds), con_senal=len(sen),
        epred_red_med=float(np.median([d["B_epred_red"] for d in ds])),
        epred_full_med=float(np.median([d["B_epred_full"] for d in par])) if par else None,
        red_ok_senal=sum(d["B_epred_red"] <= TAU for d in sen),
        comparadas=len(par), red_le_full=sum(d["B_epred_red"] <= d["B_epred_full"] for d in par),
        comparadas_senal=len(psen),
        red_le_full_senal=sum(d["B_epred_red"] <= d["B_epred_full"] for d in psen)))

tot = {k: sum(c[k] for c in por_semilla) for k in ("senal", "red_ok", "comp", "red_le_full", "ruido", "ruido_ok")}
q = lambda k: [c[k] for c in por_semilla]
fr = lambda a, b: [c[a] / c[b] for c in por_semilla if c[b]]

L = ["# Experimento sintético con varias semillas", "",
     f"Semillas: {seeds[0]}–{seeds[-1]} ({len(seeds)}); τ_e = {TAU:.3f}; señal si χ²/n(θ₀) ≥ 2.", "",
     "## Recuentos por semilla (los del artículo corresponden a la semilla 42)", "",
     "| semilla | evaluables | con señal | reducido ≤ τ_e | comparados con completo | reducido ≤ completo | sin señal | reducido al nivel del ruido |",
     "|---|---|---|---|---|---|---|---|"]
for c in por_semilla:
    L.append(f"| {c['semilla']} | {c['evaluables']} | {c['senal']} | {c['red_ok']} | {c['comp']} | "
             f"{c['red_le_full']} | {c['ruido']} | {c['ruido_ok']} |")
L += ["", f"**Agregado ({len(seeds)} semillas), problemas con señal:** reducido ≤ τ_e en "
      f"{tot['red_ok']}/{tot['senal']} ({100 * tot['red_ok'] / max(tot['senal'], 1):.0f} %); "
      f"reducido ≤ completo en {tot['red_le_full']}/{tot['comp']} "
      f"({100 * tot['red_le_full'] / max(tot['comp'], 1):.0f} %).",
      f"Fracción por semilla de reducido ≤ τ_e: mediana {np.median(fr('red_ok', 'senal')):.2f}, "
      f"rango {min(fr('red_ok', 'senal')):.2f}–{max(fr('red_ok', 'senal')):.2f}; "
      f"de reducido ≤ completo: mediana {np.median(fr('red_le_full', 'comp')):.2f}, "
      f"rango {min(fr('red_le_full', 'comp')):.2f}–{max(fr('red_le_full', 'comp')):.2f}.",
      f"Sin señal: reducido al nivel del ruido (χ²/n ≤ 2) en {tot['ruido_ok']}/{tot['ruido']}.", "",
      "## Por sistema", "",
      "| sistema | semillas válidas | con señal | e_pred reducido (mediana) | e_pred completo (mediana) | reducido ≤ τ_e (con señal) | reducido ≤ completo (con señal) | reducido ≤ completo (todas) |",
      "|---|---|---|---|---|---|---|---|"]
g = lambda x: "–" if x is None else f"{x:.3g}"
for r in por_sistema:
    if not r["validas"]:
        L.append(f"| {r['sistema'].split('_')[0]} | 0 | | | | | | {r['nota']} |")
        continue
    L.append(f"| {r['sistema'].split('_')[0]} | {r['validas']} | {r['con_senal']} | {g(r['epred_red_med'])} | "
             f"{g(r['epred_full_med'])} | {r['red_ok_senal']}/{r['con_senal']} | "
             f"{r['red_le_full_senal']}/{r['comparadas_senal']} | {r['red_le_full']}/{r['comparadas']} |")
(D / "RESUMEN.md").write_text("\n".join(L) + "\n", encoding="utf-8")
(D / "RESUMEN.json").write_text(json.dumps(dict(por_semilla=por_semilla, por_sistema=por_sistema, total=tot),
                                           indent=1, default=int), encoding="utf-8")
print("\n".join(L))
