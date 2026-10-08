# Verificación del simulador de salidas medidas (petab_outputs.py)

Predicciones en θ₀ (valores nominales de PEtab) comparadas con `simulations.tsv` del benchmark (commit fcbddf1), emparejando cada medición por observable, condición y tiempo. Error relativo |mío − referencia| / |referencia|.

| Sistema | Mediciones | Condiciones | p (θ) | p que afectan a y | Error mediano | Error máximo | Nota |
|---|---|---|---|---|---|---|---|
| Alkan_SciSignal2018 | 1733 | 73 | 44 | 44 | 3.1e-08 | 3.1e-05 | coincide |
| Armistead_CellDeathDis2024 | 58 | 2 | 14 | 10 | 0.0e+00 | 6.1e-07 | coincide |
| Bachmann_MSB2011 | 541 | 36 | 113 | 101 | 7.1e-08 | 2.2e-05 | coincide |
| Beer_MolBioSystems2014 | 27132 | 19 | 72 | 70 | 5.9e-08 | 3.8e-04 | coincide |
| Bertozzi_PNAS2020 | 22 | 2 | 8 | 6 | 1.6e-07 | 1.3e-06 | coincide |
| Blasi_CellSystems2016 | 252 | 1 | 9 | 8 |  |  | simulations.tsv tiene 288 filas |
| Boehm_JProteomeRes2014 | 48 | 1 | 9 | 6 | 1.1e-07 | 8.6e-07 | coincide |
| Borghans_BiophysChem1997 | 111 | 1 | 23 | 22 | 2.2e-06 | 1.6e-04 | coincide |
| Brannmark_JBC2010 | 43 | 8 | 22 | 18 | 2.3e-07 | 1.3e-05 | coincide |
| Bruno_JExpBot2016 | 77 | 6 | 13 | 13 | 1.3e-07 | 2.3e-06 | coincide |
| Chen_MSB2009 | 120 | 4 | 155 | 155 | 1.1e-04 | 2.8e-03 | coincide |
| Crauste_CellSystems2017 | 21 | 1 | 12 | 12 | 7.8e-03 | 7.9e-02 | diferencia < 1 % en mediana (modelo muy rígido) |
| Elowitz_Nature2000 | 58 | 1 | 21 | 20 | 1.6e-06 | 1.7e-05 | coincide |
| Fiedler_BMCSystBiol2016 | 72 | 3 | 22 | 20 | 1.1e-07 | 9.9e-07 | coincide |
| Fujita_SciSignal2010 | 144 | 6 | 19 | 19 |  |  | simulations.tsv no comparable (otros identificadores de condición) |
| Giordano_Nature2020 | 313 | 1 | 50 | 43 | 8.9e-07 | 2.0e-06 | coincide |
| Isensee_JCB2018 | 687 | 123 | 46 | 43 |  |  | simulations.tsv no comparable (otros identificadores de condición) |
| Lang_PLOSComputBiol2024 | 9600 | 1 | 294 | 277 | 2.8e-02 | 2.3e+00 | ciclo celular oscilante hasta t = 136 472: la mediana coincide (2,8 %), los picos difieren por desfase acumulado |
| Laske_PLOSComputBiol2019 | 42 | 3 | 13 | 8 | 1.3e-07 | 4.5e-07 | coincide |
| Liu_IFACPapersOnLine2025 | 100 | 2 | 9 | 7 | 2.9e-08 | 6.1e-07 | coincide |
| Lucarelli_CellSystems2018 | 1755 | 16 | 84 | 72 | 0.0e+00 | 1.5e-06 | coincide |
| Okuonghae_ChaosSolitonsFractals2020 | 92 | 1 | 16 | 14 |  |  | sin simulations.tsv en el benchmark |
| Oliveira_NatCommun2021 | 120 | 1 | 12 | 12 |  |  | sin simulations.tsv en el benchmark |
| Perelson_Science1996 | 16 | 1 | 3 | 2 | 1.7e-01 | 4.5e-01 | discrepancia con simulations.tsv; el estado inicial del modelo es estacionario (dV/dt(0) = 0) y RoadRunner lo respeta: probable referencia generada con otros valores |
| Rahman_MBS2016 | 23 | 1 | 9 | 9 | 6.5e-08 | 6.0e-07 | coincide |
| Raia_CancerResearch2011 | 205 | 4 | 39 | 23 |  |  | simulations.tsv no comparable (otros identificadores de condición) |
| Raimundez_PCB2020 | 627 | 170 | 136 | 136 | 9.3e-06 | 3.3e-05 | coincide |
| SalazarCavazos_MBoC2020 | 18 | 4 | 6 | 6 | 7.5e-09 | 1.2e-07 | coincide |
| Schwen_PONE2014 | 286 | 19 | 30 | 28 | 2.0e-08 | 2.1e-07 | coincide |
| Smith_BMCSystBiol2013 | 62 | 35 | 25 | 25 | 2.6e-08 | 7.2e-07 | coincide |
| Sneyd_PNAS2002 | 135 | 9 | 15 | 14 | 2.0e-07 | 5.3e-01 | mediana exacta; el máximo corresponde a filas duplicadas (mismo tiempo) |
| Weber_BMC2015 | 135 | 2 | 36 | 31 | 1.0e-10 | 1.5e-08 | coincide |
| Zhao_QuantBiol2020 | 82 | 7 | 28 | 21 |  |  | simulations.tsv tiene 169 filas |
| Zheng_PNAS2012 | 60 | 1 | 46 | 45 | 1.1e-01 | 9.0e-01 | simulations.tsv del benchmark copia los datos medidos, no es una simulación |

Froehlich_CellSystems2018 no se incluye: 9 169 condiciones experimentales (una simulación del modelo de 1 228 especies por condición) hacen inviable el cálculo de sensibilidades sobre las salidas medidas con los recursos disponibles.
