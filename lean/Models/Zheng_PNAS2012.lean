import KineticCheck

/-! Modelo `Zheng_PNAS2012` traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (15): K27me0K36me0, K27me0K36me1, K27me1K36me0, K27me0K36me2, K27me1K36me1, K27me2K36me0, K27me0K36me3, K27me1K36me2, K27me2K36me1, K27me3K36me0, K27me1K36me3, K27me2K36me2, K27me3K36me1, K27me2K36me3, K27me3K36me2

Parámetros estimados θ (45): inflowp, k00_01, k00_10, k01_00, k01_02, k01_11, k02_01, k02_03, k02_12, k03_02, k03_13, k10_00, k10_11, k10_20, k11_01, k11_10, k11_12, k11_21, k12_02, k12_11, k12_13, k12_22, k13_03, k13_12, k13_23, k20_10, k20_21, k20_30, k21_11, k21_20, k21_22, k21_31, k22_12, k22_21, k22_23, k22_32, k23_13, k23_22, k30_20, k30_31, k31_21, k31_30, k31_32, k32_22, k32_31
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck

namespace Models.Zheng_PNAS2012

def F : Fin 15 → KExpr 15 45 := ![
  (.add (.sub (.add (.sub (.qconst (0 : ℚ)) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 0) (.par 1)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 1) (.par 3)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 0) (.par 2)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 2) (.par 11)) (.qconst (1 : ℚ))))),
  (.add (.sub (.add (.sub (.sub (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 0) (.par 1)) (.qconst (1 : ℚ)))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 1) (.par 3)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 1) (.par 5)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 4) (.par 14)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 1) (.par 4)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 3) (.par 6)) (.qconst (1 : ℚ))))),
  (.add (.sub (.add (.sub (.sub (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 0) (.par 2)) (.qconst (1 : ℚ)))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 2) (.par 11)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 2) (.par 12)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 4) (.par 15)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 2) (.par 13)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 5) (.par 25)) (.qconst (1 : ℚ))))),
  (.add (.sub (.add (.sub (.sub (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 1) (.par 4)) (.qconst (1 : ℚ)))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 3) (.par 6)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 3) (.par 8)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 7) (.par 18)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 3) (.par 7)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 6) (.par 9)) (.qconst (1 : ℚ))))),
  (.add (.sub (.add (.sub (.sub (.add (.sub (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 2) (.par 12)) (.qconst (1 : ℚ)))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 4) (.par 15)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 1) (.par 5)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 4) (.par 14)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 4) (.par 16)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 7) (.par 19)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 4) (.par 17)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 8) (.par 28)) (.qconst (1 : ℚ))))),
  (.add (.sub (.add (.sub (.sub (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 2) (.par 13)) (.qconst (1 : ℚ)))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 5) (.par 25)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 5) (.par 26)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 8) (.par 29)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 5) (.par 27)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 9) (.par 38)) (.qconst (1 : ℚ))))),
  (.add (.sub (.sub (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 3) (.par 7)) (.qconst (1 : ℚ)))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 6) (.par 9)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 6) (.par 10)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 10) (.par 22)) (.qconst (1 : ℚ))))),
  (.add (.sub (.add (.sub (.sub (.add (.sub (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 3) (.par 8)) (.qconst (1 : ℚ)))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 7) (.par 18)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 4) (.par 16)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 7) (.par 19)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 7) (.par 21)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 11) (.par 32)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 7) (.par 20)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 10) (.par 23)) (.qconst (1 : ℚ))))),
  (.add (.sub (.add (.sub (.sub (.add (.sub (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 5) (.par 26)) (.qconst (1 : ℚ)))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 8) (.par 29)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 4) (.par 17)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 8) (.par 28)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 8) (.par 30)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 11) (.par 33)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 8) (.par 31)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 12) (.par 40)) (.qconst (1 : ℚ))))),
  (.add (.sub (.sub (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 5) (.par 27)) (.qconst (1 : ℚ)))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 9) (.par 38)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 9) (.par 39)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 12) (.par 41)) (.qconst (1 : ℚ))))),
  (.add (.sub (.sub (.add (.sub (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 6) (.par 10)) (.qconst (1 : ℚ)))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 10) (.par 22)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 7) (.par 20)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 10) (.par 23)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 10) (.par 24)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 13) (.par 36)) (.qconst (1 : ℚ))))),
  (.add (.sub (.add (.sub (.sub (.add (.sub (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 7) (.par 21)) (.qconst (1 : ℚ)))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 11) (.par 32)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 8) (.par 30)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 11) (.par 33)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 11) (.par 34)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 13) (.par 37)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 11) (.par 35)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 14) (.par 43)) (.qconst (1 : ℚ))))),
  (.add (.sub (.sub (.add (.sub (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 9) (.par 39)) (.qconst (1 : ℚ)))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 12) (.par 41)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 8) (.par 31)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 12) (.par 40)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 12) (.par 42)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 14) (.par 44)) (.qconst (1 : ℚ))))),
  (.sub (.add (.sub (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 11) (.par 34)) (.qconst (1 : ℚ)))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 13) (.par 37)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 10) (.par 24)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 13) (.par 36)) (.qconst (1 : ℚ))))),
  (.sub (.add (.sub (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 11) (.par 35)) (.qconst (1 : ℚ)))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 14) (.par 43)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 12) (.par 42)) (.qconst (1 : ℚ))))) (.mul (.qconst (1 : ℚ)) (.div (.mul (.var 14) (.par 44)) (.qconst (1 : ℚ)))))
]

theorem check : checkModel F = true := by decide +kernel

/-- Diferenciabilidad de la trayectoria (y positividad) para este modelo. -/
def diff := @checked_model_hasFDerivAt _ _ F check

end Models.Zheng_PNAS2012

#print axioms Models.Zheng_PNAS2012.diff
