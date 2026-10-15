import KineticNetwork

/-! Modelo `Isensee_JCB2018` (forma de red), traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (25): AC, pAC, AC_Fsk, pAC_Fsk, cAMP, Csub, Csub_H89, RII_C_2, RIIp_C_2, RIIp_cAMP_C_2, RIIp_cAMP_2, Sp8_Br_cAMPS, Rp8_Br_cAMPS, Rp8_pCPT_cAMPS, Rp_cAMPS, RIIp_Rp8_Br_cAMPS_C_2, RIIp_Rp8_pCPT_cAMPS_C_2, RIIp_Rp_cAMPS_C_2, RIIp_Sp8_Br_cAMPS_C_2, RIIp_Sp8_Br_cAMPS_2, RIIp_2, RII_2, IBMX, PDE, pPDE

Parámetros estimados θ (32): KD_Fsk, KD_H89, KD_IBMX, KD_cAMP, kdeg_cAMP, kdeg_cAMP_free, kf_Fsk, kf_H89, kf_RII_2__RII_C_2, kf_RII_C_2__RII_2, kf_RII_C_2__RIIp_C_2, kf_RIIp_2__RII_2, kf_RIIp_C_2__RII_C_2, kf_RIIp_cAMP_C_2__RIIp_2, kf_cAMP, ki_IBMX, ki_Rp8_Br_cAMPS_pAB, ki_Rp8_pCPT_cAMPS_pAB, ki_Rp_cAMPS_pAB, ki_Sp8_Br_cAMPS_AM, ks_AC_cAMP, xi_AC_cAMP_Fsk, xi_b_Rp8_Br_cAMPS, xi_b_Rp8_pCPT_cAMPS, xi_b_Rp_cAMPS, xi_b_Sp8_Br_cAMPS, xi_kf_RII_2__RII_C_2, xi_kf_RII_C_2__RII_2, xi_KD_Rp8_Br_cAMPS, xi_KD_Rp8_pCPT_cAMPS, xi_KD_Rp_cAMPS, xi_KD_Sp8_Br_cAMPS
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck KineticNetwork

namespace Models.Isensee_JCB2018

/-- Máscara de parámetros positivos (nominal > 0 o escala log). -/
def pos : Fin 32 → Bool := fun _ => true

/-- Términos de velocidad con su columna estequiométrica (34 términos). -/
def Rx : List (KExpr 25 32 × List (Fin 25 × ℚ)) := [
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 2)) (KExpr.par 0)) (KExpr.par 6)), [(0, (1 : ℚ)), (2, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 0)) (KExpr.par 6)) (KExpr.var 3)), [(1, (1 : ℚ)), (3, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 20)) (KExpr.var 0)), [(4, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 20)) (KExpr.par 21)) (KExpr.var 2)), [(4, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.par 2) (KExpr.var 4)) (KExpr.par 5)) (KExpr.var 23)) (KExpr.add (KExpr.var 22) (KExpr.par 2)))), [(4, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 7)) (KExpr.par 9)), [(5, (1 : ℚ)), (7, (-1 : ℚ)), (21, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 5)) (KExpr.var 21)) (KExpr.par 8)), [(5, (-1 : ℚ)), (7, (1 : ℚ)), (21, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 8)) (KExpr.par 9)) (KExpr.par 27)), [(5, (1 : ℚ)), (8, (-1 : ℚ)), (20, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 5)) (KExpr.var 20)) (KExpr.par 8)) (KExpr.par 26)), [(5, (-1 : ℚ)), (8, (1 : ℚ)), (20, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 9)) (KExpr.par 13)), [(5, (1 : ℚ)), (9, (-1 : ℚ)), (10, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 18)) (KExpr.par 13)), [(5, (1 : ℚ)), (18, (-1 : ℚ)), (19, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 6)) (KExpr.par 1)) (KExpr.par 7)), [(5, (1 : ℚ)), (6, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 7)) (KExpr.par 10)), [(7, (-1 : ℚ)), (8, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 8)) (KExpr.par 12)), [(7, (1 : ℚ)), (8, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 8)) (KExpr.var 4)) (KExpr.par 14)), [(8, (-1 : ℚ)), (9, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 3)) (KExpr.var 9)) (KExpr.par 14)), [(8, (1 : ℚ)), (9, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.par 2) (KExpr.var 9)) (KExpr.par 4)) (KExpr.var 23)) (KExpr.add (KExpr.var 22) (KExpr.par 2)))), [(8, (1 : ℚ)), (9, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 8)) (KExpr.var 12)) (KExpr.par 14)) (KExpr.par 22)), [(8, (-1 : ℚ)), (15, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 3)) (KExpr.var 15)) (KExpr.par 14)) (KExpr.par 22)) (KExpr.par 28)), [(8, (1 : ℚ)), (15, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 8)) (KExpr.var 13)) (KExpr.par 14)) (KExpr.par 23)), [(8, (-1 : ℚ)), (16, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 3)) (KExpr.var 16)) (KExpr.par 14)) (KExpr.par 23)) (KExpr.par 29)), [(8, (1 : ℚ)), (16, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 8)) (KExpr.var 14)) (KExpr.par 14)) (KExpr.par 24)), [(8, (-1 : ℚ)), (17, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 3)) (KExpr.var 17)) (KExpr.par 14)) (KExpr.par 24)) (KExpr.par 30)), [(8, (1 : ℚ)), (17, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 8)) (KExpr.var 11)) (KExpr.par 14)) (KExpr.par 25)), [(8, (-1 : ℚ)), (18, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 3)) (KExpr.var 18)) (KExpr.par 14)) (KExpr.par 25)) (KExpr.par 31)), [(8, (1 : ℚ)), (18, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 3)) (KExpr.var 10)) (KExpr.par 14)), [(10, (-1 : ℚ)), (20, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.div (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.par 2) (KExpr.var 10)) (KExpr.par 4)) (KExpr.var 23)) (KExpr.add (KExpr.var 22) (KExpr.par 2)))), [(10, (-1 : ℚ)), (20, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 19)) (KExpr.var 11)), [(11, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 16)) (KExpr.var 12)), [(12, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 17)) (KExpr.var 13)), [(13, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 18)) (KExpr.var 14)), [(14, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 3)) (KExpr.var 19)) (KExpr.par 14)) (KExpr.par 25)) (KExpr.par 31)), [(19, (-1 : ℚ)), (20, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 20)) (KExpr.par 11)), [(20, (-1 : ℚ)), (21, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 15)) (KExpr.var 22)), [(22, (-1 : ℚ))])
]

