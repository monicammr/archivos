import KineticNetwork

/-! Modelo `Bachmann_MSB2011` (forma de red), traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (25): EpoRJAK2, EpoRpJAK2, p1EpoRpJAK2, p2EpoRpJAK2, p12EpoRpJAK2, EpoRJAK2_CIS, SHP1, SHP1Act, STAT5, pSTAT5, npSTAT5, CISnRNA1, CISnRNA2, CISnRNA3, CISnRNA4, CISnRNA5, CISRNA, CIS, SOCS3nRNA1, SOCS3nRNA2, SOCS3nRNA3, SOCS3nRNA4, SOCS3nRNA5, SOCS3RNA, SOCS3

Parámetros estimados θ (27): CISEqc, CISEqcOE, CISInh, CISRNADelay, CISRNATurn, CISTurn, EpoRActJAK2, EpoRCISInh, EpoRCISRemove, JAK2ActEpo, JAK2EpoRDeaSHP1, SHP1ActEpoR, SHP1Dea, SHP1ProOE, SOCS3Eqc, SOCS3EqcOE, SOCS3Inh, SOCS3RNADelay, SOCS3RNATurn, SOCS3Turn, STAT5ActEpoR, STAT5ActJAK2, STAT5Exp, STAT5Imp, init_EpoRJAK2, init_SHP1, init_STAT5
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck KineticNetwork

namespace Models.Bachmann_MSB2011

/-- Máscara de parámetros positivos (nominal > 0 o escala log). -/
def pos : Fin 27 → Bool := ![true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true]

