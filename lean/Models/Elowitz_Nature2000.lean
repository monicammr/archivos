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

def F : Fin 8 → KExpr 8 18 := ![
  (.sub (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 4) (.par 1)) (.par 12))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 0) (.log (.qconst (2 : ℚ)))) (.par 14)))),
  (.sub (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 5) (.par 1)) (.par 12))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 1) (.log (.qconst (2 : ℚ)))) (.par 14)))),
  (.sub (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 6) (.par 1)) (.par 12))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 2) (.log (.qconst (2 : ℚ)))) (.par 14)))),
  (.add (.sub (.add (.sub (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 7) (.par 2)) (.par 13))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 3) (.log (.qconst (2 : ℚ)))) (.par 15)))) (.mul (.qconst (1 : ℚ)) (.mul (.qconst (60 : ℚ)) (.par 17)))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.exp (.mul (.par 11) (.log (.par 0)))) (.mul (.qconst (60 : ℚ)) (.par 17))) (.add (.exp (.mul (.par 11) (.log (.par 0)))) (.exp (.mul (.par 11) (.log (.var 0)))))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.exp (.mul (.par 11) (.log (.par 0)))) (.mul (.qconst (60 : ℚ)) (.par 16))) (.add (.exp (.mul (.par 11) (.log (.par 0)))) (.exp (.mul (.par 11) (.log (.var 0)))))))),
  (.add (.sub (.add (.sub (.qconst (0 : ℚ)) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 4) (.log (.qconst (2 : ℚ)))) (.par 12)))) (.mul (.qconst (1 : ℚ)) (.mul (.qconst (60 : ℚ)) (.par 17)))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.exp (.mul (.par 11) (.log (.par 0)))) (.mul (.qconst (60 : ℚ)) (.par 17))) (.add (.exp (.mul (.par 11) (.log (.par 0)))) (.exp (.mul (.par 11) (.log (.var 2)))))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.exp (.mul (.par 11) (.log (.par 0)))) (.mul (.qconst (60 : ℚ)) (.par 16))) (.add (.exp (.mul (.par 11) (.log (.par 0)))) (.exp (.mul (.par 11) (.log (.var 2)))))))),
  (.add (.sub (.add (.sub (.qconst (0 : ℚ)) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 5) (.log (.qconst (2 : ℚ)))) (.par 12)))) (.mul (.qconst (1 : ℚ)) (.mul (.qconst (60 : ℚ)) (.par 17)))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.exp (.mul (.par 11) (.log (.par 0)))) (.mul (.qconst (60 : ℚ)) (.par 17))) (.add (.exp (.mul (.par 11) (.log (.par 0)))) (.exp (.mul (.par 11) (.log (.var 0)))))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.exp (.mul (.par 11) (.log (.par 0)))) (.mul (.qconst (60 : ℚ)) (.par 16))) (.add (.exp (.mul (.par 11) (.log (.par 0)))) (.exp (.mul (.par 11) (.log (.var 0)))))))),
  (.add (.sub (.add (.sub (.qconst (0 : ℚ)) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 6) (.log (.qconst (2 : ℚ)))) (.par 12)))) (.mul (.qconst (1 : ℚ)) (.mul (.qconst (60 : ℚ)) (.par 17)))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.exp (.mul (.par 11) (.log (.par 0)))) (.mul (.qconst (60 : ℚ)) (.par 17))) (.add (.exp (.mul (.par 11) (.log (.par 0)))) (.exp (.mul (.par 11) (.log (.var 1)))))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.exp (.mul (.par 11) (.log (.par 0)))) (.mul (.qconst (60 : ℚ)) (.par 16))) (.add (.exp (.mul (.par 11) (.log (.par 0)))) (.exp (.mul (.par 11) (.log (.var 1)))))))),
  (.sub (.qconst (0 : ℚ)) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 7) (.log (.qconst (2 : ℚ)))) (.par 13))))
]

/-- La comprobación sintáctica FALLA para este modelo (ver el informe JSON). -/
theorem check_falla : checkModel F = false := by decide +kernel

end Models.Elowitz_Nature2000
