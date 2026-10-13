import KineticNetwork

/-! Modelo `Zhao_QuantBiol2020` (forma de red), traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (4): Susceptible, Unquarantined_Infected, Quarantined_Infected, Confirmed_Infected

Parámetros estimados θ (21): R_Stage_I_Wuhan, gamma_1_Stage_I_Wuhan, gamma_2_Stage_I_Wuhan, R_Stage_II_Wuhan, gamma_1_Stage_II_Wuhan, gamma_2_Stage_II_Wuhan, R_Stage_III_Wuhan, gamma_1_Stage_III_Wuhan, gamma_2_Stage_III_Wuhan, R_Stage_I_Hubei, gamma_1_Stage_I_Hubei, gamma_2_Stage_I_Hubei, R_Stage_II_Hubei, gamma_1_Stage_II_Hubei, gamma_2_Stage_II_Hubei, R_Stage_I_China, gamma_1_Stage_I_China, gamma_2_Stage_I_China, R_Stage_II_China, gamma_1_Stage_II_China, gamma_2_Stage_II_China
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck KineticNetwork

namespace Models.Zhao_QuantBiol2020

/-- Máscara de parámetros positivos (nominal > 0 o escala log). -/
def pos : Fin 21 → Bool := fun _ => true

/-- Términos de velocidad con su columna estequiométrica (3 términos). -/
def Rx : List (KExpr 4 21 × List (Fin 4 × ℚ)) := [
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 0))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 1)))) (KExpr.var 0)) (KExpr.var 1)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (9010000 : ℚ))))), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 1)))) (KExpr.var 1)), [(1, (-1 : ℚ)), (2, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 2)))) (KExpr.var 2)), [(2, (-1 : ℚ)), (3, (1 : ℚ))])
]

/-- El campo del modelo: `Fᵢ = Σ_r coef_r(i) · V_r`. -/
def F : Fin 4 → KExpr 4 21 := netF Rx

/-- Dominio ⊇ ortante y cuasi-positividad (Lean ejecuta el comprobador). -/
theorem net_ok : checkNet pos Rx = true := by decide +kernel

/-- Pesos de la combinación con crecimiento lineal (cᵢ ≥ 1). -/
def c : Fin 4 → ℚ := fun _ => (1 : ℚ)

theorem growth_ok : checkGrowth pos c Rx = true := by decide +kernel

/-- θ₀ nominal (PEtab), en racionales exactos. -/
def θq : Fin 21 → ℚ := ![(11773 / 2500 : ℚ), (63 / 1000 : ℚ), (1 / 20 : ℚ), (303 / 400 : ℚ), (3917 / 10000 : ℚ), (643 / 10000 : ℚ), (4797 / 10000 : ℚ), (1237 / 2000 : ℚ), (161 / 500 : ℚ), (2967 / 500 : ℚ), (1 / 20 : ℚ), (1 / 20 : ℚ), (6079 / 10000 : ℚ), (61 / 125 : ℚ), (957 / 5000 : ℚ), (15283 / 10000 : ℚ), (1941 / 10000 : ℚ), (1 / 20 : ℚ), (5753 / 10000 : ℚ), (5157 / 10000 : ℚ), (2189 / 10000 : ℚ)]

theorem theta_ok : checkPosParams pos θq = true := by decide +kernel

/-- Condiciones iniciales nominales. -/
def xq : Fin 4 → ℚ := ![(9010000 : ℚ), (258 : ℚ), (0 : ℚ), (258 : ℚ)]

theorem x0_ok : checkNonneg xq = true := by decide +kernel

/-- **Teorema final, sin condiciones pendientes**: para todo T ≥ 0 la solución
nominal existe en [0, T], es ≥ 0, queda en el dominio, y la trayectoria es
diferenciable respecto a θ en θ₀. -/
def final := @network_final _ _ pos Rx net_ok c growth_ok θq theta_ok xq x0_ok

end Models.Zhao_QuantBiol2020

#print axioms Models.Zhao_QuantBiol2020.final
