import KineticCheck

/-! Modelo `Sneyd_PNAS2002` traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (6): IPR_O, IPR_R, IPR_I1, IPR_S, IPR_A, IPR_I2

Parámetros estimados θ (14): k1, k2, k3, k4, k_1, k_2, k_3, k_4, l2, l4, l6, l_2, l_4, l_6
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck

namespace Models.Sneyd_PNAS2002

def F : Fin 6 → KExpr 6 14 := ![
  (.add (.sub (.add (.add (.sub (.sub (.sub (.sub (.qconst (0 : ℚ)) (.mul (.div (.par 5) (.add (.qconst (1 : ℚ)) (.div (.qconst (10 : ℚ)) (.div (.div (.par 7) (.par 3)) (.div (.par 13) (.par 10)))))) (.var 0))) (.mul (.div (.mul (.par 12) (.qconst (10 : ℚ))) (.add (.qconst (1 : ℚ)) (.div (.qconst (10 : ℚ)) (.div (.div (.par 7) (.par 3)) (.div (.par 13) (.par 10)))))) (.var 0))) (.mul (.div (.mul (.mul (.par 3) (.div (.div (.par 7) (.par 3)) (.div (.par 13) (.par 10)))) (.qconst (10 : ℚ))) (.add (.div (.div (.par 7) (.par 3)) (.div (.par 13) (.par 10))) (.qconst (10 : ℚ)))) (.var 0))) (.mul (.div (.mul (.par 10) (.qconst (10 : ℚ))) (.add (.div (.div (.par 7) (.par 3)) (.div (.par 13) (.par 10))) (.qconst (10 : ℚ)))) (.var 0))) (.mul (.div (.mul (.div (.div (.par 4) (.par 0)) (.div (.par 11) (.par 8))) (.par 7)) (.add (.div (.div (.par 4) (.par 0)) (.div (.par 11) (.par 8))) (.qconst (10 : ℚ)))) (.var 4))) (.mul (.div (.mul (.div (.div (.par 4) (.par 0)) (.div (.par 11) (.par 8))) (.par 13)) (.add (.div (.div (.par 4) (.par 0)) (.div (.par 11) (.par 8))) (.qconst (10 : ℚ)))) (.var 4))) (.mul (.div (.mul (.par 2) (.div (.div (.par 7) (.par 3)) (.div (.par 13) (.par 10)))) (.add (.div (.div (.par 7) (.par 3)) (.div (.par 13) (.par 10))) (.qconst (10 : ℚ)))) (.var 0))) (.mul (.par 6) (.var 3))),
  (.add (.add (.sub (.sub (.add (.mul (.div (.par 5) (.add (.qconst (1 : ℚ)) (.div (.qconst (10 : ℚ)) (.div (.div (.par 7) (.par 3)) (.div (.par 13) (.par 10)))))) (.var 0)) (.mul (.div (.mul (.par 12) (.qconst (10 : ℚ))) (.add (.qconst (1 : ℚ)) (.div (.qconst (10 : ℚ)) (.div (.div (.par 7) (.par 3)) (.div (.par 13) (.par 10)))))) (.var 0))) (.mul (.div (.mul (.mul (.par 0) (.div (.div (.par 4) (.par 0)) (.div (.par 11) (.par 8)))) (.qconst (10 : ℚ))) (.add (.div (.div (.par 4) (.par 0)) (.div (.par 11) (.par 8))) (.mul (.qconst (10 : ℚ)) (.add (.qconst (1 : ℚ)) (.div (.div (.div (.par 4) (.par 0)) (.div (.par 11) (.par 8))) (.div (.div (.par 5) (.par 1)) (.div (.par 12) (.par 9)))))))) (.var 1))) (.mul (.div (.mul (.par 8) (.qconst (10 : ℚ))) (.add (.div (.div (.par 4) (.par 0)) (.div (.par 11) (.par 8))) (.mul (.qconst (10 : ℚ)) (.add (.qconst (1 : ℚ)) (.div (.div (.div (.par 4) (.par 0)) (.div (.par 11) (.par 8))) (.div (.div (.par 5) (.par 1)) (.div (.par 12) (.par 9)))))))) (.var 1))) (.mul (.par 4) (.var 2))) (.mul (.par 11) (.var 2))),
  (.sub (.sub (.add (.mul (.div (.mul (.mul (.par 0) (.div (.div (.par 4) (.par 0)) (.div (.par 11) (.par 8)))) (.qconst (10 : ℚ))) (.add (.div (.div (.par 4) (.par 0)) (.div (.par 11) (.par 8))) (.mul (.qconst (10 : ℚ)) (.add (.qconst (1 : ℚ)) (.div (.div (.div (.par 4) (.par 0)) (.div (.par 11) (.par 8))) (.div (.div (.par 5) (.par 1)) (.div (.par 12) (.par 9)))))))) (.var 1)) (.mul (.div (.mul (.par 8) (.qconst (10 : ℚ))) (.add (.div (.div (.par 4) (.par 0)) (.div (.par 11) (.par 8))) (.mul (.qconst (10 : ℚ)) (.add (.qconst (1 : ℚ)) (.div (.div (.div (.par 4) (.par 0)) (.div (.par 11) (.par 8))) (.div (.div (.par 5) (.par 1)) (.div (.par 12) (.par 9)))))))) (.var 1))) (.mul (.par 4) (.var 2))) (.mul (.par 11) (.var 2))),
  (.sub (.mul (.div (.mul (.par 2) (.div (.div (.par 7) (.par 3)) (.div (.par 13) (.par 10)))) (.add (.div (.div (.par 7) (.par 3)) (.div (.par 13) (.par 10))) (.qconst (10 : ℚ)))) (.var 0)) (.mul (.par 6) (.var 3))),
  (.add (.add (.sub (.sub (.sub (.sub (.add (.mul (.div (.mul (.mul (.par 3) (.div (.div (.par 7) (.par 3)) (.div (.par 13) (.par 10)))) (.qconst (10 : ℚ))) (.add (.div (.div (.par 7) (.par 3)) (.div (.par 13) (.par 10))) (.qconst (10 : ℚ)))) (.var 0)) (.mul (.div (.mul (.par 10) (.qconst (10 : ℚ))) (.add (.div (.div (.par 7) (.par 3)) (.div (.par 13) (.par 10))) (.qconst (10 : ℚ)))) (.var 0))) (.mul (.div (.mul (.div (.div (.par 4) (.par 0)) (.div (.par 11) (.par 8))) (.par 7)) (.add (.div (.div (.par 4) (.par 0)) (.div (.par 11) (.par 8))) (.qconst (10 : ℚ)))) (.var 4))) (.mul (.div (.mul (.div (.div (.par 4) (.par 0)) (.div (.par 11) (.par 8))) (.par 13)) (.add (.div (.div (.par 4) (.par 0)) (.div (.par 11) (.par 8))) (.qconst (10 : ℚ)))) (.var 4))) (.mul (.div (.mul (.mul (.par 0) (.div (.div (.par 4) (.par 0)) (.div (.par 11) (.par 8)))) (.qconst (10 : ℚ))) (.add (.div (.div (.par 4) (.par 0)) (.div (.par 11) (.par 8))) (.qconst (10 : ℚ)))) (.var 4))) (.mul (.div (.mul (.par 8) (.qconst (10 : ℚ))) (.add (.div (.div (.par 4) (.par 0)) (.div (.par 11) (.par 8))) (.qconst (10 : ℚ)))) (.var 4))) (.mul (.par 4) (.var 5))) (.mul (.par 11) (.var 5))),
  (.sub (.sub (.add (.mul (.div (.mul (.mul (.par 0) (.div (.div (.par 4) (.par 0)) (.div (.par 11) (.par 8)))) (.qconst (10 : ℚ))) (.add (.div (.div (.par 4) (.par 0)) (.div (.par 11) (.par 8))) (.qconst (10 : ℚ)))) (.var 4)) (.mul (.div (.mul (.par 8) (.qconst (10 : ℚ))) (.add (.div (.div (.par 4) (.par 0)) (.div (.par 11) (.par 8))) (.qconst (10 : ℚ)))) (.var 4))) (.mul (.par 4) (.var 5))) (.mul (.par 11) (.var 5)))
]

theorem check : checkModel F = true := by decide +kernel

/-- Diferenciabilidad de la trayectoria (y positividad) para este modelo. -/
def diff := @checked_model_hasFDerivAt _ _ F check

end Models.Sneyd_PNAS2002

#print axioms Models.Sneyd_PNAS2002.diff
