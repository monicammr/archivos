import Lake
open Lake DSL

package «certifiedReduction» where

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "v4.23.0"

/-- Teoría: los 32 módulos y `All`, que los importa todos. -/
@[default_target]
lean_lib «Theory» where
  roots := #[`All, `CertifiedFiniteODE, `CertifiedODEReduction, `CosineCertificate, `EventSystems, `ExactLinearCertificate, `FirstOrderErrorBound, `GlobalExistence, `GlobalLipschitzODE, `GreedySelection, `IdentifiabilityConditioning, `IntervalInit, `KineticCheck, `KineticNetwork, `KineticRegularity, `LinearizedFit, `LocalExistence, `NominalCertificate, `NumericalRobustness, `OutputComposition, `ParamDiffODE, `PatternMechanisms, `Poda, `PositivityInvariance, `RefitMonotone, `RiccatiNetwork, `ScaledError, `SensitivityLipschitz, `SpectralConditioning, `StrictExistence, `StrictNetwork, `TrajectoryErrorBound, `ProfileIdentifiability]

/-- Los 22 modelos del benchmark traducidos de SBML (Chen y Froehlich, en partes). -/
@[default_target]
lean_lib «Models» where
  globs := #[.submodules `Models]
  -- los modelos grandes necesitan una pila grande (además de `ulimit -s unlimited`)
  moreLeanArgs := #["--tstack=4000000"]
