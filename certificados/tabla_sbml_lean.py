#!/usr/bin/env python3
"""Tabla resumen: traducción SBML → Lean y resultado de la comprobación en Lean.

Lee resultados/sbml_lean/*.json (sbml_to_lean.py) y resultados/sbml_lean/lean_log.txt
(líneas `Sistema|tiempo|salida de lean`) y escribe resultados/sbml_lean/tabla.md.
"""
import json
from pathlib import Path

D = Path(__file__).resolve().parent / "resultados" / "sbml_lean"

lean = {}
logf = D / "lean_log.txt"
if logf.exists():
    for line in logf.read_text().splitlines():
        parts = line.split("|", 2)
        if len(parts) == 3:
            lean[parts[0]] = (parts[1], parts[2])

MOTIVO = {
    "Elowitz_Nature2000": "Hill con exponente estimado sobre una concentración (x^θ no es C¹ en x = 0 si θ < 1)",
    "Borghans_BiophysChem1997": "Hill con exponente estimado sobre una concentración (Z^n)",
    "Okuonghae_ChaosSolitonsFractals2020": "incidencia β·S·I/N (exige N > 0) y, además, el flujo symptomatic → asymptomatic tiene tasa ν·σ·E, que no depende de symptomatic: symptomatic' = σ(1 − ν)E − …, así que con ν > 1 (permitido por los límites de PEtab, ν ≤ 1000) symptomatic puede volverse negativo; la positividad sólo vale si ν ≤ 1 (nominal 0.5)",
    "Rahman_MBS2016": "incidencia β·S·I/N: no definida si N = 0",
    "Armistead_CellDeathDis2024": "producción k3(1 − S_on·α)·Sphingo de signo dependiente de parámetros; alpha_cer < 0 por diseño",
    "Fiedler_BMCSystBiol2016": "entrada k10 − k11·e^{−t/τ2}(e^{−t/τ1} − 1) ≥ 0, pero el comprobador sintáctico no lo detecta (conservador)",
    "Smith_BMCSystBiol2013": "las reacciones R16f/R17f usan max(PIP3 − basal, 0), que no es diferenciable: el campo no es C¹ y el teorema de diferenciabilidad no aplica (los eventos en tiempos fijos sí se traducen)",
}

ESTRICTA = {
    "Okuonghae_ChaosSolitonsFractals2020": "red reescrita de forma exacta (σ(1 − ν)E y σνE); Lean comprueba ν₀ = 0,5 ≤ 1 en θ₀ (con ν > 1 la positividad falla)",
    "Armistead_CellDeathDis2024": "las tasas k00(1 + α_cer) y k3(1 − α_hai1a) son ≥ 0 si α_cer ≥ −1 y α_hai1a ≤ 1; Lean lo comprueba en θ₀, y todo el rango de PEtab (α_cer ∈ [−0,999, −0,001], α_hai1a ∈ [0,5, 0,999]) cumple esas cotas",
    "Fiedler_BMCSystBiol2016": "entrada 1 − e^{−t/τ1} ≥ 0; dato inicial (estado estacionario con raíces) certificado > 0 por intervalos en ℚ",
}

rows = []
for f in sorted(D.glob("*.json")):
    d = json.loads(f.read_text())
    nm = d.get("sistema")
    if not nm:
        continue
    if not d.get("traducido"):
        rows.append([nm, "—", "—", "no traducido", MOTIVO.get(nm, d.get("motivo", ""))])
        continue
    notas = []
    if d.get("tiempo_como_estado"):
        notas.append("tiempo como estado")
    if len(d.get("tramos", [])) > 1:
        notas.append(f"{len(d['tramos'])} tramos (escalones)")
    if d.get("theta_log_nominal_0"):
        notas.append("nominal 0 en escala log: " + ", ".join(d["theta_log_nominal_0"]))
    if d.get("theta_signo_libre"):
        notas.append("signo libre: " + ", ".join(d["theta_signo_libre"]))
    t, out = lean.get(nm, ("", ""))
    if "check_falla demostrado" in out:
        res = f"✅ verificado con condición: la solución nominal existe en [0,T] y permanece en el dominio"
        notas.append(MOTIVO.get(nm, ""))
    elif "depends on axioms: [propext, Classical.choice, Quot.sound]" in out:
        if d.get("red") == "ok":
            res = f"✅ verificado, sin condiciones pendientes ({t})"
        elif d.get("red") == "riccati":
            res = f"✅ verificado, sin condiciones pendientes para T ≤ {d.get('T')} ({t}); cota de Riccati"
            notas.append("crecimiento cuadrático (ρ_P·P²): existencia demostrada en el horizonte del análisis, no global")
        elif d.get("red") == "estricta":
            res = f"✅ verificado, sin condiciones pendientes ({t}); positividad estricta"
            notas.append("las especies con dato inicial > 0 permanecen > 0 (lo exige el dominio)")
            notas.append(ESTRICTA.get(nm, ""))
        else:
            res = f"✅ verificado; condición: existe la solución nominal en [0,T] ({t})"
            if d.get("red") == "crecimiento":
                notas.append("crecimiento superlineal (P²): la existencia global no se puede garantizar")
    elif d.get("prediccion_check") is False and out.strip() == "":
        res = f"❌ Lean demuestra que la comprobación falla ({t})"
        notas.append(MOTIVO.get(nm, ""))
    elif "SIN MEMORIA" in out:
        res = f"⏸ sin verificar: Lean sin memoria ({t}); Python predice que pasa"
    elif not out:
        res = "pendiente"
    else:
        res = "error: " + out[:80]
    rows.append([nm, f"{d['n_estados']}", f"{d['n_theta']}", res, "; ".join(x for x in notas if x)])

head = ["Sistema", "Estados", "θ", "Lean", "Notas"]
md = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
md += ["| " + " | ".join(r) + " |" for r in rows]
(D / "tabla.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
