import Lake
open Lake DSL

package «certifiedReduction» where

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "v4.23.0"

@[default_target]
lean_lib «CertifiedReduction» where
  roots := #[`FirstOrderErrorBound, `TrajectoryErrorBound, `GlobalLipschitzODE,
    `ParamDiffODE, `CertifiedODEReduction, `IdentifiabilityConditioning,
    `GreedySelection]
