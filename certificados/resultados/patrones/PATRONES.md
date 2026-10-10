# Patrones de robustez con el método final

Mediana de e_ajuste (S biológico + calibración, reajustados) frente al tamaño de la perturbación; ✓ = ≤ 0,436. A: robusto hasta ±50 %; B: colapso a partir de ±20 % o más; C: irregular (deja de cumplir y vuelve a cumplir); D: falla ya a ±10 % o menos.

| Sistema | k | ±1% | ±5% | ±10% | ±20% | ±30% | ±40% | ±50% | Patrón |
|---|---|---|---|---|---|---|---|---|---|
| Alkan_SciSignal2018 | 2 | 12% ✓ | 12% ✓ | 13% ✓ | 13% ✓ | 14% ✓ | 14% ✓ | 15% ✓ | **A** |
| Armistead_CellDeathDis2024 | 2 | 3% ✓ | 12% ✓ | 20% ✓ | 40% ✓ | 54% | 60% | 63% | **B** |
| Bachmann_MSB2011 | 2 | 34% ✓ | 34% ✓ | 33% ✓ | 32% ✓ | 32% ✓ | 32% ✓ | 34% ✓ | **A** |
| Bertozzi_PNAS2020 | 2 | 31% ✓ | 33% ✓ | 36% ✓ | 43% ✓ | 45% | 51% | 55% | **B** |
| Blasi_CellSystems2016 | 2 | 41% ✓ | 40% ✓ | 40% ✓ | 43% ✓ | 45% | 44% | 44% | **B** |
| Boehm_JProteomeRes2014 | 2 | 10% ✓ | 9% ✓ | 9% ✓ | 10% ✓ | 10% ✓ | 10% ✓ | 10% ✓ | **A** |
| Borghans_BiophysChem1997 | 2 | 20% ✓ | 4% ✓ | 8% ✓ | 17% ✓ | 17% ✓ | 23% ✓ | 16% ✓ | **A** |
| Brannmark_JBC2010 | 2 | 8% ✓ | 8% ✓ | 8% ✓ | 8% ✓ | 8% ✓ | 8% ✓ | 7% ✓ | **A** |
| Bruno_JExpBot2016 | 5 | 37% ✓ | 38% ✓ | 38% ✓ | 39% ✓ | 40% ✓ | 40% ✓ | 41% ✓ | **A** |
| Elowitz_Nature2000 | 2 | 35% ✓ | 36% ✓ | 37% ✓ | 44% | 44% | 46% | 48% | **B** |
| Fiedler_BMCSystBiol2016 | 2 | 15% ✓ | 15% ✓ | 14% ✓ | 13% ✓ | 12% ✓ | 11% ✓ | 10% ✓ | **A** |
| Fujita_SciSignal2010 | 2 | 29% ✓ | 29% ✓ | 28% ✓ | 25% ✓ | 25% ✓ | 26% ✓ | 25% ✓ | **A** |
| Giordano_Nature2020 | 2 | 6% ✓ | 6% ✓ | 5% ✓ | 6% ✓ | 8% ✓ | 9% ✓ | 9% ✓ | **A** |
| Isensee_JCB2018 | 2 | 9% ✓ | 10% ✓ | 7% ✓ | 5% ✓ | 8% ✓ | 7% ✓ | 6% ✓ | **A** |
| Lang_PLOSComputBiol2024 | 2 | 17% ✓ | 16% ✓ | 14% ✓ | 10% ✓ | 7% ✓ | 6% ✓ | 5% ✓ | **A** |
| Laske_PLOSComputBiol2019 | 2 | 10% ✓ | 10% ✓ | 10% ✓ | 11% ✓ | 11% ✓ | 12% ✓ | 12% ✓ | **A** |
| Liu_IFACPapersOnLine2025 | 2 | 26% ✓ | 26% ✓ | 26% ✓ | 25% ✓ | 23% ✓ | 23% ✓ | 22% ✓ | **A** |
| Lucarelli_CellSystems2018 | 10 | 44% | 44% ✓ | 43% ✓ | 43% ✓ | 44% | 45% | 47% | **C** |
| Okuonghae_ChaosSolitonsFractals2020 | 2 | 4% ✓ | 4% ✓ | 4% ✓ | 5% ✓ | 5% ✓ | 5% ✓ | 5% ✓ | **A** |
| Oliveira_NatCommun2021 | 2 | 13% ✓ | 13% ✓ | 13% ✓ | 14% ✓ | 15% ✓ | 15% ✓ | 17% ✓ | **A** |
| Perelson_Science1996 | 2 | — | 0% ✓ | 0% ✓ | 0% ✓ | 0% ✓ | 0% ✓ | 0% ✓ | **A** |
| Rahman_MBS2016 | 2 | 3% ✓ | 4% ✓ | 4% ✓ | 4% ✓ | 5% ✓ | 5% ✓ | 5% ✓ | **A** |
| Raia_CancerResearch2011 | 2 | 3% ✓ | 3% ✓ | 3% ✓ | 3% ✓ | 3% ✓ | 4% ✓ | 4% ✓ | **A** |
| Raimundez_PCB2020 | 2 | 37% ✓ | 37% ✓ | 37% ✓ | 36% ✓ | 36% ✓ | 34% ✓ | 34% ✓ | **A** |
| SalazarCavazos_MBoC2020 | 2 | 19% ✓ | 19% ✓ | 19% ✓ | 19% ✓ | 19% ✓ | 18% ✓ | 17% ✓ | **A** |
| Schwen_PONE2014 | 2 | 17% ✓ | 17% ✓ | 17% ✓ | 18% ✓ | 19% ✓ | 18% ✓ | 17% ✓ | **A** |
| Sneyd_PNAS2002 | 2 | 41% ✓ | 38% ✓ | 34% ✓ | 35% ✓ | 35% ✓ | 33% ✓ | 33% ✓ | **A** |
| Weber_BMC2015 | 2 | 4% ✓ | 4% ✓ | 4% ✓ | 4% ✓ | 4% ✓ | 4% ✓ | 4% ✓ | **A** |
| Zhao_QuantBiol2020 | 3 | 27% ✓ | 30% ✓ | 33% ✓ | 28% ✓ | 26% ✓ | 19% ✓ | 16% ✓ | **A** |
| Zheng_PNAS2012 | 2 | 30% ✓ | 30% ✓ | 30% ✓ | 30% ✓ | 30% ✓ | 32% ✓ | 33% ✓ | **A** |

Recuento: A: 25, B: 4, C: 1.
