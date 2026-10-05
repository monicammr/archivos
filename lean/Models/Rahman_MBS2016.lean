import KineticCheck

/-! Modelo `Rahman_MBS2016` traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (7): susceptible, infected_normal, infected_moderate, infected_weak, treated_normal, treated_moderate, treated_weak

Parámetros estimados θ (9): infected_normal_transmission_rate_relative, infected_moderate_transmission_rate, infected_weak_transmission_rate_relative, infected_weak_treatment_rate, infected_normal_worsen_rate, infected_moderate_worsen_rate, treated_moderate_improve_rate, treated_weak_improve_rate, behavioural_change_rate
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck

namespace Models.Rahman_MBS2016

def F : Fin 7 → KExpr 7 9 := ![
  (.sub (.sub (.sub (.sub (.sub (.sub (.sub (.qconst (1032672 : ℚ)) (.mul (.mul (.div (.mul (.mul (.par 0) (.par 1)) (.var 1)) (.add (.add (.add (.add (.add (.add (.var 0) (.var 1)) (.var 2)) (.var 3)) (.var 4)) (.var 5)) (.var 6))) (.exp (.mul (.mul (.qconst (-1 : ℚ)) (.par 8)) (.add (.add (.add (.add (.add (.var 1) (.var 2)) (.var 3)) (.var 4)) (.var 5)) (.var 6))))) (.var 0))) (.mul (.mul (.div (.mul (.par 1) (.var 2)) (.add (.add (.add (.add (.add (.add (.var 0) (.var 1)) (.var 2)) (.var 3)) (.var 4)) (.var 5)) (.var 6))) (.exp (.mul (.mul (.qconst (-1 : ℚ)) (.par 8)) (.add (.add (.add (.add (.add (.var 1) (.var 2)) (.var 3)) (.var 4)) (.var 5)) (.var 6))))) (.var 0))) (.mul (.mul (.div (.mul (.mul (.par 2) (.par 1)) (.var 3)) (.add (.add (.add (.add (.add (.add (.var 0) (.var 1)) (.var 2)) (.var 3)) (.var 4)) (.var 5)) (.var 6))) (.exp (.mul (.mul (.qconst (-1 : ℚ)) (.par 8)) (.add (.add (.add (.add (.add (.var 1) (.var 2)) (.var 3)) (.var 4)) (.var 5)) (.var 6))))) (.var 0))) (.mul (.mul (.div (.mul (.mul (.qconst (1 / 25 : ℚ)) (.par 1)) (.var 4)) (.add (.add (.add (.add (.add (.add (.var 0) (.var 1)) (.var 2)) (.var 3)) (.var 4)) (.var 5)) (.var 6))) (.exp (.mul (.mul (.qconst (-1 : ℚ)) (.par 8)) (.add (.add (.add (.add (.add (.var 1) (.var 2)) (.var 3)) (.var 4)) (.var 5)) (.var 6))))) (.var 0))) (.mul (.mul (.div (.mul (.mul (.qconst (1 / 25 : ℚ)) (.par 1)) (.var 5)) (.add (.add (.add (.add (.add (.add (.var 0) (.var 1)) (.var 2)) (.var 3)) (.var 4)) (.var 5)) (.var 6))) (.exp (.mul (.mul (.qconst (-1 : ℚ)) (.par 8)) (.add (.add (.add (.add (.add (.var 1) (.var 2)) (.var 3)) (.var 4)) (.var 5)) (.var 6))))) (.var 0))) (.mul (.mul (.div (.mul (.mul (.qconst (1 / 25 : ℚ)) (.par 1)) (.var 6)) (.add (.add (.add (.add (.add (.add (.var 0) (.var 1)) (.var 2)) (.var 3)) (.var 4)) (.var 5)) (.var 6))) (.exp (.mul (.mul (.qconst (-1 : ℚ)) (.par 8)) (.add (.add (.add (.add (.add (.var 1) (.var 2)) (.var 3)) (.var 4)) (.var 5)) (.var 6))))) (.var 0))) (.mul (.qconst (18 / 625 : ℚ)) (.var 0))),
  (.sub (.sub (.add (.add (.add (.add (.add (.mul (.mul (.div (.mul (.mul (.par 0) (.par 1)) (.var 1)) (.add (.add (.add (.add (.add (.add (.var 0) (.var 1)) (.var 2)) (.var 3)) (.var 4)) (.var 5)) (.var 6))) (.exp (.mul (.mul (.qconst (-1 : ℚ)) (.par 8)) (.add (.add (.add (.add (.add (.var 1) (.var 2)) (.var 3)) (.var 4)) (.var 5)) (.var 6))))) (.var 0)) (.mul (.mul (.div (.mul (.par 1) (.var 2)) (.add (.add (.add (.add (.add (.add (.var 0) (.var 1)) (.var 2)) (.var 3)) (.var 4)) (.var 5)) (.var 6))) (.exp (.mul (.mul (.qconst (-1 : ℚ)) (.par 8)) (.add (.add (.add (.add (.add (.var 1) (.var 2)) (.var 3)) (.var 4)) (.var 5)) (.var 6))))) (.var 0))) (.mul (.mul (.div (.mul (.mul (.par 2) (.par 1)) (.var 3)) (.add (.add (.add (.add (.add (.add (.var 0) (.var 1)) (.var 2)) (.var 3)) (.var 4)) (.var 5)) (.var 6))) (.exp (.mul (.mul (.qconst (-1 : ℚ)) (.par 8)) (.add (.add (.add (.add (.add (.var 1) (.var 2)) (.var 3)) (.var 4)) (.var 5)) (.var 6))))) (.var 0))) (.mul (.mul (.div (.mul (.mul (.qconst (1 / 25 : ℚ)) (.par 1)) (.var 4)) (.add (.add (.add (.add (.add (.add (.var 0) (.var 1)) (.var 2)) (.var 3)) (.var 4)) (.var 5)) (.var 6))) (.exp (.mul (.mul (.qconst (-1 : ℚ)) (.par 8)) (.add (.add (.add (.add (.add (.var 1) (.var 2)) (.var 3)) (.var 4)) (.var 5)) (.var 6))))) (.var 0))) (.mul (.mul (.div (.mul (.mul (.qconst (1 / 25 : ℚ)) (.par 1)) (.var 5)) (.add (.add (.add (.add (.add (.add (.var 0) (.var 1)) (.var 2)) (.var 3)) (.var 4)) (.var 5)) (.var 6))) (.exp (.mul (.mul (.qconst (-1 : ℚ)) (.par 8)) (.add (.add (.add (.add (.add (.var 1) (.var 2)) (.var 3)) (.var 4)) (.var 5)) (.var 6))))) (.var 0))) (.mul (.mul (.div (.mul (.mul (.qconst (1 / 25 : ℚ)) (.par 1)) (.var 6)) (.add (.add (.add (.add (.add (.add (.var 0) (.var 1)) (.var 2)) (.var 3)) (.var 4)) (.var 5)) (.var 6))) (.exp (.mul (.mul (.qconst (-1 : ℚ)) (.par 8)) (.add (.add (.add (.add (.add (.var 1) (.var 2)) (.var 3)) (.var 4)) (.var 5)) (.var 6))))) (.var 0))) (.mul (.par 4) (.var 1))) (.mul (.qconst (111 / 1250 : ℚ)) (.var 1))),
  (.sub (.sub (.mul (.par 4) (.var 1)) (.mul (.par 5) (.var 2))) (.mul (.qconst (171 / 1250 : ℚ)) (.var 2))),
  (.sub (.sub (.mul (.par 5) (.var 2)) (.mul (.par 3) (.var 3))) (.mul (.qconst (777 / 2500 : ℚ)) (.var 3))),
  (.sub (.mul (.par 6) (.var 5)) (.mul (.qconst (51 / 1250 : ℚ)) (.var 4))),
  (.sub (.sub (.mul (.par 7) (.var 6)) (.mul (.par 6) (.var 5))) (.mul (.qconst (33 / 625 : ℚ)) (.var 5))),
  (.sub (.add (.sub (.qconst (0 : ℚ)) (.mul (.par 7) (.var 6))) (.mul (.par 3) (.var 3))) (.mul (.qconst (219 / 1250 : ℚ)) (.var 6)))
]

/-- La comprobación sintáctica FALLA para este modelo (ver el informe JSON). -/
theorem check_falla : checkModel F = false := by decide +kernel

end Models.Rahman_MBS2016
