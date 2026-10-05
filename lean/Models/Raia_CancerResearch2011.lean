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

def F : Fin 14 → KExpr 14 18 := ![
  (.add (.sub (.qconst (0 : ℚ)) (.mul (.qconst (1 / 100 : ℚ)) (.mul (.mul (.qconst (100 : ℚ)) (.var 0)) (.par 5)))) (.mul (.qconst (1 / 100 : ℚ)) (.mul (.mul (.qconst (100 : ℚ)) (.var 1)) (.par 7)))),
  (.sub (.mul (.qconst (1 / 100 : ℚ)) (.mul (.mul (.qconst (100 : ℚ)) (.var 0)) (.par 5))) (.mul (.qconst (1 / 100 : ℚ)) (.mul (.mul (.qconst (100 : ℚ)) (.var 1)) (.par 7)))),
  (.sub (.qconst (0 : ℚ)) (.mul (.qconst (1 / 100 : ℚ)) (.mul (.mul (.mul (.qconst (100 : ℚ)) (.var 2)) (.par 6)) (.var 6)))),
  (.sub (.mul (.qconst (1 / 100 : ℚ)) (.mul (.mul (.mul (.qconst (100 : ℚ)) (.var 2)) (.par 6)) (.var 6))) (.mul (.qconst (1 / 100 : ℚ)) (.mul (.mul (.qconst (100 : ℚ)) (.par 16)) (.var 3)))),
  (.sub (.mul (.qconst (1 / 100 : ℚ)) (.mul (.mul (.qconst (100 : ℚ)) (.par 16)) (.var 3))) (.mul (.qconst (1 / 100 : ℚ)) (.mul (.mul (.qconst (100 : ℚ)) (.par 15)) (.var 4)))),
  (.add (.sub (.sub (.qconst (0 : ℚ)) (.mul (.qconst (1 / 100 : ℚ)) (.mul (.qconst (100 : ℚ)) (.div (.mul (.mul (.var 2) (.var 5)) (.par 3)) (.add (.mul (.par 2) (.var 12)) (.qconst (1 : ℚ))))))) (.mul (.qconst (1 / 100 : ℚ)) (.mul (.qconst (100 : ℚ)) (.div (.mul (.mul (.var 5) (.par 3)) (.var 3)) (.add (.mul (.par 2) (.var 12)) (.qconst (1 : ℚ))))))) (.mul (.qconst (1 / 100 : ℚ)) (.mul (.mul (.mul (.qconst (100 : ℚ)) (.qconst (91 : ℚ))) (.var 6)) (.par 14)))),
  (.sub (.add (.mul (.qconst (1 / 100 : ℚ)) (.mul (.qconst (100 : ℚ)) (.div (.mul (.mul (.var 2) (.var 5)) (.par 3)) (.add (.mul (.par 2) (.var 12)) (.qconst (1 : ℚ)))))) (.mul (.qconst (1 / 100 : ℚ)) (.mul (.qconst (100 : ℚ)) (.div (.mul (.mul (.var 5) (.par 3)) (.var 3)) (.add (.mul (.par 2) (.var 12)) (.qconst (1 : ℚ))))))) (.mul (.qconst (1 / 100 : ℚ)) (.mul (.mul (.mul (.qconst (100 : ℚ)) (.qconst (91 : ℚ))) (.var 6)) (.par 14)))),
  (.add (.sub (.qconst (0 : ℚ)) (.mul (.qconst (1 / 100 : ℚ)) (.mul (.mul (.mul (.qconst (100 : ℚ)) (.var 7)) (.par 12)) (.var 6)))) (.mul (.qconst (1 / 100 : ℚ)) (.mul (.mul (.mul (.qconst (100 : ℚ)) (.qconst (91 : ℚ))) (.var 8)) (.par 17)))),
  (.sub (.mul (.qconst (1 / 100 : ℚ)) (.mul (.mul (.mul (.qconst (100 : ℚ)) (.var 7)) (.par 12)) (.var 6))) (.mul (.qconst (1 / 100 : ℚ)) (.mul (.mul (.mul (.qconst (100 : ℚ)) (.qconst (91 : ℚ))) (.var 8)) (.par 17)))),
  (.mul (.qconst (1 / 10 : ℚ)) (.mul (.mul (.qconst (10 : ℚ)) (.par 11)) (.var 8))),
  (.qconst (0 : ℚ)),
  (.qconst (0 : ℚ)),
  (.sub (.mul (.qconst (1 / 100 : ℚ)) (.mul (.qconst (100 : ℚ)) (.div (.mul (.var 9) (.par 10)) (.add (.var 9) (.par 8))))) (.mul (.qconst (1 / 100 : ℚ)) (.mul (.mul (.qconst (100 : ℚ)) (.var 12)) (.par 9)))),
  (.mul (.qconst (1 / 10 : ℚ)) (.mul (.mul (.qconst (10 : ℚ)) (.par 0)) (.var 8)))
]

theorem check : checkModel F = true := by decide +kernel

/-- Diferenciabilidad de la trayectoria (y positividad) para este modelo. -/
def diff := @checked_model_hasFDerivAt _ _ F check

end Models.Raia_CancerResearch2011

#print axioms Models.Raia_CancerResearch2011.diff
