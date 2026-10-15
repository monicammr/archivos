# Patrones de robustez con el método final

Mediana de e_ajuste (S biológico + calibración, reajustados) frente al tamaño de la perturbación; ✓ = ≤ 0,436. A: robusto hasta ±50 %; B: colapso a partir de ±20 % o más; C: irregular (deja de cumplir y vuelve a cumplir); D: falla ya a ±10 % o menos.

| Sistema | k | ±1% | ±5% | ±10% | ±20% | ±30% | ±40% | ±50% | Patrón |
|---|---|---|---|---|---|---|---|---|---|
| Alkan_SciSignal2018 | 2 | 24% ✓ | 12% ✓ | 16% ✓ | 10% ✓ | 17% ✓ | 21% ✓ | 17% ✓ | **A** |
| Armistead_CellDeathDis2024 | 2 | 35% ✓ | 33% ✓ | 33% ✓ | 40% ✓ | 31% ✓ | 35% ✓ | 40% ✓ | **A** |
| Bachmann_MSB2011 | 2 | 32% ✓ | 34% ✓ | 31% ✓ | 34% ✓ | 29% ✓ | 33% ✓ | 35% ✓ | **A** |
| Bertozzi_PNAS2020 | 2 | 49% | 33% ✓ | 30% ✓ | 55% | 36% ✓ | 27% ✓ | 55% | **C** |
| Blasi_CellSystems2016 | 2 | 44% | 40% ✓ | 33% ✓ | 49% | 37% ✓ | 46% | 58% | **C** |
| Boehm_JProteomeRes2014 | 2 | 7% ✓ | 9% ✓ | 11% ✓ | 6% ✓ | 20% ✓ | 9% ✓ | 13% ✓ | **A** |
| Borghans_BiophysChem1997 | 2 | 10% ✓ | 4% ✓ | 8% ✓ | 29% ✓ | 32% ✓ | 23% ✓ | 43% ✓ | **A** |
| Brannmark_JBC2010 | 2 | 18% ✓ | 8% ✓ | 12% ✓ | 14% ✓ | 9% ✓ | 16% ✓ | 13% ✓ | **A** |
| Bruno_JExpBot2016 | 5 | 38% ✓ | 38% ✓ | 41% ✓ | 40% ✓ | 42% ✓ | 46% | 42% ✓ | **C** |
| Chen_MSB2009 | 2 | 6% ✓ | 8% ✓ | 10% ✓ | 8% ✓ | 8% ✓ | 11% ✓ | 9% ✓ | **A** |
| Elowitz_Nature2000 | 2 | 33% ✓ | 36% ✓ | 25% ✓ | 32% ✓ | 33% ✓ | 31% ✓ | 37% ✓ | **A** |
| Fiedler_BMCSystBiol2016 | 2 | 11% ✓ | 15% ✓ | 10% ✓ | 12% ✓ | 8% ✓ | 8% ✓ | 12% ✓ | **A** |
| Fujita_SciSignal2010 | 2 | 23% ✓ | 29% ✓ | 39% ✓ | 41% ✓ | 35% ✓ | 29% ✓ | 27% ✓ | **A** |
| Giordano_Nature2020 | 2 | 4% ✓ | 6% ✓ | 3% ✓ | 4% ✓ | 9% ✓ | 5% ✓ | 6% ✓ | **A** |
| Isensee_JCB2018 | 2 | 6% ✓ | 10% ✓ | 6% ✓ | 8% ✓ | 7% ✓ | 6% ✓ | 8% ✓ | **A** |
| Laske_PLOSComputBiol2019 | 2 | 13% ✓ | 10% ✓ | 15% ✓ | 12% ✓ | 9% ✓ | 8% ✓ | 11% ✓ | **A** |
| Liu_IFACPapersOnLine2025 | 2 | 11% ✓ | 26% ✓ | 24% ✓ | 17% ✓ | 28% ✓ | 26% ✓ | 22% ✓ | **A** |
| Lucarelli_CellSystems2018 | 10 | 41% ✓ | 44% ✓ | 35% ✓ | 41% ✓ | 44% | 51% | 44% | **B** |
| Okuonghae_ChaosSolitonsFractals2020 | 2 | 4% ✓ | 4% ✓ | 5% ✓ | 5% ✓ | 11% ✓ | 4% ✓ | 6% ✓ | **A** |
| Oliveira_NatCommun2021 | 2 | 9% ✓ | 13% ✓ | 14% ✓ | 4% ✓ | 17% ✓ | 17% ✓ | 5% ✓ | **A** |
| Perelson_Science1996 | 2 | — | 0% ✓ | 0% ✓ | 0% ✓ | 0% ✓ | 0% ✓ | 0% ✓ | **A** |
| Rahman_MBS2016 | 2 | 3% ✓ | 4% ✓ | 6% ✓ | 3% ✓ | 9% ✓ | 2% ✓ | 3% ✓ | **A** |
| Raia_CancerResearch2011 | 2 | 6% ✓ | 3% ✓ | 3% ✓ | 5% ✓ | 3% ✓ | 3% ✓ | 3% ✓ | **A** |
| Raimundez_PCB2020 | 2 | 23% ✓ | 19% ✓ | 17% ✓ | 17% ✓ | 18% ✓ | 18% ✓ | 19% ✓ | **A** |
| SalazarCavazos_MBoC2020 | 2 | 14% ✓ | 19% ✓ | 31% ✓ | 19% ✓ | 20% ✓ | 18% ✓ | 15% ✓ | **A** |
| Schwen_PONE2014 | 2 | 23% ✓ | 17% ✓ | 15% ✓ | 16% ✓ | 18% ✓ | 22% ✓ | 15% ✓ | **A** |
| Smith_BMCSystBiol2013 | 2 | 8% ✓ | 8% ✓ | 9% ✓ | 7% ✓ | 7% ✓ | 8% ✓ | 8% ✓ | **A** |
| Sneyd_PNAS2002 | 2 | 38% ✓ | 38% ✓ | 54% | 48% | 44% | 36% ✓ | 56% | **C** |
| Weber_BMC2015 | 2 | 4% ✓ | 4% ✓ | 5% ✓ | 5% ✓ | 4% ✓ | 3% ✓ | 6% ✓ | **A** |
| Zhao_QuantBiol2020 | 3 | 28% ✓ | 30% ✓ | 40% ✓ | 45% | 22% ✓ | 44% | 37% ✓ | **C** |
| Zheng_PNAS2012 | 2 | 35% ✓ | 30% ✓ | 27% ✓ | 32% ✓ | 23% ✓ | 45% | 34% ✓ | **C** |

Recuento: A: 24, B: 1, C: 6.
