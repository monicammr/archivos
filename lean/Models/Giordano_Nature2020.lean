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

def F0 : Fin 10 → KExpr 10 43 := ![
  (.sub (.sub (.sub (.sub (.qconst (0 : ℚ)) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 0) (.var 1))))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 1) (.var 2))))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 5) (.var 3))))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 2) (.var 4))))),
  (.sub (.sub (.sub (.add (.add (.add (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 0) (.var 1)))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 1) (.var 2))))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 5) (.var 3))))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 2) (.var 4))))) (.mul (.mul (.qconst (1 : ℚ)) (.par 3)) (.var 1))) (.mul (.mul (.qconst (1 : ℚ)) (.par 15)) (.var 1))) (.mul (.mul (.qconst (1 : ℚ)) (.par 7)) (.var 1))),
  (.sub (.sub (.mul (.mul (.qconst (1 : ℚ)) (.par 3)) (.var 1)) (.mul (.mul (.qconst (1 : ℚ)) (.par 4)) (.var 2))) (.mul (.mul (.qconst (1 : ℚ)) (.par 10)) (.var 2))),
  (.sub (.sub (.sub (.mul (.mul (.qconst (1 : ℚ)) (.par 15)) (.var 1)) (.mul (.mul (.qconst (1 : ℚ)) (.par 13)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 6)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 8)) (.var 3))),
  (.sub (.sub (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 4)) (.var 2)) (.mul (.mul (.qconst (1 : ℚ)) (.par 13)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 9)) (.var 4))) (.mul (.mul (.qconst (1 : ℚ)) (.par 14)) (.var 4))),
  (.sub (.sub (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 8)) (.var 3)) (.mul (.mul (.qconst (1 : ℚ)) (.par 9)) (.var 4))) (.mul (.mul (.qconst (1 : ℚ)) (.par 12)) (.var 5))) (.mul (.mul (.qconst (1 : ℚ)) (.par 11)) (.var 5))),
  (.add (.add (.add (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 7)) (.var 1)) (.mul (.mul (.qconst (1 : ℚ)) (.par 10)) (.var 2))) (.mul (.mul (.qconst (1 : ℚ)) (.par 6)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 14)) (.var 4))) (.mul (.mul (.qconst (1 : ℚ)) (.par 11)) (.var 5))),
  (.mul (.mul (.qconst (1 : ℚ)) (.par 12)) (.var 5)),
  (.add (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 3)) (.var 1)) (.mul (.mul (.qconst (1 : ℚ)) (.par 13)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 8)) (.var 3))),
  (.add (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 10)) (.var 2)) (.mul (.mul (.qconst (1 : ℚ)) (.par 14)) (.var 4))) (.mul (.mul (.qconst (1 : ℚ)) (.par 11)) (.var 5)))
]

theorem check0 : checkModel F0 = true := by decide +kernel

def F1 : Fin 10 → KExpr 10 43 := ![
  (.sub (.sub (.sub (.sub (.qconst (0 : ℚ)) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 16) (.var 1))))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 19) (.var 2))))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 27) (.var 3))))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 21) (.var 4))))),
  (.sub (.sub (.sub (.add (.add (.add (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 16) (.var 1)))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 19) (.var 2))))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 27) (.var 3))))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 21) (.var 4))))) (.mul (.mul (.qconst (1 : ℚ)) (.par 3)) (.var 1))) (.mul (.mul (.qconst (1 : ℚ)) (.par 15)) (.var 1))) (.mul (.mul (.qconst (1 : ℚ)) (.par 7)) (.var 1))),
  (.sub (.sub (.mul (.mul (.qconst (1 : ℚ)) (.par 3)) (.var 1)) (.mul (.mul (.qconst (1 : ℚ)) (.par 4)) (.var 2))) (.mul (.mul (.qconst (1 : ℚ)) (.par 10)) (.var 2))),
  (.sub (.sub (.sub (.mul (.mul (.qconst (1 : ℚ)) (.par 15)) (.var 1)) (.mul (.mul (.qconst (1 : ℚ)) (.par 13)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 6)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 8)) (.var 3))),
  (.sub (.sub (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 4)) (.var 2)) (.mul (.mul (.qconst (1 : ℚ)) (.par 13)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 9)) (.var 4))) (.mul (.mul (.qconst (1 : ℚ)) (.par 14)) (.var 4))),
  (.sub (.sub (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 8)) (.var 3)) (.mul (.mul (.qconst (1 : ℚ)) (.par 9)) (.var 4))) (.mul (.mul (.qconst (1 : ℚ)) (.par 12)) (.var 5))) (.mul (.mul (.qconst (1 : ℚ)) (.par 11)) (.var 5))),
  (.add (.add (.add (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 7)) (.var 1)) (.mul (.mul (.qconst (1 : ℚ)) (.par 10)) (.var 2))) (.mul (.mul (.qconst (1 : ℚ)) (.par 6)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 14)) (.var 4))) (.mul (.mul (.qconst (1 : ℚ)) (.par 11)) (.var 5))),
  (.mul (.mul (.qconst (1 : ℚ)) (.par 12)) (.var 5)),
  (.add (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 3)) (.var 1)) (.mul (.mul (.qconst (1 : ℚ)) (.par 13)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 8)) (.var 3))),
  (.add (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 10)) (.var 2)) (.mul (.mul (.qconst (1 : ℚ)) (.par 14)) (.var 4))) (.mul (.mul (.qconst (1 : ℚ)) (.par 11)) (.var 5)))
]

