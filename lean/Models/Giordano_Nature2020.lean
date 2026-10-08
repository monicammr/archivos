import KineticCheck

/-! Modelo `Giordano_Nature2020` traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (10): Susceptible, Infected, Diagnosed, Ailing, Recognized, Threatened, Healed, Extinct, CumulativeDiagnosed, DiagnosedHealed

Parámetros estimados θ (43): alpha_0, beta_0, delta_0, epsilon_0, eta_0, gamma_0, kappa_0, lam_0, mu_0, nu_0, rho_0, sigma_0, tau, theta, xi_0, zeta_0, alpha_4, alpha_22, alpha_28, beta_4, beta_22, delta_4, delta_22, epsilon_12, epsilon_38, eta_22, eta_38, gamma_4, gamma_22, gamma_28, kappa_22, kappa_38, lam_22, mu_22, nu_22, rho_22, rho_38, sigma_22, sigma_38, xi_22, xi_38, zeta_22, zeta_38

Tramos (entradas por escalones en tiempos fijos): [0, 4], [4, 12], [12, 22], [22, 28], [28, 38], [38, 50]
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck

namespace Models.Giordano_Nature2020

/-- Máscara de parámetros con valor nominal > 0 (los demás: signo arbitrario). -/
def pos : Fin 43 → Bool := ![true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true]

def F0 : Fin 10 → KExpr 10 43 := ![
  (KExpr.sub (KExpr.qconst (0 : ℚ)) (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 0) (KExpr.var 1)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 1) (KExpr.var 2))))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 5) (KExpr.var 3)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 2) (KExpr.var 4))))))),
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 0) (KExpr.var 1)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 1) (KExpr.var 2))))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 5) (KExpr.var 3)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 2) (KExpr.var 4)))))) (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 3)) (KExpr.var 1)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 15)) (KExpr.var 1))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 7)) (KExpr.var 1)))),
  (KExpr.sub (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 3)) (KExpr.var 1)) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 4)) (KExpr.var 2)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 10)) (KExpr.var 2)))),
  (KExpr.sub (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 15)) (KExpr.var 1)) (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 13)) (KExpr.var 3)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 6)) (KExpr.var 3))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 8)) (KExpr.var 3)))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 4)) (KExpr.var 2)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 13)) (KExpr.var 3))) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 9)) (KExpr.var 4)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 14)) (KExpr.var 4)))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 8)) (KExpr.var 3)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 9)) (KExpr.var 4))) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 12)) (KExpr.var 5)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 11)) (KExpr.var 5)))),
  (KExpr.add (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 7)) (KExpr.var 1)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 10)) (KExpr.var 2))) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 6)) (KExpr.var 3)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 14)) (KExpr.var 4)))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 11)) (KExpr.var 5))),
  (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 12)) (KExpr.var 5)),
  (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 3)) (KExpr.var 1)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 13)) (KExpr.var 3))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 8)) (KExpr.var 3))),
  (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 10)) (KExpr.var 2)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 14)) (KExpr.var 4))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 11)) (KExpr.var 5)))
]

theorem check0 : checkModel pos F0 = true := by decide +kernel

def F1 : Fin 10 → KExpr 10 43 := ![
  (KExpr.sub (KExpr.qconst (0 : ℚ)) (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 16) (KExpr.var 1)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 19) (KExpr.var 2))))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 27) (KExpr.var 3)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 21) (KExpr.var 4))))))),
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 16) (KExpr.var 1)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 19) (KExpr.var 2))))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 27) (KExpr.var 3)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 21) (KExpr.var 4)))))) (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 3)) (KExpr.var 1)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 15)) (KExpr.var 1))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 7)) (KExpr.var 1)))),
  (KExpr.sub (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 3)) (KExpr.var 1)) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 4)) (KExpr.var 2)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 10)) (KExpr.var 2)))),
  (KExpr.sub (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 15)) (KExpr.var 1)) (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 13)) (KExpr.var 3)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 6)) (KExpr.var 3))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 8)) (KExpr.var 3)))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 4)) (KExpr.var 2)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 13)) (KExpr.var 3))) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 9)) (KExpr.var 4)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 14)) (KExpr.var 4)))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 8)) (KExpr.var 3)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 9)) (KExpr.var 4))) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 12)) (KExpr.var 5)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 11)) (KExpr.var 5)))),
  (KExpr.add (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 7)) (KExpr.var 1)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 10)) (KExpr.var 2))) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 6)) (KExpr.var 3)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 14)) (KExpr.var 4)))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 11)) (KExpr.var 5))),
  (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 12)) (KExpr.var 5)),
  (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 3)) (KExpr.var 1)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 13)) (KExpr.var 3))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 8)) (KExpr.var 3))),
  (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 10)) (KExpr.var 2)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 14)) (KExpr.var 4))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 11)) (KExpr.var 5)))
]

theorem check1 : checkModel pos F1 = true := by decide +kernel

