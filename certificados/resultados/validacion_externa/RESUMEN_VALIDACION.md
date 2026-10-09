# Validación externa del modelo reducido (comentario 5)

Ajuste con una parte de los experimentos y predicción de los que NO se usaron (condiciones nuevas, o tiempos posteriores si sólo hay una condición). χ²/n = media de los residuos estandarizados al cuadrado en el conjunto de prueba (≈ 1: error del tamaño del ruido experimental). e_pred = error relativo de predicción frente a la verdad (sólo en el experimento sintético; umbral 0,436).

## A. Datos reales

| Sistema | División | |S| / p | χ²/n prueba reducido | χ²/n prueba completo | χ²/n prueba θ₀ (vio todos los datos) |
|---|---|---|---|---|---|
| Alkan_SciSignal2018 | condiciones nuevas | 3 / 44 | 2.51 | 3.38 | 2.47 |
| Armistead_CellDeathDis2024 | condiciones nuevas | 4 / 10 | 1.37 | 1.37 | 1.16 |
| Bachmann_MSB2011 | condiciones nuevas | 22 / 101 | 4.70 | — | 1.05 |
| Boehm_JProteomeRes2014 | extrapolación temporal (t ≥ 80) | 2 / 6 | 2.57 | 11.35 | 0.34 |
| Borghans_BiophysChem1997 | extrapolación temporal (t ≥ 6.48875) | 2 / 22 | 0.74 | 0.74 | 0.74 |
| Brannmark_JBC2010 | condiciones nuevas | 2 / 18 | 0.94 | 2145.47 | 0.94 |
| Bruno_JExpBot2016 | condiciones nuevas | 7 / 13 | 0.91 | 7.86 | 0.91 |
| Elowitz_Nature2000 | extrapolación temporal (t ≥ 410) | 6 / 20 | 1.50 | 4.45 | 1.38 |
| Fiedler_BMCSystBiol2016 | condiciones nuevas | 5 / 20 | 11.66 | 14.11 | 1.22 |
| Fujita_SciSignal2010 | condiciones nuevas | 2 / 19 | 5.66 | 8.04 | 5.63 |
| Giordano_Nature2020 | extrapolación temporal (t ≥ 30) | 2 / 43 | 0.00 | 0.06 | 0.00 |
| Isensee_JCB2018 | condiciones nuevas | 10 / 43 | 1.04 | 1.08 | 1.04 |
| Lang_PLOSComputBiol2024 | extrapolación temporal (t ≥ 86391.6) | 12 / 277 | 6.22 | — | 7.33 |
| Laske_PLOSComputBiol2019 | condiciones nuevas | 2 / 8 | 0.44 | 1.88 | 0.44 |
| Liu_IFACPapersOnLine2025 | condiciones nuevas | 2 / 7 | 0.95 | 1.02 | 0.94 |
| Lucarelli_CellSystems2018 | condiciones nuevas | 10 / 72 | 1.57 | — | 1.02 |
| Okuonghae_ChaosSolitonsFractals2020 | extrapolación temporal (t ≥ 32) | 2 / 14 | 46705.21 | 122419.25 | 28748.50 |
| Oliveira_NatCommun2021 | extrapolación temporal (t ≥ 40) | 2 / 12 | 914.51 | 81453.15 | 460396.13 |
| Perelson_Science1996 | extrapolación temporal (t ≥ 2.038) | 2 / 2 | 0.00 | 0.00 | 0.00 |
| Rahman_MBS2016 | extrapolación temporal (t ≥ 15) | 2 / 9 | 0.00 | 0.03 | 0.00 |
| Raia_CancerResearch2011 | condiciones nuevas | 2 / 23 | 6.92 | 5.10 | 0.42 |
| Raimundez_PCB2020 | condiciones nuevas | 5 / 136 | 0.98 | — | 0.98 |
| SalazarCavazos_MBoC2020 | condiciones nuevas | 2 / 6 | 101.83 | 124.19 | 96.93 |
| Schwen_PONE2014 | condiciones nuevas | 4 / 28 | 0.93 | 8.40 | 0.77 |
| Smith_BMCSystBiol2013 | condiciones nuevas | 3 / 25 | 16361.97 | 14977.66 | 82920.71 |
| Sneyd_PNAS2002 | condiciones nuevas | 2 / 14 | 2.22 | 2.55 | 1.37 |
| Weber_BMC2015 | condiciones nuevas | 2 / 31 | 0.99 | 226.02 | 0.99 |
| Zhao_QuantBiol2020 | condiciones nuevas | 3 / 21 | 0.35 | 0.35 | 0.35 |
| Zheng_PNAS2012 | extrapolación temporal (t ≥ 10) | 2 / 45 | 1.58 | 20.60 | 1.51 |

