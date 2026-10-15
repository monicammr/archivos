import RiccatiNetwork

/-! Modelo `Crauste_CellSystems2017` (forma de red, crecimiento cuadrático), traducido
automáticamente de SBML por `certificados/sbml_to_lean.py`. No editar a mano.

Estados (5): Naive, EarlyEffector, LateEffector, Memory, Pathogen

Parámetros estimados θ (12): delta_EL, delta_LM, delta_NE, mu_EE, mu_LE, mu_LL, mu_N, mu_P, mu_PE, mu_PL, rho_E, rho_P

Horizonte: T ≤ (1 : ℚ) (la cota de Riccati no da existencia global).
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck KineticNetwork RiccatiNetwork

namespace Models.Crauste_CellSystems2017

def pos : Fin 12 → Bool := fun _ => true

def Rx : List (KExpr 5 12 × List (Fin 5 × ℚ)) := [
  ((KExpr.mul (KExpr.var 0) (KExpr.par 6)), [(0, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.var 0) (KExpr.var 4)) (KExpr.par 2)), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.var 1) (KExpr.var 4)) (KExpr.par 10)), [(1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.npow (KExpr.var 1) 2) (KExpr.par 3)), [(1, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.var 1) (KExpr.par 0)), [(1, (-1 : ℚ)), (2, (1 : ℚ))]),
  ((KExpr.mul (KExpr.npow (KExpr.var 2) 2) (KExpr.par 5)), [(2, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.var 1) (KExpr.var 2)) (KExpr.par 4)), [(2, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.var 2) (KExpr.par 1)), [(2, (-1 : ℚ)), (3, (1 : ℚ))]),
  ((KExpr.mul (KExpr.npow (KExpr.var 4) 2) (KExpr.par 11)), [(4, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.var 1) (KExpr.var 4)) (KExpr.par 8)), [(4, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.var 2) (KExpr.var 4)) (KExpr.par 9)), [(4, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.var 4) (KExpr.par 7)), [(4, (-1 : ℚ))])
]

def F : Fin 5 → KExpr 5 12 := netF Rx

theorem net_ok : checkNet pos Rx = true := by decide +kernel

def θq : Fin 12 → ℚ := ![(517945937424841 / 1000000000000000 : ℚ), (22580636941607 / 1000000000000000 : ℚ), (5965393966801 / 500000000000000 : ℚ), (391359465940441 / 10000000000000000000 : ℚ), (100000000000007 / 1000000000000000000000000 : ℚ), (811520130499257 / 100000000000000000000 : ℚ), (184976826099781 / 250000000000000 : ℚ), (50000001761047 / 5000000000000000000 : ℚ), (70624362042397 / 500000000000000000000000 : ℚ), (363403086241783 / 10000000000000000000 : ℚ), (253707824502007 / 500000000000000 : ℚ), (63191146312751 / 500000000000000 : ℚ)]

theorem theta_ok : checkPosParams pos θq = true := by decide +kernel

def xq : Fin 5 → ℚ := ![(8090 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (1 : ℚ)]

theorem x0_ok : checkNonneg xq = true := by decide +kernel

/-- Pesos de la combinación `φ = Σ cᵢ xᵢ`. -/
def c : Fin 5 → ℚ := ![(1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (100000 : ℚ)]

/-- Horizonte `T_q = (1 : ℚ)`. -/
def Tq : ℚ := (1 : ℚ)

/-- Cota de Riccati `Σ cᵢ Fᵢ ≤ Q (φ + 1)²` y `1.1·Q·(φ₀ + 1)·T_q < 1`. -/
theorem riccati_ok : checkRiccati pos c θq xq Tq Rx = true := by decide +kernel

/-- **Teorema final, sin condiciones pendientes** para `0 ≤ T ≤ T_q`: la solución
nominal existe en [0, T], es ≥ 0, queda en el dominio, y la trayectoria es
diferenciable respecto a θ en θ₀. -/
def final := @riccati_final _ _ pos Rx net_ok c θq theta_ok xq x0_ok Tq riccati_ok

end Models.Crauste_CellSystems2017

#print axioms Models.Crauste_CellSystems2017.final
