import KineticNetwork

/-! Modelo `Giordano_Nature2020` (forma de red, 6 tramos), traducido automáticamente de
SBML por `certificados/sbml_to_lean.py`. No editar a mano.

Estados (10): Susceptible, Infected, Diagnosed, Ailing, Recognized, Threatened, Healed, Extinct, CumulativeDiagnosed, DiagnosedHealed

Parámetros estimados θ (43): alpha_0, beta_0, delta_0, epsilon_0, eta_0, gamma_0, kappa_0, lam_0, mu_0, nu_0, rho_0, sigma_0, tau, theta, xi_0, zeta_0, alpha_4, alpha_22, alpha_28, beta_4, beta_22, delta_4, delta_22, epsilon_12, epsilon_38, eta_22, eta_38, gamma_4, gamma_22, gamma_28, kappa_22, kappa_38, lam_22, mu_22, nu_22, rho_22, rho_38, sigma_22, sigma_38, xi_22, xi_38, zeta_22, zeta_38

Tramos: [0, 4], [4, 12], [12, 22], [22, 28], [28, 38], [38, 50]
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck KineticNetwork

namespace Models.Giordano_Nature2020

def pos : Fin 43 → Bool := ![true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true]

def Rx0 : List (KExpr 10 43 × List (Fin 10 × ℚ)) := [
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 0) (KExpr.var 1)))), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 1) (KExpr.var 2)))), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 5) (KExpr.var 3)))), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 2) (KExpr.var 4)))), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 3)) (KExpr.var 1)), [(1, (-1 : ℚ)), (2, (1 : ℚ)), (8, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 15)) (KExpr.var 1)), [(1, (-1 : ℚ)), (3, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 7)) (KExpr.var 1)), [(1, (-1 : ℚ)), (6, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 4)) (KExpr.var 2)), [(2, (-1 : ℚ)), (4, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 10)) (KExpr.var 2)), [(2, (-1 : ℚ)), (6, (1 : ℚ)), (9, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 13)) (KExpr.var 3)), [(3, (-1 : ℚ)), (4, (1 : ℚ)), (8, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 6)) (KExpr.var 3)), [(3, (-1 : ℚ)), (6, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 8)) (KExpr.var 3)), [(3, (-1 : ℚ)), (5, (1 : ℚ)), (8, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 9)) (KExpr.var 4)), [(4, (-1 : ℚ)), (5, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 14)) (KExpr.var 4)), [(4, (-1 : ℚ)), (6, (1 : ℚ)), (9, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 12)) (KExpr.var 5)), [(5, (-1 : ℚ)), (7, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 11)) (KExpr.var 5)), [(5, (-1 : ℚ)), (6, (1 : ℚ)), (9, (1 : ℚ))])
]

theorem net_ok0 : checkNet pos Rx0 = true := by decide +kernel

def c0 : Fin 10 → ℚ := ![(1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ)]

theorem growth_ok0 : checkGrowth pos c0 Rx0 = true := by decide +kernel

def Rx1 : List (KExpr 10 43 × List (Fin 10 × ℚ)) := [
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 16) (KExpr.var 1)))), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 19) (KExpr.var 2)))), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 27) (KExpr.var 3)))), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 21) (KExpr.var 4)))), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 3)) (KExpr.var 1)), [(1, (-1 : ℚ)), (2, (1 : ℚ)), (8, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 15)) (KExpr.var 1)), [(1, (-1 : ℚ)), (3, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 7)) (KExpr.var 1)), [(1, (-1 : ℚ)), (6, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 4)) (KExpr.var 2)), [(2, (-1 : ℚ)), (4, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 10)) (KExpr.var 2)), [(2, (-1 : ℚ)), (6, (1 : ℚ)), (9, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 13)) (KExpr.var 3)), [(3, (-1 : ℚ)), (4, (1 : ℚ)), (8, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 6)) (KExpr.var 3)), [(3, (-1 : ℚ)), (6, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 8)) (KExpr.var 3)), [(3, (-1 : ℚ)), (5, (1 : ℚ)), (8, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 9)) (KExpr.var 4)), [(4, (-1 : ℚ)), (5, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 14)) (KExpr.var 4)), [(4, (-1 : ℚ)), (6, (1 : ℚ)), (9, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 12)) (KExpr.var 5)), [(5, (-1 : ℚ)), (7, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 11)) (KExpr.var 5)), [(5, (-1 : ℚ)), (6, (1 : ℚ)), (9, (1 : ℚ))])
]

