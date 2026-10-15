import KineticNetwork

/-! Modelo `Bruno_JExpBot2016` (forma de red), traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (7): bcar, bcry, b10, bio, ohb10, ohbio, zea

Parámetros estimados θ (6): k5, kb1, kb2, kc1, kc2, kc4
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck KineticNetwork

namespace Models.Bruno_JExpBot2016

/-- Máscara de parámetros positivos (nominal > 0 o escala log). -/
def pos : Fin 6 → Bool := fun _ => true

/-- Términos de velocidad con su columna estequiométrica (6 términos). -/
def Rx : List (KExpr 7 6 × List (Fin 7 × ℚ)) := [
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 0)) (KExpr.par 1)) (KExpr.qconst (521817105884857 / 1000000000000000 : ℚ))), [(0, (-1 : ℚ)), (2, (1 : ℚ)), (3, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 1)) (KExpr.par 3)) (KExpr.qconst (521817105884857 / 1000000000000000 : ℚ))), [(1, (-1 : ℚ)), (2, (1 : ℚ)), (5, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 1)) (KExpr.par 4)) (KExpr.qconst (521817105884857 / 1000000000000000 : ℚ))), [(1, (-1 : ℚ)), (3, (1 : ℚ)), (4, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 2)) (KExpr.par 2)) (KExpr.qconst (521817105884857 / 1000000000000000 : ℚ))), [(2, (-1 : ℚ)), (3, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 5)) (KExpr.qconst (521817105884857 / 1000000000000000 : ℚ))) (KExpr.var 4)), [(4, (-1 : ℚ)), (5, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 0)) (KExpr.qconst (521817105884857 / 1000000000000000 : ℚ))) (KExpr.var 6)), [(4, (1 : ℚ)), (5, (1 : ℚ)), (6, (-1 : ℚ))])
]

/-- El campo del modelo: `Fᵢ = Σ_r coef_r(i) · V_r`. -/
def F : Fin 7 → KExpr 7 6 := netF Rx

/-- Dominio ⊇ ortante y cuasi-positividad (Lean ejecuta el comprobador). -/
theorem net_ok : checkNet pos Rx = true := by decide +kernel

/-- Pesos de la combinación con crecimiento lineal (cᵢ ≥ 1). -/
def c : Fin 7 → ℚ := fun _ => (1 : ℚ)

theorem growth_ok : checkGrowth pos c Rx = true := by decide +kernel

/-- θ₀ nominal (PEtab), en racionales exactos. -/
def θq : Fin 6 → ℚ := ![(3086673219173 / 1000000000000000 : ℚ), (16628409992721 / 1000000000000000 : ℚ), (5843831819271 / 1000000000000000 : ℚ), (839412621137 / 500000000000000 : ℚ), (6975989070463 / 1000000000000000 : ℚ), (1216540179839 / 200000000000000 : ℚ)]

theorem theta_ok : checkPosParams pos θq = true := by decide +kernel

/-- Condiciones iniciales nominales. -/
def xq : Fin 7 → ℚ := ![(325673310603827 / 100000000000000 : ℚ), (325673310603827 / 100000000000000 : ℚ), (325673310603827 / 100000000000000 : ℚ), (0 : ℚ), (325673310603827 / 100000000000000 : ℚ), (0 : ℚ), (325673310603827 / 100000000000000 : ℚ)]

theorem x0_ok : checkNonneg xq = true := by decide +kernel

/-- **Teorema final, sin condiciones pendientes**: para todo T ≥ 0 la solución
nominal existe en [0, T], es ≥ 0, queda en el dominio, y la trayectoria es
diferenciable respecto a θ en θ₀. -/
def final := @network_final _ _ pos Rx net_ok c growth_ok θq theta_ok xq x0_ok

end Models.Bruno_JExpBot2016

#print axioms Models.Bruno_JExpBot2016.final
