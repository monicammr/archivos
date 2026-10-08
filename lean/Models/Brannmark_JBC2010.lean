import KineticCheck

/-! Modelo `Brannmark_JBC2010` traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (9): IR, IRins, IRp, IRiP, IRi, IRS, IRSiP, X, Xp

Parámetros estimados θ (15): k1a, k1aBasic, k1b, k1c, k1d, k1e, k1f, k1g, k1r, k21, k22, k3, k_IRSiP_DosR, km2, km3
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck

namespace Models.Brannmark_JBC2010

/-- Máscara de parámetros con valor nominal > 0 (los demás: signo arbitrario). -/
def pos : Fin 15 → Bool := ![true, true, true, true, true, true, true, true, true, true, true, true, true, true, true]

def F : Fin 9 → KExpr 9 15 := ![
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 1)) (KExpr.par 2)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 2)) (KExpr.par 7))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 4)) (KExpr.par 8))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.par 1))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.qconst (3 / 10 : ℚ)) (KExpr.qconst (1 : ℚ)))) (KExpr.par 0))))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.par 1))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.qconst (3 / 10 : ℚ)) (KExpr.qconst (1 : ℚ)))) (KExpr.par 0)))) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 1)) (KExpr.par 2)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 1)) (KExpr.par 3)))),
  (KExpr.sub (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 1)) (KExpr.par 3)) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 2)) (KExpr.par 4)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 2)) (KExpr.par 7)))),
  (KExpr.sub (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 2)) (KExpr.par 4)) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 3)) (KExpr.par 5)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 3)) (KExpr.div (KExpr.mul (KExpr.var 8) (KExpr.par 6)) (KExpr.add (KExpr.var 8) (KExpr.qconst (1 : ℚ))))))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 3)) (KExpr.par 5)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 3)) (KExpr.div (KExpr.mul (KExpr.var 8) (KExpr.par 6)) (KExpr.add (KExpr.var 8) (KExpr.qconst (1 : ℚ)))))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 4)) (KExpr.par 8))),
  (KExpr.sub (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 6)) (KExpr.par 13)) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 5)) (KExpr.par 9)) (KExpr.var 2)) (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 5)) (KExpr.par 9)) (KExpr.mul (KExpr.var 3) (KExpr.par 10))))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 5)) (KExpr.par 9)) (KExpr.var 2)) (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 5)) (KExpr.par 9)) (KExpr.mul (KExpr.var 3) (KExpr.par 10)))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 6)) (KExpr.par 13))),
  (KExpr.sub (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 8)) (KExpr.par 14)) (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 6)) (KExpr.var 7)) (KExpr.par 11))),
  (KExpr.sub (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 6)) (KExpr.var 7)) (KExpr.par 11)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 8)) (KExpr.par 14)))
]

theorem check : checkModel pos F = true := by decide +kernel

/-- θ₀ nominal (PEtab), en racionales exactos. -/
def θq : Fin 15 → ℚ := ![(177219477727669 / 1000000000000000 : ℚ), (392767904337 / 1000000000000000 : ℚ), (174695978547559 / 1000000000000000 : ℚ), (50857471885817 / 1000000000000000 : ℚ), (499999999999977 / 1000000000 : ℚ), (100000000000009 / 100000000000000000000 : ℚ), (1562499975013 / 3125000 : ℚ), (17293765495871 / 10000000000 : ℚ), (26696391080189 / 1000000000000000 : ℚ), (105119082752209 / 50000000000000 : ℚ), (1333671147959 / 2000000000 : ℚ), (494410392362901 / 10000000000000000000 : ℚ), (7588703588757 / 200000000000 : ℚ), (7248171355653 / 6250000000000 : ℚ), (83276500181357 / 200000000000000 : ℚ)]

/-- Condiciones iniciales nominales (no dependen de θ). -/
def xq : Fin 9 → ℚ := ![(994957642787569 / 100000000000000 : ℚ), (173972221725393 / 10000000000000000 : ℚ), (17629010620181 / 10000000000000000000000 : ℚ), (13948753269037 / 1250000000000000000 : ℚ), (330151891862681 / 10000000000000000 : ℚ), (986699348701367 / 100000000000000 : ℚ), (4156453530823 / 31250000000000 : ℚ), (999984199487351 / 100000000000000 : ℚ), (4937660203059 / 31250000000000000 : ℚ)]

theorem theta_ok : checkPosParams pos θq = true := by decide +kernel

theorem x0_ok : checkNonneg xq = true := by decide +kernel

/-- Diferenciabilidad de la trayectoria (y positividad) para este modelo. -/
def diff := @checked_model_hasFDerivAt _ _ pos F check

/-- Teorema final: la única condición restante es que la solución nominal
exista en [0, T]. -/
def final := @checked_model_final _ _ pos F check θq theta_ok xq x0_ok

end Models.Brannmark_JBC2010

#print axioms Models.Brannmark_JBC2010.diff

#print axioms Models.Brannmark_JBC2010.final
