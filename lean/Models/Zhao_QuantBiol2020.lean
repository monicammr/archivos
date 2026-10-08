import KineticCheck

/-! Modelo `Zhao_QuantBiol2020` traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (4): Susceptible, Unquarantined_Infected, Quarantined_Infected, Confirmed_Infected

Parámetros estimados θ (21): R_Stage_I_Wuhan, gamma_1_Stage_I_Wuhan, gamma_2_Stage_I_Wuhan, R_Stage_II_Wuhan, gamma_1_Stage_II_Wuhan, gamma_2_Stage_II_Wuhan, R_Stage_III_Wuhan, gamma_1_Stage_III_Wuhan, gamma_2_Stage_III_Wuhan, R_Stage_I_Hubei, gamma_1_Stage_I_Hubei, gamma_2_Stage_I_Hubei, R_Stage_II_Hubei, gamma_1_Stage_II_Hubei, gamma_2_Stage_II_Hubei, R_Stage_I_China, gamma_1_Stage_I_China, gamma_2_Stage_I_China, R_Stage_II_China, gamma_1_Stage_II_China, gamma_2_Stage_II_China
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck

namespace Models.Zhao_QuantBiol2020

/-- Máscara de parámetros con valor nominal > 0 (los demás: signo arbitrario). -/
def pos : Fin 21 → Bool := ![true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true]

def F : Fin 4 → KExpr 4 21 := ![
  (KExpr.sub (KExpr.qconst (0 : ℚ)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 0))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 1)))) (KExpr.var 0)) (KExpr.var 1)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (9010000 : ℚ)))))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 0))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 1)))) (KExpr.var 0)) (KExpr.var 1)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (9010000 : ℚ))))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 1)))) (KExpr.var 1))),
  (KExpr.sub (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 1)))) (KExpr.var 1)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 2)))) (KExpr.var 2))),
  (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 2)))) (KExpr.var 2))
]

theorem check : checkModel pos F = true := by decide +kernel

/-- θ₀ nominal (PEtab), en racionales exactos. -/
def θq : Fin 21 → ℚ := ![(11773 / 2500 : ℚ), (63 / 1000 : ℚ), (1 / 20 : ℚ), (303 / 400 : ℚ), (3917 / 10000 : ℚ), (643 / 10000 : ℚ), (4797 / 10000 : ℚ), (1237 / 2000 : ℚ), (161 / 500 : ℚ), (2967 / 500 : ℚ), (1 / 20 : ℚ), (1 / 20 : ℚ), (6079 / 10000 : ℚ), (61 / 125 : ℚ), (957 / 5000 : ℚ), (15283 / 10000 : ℚ), (1941 / 10000 : ℚ), (1 / 20 : ℚ), (5753 / 10000 : ℚ), (5157 / 10000 : ℚ), (2189 / 10000 : ℚ)]

/-- Condiciones iniciales nominales (no dependen de θ). -/
def xq : Fin 4 → ℚ := ![(9010000 : ℚ), (258 : ℚ), (0 : ℚ), (258 : ℚ)]

theorem theta_ok : checkPosParams pos θq = true := by decide +kernel

theorem x0_ok : checkNonneg xq = true := by decide +kernel

/-- Diferenciabilidad de la trayectoria (y positividad) para este modelo. -/
def diff := @checked_model_hasFDerivAt _ _ pos F check

/-- Teorema final: la única condición restante es que la solución nominal
exista en [0, T]. -/
def final := @checked_model_final _ _ pos F check θq theta_ok xq x0_ok

end Models.Zhao_QuantBiol2020

#print axioms Models.Zhao_QuantBiol2020.diff

#print axioms Models.Zhao_QuantBiol2020.final
