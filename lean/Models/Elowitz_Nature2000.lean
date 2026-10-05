import KineticCheck

/-! Modelo `Elowitz_Nature2000` traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (8): X_protein, Y_protein, Z_protein, GFP, X_mRNA, Y_mRNA, Z_mRNA, GFP_mRNA

Parámetros estimados θ (18): KM, eff, eff_GFP, init_GFP, init_GFP_mRNA, init_X_mRNA, init_X_protein, init_Y_mRNA, init_Y_protein, init_Z_mRNA, init_Z_protein, n_Hill, tau_mRNA, tau_mRNA_GFP, tau_prot, tau_prot_GFP, tps_active, tps_repr
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck

namespace Models.Elowitz_Nature2000

/-- Máscara de parámetros con valor nominal > 0 (los demás: signo arbitrario). -/
def pos : Fin 18 → Bool := ![true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true]

def F : Fin 8 → KExpr 8 18 := ![
  (KExpr.sub (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 4) (KExpr.par 1)) (KExpr.par 12))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 0) (KExpr.log (KExpr.qconst (2 : ℚ)))) (KExpr.par 14)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 5) (KExpr.par 1)) (KExpr.par 12))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 1) (KExpr.log (KExpr.qconst (2 : ℚ)))) (KExpr.par 14)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 6) (KExpr.par 1)) (KExpr.par 12))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 2) (KExpr.log (KExpr.qconst (2 : ℚ)))) (KExpr.par 14)))),
  (KExpr.sub (KExpr.add (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 7) (KExpr.par 2)) (KExpr.par 13))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.qconst (60 : ℚ)) (KExpr.par 17)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.par 0)))) (KExpr.mul (KExpr.qconst (60 : ℚ)) (KExpr.par 16))) (KExpr.add (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.par 0)))) (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.var 0)))))))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 3) (KExpr.log (KExpr.qconst (2 : ℚ)))) (KExpr.par 15))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.par 0)))) (KExpr.mul (KExpr.qconst (60 : ℚ)) (KExpr.par 17))) (KExpr.add (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.par 0)))) (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.var 0))))))))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.qconst (60 : ℚ)) (KExpr.par 17))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.par 0)))) (KExpr.mul (KExpr.qconst (60 : ℚ)) (KExpr.par 16))) (KExpr.add (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.par 0)))) (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.var 2)))))))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 4) (KExpr.log (KExpr.qconst (2 : ℚ)))) (KExpr.par 12))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.par 0)))) (KExpr.mul (KExpr.qconst (60 : ℚ)) (KExpr.par 17))) (KExpr.add (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.par 0)))) (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.var 2))))))))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.qconst (60 : ℚ)) (KExpr.par 17))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.par 0)))) (KExpr.mul (KExpr.qconst (60 : ℚ)) (KExpr.par 16))) (KExpr.add (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.par 0)))) (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.var 0)))))))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 5) (KExpr.log (KExpr.qconst (2 : ℚ)))) (KExpr.par 12))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.par 0)))) (KExpr.mul (KExpr.qconst (60 : ℚ)) (KExpr.par 17))) (KExpr.add (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.par 0)))) (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.var 0))))))))),
  (KExpr.sub (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.qconst (60 : ℚ)) (KExpr.par 17))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.par 0)))) (KExpr.mul (KExpr.qconst (60 : ℚ)) (KExpr.par 16))) (KExpr.add (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.par 0)))) (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.var 1)))))))) (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 6) (KExpr.log (KExpr.qconst (2 : ℚ)))) (KExpr.par 12))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.par 0)))) (KExpr.mul (KExpr.qconst (60 : ℚ)) (KExpr.par 17))) (KExpr.add (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.par 0)))) (KExpr.exp (KExpr.mul (KExpr.par 11) (KExpr.log (KExpr.var 1))))))))),
  (KExpr.sub (KExpr.qconst (0 : ℚ)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 7) (KExpr.log (KExpr.qconst (2 : ℚ)))) (KExpr.par 13))))
]

/-- La comprobación sintáctica FALLA para este modelo (ver el informe JSON). -/
theorem check_falla : checkModel pos F = false := by decide +kernel

end Models.Elowitz_Nature2000
