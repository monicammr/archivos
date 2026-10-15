import KineticNetwork

/-! Modelo `Boehm_JProteomeRes2014` (forma de red), traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (9): STAT5A, STAT5B, pApB, pApA, pBpB, nucpApA, nucpApB, nucpBpB, τ (tiempo)

Parámetros estimados θ (6): Epo_degradation_BaF3, k_exp_hetero, k_exp_homo, k_imp_hetero, k_imp_homo, k_phos
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck KineticNetwork

namespace Models.Boehm_JProteomeRes2014

/-- Máscara de parámetros positivos (nominal > 0 o escala log). -/
def pos : Fin 6 → Bool := fun _ => true

/-- Términos de velocidad con su columna estequiométrica (10 términos). -/
def Rx : List (KExpr 9 6 × List (Fin 9 × ℚ)) := [
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (7 / 5 : ℚ)) (KExpr.mul (KExpr.qconst (1 / 8000000 : ℚ)) (KExpr.exp (KExpr.mul (KExpr.mul (KExpr.qconst (-1 : ℚ)) (KExpr.par 0)) (KExpr.var 8))))) (KExpr.npow (KExpr.var 0) 2)) (KExpr.par 5)), [(0, (-10 / 7 : ℚ)), (3, (5 / 7 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (7 / 5 : ℚ)) (KExpr.mul (KExpr.qconst (1 / 8000000 : ℚ)) (KExpr.exp (KExpr.mul (KExpr.mul (KExpr.qconst (-1 : ℚ)) (KExpr.par 0)) (KExpr.var 8))))) (KExpr.var 0)) (KExpr.var 1)) (KExpr.par 5)), [(0, (-5 / 7 : ℚ)), (1, (-5 / 7 : ℚ)), (2, (5 / 7 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (9 / 20 : ℚ)) (KExpr.par 2)) (KExpr.var 5)), [(0, (10 / 7 : ℚ)), (5, (-20 / 9 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (9 / 20 : ℚ)) (KExpr.par 1)) (KExpr.var 6)), [(0, (5 / 7 : ℚ)), (1, (5 / 7 : ℚ)), (6, (-20 / 9 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (7 / 5 : ℚ)) (KExpr.mul (KExpr.qconst (1 / 8000000 : ℚ)) (KExpr.exp (KExpr.mul (KExpr.mul (KExpr.qconst (-1 : ℚ)) (KExpr.par 0)) (KExpr.var 8))))) (KExpr.npow (KExpr.var 1) 2)) (KExpr.par 5)), [(1, (-10 / 7 : ℚ)), (4, (5 / 7 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (9 / 20 : ℚ)) (KExpr.par 2)) (KExpr.var 7)), [(1, (10 / 7 : ℚ)), (7, (-20 / 9 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (7 / 5 : ℚ)) (KExpr.par 3)) (KExpr.var 2)), [(2, (-5 / 7 : ℚ)), (6, (20 / 9 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (7 / 5 : ℚ)) (KExpr.par 4)) (KExpr.var 3)), [(3, (-5 / 7 : ℚ)), (5, (20 / 9 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (7 / 5 : ℚ)) (KExpr.par 4)) (KExpr.var 4)), [(4, (-5 / 7 : ℚ)), (7, (20 / 9 : ℚ))]),
  ((KExpr.qconst (1 : ℚ)), [(8, (1 : ℚ))])
]

/-- El campo del modelo: `Fᵢ = Σ_r coef_r(i) · V_r`. -/
def F : Fin 9 → KExpr 9 6 := netF Rx

/-- Dominio ⊇ ortante y cuasi-positividad (Lean ejecuta el comprobador). -/
theorem net_ok : checkNet pos Rx = true := by decide +kernel

/-- Pesos de la combinación con crecimiento lineal (cᵢ ≥ 1). -/
def c : Fin 9 → ℚ := fun _ => (1 : ℚ)

theorem growth_ok : checkGrowth pos c Rx = true := by decide +kernel

/-- θ₀ nominal (PEtab), en racionales exactos. -/
def θq : Fin 6 → ℚ := ![(26982514033029 / 1000000000000000 : ℚ), (25016993462877 / 2500000000000000000 : ℚ), (6170228086381 / 1000000000000000 : ℚ), (40919796117 / 2500000000000 : ℚ), (244373448506179 / 2500000000 : ℚ), (157665070195731 / 10000000000 : ℚ)]

theorem theta_ok : checkPosParams pos θq = true := by decide +kernel

/-- Condiciones iniciales nominales. -/
def xq : Fin 9 → ℚ := ![(7193339999999999 / 50000000000000 : ℚ), (6373320000000001 / 100000000000000 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]

theorem x0_ok : checkNonneg xq = true := by decide +kernel

/-- **Teorema final, sin condiciones pendientes**: para todo T ≥ 0 la solución
nominal existe en [0, T], es ≥ 0, queda en el dominio, y la trayectoria es
diferenciable respecto a θ en θ₀. -/
def final := @network_final _ _ pos Rx net_ok c growth_ok θq theta_ok xq x0_ok

end Models.Boehm_JProteomeRes2014

#print axioms Models.Boehm_JProteomeRes2014.final
