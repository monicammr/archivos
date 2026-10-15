# Minimalidad del subconjunto (comentario 2)

Criterio en todas las pruebas: mediana de e_ajuste ≤ 43,6 % (equivale a cos Δ ≥ 0,9 tras reajustar, demostrado en Lean). Sobre las salidas medidas de PEtab.

| Sistema | |S| | ¿Sobra algún parámetro? (quitar uno) | Mejor e_ajuste al quitar uno | ¿Basta un solo parámetro? (de los más influyentes) | Mejor e_ajuste con uno solo |
|---|---|---|---|---|---|
| Armistead_CellDeathDis2024 | 4 | sí: k_d, k00, k2 | 11.1 % | sí: alpha_cer | 16.0 % |
| Bertozzi_PNAS2020 | 2 | no | 46.3 % | no | 46.2 % |
| Blasi_CellSystems2016 | 5 | sí: a_k16_k12k16, a_k12k16_k8k12k16, a_k5k12_k5k8k12, a_k8k12k16_4ac | 24.4 % | no | 50.3 % |
| Boehm_JProteomeRes2014 | 2 | no | 46.3 % | no | 45.8 % |
| Borghans_BiophysChem1997 | 2 | sí: K_par | 25.8 % | sí: Kz, v0 | 25.8 % |
| Brannmark_JBC2010 | 2 | no | 55.9 % | no | 55.9 % |
| Bruno_JExpBot2016 | 7 | sí: init_bcar1, szea, init_bcry_1, init_b10_1 | 33.5 % | no | 85.9 % |
| Elowitz_Nature2000 | 6 | sí: n_Hill, tau_mRNA, tau_prot, scale, tau_prot_GFP, eff | 19.5 % | no | 73.5 % |
| Fiedler_BMCSystBiol2016 | 5 | sí: s_pMek_20140430_gel2, k6 | 40.1 % | no | 60.3 % |
| Fujita_SciSignal2010 | 2 | no | 46.7 % | no | 46.7 % |
| Giordano_Nature2020 | 2 | sí: alpha_28 | 11.3 % | sí: alpha_4, alpha_0, epsilon_0, epsilon_12, alpha_22, zeta_0, gamma_4, theta, lam_0 | 11.3 % |
| Laske_PLOSComputBiol2019 | 2 | sí: k_imp | 27.8 % | sí: Int_nuc_off | 27.8 % |
| Liu_IFACPapersOnLine2025 | 2 | no | 56.7 % | no | 52.7 % |
| Okuonghae_ChaosSolitonsFractals2020 | 2 | sí: gamma_i | 6.5 % | sí: transmission_rate_effective, nu, gamma_0, sigma, alpha, psi, gamma_a, exposed_start, symptomatic_start, d_0 | 4.9 % |
| Oliveira_NatCommun2021 | 2 | sí: h_hosp_rate | 12.9 % | sí: beta_0, delta_, t_1, beta_1, asymptomatic_init_concentration, symptomatic_init_concentration | 11.2 % |
| Perelson_Science1996 | 2 | no | 50.8 % | no | 50.8 % |
| Rahman_MBS2016 | 2 | sí: infected_moderate_transmission_rate, infected_normal_worsen_rate | 11.2 % | sí: infected_moderate_transmission_rate, infected_normal_transmission_rate_relative, infected_normal_worsen_rate, infected_weak_transmission_rate_relative | 11.2 % |
| Raia_CancerResearch2011 | 2 | sí: scaling_SOCS3mRNA, init_Rec_i | 7.8 % | sí: scaling_SOCS3mRNA, SOCS3mRNA_production, STAT5_phosphorylation, pSTAT5_dephosphorylation, JAK2_phosphorylation, init_Rec_i, pRec_intern, Rec_recycle, pJAK2_dephosphorylation, Kon_IL13Rec | 7.7 % |
| SalazarCavazos_MBoC2020 | 2 | sí: ratio_kpkd_Y1068__FREE, ratio_kpkd_YN__FREE | 29.7 % | sí: ratio_kpkd_Y1068__FREE, ratio_kpkd_YN__FREE, SHC1_total__FREE, kdephosY1068__FREE | 29.7 % |
| Schwen_PONE2014 | 4 | sí: ini_R1, ini_R2fold | 40.9 % | no | 72.8 % |
| Smith_BMCSystBiol2013 | 3 | no | 48.8 % | no | 78.1 % |
| Sneyd_PNAS2002 | 2 | no | 75.1 % | no | 73.5 % |
| Weber_BMC2015 | 2 | no | 48.7 % | sí: m31, p31, s21 | 39.8 % |
| Zhao_QuantBiol2020 | 3 | no | 46.5 % | no | 61.2 % |
| Zheng_PNAS2012 | 2 | no | 67.1 % | no | 67.1 % |

* Mínimos por inclusión (no sobra ningún parámetro): 11 de 25.
* Sistemas donde un solo parámetro bastaría: 10 de 25.
