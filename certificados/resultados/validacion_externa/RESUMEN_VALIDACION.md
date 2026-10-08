# Validación externa del modelo reducido (comentario 5)

Ajuste con una parte de los experimentos y predicción de los que NO se usaron (condiciones nuevas, o tiempos posteriores si sólo hay una condición). χ²/n = media de los residuos estandarizados al cuadrado en el conjunto de prueba (≈ 1: error del tamaño del ruido experimental). e_pred = error relativo de predicción frente a la verdad (sólo en el experimento sintético; umbral 0,436).

## A. Datos reales

| Sistema | División | |S| / p | χ²/n prueba reducido | χ²/n prueba completo | χ²/n prueba θ₀ (vio todos los datos) |
|---|---|---|---|---|---|
| Armistead_CellDeathDis2024 | condiciones nuevas | 4 / 10 | 1.37 | 1.37 | 1.16 |
| Bertozzi_PNAS2020 | condiciones nuevas | 2 / 6 | 1.00 | 1.00 | 1.00 |
| Blasi_CellSystems2016 | extrapolación temporal (t ≥ inf) | 5 / 8 | 6.41 | 6.41 | 6.41 |
| Boehm_JProteomeRes2014 | extrapolación temporal (t ≥ 80) | 2 / 6 | 2.57 | 11.35 | 0.34 |
| Borghans_BiophysChem1997 | extrapolación temporal (t ≥ 6.48875) | 2 / 22 | 0.74 | 0.74 | 0.74 |
| Brannmark_JBC2010 | condiciones nuevas | 2 / 18 | 0.94 | 68910.90 | 0.94 |
| Bruno_JExpBot2016 | condiciones nuevas | 7 / 13 | 0.91 | 6758.58 | 0.91 |
| Elowitz_Nature2000 | extrapolación temporal (t ≥ 410) | 6 / 20 | 1.50 | 4.45 | 1.38 |
| Fiedler_BMCSystBiol2016 | condiciones nuevas | 5 / 20 | 11.66 | 14.11 | 1.22 |

## B. Sintético con ruido (verdad θ* = θ₀ ± 20 %, ruido N(0, σ²))

| Sistema | e_pred reducido | e_pred completo | χ²/n prueba reducido | χ²/n prueba completo | Reducido ≤ 0,436 |
|---|---|---|---|---|---|
| Armistead_CellDeathDis2024 | 0.17 | 0.18 | 0.59 | 0.58 | sí |
| Bertozzi_PNAS2020 | 1.00 | 53.21 | 11.32 | 27970.66 | no |
| Blasi_CellSystems2016 | 1.00 | 1.00 | 2.45 | 2.45 | no |
| Boehm_JProteomeRes2014 | 0.45 | 6.63 | 0.57 | 24.18 | no |
| Borghans_BiophysChem1997 | 1.00 | 0.31 | 2.73 | 0.90 | no |
| Brannmark_JBC2010 | 1.35 | 42.01 | 5.23 | 3877.45 | no |
| Bruno_JExpBot2016 | 16.76 | 39.15 | 1307.35 | 7158.22 | no |
| Elowitz_Nature2000 | 0.13 | 0.11 | 0.86 | 0.79 | sí |
| Fiedler_BMCSystBiol2016 | 0.25 | 3.12 | 0.45 | 10.17 | sí |

## Resumen

* Sistemas evaluados: 9 (errores: 0).
* Datos reales: el reducido predice igual o mejor que el completo reajustado en 9 de 9 sistemas.
* Sintético: e_pred del reducido ≤ 0,436 en 3 de 9; reducido igual o mejor que el completo en 7 de 9.