def F2 : Fin 10 → KExpr 10 43 := ![
  (KExpr.sub (KExpr.qconst (0 : ℚ)) (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 16) (KExpr.var 1)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 19) (KExpr.var 2))))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 27) (KExpr.var 3)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 21) (KExpr.var 4))))))),
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 16) (KExpr.var 1)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 19) (KExpr.var 2))))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 27) (KExpr.var 3)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 21) (KExpr.var 4)))))) (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 23)) (KExpr.var 1)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 15)) (KExpr.var 1))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 7)) (KExpr.var 1)))),
  (KExpr.sub (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 23)) (KExpr.var 1)) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 4)) (KExpr.var 2)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 10)) (KExpr.var 2)))),
  (KExpr.sub (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 15)) (KExpr.var 1)) (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 13)) (KExpr.var 3)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 6)) (KExpr.var 3))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 8)) (KExpr.var 3)))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 4)) (KExpr.var 2)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 13)) (KExpr.var 3))) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 9)) (KExpr.var 4)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 14)) (KExpr.var 4)))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 8)) (KExpr.var 3)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 9)) (KExpr.var 4))) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 12)) (KExpr.var 5)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 11)) (KExpr.var 5)))),
  (KExpr.add (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 7)) (KExpr.var 1)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 10)) (KExpr.var 2))) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 6)) (KExpr.var 3)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 14)) (KExpr.var 4)))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 11)) (KExpr.var 5))),
  (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 12)) (KExpr.var 5)),
  (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 23)) (KExpr.var 1)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 13)) (KExpr.var 3))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 8)) (KExpr.var 3))),
  (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 10)) (KExpr.var 2)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 14)) (KExpr.var 4))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 11)) (KExpr.var 5)))
]

theorem check2 : checkModel pos F2 = true := by decide +kernel

def F3 : Fin 10 → KExpr 10 43 := ![
  (KExpr.sub (KExpr.qconst (0 : ℚ)) (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 17) (KExpr.var 1)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 20) (KExpr.var 2))))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 28) (KExpr.var 3)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 22) (KExpr.var 4))))))),
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 17) (KExpr.var 1)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 20) (KExpr.var 2))))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 28) (KExpr.var 3)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 22) (KExpr.var 4)))))) (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 23)) (KExpr.var 1)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 41)) (KExpr.var 1))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 32)) (KExpr.var 1)))),
  (KExpr.sub (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 23)) (KExpr.var 1)) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 25)) (KExpr.var 2)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 35)) (KExpr.var 2)))),
  (KExpr.sub (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 41)) (KExpr.var 1)) (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 13)) (KExpr.var 3)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 30)) (KExpr.var 3))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 33)) (KExpr.var 3)))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 25)) (KExpr.var 2)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 13)) (KExpr.var 3))) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 34)) (KExpr.var 4)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 39)) (KExpr.var 4)))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 33)) (KExpr.var 3)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 34)) (KExpr.var 4))) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 12)) (KExpr.var 5)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 37)) (KExpr.var 5)))),
  (KExpr.add (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 32)) (KExpr.var 1)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 35)) (KExpr.var 2))) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 30)) (KExpr.var 3)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 39)) (KExpr.var 4)))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 37)) (KExpr.var 5))),
  (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 12)) (KExpr.var 5)),
  (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 23)) (KExpr.var 1)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 13)) (KExpr.var 3))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 33)) (KExpr.var 3))),
  (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 35)) (KExpr.var 2)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 39)) (KExpr.var 4))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 37)) (KExpr.var 5)))
]

theorem check3 : checkModel pos F3 = true := by decide +kernel

def F4 : Fin 10 → KExpr 10 43 := ![
  (KExpr.sub (KExpr.qconst (0 : ℚ)) (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 18) (KExpr.var 1)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 20) (KExpr.var 2))))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 29) (KExpr.var 3)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 22) (KExpr.var 4))))))),
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 18) (KExpr.var 1)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 20) (KExpr.var 2))))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 29) (KExpr.var 3)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 22) (KExpr.var 4)))))) (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 23)) (KExpr.var 1)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 41)) (KExpr.var 1))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 32)) (KExpr.var 1)))),
  (KExpr.sub (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 23)) (KExpr.var 1)) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 25)) (KExpr.var 2)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 35)) (KExpr.var 2)))),
  (KExpr.sub (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 41)) (KExpr.var 1)) (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 13)) (KExpr.var 3)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 30)) (KExpr.var 3))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 33)) (KExpr.var 3)))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 25)) (KExpr.var 2)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 13)) (KExpr.var 3))) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 34)) (KExpr.var 4)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 39)) (KExpr.var 4)))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 33)) (KExpr.var 3)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 34)) (KExpr.var 4))) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 12)) (KExpr.var 5)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 37)) (KExpr.var 5)))),
  (KExpr.add (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 32)) (KExpr.var 1)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 35)) (KExpr.var 2))) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 30)) (KExpr.var 3)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 39)) (KExpr.var 4)))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 37)) (KExpr.var 5))),
  (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 12)) (KExpr.var 5)),
  (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 23)) (KExpr.var 1)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 13)) (KExpr.var 3))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 33)) (KExpr.var 3))),
  (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 35)) (KExpr.var 2)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 39)) (KExpr.var 4))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 37)) (KExpr.var 5)))
]