theorem net_ok1 : checkNet pos Rx1 = true := by decide +kernel

def c1 : Fin 10 → ℚ := ![(1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ)]

theorem growth_ok1 : checkGrowth pos c1 Rx1 = true := by decide +kernel

def Rx2 : List (KExpr 10 43 × List (Fin 10 × ℚ)) := [
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 16) (KExpr.var 1)))), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 19) (KExpr.var 2)))), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 27) (KExpr.var 3)))), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 21) (KExpr.var 4)))), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 23)) (KExpr.var 1)), [(1, (-1 : ℚ)), (2, (1 : ℚ)), (8, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 15)) (KExpr.var 1)), [(1, (-1 : ℚ)), (3, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 7)) (KExpr.var 1)), [(1, (-1 : ℚ)), (6, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 4)) (KExpr.var 2)), [(2, (-1 : ℚ)), (4, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 10)) (KExpr.var 2)), [(2, (-1 : ℚ)), (6, (1 : ℚ)), (9, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 13)) (KExpr.var 3)), [(3, (-1 : ℚ)), (4, (1 : ℚ)), (8, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 6)) (KExpr.var 3)), [(3, (-1 : ℚ)), (6, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 8)) (KExpr.var 3)), [(3, (-1 : ℚ)), (5, (1 : ℚ)), (8, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 9)) (KExpr.var 4)), [(4, (-1 : ℚ)), (5, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 14)) (KExpr.var 4)), [(4, (-1 : ℚ)), (6, (1 : ℚ)), (9, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 12)) (KExpr.var 5)), [(5, (-1 : ℚ)), (7, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 11)) (KExpr.var 5)), [(5, (-1 : ℚ)), (6, (1 : ℚ)), (9, (1 : ℚ))])
]

theorem net_ok2 : checkNet pos Rx2 = true := by decide +kernel

def c2 : Fin 10 → ℚ := ![(1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ)]

theorem growth_ok2 : checkGrowth pos c2 Rx2 = true := by decide +kernel

def Rx3 : List (KExpr 10 43 × List (Fin 10 × ℚ)) := [
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 17) (KExpr.var 1)))), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 20) (KExpr.var 2)))), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 28) (KExpr.var 3)))), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 22) (KExpr.var 4)))), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 23)) (KExpr.var 1)), [(1, (-1 : ℚ)), (2, (1 : ℚ)), (8, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 41)) (KExpr.var 1)), [(1, (-1 : ℚ)), (3, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 32)) (KExpr.var 1)), [(1, (-1 : ℚ)), (6, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 25)) (KExpr.var 2)), [(2, (-1 : ℚ)), (4, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 35)) (KExpr.var 2)), [(2, (-1 : ℚ)), (6, (1 : ℚ)), (9, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 13)) (KExpr.var 3)), [(3, (-1 : ℚ)), (4, (1 : ℚ)), (8, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 30)) (KExpr.var 3)), [(3, (-1 : ℚ)), (6, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 33)) (KExpr.var 3)), [(3, (-1 : ℚ)), (5, (1 : ℚ)), (8, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 34)) (KExpr.var 4)), [(4, (-1 : ℚ)), (5, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 39)) (KExpr.var 4)), [(4, (-1 : ℚ)), (6, (1 : ℚ)), (9, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 12)) (KExpr.var 5)), [(5, (-1 : ℚ)), (7, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 37)) (KExpr.var 5)), [(5, (-1 : ℚ)), (6, (1 : ℚ)), (9, (1 : ℚ))])
]

theorem net_ok3 : checkNet pos Rx3 = true := by decide +kernel

