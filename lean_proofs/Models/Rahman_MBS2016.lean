import StrictNetwork

/-! Modelo `Rahman_MBS2016` (forma de red, positividad estricta), traducido
automáticamente de SBML por `certificados/sbml_to_lean.py`. No editar a mano.

Estados (7): susceptible, infected_normal, infected_moderate, infected_weak, treated_normal, treated_moderate, treated_weak

Σ (dato inicial > 0, permanecen estrictamente positivas): susceptible, infected_normal, infected_moderate, infected_weak

Parámetros estimados θ (9): infected_normal_transmission_rate_relative, infected_moderate_transmission_rate, infected_weak_transmission_rate_relative, infected_weak_treatment_rate, infected_normal_worsen_rate, infected_moderate_worsen_rate, treated_moderate_improve_rate, treated_weak_improve_rate, behavioural_change_rate
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck KineticNetwork StrictNetwork

namespace Models.Rahman_MBS2016

/-- Máscara de parámetros positivos (nominal > 0 o escala log). -/
def pos : Fin 9 → Bool := fun _ => true

/-- Cotas superiores de parámetros usadas (θⱼ ≤ q), comprobadas en θ₀ (`ub_ok`). -/
def ub : Fin 9 → Option ℚ × Option ℚ := fun _ => (none, none)

/-- Σ: especies con dato inicial nominal > 0. -/
def sx : Fin 7 → Bool := ![true, true, true, true, false, false, false]

/-- Términos de velocidad con su columna estequiométrica (19 términos). -/
def Rx : List (KExpr 7 9 × List (Fin 7 × ℚ)) := [
  ((KExpr.qconst (1032672 : ℚ)), [(0, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.div (KExpr.mul (KExpr.mul (KExpr.par 0) (KExpr.par 1)) (KExpr.var 1)) (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.var 0) (KExpr.var 1)) (KExpr.var 2)) (KExpr.var 3)) (KExpr.var 4)) (KExpr.var 5)) (KExpr.var 6))) (KExpr.exp (KExpr.mul (KExpr.mul (KExpr.qconst (-1 : ℚ)) (KExpr.par 8)) (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.var 1) (KExpr.var 2)) (KExpr.var 3)) (KExpr.var 4)) (KExpr.var 5)) (KExpr.var 6))))) (KExpr.var 0)), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.div (KExpr.mul (KExpr.par 1) (KExpr.var 2)) (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.var 0) (KExpr.var 1)) (KExpr.var 2)) (KExpr.var 3)) (KExpr.var 4)) (KExpr.var 5)) (KExpr.var 6))) (KExpr.exp (KExpr.mul (KExpr.mul (KExpr.qconst (-1 : ℚ)) (KExpr.par 8)) (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.var 1) (KExpr.var 2)) (KExpr.var 3)) (KExpr.var 4)) (KExpr.var 5)) (KExpr.var 6))))) (KExpr.var 0)), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.div (KExpr.mul (KExpr.mul (KExpr.par 2) (KExpr.par 1)) (KExpr.var 3)) (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.var 0) (KExpr.var 1)) (KExpr.var 2)) (KExpr.var 3)) (KExpr.var 4)) (KExpr.var 5)) (KExpr.var 6))) (KExpr.exp (KExpr.mul (KExpr.mul (KExpr.qconst (-1 : ℚ)) (KExpr.par 8)) (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.var 1) (KExpr.var 2)) (KExpr.var 3)) (KExpr.var 4)) (KExpr.var 5)) (KExpr.var 6))))) (KExpr.var 0)), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.div (KExpr.mul (KExpr.mul (KExpr.qconst (1 / 25 : ℚ)) (KExpr.par 1)) (KExpr.var 4)) (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.var 0) (KExpr.var 1)) (KExpr.var 2)) (KExpr.var 3)) (KExpr.var 4)) (KExpr.var 5)) (KExpr.var 6))) (KExpr.exp (KExpr.mul (KExpr.mul (KExpr.qconst (-1 : ℚ)) (KExpr.par 8)) (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.var 1) (KExpr.var 2)) (KExpr.var 3)) (KExpr.var 4)) (KExpr.var 5)) (KExpr.var 6))))) (KExpr.var 0)), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.div (KExpr.mul (KExpr.mul (KExpr.qconst (1 / 25 : ℚ)) (KExpr.par 1)) (KExpr.var 5)) (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.var 0) (KExpr.var 1)) (KExpr.var 2)) (KExpr.var 3)) (KExpr.var 4)) (KExpr.var 5)) (KExpr.var 6))) (KExpr.exp (KExpr.mul (KExpr.mul (KExpr.qconst (-1 : ℚ)) (KExpr.par 8)) (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.var 1) (KExpr.var 2)) (KExpr.var 3)) (KExpr.var 4)) (KExpr.var 5)) (KExpr.var 6))))) (KExpr.var 0)), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.div (KExpr.mul (KExpr.mul (KExpr.qconst (1 / 25 : ℚ)) (KExpr.par 1)) (KExpr.var 6)) (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.var 0) (KExpr.var 1)) (KExpr.var 2)) (KExpr.var 3)) (KExpr.var 4)) (KExpr.var 5)) (KExpr.var 6))) (KExpr.exp (KExpr.mul (KExpr.mul (KExpr.qconst (-1 : ℚ)) (KExpr.par 8)) (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.var 1) (KExpr.var 2)) (KExpr.var 3)) (KExpr.var 4)) (KExpr.var 5)) (KExpr.var 6))))) (KExpr.var 0)), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (18 / 625 : ℚ)) (KExpr.var 0)), [(0, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.par 4) (KExpr.var 1)), [(1, (-1 : ℚ)), (2, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (111 / 1250 : ℚ)) (KExpr.var 1)), [(1, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.par 5) (KExpr.var 2)), [(2, (-1 : ℚ)), (3, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (171 / 1250 : ℚ)) (KExpr.var 2)), [(2, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.par 3) (KExpr.var 3)), [(3, (-1 : ℚ)), (6, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (777 / 2500 : ℚ)) (KExpr.var 3)), [(3, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.par 6) (KExpr.var 5)), [(4, (1 : ℚ)), (5, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (51 / 1250 : ℚ)) (KExpr.var 4)), [(4, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.par 7) (KExpr.var 6)), [(5, (1 : ℚ)), (6, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (33 / 625 : ℚ)) (KExpr.var 5)), [(5, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (219 / 1250 : ℚ)) (KExpr.var 6)), [(6, (-1 : ℚ))])
]

