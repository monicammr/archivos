#!/usr/bin/env python3
"""Tabla de verificación del simulador de salidas (petab_outputs.py) frente a simulations.tsv.

Lee resultados/salidas_check_log.txt (una línea JSON por sistema, de `petab_outputs.py`) y escribe
resultados/salidas/VERIFICACION_SIMULADOR.md.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOG = HERE / "resultados" / "salidas_check_log.txt"
OUT = HERE / "resultados" / "salidas" / "VERIFICACION_SIMULADOR.md"

NOTAS = {
    "Zheng_PNAS2012": "simulations.tsv del benchmark copia los datos medidos, no es una simulación",
    "Perelson_Science1996": "discrepancia con simulations.tsv; el estado inicial del modelo es "
                            "estacionario (dV/dt(0) = 0) y RoadRunner lo respeta: probable "
                            "referencia generada con otros valores",
    "Lang_PLOSComputBiol2024": "ciclo celular oscilante hasta t = 136 472: la mediana coincide "
                               "(2,8 %), los picos difieren por desfase acumulado",
    "Crauste_CellSystems2017": "diferencia < 1 % en mediana (modelo muy rígido)",
    "Sneyd_PNAS2002": "mediana exacta; el máximo corresponde a filas duplicadas (mismo tiempo)",
}


def main():
    filas = [json.loads(l) for l in LOG.read_text().splitlines() if l.startswith("{")]
    filas.sort(key=lambda d: d["sistema"])
    L = ["# Verificación del simulador de salidas medidas (petab_outputs.py)", "",
         "Predicciones en θ₀ (valores nominales de PEtab) comparadas con `simulations.tsv` del "
         "benchmark (commit fcbddf1), emparejando cada medición por observable, condición y "
         "tiempo. Error relativo |mío − referencia| / |referencia|.", "",
         "| Sistema | Mediciones | Condiciones | p (θ) | p que afectan a y | Error mediano | "
         "Error máximo | Nota |", "|---|---|---|---|---|---|---|---|"]
    for d in filas:
        n = d["sistema"]
        med = d.get("err_rel_mediana")
        mx = d.get("err_rel_max_vs_simulations")
        nota = d.get("error") or d.get("nota") or NOTAS.get(n, "") or \
            ("sin simulations.tsv en el benchmark" if med is None else "")
        if med is not None and mx is not None and mx < 1e-2 and n not in NOTAS:
            nota = "coincide"
        L.append(f"| {n} | {d.get('mediciones', '')} | {d.get('condiciones', '')} | "
                 f"{d.get('p', '')} | {d.get('p_y', '')} | "
                 f"{'' if med is None else f'{med:.1e}'} | {'' if mx is None else f'{mx:.1e}'} | "
                 f"{nota} |")
    L += ["", "Froehlich_CellSystems2018 no se incluye: 9 169 condiciones experimentales "
          "(una simulación del modelo de 1 228 especies por condición) hacen inviable el cálculo "
          "de sensibilidades sobre las salidas medidas con los recursos disponibles."]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(L) + "\n")
    print(OUT.read_text())


if __name__ == "__main__":
    main()
