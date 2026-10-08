import KineticCheck

/-! Modelo `Bachmann_MSB2011` traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (25): EpoRJAK2, EpoRpJAK2, p1EpoRpJAK2, p2EpoRpJAK2, p12EpoRpJAK2, EpoRJAK2_CIS, SHP1, SHP1Act, STAT5, pSTAT5, npSTAT5, CISnRNA1, CISnRNA2, CISnRNA3, CISnRNA4, CISnRNA5, CISRNA, CIS, SOCS3nRNA1, SOCS3nRNA2, SOCS3nRNA3, SOCS3nRNA4, SOCS3nRNA5, SOCS3RNA, SOCS3

Parámetros estimados θ (27): CISEqc, CISEqcOE, CISInh, CISRNADelay, CISRNATurn, CISTurn, EpoRActJAK2, EpoRCISInh, EpoRCISRemove, JAK2ActEpo, JAK2EpoRDeaSHP1, SHP1ActEpoR, SHP1Dea, SHP1ProOE, SOCS3Eqc, SOCS3EqcOE, SOCS3Inh, SOCS3RNADelay, SOCS3RNATurn, SOCS3Turn, STAT5ActEpoR, STAT5ActJAK2, STAT5Exp, STAT5Imp, init_EpoRJAK2, init_SHP1, init_STAT5
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck

namespace Models.Bachmann_MSB2011

/-- Máscara de parámetros con valor nominal > 0 (los demás: signo arbitrario). -/
def pos : Fin 27 → Bool := ![true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true]

