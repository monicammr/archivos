# Selección sobre estados frente a salidas medidas

**Estados**: trayectorias de todos los estados x(t) en 60 puntos de [0, T] (v3). **Salidas**: predicciones de las mediciones de PEtab, y_i = h(g_i(x(t_i), θ))/σ_i (observables, condiciones experimentales, preequilibrio, transformación y ruido; `petab_outputs.py`). Mismas reglas en ambos casos (Etapa 1: R_var ≥ 0,89; Etapa 2: barrido; admisible ⇔ |S| ≥ 2 y e_ajuste ≤ 0,436). ✓ = admisible, ✗ = no admisible.

| Sistema | Estados | Salidas | p | |S| salidas | cos Δ | e_rel | e_ajuste | Parámetros comunes |
|---|---|---|---|---|---|---|---|---|
| Alkan_SciSignal2018 | Stage 2 ✓ (5) | — | — | 0 | — | — | — | 0 |
| Armistead_CellDeathDis2024 | Stage 1 ✓ (2) | Stage 2 ✓ | 14 | 4 | 0.997 | 11.6 % | 5.7 % | 2 |
| Bachmann_MSB2011 | Stage 2 ✓ (2) | Stage 2 ✓ | 113 | 22 | 0.845 | 55.4 % | 41.2 % | 2 |
| Beer_MolBioSystems2014 | Técnico (0) | — | — | 0 | — | — | — | 0 |
| Bertozzi_PNAS2020 | Técnico (0) | Stage 2 ✓ | 8 | 2 | 0.917 | 58.5 % | 32.9 % | 0 |
| Blasi_CellSystems2016 | Stage 1 ✓ (2) | Stage 1 ✓ | 9 | 5 | 0.979 | 21.1 % | 19.8 % | 1 |
| Boehm_JProteomeRes2014 | Stage 1 ✓ (3) | Stage 2 ✓ | 9 | 2 | 0.927 | 60.0 % | 9.4 % | 2 |
| Borghans_BiophysChem1997 | Stage 2 ✓ (2) | Stage 2 ✓ | 23 | 2 | 0.863 | 50.6 % | 16.3 % | 1 |
| Brannmark_JBC2010 | Stage 2 ✓ (3) | Stage 2 ✓ | 22 | 2 | 0.731 | 81.5 % | 22.2 % | 0 |
| Bruno_JExpBot2016 | Stage 1 ✓ (4) | Stage 1 ✓ | 13 | 7 | 0.954 | 30.5 % | 27.3 % | 1 |
| Chen_MSB2009 | Stage 2 ✓ (2) | Stage 2 ✓ | 155 | 2 | 0.645 | 78.1 % | 39.5 % | 0 |
| Crauste_CellSystems2017 | Stage 1 ✓ (2) | Stage 2 (|S| = 1) | 12 | 1 | 0.535 | 84.7 % | 95.2 % | 0 |
| Elowitz_Nature2000 | Stage 1 ✓ (2) | Stage 1 ✓ | 21 | 6 | 0.963 | 36.7 % | 5.2 % | 2 |
| Fiedler_BMCSystBiol2016 | Stage 2 ✓ (2) | Stage 2 ✓ | 22 | 5 | 0.836 | 67.2 % | 38.4 % | 1 |
| Froehlich_CellSystems2018 | Stage 1 ✓ (22) | — | — | 0 | — | — | — | 0 |
| Fujita_SciSignal2010 | Stage 2 (|S| = 1) (1) | Stage 2 ✓ | 19 | 2 | 0.659 | 85.1 % | 32.5 % | 0 |
| Giordano_Nature2020 | Stage 2 ✓ (2) | Stage 2 ✓ | 50 | 2 | 0.967 | 108.3 % | 5.8 % | 2 |
| Isensee_JCB2018 | Stage 2 ✓ (2) | — | — | 0 | — | — | — | 0 |
| Lang_PLOSComputBiol2024 | Stage 2 ✓ (19) | Stage 2 ✓ | 294 | 12 | 0.339 | 95.0 % | 42.6 % | 1 |
| Laske_PLOSComputBiol2019 | Stage 1 ✓ (2) | Stage 1 ✓ | 13 | 2 | 0.987 | 16.0 % | 15.8 % | 0 |
| Liu_IFACPapersOnLine2025 | Stage 1 ✓ (2) | Stage 2 ✓ | 9 | 2 | 0.923 | 47.4 % | 26.1 % | 1 |
| Lucarelli_CellSystems2018 | Técnico (0) | — | — | 0 | — | — | — | 0 |
| Okuonghae_ChaosSolitonsFractals2020 | Stage 2 ✓ (2) | Stage 2 ✓ | 16 | 2 | 0.998 | 74.9 % | 4.1 % | 1 |
| Oliveira_NatCommun2021 | Stage 2 ✓ (2) | Stage 2 ✓ | 12 | 2 | 0.950 | 133.6 % | 12.9 % | 1 |
| Perelson_Science1996 | Stage 1 ✓ (2) | Stage 1 ✓ | 3 | 2 | 1.000 | 0.0 % | 0.0 % | 2 |
| Rahman_MBS2016 | Stage 2 ✓ (2) | Stage 2 ✓ | 9 | 2 | 0.967 | 70.2 % | 3.7 % | 1 |
| Raia_CancerResearch2011 | Stage 2 (|S| = 1) (1) | Stage 2 ✓ | 39 | 2 | 0.994 | 70.8 % | 4.7 % | 0 |
| Raimundez_PCB2020 | Stage 1 ✓ (2) | Stage 2 ✓ | 136 | 5 | 0.951 | 83.5 % | 43.3 % | 1 |
| SCT_Bandura | Stage 1 ✓ (2) | — | — | 0 | — | — | — | 0 |
| SalazarCavazos_MBoC2020 | Stage 2 ✗ (2) | Stage 2 ✓ | 6 | 2 | 0.973 | 41.1 % | 18.7 % | 2 |
| Schwen_PONE2014 | Técnico (0) | Stage 2 ✓ | 30 | 4 | 0.776 | 69.3 % | 33.2 % | 0 |
| Smith_BMCSystBiol2013 | Stage 2 ✓ (2) | Stage 2 ✓ | 25 | 3 | 0.884 | 51.0 % | 34.4 % | 0 |
| Sneyd_PNAS2002 | Stage 2 ✓ (2) | Stage 2 ✓ | 15 | 2 | 0.877 | 56.5 % | 38.1 % | 0 |
| Weber_BMC2015 | Stage 2 ✓ (2) | Stage 2 ✓ | 36 | 2 | 0.493 | 102.1 % | 34.3 % | 0 |
| Zhao_QuantBiol2020 | Stage 2 ✓ (2) | Stage 2 ✓ | 28 | 3 | 0.902 | 69.5 % | 29.6 % | 0 |
| Zheng_PNAS2012 | Stage 2 ✓ (3) | Stage 2 ✓ | 46 | 2 | 0.568 | 94.7 % | 30.0 % | 1 |

