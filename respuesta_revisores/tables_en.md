# Tables (English version)

## Table A. Per-system results (final method)

Measured outputs (PEtab observables, conditions, noise); selection among biological parameters only, calibration parameters (scalings/offsets) always re-estimated; backward elimination. e_fit: median relative error after re-estimation over 15 scenarios at ±5% (threshold 0.436 ⇔ cos Δ ≥ 0.9). External validation: χ²/n on held-out conditions (real data; reduced vs full model re-fitted on the training conditions; full model only for p ≤ 60; θ₀ = published estimate, obtained with all data including the test conditions) and relative prediction error e_pred on synthetic noisy data (truth θ* = θ₀ ± 20%, Gaussian noise with the PEtab σ). When the effect of the perturbation on the test outputs is smaller than the noise (χ²/n(θ₀) < 2), e_pred is not informative and the test χ²/n of the reduced model is reported instead (≈ 1 = prediction at noise level). * e_fit computed to first order (linearized) for computational cost.

| System | p | Meas. | Cond. | Stage | k (biological) | Selected biological parameters | Calibration re-estimated | e_fit | Admissible | χ²/n test (reduced / full / θ₀) | e_pred (synthetic) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Alkan | 44 | 1733 | 73 | 1 | 2 | kt, k_rep_nhej | 10 | 12.1%* | yes | 2.75 / 3.38 / 2.47 | 0.13 |
| Armistead | 14 | 58 | 2 | 2 | 2 | k_d, alpha_cer | 0 | 11.7% | yes | 1.22 / 1.37 / 1.16 | noise-dominated (χ²/n = 1.11) |
| Bachmann | 113 | 541 | 36 | 2 | 2 | CISRNADelay, JAK2ActEpo | 74 | 33.7%* | yes | 4.77 / — / 1.05 | noise-dominated (χ²/n = 3.37) |
| Beer | 72 | 27132 | 19 | 2 | 18 | kdegi_typeIDT1, kdegi_typeIDT3, ksyn_typeIDT3, kdim_typeIDT1, beta_typeIDT3_ExpID2, beta_typeIDT3_ExpID3, beta_typeIDT3_ExpID5, beta_typeIDT3_ExpID1, beta_typeIDT3_ExpID4, init_Bac, beta_typeIDT1_ExpID6, beta_typeIDT1_ExpID5, beta_typeIDT1_ExpID1, beta_typeIDT1_ExpID4, beta_typeIDT1_ExpID3, kdim_typeIDwt, ksyn_typeIDT5, kdim_typeIDT5 | 0 | 50.1%* | no | not run | — |
| Bertozzi | 8 | 22 | 2 | 2 | 2 | R0_NY, I0_NY | 0 | 32.9% | yes | not evaluable | — |
| Blasi | 9 | 252 | 1 | 1 | 2 | a_basal, a_k16_k12k16 | 0 | 40.2% | yes | not evaluable | — |
| Boehm | 9 | 48 | 1 | 2 | 2 | k_imp_hetero, k_phos | 0 | 9.4% | yes | 2.57 / 11.35 / 0.34 | noise-dominated (χ²/n = 0.57) |
| Borghans | 23 | 111 | 1 | 2 | 2 | Kz, K_par | 2 | 4.3% | yes | 0.74 / 0.74 / 0.74 | 1.04 |
| Brannmark | 22 | 43 | 8 | 2 | 2 | k1f, km2 | 3 | 7.8% | yes | 5.79 / 2145.47 / 0.94 | 0.92 |
| Bruno | 13 | 77 | 6 | 1 | 5 | kb1, init_bcar2, init_zea_1, init_bcar1, init_bcry_1 | 0 | 37.8% | yes | 0.91 / 7.86 / 0.91 | noise-dominated (χ²/n = 0.46) |
| Chen | 155 | 120 | 4 | 2 | 2 | k106, k44 | 3 | 8.2%* | yes | not run | — |
| Crauste | 12 | 21 | 1 | 2 | 1 | rho_E | 0 | 95.2% | no | not run | — |
| Elowitz | 21 | 58 | 1 | 1 | 2 | n_Hill, tau_mRNA | 2 | 35.8% | yes | 1.50 / 4.45 / 1.38 | 0.47 |
| Fiedler | 22 | 72 | 3 | 2 | 2 | tau2, k6 | 8 | 14.7% | yes | 11.21 / 14.11 / 1.22 | noise-dominated (χ²/n = 0.53) |
| Fujita | 19 | 144 | 6 | 2 | 2 | init_AKT, reaction_6_k1 | 3 | 29.4% | yes | 5.94 / 8.04 / 5.63 | noise-dominated (χ²/n = 1.47) |
| Giordano | 50 | 313 | 1 | 2 | 2 | alpha_4, alpha_28 | 0 | 5.8% | yes | 0.00 / 0.06 / 0.00 | noise-dominated (χ²/n = 0.86) |
| Isensee | 46 | 687 | 123 | 1 | 2 | kf_RIIp_C_2__RII_C_2, xi_kf_RII_C_2__RII_2 | 11 | 7.6%* | yes | 1.08 / 1.08 / 1.04 | — |
| Lang | 294 | 9600 | 1 | 2 | 2 | kDeE2f1, kDeCe | 16 | 16.1%* | yes | 8.98 / — / 7.33 | 0.17 |
| Laske | 13 | 42 | 3 | 1 | 2 | k_imp, k_syn_R_M | 2 | 10.1% | yes | 0.76 / 1.88 / 0.44 | noise-dominated (χ²/n = 0.44) |
| Liu | 9 | 100 | 2 | 2 | 2 | kappa, phi | 0 | 26.1% | yes | 0.95 / 1.02 / 0.94 | noise-dominated (χ²/n = 0.58) |
| Lucarelli | 84 | 1755 | 16 | 2 | 10 | init_Rec, S2tot, S3tot, S_dephosphos, S_phos, geneF_turn, k_234, geneK_turn, S4tot, geneH_turn | 0 | 43.5%* | yes | 1.57 / — / 1.02 | noise-dominated (χ²/n = 1.30) |
| Okuonghae | 16 | 92 | 1 | 2 | 2 | transmission_rate_effective, gamma_i | 0 | 4.1% | yes | 46705.21 / 122419.25 / 28748.50 | 0.08 |
| Oliveira | 12 | 120 | 1 | 2 | 2 | beta_0, h_hosp_rate | 0 | 12.9% | yes | 914.51 / 81453.15 / 460396.13 | 0.29 |
| Perelson | 3 | 16 | 1 | 1 | 2 | c, delta | 0 | 0.0% | yes | 0.00 / 0.00 / 0.00 | noise-dominated (χ²/n = 0.68) |
| Rahman | 9 | 23 | 1 | 2 | 2 | infected_moderate_transmission_rate, infected_normal_worsen_rate | 0 | 3.7% | yes | 0.00 / 0.03 / 0.00 | 0.07 |
| Raia | 39 | 205 | 4 | 2 | 2 | SOCS3mRNA_production, init_Rec_i | 5 | 3.3% | yes | 8.23 / 5.10 / 0.42 | noise-dominated (χ²/n = 0.92) |
| Raimundez | 136 | 627 | 170 | 2 | 2 | kdeg_membran__MKN1, d_kimp_pEGFR_EGF_2__MKN1_2_HS746T | 79 | 37.2%* | yes | 1.19 / — / 0.98 | 1.27 |
| SalazarCavazos | 6 | 18 | 4 | 2 | 2 | ratio_kpkd_Y1068__FREE, ratio_kpkd_YN__FREE | 0 | 18.7% | yes | 101.83 / 124.19 / 96.93 | 0.17 |
| Schwen | 30 | 286 | 19 | 2 | 2 | ini_R1, ini_R2fold | 15 | 17.1% | yes | 8.20 / 8.40 / 0.77 | noise-dominated (χ²/n = 4.56) |
| Smith | 25 | 62 | 35 | 2 | 2 | k8, kminus7b | 9 | 7.8% | yes | 14976.89 / 14977.66 / 82920.71 | 0.07 |
| Sneyd | 15 | 135 | 9 | 2 | 2 | l4, l2 | 0 | 38.1% | yes | 2.22 / 2.55 / 1.37 | noise-dominated (χ²/n = 0.90) |
| Weber | 36 | 135 | 2 | 2 | 2 | s12, a21 | 5 | 4.1% | yes | 1.00 / 226.02 / 0.99 | 0.63 |
| Zhao | 28 | 82 | 7 | 2 | 3 | R_Stage_I_China, R_Stage_II_Wuhan, gamma_1_Stage_I_Hubei | 0 | 29.6% | yes | 0.35 / 0.35 / 0.35 | noise-dominated (χ²/n = 0.87) |
| Zheng | 46 | 60 | 1 | 2 | 2 | k01_02, k13_12 | 0 | 30.0% | yes | 1.58 / 20.60 / 1.51 | 0.36 |

