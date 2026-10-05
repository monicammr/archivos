import KineticCheck

/-! Modelo `Brannmark_JBC2010` traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (9): IR, IRins, IRp, IRiP, IRi, IRS, IRSiP, X, Xp

Parámetros estimados θ (15): k1a, k1aBasic, k1b, k1c, k1d, k1e, k1f, k1g, k1r, k21, k22, k3, k_IRSiP_DosR, km2, km3
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck

namespace Models.Brannmark_JBC2010

def F : Fin 9 → KExpr 9 15 := ![
  (.add (.add (.add (.sub (.sub (.qconst (0 : ℚ)) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.par 1)))) (.mul (.qconst (1 : ℚ)) (.mul (.mul (.var 0) (.mul (.qconst (3 / 10 : ℚ)) (.qconst (1 : ℚ)))) (.par 0)))) (.mul (.mul (.qconst (1 : ℚ)) (.var 1)) (.par 2))) (.mul (.mul (.qconst (1 : ℚ)) (.var 2)) (.par 7))) (.mul (.mul (.qconst (1 : ℚ)) (.var 4)) (.par 8))),
  (.sub (.sub (.add (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.par 1))) (.mul (.qconst (1 : ℚ)) (.mul (.mul (.var 0) (.mul (.qconst (3 / 10 : ℚ)) (.qconst (1 : ℚ)))) (.par 0)))) (.mul (.mul (.qconst (1 : ℚ)) (.var 1)) (.par 2))) (.mul (.mul (.qconst (1 : ℚ)) (.var 1)) (.par 3))),
  (.sub (.sub (.mul (.mul (.qconst (1 : ℚ)) (.var 1)) (.par 3)) (.mul (.mul (.qconst (1 : ℚ)) (.var 2)) (.par 4))) (.mul (.mul (.qconst (1 : ℚ)) (.var 2)) (.par 7))),
  (.sub (.sub (.mul (.mul (.qconst (1 : ℚ)) (.var 2)) (.par 4)) (.mul (.mul (.qconst (1 : ℚ)) (.var 3)) (.par 5))) (.mul (.mul (.qconst (1 : ℚ)) (.var 3)) (.div (.mul (.var 8) (.par 6)) (.add (.var 8) (.qconst (1 : ℚ)))))),
  (.sub (.add (.mul (.mul (.qconst (1 : ℚ)) (.var 3)) (.par 5)) (.mul (.mul (.qconst (1 : ℚ)) (.var 3)) (.div (.mul (.var 8) (.par 6)) (.add (.var 8) (.qconst (1 : ℚ)))))) (.mul (.mul (.qconst (1 : ℚ)) (.var 4)) (.par 8))),
  (.add (.sub (.sub (.qconst (0 : ℚ)) (.mul (.mul (.mul (.qconst (1 : ℚ)) (.var 5)) (.par 9)) (.var 2))) (.mul (.mul (.mul (.qconst (1 : ℚ)) (.var 5)) (.par 9)) (.mul (.var 3) (.par 10)))) (.mul (.mul (.qconst (1 : ℚ)) (.var 6)) (.par 13))),
  (.sub (.add (.mul (.mul (.mul (.qconst (1 : ℚ)) (.var 5)) (.par 9)) (.var 2)) (.mul (.mul (.mul (.qconst (1 : ℚ)) (.var 5)) (.par 9)) (.mul (.var 3) (.par 10)))) (.mul (.mul (.qconst (1 : ℚ)) (.var 6)) (.par 13))),
  (.add (.sub (.qconst (0 : ℚ)) (.mul (.mul (.mul (.qconst (1 : ℚ)) (.var 6)) (.var 7)) (.par 11))) (.mul (.mul (.qconst (1 : ℚ)) (.var 8)) (.par 14))),
  (.sub (.mul (.mul (.mul (.qconst (1 : ℚ)) (.var 6)) (.var 7)) (.par 11)) (.mul (.mul (.qconst (1 : ℚ)) (.var 8)) (.par 14)))
]

theorem check : checkModel F = true := by decide +kernel

/-- Diferenciabilidad de la trayectoria (y positividad) para este modelo. -/
def diff := @checked_model_hasFDerivAt _ _ F check

end Models.Brannmark_JBC2010

#print axioms Models.Brannmark_JBC2010.diff
