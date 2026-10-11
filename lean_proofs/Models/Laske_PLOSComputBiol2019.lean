import KineticNetwork

/-! Modelo `Laske_PLOSComputBiol2019` (forma de red), traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (34): V_ex, V_end, Vp_cyt, Vp_nuc, R_C, R_C_RdRp, R_V, R_V_RdRp, R_M1, R_M2, R_M3, R_M4, R_M5, R_M6, R_M7, R_M8, P_B1, P_B2, P_PA, P_HA, P_NP, P_NA, P_M1, P_NEP, Vp_nuc_M1, Vp_cyt_M1, V_rel, P_RdRp, Cp, V_att_Hi, V_att_Lo, P_M2, B_att_Lo, B_att_Hi

Parámetros estimados θ (6): k_imp, k_syn_R_M, k_syn_R_C, k_syn_R_V, k_bind_M1, k_rel
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck KineticNetwork

namespace Models.Laske_PLOSComputBiol2019

/-- Máscara de parámetros positivos (nominal > 0 o escala log). -/
def pos : Fin 6 → Bool := fun _ => true

/-- Términos de velocidad con su columna estequiométrica (51 términos). -/
def Rx : List (KExpr 34 6 × List (Fin 34 × ℚ)) := [
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (809 / 10000 : ℚ))) (KExpr.var 0)) (KExpr.var 33)), [(0, (-1 : ℚ)), (29, (1 : ℚ)), (33, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.qconst (809 / 10000 : ℚ)) (KExpr.qconst (113 / 10000 : ℚ)))) (KExpr.var 29)), [(0, (1 : ℚ)), (29, (-1 : ℚ)), (33, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (91 / 200000 : ℚ))) (KExpr.var 0)) (KExpr.var 32)), [(0, (-1 : ℚ)), (30, (1 : ℚ)), (32, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.qconst (91 / 200000 : ℚ)) (KExpr.qconst (833 / 10000000 : ℚ)))) (KExpr.var 30)), [(0, (1 : ℚ)), (30, (-1 : ℚ)), (32, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (24 / 5 : ℚ))) (KExpr.var 29)), [(1, (1 : ℚ)), (29, (-1 : ℚ)), (33, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.div (KExpr.qconst (49 / 100 : ℚ)) (KExpr.qconst (51 / 100 : ℚ))) (KExpr.qconst (321 / 100 : ℚ)))) (KExpr.var 1)), [(1, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (321 / 100 : ℚ))) (KExpr.var 1)), [(1, (-1 : ℚ)), (2, (8 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (24 / 5 : ℚ))) (KExpr.var 30)), [(1, (1 : ℚ)), (30, (-1 : ℚ)), (32, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 0)) (KExpr.var 2)), [(2, (-1 : ℚ)), (3, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (301 / 1000000 : ℚ)) (KExpr.var 7)) (KExpr.var 20))), [(3, (1 : ℚ)), (7, (-1 : ℚ)), (20, (-71 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (9 / 100 : ℚ))) (KExpr.var 3)), [(3, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.par 4) (KExpr.var 3)) (KExpr.var 22))), [(3, (-1 : ℚ)), (22, (-17 / 2 : ℚ)), (24, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 2)) (KExpr.var 3)), [(4, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (909 / 25 : ℚ))) (KExpr.var 4)), [(4, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (1 : ℚ))) (KExpr.var 4)) (KExpr.var 27)), [(4, (-1 : ℚ)), (5, (1 : ℚ)), (27, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (17 / 4 : ℚ))) (KExpr.var 5)), [(5, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (301 / 1000000 : ℚ)) (KExpr.var 5)) (KExpr.var 20))), [(5, (-1 : ℚ)), (20, (-71 : ℚ)), (28, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 3)) (KExpr.var 28)), [(6, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (1 : ℚ))) (KExpr.var 6)) (KExpr.var 27)), [(6, (-1 : ℚ)), (7, (1 : ℚ)), (27, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (909 / 25 : ℚ))) (KExpr.var 6)), [(6, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (17 / 4 : ℚ))) (KExpr.var 7)), [(7, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.div (KExpr.qconst (30600 : ℚ)) (KExpr.qconst (2320 : ℚ))) (KExpr.qconst (8 : ℚ)))) (KExpr.var 3)), [(8, (1 : ℚ)), (9, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (33 / 100 : ℚ))) (KExpr.var 8)), [(8, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (33 / 100 : ℚ))) (KExpr.var 9)), [(9, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.div (KExpr.qconst (30600 : ℚ)) (KExpr.qconst (2211 : ℚ))) (KExpr.qconst (8 : ℚ)))) (KExpr.var 3)), [(10, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (33 / 100 : ℚ))) (KExpr.var 10)), [(10, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.div (KExpr.qconst (30600 : ℚ)) (KExpr.qconst (1757 : ℚ))) (KExpr.qconst (8 : ℚ)))) (KExpr.var 3)), [(11, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (33 / 100 : ℚ))) (KExpr.var 11)), [(11, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.div (KExpr.qconst (30600 : ℚ)) (KExpr.qconst (1540 : ℚ))) (KExpr.qconst (8 : ℚ)))) (KExpr.var 3)), [(12, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (33 / 100 : ℚ))) (KExpr.var 12)), [(12, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.div (KExpr.qconst (30600 : ℚ)) (KExpr.qconst (1392 : ℚ))) (KExpr.qconst (8 : ℚ)))) (KExpr.var 3)), [(13, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (33 / 100 : ℚ))) (KExpr.var 13)), [(13, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.div (KExpr.qconst (30600 : ℚ)) (KExpr.qconst (1005 : ℚ))) (KExpr.qconst (8 : ℚ)))) (KExpr.var 3)), [(14, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (33 / 100 : ℚ))) (KExpr.var 14)), [(14, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.div (KExpr.qconst (30600 : ℚ)) (KExpr.qconst (868 : ℚ))) (KExpr.qconst (8 : ℚ)))) (KExpr.var 3)), [(15, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (33 / 100 : ℚ))) (KExpr.var 15)), [(15, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.qconst (64800 : ℚ)) (KExpr.qconst (160 : ℚ)))) (KExpr.var 9)), [(16, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (1 : ℚ))) (KExpr.var 16)) (KExpr.var 17)) (KExpr.var 18)), [(16, (-1 : ℚ)), (17, (-1 : ℚ)), (18, (-1 : ℚ)), (27, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.qconst (64800 : ℚ)) (KExpr.qconst (160 : ℚ)))) (KExpr.var 8)), [(17, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.qconst (64800 : ℚ)) (KExpr.qconst (160 : ℚ)))) (KExpr.var 10)), [(18, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.qconst (64800 : ℚ)) (KExpr.qconst (160 : ℚ)))) (KExpr.var 11)), [(19, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.par 5) (KExpr.var 25)) (KExpr.var 27)) (KExpr.var 19)) (KExpr.var 20)) (KExpr.var 21)) (KExpr.var 22)) (KExpr.var 31)) (KExpr.var 23)) (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.add (KExpr.var 27) (KExpr.mul (KExpr.qconst (10 : ℚ)) (KExpr.qconst (45 : ℚ)))) (KExpr.add (KExpr.var 19) (KExpr.mul (KExpr.qconst (10 : ℚ)) (KExpr.qconst (500 : ℚ))))) (KExpr.add (KExpr.var 20) (KExpr.mul (KExpr.qconst (10 : ℚ)) (KExpr.qconst (1000 : ℚ))))) (KExpr.add (KExpr.var 21) (KExpr.mul (KExpr.qconst (10 : ℚ)) (KExpr.qconst (100 : ℚ))))) (KExpr.add (KExpr.var 22) (KExpr.mul (KExpr.qconst (10 : ℚ)) (KExpr.qconst (3000 : ℚ))))) (KExpr.add (KExpr.var 31) (KExpr.mul (KExpr.qconst (10 : ℚ)) (KExpr.qconst (40 : ℚ))))) (KExpr.add (KExpr.var 23) (KExpr.mul (KExpr.qconst (10 : ℚ)) (KExpr.qconst (165 : ℚ))))))), [(19, (-500 : ℚ)), (20, (-433 : ℚ)), (21, (-100 : ℚ)), (22, (-2932 : ℚ)), (23, (-157 : ℚ)), (25, (-8 : ℚ)), (26, (1 : ℚ)), (27, (-37 : ℚ)), (31, (-40 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.qconst (64800 : ℚ)) (KExpr.qconst (160 : ℚ)))) (KExpr.var 12)), [(20, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.qconst (64800 : ℚ)) (KExpr.qconst (160 : ℚ)))) (KExpr.var 13)), [(21, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.div (KExpr.qconst (64800 : ℚ)) (KExpr.qconst (160 : ℚ))) (KExpr.qconst (49 / 50 : ℚ)))) (KExpr.var 14)), [(22, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.div (KExpr.qconst (64800 : ℚ)) (KExpr.qconst (160 : ℚ))) (KExpr.qconst (1 / 8 : ℚ)))) (KExpr.var 15)), [(23, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (1 / 1000000 : ℚ))) (KExpr.var 24)) (KExpr.var 23)), [(23, (-1 : ℚ)), (24, (-1 : ℚ)), (25, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (9 / 100 : ℚ))) (KExpr.var 24)), [(24, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (9 / 100 : ℚ))) (KExpr.var 25)), [(25, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (9 / 100 : ℚ))) (KExpr.var 28)), [(28, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.div (KExpr.qconst (64800 : ℚ)) (KExpr.qconst (160 : ℚ))) (KExpr.qconst (1 / 50 : ℚ)))) (KExpr.var 14)), [(31, (1 : ℚ))])
]