theorem check4 : checkModel pos F4 = true := by decide +kernel

def F5 : Fin 10 → KExpr 10 43 := ![
  (KExpr.sub (KExpr.qconst (0 : ℚ)) (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 18) (KExpr.var 1)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 20) (KExpr.var 2))))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 29) (KExpr.var 3)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 22) (KExpr.var 4))))))),
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 18) (KExpr.var 1)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 20) (KExpr.var 2))))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 29) (KExpr.var 3)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 22) (KExpr.var 4)))))) (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 24)) (KExpr.var 1)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 42)) (KExpr.var 1))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 32)) (KExpr.var 1)))),
  (KExpr.sub (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 24)) (KExpr.var 1)) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 26)) (KExpr.var 2)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 36)) (KExpr.var 2)))),
  (KExpr.sub (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 42)) (KExpr.var 1)) (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 13)) (KExpr.var 3)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 31)) (KExpr.var 3))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 33)) (KExpr.var 3)))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 26)) (KExpr.var 2)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 13)) (KExpr.var 3))) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 34)) (KExpr.var 4)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 40)) (KExpr.var 4)))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 33)) (KExpr.var 3)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 34)) (KExpr.var 4))) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 12)) (KExpr.var 5)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 38)) (KExpr.var 5)))),
  (KExpr.add (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 32)) (KExpr.var 1)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 36)) (KExpr.var 2))) (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 31)) (KExpr.var 3)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 40)) (KExpr.var 4)))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 38)) (KExpr.var 5))),
  (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 12)) (KExpr.var 5)),
  (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 24)) (KExpr.var 1)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 13)) (KExpr.var 3))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 33)) (KExpr.var 3))),
  (KExpr.add (KExpr.add (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 36)) (KExpr.var 2)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 40)) (KExpr.var 4))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 38)) (KExpr.var 5)))
]

theorem check5 : checkModel pos F5 = true := by decide +kernel

/-- θ₀ nominal (PEtab), en racionales exactos. -/
def θq : Fin 43 → ℚ := ![(57 / 100 : ℚ), (11 / 1000 : ℚ), (11 / 1000 : ℚ), (171 / 1000 : ℚ), (1 / 8 : ℚ), (57 / 125 : ℚ), (17 / 1000 : ℚ), (17 / 500 : ℚ), (17 / 1000 : ℚ), (27 / 1000 : ℚ), (17 / 500 : ℚ), (17 / 1000 : ℚ), (1 / 100 : ℚ), (371 / 1000 : ℚ), (17 / 1000 : ℚ), (1 / 8 : ℚ), (211 / 500 : ℚ), (9 / 25 : ℚ), (21 / 100 : ℚ), (57 / 10000 : ℚ), (1 / 200 : ℚ), (57 / 10000 : ℚ), (1 / 200 : ℚ), (143 / 1000 : ℚ), (1 / 5 : ℚ), (17 / 500 : ℚ), (1 / 40 : ℚ), (57 / 200 : ℚ), (1 / 5 : ℚ), (11 / 100 : ℚ), (17 / 1000 : ℚ), (1 / 50 : ℚ), (2 / 25 : ℚ), (1 / 125 : ℚ), (3 / 200 : ℚ), (17 / 1000 : ℚ), (1 / 50 : ℚ), (17 / 1000 : ℚ), (1 / 100 : ℚ), (17 / 1000 : ℚ), (1 / 50 : ℚ), (17 / 500 : ℚ), (1 / 40 : ℚ)]

/-- Condiciones iniciales nominales (no dependen de θ). -/
def xq : Fin 10 → ℚ := ![(9999963 / 10000000 : ℚ), (333333333 / 100000000000000 : ℚ), (333333333 / 1000000000000000 : ℚ), (83333333 / 5000000000000000 : ℚ), (333333333 / 10000000000000000 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (3666666662999999 / 10000000000000000000000 : ℚ), (0 : ℚ)]

theorem theta_ok : checkPosParams pos θq = true := by decide +kernel

theorem x0_ok : checkNonneg xq = true := by decide +kernel

def Fseg : ℕ → Fin 10 → KExpr 10 43
  | 0 => F0
  | 1 => F1
  | 2 => F2
  | 3 => F3
  | 4 => F4
  | _ => F5

theorem check : ∀ k, checkModel pos (Fseg k) = true := by
  intro k
  match k with
  | 0 => exact check0
  | 1 => exact check1
  | 2 => exact check2
  | 3 => exact check3
  | 4 => exact check4
  | _ + 5 => exact check5

/-- Diferenciabilidad de la trayectoria en todos los tramos. -/
def diff := @checked_segments_hasFDerivAt _ _ pos Fseg check

/-- Teorema final: la única condición restante es que la solución nominal
exista en cada tramo. -/
def final := @checked_segments_final _ _ pos Fseg check θq theta_ok xq x0_ok

end Models.Giordano_Nature2020

#print axioms Models.Giordano_Nature2020.diff

#print axioms Models.Giordano_Nature2020.final