Admissible: 32 of 34 PEtab systems. Not included: Froehlich_CellSystems2018 (9,169 experimental conditions; see Table B) and the SCT Bandura model (not a PEtab problem; analysed on states only).

## Table B. Computational cost

The dominant step is the sensitivity matrix J by central differences (2p simulations) plus the stage-2 scan (p simulations); all simulations are independent (embarrassingly parallel). Greedy selection, κ/VIF, backward elimination and the linearized e_fit use only J (linear algebra). Times measured on a 4-core server.

| System | p | Data | Time per simulation | Simulations (3p) | Serial time | 4 cores |
|---|---|---|---|---|---|---|
| Boehm | 9 | measured outputs | 0.00168 s | 27 | 0 s | 0 s |
| Elowitz | 21 | measured outputs | 0.00243 s | 63 | 0 s | 0 s |
| Fiedler | 22 | measured outputs | 0.00257 s | 66 | 0 s | 0 s |
| Weber | 36 | measured outputs | 0.00374 s | 108 | 0 s | 0 s |
| Raia | 39 | measured outputs | 0.0106 s | 117 | 1 s | 0 s |
| Alkan | 44 | measured outputs | 0.13 s | 132 | 17 s | 4 s |
| Zheng | 46 | measured outputs | 0.00449 s | 138 | 1 s | 0 s |
| Isensee | 46 | measured outputs | 0.64 s | 138 | 88 s | 22 s |
| Giordano | 50 | measured outputs | 0.00613 s | 150 | 1 s | 0 s |
| Beer | 72 | measured outputs | 0.173 s | 216 | 37 s | 9 s |
| Lucarelli | 84 | measured outputs | 0.04 s | 252 | 10 s | 3 s |
| Bachmann | 113 | measured outputs | 0.04 s | 339 | 14 s | 3 s |
| Raimundez | 136 | measured outputs | 0.37 s | 408 | 3 min | 38 s |
| Chen | 155 | measured outputs | 35 s | 465 | 4.5 h | 68 min |
| Lang | 294 | measured outputs | 0.65 s | 882 | 10 min | 2 min |
| Froehlich | 4231 | states | 2.93 s | 12693 | 10.3 h | 2.6 h |

