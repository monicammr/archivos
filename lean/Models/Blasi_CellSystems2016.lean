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
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 2)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 1))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 3)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 4)))) (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 0) (KExpr.var 0)) (KExpr.mul (KExpr.par 1) (KExpr.var 0))) (KExpr.add (KExpr.mul (KExpr.par 0) (KExpr.var 0)) (KExpr.mul (KExpr.par 0) (KExpr.var 0))))),
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 1) (KExpr.var 0)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 5))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 8)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 9)))) (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 1)) (KExpr.mul (KExpr.par 0) (KExpr.var 1))) (KExpr.add (KExpr.mul (KExpr.par 0) (KExpr.var 1)) (KExpr.mul (KExpr.par 0) (KExpr.var 1))))),
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 0) (KExpr.var 0)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 5))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 6)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 7)))) (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 2)) (KExpr.mul (KExpr.par 0) (KExpr.var 2))) (KExpr.add (KExpr.mul (KExpr.par 2) (KExpr.var 2)) (KExpr.mul (KExpr.par 0) (KExpr.var 2))))),
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 0) (KExpr.var 0)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 6))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 8)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 10)))) (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 3)) (KExpr.mul (KExpr.par 3) (KExpr.var 3))) (KExpr.add (KExpr.mul (KExpr.par 0) (KExpr.var 3)) (KExpr.mul (KExpr.par 0) (KExpr.var 3))))),
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 0) (KExpr.var 0)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 7))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 9)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 10)))) (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 4)) (KExpr.mul (KExpr.par 0) (KExpr.var 4))) (KExpr.add (KExpr.mul (KExpr.par 0) (KExpr.var 4)) (KExpr.mul (KExpr.par 4) (KExpr.var 4))))),
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 0) (KExpr.var 2)) (KExpr.mul (KExpr.par 0) (KExpr.var 1))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 11)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 12)))) (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 5)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 5))) (KExpr.add (KExpr.mul (KExpr.par 0) (KExpr.var 5)) (KExpr.mul (KExpr.par 0) (KExpr.var 5))))),
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 2) (KExpr.var 2)) (KExpr.mul (KExpr.par 3) (KExpr.var 3))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 11)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 13)))) (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 6)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 6))) (KExpr.add (KExpr.mul (KExpr.par 5) (KExpr.var 6)) (KExpr.mul (KExpr.par 0) (KExpr.var 6))))),
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 0) (KExpr.var 2)) (KExpr.mul (KExpr.par 0) (KExpr.var 4))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 12)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 13)))) (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 7)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 7))) (KExpr.add (KExpr.mul (KExpr.par 0) (KExpr.var 7)) (KExpr.mul (KExpr.par 0) (KExpr.var 7))))),
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 0) (KExpr.var 1)) (KExpr.mul (KExpr.par 0) (KExpr.var 3))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 11)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 14)))) (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 8)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 8))) (KExpr.add (KExpr.mul (KExpr.par 0) (KExpr.var 8)) (KExpr.mul (KExpr.par 0) (KExpr.var 8))))),
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 0) (KExpr.var 1)) (KExpr.mul (KExpr.par 0) (KExpr.var 4))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 12)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 14)))) (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 9)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 9))) (KExpr.add (KExpr.mul (KExpr.par 0) (KExpr.var 9)) (KExpr.mul (KExpr.par 0) (KExpr.var 9))))),
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 0) (KExpr.var 3)) (KExpr.mul (KExpr.par 4) (KExpr.var 4))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 13)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 14)))) (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 10)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 10))) (KExpr.add (KExpr.mul (KExpr.par 0) (KExpr.var 10)) (KExpr.mul (KExpr.par 6) (KExpr.var 10))))),
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 0) (KExpr.var 5)) (KExpr.mul (KExpr.par 5) (KExpr.var 6))) (KExpr.add (KExpr.mul (KExpr.par 0) (KExpr.var 8)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 15)))) (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 11)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 11))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 11)) (KExpr.mul (KExpr.par 0) (KExpr.var 11))))),
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 0) (KExpr.var 5)) (KExpr.mul (KExpr.par 0) (KExpr.var 7))) (KExpr.add (KExpr.mul (KExpr.par 0) (KExpr.var 9)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 15)))) (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 12)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 12))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 12)) (KExpr.mul (KExpr.par 0) (KExpr.var 12))))),
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 0) (KExpr.var 6)) (KExpr.mul (KExpr.par 0) (KExpr.var 7))) (KExpr.add (KExpr.mul (KExpr.par 0) (KExpr.var 10)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 15)))) (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 13)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 13))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 13)) (KExpr.mul (KExpr.par 0) (KExpr.var 13))))),
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 0) (KExpr.var 8)) (KExpr.mul (KExpr.par 0) (KExpr.var 9))) (KExpr.add (KExpr.mul (KExpr.par 6) (KExpr.var 10)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 15)))) (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 14)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 14))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 14)) (KExpr.mul (KExpr.par 7) (KExpr.var 14))))),
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 0) (KExpr.var 11)) (KExpr.mul (KExpr.par 0) (KExpr.var 12))) (KExpr.add (KExpr.mul (KExpr.par 0) (KExpr.var 13)) (KExpr.mul (KExpr.par 7) (KExpr.var 14)))) (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 15)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 15))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 15)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 15)))))
]

theorem check : checkModel pos F = true := by decide +kernel

/-- θ₀ nominal (PEtab), en racionales exactos. -/
def θq : Fin 8 → ℚ := ![(13359999985371 / 200000000000000 : ℚ), (13649999998719 / 500000000000000 : ℚ), (6443750000779 / 3125000000000 : ℚ), (551899999917063 / 1000000000000000 : ℚ), (695899999206803 / 1000000000000000 : ℚ), (325299999788883 / 1000000000000000 : ℚ), (22054999994189 / 10000000000000 : ℚ), (359170000273213 / 100000000000000 : ℚ)]

/-- Condiciones iniciales nominales (no dependen de θ). -/
def xq : Fin 16 → ℚ := ![(1 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]

theorem theta_ok : checkPosParams pos θq = true := by decide +kernel

theorem x0_ok : checkNonneg xq = true := by decide +kernel

/-- Diferenciabilidad de la trayectoria (y positividad) para este modelo. -/
def diff := @checked_model_hasFDerivAt _ _ pos F check

/-- Teorema final: la única condición restante es que la solución nominal
exista en [0, T]. -/
def final := @checked_model_final _ _ pos F check θq theta_ok xq x0_ok

end Models.Blasi_CellSystems2016

#print axioms Models.Blasi_CellSystems2016.diff

#print axioms Models.Blasi_CellSystems2016.final
