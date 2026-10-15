import KineticNetwork

/-! Modelo `Bertozzi_PNAS2020` (forma de red), traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (3): I_, R_, S_

Parámetros estimados θ (0): 
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck KineticNetwork

namespace Models.Bertozzi_PNAS2020

/-- Máscara de parámetros positivos (nominal > 0 o escala log). -/
def pos : Fin 0 → Bool := ![]

/-- Términos de velocidad con su columna estequiométrica (2 términos). -/
def Rx : List (KExpr 3 0 × List (Fin 3 × ℚ)) := [
  ((KExpr.mul (KExpr.mul (KExpr.qconst (5000000000000001 / 500000000000000000 : ℚ)) (KExpr.var 0)) (KExpr.var 2)), [(0, (1 : ℚ)), (2, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 / 10 : ℚ)) (KExpr.var 0)), [(0, (-1 : ℚ)), (1, (1 : ℚ))])
]

/-- El campo del modelo: `Fᵢ = Σ_r coef_r(i) · V_r`. -/
def F : Fin 3 → KExpr 3 0 := netF Rx

/-- Dominio ⊇ ortante y cuasi-positividad (Lean ejecuta el comprobador). -/
theorem net_ok : checkNet pos Rx = true := by decide +kernel

/-- Pesos de la combinación con crecimiento lineal (cᵢ ≥ 1). -/
def c : Fin 3 → ℚ := fun _ => (1 : ℚ)

theorem growth_ok : checkGrowth pos c Rx = true := by decide +kernel

/-- θ₀ nominal (PEtab), en racionales exactos. -/
def θq : Fin 0 → ℚ := ![]

theorem theta_ok : checkPosParams pos θq = true := by decide +kernel

/-- Condiciones iniciales nominales. -/
def xq : Fin 3 → ℚ := ![(1 / 10 : ℚ), (0 : ℚ), (9 / 10 : ℚ)]

theorem x0_ok : checkNonneg xq = true := by decide +kernel

/-- **Teorema final, sin condiciones pendientes**: para todo T ≥ 0 la solución
nominal existe en [0, T], es ≥ 0, queda en el dominio, y la trayectoria es
diferenciable respecto a θ en θ₀. -/
def final := @network_final _ _ pos Rx net_ok c growth_ok θq theta_ok xq x0_ok

end Models.Bertozzi_PNAS2020

#print axioms Models.Bertozzi_PNAS2020.final
