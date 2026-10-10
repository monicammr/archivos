import KineticNetwork

/-! Modelo `Zheng_PNAS2012` (forma de red), traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (15): K27me0K36me0, K27me0K36me1, K27me1K36me0, K27me0K36me2, K27me1K36me1, K27me2K36me0, K27me0K36me3, K27me1K36me2, K27me2K36me1, K27me3K36me0, K27me1K36me3, K27me2K36me2, K27me3K36me1, K27me2K36me3, K27me3K36me2

Parámetros estimados θ (45): inflowp, k00_01, k00_10, k01_00, k01_02, k01_11, k02_01, k02_03, k02_12, k03_02, k03_13, k10_00, k10_11, k10_20, k11_01, k11_10, k11_12, k11_21, k12_02, k12_11, k12_13, k12_22, k13_03, k13_12, k13_23, k20_10, k20_21, k20_30, k21_11, k21_20, k21_22, k21_31, k22_12, k22_21, k22_23, k22_32, k23_13, k23_22, k30_20, k30_31, k31_21, k31_30, k31_32, k32_22, k32_31
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck KineticNetwork

namespace Models.Zheng_PNAS2012

/-- Máscara de parámetros positivos (nominal > 0 o escala log). -/
def pos : Fin 45 → Bool := fun _ => true

