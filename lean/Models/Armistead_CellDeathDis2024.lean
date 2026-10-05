import KineticCheck

/-! Modelo `Armistead_CellDeathDis2024` traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (4): Cer, Sphingo, S1P, Sphinga

Parámetros estimados θ (10): k00, k0, k_d, k1, k2, k3, k4, k5, alpha_hai1a, alpha_cer
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck

namespace Models.Armistead_CellDeathDis2024

def F : Fin 4 → KExpr 4 10 := ![
  (.sub (.add (.sub (.mul (.par 1) (.var 3)) (.mul (.par 3) (.var 0))) (.mul (.par 4) (.var 1))) (.mul (.par 2) (.var 0))),
  (.add (.add (.sub (.sub (.mul (.par 3) (.var 0)) (.mul (.par 4) (.var 1))) (.mul (.mul (.par 5) (.qconst (1 : ℚ))) (.var 1))) (.mul (.mul (.par 5) (.mul (.qconst (1 : ℚ)) (.par 8))) (.var 1))) (.mul (.par 6) (.var 2))),
  (.sub (.sub (.sub (.mul (.mul (.par 5) (.qconst (1 : ℚ))) (.var 1)) (.mul (.mul (.par 5) (.mul (.qconst (1 : ℚ)) (.par 8))) (.var 1))) (.mul (.par 6) (.var 2))) (.mul (.par 7) (.var 2))),
  (.sub (.add (.mul (.par 0) (.qconst (1 : ℚ))) (.mul (.par 0) (.mul (.qconst (1 : ℚ)) (.par 9)))) (.mul (.par 1) (.var 3)))
]

/-- La comprobación sintáctica FALLA para este modelo (ver el informe JSON). -/
theorem check_falla : checkModel F = false := by decide +kernel

end Models.Armistead_CellDeathDis2024
