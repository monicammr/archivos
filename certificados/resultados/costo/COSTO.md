# Costo computacional

J (diferencias centradas) = 2p simulaciones; barrido de la Etapa 2 = p simulaciones. La selección voraz, κ/VIF, la poda y e_ajuste linealizado sólo usan J (álgebra lineal, costo despreciable frente a las simulaciones).

| Sistema | p | Datos | t por simulación | Simulaciones para J + barrido (3p) | Tiempo en serie | Tiempo con 4 núcleos |
|---|---|---|---|---|---|---|
| Boehm_JProteomeRes2014 | 9 | salidas | 0.00168 s | 27 | 0 s | 0 s |
| Elowitz_Nature2000 | 21 | salidas | 0.00243 s | 63 | 0 s | 0 s |
| Fiedler_BMCSystBiol2016 | 22 | salidas | 0.00257 s | 66 | 0 s | 0 s |
| Weber_BMC2015 | 36 | salidas | 0.00374 s | 108 | 0 s | 0 s |
| Raia_CancerResearch2011 | 39 | salidas | 0.0106 s | 117 | 1 s | 0 s |
| Alkan_SciSignal2018 | 44 | salidas | 0.13 s | 132 | 17 s | 4 s |
| Zheng_PNAS2012 | 46 | salidas | 0.00449 s | 138 | 1 s | 0 s |
| Isensee_JCB2018 | 46 | salidas | 0.64 s | 138 | 88 s | 22 s |
| Giordano_Nature2020 | 50 | salidas | 0.00613 s | 150 | 1 s | 0 s |
| Beer_MolBioSystems2014 | 72 | salidas | 0.173 s | 216 | 37 s | 9 s |
| Lucarelli_CellSystems2018 | 84 | salidas | 0.04 s | 252 | 10 s | 3 s |
| Bachmann_MSB2011 | 113 | salidas | 0.04 s | 339 | 14 s | 3 s |
| Raimundez_PCB2020 | 136 | salidas | 0.37 s | 408 | 3 min | 38 s |
| Chen_MSB2009 | 155 | salidas | 35 s | 465 | 4.5 h | 68 min |
| Lang_PLOSComputBiol2024 | 294 | salidas | 0.65 s | 882 | 10 min | 2 min |
| Froehlich_CellSystems2018 | 4231 | estados | 2.93 s | 12693 | 10.3 h | 2.6 h |

El costo crece linealmente con p (y con el costo de una simulación). Froehlich (4 231 parámetros, 1 228 especies) se calculó completo sobre estados. Sobre sus salidas medidas (9 169 condiciones) cada evaluación requiere del orden de 9 000 simulaciones (una por condición), por lo que se excluye; para estos casos se recomiendan sensibilidades por ecuaciones de sensibilidad directas o adjuntas (p. ej. AMICI), que calculan J con un costo de unas pocas simulaciones.
