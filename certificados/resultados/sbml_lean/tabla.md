| Sistema | Estados | θ | Lean | Notas |
|---|---|---|---|---|
| Armistead_CellDeathDis2024 | 4 | 10 | ✅ verificado, sin condiciones pendientes (4s); positividad estricta | signo libre: alpha_cer; las especies con dato inicial > 0 permanecen > 0 (lo exige el dominio); las tasas k00(1 + α_cer) y k3(1 − α_hai1a) son ≥ 0 si α_cer ≥ −1 y α_hai1a ≤ 1; Lean lo comprueba en θ₀, y todo el rango de PEtab (α_cer ∈ [−0,999, −0,001], α_hai1a ∈ [0,5, 0,999]) cumple esas cotas |
| Bachmann_MSB2011 | 25 | 27 | ✅ verificado, sin condiciones pendientes (10s) |  |
| Blasi_CellSystems2016 | 16 | 8 | ✅ verificado, sin condiciones pendientes (6s) |  |
| Boehm_JProteomeRes2014 | 8 | 6 | ✅ verificado, sin condiciones pendientes (4s) | tiempo como estado |
| Borghans_BiophysChem1997 | 3 | 20 | ✅ verificado, sin condiciones pendientes (5s); positividad estricta | las especies con dato inicial > 0 permanecen > 0 (lo exige el dominio) |
| Brannmark_JBC2010 | 9 | 15 | ✅ verificado, sin condiciones pendientes (5s) |  |
| Chen_MSB2009 | 500 | 152 | ✅ verificado, sin condiciones pendientes (630s) | tiempo como estado |
| Crauste_CellSystems2017 | 5 | 12 | ✅ verificado, sin condiciones pendientes para T ≤ 1.0 (5s); cota de Riccati | crecimiento cuadrático (ρ_P·P²): existencia demostrada en el horizonte del análisis, no global |
| Elowitz_Nature2000 | 8 | 18 | ✅ verificado, sin condiciones pendientes (4s); positividad estricta | las especies con dato inicial > 0 permanecen > 0 (lo exige el dominio) |
| Fiedler_BMCSystBiol2016 | 6 | 12 | ✅ verificado, sin condiciones pendientes (14s); positividad estricta | tiempo como estado; las especies con dato inicial > 0 permanecen > 0 (lo exige el dominio); entrada 1 − e^{−t/τ1} ≥ 0; dato inicial (estado estacionario con raíces) certificado > 0 por intervalos en ℚ |
| Froehlich_CellSystems2018 | 1228 | 4088 | ✅ verificado, sin condiciones pendientes (1800s) |  |
| Giordano_Nature2020 | 10 | 43 | ✅ verificado, sin condiciones pendientes (8s) | 6 tramos (escalones) |
| Lang_PLOSComputBiol2024 | 124 | 164 | ✅ verificado, sin condiciones pendientes (261s) | nominal 0 en escala log: kDpApc_1, kDpE2f1, kPhC25A |
| Okuonghae_ChaosSolitonsFractals2020 | 8 | 14 | ✅ verificado, sin condiciones pendientes (4s); positividad estricta | las especies con dato inicial > 0 permanecen > 0 (lo exige el dominio); red reescrita de forma exacta (σ(1 − ν)E y σνE); Lean comprueba ν₀ = 0,5 ≤ 1 en θ₀ (con ν > 1 la positividad falla) |
| Rahman_MBS2016 | 7 | 9 | ✅ verificado, sin condiciones pendientes (5s); positividad estricta | las especies con dato inicial > 0 permanecen > 0 (lo exige el dominio) |
| Raia_CancerResearch2011 | 14 | 18 | ✅ verificado, sin condiciones pendientes (5s) |  |
| Raimundez_PCB2020 | 22 | 57 | ✅ verificado, sin condiciones pendientes (13s) | signo libre: d_AKTtotal__MKN1_2_HS746T, d_MAPKtotal__MKN1_2_HS746T, d_MPI3Ktotal__fm_2_hm, d_PI3Ktotal__fm_2_hm, d_RAStotal__MKN1_2_HS746T, d_RAStotal__fm_2_hm, d_kdeg_membran__MKN1_2_HS746T, d_kexp_pEGFR_EGF_2_i__MKN1_2_HS746T, d_kimp_pEGFR_EGF_2__MKN1_2_HS746T, d_ksyn_EGFR__MKN1_2_HS746T, d_ksyn_EGFR__fm_2_hm, d_ksyn_MMET__fm_2_hm |
| SalazarCavazos_MBoC2020 | 75 | 6 | ✅ verificado, sin condiciones pendientes (324s) |  |
| Smith_BMCSystBiol2013 | — | — | no traducido | las reacciones R16f/R17f usan max(PIP3 − basal, 0), que no es diferenciable: el campo no es C¹ y el teorema de diferenciabilidad no aplica (los eventos en tiempos fijos sí se traducen) |
| Sneyd_PNAS2002 | 6 | 14 | ✅ verificado, sin condiciones pendientes (5s) |  |
| Weber_BMC2015 | 7 | 26 | ✅ verificado, sin condiciones pendientes (5s) |  |
| Zhao_QuantBiol2020 | 4 | 21 | ✅ verificado, sin condiciones pendientes (4s) |  |
| Zheng_PNAS2012 | 15 | 45 | ✅ verificado, sin condiciones pendientes (7s) |  |