theorem check1 : checkModel F1 = true := by decide +kernel

def F2 : Fin 10 → KExpr 10 43 := ![
  (.sub (.sub (.sub (.sub (.qconst (0 : ℚ)) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 16) (.var 1))))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 19) (.var 2))))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 27) (.var 3))))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 21) (.var 4))))),
  (.sub (.sub (.sub (.add (.add (.add (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 16) (.var 1)))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 19) (.var 2))))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 27) (.var 3))))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 21) (.var 4))))) (.mul (.mul (.qconst (1 : ℚ)) (.par 23)) (.var 1))) (.mul (.mul (.qconst (1 : ℚ)) (.par 15)) (.var 1))) (.mul (.mul (.qconst (1 : ℚ)) (.par 7)) (.var 1))),
  (.sub (.sub (.mul (.mul (.qconst (1 : ℚ)) (.par 23)) (.var 1)) (.mul (.mul (.qconst (1 : ℚ)) (.par 4)) (.var 2))) (.mul (.mul (.qconst (1 : ℚ)) (.par 10)) (.var 2))),
  (.sub (.sub (.sub (.mul (.mul (.qconst (1 : ℚ)) (.par 15)) (.var 1)) (.mul (.mul (.qconst (1 : ℚ)) (.par 13)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 6)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 8)) (.var 3))),
  (.sub (.sub (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 4)) (.var 2)) (.mul (.mul (.qconst (1 : ℚ)) (.par 13)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 9)) (.var 4))) (.mul (.mul (.qconst (1 : ℚ)) (.par 14)) (.var 4))),
  (.sub (.sub (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 8)) (.var 3)) (.mul (.mul (.qconst (1 : ℚ)) (.par 9)) (.var 4))) (.mul (.mul (.qconst (1 : ℚ)) (.par 12)) (.var 5))) (.mul (.mul (.qconst (1 : ℚ)) (.par 11)) (.var 5))),
  (.add (.add (.add (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 7)) (.var 1)) (.mul (.mul (.qconst (1 : ℚ)) (.par 10)) (.var 2))) (.mul (.mul (.qconst (1 : ℚ)) (.par 6)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 14)) (.var 4))) (.mul (.mul (.qconst (1 : ℚ)) (.par 11)) (.var 5))),
  (.mul (.mul (.qconst (1 : ℚ)) (.par 12)) (.var 5)),
  (.add (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 23)) (.var 1)) (.mul (.mul (.qconst (1 : ℚ)) (.par 13)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 8)) (.var 3))),
  (.add (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 10)) (.var 2)) (.mul (.mul (.qconst (1 : ℚ)) (.par 14)) (.var 4))) (.mul (.mul (.qconst (1 : ℚ)) (.par 11)) (.var 5)))
]

theorem check2 : checkModel F2 = true := by decide +kernel

