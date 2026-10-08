import KineticCheck

/-! Modelo `Armistead_CellDeathDis2024` traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (4): Cer, Sphingo, S1P, Sphinga

Parámetros estimados θ (10): k00, k0, k_d, k1, k2, k3, k4, k5, alpha_hai1a, alpha_cer
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck

namespace Models.Armistead_CellDeathDis2024

/-- Máscara de parámetros con valor nominal > 0 (los demás: signo arbitrario). -/
def pos : Fin 10 → Bool := ![true, true, true, true, true, true, true, true, true, false]

def F : Fin 4 → KExpr 4 10 := ![
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.par 1) (KExpr.var 3)) (KExpr.mul (KExpr.par 4) (KExpr.var 1))) (KExpr.add (KExpr.mul (KExpr.par 3) (KExpr.var 0)) (KExpr.mul (KExpr.par 2) (KExpr.var 0)))),
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 3) (KExpr.var 0)) (KExpr.mul (KExpr.mul (KExpr.par 5) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 8))) (KExpr.var 1))) (KExpr.mul (KExpr.par 6) (KExpr.var 2))) (KExpr.add (KExpr.mul (KExpr.par 4) (KExpr.var 1)) (KExpr.mul (KExpr.mul (KExpr.par 5) (KExpr.qconst (1 : ℚ))) (KExpr.var 1)))),
  (KExpr.sub (KExpr.mul (KExpr.mul (KExpr.par 5) (KExpr.qconst (1 : ℚ))) (KExpr.var 1)) (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.par 5) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 8))) (KExpr.var 1)) (KExpr.mul (KExpr.par 6) (KExpr.var 2))) (KExpr.mul (KExpr.par 7) (KExpr.var 2)))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.par 0) (KExpr.qconst (1 : ℚ))) (KExpr.mul (KExpr.par 0) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 9)))) (KExpr.mul (KExpr.par 1) (KExpr.var 3)))
]

/-- La comprobación sintáctica FALLA para este modelo (ver el informe JSON). -/
theorem check_falla : checkModel pos F = false := by decide +kernel

/-- **Diferenciabilidad con condiciones explícitas.** El campo es C¹ en su dominio
(demostrado para todo `KExpr`); quedan como condiciones que la solución nominal
exista en [0, T] y permanezca en el dominio (para este modelo el comprobador
sintáctico no puede garantizarlo; ver `check_falla`). -/
def diff := @kinetic_hasFDerivAt _ _ F

end Models.Armistead_CellDeathDis2024

#print axioms Models.Armistead_CellDeathDis2024.diff
