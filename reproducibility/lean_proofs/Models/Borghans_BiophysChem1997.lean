import StrictNetwork

/-! Modelo `Borghans_BiophysChem1997` (forma de red, positividad estricta), traducido
automáticamente de SBML por `certificados/sbml_to_lean.py`. No editar a mano.

Estados (3): Z_state, Y_state, A_state

Σ (dato inicial > 0, permanecen estrictamente positivas): Z_state, Y_state, A_state

Parámetros estimados θ (20): K2, K_par, Ka, Kd, Kf, Kp, Ky, Kz, Vd, Vm2, Vm3, Vp, beta_par, epsilon_par, init_A_state, init_Y_state, init_Z_state, n_par, v0, v1
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck KineticNetwork StrictNetwork

namespace Models.Borghans_BiophysChem1997

/-- Máscara de parámetros positivos (nominal > 0 o escala log). -/
def pos : Fin 20 → Bool := fun _ => true

/-- Cotas superiores de parámetros usadas (θⱼ ≤ q), comprobadas en θ₀ (`ub_ok`). -/
def ub : Fin 20 → Option ℚ × Option ℚ := fun _ => (none, none)

/-- Σ: especies con dato inicial nominal > 0. -/
def sx : Fin 3 → Bool := fun _ => true

/-- Términos de velocidad con su columna estequiométrica (9 términos). -/
def Rx : List (KExpr 3 20 × List (Fin 3 × ℚ)) := [
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 18)), [(0, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 12) (KExpr.par 19))), [(0, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.par 9) (KExpr.npow (KExpr.var 0) 2)) (KExpr.add (KExpr.npow (KExpr.par 0) 2) (KExpr.npow (KExpr.var 0) 2)))), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.npow (KExpr.var 2) 4) (KExpr.par 10)) (KExpr.npow (KExpr.var 1) 2)) (KExpr.npow (KExpr.var 0) 4)) (KExpr.mul (KExpr.mul (KExpr.add (KExpr.npow (KExpr.var 2) 4) (KExpr.npow (KExpr.par 2) 4)) (KExpr.add (KExpr.npow (KExpr.par 6) 2) (KExpr.npow (KExpr.var 1) 2))) (KExpr.add (KExpr.npow (KExpr.par 7) 4) (KExpr.npow (KExpr.var 0) 4))))), [(0, (1 : ℚ)), (1, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 4)) (KExpr.var 1)), [(0, (1 : ℚ)), (1, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 1)) (KExpr.var 0)), [(0, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 11)) (KExpr.par 12)), [(2, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.npow (KExpr.var 2) 2) (KExpr.par 8)) (KExpr.exp (KExpr.mul (KExpr.par 17) (KExpr.log (KExpr.var 0))))) (KExpr.mul (KExpr.add (KExpr.exp (KExpr.mul (KExpr.par 17) (KExpr.log (KExpr.par 3)))) (KExpr.exp (KExpr.mul (KExpr.par 17) (KExpr.log (KExpr.var 0))))) (KExpr.add (KExpr.npow (KExpr.var 2) 2) (KExpr.npow (KExpr.par 5) 2))))), [(2, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 2)) (KExpr.par 13)), [(2, (-1 : ℚ))])
]

/-- El campo del modelo: `Fᵢ = Σ_r coef_r(i) · V_r`. -/
def F : Fin 3 → KExpr 3 20 := netF Rx

/-- Dominio ⊇ región estricta, cuasi-positividad fuera de Σ y consumo proporcional
en Σ (Lean ejecuta el comprobador). -/
theorem net_ok : checkNetS pos ub sx Rx = true := by decide +kernel

/-- Pesos de la combinación con crecimiento lineal (cᵢ ≥ 1). -/
def c : Fin 3 → ℚ := fun _ => (1 : ℚ)

theorem growth_ok : checkGrowthS pos ub c Rx = true := by decide +kernel

/-- θ₀ nominal (PEtab), en racionales exactos. -/
def θq : Fin 20 → ℚ := ![(1998971160313 / 20000000000000 : ℚ), (22824160918853 / 2000000000000 : ℚ), (197593940310187 / 1000000000000000 : ℚ), (196248756053737 / 500000000000000 : ℚ), (28448742090309 / 25000000000000 : ℚ), (124570933024559 / 125000000000000 : ℚ), (12522758314267 / 62500000000000 : ℚ), (4739899172773 / 15625000000000 : ℚ), (116092412572247 / 1250000000000 : ℚ), (29828497819689 / 4000000000000 : ℚ), (28378156103169 / 1250000000000 : ℚ), (275685784345759 / 100000000000000 : ℚ), (112395230256787 / 100000000000000 : ℚ), (40808048826547 / 250000000000000 : ℚ), (24999999999999 / 25000000000000 : ℚ), (999348084438687 / 1000000000000000 : ℚ), (2747516388297 / 31250000000000 : ℚ), (41025144127497 / 10000000000000 : ℚ), (231778715779187 / 100000000000000 : ℚ), (100488755696677 / 100000000000000 : ℚ)]

theorem theta_ok : checkPosParams pos θq = true := by decide +kernel

theorem ub_ok : checkUB ub θq = true := by decide +kernel

/-- Condición inicial x₀(θ). -/
def G : Fin 3 → KExpr 3 20 := ![
  (KExpr.par 16),
  (KExpr.par 15),
  (KExpr.par 14)
]

theorem init_ok : checkInitS pos sx G = true := by decide +kernel

/-- **Teorema final, sin condiciones pendientes**: para todo T ≥ 0 la solución
nominal existe en [0, T], las especies de Σ permanecen > 0 y las demás ≥ 0, queda
en el dominio, y la trayectoria es diferenciable respecto a θ en θ₀. -/
def final := @strict_final_init _ _ pos ub sx Rx net_ok c growth_ok G init_ok θq theta_ok ub_ok

end Models.Borghans_BiophysChem1997

#print axioms Models.Borghans_BiophysChem1997.final
