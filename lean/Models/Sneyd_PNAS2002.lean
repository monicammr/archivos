import KineticCheck

/-! Modelo `Sneyd_PNAS2002` traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (6): IPR_O, IPR_R, IPR_I1, IPR_S, IPR_A, IPR_I2

Parámetros estimados θ (14): k1, k2, k3, k4, k_1, k_2, k_3, k_4, l2, l4, l6, l_2, l_4, l_6
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck

namespace Models.Sneyd_PNAS2002

/-- Máscara de parámetros con valor nominal > 0 (los demás: signo arbitrario). -/
def pos : Fin 14 → Bool := ![true, true, true, true, true, true, true, true, true, true, true, true, true, true]

def F : Fin 6 → KExpr 6 14 := ![
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.mul (KExpr.div (KExpr.mul (KExpr.div (KExpr.div (KExpr.par 4) (KExpr.par 0)) (KExpr.div (KExpr.par 11) (KExpr.par 8))) (KExpr.par 7)) (KExpr.add (KExpr.div (KExpr.div (KExpr.par 4) (KExpr.par 0)) (KExpr.div (KExpr.par 11) (KExpr.par 8))) (KExpr.qconst (10 : ℚ)))) (KExpr.var 4)) (KExpr.mul (KExpr.div (KExpr.mul (KExpr.div (KExpr.div (KExpr.par 4) (KExpr.par 0)) (KExpr.div (KExpr.par 11) (KExpr.par 8))) (KExpr.par 13)) (KExpr.add (KExpr.div (KExpr.div (KExpr.par 4) (KExpr.par 0)) (KExpr.div (KExpr.par 11) (KExpr.par 8))) (KExpr.qconst (10 : ℚ)))) (KExpr.var 4))) (KExpr.mul (KExpr.par 6) (KExpr.var 3))) (KExpr.add (KExpr.add (KExpr.add (KExpr.mul (KExpr.div (KExpr.par 5) (KExpr.add (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.qconst (10 : ℚ)) (KExpr.div (KExpr.div (KExpr.par 7) (KExpr.par 3)) (KExpr.div (KExpr.par 13) (KExpr.par 10)))))) (KExpr.var 0)) (KExpr.mul (KExpr.div (KExpr.mul (KExpr.par 12) (KExpr.qconst (10 : ℚ))) (KExpr.add (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.qconst (10 : ℚ)) (KExpr.div (KExpr.div (KExpr.par 7) (KExpr.par 3)) (KExpr.div (KExpr.par 13) (KExpr.par 10)))))) (KExpr.var 0))) (KExpr.add (KExpr.mul (KExpr.div (KExpr.mul (KExpr.mul (KExpr.par 3) (KExpr.div (KExpr.div (KExpr.par 7) (KExpr.par 3)) (KExpr.div (KExpr.par 13) (KExpr.par 10)))) (KExpr.qconst (10 : ℚ))) (KExpr.add (KExpr.div (KExpr.div (KExpr.par 7) (KExpr.par 3)) (KExpr.div (KExpr.par 13) (KExpr.par 10))) (KExpr.qconst (10 : ℚ)))) (KExpr.var 0)) (KExpr.mul (KExpr.div (KExpr.mul (KExpr.par 10) (KExpr.qconst (10 : ℚ))) (KExpr.add (KExpr.div (KExpr.div (KExpr.par 7) (KExpr.par 3)) (KExpr.div (KExpr.par 13) (KExpr.par 10))) (KExpr.qconst (10 : ℚ)))) (KExpr.var 0)))) (KExpr.mul (KExpr.div (KExpr.mul (KExpr.par 2) (KExpr.div (KExpr.div (KExpr.par 7) (KExpr.par 3)) (KExpr.div (KExpr.par 13) (KExpr.par 10)))) (KExpr.add (KExpr.div (KExpr.div (KExpr.par 7) (KExpr.par 3)) (KExpr.div (KExpr.par 13) (KExpr.par 10))) (KExpr.qconst (10 : ℚ)))) (KExpr.var 0)))),
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.mul (KExpr.div (KExpr.par 5) (KExpr.add (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.qconst (10 : ℚ)) (KExpr.div (KExpr.div (KExpr.par 7) (KExpr.par 3)) (KExpr.div (KExpr.par 13) (KExpr.par 10)))))) (KExpr.var 0)) (KExpr.mul (KExpr.div (KExpr.mul (KExpr.par 12) (KExpr.qconst (10 : ℚ))) (KExpr.add (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.qconst (10 : ℚ)) (KExpr.div (KExpr.div (KExpr.par 7) (KExpr.par 3)) (KExpr.div (KExpr.par 13) (KExpr.par 10)))))) (KExpr.var 0))) (KExpr.add (KExpr.mul (KExpr.par 4) (KExpr.var 2)) (KExpr.mul (KExpr.par 11) (KExpr.var 2)))) (KExpr.add (KExpr.mul (KExpr.div (KExpr.mul (KExpr.mul (KExpr.par 0) (KExpr.div (KExpr.div (KExpr.par 4) (KExpr.par 0)) (KExpr.div (KExpr.par 11) (KExpr.par 8)))) (KExpr.qconst (10 : ℚ))) (KExpr.add (KExpr.div (KExpr.div (KExpr.par 4) (KExpr.par 0)) (KExpr.div (KExpr.par 11) (KExpr.par 8))) (KExpr.mul (KExpr.qconst (10 : ℚ)) (KExpr.add (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.div (KExpr.div (KExpr.par 4) (KExpr.par 0)) (KExpr.div (KExpr.par 11) (KExpr.par 8))) (KExpr.div (KExpr.div (KExpr.par 5) (KExpr.par 1)) (KExpr.div (KExpr.par 12) (KExpr.par 9)))))))) (KExpr.var 1)) (KExpr.mul (KExpr.div (KExpr.mul (KExpr.par 8) (KExpr.qconst (10 : ℚ))) (KExpr.add (KExpr.div (KExpr.div (KExpr.par 4) (KExpr.par 0)) (KExpr.div (KExpr.par 11) (KExpr.par 8))) (KExpr.mul (KExpr.qconst (10 : ℚ)) (KExpr.add (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.div (KExpr.div (KExpr.par 4) (KExpr.par 0)) (KExpr.div (KExpr.par 11) (KExpr.par 8))) (KExpr.div (KExpr.div (KExpr.par 5) (KExpr.par 1)) (KExpr.div (KExpr.par 12) (KExpr.par 9)))))))) (KExpr.var 1)))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.div (KExpr.mul (KExpr.mul (KExpr.par 0) (KExpr.div (KExpr.div (KExpr.par 4) (KExpr.par 0)) (KExpr.div (KExpr.par 11) (KExpr.par 8)))) (KExpr.qconst (10 : ℚ))) (KExpr.add (KExpr.div (KExpr.div (KExpr.par 4) (KExpr.par 0)) (KExpr.div (KExpr.par 11) (KExpr.par 8))) (KExpr.mul (KExpr.qconst (10 : ℚ)) (KExpr.add (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.div (KExpr.div (KExpr.par 4) (KExpr.par 0)) (KExpr.div (KExpr.par 11) (KExpr.par 8))) (KExpr.div (KExpr.div (KExpr.par 5) (KExpr.par 1)) (KExpr.div (KExpr.par 12) (KExpr.par 9)))))))) (KExpr.var 1)) (KExpr.mul (KExpr.div (KExpr.mul (KExpr.par 8) (KExpr.qconst (10 : ℚ))) (KExpr.add (KExpr.div (KExpr.div (KExpr.par 4) (KExpr.par 0)) (KExpr.div (KExpr.par 11) (KExpr.par 8))) (KExpr.mul (KExpr.qconst (10 : ℚ)) (KExpr.add (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.div (KExpr.div (KExpr.par 4) (KExpr.par 0)) (KExpr.div (KExpr.par 11) (KExpr.par 8))) (KExpr.div (KExpr.div (KExpr.par 5) (KExpr.par 1)) (KExpr.div (KExpr.par 12) (KExpr.par 9)))))))) (KExpr.var 1))) (KExpr.add (KExpr.mul (KExpr.par 4) (KExpr.var 2)) (KExpr.mul (KExpr.par 11) (KExpr.var 2)))),
  (KExpr.sub (KExpr.mul (KExpr.div (KExpr.mul (KExpr.par 2) (KExpr.div (KExpr.div (KExpr.par 7) (KExpr.par 3)) (KExpr.div (KExpr.par 13) (KExpr.par 10)))) (KExpr.add (KExpr.div (KExpr.div (KExpr.par 7) (KExpr.par 3)) (KExpr.div (KExpr.par 13) (KExpr.par 10))) (KExpr.qconst (10 : ℚ)))) (KExpr.var 0)) (KExpr.mul (KExpr.par 6) (KExpr.var 3))),
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.mul (KExpr.div (KExpr.mul (KExpr.mul (KExpr.par 3) (KExpr.div (KExpr.div (KExpr.par 7) (KExpr.par 3)) (KExpr.div (KExpr.par 13) (KExpr.par 10)))) (KExpr.qconst (10 : ℚ))) (KExpr.add (KExpr.div (KExpr.div (KExpr.par 7) (KExpr.par 3)) (KExpr.div (KExpr.par 13) (KExpr.par 10))) (KExpr.qconst (10 : ℚ)))) (KExpr.var 0)) (KExpr.mul (KExpr.div (KExpr.mul (KExpr.par 10) (KExpr.qconst (10 : ℚ))) (KExpr.add (KExpr.div (KExpr.div (KExpr.par 7) (KExpr.par 3)) (KExpr.div (KExpr.par 13) (KExpr.par 10))) (KExpr.qconst (10 : ℚ)))) (KExpr.var 0))) (KExpr.add (KExpr.mul (KExpr.par 4) (KExpr.var 5)) (KExpr.mul (KExpr.par 11) (KExpr.var 5)))) (KExpr.add (KExpr.add (KExpr.mul (KExpr.div (KExpr.mul (KExpr.div (KExpr.div (KExpr.par 4) (KExpr.par 0)) (KExpr.div (KExpr.par 11) (KExpr.par 8))) (KExpr.par 7)) (KExpr.add (KExpr.div (KExpr.div (KExpr.par 4) (KExpr.par 0)) (KExpr.div (KExpr.par 11) (KExpr.par 8))) (KExpr.qconst (10 : ℚ)))) (KExpr.var 4)) (KExpr.mul (KExpr.div (KExpr.mul (KExpr.div (KExpr.div (KExpr.par 4) (KExpr.par 0)) (KExpr.div (KExpr.par 11) (KExpr.par 8))) (KExpr.par 13)) (KExpr.add (KExpr.div (KExpr.div (KExpr.par 4) (KExpr.par 0)) (KExpr.div (KExpr.par 11) (KExpr.par 8))) (KExpr.qconst (10 : ℚ)))) (KExpr.var 4))) (KExpr.add (KExpr.mul (KExpr.div (KExpr.mul (KExpr.mul (KExpr.par 0) (KExpr.div (KExpr.div (KExpr.par 4) (KExpr.par 0)) (KExpr.div (KExpr.par 11) (KExpr.par 8)))) (KExpr.qconst (10 : ℚ))) (KExpr.add (KExpr.div (KExpr.div (KExpr.par 4) (KExpr.par 0)) (KExpr.div (KExpr.par 11) (KExpr.par 8))) (KExpr.qconst (10 : ℚ)))) (KExpr.var 4)) (KExpr.mul (KExpr.div (KExpr.mul (KExpr.par 8) (KExpr.qconst (10 : ℚ))) (KExpr.add (KExpr.div (KExpr.div (KExpr.par 4) (KExpr.par 0)) (KExpr.div (KExpr.par 11) (KExpr.par 8))) (KExpr.qconst (10 : ℚ)))) (KExpr.var 4))))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.div (KExpr.mul (KExpr.mul (KExpr.par 0) (KExpr.div (KExpr.div (KExpr.par 4) (KExpr.par 0)) (KExpr.div (KExpr.par 11) (KExpr.par 8)))) (KExpr.qconst (10 : ℚ))) (KExpr.add (KExpr.div (KExpr.div (KExpr.par 4) (KExpr.par 0)) (KExpr.div (KExpr.par 11) (KExpr.par 8))) (KExpr.qconst (10 : ℚ)))) (KExpr.var 4)) (KExpr.mul (KExpr.div (KExpr.mul (KExpr.par 8) (KExpr.qconst (10 : ℚ))) (KExpr.add (KExpr.div (KExpr.div (KExpr.par 4) (KExpr.par 0)) (KExpr.div (KExpr.par 11) (KExpr.par 8))) (KExpr.qconst (10 : ℚ)))) (KExpr.var 4))) (KExpr.add (KExpr.mul (KExpr.par 4) (KExpr.var 5)) (KExpr.mul (KExpr.par 11) (KExpr.var 5))))
]