Admisibles: estados 29/36, salidas 29/30.

## Subconjuntos seleccionados (salidas)

* **Armistead_CellDeathDis2024**: k_d, k00, k2, alpha_cer
* **Bachmann_MSB2011**: CISRNADelay, JAK2ActEpo, EpoRActJAK2, STAT5Imp, STAT5Exp, JAK2EpoRDeaSHP1, CISTurn, scale_SHP1_shp1oe, scale_tSTAT5_actd, scale_pSTAT5_dr10, scale_pSTAT5_actd, STAT5ActJAK2, scale_tSTAT5_long, scale1_CIS_dr90, scale2_CIS_dr90, scale_SOCS3_socs3oe, offset_SOCS3_cisoe, scale_pSTAT5_long, SOCS3EqcOE, init_SHP1, SOCS3RNATurn, offset_CIS_actd
* **Bertozzi_PNAS2020**: R0_NY, I0_NY
* **Blasi_CellSystems2016**: a_basal, a_k16_k12k16, a_k12k16_k8k12k16, a_k5k12_k5k8k12, a_k8k12k16_4ac
* **Boehm_JProteomeRes2014**: k_imp_hetero, k_phos
* **Borghans_BiophysChem1997**: Kz, K_par
* **Brannmark_JBC2010**: k_IRP_1Step, k1f
* **Bruno_JExpBot2016**: kb1, init_bcar2, init_zea_1, init_bcar1, szea, init_bcry_1, init_b10_1
* **Chen_MSB2009**: AKT_t, k106
* **Crauste_CellSystems2017**: rho_E
* **Elowitz_Nature2000**: n_Hill, tau_mRNA, tau_prot, scale, tau_prot_GFP, eff
* **Fiedler_BMCSystBiol2016**: tau2, s_pMek_20140505_gel2, s_pMek_20140430_gel2, k6, k3
* **Fujita_SciSignal2010**: init_AKT, scaling_pS6_tot
* **Giordano_Nature2020**: alpha_4, alpha_28
* **Lang_PLOSComputBiol2024**: oCCNA, kDeE2f1, oRB1_pSer807Ser811, oCDKN1B, oSKP2, oCDKN1A, kWee2, oCCNE, oCCNB, sCCNE, sRB1_pSer807Ser811, sCCNB
* **Laske_PLOSComputBiol2019**: Int_nuc_off, k_imp
* **Liu_IFACPapersOnLine2025**: kappa, phi
* **Okuonghae_ChaosSolitonsFractals2020**: transmission_rate_effective, gamma_i
* **Oliveira_NatCommun2021**: beta_0, h_hosp_rate
* **Perelson_Science1996**: c, delta
* **Rahman_MBS2016**: infected_moderate_transmission_rate, infected_normal_worsen_rate
* **Raia_CancerResearch2011**: scaling_SOCS3mRNA, init_Rec_i
* **Raimundez_PCB2020**: kdeg_membran__MKN1, s_pMAPK_ID9b_MKN1_HM_1EGF, ka_MAPK__MKN1, d_kimp_pEGFR_EGF_2__MKN1_2_HS746T, d_ksyn_EGFR__MKN1_2_HS746T
* **SalazarCavazos_MBoC2020**: ratio_kpkd_Y1068__FREE, ratio_kpkd_YN__FREE
* **Schwen_PONE2014**: scale, ini_R1, ini_R2fold, kon_unspec
* **Smith_BMCSystBiol2013**: sc_GLUT_3B_240, sc_GLUT_3B_120, sc_PI3K
* **Sneyd_PNAS2002**: l4, l2
* **Weber_BMC2015**: s12, a21
* **Zhao_QuantBiol2020**: R_Stage_I_China, R_Stage_II_Wuhan, gamma_1_Stage_I_Hubei
* **Zheng_PNAS2012**: k01_02, k13_12