Cost grows linearly in p. Froehlich (4,231 parameters, 1,228 species) was processed completely on states; on its measured outputs (9,169 conditions) each evaluation requires ~9,000 simulations and it was excluded. For such models, forward or adjoint sensitivity equations (e.g. AMICI) compute J at the cost of a few simulations.

## Table C. Sensitivity to the method thresholds

Final method re-run on the small and medium systems changing one threshold at a time (baseline: τ_R = 0.89, τ_κ = τ_VIF = 10, τ_e = 0.436). Same S: identical selected subset as the baseline.

| Setting | Systems | Admissible | Mean k (admissible) | Stage 1 | Same S | Same stage |
|---|---|---|---|---|---|---|
| τ_R = 0.80 | 26 | 25 | 2.16 | 8 | 26/26 | 23/26 |
| τ_R = 0.85 | 15 | 14 | 2.07 | 2 | 15/15 | 15/15 |
| baseline | 26 | 25 | 2.16 | 5 | 26/26 | 26/26 |
| τ_κ = τ_VIF = 5 | 26 | 25 | 2.16 | 5 | 23/26 | 26/26 |
| τ_κ = τ_VIF = 30 | 15 | 14 | 2.07 | 3 | 13/15 | 14/15 |
| τ_e = 0.20 | 20 | 19 | 2.89 | 2 | 13/20 | 19/20 |

Robustness to δ (0.1%, 1%, 5%), integrator tolerances, perturbation size (±1%, ±5%, ±10%) and time grid (N_t = 30, 60, 120; horizon 2T) is reported separately (sensitivity analysis, reviewer 4 comment 6).