theorem check : checkModel pos F = true := by decide +kernel

/-- θ₀ nominal (PEtab), en racionales exactos. -/
def θq : Fin 14 → ℚ := ![(93180273932749 / 25000000000000 : ℚ), (249999999999977 / 2500000000 : ℚ), (78726703461853 / 5000000000000 : ℚ), (124922822035393 / 1250000000 : ℚ), (923924728172173 / 1000000000000000 : ℚ), (250623681331 / 250000000000000 : ℚ), (191463005974811 / 100000000000000 : ℚ), (307920732487903 / 100000000000 : ℚ), (940077018858089 / 1000000000000000 : ℚ), (285837713545253 / 100000000000000 : ℚ), (249999999999977 / 2500000000 : ℚ), (173832229564051 / 500000000000000 : ℚ), (1388020361713 / 100000000000000 : ℚ), (1 / 1000 : ℚ)]

/-- Condiciones iniciales nominales (no dependen de θ). -/
def xq : Fin 6 → ℚ := ![(0 : ℚ), (1 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]

theorem theta_ok : checkPosParams pos θq = true := by decide +kernel

theorem x0_ok : checkNonneg xq = true := by decide +kernel

/-- Diferenciabilidad de la trayectoria (y positividad) para este modelo. -/
def diff := @checked_model_hasFDerivAt _ _ pos F check

/-- Teorema final: la única condición restante es que la solución nominal
exista en [0, T]. -/
def final := @checked_model_final _ _ pos F check θq theta_ok xq x0_ok

end Models.Sneyd_PNAS2002

#print axioms Models.Sneyd_PNAS2002.diff

#print axioms Models.Sneyd_PNAS2002.final