/-- Términos de velocidad con su columna estequiométrica (44 términos). -/
def Rx : List (KExpr 15 45 × List (Fin 15 × ℚ)) := [
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 0) (KExpr.par 1)) (KExpr.qconst (1 : ℚ)))), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 1) (KExpr.par 3)) (KExpr.qconst (1 : ℚ)))), [(0, (1 : ℚ)), (1, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 0) (KExpr.par 2)) (KExpr.qconst (1 : ℚ)))), [(0, (-1 : ℚ)), (2, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 2) (KExpr.par 11)) (KExpr.qconst (1 : ℚ)))), [(0, (1 : ℚ)), (2, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 1) (KExpr.par 5)) (KExpr.qconst (1 : ℚ)))), [(1, (-1 : ℚ)), (4, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 4) (KExpr.par 14)) (KExpr.qconst (1 : ℚ)))), [(1, (1 : ℚ)), (4, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 1) (KExpr.par 4)) (KExpr.qconst (1 : ℚ)))), [(1, (-1 : ℚ)), (3, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 3) (KExpr.par 6)) (KExpr.qconst (1 : ℚ)))), [(1, (1 : ℚ)), (3, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 2) (KExpr.par 12)) (KExpr.qconst (1 : ℚ)))), [(2, (-1 : ℚ)), (4, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 4) (KExpr.par 15)) (KExpr.qconst (1 : ℚ)))), [(2, (1 : ℚ)), (4, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 2) (KExpr.par 13)) (KExpr.qconst (1 : ℚ)))), [(2, (-1 : ℚ)), (5, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 5) (KExpr.par 25)) (KExpr.qconst (1 : ℚ)))), [(2, (1 : ℚ)), (5, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 3) (KExpr.par 8)) (KExpr.qconst (1 : ℚ)))), [(3, (-1 : ℚ)), (7, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 7) (KExpr.par 18)) (KExpr.qconst (1 : ℚ)))), [(3, (1 : ℚ)), (7, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 3) (KExpr.par 7)) (KExpr.qconst (1 : ℚ)))), [(3, (-1 : ℚ)), (6, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 6) (KExpr.par 9)) (KExpr.qconst (1 : ℚ)))), [(3, (1 : ℚ)), (6, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 4) (KExpr.par 16)) (KExpr.qconst (1 : ℚ)))), [(4, (-1 : ℚ)), (7, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 7) (KExpr.par 19)) (KExpr.qconst (1 : ℚ)))), [(4, (1 : ℚ)), (7, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 4) (KExpr.par 17)) (KExpr.qconst (1 : ℚ)))), [(4, (-1 : ℚ)), (8, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 8) (KExpr.par 28)) (KExpr.qconst (1 : ℚ)))), [(4, (1 : ℚ)), (8, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 5) (KExpr.par 26)) (KExpr.qconst (1 : ℚ)))), [(5, (-1 : ℚ)), (8, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 8) (KExpr.par 29)) (KExpr.qconst (1 : ℚ)))), [(5, (1 : ℚ)), (8, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 5) (KExpr.par 27)) (KExpr.qconst (1 : ℚ)))), [(5, (-1 : ℚ)), (9, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 9) (KExpr.par 38)) (KExpr.qconst (1 : ℚ)))), [(5, (1 : ℚ)), (9, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 6) (KExpr.par 10)) (KExpr.qconst (1 : ℚ)))), [(6, (-1 : ℚ)), (10, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 10) (KExpr.par 22)) (KExpr.qconst (1 : ℚ)))), [(6, (1 : ℚ)), (10, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 7) (KExpr.par 21)) (KExpr.qconst (1 : ℚ)))), [(7, (-1 : ℚ)), (11, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 11) (KExpr.par 32)) (KExpr.qconst (1 : ℚ)))), [(7, (1 : ℚ)), (11, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 7) (KExpr.par 20)) (KExpr.qconst (1 : ℚ)))), [(7, (-1 : ℚ)), (10, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 10) (KExpr.par 23)) (KExpr.qconst (1 : ℚ)))), [(7, (1 : ℚ)), (10, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 8) (KExpr.par 30)) (KExpr.qconst (1 : ℚ)))), [(8, (-1 : ℚ)), (11, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 11) (KExpr.par 33)) (KExpr.qconst (1 : ℚ)))), [(8, (1 : ℚ)), (11, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 8) (KExpr.par 31)) (KExpr.qconst (1 : ℚ)))), [(8, (-1 : ℚ)), (12, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 12) (KExpr.par 40)) (KExpr.qconst (1 : ℚ)))), [(8, (1 : ℚ)), (12, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 9) (KExpr.par 39)) (KExpr.qconst (1 : ℚ)))), [(9, (-1 : ℚ)), (12, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 12) (KExpr.par 41)) (KExpr.qconst (1 : ℚ)))), [(9, (1 : ℚ)), (12, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 10) (KExpr.par 24)) (KExpr.qconst (1 : ℚ)))), [(10, (-1 : ℚ)), (13, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 13) (KExpr.par 36)) (KExpr.qconst (1 : ℚ)))), [(10, (1 : ℚ)), (13, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 11) (KExpr.par 34)) (KExpr.qconst (1 : ℚ)))), [(11, (-1 : ℚ)), (13, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 13) (KExpr.par 37)) (KExpr.qconst (1 : ℚ)))), [(11, (1 : ℚ)), (13, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 11) (KExpr.par 35)) (KExpr.qconst (1 : ℚ)))), [(11, (-1 : ℚ)), (14, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 14) (KExpr.par 43)) (KExpr.qconst (1 : ℚ)))), [(11, (1 : ℚ)), (14, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 12) (KExpr.par 42)) (KExpr.qconst (1 : ℚ)))), [(12, (-1 : ℚ)), (14, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.var 14) (KExpr.par 44)) (KExpr.qconst (1 : ℚ)))), [(12, (1 : ℚ)), (14, (-1 : ℚ))])
]

/-- El campo del modelo: `Fᵢ = Σ_r coef_r(i) · V_r`. -/
def F : Fin 15 → KExpr 15 45 := netF Rx

/-- Dominio ⊇ ortante y cuasi-positividad (Lean ejecuta el comprobador). -/
theorem net_ok : checkNet pos Rx = true := by decide +kernel

/-- Pesos de la combinación con crecimiento lineal (cᵢ ≥ 1). -/
def c : Fin 15 → ℚ := fun _ => (1 : ℚ)

theorem growth_ok : checkGrowth pos c Rx = true := by decide +kernel

