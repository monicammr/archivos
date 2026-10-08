import KineticNetwork

/-! Modelo `Brannmark_JBC2010` (forma de red), traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (9): IR, IRins, IRp, IRiP, IRi, IRS, IRSiP, X, Xp

Parámetros estimados θ (15): k1a, k1aBasic, k1b, k1c, k1d, k1e, k1f, k1g, k1r, k21, k22, k3, k_IRSiP_DosR, km2, km3
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck KineticNetwork

namespace Models.Brannmark_JBC2010

/-- Máscara de parámetros positivos (nominal > 0 o escala log). -/
def pos : Fin 15 → Bool := ![true, true, true, true, true, true, true, true, true, true, true, true, true, true, true]

/-- Términos de velocidad con su columna estequiométrica (14 términos). -/
def Rx : List (KExpr 9 15 × List (Fin 9 × ℚ)) := [
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.par 1))), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.qconst (3 / 10 : ℚ)) (KExpr.qconst (1 : ℚ)))) (KExpr.par 0))), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 1)) (KExpr.par 2)), [(0, (1 : ℚ)), (1, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 2)) (KExpr.par 7)), [(0, (1 : ℚ)), (2, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 4)) (KExpr.par 8)), [(0, (1 : ℚ)), (4, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 1)) (KExpr.par 3)), [(1, (-1 : ℚ)), (2, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 2)) (KExpr.par 4)), [(2, (-1 : ℚ)), (3, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 3)) (KExpr.par 5)), [(3, (-1 : ℚ)), (4, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 3)) (KExpr.div (KExpr.mul (KExpr.var 8) (KExpr.par 6)) (KExpr.add (KExpr.var 8) (KExpr.qconst (1 : ℚ))))), [(3, (-1 : ℚ)), (4, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 5)) (KExpr.par 9)) (KExpr.var 2)), [(5, (-1 : ℚ)), (6, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 5)) (KExpr.par 9)) (KExpr.mul (KExpr.var 3) (KExpr.par 10))), [(5, (-1 : ℚ)), (6, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 6)) (KExpr.par 13)), [(5, (1 : ℚ)), (6, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 6)) (KExpr.var 7)) (KExpr.par 11)), [(7, (-1 : ℚ)), (8, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 8)) (KExpr.par 14)), [(7, (1 : ℚ)), (8, (-1 : ℚ))])
]

/-- El campo del modelo: `Fᵢ = Σ_r coef_r(i) · V_r`. -/
def F : Fin 9 → KExpr 9 15 := netF Rx

/-- Dominio ⊇ ortante y cuasi-positividad (Lean ejecuta el comprobador). -/
theorem net_ok : checkNet pos Rx = true := by decide +kernel

/-- Pesos de la combinación con crecimiento lineal (cᵢ ≥ 1). -/
def c : Fin 9 → ℚ := ![(1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ)]

theorem growth_ok : checkGrowth pos c Rx = true := by decide +kernel

/-- θ₀ nominal (PEtab), en racionales exactos. -/
def θq : Fin 15 → ℚ := ![(177219477727669 / 1000000000000000 : ℚ), (392767904337 / 1000000000000000 : ℚ), (174695978547559 / 1000000000000000 : ℚ), (50857471885817 / 1000000000000000 : ℚ), (499999999999977 / 1000000000 : ℚ), (100000000000009 / 100000000000000000000 : ℚ), (1562499975013 / 3125000 : ℚ), (17293765495871 / 10000000000 : ℚ), (26696391080189 / 1000000000000000 : ℚ), (105119082752209 / 50000000000000 : ℚ), (1333671147959 / 2000000000 : ℚ), (494410392362901 / 10000000000000000000 : ℚ), (7588703588757 / 200000000000 : ℚ), (7248171355653 / 6250000000000 : ℚ), (83276500181357 / 200000000000000 : ℚ)]

theorem theta_ok : checkPosParams pos θq = true := by decide +kernel

/-- Condiciones iniciales nominales. -/
def xq : Fin 9 → ℚ := ![(994957642787569 / 100000000000000 : ℚ), (173972221725393 / 10000000000000000 : ℚ), (17629010620181 / 10000000000000000000000 : ℚ), (13948753269037 / 1250000000000000000 : ℚ), (330151891862681 / 10000000000000000 : ℚ), (986699348701367 / 100000000000000 : ℚ), (4156453530823 / 31250000000000 : ℚ), (999984199487351 / 100000000000000 : ℚ), (4937660203059 / 31250000000000000 : ℚ)]

theorem x0_ok : checkNonneg xq = true := by decide +kernel

/-- **Teorema final, sin condiciones pendientes**: para todo T ≥ 0 la solución
nominal existe en [0, T], es ≥ 0, queda en el dominio, y la trayectoria es
diferenciable respecto a θ en θ₀. -/
def final := @network_final _ _ pos Rx net_ok c growth_ok θq theta_ok xq x0_ok

end Models.Brannmark_JBC2010

#print axioms Models.Brannmark_JBC2010.final
