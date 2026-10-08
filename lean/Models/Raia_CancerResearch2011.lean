import KineticNetwork

/-! Modelo `Raia_CancerResearch2011` (forma de red), traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (14): Rec, Rec_i, IL13_Rec, p_IL13_Rec, p_IL13_Rec_i, JAK2, pJAK2, STAT5, pSTAT5, SOCS3mRNA, DecoyR, IL13_DecoyR, SOCS3, CD274mRNA

Parámetros estimados θ (18): CD274mRNA_production, DecoyR_binding, JAK2_p_inhibition, JAK2_phosphorylation, Kon_IL13Rec, Rec_intern, Rec_phosphorylation, Rec_recycle, SOCS3_accumulation, SOCS3_degradation, SOCS3_translation, SOCS3mRNA_production, STAT5_phosphorylation, init_Rec_i, pJAK2_dephosphorylation, pRec_degradation, pRec_intern, pSTAT5_dephosphorylation
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck KineticNetwork

namespace Models.Raia_CancerResearch2011

/-- Máscara de parámetros positivos (nominal > 0 o escala log). -/
def pos : Fin 18 → Bool := ![true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true]

/-- Términos de velocidad con su columna estequiométrica (14 términos). -/
def Rx : List (KExpr 14 18 × List (Fin 14 × ℚ)) := [
  ((KExpr.mul (KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.var 0)) (KExpr.par 5)), [(0, (-1 / 100 : ℚ)), (1, (1 / 100 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.var 1)) (KExpr.par 7)), [(0, (1 / 100 : ℚ)), (1, (-1 / 100 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.var 2)) (KExpr.par 6)) (KExpr.var 6)), [(2, (-1 / 100 : ℚ)), (3, (1 / 100 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.par 16)) (KExpr.var 3)), [(3, (-1 / 100 : ℚ)), (4, (1 / 100 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.par 15)) (KExpr.var 4)), [(4, (-1 / 100 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 2) (KExpr.var 5)) (KExpr.par 3)) (KExpr.add (KExpr.mul (KExpr.par 2) (KExpr.var 12)) (KExpr.qconst (1 : ℚ))))), [(5, (-1 / 100 : ℚ)), (6, (1 / 100 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 5) (KExpr.par 3)) (KExpr.var 3)) (KExpr.add (KExpr.mul (KExpr.par 2) (KExpr.var 12)) (KExpr.qconst (1 : ℚ))))), [(5, (-1 / 100 : ℚ)), (6, (1 / 100 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.qconst (91 : ℚ))) (KExpr.var 6)) (KExpr.par 14)), [(5, (1 / 100 : ℚ)), (6, (-1 / 100 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.var 7)) (KExpr.par 12)) (KExpr.var 6)), [(7, (-1 / 100 : ℚ)), (8, (1 / 100 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.qconst (91 : ℚ))) (KExpr.var 8)) (KExpr.par 17)), [(7, (1 / 100 : ℚ)), (8, (-1 / 100 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (10 : ℚ)) (KExpr.par 11)) (KExpr.var 8)), [(9, (1 / 10 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 9) (KExpr.par 10)) (KExpr.add (KExpr.var 9) (KExpr.par 8)))), [(12, (1 / 100 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.var 12)) (KExpr.par 9)), [(12, (-1 / 100 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (10 : ℚ)) (KExpr.par 0)) (KExpr.var 8)), [(13, (1 / 10 : ℚ))])
]

/-- El campo del modelo: `Fᵢ = Σ_r coef_r(i) · V_r`. -/
def F : Fin 14 → KExpr 14 18 := netF Rx

/-- Dominio ⊇ ortante y cuasi-positividad (Lean ejecuta el comprobador). -/
theorem net_ok : checkNet pos Rx = true := by decide +kernel

/-- Pesos de la combinación con crecimiento lineal (cᵢ ≥ 1). -/
def c : Fin 14 → ℚ := ![(1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ)]

theorem growth_ok : checkGrowth pos c Rx = true := by decide +kernel

/-- θ₀ nominal (PEtab), en racionales exactos. -/
def θq : Fin 18 → ℚ := ![(21208853684209 / 1000000000000000 : ℚ), (1925519568701 / 500000000000000 : ℚ), (78140000505809 / 1000000000000000 : ℚ), (101721171826747 / 100000000000000 : ℚ), (2278141087201 / 1000000000000000 : ℚ), (344129281159739 / 1000000000000000 : ℚ), (62499988530249 / 62500000000 : ℚ), (104887453397 / 50000000000000 : ℚ), (28236118856949 / 62500000000 : ℚ), (43380223348167 / 1000000000000000 : ℚ), (78593444193003 / 5000000000000 : ℚ), (7168575888093 / 50000000000000 : ℚ), (974103739653 / 50000000000000 : ℚ), (235058493601113 / 1000000000000 : ℚ), (175894009439 / 1000000000000000 : ℚ), (13098373658991 / 62500000000000 : ℚ), (146317883824441 / 250000000000000 : ℚ), (137416159659 / 500000000000000 : ℚ)]

theorem theta_ok : checkPosParams pos θq = true := by decide +kernel

/-- Condición inicial x₀(θ) (asignaciones iniciales de SBML). -/
def G : Fin 14 → KExpr 14 18 := ![
  (KExpr.qconst (13 / 10 : ℚ)),
  (KExpr.par 13),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (14 / 5 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (165 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (17 / 50 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ))
]

theorem init_ok : checkInit pos G = true := by decide +kernel

/-- **Teorema final, sin condiciones pendientes** (condición inicial x₀(θ)). -/
def final := @network_final_init _ _ pos Rx net_ok c growth_ok G init_ok θq theta_ok

end Models.Raia_CancerResearch2011

#print axioms Models.Raia_CancerResearch2011.final
