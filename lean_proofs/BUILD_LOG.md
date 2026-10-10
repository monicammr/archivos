# Build log

Complete compilation of this folder from scratch (Lean 4.23.0, Mathlib v4.23.0; 4 cores, 15 GB RAM;
stack `ulimit -s unlimited`, `--tstack=4000000` for the models). Generated 2026-10-10.

* Modules compiled: **71 of 71** without errors (31 theory modules; 22 models, Chen and Froehlich split into parts), plus `All.lean` and `AllModels.lean`.
* Warnings reported by Lean: 5 (linter style messages only; no `sorry`).
* `CheckAxioms.lean` (all 289 theorems and lemmas of the theory):
  * 288 × `[propext, Classical.choice, Quot.sound]`
  * 1 × `[propext, Quot.sound]`
* `CheckModelAxioms.lean` (final theorem of each of the 22 models):
  * 22 × `[propext, Classical.choice, Quot.sound]`

No theorem depends on any axiom beyond Lean's standard ones (`propext`, `Classical.choice`, `Quot.sound`).

## Compilation time per module

| Module | Time (s) |
|---|---|
| `Models.Chen_MSB2009.Part1` | 359.5 |
| `Models.Chen_MSB2009.Part2` | 347.4 |
| `Models.Chen_MSB2009.Part0` | 339.8 |
| `Models.SalazarCavazos_MBoC2020` | 317.6 |
| `Models.Lang_PLOSComputBiol2024` | 263.7 |
| `Models.Froehlich_CellSystems2018.Part3` | 238.4 |
| `Models.Froehlich_CellSystems2018.Part0` | 232.7 |
| `Models.Froehlich_CellSystems2018.Part4` | 186.9 |
| `Models.Froehlich_CellSystems2018.Part6` | 171.9 |
| `Models.Froehlich_CellSystems2018.Part2` | 170.2 |
| `Models.Froehlich_CellSystems2018.Part5` | 156.9 |
| `Models.Froehlich_CellSystems2018.Part7` | 156.4 |
| `Models.Froehlich_CellSystems2018.Part1` | 156.1 |
| `Models.Froehlich_CellSystems2018.Part8` | 146.5 |
| `IdentifiabilityConditioning` | 143.1 |
| `SensitivityLipschitz` | 142.7 |
| `GlobalLipschitzODE` | 141.0 |
| `FirstOrderErrorBound` | 139.7 |
| `Models.Froehlich_CellSystems2018.Part9` | 130.3 |
| `Models.Froehlich_CellSystems2018.Base` | 127.2 |
| `Models.Froehlich_CellSystems2018.Part10` | 126.2 |
| `ParamDiffODE` | 26.0 |
| `RiccatiNetwork` | 24.2 |
| `Models.Chen_MSB2009` | 22.7 |
| `StrictNetwork` | 22.4 |
| `LocalExistence` | 22.2 |
| `StrictExistence` | 20.1 |
| `KineticCheck` | 16.2 |
| `Models.Fiedler_BMCSystBiol2016` | 15.0 |
| `Models.Raimundez_PCB2020` | 14.8 |
| `SpectralConditioning` | 14.6 |
| `KineticNetwork` | 13.7 |
| `ExactLinearCertificate` | 12.1 |
| `CosineCertificate` | 12.0 |
| `Models.Bachmann_MSB2011` | 11.6 |
| `Models.Froehlich_CellSystems2018.Part11` | 11.1 |
| `PositivityInvariance` | 11.0 |
| `Models.Froehlich_CellSystems2018` | 10.6 |
| `IntervalInit` | 9.9 |
| `KineticRegularity` | 9.7 |
| `GlobalExistence` | 9.7 |
| `Models.Giordano_Nature2020` | 8.3 |
| `Models.Blasi_CellSystems2016` | 8.2 |
| `Models.Boehm_JProteomeRes2014` | 7.2 |
| `Models.Zheng_PNAS2012` | 7.2 |
| `TrajectoryErrorBound` | 6.8 |
| `ScaledError` | 6.7 |
| `CertifiedFiniteODE` | 6.5 |
| `Models.Brannmark_JBC2010` | 6.1 |
| `Models.Chen_MSB2009.Part3` | 6.1 |
| `GreedySelection` | 6.0 |
| `Models.Crauste_CellSystems2017` | 5.9 |
| `CertifiedODEReduction` | 5.7 |
| `NumericalRobustness` | 5.5 |
| `EventSystems` | 5.5 |
| `Models.Elowitz_Nature2000` | 5.5 |
| `Models.Weber_BMC2015` | 5.5 |
| `Models.Rahman_MBS2016` | 5.4 |
| `Models.Borghans_BiophysChem1997` | 5.2 |
| `Models.Raia_CancerResearch2011` | 5.2 |
| `NominalCertificate` | 4.9 |
| `Models.Chen_MSB2009.Base` | 4.9 |
| `Models.Armistead_CellDeathDis2024` | 4.9 |
| `Models.Okuonghae_ChaosSolitonsFractals2020` | 4.9 |
| `Models.Zhao_QuantBiol2020` | 4.9 |
| `Models.Sneyd_PNAS2002` | 4.8 |
| `OutputComposition` | 4.6 |
| `LinearizedFit` | 4.4 |
| `PatternMechanisms` | 2.8 |
| `RefitMonotone` | 2.0 |
| `Poda` | 1.5 |
