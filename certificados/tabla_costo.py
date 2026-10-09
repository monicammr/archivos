#!/usr/bin/env python3
"""Costo computacional del método (revisor 2, comentario 5) → resultados/costo/COSTO.md

El paso dominante es J por diferencias centradas: 2p simulaciones (más p del barrido de la
Etapa 2). Las simulaciones son independientes, así que el cálculo es paralelo perfecto.
Tiempos por simulación medidos en el servidor usado (4 núcleos); Froehlich sobre estados (una
condición), los demás sobre las salidas medidas (todas las condiciones de PEtab).
"""
import json
from pathlib import Path

R = Path(__file__).resolve().parent / "resultados" / "costo"


def hms(s):
    return f"{s:.0f} s" if s < 120 else (f"{s/60:.0f} min" if s < 7200 else f"{s/3600:.1f} h")


def main():
    d = json.loads((R / "tiempos_simulacion.json").read_text())
    filas = sorted(d.items(), key=lambda kv: kv[1]["p"])
    L = ["# Costo computacional", "",
         "J (diferencias centradas) = 2p simulaciones; barrido de la Etapa 2 = p simulaciones. "
         "La selección voraz, κ/VIF, la poda y e_ajuste linealizado sólo usan J (álgebra lineal, "
         "costo despreciable frente a las simulaciones).", "",
         "| Sistema | p | Datos | t por simulación | Simulaciones para J + barrido (3p) | "
         "Tiempo en serie | Tiempo con 4 núcleos |", "|---|---|---|---|---|---|---|"]
    for n, v in filas:
        sims = 3 * v["p"]
        t = sims * v["t_sim"]
        L.append(f"| {n} | {v['p']} | {v['modo']} | {v['t_sim']:.3g} s | {sims} | {hms(t)} | "
                 f"{hms(t / 4)} |")
    L += ["", "El costo crece linealmente con p (y con el costo de una simulación). Froehlich "
          "(4 231 parámetros, 1 228 especies) se calculó completo sobre estados. Sobre sus salidas "
          "medidas (9 169 condiciones) cada evaluación requiere del orden de 9 000 simulaciones (una por condición), por lo que se "
          "excluye; para estos casos se recomiendan sensibilidades por ecuaciones de sensibilidad "
          "directas o adjuntas (p. ej. AMICI), que calculan J con un costo de unas pocas "
          "simulaciones."]
    (R / "COSTO.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