/-- El campo del modelo: `Fᵢ = Σ_r coef_r(i) · V_r`. -/
def F : Fin 7 → KExpr 7 9 := netF Rx

/-- Dominio ⊇ región estricta, cuasi-positividad fuera de Σ y consumo proporcional
en Σ (Lean ejecuta el comprobador). -/
theorem net_ok : checkNetS pos ub sx Rx = true := by decide +kernel

/-- Pesos de la combinación con crecimiento lineal (cᵢ ≥ 1). -/
def c : Fin 7 → ℚ := fun _ => (1 : ℚ)

theorem growth_ok : checkGrowthS pos ub c Rx = true := by decide +kernel

/-- θ₀ nominal (PEtab), en racionales exactos. -/
def θq : Fin 9 → ℚ := ![(42747 / 100 : ℚ), (29273 / 10000000 : ℚ), (24824 / 25 : ℚ), (1 / 10000 : ℚ), (13309 / 20000 : ℚ), (79757 / 10000000 : ℚ), (3409 / 25000 : ℚ), (77557 / 100000 : ℚ), (669 / 5000000000 : ℚ)]

theorem theta_ok : checkPosParams pos θq = true := by decide +kernel

theorem ub_ok : checkUB ub θq = true := by decide +kernel

/-- Condición inicial x₀(θ). -/
def G : Fin 7 → KExpr 7 9 := ![
  (KExpr.qconst (17940000 : ℚ)),
  (KExpr.qconst (16300 : ℚ)),
  (KExpr.qconst (9000 : ℚ)),
  (KExpr.qconst (11000 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ))
]

theorem init_ok : checkInitS pos sx G = true := by decide +kernel

/-- **Teorema final, sin condiciones pendientes**: para todo T ≥ 0 la solución
nominal existe en [0, T], las especies de Σ permanecen > 0 y las demás ≥ 0, queda
en el dominio, y la trayectoria es diferenciable respecto a θ en θ₀. -/
def final := @strict_final_init _ _ pos ub sx Rx net_ok c growth_ok G init_ok θq theta_ok ub_ok

end Models.Rahman_MBS2016

#print axioms Models.Rahman_MBS2016.final
