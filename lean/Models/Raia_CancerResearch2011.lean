import KineticCheck

/-! Modelo `Raia_CancerResearch2011` traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (14): Rec, Rec_i, IL13_Rec, p_IL13_Rec, p_IL13_Rec_i, JAK2, pJAK2, STAT5, pSTAT5, SOCS3mRNA, DecoyR, IL13_DecoyR, SOCS3, CD274mRNA

Parámetros estimados θ (18): CD274mRNA_production, DecoyR_binding, JAK2_p_inhibition, JAK2_phosphorylation, Kon_IL13Rec, Rec_intern, Rec_phosphorylation, Rec_recycle, SOCS3_accumulation, SOCS3_degradation, SOCS3_translation, SOCS3mRNA_production, STAT5_phosphorylation, init_Rec_i, pJAK2_dephosphorylation, pRec_degradation, pRec_intern, pSTAT5_dephosphorylation
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck

namespace Models.Raia_CancerResearch2011

/-- Máscara de parámetros con valor nominal > 0 (los demás: signo arbitrario). -/
def pos : Fin 18 → Bool := ![true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true]

def F : Fin 14 → KExpr 14 18 := ![
  (KExpr.sub (KExpr.mul (KExpr.qconst (1 / 100 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.var 1)) (KExpr.par 7))) (KExpr.mul (KExpr.qconst (1 / 100 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.var 0)) (KExpr.par 5)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (1 / 100 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.var 0)) (KExpr.par 5))) (KExpr.mul (KExpr.qconst (1 / 100 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.var 1)) (KExpr.par 7)))),
  (KExpr.sub (KExpr.qconst (0 : ℚ)) (KExpr.mul (KExpr.qconst (1 / 100 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.var 2)) (KExpr.par 6)) (KExpr.var 6)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (1 / 100 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.var 2)) (KExpr.par 6)) (KExpr.var 6))) (KExpr.mul (KExpr.qconst (1 / 100 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.par 16)) (KExpr.var 3)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (1 / 100 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.par 16)) (KExpr.var 3))) (KExpr.mul (KExpr.qconst (1 / 100 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.par 15)) (KExpr.var 4)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (1 / 100 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.qconst (91 : ℚ))) (KExpr.var 6)) (KExpr.par 14))) (KExpr.add (KExpr.mul (KExpr.qconst (1 / 100 : ℚ)) (KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 2) (KExpr.var 5)) (KExpr.par 3)) (KExpr.add (KExpr.mul (KExpr.par 2) (KExpr.var 12)) (KExpr.qconst (1 : ℚ)))))) (KExpr.mul (KExpr.qconst (1 / 100 : ℚ)) (KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 5) (KExpr.par 3)) (KExpr.var 3)) (KExpr.add (KExpr.mul (KExpr.par 2) (KExpr.var 12)) (KExpr.qconst (1 : ℚ)))))))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.qconst (1 / 100 : ℚ)) (KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 2) (KExpr.var 5)) (KExpr.par 3)) (KExpr.add (KExpr.mul (KExpr.par 2) (KExpr.var 12)) (KExpr.qconst (1 : ℚ)))))) (KExpr.mul (KExpr.qconst (1 / 100 : ℚ)) (KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 5) (KExpr.par 3)) (KExpr.var 3)) (KExpr.add (KExpr.mul (KExpr.par 2) (KExpr.var 12)) (KExpr.qconst (1 : ℚ))))))) (KExpr.mul (KExpr.qconst (1 / 100 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.qconst (91 : ℚ))) (KExpr.var 6)) (KExpr.par 14)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (1 / 100 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.qconst (91 : ℚ))) (KExpr.var 8)) (KExpr.par 17))) (KExpr.mul (KExpr.qconst (1 / 100 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.var 7)) (KExpr.par 12)) (KExpr.var 6)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (1 / 100 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.var 7)) (KExpr.par 12)) (KExpr.var 6))) (KExpr.mul (KExpr.qconst (1 / 100 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.qconst (91 : ℚ))) (KExpr.var 8)) (KExpr.par 17)))),
  (KExpr.mul (KExpr.qconst (1 / 10 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (10 : ℚ)) (KExpr.par 11)) (KExpr.var 8))),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.sub (KExpr.mul (KExpr.qconst (1 / 100 : ℚ)) (KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 9) (KExpr.par 10)) (KExpr.add (KExpr.var 9) (KExpr.par 8))))) (KExpr.mul (KExpr.qconst (1 / 100 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (100 : ℚ)) (KExpr.var 12)) (KExpr.par 9)))),
  (KExpr.mul (KExpr.qconst (1 / 10 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (10 : ℚ)) (KExpr.par 0)) (KExpr.var 8)))
]

theorem check : checkModel pos F = true := by decide +kernel

/-- θ₀ nominal (PEtab), en racionales exactos. -/
def θq : Fin 18 → ℚ := ![(21208853684209 / 1000000000000000 : ℚ), (1925519568701 / 500000000000000 : ℚ), (78140000505809 / 1000000000000000 : ℚ), (101721171826747 / 100000000000000 : ℚ), (2278141087201 / 1000000000000000 : ℚ), (344129281159739 / 1000000000000000 : ℚ), (62499988530249 / 62500000000 : ℚ), (104887453397 / 50000000000000 : ℚ), (28236118856949 / 62500000000 : ℚ), (43380223348167 / 1000000000000000 : ℚ), (78593444193003 / 5000000000000 : ℚ), (7168575888093 / 50000000000000 : ℚ), (974103739653 / 50000000000000 : ℚ), (235058493601113 / 1000000000000 : ℚ), (175894009439 / 1000000000000000 : ℚ), (13098373658991 / 62500000000000 : ℚ), (146317883824441 / 250000000000000 : ℚ), (137416159659 / 500000000000000 : ℚ)]

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

theorem theta_ok : checkPosParams pos θq = true := by decide +kernel

theorem init_ok : checkInit pos G = true := by decide +kernel

/-- Diferenciabilidad de la trayectoria (y positividad) para este modelo. -/
def diff := @checked_model_hasFDerivAt _ _ pos F check

/-- Teorema final (condición inicial dependiente de θ): la única condición
restante es que la solución nominal exista en [0, T]. -/
def final := @checked_model_final_init _ _ pos F check G init_ok θq theta_ok

end Models.Raia_CancerResearch2011

#print axioms Models.Raia_CancerResearch2011.diff

#print axioms Models.Raia_CancerResearch2011.final