/-- θ₀ nominal (PEtab), en racionales exactos. -/
def θq : Fin 45 → ℚ := ![(15240587513769 / 500000000000000 : ℚ), (997285248531849 / 1000000000000 : ℚ), (234022855508701 / 1000000000000000 : ℚ), (479841669671183 / 1000000000000 : ℚ), (95669165795857 / 50000000000000 : ℚ), (66287375808341 / 25000000000000 : ℚ), (17490905619863 / 250000000000000 : ℚ), (50000021593203 / 5000000000000000000 : ℚ), (50000060494379 / 5000000000000000000 : ℚ), (20000000000001 / 2000000000000000000 : ℚ), (197624484863839 / 200000000000 : ℚ), (100000000016979 / 10000000000000000000 : ℚ), (20000000477547 / 2000000000000000000 : ℚ), (33648960176141 / 125000000000000 : ℚ), (4000000000069 / 400000000000000000 : ℚ), (10002960370593 / 1000000000000000000 : ℚ), (118517895122981 / 10000000000000 : ℚ), (100000003508203 / 10000000000000000000 : ℚ), (25000000000049 / 2500000000000000000 : ℚ), (1069993783787 / 10000000000000 : ℚ), (35629896010771 / 1000000000000000 : ℚ), (5308295329971 / 500000000000000 : ℚ), (450435886070063 / 1000000000000 : ℚ), (195255677936969 / 1000000000000000 : ℚ), (1562500006849 / 156250000000000000 : ℚ), (20000000000001 / 2000000000000000000 : ℚ), (25000010800741 / 2500000000000000000 : ℚ), (150740144379533 / 1000000000000000 : ℚ), (100035442572023 / 10000000000000000000 : ℚ), (35397749723473 / 1000000000000000 : ℚ), (499639814419269 / 500000000000 : ℚ), (100000000261933 / 10000000000000000000 : ℚ), (53379637739473 / 1000000000000000 : ℚ), (426143170255777 / 1000000000000 : ℚ), (75870700408083 / 500000000000000 : ℚ), (20000000000001 / 2000000000000000000 : ℚ), (791201186423607 / 1000000000000000 : ℚ), (25000189464007 / 2500000000000000000 : ℚ), (50000068981867 / 5000000000000000000 : ℚ), (17581402007101 / 62500000000000 : ℚ), (100087528532117 / 10000000000000000000 : ℚ), (800019207957 / 80000000000000000 : ℚ), (353631402713609 / 1000000000000000 : ℚ), (632981853600849 / 1000000000000000 : ℚ), (20000000000001 / 2000000000000000000 : ℚ)]

theorem theta_ok : checkPosParams pos θq = true := by decide +kernel

/-- Condiciones iniciales nominales. -/
def xq : Fin 15 → ℚ := ![(417724976345759 / 100000000000000000 : ℚ), (102104668587641 / 10000000000000000 : ℚ), (165412810279407 / 100000000000000000 : ℚ), (84845158119773 / 500000000000000 : ℚ), (78328187288069 / 10000000000000000 : ℚ), (632744816295157 / 100000000000000000 : ℚ), (63116901850943 / 1250000000000000 : ℚ), (594249755169037 / 1000000000000000 : ℚ), (143896310177379 / 10000000000000000 : ℚ), (66033682320833 / 20000000000000000 : ℚ), (51374337538979 / 500000000000000 : ℚ), (263372634996529 / 10000000000000000 : ℚ), (250831034920277 / 100000000000000000 : ℚ), (235915718001067 / 50000000000000000 : ℚ), (68020815897781 / 50000000000000000 : ℚ)]

theorem x0_ok : checkNonneg xq = true := by decide +kernel

/-- **Teorema final, sin condiciones pendientes**: para todo T ≥ 0 la solución
nominal existe en [0, T], es ≥ 0, queda en el dominio, y la trayectoria es
diferenciable respecto a θ en θ₀. -/
def final := @network_final _ _ pos Rx net_ok c growth_ok θq theta_ok xq x0_ok

end Models.Zheng_PNAS2012

#print axioms Models.Zheng_PNAS2012.final
