import KineticCheck

/-! Modelo `Zhao_QuantBiol2020` traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (4): Susceptible, Unquarantined_Infected, Quarantined_Infected, Confirmed_Infected

Parámetros estimados θ (21): R_Stage_I_Wuhan, gamma_1_Stage_I_Wuhan, gamma_2_Stage_I_Wuhan, R_Stage_II_Wuhan, gamma_1_Stage_II_Wuhan, gamma_2_Stage_II_Wuhan, R_Stage_III_Wuhan, gamma_1_Stage_III_Wuhan, gamma_2_Stage_III_Wuhan, R_Stage_I_Hubei, gamma_1_Stage_I_Hubei, gamma_2_Stage_I_Hubei, R_Stage_II_Hubei, gamma_1_Stage_II_Hubei, gamma_2_Stage_II_Hubei, R_Stage_I_China, gamma_1_Stage_I_China, gamma_2_Stage_I_China, R_Stage_II_China, gamma_1_Stage_II_China, gamma_2_Stage_II_China
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck

namespace Models.Zhao_QuantBiol2020

def F : Fin 4 → KExpr 4 21 := ![
  (.sub (.qconst (0 : ℚ)) (.mul (.qconst (1 : ℚ)) (.div (.mul (.mul (.mul (.mul (.qconst (1 : ℚ)) (.mul (.qconst (1 : ℚ)) (.par 0))) (.mul (.qconst (1 : ℚ)) (.mul (.qconst (1 : ℚ)) (.par 1)))) (.var 0)) (.var 1)) (.mul (.qconst (1 : ℚ)) (.qconst (9010000 : ℚ)))))),
  (.sub (.mul (.qconst (1 : ℚ)) (.div (.mul (.mul (.mul (.mul (.qconst (1 : ℚ)) (.mul (.qconst (1 : ℚ)) (.par 0))) (.mul (.qconst (1 : ℚ)) (.mul (.qconst (1 : ℚ)) (.par 1)))) (.var 0)) (.var 1)) (.mul (.qconst (1 : ℚ)) (.qconst (9010000 : ℚ))))) (.mul (.mul (.qconst (1 : ℚ)) (.mul (.qconst (1 : ℚ)) (.mul (.qconst (1 : ℚ)) (.par 1)))) (.var 1))),
  (.sub (.mul (.mul (.qconst (1 : ℚ)) (.mul (.qconst (1 : ℚ)) (.mul (.qconst (1 : ℚ)) (.par 1)))) (.var 1)) (.mul (.mul (.qconst (1 : ℚ)) (.mul (.qconst (1 : ℚ)) (.mul (.qconst (1 : ℚ)) (.par 2)))) (.var 2))),
  (.mul (.mul (.qconst (1 : ℚ)) (.mul (.qconst (1 : ℚ)) (.mul (.qconst (1 : ℚ)) (.par 2)))) (.var 2))
]

theorem check : checkModel F = true := by decide +kernel

/-- Diferenciabilidad de la trayectoria (y positividad) para este modelo. -/
def diff := @checked_model_hasFDerivAt _ _ F check

end Models.Zhao_QuantBiol2020

#print axioms Models.Zhao_QuantBiol2020.diff
