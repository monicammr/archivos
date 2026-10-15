import StrictNetwork

/-! Modelo `Armistead_CellDeathDis2024` (forma de red, positividad estricta), traducido
automáticamente de SBML por `certificados/sbml_to_lean.py`. No editar a mano.

Estados (4): Cer, Sphingo, S1P, Sphinga

Σ (dato inicial > 0, permanecen estrictamente positivas): Cer, Sphingo, S1P, Sphinga

Parámetros estimados θ (10): k00, k0, k_d, k1, k2, k3, k4, k5, alpha_hai1a, alpha_cer
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck KineticNetwork StrictNetwork

namespace Models.Armistead_CellDeathDis2024

/-- Máscara de parámetros positivos (nominal > 0 o escala log). -/
def pos : Fin 10 → Bool := ![true, true, true, true, true, true, true, true, true, false]

/-- Cotas superiores de parámetros usadas (θⱼ ≤ q), comprobadas en θ₀ (`ub_ok`). -/
def ub : Fin 10 → Option ℚ × Option ℚ := ![(none, none), (none, none), (none, none), (none, none), (none, none), (none, none), (none, none), (none, none), (none, some (1 : ℚ)), (some (-1 : ℚ), none)]

/-- Σ: especies con dato inicial nominal > 0. -/
def sx : Fin 4 → Bool := fun _ => true

/-- Términos de velocidad con su columna estequiométrica (8 términos). -/
def Rx : List (KExpr 4 10 × List (Fin 4 × ℚ)) := [
  ((KExpr.mul (KExpr.par 1) (KExpr.var 3)), [(0, (1 : ℚ)), (3, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.par 3) (KExpr.var 0)), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.par 4) (KExpr.var 1)), [(0, (1 : ℚ)), (1, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.par 2) (KExpr.var 0)), [(0, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.par 5) (KExpr.sub (KExpr.qconst (1 : ℚ)) (KExpr.par 8))) (KExpr.var 1)), [(1, (-1 : ℚ)), (2, (1 : ℚ))]),
  ((KExpr.mul (KExpr.par 6) (KExpr.var 2)), [(1, (1 : ℚ)), (2, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.par 7) (KExpr.var 2)), [(2, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.par 0) (KExpr.add (KExpr.qconst (1 : ℚ)) (KExpr.par 9))), [(3, (1 : ℚ))])
]

/-- El campo del modelo: `Fᵢ = Σ_r coef_r(i) · V_r`. -/
def F : Fin 4 → KExpr 4 10 := netF Rx

/-- Dominio ⊇ región estricta, cuasi-positividad fuera de Σ y consumo proporcional
en Σ (Lean ejecuta el comprobador). -/
theorem net_ok : checkNetS pos ub sx Rx = true := by decide +kernel

/-- Pesos de la combinación con crecimiento lineal (cᵢ ≥ 1). -/
def c : Fin 4 → ℚ := fun _ => (1 : ℚ)

theorem growth_ok : checkGrowthS pos ub c Rx = true := by decide +kernel

/-- θ₀ nominal (PEtab), en racionales exactos. -/
def θq : Fin 10 → ℚ := ![(2380825042587659 / 10000000000000000 : ℚ), (2499999819287869 / 2500000000000 : ℚ), (4533863155477237 / 5000000000000000 : ℚ), (376410406421301 / 1250000000000000 : ℚ), (1249996546840289 / 1250000000000 : ℚ), (10000471839981 / 10000000000000000 : ℚ), (23616885412588227 / 10000000000000000 : ℚ), (10007718402407 / 10000000000000000 : ℚ), (1250000134696183 / 2500000000000000 : ℚ), (-81873449517767 / 250000000000000 : ℚ)]

theorem theta_ok : checkPosParams pos θq = true := by decide +kernel

theorem ub_ok : checkUB ub θq = true := by decide +kernel

/-- Condición inicial x₀(θ). -/
def G : Fin 4 → KExpr 4 10 := ![
  (KExpr.qconst (247 / 250 : ℚ)),
  (KExpr.qconst (79 / 200000 : ℚ)),
  (KExpr.qconst (1551 / 1000 : ℚ)),
  (KExpr.qconst (183 / 250000 : ℚ))
]

theorem init_ok : checkInitS pos sx G = true := by decide +kernel

/-- **Teorema final, sin condiciones pendientes**: para todo T ≥ 0 la solución
nominal existe en [0, T], las especies de Σ permanecen > 0 y las demás ≥ 0, queda
en el dominio, y la trayectoria es diferenciable respecto a θ en θ₀. -/
def final := @strict_final_init _ _ pos ub sx Rx net_ok c growth_ok G init_ok θq theta_ok ub_ok

end Models.Armistead_CellDeathDis2024

#print axioms Models.Armistead_CellDeathDis2024.final
