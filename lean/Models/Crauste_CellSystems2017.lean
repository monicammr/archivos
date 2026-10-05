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

/-- Máscara de parámetros con valor nominal > 0 (los demás: signo arbitrario). -/
def pos : Fin 12 → Bool := ![true, true, true, true, true, true, true, true, true, true, true, true]

def F : Fin 5 → KExpr 5 12 := ![
  (KExpr.sub (KExpr.qconst (0 : ℚ)) (KExpr.add (KExpr.mul (KExpr.var 0) (KExpr.par 6)) (KExpr.mul (KExpr.mul (KExpr.var 0) (KExpr.var 4)) (KExpr.par 2)))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.mul (KExpr.var 0) (KExpr.var 4)) (KExpr.par 2)) (KExpr.mul (KExpr.mul (KExpr.var 1) (KExpr.var 4)) (KExpr.par 10))) (KExpr.add (KExpr.mul (KExpr.npow (KExpr.var 1) 2) (KExpr.par 3)) (KExpr.mul (KExpr.var 1) (KExpr.par 0)))),
  (KExpr.sub (KExpr.mul (KExpr.var 1) (KExpr.par 0)) (KExpr.add (KExpr.add (KExpr.mul (KExpr.npow (KExpr.var 2) 2) (KExpr.par 5)) (KExpr.mul (KExpr.mul (KExpr.var 1) (KExpr.var 2)) (KExpr.par 4))) (KExpr.mul (KExpr.var 2) (KExpr.par 1)))),
  (KExpr.mul (KExpr.var 2) (KExpr.par 1)),
  (KExpr.sub (KExpr.mul (KExpr.npow (KExpr.var 4) 2) (KExpr.par 11)) (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.var 1) (KExpr.var 4)) (KExpr.par 8)) (KExpr.mul (KExpr.mul (KExpr.var 2) (KExpr.var 4)) (KExpr.par 9))) (KExpr.mul (KExpr.var 4) (KExpr.par 7))))
]

theorem check : checkModel pos F = true := by decide +kernel

/-- Diferenciabilidad de la trayectoria (y positividad) para este modelo. -/
def diff := @checked_model_hasFDerivAt _ _ pos F check

end Models.Crauste_CellSystems2017

#print axioms Models.Crauste_CellSystems2017.diff
