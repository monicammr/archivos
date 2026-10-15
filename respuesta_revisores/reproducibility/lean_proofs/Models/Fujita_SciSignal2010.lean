import KineticNetwork

/-! Modelo `Fujita_SciSignal2010` (forma de red), traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (9): EGFR, pEGFR, pEGFR_Akt, Akt, pAkt, S6, pAkt_S6, pS6, EGF_EGFR

Parámetros estimados θ (16): EGFR_turnover, init_AKT, init_EGFR, init_S6, reaction_1_k1, reaction_1_k2, reaction_2_k1, reaction_2_k2, reaction_3_k1, reaction_4_k1, reaction_5_k1, reaction_5_k2, reaction_6_k1, reaction_7_k1, reaction_8_k1, reaction_9_k1
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck KineticNetwork

namespace Models.Fujita_SciSignal2010

/-- Máscara de parámetros positivos (nominal > 0 o escala log). -/
def pos : Fin 16 → Bool := fun _ => true

/-- Términos de velocidad con su columna estequiométrica (13 términos). -/
def Rx : List (KExpr 9 16 × List (Fin 9 × ℚ)) := [
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 8) (KExpr.par 5))), [(0, (1 : ℚ)), (8, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 0)) (KExpr.par 0)), [(0, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (68190 : ℚ))) (KExpr.par 0)), [(0, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.var 3) (KExpr.var 1)) (KExpr.par 6))), [(1, (-1 : ℚ)), (2, (1 : ℚ)), (3, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 2) (KExpr.par 7))), [(1, (1 : ℚ)), (2, (-1 : ℚ)), (3, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 2)) (KExpr.par 8)), [(1, (1 : ℚ)), (2, (-1 : ℚ)), (4, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 1)) (KExpr.par 9)), [(1, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 8)) (KExpr.par 15)), [(1, (1 : ℚ)), (8, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 4)) (KExpr.par 13)), [(3, (1 : ℚ)), (4, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.var 5) (KExpr.var 4)) (KExpr.par 10))), [(4, (-1 : ℚ)), (5, (-1 : ℚ)), (6, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 6) (KExpr.par 11))), [(4, (1 : ℚ)), (5, (1 : ℚ)), (6, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 6)) (KExpr.par 12)), [(4, (1 : ℚ)), (6, (-1 : ℚ)), (7, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 7)) (KExpr.par 14)), [(5, (1 : ℚ)), (7, (-1 : ℚ))])
]

/-- El campo del modelo: `Fᵢ = Σ_r coef_r(i) · V_r`. -/
def F : Fin 9 → KExpr 9 16 := netF Rx

/-- Dominio ⊇ ortante y cuasi-positividad (Lean ejecuta el comprobador). -/
theorem net_ok : checkNet pos Rx = true := by decide +kernel

/-- Pesos de la combinación con crecimiento lineal (cᵢ ≥ 1). -/
def c : Fin 9 → ℚ := fun _ => (1 : ℚ)

theorem growth_ok : checkGrowth pos c Rx = true := by decide +kernel

/-- θ₀ nominal (PEtab), en racionales exactos. -/
def θq : Fin 16 → ℚ := ![(1479614562719 / 1000000000000000 : ℚ), (26930923029049 / 1000000000000000 : ℚ), (75072307611821 / 2000000 : ℚ), (188063148677911 / 1000000000000 : ℚ), (3690766129111 / 1000000000000000 : ℚ), (460235097201 / 200000000000000 : ℚ), (936500808211 / 1000000000000000 : ℚ), (304826033321293 / 5000000000 : ℚ), (433225051651771 / 1000000000000000 : ℚ), (1884698588939 / 62500000000000 : ℚ), (327310803801897 / 100000000000000000000 : ℚ), (199273149891 / 500000000000000 : ℚ), (273159846467273 / 50000000000000000000 : ℚ), (2360641662347 / 200000000000000 : ℚ), (944761775113 / 1000000000000000 : ℚ), (14255399239719 / 500000000000000 : ℚ)]

theorem theta_ok : checkPosParams pos θq = true := by decide +kernel

/-- Condición inicial x₀(θ) (asignaciones iniciales de SBML). -/
def G : Fin 9 → KExpr 9 16 := ![
  (KExpr.par 2),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.par 1),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.par 3),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ))
]

theorem init_ok : checkInit pos G = true := by decide +kernel

/-- **Teorema final, sin condiciones pendientes** (condición inicial x₀(θ)). -/
def final := @network_final_init _ _ pos Rx net_ok c growth_ok G init_ok θq theta_ok

end Models.Fujita_SciSignal2010

#print axioms Models.Fujita_SciSignal2010.final