def F : Fin 25 → KExpr 25 27 := ![
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 1) (KExpr.par 10)) (KExpr.var 7)) (KExpr.par 25)))) (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.par 10) (KExpr.var 7)) (KExpr.var 2)) (KExpr.par 25))))) (KExpr.add (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.par 10) (KExpr.var 7)) (KExpr.var 3)) (KExpr.par 25)))) (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.par 10) (KExpr.var 7)) (KExpr.var 4)) (KExpr.par 25)))))) (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.qconst (1 / 8000000 : ℚ)) (KExpr.var 0)) (KExpr.par 9)) (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 24) (KExpr.par 16)) (KExpr.par 14)) (KExpr.qconst (1 : ℚ))))))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.qconst (1 / 8000000 : ℚ)) (KExpr.var 0)) (KExpr.par 9)) (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 24) (KExpr.par 16)) (KExpr.par 14)) (KExpr.qconst (1 : ℚ)))))) (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 1) (KExpr.par 10)) (KExpr.var 7)) (KExpr.par 25)))) (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 1) (KExpr.par 6)) (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 24) (KExpr.par 16)) (KExpr.par 14)) (KExpr.qconst (1 : ℚ))))))) (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.qconst (3 : ℚ)) (KExpr.var 1)) (KExpr.par 6)) (KExpr.mul (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 24) (KExpr.par 16)) (KExpr.par 14)) (KExpr.qconst (1 : ℚ))) (KExpr.add (KExpr.mul (KExpr.par 7) (KExpr.var 5)) (KExpr.qconst (1 : ℚ))))))))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 1) (KExpr.par 6)) (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 24) (KExpr.par 16)) (KExpr.par 14)) (KExpr.qconst (1 : ℚ)))))) (KExpr.add (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.qconst (3 : ℚ)) (KExpr.par 6)) (KExpr.var 2)) (KExpr.mul (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 24) (KExpr.par 16)) (KExpr.par 14)) (KExpr.qconst (1 : ℚ))) (KExpr.add (KExpr.mul (KExpr.par 7) (KExpr.var 5)) (KExpr.qconst (1 : ℚ))))))) (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.par 10) (KExpr.var 7)) (KExpr.var 2)) (KExpr.par 25)))))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.qconst (3 : ℚ)) (KExpr.var 1)) (KExpr.par 6)) (KExpr.mul (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 24) (KExpr.par 16)) (KExpr.par 14)) (KExpr.qconst (1 : ℚ))) (KExpr.add (KExpr.mul (KExpr.par 7) (KExpr.var 5)) (KExpr.qconst (1 : ℚ))))))) (KExpr.add (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.par 6) (KExpr.var 3)) (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 24) (KExpr.par 16)) (KExpr.par 14)) (KExpr.qconst (1 : ℚ)))))) (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.par 10) (KExpr.var 7)) (KExpr.var 3)) (KExpr.par 25)))))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.qconst (3 : ℚ)) (KExpr.par 6)) (KExpr.var 2)) (KExpr.mul (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 24) (KExpr.par 16)) (KExpr.par 14)) (KExpr.qconst (1 : ℚ))) (KExpr.add (KExpr.mul (KExpr.par 7) (KExpr.var 5)) (KExpr.qconst (1 : ℚ))))))) (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.par 6) (KExpr.var 3)) (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 24) (KExpr.par 16)) (KExpr.par 14)) (KExpr.qconst (1 : ℚ))))))) (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.par 10) (KExpr.var 7)) (KExpr.var 4)) (KExpr.par 25))))),
  (KExpr.sub (KExpr.qconst (0 : ℚ)) (KExpr.add (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 5) (KExpr.par 8)) (KExpr.var 4)) (KExpr.par 24)))) (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 5) (KExpr.par 8)) (KExpr.var 2)) (KExpr.par 24)))))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.par 12)) (KExpr.var 7))) (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 6) (KExpr.par 11)) (KExpr.var 1)) (KExpr.par 24)))) (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 6) (KExpr.par 11)) (KExpr.var 4)) (KExpr.par 24))))) (KExpr.add (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 6) (KExpr.par 11)) (KExpr.var 2)) (KExpr.par 24)))) (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 6) (KExpr.par 11)) (KExpr.var 3)) (KExpr.par 24))))))),
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 6) (KExpr.par 11)) (KExpr.var 1)) (KExpr.par 24)))) (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 6) (KExpr.par 11)) (KExpr.var 4)) (KExpr.par 24))))) (KExpr.add (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 6) (KExpr.par 11)) (KExpr.var 2)) (KExpr.par 24)))) (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 6) (KExpr.par 11)) (KExpr.var 3)) (KExpr.par 24)))))) (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.par 12)) (KExpr.var 7)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.par 22)) (KExpr.var 10))) (KExpr.add (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 8) (KExpr.par 21)) (KExpr.var 1)) (KExpr.mul (KExpr.par 24) (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 24) (KExpr.par 16)) (KExpr.par 14)) (KExpr.qconst (1 : ℚ))))))) (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 8) (KExpr.par 21)) (KExpr.var 4)) (KExpr.mul (KExpr.par 24) (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 24) (KExpr.par 16)) (KExpr.par 14)) (KExpr.qconst (1 : ℚ)))))))) (KExpr.add (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 8) (KExpr.par 21)) (KExpr.var 2)) (KExpr.mul (KExpr.par 24) (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 24) (KExpr.par 16)) (KExpr.par 14)) (KExpr.qconst (1 : ℚ))))))) (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 8) (KExpr.par 21)) (KExpr.var 3)) (KExpr.mul (KExpr.par 24) (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 24) (KExpr.par 16)) (KExpr.par 14)) (KExpr.qconst (1 : ℚ))))))))) (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 8) (KExpr.par 20)) (KExpr.npow (KExpr.add (KExpr.var 4) (KExpr.var 2)) 2)) (KExpr.mul (KExpr.mul (KExpr.npow (KExpr.par 24) 2) (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 24) (KExpr.par 16)) (KExpr.par 14)) (KExpr.qconst (1 : ℚ)))) (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 17) (KExpr.par 2)) (KExpr.par 0)) (KExpr.qconst (1 : ℚ))))))))),
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 8) (KExpr.par 21)) (KExpr.var 1)) (KExpr.mul (KExpr.par 24) (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 24) (KExpr.par 16)) (KExpr.par 14)) (KExpr.qconst (1 : ℚ))))))) (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 8) (KExpr.par 21)) (KExpr.var 4)) (KExpr.mul (KExpr.par 24) (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 24) (KExpr.par 16)) (KExpr.par 14)) (KExpr.qconst (1 : ℚ)))))))) (KExpr.add (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 8) (KExpr.par 21)) (KExpr.var 2)) (KExpr.mul (KExpr.par 24) (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 24) (KExpr.par 16)) (KExpr.par 14)) (KExpr.qconst (1 : ℚ))))))) (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 8) (KExpr.par 21)) (KExpr.var 3)) (KExpr.mul (KExpr.par 24) (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 24) (KExpr.par 16)) (KExpr.par 14)) (KExpr.qconst (1 : ℚ))))))))) (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 8) (KExpr.par 20)) (KExpr.npow (KExpr.add (KExpr.var 4) (KExpr.var 2)) 2)) (KExpr.mul (KExpr.mul (KExpr.npow (KExpr.par 24) 2) (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 24) (KExpr.par 16)) (KExpr.par 14)) (KExpr.qconst (1 : ℚ)))) (KExpr.add (KExpr.div (KExpr.mul (KExpr.var 17) (KExpr.par 2)) (KExpr.par 0)) (KExpr.qconst (1 : ℚ)))))))) (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.par 23)) (KExpr.var 9)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (40 / 11 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.par 23)) (KExpr.var 9))) (KExpr.mul (KExpr.qconst (40 / 11 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.par 22)) (KExpr.var 10)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (40 / 11 : ℚ)) (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 4)) (KExpr.var 10)) (KExpr.qconst (1 / 8000000 : ℚ))) (KExpr.par 26)))) (KExpr.mul (KExpr.qconst (40 / 11 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.var 11)) (KExpr.par 3)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (40 / 11 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.var 11)) (KExpr.par 3))) (KExpr.mul (KExpr.qconst (40 / 11 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.var 12)) (KExpr.par 3)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (40 / 11 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.var 12)) (KExpr.par 3))) (KExpr.mul (KExpr.qconst (40 / 11 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.var 13)) (KExpr.par 3)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (40 / 11 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.var 13)) (KExpr.par 3))) (KExpr.mul (KExpr.qconst (40 / 11 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.var 14)) (KExpr.par 3)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (40 / 11 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.var 14)) (KExpr.par 3))) (KExpr.mul (KExpr.qconst (40 / 11 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.var 15)) (KExpr.par 3)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.var 15)) (KExpr.par 3))) (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.var 16)) (KExpr.par 4)))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 16) (KExpr.par 0)) (KExpr.par 5)) (KExpr.qconst (1 : ℚ))))) (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.par 0)) (KExpr.par 5)) (KExpr.par 1)) (KExpr.qconst (1 / 8000000 : ℚ))))) (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.var 17)) (KExpr.par 5)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (40 / 11 : ℚ)) (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 18)) (KExpr.var 10)) (KExpr.qconst (1 / 8000000 : ℚ))) (KExpr.par 26)))) (KExpr.mul (KExpr.qconst (40 / 11 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.var 18)) (KExpr.par 17)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (40 / 11 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.var 18)) (KExpr.par 17))) (KExpr.mul (KExpr.qconst (40 / 11 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.var 19)) (KExpr.par 17)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (40 / 11 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.var 19)) (KExpr.par 17))) (KExpr.mul (KExpr.qconst (40 / 11 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.var 20)) (KExpr.par 17)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (40 / 11 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.var 20)) (KExpr.par 17))) (KExpr.mul (KExpr.qconst (40 / 11 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.var 21)) (KExpr.par 17)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (40 / 11 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.var 21)) (KExpr.par 17))) (KExpr.mul (KExpr.qconst (40 / 11 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.var 22)) (KExpr.par 17)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (11 / 40 : ℚ)) (KExpr.var 22)) (KExpr.par 17))) (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.var 23)) (KExpr.par 18)))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.var 23) (KExpr.par 14)) (KExpr.par 19)) (KExpr.qconst (1 : ℚ))))) (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.qconst (1 / 8000000 : ℚ))) (KExpr.par 14)) (KExpr.par 19)) (KExpr.par 15)))) (KExpr.mul (KExpr.qconst (5 / 2 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (2 / 5 : ℚ)) (KExpr.var 24)) (KExpr.par 19))))
]

