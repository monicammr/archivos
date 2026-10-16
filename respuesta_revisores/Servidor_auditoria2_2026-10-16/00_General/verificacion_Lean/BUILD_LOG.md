# Build log

Clean build and independent check of this folder, 16 October 2026 (second audit), on a fresh clone
of commit `b64f2c7` (Lean 4.23.0, Mathlib v4.23.0; Linux x86-64, 88 cores, 251 GB RAM).

* `./verify.sh` from scratch: **2,658 build jobs completed without errors** (32 theory modules, the
  non-vacuity witnesses `NonVacuity.lean`, and the 28 benchmark models, Chen and Froehlich split into
  parts; 46 model modules), in 18 min 20 s of wall-clock time.
* No `sorry` and no `axiom` declaration in the sources.
* `CheckAxioms.lean`: **309 of 309** theorems and lemmas reported; 308 depend on
  `[propext, Classical.choice, Quot.sound]` and 1 on `[propext, Quot.sound]`; none on any other axiom.
* `CheckModelAxioms.lean`: **28 of 28** final model theorems reported, all on the standard axioms.
  (In earlier versions this check failed silently because `AllModels` was not a build target;
  `verify.sh` now stops with an error unless every declaration is reported with standard axioms only.)
* Independent re-check with **lean4checker** (v4.23.0), which replays every declaration of a module
  through the kernel: all 32 theory modules, `NonVacuity`, and all 46 model modules accepted.
* Negative control: a test file with `theorem neg_control : (1:Nat) = 2 := by sorry` is reported as
  depending on `sorryAx`, so the axiom check detects an unproved statement.
* `NonVacuity.lean` gives, for the central theorems (threshold, backward elimination, κ/VIF filters,
  monotone re-estimation, least-squares stability and the three identifiability theorems), concrete
  instances in which every hypothesis is proved, including a nonlinear residual for the
  identifiability theorems, and negative examples in which the defined properties fail.
  `DEFINITIONS_AUDIT.md` compares every definition with the paper and the code.

## Previous build (10 October 2026; 31 theory modules, 289 theorems, 22 models)

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

## Models added on 2026-10-11

Six further benchmark models were translated with `../lean_translation/sbml_to_lean.py` (horizon = last
measurement time of each PEtab problem) and compiled individually with the same toolchain
(`lean --tstack=4000000`, stack unlimited). Each final theorem reports only the standard axioms:

| Model | Final theorem | Time (s) | `#print axioms` |
|---|---|---|---|
| `Models.Bertozzi_PNAS2020` | `network_final` | 188 | `[propext, Classical.choice, Quot.sound]` |
| `Models.Bruno_JExpBot2016` | `network_final` | 4 | `[propext, Classical.choice, Quot.sound]` |
| `Models.Fujita_SciSignal2010` | `network_final_init` | 5 | `[propext, Classical.choice, Quot.sound]` |
| `Models.Isensee_JCB2018` | `network_final` | 8 | `[propext, Classical.choice, Quot.sound]` |
| `Models.Laske_PLOSComputBiol2019` | `network_final` | 10 | `[propext, Classical.choice, Quot.sound]` |
| `Models.Lucarelli_CellSystems2018` | `network_final_init` | 26 | `[propext, Classical.choice, Quot.sound]` |

(The 188 s of the first file include loading the compiled theory.) `AllModels.lean` and
`CheckModelAxioms.lean` now cover the 28 models.
