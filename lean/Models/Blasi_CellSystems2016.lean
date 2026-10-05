import KineticCheck

/-! Modelo `Blasi_CellSystems2016` traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (16): x_0ac, x_k8, x_k5, x_k12, x_k16, x_k5k8, x_k5k12, x_k5k16, x_k8k12, x_k8k16, x_k12k16, x_k5k8k12, x_k5k8k16, x_k5k12k16, x_k8k12k16, x_4ac

Parámetros estimados θ (8): a_basal, a_k8, a_k5_k5k12, a_k12_k5k12, a_k16_k12k16, a_k5k12_k5k8k12, a_k12k16_k8k12k16, a_k8k12k16_4ac
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck

namespace Models.Blasi_CellSystems2016

def F : Fin 16 → KExpr 16 8 := ![
  (.add (.sub (.add (.sub (.add (.sub (.add (.sub (.qconst (0 : ℚ)) (.mul (.par 0) (.var 0))) (.mul (.qconst (1 : ℚ)) (.var 2))) (.mul (.par 1) (.var 0))) (.mul (.qconst (1 : ℚ)) (.var 1))) (.mul (.par 0) (.var 0))) (.mul (.qconst (1 : ℚ)) (.var 3))) (.mul (.par 0) (.var 0))) (.mul (.qconst (1 : ℚ)) (.var 4))),
  (.add (.sub (.add (.sub (.add (.sub (.sub (.mul (.par 1) (.var 0)) (.mul (.qconst (1 : ℚ)) (.var 1))) (.mul (.par 0) (.var 1))) (.mul (.qconst (1 : ℚ)) (.var 5))) (.mul (.par 0) (.var 1))) (.mul (.qconst (1 : ℚ)) (.var 8))) (.mul (.par 0) (.var 1))) (.mul (.qconst (1 : ℚ)) (.var 9))),
  (.add (.sub (.add (.sub (.add (.sub (.sub (.mul (.par 0) (.var 0)) (.mul (.qconst (1 : ℚ)) (.var 2))) (.mul (.par 0) (.var 2))) (.mul (.qconst (1 : ℚ)) (.var 5))) (.mul (.par 2) (.var 2))) (.mul (.qconst (1 : ℚ)) (.var 6))) (.mul (.par 0) (.var 2))) (.mul (.qconst (1 : ℚ)) (.var 7))),
  (.add (.sub (.add (.sub (.add (.sub (.sub (.mul (.par 0) (.var 0)) (.mul (.qconst (1 : ℚ)) (.var 3))) (.mul (.par 3) (.var 3))) (.mul (.qconst (1 : ℚ)) (.var 6))) (.mul (.par 0) (.var 3))) (.mul (.qconst (1 : ℚ)) (.var 8))) (.mul (.par 0) (.var 3))) (.mul (.qconst (1 : ℚ)) (.var 10))),
  (.add (.sub (.add (.sub (.add (.sub (.sub (.mul (.par 0) (.var 0)) (.mul (.qconst (1 : ℚ)) (.var 4))) (.mul (.par 0) (.var 4))) (.mul (.qconst (1 : ℚ)) (.var 7))) (.mul (.par 0) (.var 4))) (.mul (.qconst (1 : ℚ)) (.var 9))) (.mul (.par 4) (.var 4))) (.mul (.qconst (1 : ℚ)) (.var 10))),
  (.add (.sub (.add (.sub (.sub (.add (.sub (.mul (.par 0) (.var 2)) (.mul (.qconst (1 : ℚ)) (.var 5))) (.mul (.par 0) (.var 1))) (.mul (.qconst (1 : ℚ)) (.var 5))) (.mul (.par 0) (.var 5))) (.mul (.qconst (1 : ℚ)) (.var 11))) (.mul (.par 0) (.var 5))) (.mul (.qconst (1 : ℚ)) (.var 12))),
  (.add (.sub (.add (.sub (.sub (.add (.sub (.mul (.par 2) (.var 2)) (.mul (.qconst (1 : ℚ)) (.var 6))) (.mul (.par 3) (.var 3))) (.mul (.qconst (1 : ℚ)) (.var 6))) (.mul (.par 5) (.var 6))) (.mul (.qconst (1 : ℚ)) (.var 11))) (.mul (.par 0) (.var 6))) (.mul (.qconst (1 : ℚ)) (.var 13))),
  (.add (.sub (.add (.sub (.sub (.add (.sub (.mul (.par 0) (.var 2)) (.mul (.qconst (1 : ℚ)) (.var 7))) (.mul (.par 0) (.var 4))) (.mul (.qconst (1 : ℚ)) (.var 7))) (.mul (.par 0) (.var 7))) (.mul (.qconst (1 : ℚ)) (.var 12))) (.mul (.par 0) (.var 7))) (.mul (.qconst (1 : ℚ)) (.var 13))),
  (.add (.sub (.add (.sub (.sub (.add (.sub (.mul (.par 0) (.var 1)) (.mul (.qconst (1 : ℚ)) (.var 8))) (.mul (.par 0) (.var 3))) (.mul (.qconst (1 : ℚ)) (.var 8))) (.mul (.par 0) (.var 8))) (.mul (.qconst (1 : ℚ)) (.var 11))) (.mul (.par 0) (.var 8))) (.mul (.qconst (1 : ℚ)) (.var 14))),
  (.add (.sub (.add (.sub (.sub (.add (.sub (.mul (.par 0) (.var 1)) (.mul (.qconst (1 : ℚ)) (.var 9))) (.mul (.par 0) (.var 4))) (.mul (.qconst (1 : ℚ)) (.var 9))) (.mul (.par 0) (.var 9))) (.mul (.qconst (1 : ℚ)) (.var 12))) (.mul (.par 0) (.var 9))) (.mul (.qconst (1 : ℚ)) (.var 14))),
  (.add (.sub (.add (.sub (.sub (.add (.sub (.mul (.par 0) (.var 3)) (.mul (.qconst (1 : ℚ)) (.var 10))) (.mul (.par 4) (.var 4))) (.mul (.qconst (1 : ℚ)) (.var 10))) (.mul (.par 0) (.var 10))) (.mul (.qconst (1 : ℚ)) (.var 13))) (.mul (.par 6) (.var 10))) (.mul (.qconst (1 : ℚ)) (.var 14))),
  (.add (.sub (.sub (.add (.sub (.add (.sub (.mul (.par 0) (.var 5)) (.mul (.qconst (1 : ℚ)) (.var 11))) (.mul (.par 5) (.var 6))) (.mul (.qconst (1 : ℚ)) (.var 11))) (.mul (.par 0) (.var 8))) (.mul (.qconst (1 : ℚ)) (.var 11))) (.mul (.par 0) (.var 11))) (.mul (.qconst (1 : ℚ)) (.var 15))),
  (.add (.sub (.sub (.add (.sub (.add (.sub (.mul (.par 0) (.var 5)) (.mul (.qconst (1 : ℚ)) (.var 12))) (.mul (.par 0) (.var 7))) (.mul (.qconst (1 : ℚ)) (.var 12))) (.mul (.par 0) (.var 9))) (.mul (.qconst (1 : ℚ)) (.var 12))) (.mul (.par 0) (.var 12))) (.mul (.qconst (1 : ℚ)) (.var 15))),
  (.add (.sub (.sub (.add (.sub (.add (.sub (.mul (.par 0) (.var 6)) (.mul (.qconst (1 : ℚ)) (.var 13))) (.mul (.par 0) (.var 7))) (.mul (.qconst (1 : ℚ)) (.var 13))) (.mul (.par 0) (.var 10))) (.mul (.qconst (1 : ℚ)) (.var 13))) (.mul (.par 0) (.var 13))) (.mul (.qconst (1 : ℚ)) (.var 15))),
  (.add (.sub (.sub (.add (.sub (.add (.sub (.mul (.par 0) (.var 8)) (.mul (.qconst (1 : ℚ)) (.var 14))) (.mul (.par 0) (.var 9))) (.mul (.qconst (1 : ℚ)) (.var 14))) (.mul (.par 6) (.var 10))) (.mul (.qconst (1 : ℚ)) (.var 14))) (.mul (.par 7) (.var 14))) (.mul (.qconst (1 : ℚ)) (.var 15))),
  (.sub (.add (.sub (.add (.sub (.add (.sub (.mul (.par 0) (.var 11)) (.mul (.qconst (1 : ℚ)) (.var 15))) (.mul (.par 0) (.var 12))) (.mul (.qconst (1 : ℚ)) (.var 15))) (.mul (.par 0) (.var 13))) (.mul (.qconst (1 : ℚ)) (.var 15))) (.mul (.par 7) (.var 14))) (.mul (.qconst (1 : ℚ)) (.var 15)))
]

theorem check : checkModel F = true := by decide +kernel

/-- Diferenciabilidad de la trayectoria (y positividad) para este modelo. -/
def diff := @checked_model_hasFDerivAt _ _ F check

end Models.Blasi_CellSystems2016

#print axioms Models.Blasi_CellSystems2016.diff