/-- Términos de velocidad con su columna estequiométrica (43 términos). -/
def Rx : List (KExpr 25 27 × List (Fin 25 × ℚ)) := [
  ((KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.qconst (1 / 8000000 : ℚ)) (KExpr.var 0)) (KExpr.par 9)) (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 24) (KExpr.par 16)) (KExpr.par 14)) (KExpr.qconst (1 : ℚ))))), [(0, (-5 / 2 : ℚ)), (1, (5 / 2 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 1) (KExpr.par 10)) (KExpr.var 7)) (KExpr.par 25))), [(0, (5 / 2 : ℚ)), (1, (-5 / 2 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.par 10) (KExpr.var 7)) (KExpr.var 2)) (KExpr.par 25))), [(0, (5 / 2 : ℚ)), (2, (-5 / 2 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.par 10) (KExpr.var 7)) (KExpr.var 3)) (KExpr.par 25))), [(0, (5 / 2 : ℚ)), (3, (-5 / 2 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.par 10) (KExpr.var 7)) (KExpr.var 4)) (KExpr.par 25))), [(0, (5 / 2 : ℚ)), (4, (-5 / 2 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 1) (KExpr.par 6)) (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 24) (KExpr.par 16)) (KExpr.par 14)) (KExpr.qconst (1 : ℚ))))), [(1, (-5 / 2 : ℚ)), (2, (5 / 2 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.qconst (3 : ℚ)) (KExpr.var 1)) (KExpr.par 6)) (KExpr.mul (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 24) (KExpr.par 16)) (KExpr.par 14)) (KExpr.qconst (1 : ℚ))) (KExpr.add (KExpr.mul (KExpr.par 7) (KExpr.var 5)) (KExpr.qconst (1 : ℚ)))))), [(1, (-5 / 2 : ℚ)), (3, (5 / 2 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.qconst (3 : ℚ)) (KExpr.par 6)) (KExpr.var 2)) (KExpr.mul (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 24) (KExpr.par 16)) (KExpr.par 14)) (KExpr.qconst (1 : ℚ))) (KExpr.add (KExpr.mul (KExpr.par 7) (KExpr.var 5)) (KExpr.qconst (1 : ℚ)))))), [(2, (-5 / 2 : ℚ)), (4, (5 / 2 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.par 6) (KExpr.var 3)) (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 24) (KExpr.par 16)) (KExpr.par 14)) (KExpr.qconst (1 : ℚ))))), [(3, (-5 / 2 : ℚ)), (4, (5 / 2 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 5) (KExpr.par 8)) (KExpr.var 4)) (KExpr.par 24))), [(5, (-5 / 2 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 5) (KExpr.par 8)) (KExpr.var 2)) (KExpr.par 24))), [(5, (-5 / 2 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 6) (KExpr.par 11)) (KExpr.var 1)) (KExpr.par 24))), [(6, (-5 / 2 : ℚ)), (7, (5 / 2 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 6) (KExpr.par 11)) (KExpr.var 4)) (KExpr.par 24))), [(6, (-5 / 2 : ℚ)), (7, (5 / 2 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 6) (KExpr.par 11)) (KExpr.var 2)) (KExpr.par 24))), [(6, (-5 / 2 : ℚ)), (7, (5 / 2 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 6) (KExpr.par 11)) (KExpr.var 3)) (KExpr.par 24))), [(6, (-5 / 2 : ℚ)), (7, (5 / 2 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.par 12)) (KExpr.var 7)), [(6, (5 / 2 : ℚ)), (7, (-5 / 2 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 8) (KExpr.par 21)) (KExpr.var 1)) (KExpr.mul (KExpr.par 24) (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 24) (KExpr.par 16)) (KExpr.par 14)) (KExpr.qconst (1 : ℚ)))))), [(8, (-5 / 2 : ℚ)), (9, (5 / 2 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 8) (KExpr.par 21)) (KExpr.var 4)) (KExpr.mul (KExpr.par 24) (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 24) (KExpr.par 16)) (KExpr.par 14)) (KExpr.qconst (1 : ℚ)))))), [(8, (-5 / 2 : ℚ)), (9, (5 / 2 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 8) (KExpr.par 21)) (KExpr.var 2)) (KExpr.mul (KExpr.par 24) (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 24) (KExpr.par 16)) (KExpr.par 14)) (KExpr.qconst (1 : ℚ)))))), [(8, (-5 / 2 : ℚ)), (9, (5 / 2 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 8) (KExpr.par 21)) (KExpr.var 3)) (KExpr.mul (KExpr.par 24) (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 24) (KExpr.par 16)) (KExpr.par 14)) (KExpr.qconst (1 : ℚ)))))), [(8, (-5 / 2 : ℚ)), (9, (5 / 2 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 8) (KExpr.par 20)) (KExpr.npow (KExpr.add (KExpr.var 4) (KExpr.var 2)) 2)) (KExpr.mul (KExpr.mul (KExpr.npow (KExpr.par 24) 2) (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 24) (KExpr.par 16)) (KExpr.par 14)) (KExpr.qconst (1 : ℚ)))) (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 17) (KExpr.par 2)) (KExpr.par 0)) (KExpr.qconst (1 : ℚ)))))), [(8, (-5 / 2 : ℚ)), (9, (5 / 2 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.par 22)) (KExpr.var 10)), [(8, (5 / 2 : ℚ)), (10, (-40 / 11 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.par 23)) (KExpr.var 9)), [(9, (-5 / 2 : ℚ)), (10, (40 / 11 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 4)) (KExpr.var 10)) (KExpr.qconst (1 / 8000000 : ℚ))) (KExpr.par 26))), [(11, (40 / 11 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.var 11)) (KExpr.par 3)), [(11, (-40 / 11 : ℚ)), (12, (40 / 11 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.var 12)) (KExpr.par 3)), [(12, (-40 / 11 : ℚ)), (13, (40 / 11 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.var 13)) (KExpr.par 3)), [(13, (-40 / 11 : ℚ)), (14, (40 / 11 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.var 14)) (KExpr.par 3)), [(14, (-40 / 11 : ℚ)), (15, (40 / 11 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.var 15)) (KExpr.par 3)), [(15, (-40 / 11 : ℚ)), (16, (5 / 2 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.var 16)) (KExpr.par 4)), [(16, (-5 / 2 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 16) (KExpr.par 0)) (KExpr.par 5)) (KExpr.qconst (1 : ℚ)))), [(17, (5 / 2 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.var 17)) (KExpr.par 5)), [(17, (-5 / 2 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.par 0)) (KExpr.par 5)) (KExpr.par 1)) (KExpr.qconst (1 / 8000000 : ℚ))), [(17, (5 / 2 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 18)) (KExpr.var 10)) (KExpr.qconst (1 / 8000000 : ℚ))) (KExpr.par 26))), [(18, (40 / 11 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.var 18)) (KExpr.par 17)), [(18, (-40 / 11 : ℚ)), (19, (40 / 11 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.var 19)) (KExpr.par 17)), [(19, (-40 / 11 : ℚ)), (20, (40 / 11 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.var 20)) (KExpr.par 17)), [(20, (-40 / 11 : ℚ)), (21, (40 / 11 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.var 21)) (KExpr.par 17)), [(21, (-40 / 11 : ℚ)), (22, (40 / 11 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.var 22)) (KExpr.par 17)), [(22, (-40 / 11 : ℚ)), (23, (5 / 2 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.var 23)) (KExpr.par 18)), [(23, (-5 / 2 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 23) (KExpr.par 14)) (KExpr.par 19)) (KExpr.qconst (1 : ℚ)))), [(24, (5 / 2 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.var 24)) (KExpr.par 19)), [(24, (-5 / 2 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.qconst (1 / 8000000 : ℚ))) (KExpr.par 14)) (KExpr.par 19)) (KExpr.par 15)), [(24, (5 / 2 : ℚ))])
]

