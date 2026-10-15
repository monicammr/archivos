import StrictNetwork

/-! Modelo `Okuonghae_ChaosSolitonsFractals2020` (forma de red, positividad estricta), traducido
automáticamente de SBML por `certificados/sbml_to_lean.py`. No editar a mano.

Estados (8): susceptible, exposed, asymptomatic, symptomatic, detected, recovered, deceased, detected_cumulative

Σ (dato inicial > 0, permanecen estrictamente positivas): susceptible, exposed, asymptomatic, symptomatic, detected, detected_cumulative

Parámetros estimados θ (14): alpha, d_0, d_D, gamma_0, gamma_a, gamma_i, nu, psi, sigma, theta, asymptomatic_start, symptomatic_start, exposed_start, transmission_rate_effective
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck KineticNetwork StrictNetwork

namespace Models.Okuonghae_ChaosSolitonsFractals2020

/-- Máscara de parámetros positivos (nominal > 0 o escala log). -/
def pos : Fin 14 → Bool := fun _ => true

/-- Cotas superiores de parámetros usadas (θⱼ ≤ q), comprobadas en θ₀ (`ub_ok`). -/
def ub : Fin 14 → Option ℚ × Option ℚ := ![(none, none), (none, none), (none, none), (none, none), (none, none), (none, none), (none, some (1 : ℚ)), (none, none), (none, none), (none, none), (none, none), (none, none), (none, none), (none, none)]

/-- Σ: especies con dato inicial nominal > 0. -/
def sx : Fin 8 → Bool := ![true, true, true, true, true, false, false, true]

/-- Términos de velocidad con su columna estequiométrica (11 términos). -/
def Rx : List (KExpr 8 14 × List (Fin 8 × ℚ)) := [
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.par 13) (KExpr.qconst (1 / 5 : ℚ))) (KExpr.qconst (1 : ℚ))) (KExpr.mul (KExpr.par 0) (KExpr.var 2))) (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.var 2) (KExpr.var 1)) (KExpr.var 5)) (KExpr.var 0)) (KExpr.var 3)))) (KExpr.var 0)), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.par 13) (KExpr.qconst (1 / 5 : ℚ))) (KExpr.qconst (1 : ℚ))) (KExpr.var 3)) (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.var 2) (KExpr.var 1)) (KExpr.var 5)) (KExpr.var 0)) (KExpr.var 3)))) (KExpr.var 0)), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.par 8) (KExpr.sub (KExpr.qconst (1 : ℚ)) (KExpr.par 6))) (KExpr.var 1))), [(1, (-1 : ℚ)), (3, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.par 8) (KExpr.par 6)) (KExpr.var 1))), [(1, (-1 : ℚ)), (2, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 9)) (KExpr.var 2)), [(2, (-1 : ℚ)), (4, (1 : ℚ)), (7, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 4)) (KExpr.var 2)), [(2, (-1 : ℚ)), (5, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 7)) (KExpr.var 3)), [(3, (-1 : ℚ)), (4, (1 : ℚ)), (7, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 3)) (KExpr.var 3)), [(3, (-1 : ℚ)), (5, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 1)) (KExpr.var 3)), [(3, (-1 : ℚ)), (6, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 5)) (KExpr.var 4)), [(4, (-1 : ℚ)), (5, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 2)) (KExpr.var 4)), [(4, (-1 : ℚ)), (6, (1 : ℚ))])
]

/-- El campo del modelo: `Fᵢ = Σ_r coef_r(i) · V_r`. -/
def F : Fin 8 → KExpr 8 14 := netF Rx

/-- Dominio ⊇ región estricta, cuasi-positividad fuera de Σ y consumo proporcional
en Σ (Lean ejecuta el comprobador). -/
theorem net_ok : checkNetS pos ub sx Rx = true := by decide +kernel

/-- Pesos de la combinación con crecimiento lineal (cᵢ ≥ 1). -/
def c : Fin 8 → ℚ := fun _ => (1 : ℚ)

theorem growth_ok : checkGrowthS pos ub c Rx = true := by decide +kernel

/-- θ₀ nominal (PEtab), en racionales exactos. -/
def θq : Fin 14 → ℚ := ![(1 / 2 : ℚ), (3 / 200 : ℚ), (3 / 200 : ℚ), (6989 / 50000 : ℚ), (6989 / 50000 : ℚ), (6666667 / 100000000 : ℚ), (1 / 2 : ℚ), (27 / 2000 : ℚ), (1923077 / 10000000 : ℚ), (1 / 500000000000 : ℚ), (188 : ℚ), (212 : ℚ), (441 : ℚ), (1059 / 2500 : ℚ)]

theorem theta_ok : checkPosParams pos θq = true := by decide +kernel

theorem ub_ok : checkUB ub θq = true := by decide +kernel

/-- Condición inicial x₀(θ). -/
def G : Fin 8 → KExpr 8 14 := ![
  (KExpr.qconst (14367982 : ℚ)),
  (KExpr.par 12),
  (KExpr.par 10),
  (KExpr.par 11),
  (KExpr.qconst (1 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (1 : ℚ))
]

theorem init_ok : checkInitS pos sx G = true := by decide +kernel

/-- **Teorema final, sin condiciones pendientes**: para todo T ≥ 0 la solución
nominal existe en [0, T], las especies de Σ permanecen > 0 y las demás ≥ 0, queda
en el dominio, y la trayectoria es diferenciable respecto a θ en θ₀. -/
def final := @strict_final_init _ _ pos ub sx Rx net_ok c growth_ok G init_ok θq theta_ok ub_ok

end Models.Okuonghae_ChaosSolitonsFractals2020

#print axioms Models.Okuonghae_ChaosSolitonsFractals2020.final
