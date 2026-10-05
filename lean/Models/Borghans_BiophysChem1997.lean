import KineticCheck

/-! Modelo `Borghans_BiophysChem1997` traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (3): Z_state, Y_state, A_state

Parámetros estimados θ (20): K2, K_par, Ka, Kd, Kf, Kp, Ky, Kz, Vd, Vm2, Vm3, Vp, beta_par, epsilon_par, init_A_state, init_Y_state, init_Z_state, n_par, v0, v1
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck

namespace Models.Borghans_BiophysChem1997

def F : Fin 3 → KExpr 3 20 := ![
  (.sub (.add (.add (.sub (.add (.mul (.qconst (1 : ℚ)) (.par 18)) (.mul (.qconst (1 : ℚ)) (.mul (.par 12) (.par 19)))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.par 9) (.npow (.var 0) 2)) (.add (.npow (.par 0) 2) (.npow (.var 0) 2))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.mul (.mul (.npow (.var 2) 4) (.par 10)) (.npow (.var 1) 2)) (.npow (.var 0) 4)) (.mul (.mul (.add (.npow (.var 2) 4) (.npow (.par 2) 4)) (.add (.npow (.par 6) 2) (.npow (.var 1) 2))) (.add (.npow (.par 7) 4) (.npow (.var 0) 4)))))) (.mul (.mul (.qconst (1 : ℚ)) (.par 4)) (.var 1))) (.mul (.mul (.qconst (1 : ℚ)) (.par 1)) (.var 0))),
  (.sub (.sub (.mul (.qconst (1 : ℚ)) (.div (.mul (.par 9) (.npow (.var 0) 2)) (.add (.npow (.par 0) 2) (.npow (.var 0) 2)))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.mul (.mul (.npow (.var 2) 4) (.par 10)) (.npow (.var 1) 2)) (.npow (.var 0) 4)) (.mul (.mul (.add (.npow (.var 2) 4) (.npow (.par 2) 4)) (.add (.npow (.par 6) 2) (.npow (.var 1) 2))) (.add (.npow (.par 7) 4) (.npow (.var 0) 4)))))) (.mul (.mul (.qconst (1 : ℚ)) (.par 4)) (.var 1))),
  (.sub (.sub (.mul (.mul (.qconst (1 : ℚ)) (.par 11)) (.par 12)) (.mul (.qconst (1 : ℚ)) (.div (.mul (.mul (.npow (.var 2) 2) (.par 8)) (.exp (.mul (.par 17) (.log (.var 0))))) (.mul (.add (.exp (.mul (.par 17) (.log (.par 3)))) (.exp (.mul (.par 17) (.log (.var 0))))) (.add (.npow (.var 2) 2) (.npow (.par 5) 2)))))) (.mul (.mul (.qconst (1 : ℚ)) (.var 2)) (.par 13)))
]

/-- La comprobación sintáctica FALLA para este modelo (ver el informe JSON). -/
theorem check_falla : checkModel F = false := by decide +kernel

end Models.Borghans_BiophysChem1997
