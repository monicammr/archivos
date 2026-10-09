import Lake
open Lake DSL

package «certifiedReduction» where

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "v4.23.0"

@[default_target]
lean_lib «CertifiedReduction» where
  roots := #[`FirstOrderErrorBound, `TrajectoryErrorBound, `GlobalLipschitzODE,
    `ParamDiffODE, `CertifiedODEReduction, `IdentifiabilityConditioning,
    `GreedySelection, `CosineCertificate, `NumericalRobustness, `PatternMechanisms,
    `SensitivityLipschitz, `CertifiedFiniteODE, `ExactLinearCertificate,
    `SpectralConditioning, `LocalExistence, `NominalCertificate,
    `KineticRegularity, `EventSystems, `PositivityInvariance, `KineticCheck, `GlobalExistence, `KineticNetwork, `StrictExistence, `StrictNetwork, `RiccatiNetwork, `IntervalInit, `ScaledError, `Poda]

/-- Modelos concretos traducidos de SBML por `certificados/sbml_to_lean.py`. -/
lean_lib «Models» where
  globs := #[.submodules `Models]
