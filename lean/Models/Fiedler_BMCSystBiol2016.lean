import KineticCheck

/-! Modelo `Fiedler_BMCSystBiol2016` traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (7): RAF, pRAF, MEK, pMEK, ERK, pERK, τ (tiempo)

Parámetros estimados θ (12): K_1, K_2, K_3, k10, k11, k2, k3, k4, k5, k6, tau1, tau2
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck

namespace Models.Fiedler_BMCSystBiol2016

def F : Fin 7 → KExpr 7 12 := ![
  (.add (.sub (.add (.sub (.qconst (0 : ℚ)) (.mul (.qconst (1 : ℚ)) (.div (.mul (.mul (.par 0) (.var 0)) (.par 3)) (.add (.par 0) (.var 5))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.mul (.par 0) (.var 0)) (.mul (.mul (.par 4) (.exp (.div (.sub (.qconst (0 : ℚ)) (.var 6)) (.par 11)))) (.exp (.div (.sub (.qconst (0 : ℚ)) (.var 6)) (.par 10))))) (.add (.par 0) (.var 5))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.mul (.par 0) (.var 0)) (.mul (.mul (.par 4) (.exp (.div (.sub (.qconst (0 : ℚ)) (.var 6)) (.par 11)))) (.qconst (1 : ℚ)))) (.add (.par 0) (.var 5))))) (.mul (.mul (.qconst (1 : ℚ)) (.par 5)) (.var 1))),
  (.sub (.add (.sub (.mul (.qconst (1 : ℚ)) (.div (.mul (.mul (.par 0) (.var 0)) (.par 3)) (.add (.par 0) (.var 5)))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.mul (.par 0) (.var 0)) (.mul (.mul (.par 4) (.exp (.div (.sub (.qconst (0 : ℚ)) (.var 6)) (.par 11)))) (.exp (.div (.sub (.qconst (0 : ℚ)) (.var 6)) (.par 10))))) (.add (.par 0) (.var 5))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.mul (.par 0) (.var 0)) (.mul (.mul (.par 4) (.exp (.div (.sub (.qconst (0 : ℚ)) (.var 6)) (.par 11)))) (.qconst (1 : ℚ)))) (.add (.par 0) (.var 5))))) (.mul (.mul (.qconst (1 : ℚ)) (.par 5)) (.var 1))),
  (.add (.sub (.qconst (0 : ℚ)) (.mul (.qconst (1 : ℚ)) (.div (.mul (.mul (.mul (.par 1) (.var 2)) (.par 6)) (.var 1)) (.par 1)))) (.mul (.mul (.qconst (1 : ℚ)) (.par 7)) (.var 3))),
  (.sub (.mul (.qconst (1 : ℚ)) (.div (.mul (.mul (.mul (.par 1) (.var 2)) (.par 6)) (.var 1)) (.par 1))) (.mul (.mul (.qconst (1 : ℚ)) (.par 7)) (.var 3))),
  (.add (.sub (.qconst (0 : ℚ)) (.mul (.qconst (1 : ℚ)) (.div (.mul (.mul (.mul (.var 4) (.par 2)) (.par 8)) (.var 3)) (.par 2)))) (.mul (.mul (.qconst (1 : ℚ)) (.par 9)) (.var 5))),
  (.sub (.mul (.qconst (1 : ℚ)) (.div (.mul (.mul (.mul (.var 4) (.par 2)) (.par 8)) (.var 3)) (.par 2))) (.mul (.mul (.qconst (1 : ℚ)) (.par 9)) (.var 5))),
  (.qconst (1 : ℚ))
]

/-- La comprobación sintáctica FALLA para este modelo (ver el informe JSON). -/
theorem check_falla : checkModel F = false := by decide +kernel

end Models.Fiedler_BMCSystBiol2016