def F3 : Fin 10 → KExpr 10 43 := ![
  (.sub (.sub (.sub (.sub (.qconst (0 : ℚ)) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 17) (.var 1))))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 20) (.var 2))))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 28) (.var 3))))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 22) (.var 4))))),
  (.sub (.sub (.sub (.add (.add (.add (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 17) (.var 1)))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 20) (.var 2))))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 28) (.var 3))))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 22) (.var 4))))) (.mul (.mul (.qconst (1 : ℚ)) (.par 23)) (.var 1))) (.mul (.mul (.qconst (1 : ℚ)) (.par 41)) (.var 1))) (.mul (.mul (.qconst (1 : ℚ)) (.par 32)) (.var 1))),
  (.sub (.sub (.mul (.mul (.qconst (1 : ℚ)) (.par 23)) (.var 1)) (.mul (.mul (.qconst (1 : ℚ)) (.par 25)) (.var 2))) (.mul (.mul (.qconst (1 : ℚ)) (.par 35)) (.var 2))),
  (.sub (.sub (.sub (.mul (.mul (.qconst (1 : ℚ)) (.par 41)) (.var 1)) (.mul (.mul (.qconst (1 : ℚ)) (.par 13)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 30)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 33)) (.var 3))),
  (.sub (.sub (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 25)) (.var 2)) (.mul (.mul (.qconst (1 : ℚ)) (.par 13)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 34)) (.var 4))) (.mul (.mul (.qconst (1 : ℚ)) (.par 39)) (.var 4))),
  (.sub (.sub (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 33)) (.var 3)) (.mul (.mul (.qconst (1 : ℚ)) (.par 34)) (.var 4))) (.mul (.mul (.qconst (1 : ℚ)) (.par 12)) (.var 5))) (.mul (.mul (.qconst (1 : ℚ)) (.par 37)) (.var 5))),
  (.add (.add (.add (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 32)) (.var 1)) (.mul (.mul (.qconst (1 : ℚ)) (.par 35)) (.var 2))) (.mul (.mul (.qconst (1 : ℚ)) (.par 30)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 39)) (.var 4))) (.mul (.mul (.qconst (1 : ℚ)) (.par 37)) (.var 5))),
  (.mul (.mul (.qconst (1 : ℚ)) (.par 12)) (.var 5)),
  (.add (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 23)) (.var 1)) (.mul (.mul (.qconst (1 : ℚ)) (.par 13)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 33)) (.var 3))),
  (.add (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 35)) (.var 2)) (.mul (.mul (.qconst (1 : ℚ)) (.par 39)) (.var 4))) (.mul (.mul (.qconst (1 : ℚ)) (.par 37)) (.var 5)))
]

theorem check3 : checkModel F3 = true := by decide +kernel

def F4 : Fin 10 → KExpr 10 43 := ![
  (.sub (.sub (.sub (.sub (.qconst (0 : ℚ)) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 18) (.var 1))))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 20) (.var 2))))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 29) (.var 3))))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 22) (.var 4))))),
  (.sub (.sub (.sub (.add (.add (.add (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 18) (.var 1)))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 20) (.var 2))))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 29) (.var 3))))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 22) (.var 4))))) (.mul (.mul (.qconst (1 : ℚ)) (.par 23)) (.var 1))) (.mul (.mul (.qconst (1 : ℚ)) (.par 41)) (.var 1))) (.mul (.mul (.qconst (1 : ℚ)) (.par 32)) (.var 1))),
  (.sub (.sub (.mul (.mul (.qconst (1 : ℚ)) (.par 23)) (.var 1)) (.mul (.mul (.qconst (1 : ℚ)) (.par 25)) (.var 2))) (.mul (.mul (.qconst (1 : ℚ)) (.par 35)) (.var 2))),
  (.sub (.sub (.sub (.mul (.mul (.qconst (1 : ℚ)) (.par 41)) (.var 1)) (.mul (.mul (.qconst (1 : ℚ)) (.par 13)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 30)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 33)) (.var 3))),
  (.sub (.sub (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 25)) (.var 2)) (.mul (.mul (.qconst (1 : ℚ)) (.par 13)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 34)) (.var 4))) (.mul (.mul (.qconst (1 : ℚ)) (.par 39)) (.var 4))),
  (.sub (.sub (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 33)) (.var 3)) (.mul (.mul (.qconst (1 : ℚ)) (.par 34)) (.var 4))) (.mul (.mul (.qconst (1 : ℚ)) (.par 12)) (.var 5))) (.mul (.mul (.qconst (1 : ℚ)) (.par 37)) (.var 5))),
  (.add (.add (.add (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 32)) (.var 1)) (.mul (.mul (.qconst (1 : ℚ)) (.par 35)) (.var 2))) (.mul (.mul (.qconst (1 : ℚ)) (.par 30)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 39)) (.var 4))) (.mul (.mul (.qconst (1 : ℚ)) (.par 37)) (.var 5))),
  (.mul (.mul (.qconst (1 : ℚ)) (.par 12)) (.var 5)),
  (.add (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 23)) (.var 1)) (.mul (.mul (.qconst (1 : ℚ)) (.par 13)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 33)) (.var 3))),
  (.add (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 35)) (.var 2)) (.mul (.mul (.qconst (1 : ℚ)) (.par 39)) (.var 4))) (.mul (.mul (.qconst (1 : ℚ)) (.par 37)) (.var 5)))
]

