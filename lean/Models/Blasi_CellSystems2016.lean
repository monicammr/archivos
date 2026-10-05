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

/-- Máscara de parámetros con valor nominal > 0 (los demás: signo arbitrario). -/
def pos : Fin 8 → Bool := ![true, true, true, true, true, true, true, true]

def F : Fin 16 → KExpr 16 8 := ![
  (KExpr.add (KExpr.sub (KExpr.add (KExpr.sub (KExpr.add (KExpr.sub (KExpr.add (KExpr.sub (KExpr.qconst (0 : ℚ)) (KExpr.mul (KExpr.par 0) (KExpr.var 0))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 2))) (KExpr.mul (KExpr.par 1) (KExpr.var 0))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 1))) (KExpr.mul (KExpr.par 0) (KExpr.var 0))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 3))) (KExpr.mul (KExpr.par 0) (KExpr.var 0))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 4))),
  (KExpr.add (KExpr.sub (KExpr.add (KExpr.sub (KExpr.add (KExpr.sub (KExpr.sub (KExpr.mul (KExpr.par 1) (KExpr.var 0)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 1))) (KExpr.mul (KExpr.par 0) (KExpr.var 1))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 5))) (KExpr.mul (KExpr.par 0) (KExpr.var 1))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 8))) (KExpr.mul (KExpr.par 0) (KExpr.var 1))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 9))),
  (KExpr.add (KExpr.sub (KExpr.add (KExpr.sub (KExpr.add (KExpr.sub (KExpr.sub (KExpr.mul (KExpr.par 0) (KExpr.var 0)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 2))) (KExpr.mul (KExpr.par 0) (KExpr.var 2))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 5))) (KExpr.mul (KExpr.par 2) (KExpr.var 2))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 6))) (KExpr.mul (KExpr.par 0) (KExpr.var 2))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 7))),
  (KExpr.add (KExpr.sub (KExpr.add (KExpr.sub (KExpr.add (KExpr.sub (KExpr.sub (KExpr.mul (KExpr.par 0) (KExpr.var 0)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 3))) (KExpr.mul (KExpr.par 3) (KExpr.var 3))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 6))) (KExpr.mul (KExpr.par 0) (KExpr.var 3))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 8))) (KExpr.mul (KExpr.par 0) (KExpr.var 3))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 10))),
  (KExpr.add (KExpr.sub (KExpr.add (KExpr.sub (KExpr.add (KExpr.sub (KExpr.sub (KExpr.mul (KExpr.par 0) (KExpr.var 0)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 4))) (KExpr.mul (KExpr.par 0) (KExpr.var 4))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 7))) (KExpr.mul (KExpr.par 0) (KExpr.var 4))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 9))) (KExpr.mul (KExpr.par 4) (KExpr.var 4))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 10))),
  (KExpr.add (KExpr.sub (KExpr.add (KExpr.sub (KExpr.sub (KExpr.add (KExpr.sub (KExpr.mul (KExpr.par 0) (KExpr.var 2)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 5))) (KExpr.mul (KExpr.par 0) (KExpr.var 1))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 5))) (KExpr.mul (KExpr.par 0) (KExpr.var 5))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 11))) (KExpr.mul (KExpr.par 0) (KExpr.var 5))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 12))),
  (KExpr.add (KExpr.sub (KExpr.add (KExpr.sub (KExpr.sub (KExpr.add (KExpr.sub (KExpr.mul (KExpr.par 2) (KExpr.var 2)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 6))) (KExpr.mul (KExpr.par 3) (KExpr.var 3))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 6))) (KExpr.mul (KExpr.par 5) (KExpr.var 6))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 11))) (KExpr.mul (KExpr.par 0) (KExpr.var 6))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 13))),
  (KExpr.add (KExpr.sub (KExpr.add (KExpr.sub (KExpr.sub (KExpr.add (KExpr.sub (KExpr.mul (KExpr.par 0) (KExpr.var 2)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 7))) (KExpr.mul (KExpr.par 0) (KExpr.var 4))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 7))) (KExpr.mul (KExpr.par 0) (KExpr.var 7))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 12))) (KExpr.mul (KExpr.par 0) (KExpr.var 7))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 13))),
  (KExpr.add (KExpr.sub (KExpr.add (KExpr.sub (KExpr.sub (KExpr.add (KExpr.sub (KExpr.mul (KExpr.par 0) (KExpr.var 1)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 8))) (KExpr.mul (KExpr.par 0) (KExpr.var 3))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 8))) (KExpr.mul (KExpr.par 0) (KExpr.var 8))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 11))) (KExpr.mul (KExpr.par 0) (KExpr.var 8))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 14))),
  (KExpr.add (KExpr.sub (KExpr.add (KExpr.sub (KExpr.sub (KExpr.add (KExpr.sub (KExpr.mul (KExpr.par 0) (KExpr.var 1)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 9))) (KExpr.mul (KExpr.par 0) (KExpr.var 4))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 9))) (KExpr.mul (KExpr.par 0) (KExpr.var 9))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 12))) (KExpr.mul (KExpr.par 0) (KExpr.var 9))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 14))),
  (KExpr.add (KExpr.sub (KExpr.add (KExpr.sub (KExpr.sub (KExpr.add (KExpr.sub (KExpr.mul (KExpr.par 0) (KExpr.var 3)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 10))) (KExpr.mul (KExpr.par 4) (KExpr.var 4))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 10))) (KExpr.mul (KExpr.par 0) (KExpr.var 10))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 13))) (KExpr.mul (KExpr.par 6) (KExpr.var 10))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 14))),
  (KExpr.add (KExpr.sub (KExpr.sub (KExpr.add (KExpr.sub (KExpr.add (KExpr.sub (KExpr.mul (KExpr.par 0) (KExpr.var 5)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 11))) (KExpr.mul (KExpr.par 5) (KExpr.var 6))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 11))) (KExpr.mul (KExpr.par 0) (KExpr.var 8))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 11))) (KExpr.mul (KExpr.par 0) (KExpr.var 11))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 15))),
  (KExpr.add (KExpr.sub (KExpr.sub (KExpr.add (KExpr.sub (KExpr.add (KExpr.sub (KExpr.mul (KExpr.par 0) (KExpr.var 5)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 12))) (KExpr.mul (KExpr.par 0) (KExpr.var 7))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 12))) (KExpr.mul (KExpr.par 0) (KExpr.var 9))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 12))) (KExpr.mul (KExpr.par 0) (KExpr.var 12))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 15))),
  (KExpr.add (KExpr.sub (KExpr.sub (KExpr.add (KExpr.sub (KExpr.add (KExpr.sub (KExpr.mul (KExpr.par 0) (KExpr.var 6)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 13))) (KExpr.mul (KExpr.par 0) (KExpr.var 7))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 13))) (KExpr.mul (KExpr.par 0) (KExpr.var 10))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 13))) (KExpr.mul (KExpr.par 0) (KExpr.var 13))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 15))),
  (KExpr.add (KExpr.sub (KExpr.sub (KExpr.add (KExpr.sub (KExpr.add (KExpr.sub (KExpr.mul (KExpr.par 0) (KExpr.var 8)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 14))) (KExpr.mul (KExpr.par 0) (KExpr.var 9))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 14))) (KExpr.mul (KExpr.par 6) (KExpr.var 10))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 14))) (KExpr.mul (KExpr.par 7) (KExpr.var 14))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 15))),
  (KExpr.sub (KExpr.add (KExpr.sub (KExpr.add (KExpr.sub (KExpr.add (KExpr.sub (KExpr.mul (KExpr.par 0) (KExpr.var 11)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 15))) (KExpr.mul (KExpr.par 0) (KExpr.var 12))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 15))) (KExpr.mul (KExpr.par 0) (KExpr.var 13))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 15))) (KExpr.mul (KExpr.par 7) (KExpr.var 14))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 15)))
]

theorem check : checkModel pos F = true := by decide +kernel

/-- Diferenciabilidad de la trayectoria (y positividad) para este modelo. -/
def diff := @checked_model_hasFDerivAt _ _ pos F check

end Models.Blasi_CellSystems2016

#print axioms Models.Blasi_CellSystems2016.diff
