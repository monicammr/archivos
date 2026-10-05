import KineticCheck

/-! Modelo `Borghans_BiophysChem1997` traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (3): Z_state, Y_state, A_state

Parámetros estimados θ (20): K2, K_par, Ka, Kd, Kf, Kp, Ky, Kz, Vd, Vm2, Vm3, Vp, beta_par, epsilon_par, init_A_state, init_Y_state, init_Z_state, n_par, v0, v1
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck

namespace Models.Borghans_BiophysChem1997

/-- Máscara de parámetros con valor nominal > 0 (los demás: signo arbitrario). -/
def pos : Fin 20 → Bool := ![true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true]

def F : Fin 3 → KExpr 3 20 := ![
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.sub (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 18)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 12) (KExpr.par 19)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.par 9) (KExpr.npow (KExpr.var 0) 2)) (KExpr.add (KExpr.npow (KExpr.par 0) 2) (KExpr.npow (KExpr.var 0) 2))))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.npow (KExpr.var 2) 4) (KExpr.par 10)) (KExpr.npow (KExpr.var 1) 2)) (KExpr.npow (KExpr.var 0) 4)) (KExpr.mul (KExpr.mul (KExpr.add (KExpr.npow (KExpr.var 2) 4) (KExpr.npow (KExpr.par 2) 4)) (KExpr.add (KExpr.npow (KExpr.par 6) 2) (KExpr.npow (KExpr.var 1) 2))) (KExpr.add (KExpr.npow (KExpr.par 7) 4) (KExpr.npow (KExpr.var 0) 4)))))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 4)) (KExpr.var 1))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 1)) (KExpr.var 0))),
  (KExpr.sub (KExpr.sub (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.par 9) (KExpr.npow (KExpr.var 0) 2)) (KExpr.add (KExpr.npow (KExpr.par 0) 2) (KExpr.npow (KExpr.var 0) 2)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.npow (KExpr.var 2) 4) (KExpr.par 10)) (KExpr.npow (KExpr.var 1) 2)) (KExpr.npow (KExpr.var 0) 4)) (KExpr.mul (KExpr.mul (KExpr.add (KExpr.npow (KExpr.var 2) 4) (KExpr.npow (KExpr.par 2) 4)) (KExpr.add (KExpr.npow (KExpr.par 6) 2) (KExpr.npow (KExpr.var 1) 2))) (KExpr.add (KExpr.npow (KExpr.par 7) 4) (KExpr.npow (KExpr.var 0) 4)))))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 4)) (KExpr.var 1))),
  (KExpr.sub (KExpr.sub (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 11)) (KExpr.par 12)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.npow (KExpr.var 2) 2) (KExpr.par 8)) (KExpr.exp (KExpr.mul (KExpr.par 17) (KExpr.log (KExpr.var 0))))) (KExpr.mul (KExpr.add (KExpr.exp (KExpr.mul (KExpr.par 17) (KExpr.log (KExpr.par 3)))) (KExpr.exp (KExpr.mul (KExpr.par 17) (KExpr.log (KExpr.var 0))))) (KExpr.add (KExpr.npow (KExpr.var 2) 2) (KExpr.npow (KExpr.par 5) 2)))))) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 2)) (KExpr.par 13)))
]

/-- La comprobación sintáctica FALLA para este modelo (ver el informe JSON). -/
theorem check_falla : checkModel pos F = false := by decide +kernel

end Models.Borghans_BiophysChem1997
