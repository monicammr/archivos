import KineticCheck

/-! Modelo `Weber_BMC2015` traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (7): PKD, PKDDAGa, PI4K3B, PI4K3Ba, CERTERa, CERT, CERTTGNa

Parámetros estimados θ (26): a11, a12, a21, a22, a31, a32, a33, m11, m22, m31, m33, p11, p12, p13, p21, p22, p31, p32, p33, pu3, pu4, pu5, pu6, s12, s21, s31
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck

namespace Models.Weber_BMC2015

/-- Máscara de parámetros con valor nominal > 0 (los demás: signo arbitrario). -/
def pos : Fin 26 → Bool := ![true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true]

def F : Fin 7 → KExpr 7 26 := ![
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 1)) (KExpr.par 13)) (KExpr.qconst (1 : ℚ))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 23))) (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.var 4) (KExpr.var 3)) (KExpr.var 0)) (KExpr.par 11)) (KExpr.par 16)) (KExpr.mul (KExpr.add (KExpr.var 3) (KExpr.par 9)) (KExpr.add (KExpr.par 7) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 4) (KExpr.var 3)) (KExpr.par 16)) (KExpr.add (KExpr.var 3) (KExpr.par 9))))))) (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 0)) (KExpr.par 12)) (KExpr.qconst (1 : ℚ)))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 0)) (KExpr.par 0)))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.var 4) (KExpr.var 3)) (KExpr.var 0)) (KExpr.par 11)) (KExpr.par 16)) (KExpr.mul (KExpr.add (KExpr.var 3) (KExpr.par 9)) (KExpr.add (KExpr.par 7) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 4) (KExpr.var 3)) (KExpr.par 16)) (KExpr.add (KExpr.var 3) (KExpr.par 9))))))) (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 0)) (KExpr.par 12)) (KExpr.qconst (1 : ℚ)))) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 1)) (KExpr.par 13)) (KExpr.qconst (1 : ℚ))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 1)) (KExpr.par 1)))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 3)) (KExpr.par 14)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 24))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 2) (KExpr.var 1)) (KExpr.par 15)) (KExpr.add (KExpr.var 1) (KExpr.par 8)))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 2)) (KExpr.par 2)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 2) (KExpr.var 1)) (KExpr.par 15)) (KExpr.add (KExpr.var 1) (KExpr.par 8)))) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 3)) (KExpr.par 14)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 3)) (KExpr.par 3)))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 5)) (KExpr.par 17)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 25))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 4) (KExpr.var 3)) (KExpr.par 16)) (KExpr.add (KExpr.var 3) (KExpr.par 9)))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 4)) (KExpr.par 4)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 6) (KExpr.var 1)) (KExpr.par 18)) (KExpr.add (KExpr.var 1) (KExpr.par 10)))) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 5)) (KExpr.par 17)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 5)) (KExpr.par 5)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 4) (KExpr.var 3)) (KExpr.par 16)) (KExpr.add (KExpr.var 3) (KExpr.par 9)))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 6) (KExpr.var 1)) (KExpr.par 18)) (KExpr.add (KExpr.var 1) (KExpr.par 10)))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 6)) (KExpr.par 6))))
]

theorem check : checkModel pos F = true := by decide +kernel

/-- Diferenciabilidad de la trayectoria (y positividad) para este modelo. -/
def diff := @checked_model_hasFDerivAt _ _ pos F check

end Models.Weber_BMC2015

#print axioms Models.Weber_BMC2015.diff