theorem check4 : checkModel F4 = true := by decide +kernel

def F5 : Fin 10 → KExpr 10 43 := ![
  (.sub (.sub (.sub (.sub (.qconst (0 : ℚ)) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 18) (.var 1))))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 20) (.var 2))))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 29) (.var 3))))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 22) (.var 4))))),
  (.sub (.sub (.sub (.add (.add (.add (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 18) (.var 1)))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 20) (.var 2))))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 29) (.var 3))))) (.mul (.qconst (1 : ℚ)) (.mul (.var 0) (.mul (.par 22) (.var 4))))) (.mul (.mul (.qconst (1 : ℚ)) (.par 24)) (.var 1))) (.mul (.mul (.qconst (1 : ℚ)) (.par 42)) (.var 1))) (.mul (.mul (.qconst (1 : ℚ)) (.par 32)) (.var 1))),
  (.sub (.sub (.mul (.mul (.qconst (1 : ℚ)) (.par 24)) (.var 1)) (.mul (.mul (.qconst (1 : ℚ)) (.par 26)) (.var 2))) (.mul (.mul (.qconst (1 : ℚ)) (.par 36)) (.var 2))),
  (.sub (.sub (.sub (.mul (.mul (.qconst (1 : ℚ)) (.par 42)) (.var 1)) (.mul (.mul (.qconst (1 : ℚ)) (.par 13)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 31)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 33)) (.var 3))),
  (.sub (.sub (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 26)) (.var 2)) (.mul (.mul (.qconst (1 : ℚ)) (.par 13)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 34)) (.var 4))) (.mul (.mul (.qconst (1 : ℚ)) (.par 40)) (.var 4))),
  (.sub (.sub (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 33)) (.var 3)) (.mul (.mul (.qconst (1 : ℚ)) (.par 34)) (.var 4))) (.mul (.mul (.qconst (1 : ℚ)) (.par 12)) (.var 5))) (.mul (.mul (.qconst (1 : ℚ)) (.par 38)) (.var 5))),
  (.add (.add (.add (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 32)) (.var 1)) (.mul (.mul (.qconst (1 : ℚ)) (.par 36)) (.var 2))) (.mul (.mul (.qconst (1 : ℚ)) (.par 31)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 40)) (.var 4))) (.mul (.mul (.qconst (1 : ℚ)) (.par 38)) (.var 5))),
  (.mul (.mul (.qconst (1 : ℚ)) (.par 12)) (.var 5)),
  (.add (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 24)) (.var 1)) (.mul (.mul (.qconst (1 : ℚ)) (.par 13)) (.var 3))) (.mul (.mul (.qconst (1 : ℚ)) (.par 33)) (.var 3))),
  (.add (.add (.mul (.mul (.qconst (1 : ℚ)) (.par 36)) (.var 2)) (.mul (.mul (.qconst (1 : ℚ)) (.par 40)) (.var 4))) (.mul (.mul (.qconst (1 : ℚ)) (.par 38)) (.var 5)))
]

theorem check5 : checkModel F5 = true := by decide +kernel

def Fseg : ℕ → Fin 10 → KExpr 10 43
  | 0 => F0
  | 1 => F1
  | 2 => F2
  | 3 => F3
  | 4 => F4
  | _ => F5

theorem check : ∀ k, checkModel (Fseg k) = true := by
  intro k
  match k with
  | 0 => exact check0
  | 1 => exact check1
  | 2 => exact check2
  | 3 => exact check3
  | 4 => exact check4
  | _ + 5 => exact check5

/-- Diferenciabilidad de la trayectoria en todos los tramos. -/
def diff := @checked_segments_hasFDerivAt _ _ Fseg check

end Models.Giordano_Nature2020

#print axioms Models.Giordano_Nature2020.diff
