import KineticCheck

/-! Modelo `Brannmark_JBC2010` traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (9): IR, IRins, IRp, IRiP, IRi, IRS, IRSiP, X, Xp

Parámetros estimados θ (15): k1a, k1aBasic, k1b, k1c, k1d, k1e, k1f, k1g, k1r, k21, k22, k3, k_IRSiP_DosR, km2, km3
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck

namespace Models.Brannmark_JBC2010

/-- Máscara de parámetros con valor nominal > 0 (los demás: signo arbitrario). -/
def pos : Fin 15 → Bool := ![true, true, true, true, true, true, true, true, true, true, true, true, true, true, true]

def F : Fin 9 → KExpr 9 15 := ![
  (KExpr.add (KExpr.add (KExpr.add (KExpr.sub (KExpr.sub (KExpr.qconst (0 : ℚ)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.par 1)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.qconst (3 / 10 : ℚ)) (KExpr.qconst (1 : ℚ)))) (KExpr.par 0)))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 1)) (KExpr.par 2))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 2)) (KExpr.par 7))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 4)) (KExpr.par 8))),
  (KExpr.sub (KExpr.sub (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.par 1))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.qconst (3 / 10 : ℚ)) (KExpr.qconst (1 : ℚ)))) (KExpr.par 0)))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 1)) (KExpr.par 2))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 1)) (KExpr.par 3))),
  (KExpr.sub (KExpr.sub (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 1)) (KExpr.par 3)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 2)) (KExpr.par 4))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 2)) (KExpr.par 7))),
  (KExpr.sub (KExpr.sub (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 2)) (KExpr.par 4)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 3)) (KExpr.par 5))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 3)) (KExpr.div (KExpr.mul (KExpr.var 8) (KExpr.par 6)) (KExpr.add (KExpr.var 8) (KExpr.qconst (1 : ℚ)))))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 3)) (KExpr.par 5)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 3)) (KExpr.div (KExpr.mul (KExpr.var 8) (KExpr.par 6)) (KExpr.add (KExpr.var 8) (KExpr.qconst (1 : ℚ)))))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 4)) (KExpr.par 8))),
  (KExpr.add (KExpr.sub (KExpr.sub (KExpr.qconst (0 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 5)) (KExpr.par 9)) (KExpr.var 2))) (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 5)) (KExpr.par 9)) (KExpr.mul (KExpr.var 3) (KExpr.par 10)))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 6)) (KExpr.par 13))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 5)) (KExpr.par 9)) (KExpr.var 2)) (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 5)) (KExpr.par 9)) (KExpr.mul (KExpr.var 3) (KExpr.par 10)))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 6)) (KExpr.par 13))),
  (KExpr.add (KExpr.sub (KExpr.qconst (0 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 6)) (KExpr.var 7)) (KExpr.par 11))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 8)) (KExpr.par 14))),
  (KExpr.sub (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 6)) (KExpr.var 7)) (KExpr.par 11)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 8)) (KExpr.par 14)))
]

theorem check : checkModel pos F = true := by decide +kernel

/-- Diferenciabilidad de la trayectoria (y positividad) para este modelo. -/
def diff := @checked_model_hasFDerivAt _ _ pos F check

end Models.Brannmark_JBC2010

#print axioms Models.Brannmark_JBC2010.diff
