# Selección sobre estados frente a salidas medidas

**Estados**: trayectorias de todos los estados x(t) en 60 puntos de [0, T] (v3). **Salidas**: predicciones de las mediciones de PEtab, y_i = h(g_i(x(t_i), θ))/σ_i (observables, condiciones experimentales, preequilibrio, transformación y ruido; `petab_outputs.py`). Mismas reglas en ambos casos (Etapa 1: R_var ≥ 0,89; Etapa 2: barrido; admisible ⇔ |S| ≥ 2 y e_ajuste ≤ 0,436). ✓ = admisible, ✗ = no admisible.

| Sistema | Estados | Salidas | p | |S| salidas | cos Δ | e_rel | e_ajuste | Parámetros comunes |
|---|---|---|---|---|---|---|---|---|
| Alkan_SciSignal2018 | Stage 2 ✓ (5) | — | — | 0 | — | — | — | 0 |
| Armistead_CellDeathDis2024 | Stage 1 ✓ (2) | Stage 2 ✓ | 14 | 4 | 0.997 | 11.6 % | 5.7 % | 2 |
| Bachmann_MSB2011 | Stage 2 ✓ (2) | — | — | 0 | — | — | — | 0 |
| Beer_MolBioSystems2014 | Técnico (0) | — | — | 0 | — | — | — | 0 |
| Bertozzi_PNAS2020 | Técnico (0) | — | — | 0 | — | — | — | 0 |
| Blasi_CellSystems2016 | Stage 1 ✓ (2) | Stage 1 ✓ | 9 | 5 | 0.979 | 21.1 % | 19.8 % | 1 |
| Boehm_JProteomeRes2014 | Stage 1 ✓ (3) | Stage 2 ✓ | 9 | 2 | 0.927 | 60.0 % | 9.4 % | 2 |
| Borghans_BiophysChem1997 | Stage 2 ✓ (2) | Stage 2 ✓ | 23 | 2 | 0.863 | 50.6 % | 16.3 % | 1 |
| Brannmark_JBC2010 | Stage 2 ✓ (3) | — | — | 0 | — | — | — | 0 |
| Bruno_JExpBot2016 | Stage 1 ✓ (4) | — | — | 0 | — | — | — | 0 |
| Chen_MSB2009 | Stage 2 ✓ (2) | — | — | 0 | — | — | — | 0 |
| Crauste_CellSystems2017 | Stage 1 ✓ (2) | Stage 2 (|S| = 1) | 12 | 1 | 0.535 | 84.7 % | 95.2 % | 0 |
| Elowitz_Nature2000 | Stage 1 ✓ (2) | Stage 1 ✓ | 21 | 6 | 0.963 | 36.7 % | 5.2 % | 2 |
| Fiedler_BMCSystBiol2016 | Stage 2 ✓ (2) | Stage 2 ✓ | 22 | 5 | 0.836 | 67.2 % | 38.4 % | 1 |
| Froehlich_CellSystems2018 | Stage 1 ✓ (22) | — | — | 0 | — | — | — | 0 |
| Fujita_SciSignal2010 | Stage 2 (|S| = 1) (1) | — | — | 0 | — | — | — | 0 |
| Giordano_Nature2020 | Stage 2 ✓ (2) | — | — | 0 | — | — | — | 0 |
| Isensee_JCB2018 | Stage 2 ✓ (2) | — | — | 0 | — | — | — | 0 |
| Lang_PLOSComputBiol2024 | Stage 2 ✓ (19) | — | — | 0 | — | — | — | 0 |
| Laske_PLOSComputBiol2019 | Stage 1 ✓ (2) | — | — | 0 | — | — | — | 0 |
| Liu_IFACPapersOnLine2025 | Stage 1 ✓ (2) | — | — | 0 | — | — | — | 0 |
| Lucarelli_CellSystems2018 | Técnico (0) | — | — | 0 | — | — | — | 0 |
| Okuonghae_ChaosSolitonsFractals2020 | Stage 2 ✓ (2) | Stage 2 ✓ | 16 | 2 | 0.998 | 74.9 % | 4.1 % | 1 |
| Oliveira_NatCommun2021 | Stage 2 ✓ (2) | — | — | 0 | — | — | — | 0 |
| Perelson_Science1996 | Stage 1 ✓ (2) | — | — | 0 | — | — | — | 0 |
| Rahman_MBS2016 | Stage 2 ✓ (2) | — | — | 0 | — | — | — | 0 |
| Raia_CancerResearch2011 | Stage 2 (|S| = 1) (1) | Stage 2 ✓ | 39 | 2 | 0.994 | 70.8 % | 4.7 % | 0 |
| Raimundez_PCB2020 | Stage 1 ✓ (2) | — | — | 0 | — | — | — | 0 |
| SCT_Bandura | Stage 1 ✓ (2) | — | — | 0 | — | — | — | 0 |
| SalazarCavazos_MBoC2020 | Stage 2 ✗ (2) | Stage 2 ✓ | 6 | 2 | 0.973 | 41.1 % | 18.7 % | 2 |
| Schwen_PONE2014 | Técnico (0) | — | — | 0 | — | — | — | 0 |
| Smith_BMCSystBiol2013 | Stage 2 ✓ (2) | — | — | 0 | — | — | — | 0 |
| Sneyd_PNAS2002 | Stage 2 ✓ (2) | Stage 2 ✓ | 15 | 2 | 0.877 | 56.5 % | 38.1 % | 0 |
| Weber_BMC2015 | Stage 2 ✓ (2) | — | — | 0 | — | — | — | 0 |
| Zhao_QuantBiol2020 | Stage 2 ✓ (2) | — | — | 0 | — | — | — | 0 |
| Zheng_PNAS2012 | Stage 2 ✓ (3) | Stage 2 ✓ | 46 | 2 | 0.568 | 94.7 % | 30.0 % | 1 |

Admisibles: estados 29/36, salidas 11/12.

## Subconjuntos seleccionados (salidas)

* **Armistead_CellDeathDis2024**: k_d, k00, k2, alpha_cer
* **Blasi_CellSystems2016**: a_basal, a_k16_k12k16, a_k12k16_k8k12k16, a_k5k12_k5k8k12, a_k8k12k16_4ac
* **Boehm_JProteomeRes2014**: k_imp_hetero, k_phos
* **Borghans_BiophysChem1997**: Kz, K_par
* **Crauste_CellSystems2017**: rho_E
* **Elowitz_Nature2000**: n_Hill, tau_mRNA, tau_prot, scale, tau_prot_GFP, eff
* **Fiedler_BMCSystBiol2016**: tau2, s_pMek_20140505_gel2, s_pMek_20140430_gel2, k6, k3
* **Okuonghae_ChaosSolitonsFractals2020**: transmission_rate_effective, gamma_i
* **Raia_CancerResearch2011**: scaling_SOCS3mRNA, init_Rec_i
* **SalazarCavazos_MBoC2020**: ratio_kpkd_Y1068__FREE, ratio_kpkd_YN__FREE
* **Sneyd_PNAS2002**: l4, l2
* **Zheng_PNAS2012**: k01_02, k13_12