theorem check : checkModel pos F = true := by decide +kernel

/-- θ₀ nominal (PEtab), en racionales exactos. -/
def θq : Fin 27 → ℚ := ![(108213506831433 / 250000000000 : ℚ), (26513614503397 / 50000000000000 : ℚ), (392610522616453 / 500000 : ℚ), (144777009620017 / 1000000000000000 : ℚ), (1000 : ℚ), (4199412514631 / 500000000000000 : ℚ), (267299659481333 / 1000000000000000 : ℚ), (1000000 : ℚ), (542989282766407 / 100000000000000 : ℚ), (633154209632843 / 1000000000 : ℚ), (71361534706159 / 500000000000 : ℚ), (1 / 1000 : ℚ), (8162255244283 / 1000000000000000 : ℚ), (282568032716189 / 100000000000000 : ℚ), (17364095522801 / 100000000000 : ℚ), (679185853534469 / 1000000000000000 : ℚ), (20814851194693 / 2000000000000 : ℚ), (106454014521077 / 100000000000000 : ℚ), (8309263619427 / 1000000000000000 : ℚ), (10000 : ℚ), (194986374447149 / 5000000000000 : ℚ), (4881802078303 / 62500000000000 : ℚ), (4657168677077 / 62500000000000 : ℚ), (26887318057561 / 1000000000000000 : ℚ), (397622379188569 / 100000000000000 : ℚ), (133625582081743 / 5000000000000 : ℚ), (79753639977851 / 1000000000000 : ℚ)]

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

theorem theta_ok : checkPosParams pos θq = true := by decide +kernel

theorem init_ok : checkInit pos G = true := by decide +kernel

/-- Diferenciabilidad de la trayectoria (y positividad) para este modelo. -/
def diff := @checked_model_hasFDerivAt _ _ pos F check

/-- Teorema final (condición inicial dependiente de θ): la única condición
restante es que la solución nominal exista en [0, T]. -/
def final := @checked_model_final_init _ _ pos F check G init_ok θq theta_ok

end Models.Bachmann_MSB2011

#print axioms Models.Bachmann_MSB2011.diff

#print axioms Models.Bachmann_MSB2011.final
