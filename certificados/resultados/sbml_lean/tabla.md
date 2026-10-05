| Sistema | Estados | θ | Lean | Notas |
|---|---|---|---|---|
| Armistead_CellDeathDis2024 | 4 | 10 | ❌ Lean demuestra que la comprobación falla (3s) | signo libre: alpha_cer; producción k3(1 − S_on·α)·Sphingo de signo dependiente de parámetros; alpha_cer < 0 por diseño |
| Bachmann_MSB2011 | 25 | 27 | ✅ verificado (7s) |  |
| Blasi_CellSystems2016 | 16 | 8 | ✅ verificado (4s) |  |
| Boehm_JProteomeRes2014 | 8 | 6 | ✅ verificado (4s) | tiempo como estado |
| Borghans_BiophysChem1997 | 3 | 20 | ❌ Lean demuestra que la comprobación falla (3s) | Hill con exponente estimado sobre una concentración (Z^n) |
| Brannmark_JBC2010 | 9 | 15 | ✅ verificado (4s) |  |
| Chen_MSB2009 | 500 | 152 | ✅ verificado (593s) | tiempo como estado |
| Crauste_CellSystems2017 | 5 | 12 | ✅ verificado (5s) |  |
| Elowitz_Nature2000 | 8 | 18 | ❌ Lean demuestra que la comprobación falla (3s) | Hill con exponente estimado sobre una concentración (x^θ no es C¹ en x = 0 si θ < 1) |
| Fiedler_BMCSystBiol2016 | 6 | 12 | ❌ Lean demuestra que la comprobación falla (2s) | tiempo como estado; entrada k10 − k11·e^{−t/τ2}(e^{−t/τ1} − 1) ≥ 0, pero el comprobador sintáctico no lo detecta (conservador) |
| Froehlich_CellSystems2018 | 1228 | 4088 | ⏸ sin verificar: Lean sin memoria (3093s); Python predice que pasa |  |
| Giordano_Nature2020 | 10 | 43 | ✅ verificado (5s) | 6 tramos (escalones) |
| Lang_PLOSComputBiol2024 | 124 | 164 | ✅ verificado (109s) | nominal 0 en escala log: kDpApc_1, kDpE2f1, kPhC25A |
| Okuonghae_ChaosSolitonsFractals2020 | 8 | 14 | ❌ Lean demuestra que la comprobación falla (2s) | incidencia β·S·I/N: no definida si N = 0 (el dominio no contiene todo el ortante) |
| Rahman_MBS2016 | 7 | 9 | ❌ Lean demuestra que la comprobación falla (3s) | incidencia β·S·I/N: no definida si N = 0 |
| Raia_CancerResearch2011 | 14 | 18 | ✅ verificado (5s) |  |
| Raimundez_PCB2020 | 22 | 57 | ✅ verificado (7s) | signo libre: d_AKTtotal__MKN1_2_HS746T, d_MAPKtotal__MKN1_2_HS746T, d_MPI3Ktotal__fm_2_hm, d_PI3Ktotal__fm_2_hm, d_RAStotal__MKN1_2_HS746T, d_RAStotal__fm_2_hm, d_kdeg_membran__MKN1_2_HS746T, d_kexp_pEGFR_EGF_2_i__MKN1_2_HS746T, d_kimp_pEGFR_EGF_2__MKN1_2_HS746T, d_ksyn_EGFR__MKN1_2_HS746T, d_ksyn_EGFR__fm_2_hm, d_ksyn_MMET__fm_2_hm |
| SalazarCavazos_MBoC2020 | 75 | 6 | ✅ verificado (148s) |  |
| Smith_BMCSystBiol2013 | — | — | no traducido | eventos SBML (tiempos fijos): cubierto por EventSystems, no por el traductor |
| Sneyd_PNAS2002 | 6 | 14 | ✅ verificado (4s) |  |
| Weber_BMC2015 | 7 | 26 | ✅ verificado (5s) |  |
| Zhao_QuantBiol2020 | 4 | 21 | ✅ verificado (4s) |  |
| Zheng_PNAS2012 | 15 | 45 | ✅ verificado (5s) |  |
