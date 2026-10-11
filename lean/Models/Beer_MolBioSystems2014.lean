import KineticCheck

/-! Modelo `Beer_MolBioSystems2014` traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (4): Bac, Glu, cGlu, Ind

Parámetros estimados θ (1): init_Bac

Tramos (entradas por escalones en tiempos fijos): [0, 1], [1, 3565]
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck

namespace Models.Beer_MolBioSystems2014

/-- Máscara de parámetros con valor nominal > 0 (los demás: signo arbitrario). -/
def pos : Fin 1 → Bool := ![true]

def F0 : Fin 4 → KExpr 4 1 := ![
  (KExpr.qconst (0 : ℚ)),
  (KExpr.sub (KExpr.qconst (0 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 0)) (KExpr.var 1)) (KExpr.qconst (1 : ℚ)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.var 0) (KExpr.var 1)) (KExpr.qconst (1 : ℚ)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.npow (KExpr.var 2) 2) (KExpr.qconst (1 : ℚ))))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.npow (KExpr.var 2) 2) (KExpr.qconst (1 : ℚ)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 3) (KExpr.qconst (1 : ℚ)))))
]

theorem check0 : checkModel pos F0 = true := by decide +kernel

def F1 : Fin 4 → KExpr 4 1 := ![
  (KExpr.sub (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.var 0) (KExpr.qconst (1 : ℚ))) (KExpr.qconst (1 : ℚ))) (KExpr.qconst (1 : ℚ))) (KExpr.qconst (1 : ℚ)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.var 0) (KExpr.qconst (1 : ℚ))) (KExpr.qconst (1 : ℚ))) (KExpr.var 0)) (KExpr.qconst (1 : ℚ))))),
  (KExpr.sub (KExpr.qconst (0 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 0)) (KExpr.var 1)) (KExpr.qconst (1 : ℚ)))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.var 0) (KExpr.var 1)) (KExpr.qconst (1 : ℚ)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.npow (KExpr.var 2) 2) (KExpr.qconst (1 : ℚ))))),
  (KExpr.sub (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.npow (KExpr.var 2) 2) (KExpr.qconst (1 : ℚ)))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 3) (KExpr.qconst (1 : ℚ)))))
]

theorem check1 : checkModel pos F1 = true := by decide +kernel

def Fseg : ℕ → Fin 4 → KExpr 4 1
  | 0 => F0
  | _ => F1

theorem check : ∀ k, checkModel pos (Fseg k) = true := by
  intro k
  match k with
  | 0 => exact check0
  | _ + 1 => exact check1

/-- Diferenciabilidad de la trayectoria en todos los tramos. -/
def diff := @checked_segments_hasFDerivAt _ _ pos Fseg check

end Models.Beer_MolBioSystems2014

#print axioms Models.Beer_MolBioSystems2014.diff
