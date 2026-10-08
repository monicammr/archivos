| Sistema | Estados | θ | Lean | Notas |
|---|---|---|---|---|
| Armistead_CellDeathDis2024 | 4 | 10 | ✅ verificado con condición: la solución nominal existe en [0,T] y permanece en el dominio | signo libre: alpha_cer; producción k3(1 − S_on·α)·Sphingo de signo dependiente de parámetros; alpha_cer < 0 por diseño |
| Bachmann_MSB2011 | 25 | 27 | ✅ verificado, sin condiciones pendientes (10s) |  |
| Blasi_CellSystems2016 | 16 | 8 | ✅ verificado, sin condiciones pendientes (6s) |  |
| Boehm_JProteomeRes2014 | 8 | 6 | ✅ verificado, sin condiciones pendientes (5s) | tiempo como estado |
| Borghans_BiophysChem1997 | 3 | 20 | ✅ verificado, sin condiciones pendientes (5s); positividad estricta | las especies con dato inicial > 0 permanecen > 0 (lo exige el dominio) |
| Brannmark_JBC2010 | 9 | 15 | ✅ verificado, sin condiciones pendientes (5s) |  |
| Chen_MSB2009 | 500 | 152 | ✅ verificado, sin condiciones pendientes (1975s) | tiempo como estado |
| Crauste_CellSystems2017 | 5 | 12 | ✅ verificado; condición: existe la solución nominal en [0,T] (6s) | crecimiento superlineal (P²): la existencia global no se puede garantizar |
| Elowitz_Nature2000 | 8 | 18 | ✅ verificado, sin condiciones pendientes (5s); positividad estricta | las especies con dato inicial > 0 permanecen > 0 (lo exige el dominio) |
| Fiedler_BMCSystBiol2016 | 6 | 12 | ✅ verificado con condición: la solución nominal existe en [0,T] y permanece en el dominio | tiempo como estado; entrada k10 − k11·e^{−t/τ2}(e^{−t/τ1} − 1) ≥ 0, pero el comprobador sintáctico no lo detecta (conservador) |
| Froehlich_CellSystems2018 | 1228 | 4088 | ✅ verificado, sin condiciones pendientes (1800s) |  |
| Giordano_Nature2020 | 10 | 43 | ✅ verificado, sin condiciones pendientes (8s) | 6 tramos (escalones) |
| Lang_PLOSComputBiol2024 | 124 | 164 | ✅ verificado, sin condiciones pendientes (485s) | nominal 0 en escala log: kDpApc_1, kDpE2f1, kPhC25A |
| Okuonghae_ChaosSolitonsFractals2020 | 8 | 14 | ✅ verificado con condición: la solución nominal existe en [0,T] y permanece en el dominio | incidencia β·S·I/N (exige N > 0) y, además, el flujo symptomatic → asymptomatic tiene tasa ν·σ·E, que no depende de symptomatic: symptomatic' = σ(1 − ν)E − …, así que con ν > 1 (permitido por los límites de PEtab, ν ≤ 1000) symptomatic puede volverse negativo; la positividad sólo vale si ν ≤ 1 (nominal 0.5) |
| Rahman_MBS2016 | 7 | 9 | ✅ verificado, sin condiciones pendientes (6s); positividad estricta | las especies con dato inicial > 0 permanecen > 0 (lo exige el dominio) |
| Raia_CancerResearch2011 | 14 | 18 | ✅ verificado, sin condiciones pendientes (5s) |  |
| Raimundez_PCB2020 | 22 | 57 | ✅ verificado, sin condiciones pendientes (13s) | signo libre: d_AKTtotal__MKN1_2_HS746T, d_MAPKtotal__MKN1_2_HS746T, d_MPI3Ktotal__fm_2_hm, d_PI3Ktotal__fm_2_hm, d_RAStotal__MKN1_2_HS746T, d_RAStotal__fm_2_hm, d_kdeg_membran__MKN1_2_HS746T, d_kexp_pEGFR_EGF_2_i__MKN1_2_HS746T, d_kimp_pEGFR_EGF_2__MKN1_2_HS746T, d_ksyn_EGFR__MKN1_2_HS746T, d_ksyn_EGFR__fm_2_hm, d_ksyn_MMET__fm_2_hm |
| SalazarCavazos_MBoC2020 | 75 | 6 | ✅ verificado, sin condiciones pendientes (377s) |  |
| Smith_BMCSystBiol2013 | — | — | no traducido | las reacciones R16f/R17f usan max(PIP3 − basal, 0), que no es diferenciable: el campo no es C¹ y el teorema de diferenciabilidad no aplica (los eventos en tiempos fijos sí se traducen) |
| Sneyd_PNAS2002 | 6 | 14 | ✅ verificado, sin condiciones pendientes (4s) |  |
| Weber_BMC2015 | 7 | 26 | ✅ verificado, sin condiciones pendientes (5s) |  |
| Zhao_QuantBiol2020 | 4 | 21 | ✅ verificado, sin condiciones pendientes (4s) |  |
| Zheng_PNAS2012 | 15 | 45 | ✅ verificado, sin condiciones pendientes (7s) |  |
