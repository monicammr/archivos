import KineticNetwork

/-! Modelo `Blasi_CellSystems2016` (forma de red), traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (16): x_0ac, x_k8, x_k5, x_k12, x_k16, x_k5k8, x_k5k12, x_k5k16, x_k8k12, x_k8k16, x_k12k16, x_k5k8k12, x_k5k8k16, x_k5k12k16, x_k8k12k16, x_4ac

Parámetros estimados θ (8): a_basal, a_k8, a_k5_k5k12, a_k12_k5k12, a_k16_k12k16, a_k5k12_k5k8k12, a_k12k16_k8k12k16, a_k8k12k16_4ac
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck KineticNetwork

namespace Models.Blasi_CellSystems2016

/-- Máscara de parámetros positivos (nominal > 0 o escala log). -/
def pos : Fin 8 → Bool := ![true, true, true, true, true, true, true, true]

/-- Términos de velocidad con su columna estequiométrica (36 términos). -/
def Rx : List (KExpr 16 8 × List (Fin 16 × ℚ)) := [
  ((KExpr.mul (KExpr.par 0) (KExpr.var 0)), [(0, (-3 : ℚ)), (2, (1 : ℚ)), (3, (1 : ℚ)), (4, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 2)), [(0, (1 : ℚ)), (2, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.par 1) (KExpr.var 0)), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 1)), [(0, (1 : ℚ)), (1, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 3)), [(0, (1 : ℚ)), (3, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 4)), [(0, (1 : ℚ)), (4, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.par 0) (KExpr.var 1)), [(1, (-3 : ℚ)), (5, (1 : ℚ)), (8, (1 : ℚ)), (9, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 5)), [(1, (1 : ℚ)), (2, (1 : ℚ)), (5, (-2 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 8)), [(1, (1 : ℚ)), (3, (1 : ℚ)), (8, (-2 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 9)), [(1, (1 : ℚ)), (4, (1 : ℚ)), (9, (-2 : ℚ))]),
  ((KExpr.mul (KExpr.par 0) (KExpr.var 2)), [(2, (-2 : ℚ)), (5, (1 : ℚ)), (7, (1 : ℚ))]),
  ((KExpr.mul (KExpr.par 2) (KExpr.var 2)), [(2, (-1 : ℚ)), (6, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 6)), [(2, (1 : ℚ)), (3, (1 : ℚ)), (6, (-2 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 7)), [(2, (1 : ℚ)), (4, (1 : ℚ)), (7, (-2 : ℚ))]),
  ((KExpr.mul (KExpr.par 3) (KExpr.var 3)), [(3, (-1 : ℚ)), (6, (1 : ℚ))]),
  ((KExpr.mul (KExpr.par 0) (KExpr.var 3)), [(3, (-2 : ℚ)), (8, (1 : ℚ)), (10, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 10)), [(3, (1 : ℚ)), (4, (1 : ℚ)), (10, (-2 : ℚ))]),
  ((KExpr.mul (KExpr.par 0) (KExpr.var 4)), [(4, (-2 : ℚ)), (7, (1 : ℚ)), (9, (1 : ℚ))]),
  ((KExpr.mul (KExpr.par 4) (KExpr.var 4)), [(4, (-1 : ℚ)), (10, (1 : ℚ))]),
  ((KExpr.mul (KExpr.par 0) (KExpr.var 5)), [(5, (-2 : ℚ)), (11, (1 : ℚ)), (12, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 11)), [(5, (1 : ℚ)), (6, (1 : ℚ)), (8, (1 : ℚ)), (11, (-3 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 12)), [(5, (1 : ℚ)), (7, (1 : ℚ)), (9, (1 : ℚ)), (12, (-3 : ℚ))]),
  ((KExpr.mul (KExpr.par 5) (KExpr.var 6)), [(6, (-1 : ℚ)), (11, (1 : ℚ))]),
  ((KExpr.mul (KExpr.par 0) (KExpr.var 6)), [(6, (-1 : ℚ)), (13, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 13)), [(6, (1 : ℚ)), (7, (1 : ℚ)), (10, (1 : ℚ)), (13, (-3 : ℚ))]),
  ((KExpr.mul (KExpr.par 0) (KExpr.var 7)), [(7, (-2 : ℚ)), (12, (1 : ℚ)), (13, (1 : ℚ))]),
  ((KExpr.mul (KExpr.par 0) (KExpr.var 8)), [(8, (-2 : ℚ)), (11, (1 : ℚ)), (14, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 14)), [(8, (1 : ℚ)), (9, (1 : ℚ)), (10, (1 : ℚ)), (14, (-3 : ℚ))]),
  ((KExpr.mul (KExpr.par 0) (KExpr.var 9)), [(9, (-2 : ℚ)), (12, (1 : ℚ)), (14, (1 : ℚ))]),
  ((KExpr.mul (KExpr.par 0) (KExpr.var 10)), [(10, (-1 : ℚ)), (13, (1 : ℚ))]),
  ((KExpr.mul (KExpr.par 6) (KExpr.var 10)), [(10, (-1 : ℚ)), (14, (1 : ℚ))]),
  ((KExpr.mul (KExpr.par 0) (KExpr.var 11)), [(11, (-1 : ℚ)), (15, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 15)), [(11, (1 : ℚ)), (12, (1 : ℚ)), (13, (1 : ℚ)), (14, (1 : ℚ)), (15, (-4 : ℚ))]),
  ((KExpr.mul (KExpr.par 0) (KExpr.var 12)), [(12, (-1 : ℚ)), (15, (1 : ℚ))]),
  ((KExpr.mul (KExpr.par 0) (KExpr.var 13)), [(13, (-1 : ℚ)), (15, (1 : ℚ))]),
  ((KExpr.mul (KExpr.par 7) (KExpr.var 14)), [(14, (-1 : ℚ)), (15, (1 : ℚ))])
]

/-- El campo del modelo: `Fᵢ = Σ_r coef_r(i) · V_r`. -/
def F : Fin 16 → KExpr 16 8 := netF Rx

/-- Dominio ⊇ ortante y cuasi-positividad (Lean ejecuta el comprobador). -/
theorem net_ok : checkNet pos Rx = true := by decide +kernel

/-- Pesos de la combinación con crecimiento lineal (cᵢ ≥ 1). -/
def c : Fin 16 → ℚ := ![(1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ)]

theorem growth_ok : checkGrowth pos c Rx = true := by decide +kernel

/-- θ₀ nominal (PEtab), en racionales exactos. -/
def θq : Fin 8 → ℚ := ![(13359999985371 / 200000000000000 : ℚ), (13649999998719 / 500000000000000 : ℚ), (6443750000779 / 3125000000000 : ℚ), (551899999917063 / 1000000000000000 : ℚ), (695899999206803 / 1000000000000000 : ℚ), (325299999788883 / 1000000000000000 : ℚ), (22054999994189 / 10000000000000 : ℚ), (359170000273213 / 100000000000000 : ℚ)]

theorem theta_ok : checkPosParams pos θq = true := by decide +kernel

/-- Condiciones iniciales nominales. -/
def xq : Fin 16 → ℚ := ![(1 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]

theorem x0_ok : checkNonneg xq = true := by decide +kernel

/-- **Teorema final, sin condiciones pendientes**: para todo T ≥ 0 la solución
nominal existe en [0, T], es ≥ 0, queda en el dominio, y la trayectoria es
diferenciable respecto a θ en θ₀. -/
def final := @network_final _ _ pos Rx net_ok c growth_ok θq theta_ok xq x0_ok

end Models.Blasi_CellSystems2016

#print axioms Models.Blasi_CellSystems2016.final