/-- El campo del modelo: `Fᵢ = Σ_r coef_r(i) · V_r`. -/
def F : Fin 25 → KExpr 25 27 := netF Rx

/-- Dominio ⊇ ortante y cuasi-positividad (Lean ejecuta el comprobador). -/
theorem net_ok : checkNet pos Rx = true := by decide +kernel

/-- Pesos de la combinación con crecimiento lineal (cᵢ ≥ 1). -/
def c : Fin 25 → ℚ := ![(1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ)]

theorem growth_ok : checkGrowth pos c Rx = true := by decide +kernel

/-- θ₀ nominal (PEtab), en racionales exactos. -/
def θq : Fin 27 → ℚ := ![(108213506831433 / 250000000000 : ℚ), (26513614503397 / 50000000000000 : ℚ), (392610522616453 / 500000 : ℚ), (144777009620017 / 1000000000000000 : ℚ), (1000 : ℚ), (4199412514631 / 500000000000000 : ℚ), (267299659481333 / 1000000000000000 : ℚ), (1000000 : ℚ), (542989282766407 / 100000000000000 : ℚ), (633154209632843 / 1000000000 : ℚ), (71361534706159 / 500000000000 : ℚ), (1 / 1000 : ℚ), (8162255244283 / 1000000000000000 : ℚ), (282568032716189 / 100000000000000 : ℚ), (17364095522801 / 100000000000 : ℚ), (679185853534469 / 1000000000000000 : ℚ), (20814851194693 / 2000000000000 : ℚ), (106454014521077 / 100000000000000 : ℚ), (8309263619427 / 1000000000000000 : ℚ), (10000 : ℚ), (194986374447149 / 5000000000000 : ℚ), (4881802078303 / 62500000000000 : ℚ), (4657168677077 / 62500000000000 : ℚ), (26887318057561 / 1000000000000000 : ℚ), (397622379188569 / 100000000000000 : ℚ), (133625582081743 / 5000000000000 : ℚ), (79753639977851 / 1000000000000 : ℚ)]

theorem theta_ok : checkPosParams pos θq = true := by decide +kernel

/-- Condición inicial x₀(θ) (asignaciones iniciales de SBML). -/
def G : Fin 25 → KExpr 25 27 := ![
  (KExpr.par 24),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.mul (KExpr.par 25) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 13)) (KExpr.qconst (1 : ℚ)))),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.par 26),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ))
]

theorem init_ok : checkInit pos G = true := by decide +kernel

/-- **Teorema final, sin condiciones pendientes** (condición inicial x₀(θ)). -/
def final := @network_final_init _ _ pos Rx net_ok c growth_ok G init_ok θq theta_ok

end Models.Bachmann_MSB2011

#print axioms Models.Bachmann_MSB2011.final
