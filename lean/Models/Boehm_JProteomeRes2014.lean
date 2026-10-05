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

/-- Máscara de parámetros con valor nominal > 0 (los demás: signo arbitrario). -/
def pos : Fin 6 → Bool := ![true, true, true, true, true, true]

def F : Fin 9 → KExpr 9 6 := ![
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.qconst (10 / 7 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (9 / 20 : ℚ)) (KExpr.par 2)) (KExpr.var 5))) (KExpr.mul (KExpr.qconst (5 / 7 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (9 / 20 : ℚ)) (KExpr.par 1)) (KExpr.var 6)))) (KExpr.add (KExpr.mul (KExpr.qconst (10 / 7 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (7 / 5 : ℚ)) (KExpr.mul (KExpr.qconst (1 / 8000000 : ℚ)) (KExpr.exp (KExpr.mul (KExpr.mul (KExpr.qconst (-1 : ℚ)) (KExpr.par 0)) (KExpr.var 8))))) (KExpr.npow (KExpr.var 0) 2)) (KExpr.par 5))) (KExpr.mul (KExpr.qconst (5 / 7 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (7 / 5 : ℚ)) (KExpr.mul (KExpr.qconst (1 / 8000000 : ℚ)) (KExpr.exp (KExpr.mul (KExpr.mul (KExpr.qconst (-1 : ℚ)) (KExpr.par 0)) (KExpr.var 8))))) (KExpr.var 0)) (KExpr.var 1)) (KExpr.par 5))))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.qconst (5 / 7 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (9 / 20 : ℚ)) (KExpr.par 1)) (KExpr.var 6))) (KExpr.mul (KExpr.qconst (10 / 7 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (9 / 20 : ℚ)) (KExpr.par 2)) (KExpr.var 7)))) (KExpr.add (KExpr.mul (KExpr.qconst (5 / 7 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (7 / 5 : ℚ)) (KExpr.mul (KExpr.qconst (1 / 8000000 : ℚ)) (KExpr.exp (KExpr.mul (KExpr.mul (KExpr.qconst (-1 : ℚ)) (KExpr.par 0)) (KExpr.var 8))))) (KExpr.var 0)) (KExpr.var 1)) (KExpr.par 5))) (KExpr.mul (KExpr.qconst (10 / 7 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (7 / 5 : ℚ)) (KExpr.mul (KExpr.qconst (1 / 8000000 : ℚ)) (KExpr.exp (KExpr.mul (KExpr.mul (KExpr.qconst (-1 : ℚ)) (KExpr.par 0)) (KExpr.var 8))))) (KExpr.npow (KExpr.var 1) 2)) (KExpr.par 5))))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (5 / 7 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (7 / 5 : ℚ)) (KExpr.mul (KExpr.qconst (1 / 8000000 : ℚ)) (KExpr.exp (KExpr.mul (KExpr.mul (KExpr.qconst (-1 : ℚ)) (KExpr.par 0)) (KExpr.var 8))))) (KExpr.var 0)) (KExpr.var 1)) (KExpr.par 5))) (KExpr.mul (KExpr.qconst (5 / 7 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (7 / 5 : ℚ)) (KExpr.par 3)) (KExpr.var 2)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (5 / 7 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (7 / 5 : ℚ)) (KExpr.mul (KExpr.qconst (1 / 8000000 : ℚ)) (KExpr.exp (KExpr.mul (KExpr.mul (KExpr.qconst (-1 : ℚ)) (KExpr.par 0)) (KExpr.var 8))))) (KExpr.npow (KExpr.var 0) 2)) (KExpr.par 5))) (KExpr.mul (KExpr.qconst (5 / 7 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (7 / 5 : ℚ)) (KExpr.par 4)) (KExpr.var 3)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (5 / 7 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (7 / 5 : ℚ)) (KExpr.mul (KExpr.qconst (1 / 8000000 : ℚ)) (KExpr.exp (KExpr.mul (KExpr.mul (KExpr.qconst (-1 : ℚ)) (KExpr.par 0)) (KExpr.var 8))))) (KExpr.npow (KExpr.var 1) 2)) (KExpr.par 5))) (KExpr.mul (KExpr.qconst (5 / 7 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (7 / 5 : ℚ)) (KExpr.par 4)) (KExpr.var 4)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (20 / 9 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (7 / 5 : ℚ)) (KExpr.par 4)) (KExpr.var 3))) (KExpr.mul (KExpr.qconst (20 / 9 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (9 / 20 : ℚ)) (KExpr.par 2)) (KExpr.var 5)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (20 / 9 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (7 / 5 : ℚ)) (KExpr.par 3)) (KExpr.var 2))) (KExpr.mul (KExpr.qconst (20 / 9 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (9 / 20 : ℚ)) (KExpr.par 1)) (KExpr.var 6)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (20 / 9 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (7 / 5 : ℚ)) (KExpr.par 4)) (KExpr.var 4))) (KExpr.mul (KExpr.qconst (20 / 9 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (9 / 20 : ℚ)) (KExpr.par 2)) (KExpr.var 7)))),
  (KExpr.qconst (1 : ℚ))
]

theorem check : checkModel pos F = true := by decide +kernel

/-- Diferenciabilidad de la trayectoria (y positividad) para este modelo. -/
def diff := @checked_model_hasFDerivAt _ _ pos F check

end Models.Boehm_JProteomeRes2014

#print axioms Models.Boehm_JProteomeRes2014.diff
