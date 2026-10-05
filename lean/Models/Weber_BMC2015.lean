import KineticCheck

/-! Modelo `Weber_BMC2015` traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (7): PKD, PKDDAGa, PI4K3B, PI4K3Ba, CERTERa, CERT, CERTTGNa

Parámetros estimados θ (26): a11, a12, a21, a22, a31, a32, a33, m11, m22, m31, m33, p11, p12, p13, p21, p22, p31, p32, p33, pu3, pu4, pu5, pu6, s12, s21, s31
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck

namespace Models.Weber_BMC2015

def F : Fin 7 → KExpr 7 26 := ![
  (.sub (.add (.add (.sub (.sub (.qconst (0 : ℚ)) (.mul (.qconst (1 : ℚ)) (.div (.mul (.mul (.mul (.mul (.var 4) (.var 3)) (.var 0)) (.par 11)) (.par 16)) (.mul (.add (.var 3) (.par 9)) (.add (.par 7) (.div (.mul (.mul (.var 4) (.var 3)) (.par 16)) (.add (.var 3) (.par 9)))))))) (.mul (.mul (.mul (.qconst (1 : ℚ)) (.var 0)) (.par 12)) (.qconst (1 : ℚ)))) (.mul (.mul (.mul (.qconst (1 : ℚ)) (.var 1)) (.par 13)) (.qconst (1 : ℚ)))) (.mul (.qconst (1 : ℚ)) (.par 23))) (.mul (.mul (.qconst (1 : ℚ)) (.var 0)) (.par 0))),
  (.sub (.sub (.add (.mul (.qconst (1 : ℚ)) (.div (.mul (.mul (.mul (.mul (.var 4) (.var 3)) (.var 0)) (.par 11)) (.par 16)) (.mul (.add (.var 3) (.par 9)) (.add (.par 7) (.div (.mul (.mul (.var 4) (.var 3)) (.par 16)) (.add (.var 3) (.par 9))))))) (.mul (.mul (.mul (.qconst (1 : ℚ)) (.var 0)) (.par 12)) (.qconst (1 : ℚ)))) (.mul (.mul (.mul (.qconst (1 : ℚ)) (.var 1)) (.par 13)) (.qconst (1 : ℚ)))) (.mul (.mul (.qconst (1 : ℚ)) (.var 1)) (.par 1))),
  (.sub (.add (.sub (.mul (.mul (.qconst (1 : ℚ)) (.var 3)) (.par 14)) (.mul (.qconst (1 : ℚ)) (.div (.mul (.mul (.var 2) (.var 1)) (.par 15)) (.add (.var 1) (.par 8))))) (.mul (.qconst (1 : ℚ)) (.par 24))) (.mul (.mul (.qconst (1 : ℚ)) (.var 2)) (.par 2))),
  (.sub (.add (.sub (.qconst (0 : ℚ)) (.mul (.mul (.qconst (1 : ℚ)) (.var 3)) (.par 14))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.mul (.var 2) (.var 1)) (.par 15)) (.add (.var 1) (.par 8))))) (.mul (.mul (.qconst (1 : ℚ)) (.var 3)) (.par 3))),
  (.sub (.add (.add (.sub (.qconst (0 : ℚ)) (.mul (.qconst (1 : ℚ)) (.div (.mul (.mul (.var 4) (.var 3)) (.par 16)) (.add (.var 3) (.par 9))))) (.mul (.mul (.qconst (1 : ℚ)) (.var 5)) (.par 17))) (.mul (.qconst (1 : ℚ)) (.par 25))) (.mul (.mul (.qconst (1 : ℚ)) (.var 4)) (.par 4))),
  (.sub (.add (.sub (.qconst (0 : ℚ)) (.mul (.mul (.qconst (1 : ℚ)) (.var 5)) (.par 17))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.mul (.var 6) (.var 1)) (.par 18)) (.add (.var 1) (.par 10))))) (.mul (.mul (.qconst (1 : ℚ)) (.var 5)) (.par 5))),
  (.sub (.sub (.mul (.qconst (1 : ℚ)) (.div (.mul (.mul (.var 4) (.var 3)) (.par 16)) (.add (.var 3) (.par 9)))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.mul (.var 6) (.var 1)) (.par 18)) (.add (.var 1) (.par 10))))) (.mul (.mul (.qconst (1 : ℚ)) (.var 6)) (.par 6)))
]

theorem check : checkModel F = true := by decide +kernel

/-- Diferenciabilidad de la trayectoria (y positividad) para este modelo. -/
def diff := @checked_model_hasFDerivAt _ _ F check

end Models.Weber_BMC2015

#print axioms Models.Weber_BMC2015.diff