## B. Sintético con ruido (verdad θ* = θ₀ ± 20 %, ruido N(0, σ²))

| Sistema | e_pred reducido | e_pred completo | χ²/n prueba reducido | χ²/n prueba completo | Reducido ≤ 0,436 |
|---|---|---|---|---|---|
| Alkan_SciSignal2018 | 0.16 | 0.15 | 1.08 | 1.06 | sí |
| Armistead_CellDeathDis2024 | 0.17 | 0.18 | 0.59 | 0.58 | sí |
| Bachmann_MSB2011 | 4.00 | — | 5.25 | — | no |
| Boehm_JProteomeRes2014 | 0.45 | 6.63 | 0.57 | 24.18 | no |
| Borghans_BiophysChem1997 | 1.00 | 0.31 | 2.73 | 0.90 | no |
| Brannmark_JBC2010 | 0.48 | 3.97 | 2.25 | 87.79 | no |
| Bruno_JExpBot2016 | 0.41 | 3.74 | 0.46 | 8.31 | sí |
| Elowitz_Nature2000 | 0.13 | 0.11 | 0.86 | 0.79 | sí |
| Fiedler_BMCSystBiol2016 | 0.25 | 3.12 | 0.45 | 10.17 | sí |
| Fujita_SciSignal2010 | 0.98 | 0.44 | 1.48 | 1.06 | no |
| Giordano_Nature2020 | 1027.15 | 3136.24 | 0.86 | 1.10 | no |
| Isensee_JCB2018 | — | — | — | — | no |
| Lang_PLOSComputBiol2024 | 0.23 | — | 1.57 | — | sí |
| Laske_PLOSComputBiol2019 | 3.19 | 4.72 | 2.50 | 4.63 | no |
| Liu_IFACPapersOnLine2025 | 0.65 | 2.15 | 0.58 | 0.75 | no |
| Lucarelli_CellSystems2018 | 2.01 | — | 1.30 | — | no |
| Okuonghae_ChaosSolitonsFractals2020 | 0.08 | 0.04 | 277.82 | 73.16 | sí |
| Oliveira_NatCommun2021 | 0.29 | 0.00 | 5480367.73 | 141.96 | sí |
| Perelson_Science1996 | 23.29 | 23.29 | 0.68 | 0.68 | no |
| Rahman_MBS2016 | 0.07 | 0.10 | 1.95 | 2.82 | sí |
| Raia_CancerResearch2011 | 0.47 | 1.08 | 0.93 | 0.96 | no |
| Raimundez_PCB2020 | 0.49 | — | 2.09 | — | no |
| SalazarCavazos_MBoC2020 | 0.17 | 0.11 | 0.44 | 0.55 | sí |
| Schwen_PONE2014 | 0.25 | 1.94 | 0.75 | 4.51 | sí |
| Smith_BMCSystBiol2013 | 0.22 | 0.07 | 213.63 | 22.73 | sí |
| Sneyd_PNAS2002 | 0.29 | 0.23 | 0.90 | 0.94 | sí |
| Weber_BMC2015 | 0.77 | 1.72 | 69.94 | 352.74 | no |
| Zhao_QuantBiol2020 | 1.00 | 1.00 | 0.87 | 0.87 | no |
| Zheng_PNAS2012 | 0.36 | 0.37 | 2.42 | 2.94 | sí |

## Resumen

* Sistemas evaluados: 29; no evaluables: 2; errores: 0.
* Datos reales: el reducido predice igual o mejor que el completo reajustado en 22 de 25 sistemas.
* Sintético: e_pred del reducido ≤ 0,436 en 14 de 29; reducido igual o mejor que el completo en 14 de 24.

No evaluables:

* Bertozzi_PNAS2020: todos los parámetros de S son exclusivos de las condiciones de prueba
* Blasi_CellSystems2016: una sola condición y un solo tiempo de medición (no se puede separar entrenamiento y prueba)
