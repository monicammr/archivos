import KineticCheck

/-! Modelo `Fiedler_BMCSystBiol2016` traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (7): RAF, pRAF, MEK, pMEK, ERK, pERK, τ (tiempo)

Parámetros estimados θ (12): K_1, K_2, K_3, k10, k11, k2, k3, k4, k5, k6, tau1, tau2
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck

namespace Models.Fiedler_BMCSystBiol2016

/-- Máscara de parámetros con valor nominal > 0 (los demás: signo arbitrario). -/
def pos : Fin 12 → Bool := ![true, true, true, true, true, true, true, true, true, true, true, true]

def F : Fin 7 → KExpr 7 12 := ![
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.par 0) (KExpr.var 0)) (KExpr.mul (KExpr.mul (KExpr.par 4) (KExpr.exp (KExpr.div (KExpr.sub (KExpr.qconst (0 : ℚ)) (KExpr.var 6)) (KExpr.par 11)))) (KExpr.exp (KExpr.div (KExpr.sub (KExpr.qconst (0 : ℚ)) (KExpr.var 6)) (KExpr.par 10))))) (KExpr.add (KExpr.par 0) (KExpr.var 5)))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 5)) (KExpr.var 1))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.par 0) (KExpr.var 0)) (KExpr.par 3)) (KExpr.add (KExpr.par 0) (KExpr.var 5)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.par 0) (KExpr.var 0)) (KExpr.mul (KExpr.mul (KExpr.par 4) (KExpr.exp (KExpr.div (KExpr.sub (KExpr.qconst (0 : ℚ)) (KExpr.var 6)) (KExpr.par 11)))) (KExpr.qconst (1 : ℚ)))) (KExpr.add (KExpr.par 0) (KExpr.var 5)))))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.par 0) (KExpr.var 0)) (KExpr.par 3)) (KExpr.add (KExpr.par 0) (KExpr.var 5)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.par 0) (KExpr.var 0)) (KExpr.mul (KExpr.mul (KExpr.par 4) (KExpr.exp (KExpr.div (KExpr.sub (KExpr.qconst (0 : ℚ)) (KExpr.var 6)) (KExpr.par 11)))) (KExpr.qconst (1 : ℚ)))) (KExpr.add (KExpr.par 0) (KExpr.var 5))))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.par 0) (KExpr.var 0)) (KExpr.mul (KExpr.mul (KExpr.par 4) (KExpr.exp (KExpr.div (KExpr.sub (KExpr.qconst (0 : ℚ)) (KExpr.var 6)) (KExpr.par 11)))) (KExpr.exp (KExpr.div (KExpr.sub (KExpr.qconst (0 : ℚ)) (KExpr.var 6)) (KExpr.par 10))))) (KExpr.add (KExpr.par 0) (KExpr.var 5)))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 5)) (KExpr.var 1)))),
  (KExpr.sub (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 7)) (KExpr.var 3)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.par 1) (KExpr.var 2)) (KExpr.par 6)) (KExpr.var 1)) (KExpr.par 1)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.par 1) (KExpr.var 2)) (KExpr.par 6)) (KExpr.var 1)) (KExpr.par 1))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 7)) (KExpr.var 3))),
  (KExpr.sub (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 9)) (KExpr.var 5)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.var 4) (KExpr.par 2)) (KExpr.par 8)) (KExpr.var 3)) (KExpr.par 2)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.var 4) (KExpr.par 2)) (KExpr.par 8)) (KExpr.var 3)) (KExpr.par 2))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 9)) (KExpr.var 5))),
  (KExpr.qconst (1 : ℚ))
]

/-- La comprobación sintáctica FALLA para este modelo (ver el informe JSON). -/
theorem check_falla : checkModel pos F = false := by decide +kernel

/-- **Diferenciabilidad con condiciones explícitas.** El campo es C¹ en su dominio
(demostrado para todo `KExpr`); quedan como condiciones que la solución nominal
exista en [0, T] y permanezca en el dominio (para este modelo el comprobador
sintáctico no puede garantizarlo; ver `check_falla`). -/
def diff := @kinetic_hasFDerivAt _ _ F

end Models.Fiedler_BMCSystBiol2016

#print axioms Models.Fiedler_BMCSystBiol2016.diff
