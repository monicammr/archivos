import KineticCheck

/-! Modelo `Boehm_JProteomeRes2014` traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (9): STAT5A, STAT5B, pApB, pApA, pBpB, nucpApA, nucpApB, nucpBpB, τ (tiempo)

Parámetros estimados θ (6): Epo_degradation_BaF3, k_exp_hetero, k_exp_homo, k_imp_hetero, k_imp_homo, k_phos
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck

namespace Models.Boehm_JProteomeRes2014

def F : Fin 9 → KExpr 9 6 := ![
  (.add (.add (.sub (.sub (.qconst (0 : ℚ)) (.mul (.qconst (10 / 7 : ℚ)) (.mul (.mul (.mul (.qconst (7 / 5 : ℚ)) (.mul (.qconst (1 / 8000000 : ℚ)) (.exp (.mul (.mul (.qconst (-1 : ℚ)) (.par 0)) (.var 8))))) (.npow (.var 0) 2)) (.par 5)))) (.mul (.qconst (5 / 7 : ℚ)) (.mul (.mul (.mul (.mul (.qconst (7 / 5 : ℚ)) (.mul (.qconst (1 / 8000000 : ℚ)) (.exp (.mul (.mul (.qconst (-1 : ℚ)) (.par 0)) (.var 8))))) (.var 0)) (.var 1)) (.par 5)))) (.mul (.qconst (10 / 7 : ℚ)) (.mul (.mul (.qconst (9 / 20 : ℚ)) (.par 2)) (.var 5)))) (.mul (.qconst (5 / 7 : ℚ)) (.mul (.mul (.qconst (9 / 20 : ℚ)) (.par 1)) (.var 6)))),
  (.add (.add (.sub (.sub (.qconst (0 : ℚ)) (.mul (.qconst (5 / 7 : ℚ)) (.mul (.mul (.mul (.mul (.qconst (7 / 5 : ℚ)) (.mul (.qconst (1 / 8000000 : ℚ)) (.exp (.mul (.mul (.qconst (-1 : ℚ)) (.par 0)) (.var 8))))) (.var 0)) (.var 1)) (.par 5)))) (.mul (.qconst (10 / 7 : ℚ)) (.mul (.mul (.mul (.qconst (7 / 5 : ℚ)) (.mul (.qconst (1 / 8000000 : ℚ)) (.exp (.mul (.mul (.qconst (-1 : ℚ)) (.par 0)) (.var 8))))) (.npow (.var 1) 2)) (.par 5)))) (.mul (.qconst (5 / 7 : ℚ)) (.mul (.mul (.qconst (9 / 20 : ℚ)) (.par 1)) (.var 6)))) (.mul (.qconst (10 / 7 : ℚ)) (.mul (.mul (.qconst (9 / 20 : ℚ)) (.par 2)) (.var 7)))),
  (.sub (.mul (.qconst (5 / 7 : ℚ)) (.mul (.mul (.mul (.mul (.qconst (7 / 5 : ℚ)) (.mul (.qconst (1 / 8000000 : ℚ)) (.exp (.mul (.mul (.qconst (-1 : ℚ)) (.par 0)) (.var 8))))) (.var 0)) (.var 1)) (.par 5))) (.mul (.qconst (5 / 7 : ℚ)) (.mul (.mul (.qconst (7 / 5 : ℚ)) (.par 3)) (.var 2)))),
  (.sub (.mul (.qconst (5 / 7 : ℚ)) (.mul (.mul (.mul (.qconst (7 / 5 : ℚ)) (.mul (.qconst (1 / 8000000 : ℚ)) (.exp (.mul (.mul (.qconst (-1 : ℚ)) (.par 0)) (.var 8))))) (.npow (.var 0) 2)) (.par 5))) (.mul (.qconst (5 / 7 : ℚ)) (.mul (.mul (.qconst (7 / 5 : ℚ)) (.par 4)) (.var 3)))),
  (.sub (.mul (.qconst (5 / 7 : ℚ)) (.mul (.mul (.mul (.qconst (7 / 5 : ℚ)) (.mul (.qconst (1 / 8000000 : ℚ)) (.exp (.mul (.mul (.qconst (-1 : ℚ)) (.par 0)) (.var 8))))) (.npow (.var 1) 2)) (.par 5))) (.mul (.qconst (5 / 7 : ℚ)) (.mul (.mul (.qconst (7 / 5 : ℚ)) (.par 4)) (.var 4)))),
  (.sub (.mul (.qconst (20 / 9 : ℚ)) (.mul (.mul (.qconst (7 / 5 : ℚ)) (.par 4)) (.var 3))) (.mul (.qconst (20 / 9 : ℚ)) (.mul (.mul (.qconst (9 / 20 : ℚ)) (.par 2)) (.var 5)))),
  (.sub (.mul (.qconst (20 / 9 : ℚ)) (.mul (.mul (.qconst (7 / 5 : ℚ)) (.par 3)) (.var 2))) (.mul (.qconst (20 / 9 : ℚ)) (.mul (.mul (.qconst (9 / 20 : ℚ)) (.par 1)) (.var 6)))),
  (.sub (.mul (.qconst (20 / 9 : ℚ)) (.mul (.mul (.qconst (7 / 5 : ℚ)) (.par 4)) (.var 4))) (.mul (.qconst (20 / 9 : ℚ)) (.mul (.mul (.qconst (9 / 20 : ℚ)) (.par 2)) (.var 7)))),
  (.qconst (1 : ℚ))
]

theorem check : checkModel F = true := by decide +kernel

/-- Diferenciabilidad de la trayectoria (y positividad) para este modelo. -/
def diff := @checked_model_hasFDerivAt _ _ F check

end Models.Boehm_JProteomeRes2014

#print axioms Models.Boehm_JProteomeRes2014.diff
