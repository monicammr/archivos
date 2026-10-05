import KineticCheck

/-! Modelo `Okuonghae_ChaosSolitonsFractals2020` traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (8): susceptible, exposed, asymptomatic, symptomatic, detected, recovered, deceased, detected_cumulative

Parámetros estimados θ (14): alpha, d_0, d_D, gamma_0, gamma_a, gamma_i, nu, psi, sigma, theta, asymptomatic_start, symptomatic_start, exposed_start, transmission_rate_effective
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck

namespace Models.Okuonghae_ChaosSolitonsFractals2020

/-- Máscara de parámetros con valor nominal > 0 (los demás: signo arbitrario). -/
def pos : Fin 14 → Bool := ![true, true, true, true, true, true, true, true, true, true, true, true, true, true]

def F : Fin 8 → KExpr 8 14 := ![
  (KExpr.sub (KExpr.qconst (0 : ℚ)) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.par 13) (KExpr.qconst (1 / 5 : ℚ))) (KExpr.qconst (1 : ℚ))) (KExpr.mul (KExpr.par 0) (KExpr.var 2))) (KExpr.sub (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.var 2) (KExpr.var 4)) (KExpr.var 1)) (KExpr.var 5)) (KExpr.var 0)) (KExpr.var 3)) (KExpr.var 4)))) (KExpr.var 0)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.par 13) (KExpr.qconst (1 / 5 : ℚ))) (KExpr.qconst (1 : ℚ))) (KExpr.var 3)) (KExpr.sub (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.var 2) (KExpr.var 4)) (KExpr.var 1)) (KExpr.var 5)) (KExpr.var 0)) (KExpr.var 3)) (KExpr.var 4)))) (KExpr.var 0)))),
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.par 13) (KExpr.qconst (1 / 5 : ℚ))) (KExpr.qconst (1 : ℚ))) (KExpr.mul (KExpr.par 0) (KExpr.var 2))) (KExpr.sub (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.var 2) (KExpr.var 4)) (KExpr.var 1)) (KExpr.var 5)) (KExpr.var 0)) (KExpr.var 3)) (KExpr.var 4)))) (KExpr.var 0)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.par 13) (KExpr.qconst (1 / 5 : ℚ))) (KExpr.qconst (1 : ℚ))) (KExpr.var 3)) (KExpr.sub (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.add (KExpr.var 2) (KExpr.var 4)) (KExpr.var 1)) (KExpr.var 5)) (KExpr.var 0)) (KExpr.var 3)) (KExpr.var 4)))) (KExpr.var 0))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.par 8) (KExpr.par 6)) (KExpr.var 1)))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.par 8) (KExpr.qconst (1 : ℚ))) (KExpr.var 1))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.par 8) (KExpr.par 6)) (KExpr.var 1))))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.par 8) (KExpr.par 6)) (KExpr.var 1))) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 9)) (KExpr.var 2)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 4)) (KExpr.var 2)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.par 8) (KExpr.qconst (1 : ℚ))) (KExpr.var 1))) (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.par 8) (KExpr.par 6)) (KExpr.var 1))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 7)) (KExpr.var 3))) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 3)) (KExpr.var 3)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 1)) (KExpr.var 3))))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 7)) (KExpr.var 3)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 9)) (KExpr.var 2))) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 5)) (KExpr.var 4)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 2)) (KExpr.var 4)))),
  (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 3)) (KExpr.var 3)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 4)) (KExpr.var 2))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 5)) (KExpr.var 4))),
  (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 1)) (KExpr.var 3)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 2)) (KExpr.var 4))),
  (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 7)) (KExpr.var 3)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 9)) (KExpr.var 2)))
]

/-- La comprobación sintáctica FALLA para este modelo (ver el informe JSON). -/
theorem check_falla : checkModel pos F = false := by decide +kernel

end Models.Okuonghae_ChaosSolitonsFractals2020