def c3 : Fin 10 → ℚ := ![(1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ)]

theorem growth_ok3 : checkGrowth pos c3 Rx3 = true := by decide +kernel

def Rx4 : List (KExpr 10 43 × List (Fin 10 × ℚ)) := [
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 18) (KExpr.var 1)))), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 20) (KExpr.var 2)))), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 29) (KExpr.var 3)))), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 22) (KExpr.var 4)))), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 23)) (KExpr.var 1)), [(1, (-1 : ℚ)), (2, (1 : ℚ)), (8, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 41)) (KExpr.var 1)), [(1, (-1 : ℚ)), (3, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 32)) (KExpr.var 1)), [(1, (-1 : ℚ)), (6, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 25)) (KExpr.var 2)), [(2, (-1 : ℚ)), (4, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 35)) (KExpr.var 2)), [(2, (-1 : ℚ)), (6, (1 : ℚ)), (9, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 13)) (KExpr.var 3)), [(3, (-1 : ℚ)), (4, (1 : ℚ)), (8, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 30)) (KExpr.var 3)), [(3, (-1 : ℚ)), (6, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 33)) (KExpr.var 3)), [(3, (-1 : ℚ)), (5, (1 : ℚ)), (8, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 34)) (KExpr.var 4)), [(4, (-1 : ℚ)), (5, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 39)) (KExpr.var 4)), [(4, (-1 : ℚ)), (6, (1 : ℚ)), (9, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 12)) (KExpr.var 5)), [(5, (-1 : ℚ)), (7, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 37)) (KExpr.var 5)), [(5, (-1 : ℚ)), (6, (1 : ℚ)), (9, (1 : ℚ))])
]

theorem net_ok4 : checkNet pos Rx4 = true := by decide +kernel

def c4 : Fin 10 → ℚ := ![(1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ)]

theorem growth_ok4 : checkGrowth pos c4 Rx4 = true := by decide +kernel

def Rx5 : List (KExpr 10 43 × List (Fin 10 × ℚ)) := [
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 18) (KExpr.var 1)))), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 20) (KExpr.var 2)))), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 29) (KExpr.var 3)))), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 0) (KExpr.mul (KExpr.par 22) (KExpr.var 4)))), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 24)) (KExpr.var 1)), [(1, (-1 : ℚ)), (2, (1 : ℚ)), (8, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 42)) (KExpr.var 1)), [(1, (-1 : ℚ)), (3, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 32)) (KExpr.var 1)), [(1, (-1 : ℚ)), (6, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 26)) (KExpr.var 2)), [(2, (-1 : ℚ)), (4, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 36)) (KExpr.var 2)), [(2, (-1 : ℚ)), (6, (1 : ℚ)), (9, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 13)) (KExpr.var 3)), [(3, (-1 : ℚ)), (4, (1 : ℚ)), (8, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 31)) (KExpr.var 3)), [(3, (-1 : ℚ)), (6, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 33)) (KExpr.var 3)), [(3, (-1 : ℚ)), (5, (1 : ℚ)), (8, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 34)) (KExpr.var 4)), [(4, (-1 : ℚ)), (5, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 40)) (KExpr.var 4)), [(4, (-1 : ℚ)), (6, (1 : ℚ)), (9, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 12)) (KExpr.var 5)), [(5, (-1 : ℚ)), (7, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 38)) (KExpr.var 5)), [(5, (-1 : ℚ)), (6, (1 : ℚ)), (9, (1 : ℚ))])
]

theorem net_ok5 : checkNet pos Rx5 = true := by decide +kernel

def c5 : Fin 10 → ℚ := ![(1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ)]

theorem growth_ok5 : checkGrowth pos c5 Rx5 = true := by decide +kernel

def Rxs : ℕ → List (KExpr 10 43 × List (Fin 10 × ℚ))
  | 0 => Rx0
  | 1 => Rx1
  | 2 => Rx2
  | 3 => Rx3
  | 4 => Rx4
  | _ => Rx5

