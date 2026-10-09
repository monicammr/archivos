# ¿Basta un parámetro? (decisión sobre la regla |S| ≥ 2)

Mejor parámetro solo {j} frente al subconjunto seleccionado S. e_ajuste a ±10 % (umbral 43,6 %); predicción de experimentos no usados: χ²/n en prueba con datos reales (menor es mejor; ≈ 1 = nivel del ruido) y e_pred con datos sintéticos (umbral 0,436).

| Sistema | j | S | e_ajuste ±10 %: j / S | χ²/n prueba (real): j / S | e_pred (sintético): j / S |
|---|---|---|---|---|---|
| Armistead_CellDeathDis2024 | alpha_cer | k_d, k00, k2, alpha_cer | 32.9 % / 21.3 % | 1.16 / 1.37 | 1.00 / 0.17 |
| Borghans_BiophysChem1997 | Kz | Kz, K_par | 56.1 % / 34.1 % | 0.74 / 0.74 | 1.00 / 1.00 |
| Giordano_Nature2020 | gamma_4 | alpha_4, alpha_28 | 11.4 % / 5.4 % | 0.00 / 0.00 | 1.78 / 1027.14 |
| Laske_PLOSComputBiol2019 | Int_nuc_off | Int_nuc_off, k_imp | 27.8 % / 16.2 % | no evaluable / 0.44 | no evaluable / 3.19 |
| Okuonghae_ChaosSolitonsFractals2020 | gamma_0 | transmission_rate_effective, gamma_i | 4.8 % / 4.2 % | 40763.76 / 46705.21 | 0.30 / 0.08 |
| Oliveira_NatCommun2021 | delta_ | beta_0, h_hosp_rate | 12.3 % / 13.2 % | 20075.89 / 1082.30 | 0.38 / 0.29 |
| Rahman_MBS2016 | infected_moderate_transmission_rate | infected_moderate_transmission_rate, infected_normal_worsen_rate | 12.4 % / 4.0 % | 0.00 / 0.00 | 0.35 / 0.07 |
| Raia_CancerResearch2011 | SOCS3mRNA_production | scaling_SOCS3mRNA, init_Rec_i | 7.6 % / 4.5 % | 0.41 / 6.92 | 1.10 / 0.47 |
| SalazarCavazos_MBoC2020 | ratio_kpkd_Y1068__FREE | ratio_kpkd_Y1068__FREE, ratio_kpkd_YN__FREE | 29.4 % / 40.6 % | 100.00 / 101.83 | 0.79 / 0.17 |
| Weber_BMC2015 | p31 | s12, a21 | 42.1 % / 33.6 % | 0.99 / 0.99 | 0.27 / 0.77 |

* Sintético (predicción de experimentos nuevos): S predice mejor en 6, un parámetro igual o mejor en 3.
* ±10 %: un parámetro sigue siendo admisible en 9 de 10; S en 10 de 10.
* «no evaluable»: el parámetro sólo actúa en las condiciones de prueba (no se puede estimar con las de entrenamiento).
