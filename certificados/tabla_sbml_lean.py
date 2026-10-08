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
    "Okuonghae_ChaosSolitonsFractals2020": "incidencia β·S·I/N: no definida si N = 0 (el dominio no contiene todo el ortante)",
    "Rahman_MBS2016": "incidencia β·S·I/N: no definida si N = 0",
    "Armistead_CellDeathDis2024": "producción k3(1 − S_on·α)·Sphingo de signo dependiente de parámetros; alpha_cer < 0 por diseño",
    "Fiedler_BMCSystBiol2016": "entrada k10 − k11·e^{−t/τ2}(e^{−t/τ1} − 1) ≥ 0, pero el comprobador sintáctico no lo detecta (conservador)",
    "Smith_BMCSystBiol2013": "eventos SBML (tiempos fijos): cubierto por EventSystems, no por el traductor",
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
    if "depends on axioms: [propext, Classical.choice, Quot.sound]" in out:
        if d.get("red") == "ok":
            res = f"✅ verificado, sin condiciones pendientes ({t})"
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
