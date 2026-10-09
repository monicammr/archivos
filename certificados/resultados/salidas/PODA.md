# Selección con poda (comentario 2)

Selección voraz sobre las salidas medidas y, después, eliminación hacia atrás: se quita cada parámetro (del menos al más influyente) mientras el subconjunto siga siendo admisible (|S| ≥ 2 y e_ajuste ≤ 43,6 %). Resultado mínimo por inclusión (Lean: `Poda.prune_spec`).

| Sistema | Etapa | |S| antes | |S| después | Quitados | S final | e_ajuste | Admisible |
|---|---|---|---|---|---|---|---|
| Armistead_CellDeathDis2024 | Stage 2 | 4 | 2 | k00, k2 | k_d, alpha_cer | 11.7 % | ✓ |
| Bertozzi_PNAS2020 | Stage 2 | 2 | 2 | — | R0_NY, I0_NY | 32.9 % | ✓ |
| Blasi_CellSystems2016 | Stage 1 | 5 | 2 | a_k12k16_k8k12k16, a_k5k12_k5k8k12, a_k8k12k16_4ac | a_basal, a_k16_k12k16 | 40.2 % | ✓ |
| Boehm_JProteomeRes2014 | Stage 2 | 2 | 2 | — | k_imp_hetero, k_phos | 9.4 % | ✓ |
| Borghans_BiophysChem1997 | Stage 2 | 2 | 2 | — | Kz, K_par | 16.3 % | ✓ |
| Brannmark_JBC2010 | Stage 2 | 2 | 2 | — | k_IRP_1Step, k1f | 22.2 % | ✓ |
| Bruno_JExpBot2016 | Stage 1 | 7 | 5 | szea, init_b10_1 | kb1, init_bcar2, init_zea_1, init_bcar1, init_bcry_1 | 37.8 % | ✓ |
| Crauste_CellSystems2017 | Stage 2 | 1 | 1 | — | rho_E | 95.2 % | ✗ |
| Elowitz_Nature2000 | Stage 1 | 6 | 2 | tau_prot, scale, tau_prot_GFP, eff | n_Hill, tau_mRNA | 43.4 % | ✓ |
| Fiedler_BMCSystBiol2016 | Stage 2 | 5 | 4 | k6 | tau2, s_pMek_20140505_gel2, s_pMek_20140430_gel2, k3 | 40.1 % | ✓ |
| Fujita_SciSignal2010 | Stage 2 | 2 | 2 | — | init_AKT, scaling_pS6_tot | 32.5 % | ✓ |
| Giordano_Nature2020 | Stage 2 | 2 | 2 | — | alpha_4, alpha_28 | 5.8 % | ✓ |
| Laske_PLOSComputBiol2019 | Stage 1 | 2 | 2 | — | Int_nuc_off, k_imp | 15.8 % | ✓ |
| Liu_IFACPapersOnLine2025 | Stage 2 | 2 | 2 | — | kappa, phi | 26.1 % | ✓ |
| Okuonghae_ChaosSolitonsFractals2020 | Stage 2 | 2 | 2 | — | transmission_rate_effective, gamma_i | 4.1 % | ✓ |
| Oliveira_NatCommun2021 | Stage 2 | 2 | 2 | — | beta_0, h_hosp_rate | 12.9 % | ✓ |
| Perelson_Science1996 | Stage 1 | 2 | 2 | — | c, delta | 0.0 % | ✓ |
| Rahman_MBS2016 | Stage 2 | 2 | 2 | — | infected_moderate_transmission_rate, infected_normal_worsen_rate | 3.7 % | ✓ |
| Raia_CancerResearch2011 | Stage 2 | 2 | 2 | — | scaling_SOCS3mRNA, init_Rec_i | 4.7 % | ✓ |
| SalazarCavazos_MBoC2020 | Stage 2 | 2 | 2 | — | ratio_kpkd_Y1068__FREE, ratio_kpkd_YN__FREE | 18.7 % | ✓ |
| Schwen_PONE2014 | Stage 2 | 4 | 3 | ini_R2fold | scale, ini_R1, kon_unspec | 40.9 % | ✓ |
| Smith_BMCSystBiol2013 | Stage 2 | 3 | 3 | — | sc_GLUT_3B_240, sc_GLUT_3B_120, sc_PI3K | 34.4 % | ✓ |
| Sneyd_PNAS2002 | Stage 2 | 2 | 2 | — | l4, l2 | 38.1 % | ✓ |
| Weber_BMC2015 | Stage 2 | 2 | 2 | — | s12, a21 | 34.3 % | ✓ |
| Zhao_QuantBiol2020 | Stage 2 | 3 | 3 | — | R_Stage_I_China, R_Stage_II_Wuhan, gamma_1_Stage_I_Hubei | 29.6 % | ✓ |
| Zheng_PNAS2012 | Stage 2 | 2 | 2 | — | k01_02, k13_12 | 30.0 % | ✓ |

* Admisibles: 25 de 26.
* Parámetros en los subconjuntos admisibles: 71 antes de la poda, 58 después (13 eliminados por redundantes).