/-- El campo del modelo: `Fᵢ = Σ_r coef_r(i) · V_r`. -/
def F : Fin 34 → KExpr 34 6 := netF Rx

/-- Dominio ⊇ ortante y cuasi-positividad (Lean ejecuta el comprobador). -/
theorem net_ok : checkNet pos Rx = true := by decide +kernel

/-- Pesos de la combinación con crecimiento lineal (cᵢ ≥ 1). -/
def c : Fin 34 → ℚ := fun _ => (1 : ℚ)

theorem growth_ok : checkGrowth pos c Rx = true := by decide +kernel

/-- θ₀ nominal (PEtab), en racionales exactos. -/
def θq : Fin 6 → ℚ := ![(37 / 125 : ℚ), (30600 : ℚ), (153 / 100 : ℚ), (10093 / 100 : ℚ), (91 / 50000000 : ℚ), (11 / 10000 : ℚ)]

theorem theta_ok : checkPosParams pos θq = true := by decide +kernel

/-- Condiciones iniciales nominales. -/
def xq : Fin 34 → ℚ := ![(50 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (1000 : ℚ), (150 : ℚ)]

theorem x0_ok : checkNonneg xq = true := by decide +kernel

/-- **Teorema final, sin condiciones pendientes**: para todo T ≥ 0 la solución
nominal existe en [0, T], es ≥ 0, queda en el dominio, y la trayectoria es
diferenciable respecto a θ en θ₀. -/
def final := @network_final _ _ pos Rx net_ok c growth_ok θq theta_ok xq x0_ok

end Models.Laske_PLOSComputBiol2019

#print axioms Models.Laske_PLOSComputBiol2019.final
