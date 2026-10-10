import StrictNetwork

/-! Modelo `Elowitz_Nature2000` (forma de red, positividad estricta), traducido
automáticamente de SBML por `certificados/sbml_to_lean.py`. No editar a mano.

Estados (8): X_protein, Y_protein, Z_protein, GFP, X_mRNA, Y_mRNA, Z_mRNA, GFP_mRNA

Σ (dato inicial > 0, permanecen estrictamente positivas): X_protein, Y_protein, Z_protein, GFP, X_mRNA, Y_mRNA, Z_mRNA, GFP_mRNA

Parámetros estimados θ (18): KM, eff, eff_GFP, init_GFP, init_GFP_mRNA, init_X_mRNA, init_X_protein, init_Y_mRNA, init_Y_protein, init_Z_mRNA, init_Z_protein, n_Hill, tau_mRNA, tau_mRNA_GFP, tau_prot, tau_prot_GFP, tps_active, tps_repr
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck KineticNetwork StrictNetwork

namespace Models.Elowitz_Nature2000

/-- Máscara de parámetros positivos (nominal > 0 o escala log). -/
def pos : Fin 18 → Bool := fun _ => true

/-- Cotas superiores de parámetros usadas (θⱼ ≤ q), comprobadas en θ₀ (`ub_ok`). -/
def ub : Fin 18 → Option ℚ × Option ℚ := fun _ => (none, none)

/-- Σ: especies con dato inicial nominal > 0. -/
def sx : Fin 8 → Bool := fun _ => true

/-- Términos de velocidad con su columna estequiométrica (18 términos). -/
def Rx : List (KExpr 8 18 × List (Fin 8 × ℚ)) := [
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 4) (KExpr.par 1)) (KExpr.par 12))), [(0, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 0) (KExpr.log (KExpr.qconst (2 : ℚ)))) (KExpr.par 14))), [(0, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 5) (KExpr.par 1)) (KExpr.par 12))), [(1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 1) (KExpr.log (KExpr.qconst (2 : ℚ)))) (KExpr.par 14))), [(1, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 6) (KExpr.par 1)) (KExpr.par 12))), [(2, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 2) (KExpr.log (KExpr.qconst (2 : ℚ)))) (KExpr.par 14))), [(2, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 7) (KExpr.par 2)) (KExpr.par 13))), [(3, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 3) (KExpr.log (KExpr.qconst (2 : ℚ)))) (KExpr.par 15))), [(3, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.qconst (60 : ℚ)) (KExpr.par 17)) (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.var 0))))) (KExpr.add (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.par 0)))) (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.var 0))))))), [(3, (1 : ℚ)), (5, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.par 0)))) (KExpr.mul (KExpr.qconst (60 : ℚ)) (KExpr.par 16))) (KExpr.add (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.par 0)))) (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.var 0))))))), [(3, (1 : ℚ)), (5, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 4) (KExpr.log (KExpr.qconst (2 : ℚ)))) (KExpr.par 12))), [(4, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.qconst (60 : ℚ)) (KExpr.par 17)) (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.var 2))))) (KExpr.add (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.par 0)))) (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.var 2))))))), [(4, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.par 0)))) (KExpr.mul (KExpr.qconst (60 : ℚ)) (KExpr.par 16))) (KExpr.add (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.par 0)))) (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.var 2))))))), [(4, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 5) (KExpr.log (KExpr.qconst (2 : ℚ)))) (KExpr.par 12))), [(5, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 6) (KExpr.log (KExpr.qconst (2 : ℚ)))) (KExpr.par 12))), [(6, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.qconst (60 : ℚ)) (KExpr.par 17)) (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.var 1))))) (KExpr.add (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.par 0)))) (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.var 1))))))), [(6, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.par 0)))) (KExpr.mul (KExpr.qconst (60 : ℚ)) (KExpr.par 16))) (KExpr.add (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.par 0)))) (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.var 1))))))), [(6, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 7) (KExpr.log (KExpr.qconst (2 : ℚ)))) (KExpr.par 13))), [(7, (-1 : ℚ))])
]

/-- El campo del modelo: `Fᵢ = Σ_r coef_r(i) · V_r`. -/
def F : Fin 8 → KExpr 8 18 := netF Rx

/-- Dominio ⊇ región estricta, cuasi-positividad fuera de Σ y consumo proporcional
en Σ (Lean ejecuta el comprobador). -/
theorem net_ok : checkNetS pos ub sx Rx = true := by decide +kernel

/-- Pesos de la combinación con crecimiento lineal (cᵢ ≥ 1). -/
def c : Fin 8 → ℚ := fun _ => (1 : ℚ)

theorem growth_ok : checkGrowthS pos ub c Rx = true := by decide +kernel

/-- θ₀ nominal (PEtab), en racionales exactos. -/
def θq : Fin 18 → ℚ := ![(100013184764193 / 10000000000000000000 : ℚ), (30159280362287 / 1000000000000000 : ℚ), (976060985483 / 500000000000000 : ℚ), (42339624779523 / 1250000000000000000 : ℚ), (3285893444739 / 25000000000 : ℚ), (255665758135759 / 100000000000000 : ℚ), (308087735629583 / 10000000000000 : ℚ), (199999989198173 / 200000000000 : ℚ), (818268062901 / 1000000000000000 : ℚ), (193670294497273 / 10000000000000 : ℚ), (994381959318229 / 1000000000000 : ℚ), (2378977618031 / 1562500000000 : ℚ), (63124122853861 / 5000000000000 : ℚ), (404064377463 / 1000000000000000 : ℚ), (267963263735031 / 50000000000000 : ℚ), (11239260014609 / 156250000000 : ℚ), (9566859238203 / 15625000000000 : ℚ), (50000000000441 / 5000000000000000000 : ℚ)]

theorem theta_ok : checkPosParams pos θq = true := by decide +kernel

theorem ub_ok : checkUB ub θq = true := by decide +kernel

/-- Condición inicial x₀(θ). -/
def G : Fin 8 → KExpr 8 18 := ![
  (KExpr.par 6),
  (KExpr.par 8),
  (KExpr.par 10),
  (KExpr.par 3),
  (KExpr.par 5),
  (KExpr.par 7),
  (KExpr.par 9),
  (KExpr.par 4)
]

theorem init_ok : checkInitS pos sx G = true := by decide +kernel

/-- **Teorema final, sin condiciones pendientes**: para todo T ≥ 0 la solución
nominal existe en [0, T], las especies de Σ permanecen > 0 y las demás ≥ 0, queda
en el dominio, y la trayectoria es diferenciable respecto a θ en θ₀. -/
def final := @strict_final_init _ _ pos ub sx Rx net_ok c growth_ok G init_ok θq theta_ok ub_ok

end Models.Elowitz_Nature2000

#print axioms Models.Elowitz_Nature2000.final
