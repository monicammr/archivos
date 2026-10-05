import KineticCheck

/-! Modelo `Crauste_CellSystems2017` traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (5): Naive, EarlyEffector, LateEffector, Memory, Pathogen

Parámetros estimados θ (12): delta_EL, delta_LM, delta_NE, mu_EE, mu_LE, mu_LL, mu_N, mu_P, mu_PE, mu_PL, rho_E, rho_P
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck

namespace Models.Crauste_CellSystems2017

def F : Fin 5 → KExpr 5 12 := ![
  (.sub (.sub (.qconst (0 : ℚ)) (.mul (.var 0) (.par 6))) (.mul (.mul (.var 0) (.var 4)) (.par 2))),
  (.sub (.sub (.add (.mul (.mul (.var 0) (.var 4)) (.par 2)) (.mul (.mul (.var 1) (.var 4)) (.par 10))) (.mul (.npow (.var 1) 2) (.par 3))) (.mul (.var 1) (.par 0))),
  (.sub (.sub (.sub (.mul (.var 1) (.par 0)) (.mul (.npow (.var 2) 2) (.par 5))) (.mul (.mul (.var 1) (.var 2)) (.par 4))) (.mul (.var 2) (.par 1))),
  (.mul (.var 2) (.par 1)),
  (.sub (.sub (.sub (.mul (.npow (.var 4) 2) (.par 11)) (.mul (.mul (.var 1) (.var 4)) (.par 8))) (.mul (.mul (.var 2) (.var 4)) (.par 9))) (.mul (.var 4) (.par 7)))
]

theorem check : checkModel F = true := by decide +kernel

/-- Diferenciabilidad de la trayectoria (y positividad) para este modelo. -/
def diff := @checked_model_hasFDerivAt _ _ F check

end Models.Crauste_CellSystems2017

#print axioms Models.Crauste_CellSystems2017.diff