/-- El campo del modelo: `Fᵢ = Σ_r coef_r(i) · V_r`. -/
def F : Fin 25 → KExpr 25 32 := netF Rx

/-- Dominio ⊇ ortante y cuasi-positividad (Lean ejecuta el comprobador). -/
theorem net_ok : checkNet pos Rx = true := by decide +kernel

/-- Pesos de la combinación con crecimiento lineal (cᵢ ≥ 1). -/
def c : Fin 25 → ℚ := fun _ => (1 : ℚ)

theorem growth_ok : checkGrowth pos c Rx = true := by decide +kernel

/-- θ₀ nominal (PEtab), en racionales exactos. -/
def θq : Fin 32 → ℚ := ![(71402585871347 / 5000000000000 : ℚ), (12018506808083 / 250000000000000 : ℚ), (1495096581983 / 125000000000 : ℚ), (285002019924967 / 100000000000000 : ℚ), (100000660182181 / 10000000000000000000 : ℚ), (147672756454509 / 20000000000000 : ℚ), (1953124918547 / 1953125000 : ℚ), (742716621349 / 1000000000000000 : ℚ), (126446106685121 / 100000000000000 : ℚ), (3749347968707 / 200000000000000 : ℚ), (2845991602093 / 125000000000000 : ℚ), (3230162532087 / 100000000000000 : ℚ), (200811871427 / 7812500000000 : ℚ), (26320937103749 / 250000000000000 : ℚ), (501542412469253 / 1000000000000000 : ℚ), (99999999999947 / 100000000000 : ℚ), (644560005260773 / 100000000000000 : ℚ), (733584332699 / 78125000000 : ℚ), (16320587381729 / 1000000000000000 : ℚ), (131657936881857 / 1000000000000000 : ℚ), (52893822953071 / 125000000000000 : ℚ), (642370332155571 / 1000000000000 : ℚ), (40559301141753 / 1000000000000000 : ℚ), (26684466293791 / 1000000000000000 : ℚ), (603928050380137 / 1000000000000000 : ℚ), (6754694093651 / 312500000000 : ℚ), (1893099823943 / 100000000000000 : ℚ), (25343489849283 / 31250000000000 : ℚ), (19981191780383 / 500000000000000 : ℚ), (97106462359859 / 500000000000000 : ℚ), (40761768716647 / 250000000000000 : ℚ), (22324026500667 / 100000000000000 : ℚ)]

theorem theta_ok : checkPosParams pos θq = true := by decide +kernel

/-- Condiciones iniciales nominales. -/
def xq : Fin 25 → ℚ := ![(1 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (575218758977949 / 10000000000000000 : ℚ), (96025702716769 / 500000000000000 : ℚ), (0 : ℚ), (514562213223039 / 1000000000000000 : ℚ), (287974352643203 / 1000000000000000 : ℚ), (541202870022029 / 100000000000000000 : ℚ), (400416634006059 / 1000000000000000000 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (33494876486229 / 250000000000000 : ℚ), (7208935356827 / 125000000000000 : ℚ), (0 : ℚ), (1 : ℚ), (0 : ℚ)]

theorem x0_ok : checkNonneg xq = true := by decide +kernel

/-- **Teorema final, sin condiciones pendientes**: para todo T ≥ 0 la solución
nominal existe en [0, T], es ≥ 0, queda en el dominio, y la trayectoria es
diferenciable respecto a θ en θ₀. -/
def final := @network_final _ _ pos Rx net_ok c growth_ok θq theta_ok xq x0_ok

end Models.Isensee_JCB2018

#print axioms Models.Isensee_JCB2018.final
