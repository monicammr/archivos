import KineticNetwork

/-! Modelo `Weber_BMC2015` (forma de red), traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (7): PKD, PKDDAGa, PI4K3B, PI4K3Ba, CERTERa, CERT, CERTTGNa

Parámetros estimados θ (26): a11, a12, a21, a22, a31, a32, a33, m11, m22, m31, m33, p11, p12, p13, p21, p22, p31, p32, p33, pu3, pu4, pu5, pu6, s12, s21, s31
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck KineticNetwork

namespace Models.Weber_BMC2015

/-- Máscara de parámetros positivos (nominal > 0 o escala log). -/
def pos : Fin 26 → Bool := ![true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true]

/-- Términos de velocidad con su columna estequiométrica (18 términos). -/
def Rx : List (KExpr 7 26 × List (Fin 7 × ℚ)) := [
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.var 4) (KExpr.var 3)) (KExpr.var 0)) (KExpr.par 11)) (KExpr.par 16)) (KExpr.mul (KExpr.add (KExpr.var 3) (KExpr.par 9)) (KExpr.add (KExpr.par 7) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 4) (KExpr.var 3)) (KExpr.par 16)) (KExpr.add (KExpr.var 3) (KExpr.par 9))))))), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 0)) (KExpr.par 12)) (KExpr.qconst (1 : ℚ))), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 1)) (KExpr.par 13)) (KExpr.qconst (1 : ℚ))), [(0, (1 : ℚ)), (1, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 23)), [(0, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 0)) (KExpr.par 0)), [(0, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 1)) (KExpr.par 1)), [(1, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 3)) (KExpr.par 14)), [(2, (1 : ℚ)), (3, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 2) (KExpr.var 1)) (KExpr.par 15)) (KExpr.add (KExpr.var 1) (KExpr.par 8)))), [(2, (-1 : ℚ)), (3, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 24)), [(2, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 2)) (KExpr.par 2)), [(2, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 3)) (KExpr.par 3)), [(3, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 4) (KExpr.var 3)) (KExpr.par 16)) (KExpr.add (KExpr.var 3) (KExpr.par 9)))), [(4, (-1 : ℚ)), (6, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 5)) (KExpr.par 17)), [(4, (1 : ℚ)), (5, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 25)), [(4, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 4)) (KExpr.par 4)), [(4, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 6) (KExpr.var 1)) (KExpr.par 18)) (KExpr.add (KExpr.var 1) (KExpr.par 10)))), [(5, (1 : ℚ)), (6, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 5)) (KExpr.par 5)), [(5, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 6)) (KExpr.par 6)), [(6, (-1 : ℚ))])
]

/-- El campo del modelo: `Fᵢ = Σ_r coef_r(i) · V_r`. -/
def F : Fin 7 → KExpr 7 26 := netF Rx

/-- Dominio ⊇ ortante y cuasi-positividad (Lean ejecuta el comprobador). -/
theorem net_ok : checkNet pos Rx = true := by decide +kernel

/-- Pesos de la combinación con crecimiento lineal (cᵢ ≥ 1). -/
def c : Fin 7 → ℚ := ![(1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ)]

theorem growth_ok : checkGrowth pos c Rx = true := by decide +kernel

/-- θ₀ nominal (PEtab), en racionales exactos. -/
def θq : Fin 26 → ℚ := ![(182532326367113 / 1000000000000000 : ℚ), (33339166094201 / 1250000000000 : ℚ), (46926119958537 / 25000000000000 : ℚ), (1 / 10000 : ℚ), (33833764834783 / 250000000000000 : ℚ), (1 / 10000 : ℚ), (1 / 10000 : ℚ), (10000000000 : ℚ), (53837848083813 / 25000000000 : ℚ), (498501785452867 / 50000 : ℚ), (418712288317411 / 10000000 : ℚ), (212191995458117 / 50000000000000 : ℚ), (2967969646137 / 500000000000000 : ℚ), (1230128738639 / 500000000000000 : ℚ), (14072591880661 / 2500000000000 : ℚ), (6808026895421 / 312500000000 : ℚ), (126898706808539 / 50000000000 : ℚ), (6707095633977 / 400000000000 : ℚ), (108294200012079 / 5000000000 : ℚ), (100000000 : ℚ), (331336069433133 / 10000000 : ℚ), (168479882762621 / 5000000000000 : ℚ), (56683003734981 / 500000000000 : ℚ), (884612150536401 / 10000000000 : ℚ), (296114746928213 / 100000000 : ℚ), (216398071518517 / 50000000 : ℚ)]

theorem theta_ok : checkPosParams pos θq = true := by decide +kernel

/-- Condiciones iniciales nominales. -/
def xq : Fin 7 → ℚ := ![(2332673997 / 5000 : ℚ), (77413 / 625 : ℚ), (7887702697 / 5000 : ℚ), (3320545041 / 10000 : ℚ), (159741942951 / 5000 : ℚ), (401994341 / 2500 : ℚ), (420828286681 / 10000 : ℚ)]

theorem x0_ok : checkNonneg xq = true := by decide +kernel

/-- **Teorema final, sin condiciones pendientes**: para todo T ≥ 0 la solución
nominal existe en [0, T], es ≥ 0, queda en el dominio, y la trayectoria es
diferenciable respecto a θ en θ₀. -/
def final := @network_final _ _ pos Rx net_ok c growth_ok θq theta_ok xq x0_ok

end Models.Weber_BMC2015

#print axioms Models.Weber_BMC2015.final
