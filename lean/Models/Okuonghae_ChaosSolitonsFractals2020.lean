import KineticCheck

/-! Modelo `Okuonghae_ChaosSolitonsFractals2020` traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (8): susceptible, exposed, asymptomatic, symptomatic, detected, recovered, deceased, detected_cumulative

Parámetros estimados θ (14): alpha, d_0, d_D, gamma_0, gamma_a, gamma_i, nu, psi, sigma, theta, asymptomatic_start, symptomatic_start, exposed_start, transmission_rate_effective
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck

namespace Models.Okuonghae_ChaosSolitonsFractals2020

def F : Fin 8 → KExpr 8 14 := ![
  (.sub (.sub (.qconst (0 : ℚ)) (.mul (.mul (.qconst (1 : ℚ)) (.div (.mul (.mul (.mul (.par 13) (.qconst (1 / 5 : ℚ))) (.qconst (1 : ℚ))) (.mul (.par 0) (.var 2))) (.sub (.add (.add (.add (.add (.add (.var 2) (.var 4)) (.var 1)) (.var 5)) (.var 0)) (.var 3)) (.var 4)))) (.var 0))) (.mul (.mul (.qconst (1 : ℚ)) (.div (.mul (.mul (.mul (.par 13) (.qconst (1 / 5 : ℚ))) (.qconst (1 : ℚ))) (.var 3)) (.sub (.add (.add (.add (.add (.add (.var 2) (.var 4)) (.var 1)) (.var 5)) (.var 0)) (.var 3)) (.var 4)))) (.var 0))),
  (.sub (.add (.sub (.add (.mul (.mul (.qconst (1 : ℚ)) (.div (.mul (.mul (.mul (.par 13) (.qconst (1 / 5 : ℚ))) (.qconst (1 : ℚ))) (.mul (.par 0) (.var 2))) (.sub (.add (.add (.add (.add (.add (.var 2) (.var 4)) (.var 1)) (.var 5)) (.var 0)) (.var 3)) (.var 4)))) (.var 0)) (.mul (.mul (.qconst (1 : ℚ)) (.div (.mul (.mul (.mul (.par 13) (.qconst (1 / 5 : ℚ))) (.qconst (1 : ℚ))) (.var 3)) (.sub (.add (.add (.add (.add (.add (.var 2) (.var 4)) (.var 1)) (.var 5)) (.var 0)) (.var 3)) (.var 4)))) (.var 0))) (.mul (.qconst (1 : ℚ)) (.mul (.mul (.par 8) (.qconst (1 : ℚ))) (.var 1)))) (.mul (.qconst (1 : ℚ)) (.mul (.mul (.par 8) (.par 6)) (.var 1)))) (.mul (.qconst (1 : ℚ)) (.mul (.mul (.par 8) (.par 6)) (.var 1)))),
  (.sub (.sub (.mul (.qconst (1 : ℚ)) (.mul (.mul (.par 8) (.par 6)) (.var 1))) (.mul (.mul (.qconst (1 : ℚ)) (.par 9)) (.var 2))) (.mul (.mul (.qconst (1 : ℚ)) (.par 4)) (.var 2))),
  (.sub (.sub (.sub (.sub (.mul (.qconst (1 : ℚ)) (.mul (.mul (.par 8) (.qconst (1 : ℚ))) (.var 1))) (.mul (.qconst (1 : ℚ)) (.mul (.mul (.par 8) (.par 6)) (.var 1)))) (.mul (.mul (.qconst (1 : ℚ)) (.par 7)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 3)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 1)) (.var 3))),
  (.sub (.sub (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 7)) (.var 3)) (.mul (.mul (.qconst (1 : ℚ)) (.par 9)) (.var 2))) (.mul (.mul (.qconst (1 : ℚ)) (.par 5)) (.var 4))) (.mul (.mul (.qconst (1 : ℚ)) (.par 2)) (.var 4))),
  (.add (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 3)) (.var 3)) (.mul (.mul (.qconst (1 : ℚ)) (.par 4)) (.var 2))) (.mul (.mul (.qconst (1 : ℚ)) (.par 5)) (.var 4))),
  (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 1)) (.var 3)) (.mul (.mul (.qconst (1 : ℚ)) (.par 2)) (.var 4))),
  (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 7)) (.var 3)) (.mul (.mul (.qconst (1 : ℚ)) (.par 9)) (.var 2)))
]

/-- La comprobación sintáctica FALLA para este modelo (ver el informe JSON). -/
theorem check_falla : checkModel F = false := by decide +kernel

end Models.Okuonghae_ChaosSolitonsFractals2020