def cs : ℕ → Fin 10 → ℚ
  | 0 => c0
  | 1 => c1
  | 2 => c2
  | 3 => c3
  | 4 => c4
  | _ => c5

theorem net_ok : ∀ k, checkNet pos (Rxs k) = true := by
  intro k
  match k with
  | 0 => exact net_ok0
  | 1 => exact net_ok1
  | 2 => exact net_ok2
  | 3 => exact net_ok3
  | 4 => exact net_ok4
  | _ + 5 => exact net_ok5

theorem growth_ok : ∀ k, checkGrowth pos (cs k) (Rxs k) = true := by
  intro k
  match k with
  | 0 => exact growth_ok0
  | 1 => exact growth_ok1
  | 2 => exact growth_ok2
  | 3 => exact growth_ok3
  | 4 => exact growth_ok4
  | _ + 5 => exact growth_ok5

/-- Duración de cada tramo. -/
def Lq : ℕ → ℚ
  | 0 => (4 : ℚ)
  | 1 => (8 : ℚ)
  | 2 => (10 : ℚ)
  | 3 => (6 : ℚ)
  | 4 => (10 : ℚ)
  | _ => (12 : ℚ)

theorem Lq_nonneg : ∀ k, 0 ≤ Lq k := by
  intro k
  match k with
  | 0 => decide +kernel
  | 1 => decide +kernel
  | 2 => decide +kernel
  | 3 => decide +kernel
  | 4 => decide +kernel
  | _ + 5 => decide +kernel

noncomputable def Lseg (k : ℕ) : ℝ := (Lq k : ℝ)

theorem Lseg_nonneg : ∀ k, 0 ≤ Lseg k := fun k => by
  unfold Lseg; exact_mod_cast Lq_nonneg k

def θq : Fin 43 → ℚ := ![(57 / 100 : ℚ), (11 / 1000 : ℚ), (11 / 1000 : ℚ), (171 / 1000 : ℚ), (1 / 8 : ℚ), (57 / 125 : ℚ), (17 / 1000 : ℚ), (17 / 500 : ℚ), (17 / 1000 : ℚ), (27 / 1000 : ℚ), (17 / 500 : ℚ), (17 / 1000 : ℚ), (1 / 100 : ℚ), (371 / 1000 : ℚ), (17 / 1000 : ℚ), (1 / 8 : ℚ), (211 / 500 : ℚ), (9 / 25 : ℚ), (21 / 100 : ℚ), (57 / 10000 : ℚ), (1 / 200 : ℚ), (57 / 10000 : ℚ), (1 / 200 : ℚ), (143 / 1000 : ℚ), (1 / 5 : ℚ), (17 / 500 : ℚ), (1 / 40 : ℚ), (57 / 200 : ℚ), (1 / 5 : ℚ), (11 / 100 : ℚ), (17 / 1000 : ℚ), (1 / 50 : ℚ), (2 / 25 : ℚ), (1 / 125 : ℚ), (3 / 200 : ℚ), (17 / 1000 : ℚ), (1 / 50 : ℚ), (17 / 1000 : ℚ), (1 / 100 : ℚ), (17 / 1000 : ℚ), (1 / 50 : ℚ), (17 / 500 : ℚ), (1 / 40 : ℚ)]

theorem theta_ok : checkPosParams pos θq = true := by decide +kernel

def xq : Fin 10 → ℚ := ![(9999963 / 10000000 : ℚ), (333333333 / 100000000000000 : ℚ), (333333333 / 1000000000000000 : ℚ), (83333333 / 5000000000000000 : ℚ), (333333333 / 10000000000000000 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (3666666662999999 / 10000000000000000000000 : ℚ), (0 : ℚ)]

theorem x0_ok : checkNonneg xq = true := by decide +kernel

/-- **Teorema final por tramos, sin condiciones pendientes.** -/
def final := @network_segments_final _ _ pos Rxs net_ok cs growth_ok θq theta_ok xq
  x0_ok Lseg Lseg_nonneg

end Models.Giordano_Nature2020

#print axioms Models.Giordano_Nature2020.final
