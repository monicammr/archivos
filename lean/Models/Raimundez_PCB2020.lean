import KineticNetwork

/-! Modelo `Raimundez_PCB2020` (forma de red), traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (22): EGFR, EGFR_CET, EGFR_EGF, EGFR_EGF_2, pEGFR_EGF_2, pEGFR_EGF_2_i, MMET, MMET_2, pMMET_2, pMMET_2_i, MMET_EGFR, pMMET_pEGFR, pMMET_pEGFR_i, MMET_METinh, MMET_MMET_METinh, MMET_METinh_2, EGFR_MMET_METinh, RAS_GTP, pMAPK, pPI3K, pMPI3K, pAKT

Parámetros estimados θ (57): KD_EGFR_CET, KD_EGFR_EGF, KD_METinh, d_AKTtotal__MKN1_2_HS746T, d_AKTtotal__fm_2_hm, d_MAPKtotal__MKN1_2_HS746T, d_MAPKtotal__fm_2_hm, d_MPI3Ktotal__fm_2_hm, d_PI3Ktotal__fm_2_hm, d_RAStotal__MKN1_2_HS746T, d_RAStotal__fm_2_hm, d_kdeg_membran__MKN1_2_HS746T, d_kdeg_pEGFR_EGF_2_i__MKN1_2_HS746T, d_kexp_pEGFR_EGF_2_i__MKN1_2_HS746T, d_kimp_pEGFR_EGF_2__MKN1_2_HS746T, d_ksyn_EGFR__MKN1_2_HS746T, d_ksyn_EGFR__fm_2_hm, d_ksyn_MMET__fm_2_hm, ka_AKT__MKN1, ka_MAPK__MKN1, ka_PI3K__basal, ka_PI3K__pEGFR_EGF_2, ka_RAS__basal__MKN1, ka_RAS__pEGFR_EGF_2__MKN1, kbin_EGFR_CET, kbin_EGFR_EGF, kdeg_membran__MKN1, kdeg_pEGFR_EGF_2_i__MKN1, kdim_EGFR_EGF, kdim_MMET, kdim_MMET_EGFR, kdim_MMETinh, kexp_pEGFR_EGF_2_i__MKN1, ki_AKT__MKN1, ki_MAPK, ki_PI3K__MKN1, ki_RAS__MKN1, kimp_pEGFR_EGF_2__MKN1, kpho_EGFR_EGF, kpho_MMET, kpho_MMET_EGFR, ksyn_MMET__HS746T_fm, xi_ka_PI3K_pMMET_2, xi_ka_PI3K_pMMET_pEGFR, xi_ka_RAS_pMMET_2, xi_ka_RAS_pMMET_pEGFR, xi_kdeg_pMMET_2_i, xi_kdeg_pMMET_pEGFR_i, xi_kdim_MMET, xi_kdim_MMET_EGFR, xi_kexp_pMMET_2_i, xi_kexp_pMMET_pEGFR_i, xi_ki_MPI3K, xi_kimp_pMMET_2, xi_kimp_pMMET_pEGFR, xi_kpho_MMET, xi_kpho_MMET_EGFR
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck KineticNetwork

namespace Models.Raimundez_PCB2020

/-- Máscara de parámetros positivos (nominal > 0 o escala log). -/
def pos : Fin 57 → Bool := ![true, true, true, false, true, false, true, false, false, false, false, false, true, false, false, false, false, false, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true]

/-- Términos de velocidad con su columna estequiométrica (91 términos). -/
def Rx : List (KExpr 22 57 × List (Fin 22 × ℚ)) := [
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (1 : ℚ))) (KExpr.exp (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 15)) (KExpr.mul (KExpr.par 16) (KExpr.qconst (1 : ℚ))))))), [(0, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 0)) (KExpr.mul (KExpr.par 26) (KExpr.exp (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 11))))), [(0, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (343 / 50 : ℚ)) (KExpr.qconst (1 : ℚ))) (KExpr.qconst (1 : ℚ)))) (KExpr.var 0)) (KExpr.par 24)), [(0, (-1 : ℚ)), (1, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 1)) (KExpr.par 0)) (KExpr.par 24)), [(0, (1 : ℚ)), (1, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (161 / 1000 : ℚ)) (KExpr.qconst (1 : ℚ))) (KExpr.qconst (1 : ℚ)))) (KExpr.var 0)) (KExpr.par 25)), [(0, (-1 : ℚ)), (2, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 2)) (KExpr.par 1)) (KExpr.par 25)), [(0, (1 : ℚ)), (2, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 32) (KExpr.exp (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 13))))) (KExpr.var 5)), [(0, (2 : ℚ)), (5, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 0)) (KExpr.var 6)) (KExpr.par 30)) (KExpr.par 49)), [(0, (-1 : ℚ)), (6, (-1 : ℚ)), (10, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 32) (KExpr.exp (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 13))))) (KExpr.var 12)) (KExpr.par 51)), [(0, (1 : ℚ)), (6, (1 : ℚ)), (12, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 0)) (KExpr.var 13)) (KExpr.par 30)) (KExpr.par 49)), [(0, (-1 : ℚ)), (13, (-1 : ℚ)), (16, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 1)) (KExpr.mul (KExpr.par 26) (KExpr.exp (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 11))))), [(1, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.npow (KExpr.var 2) 2)) (KExpr.par 28)), [(2, (-2 : ℚ)), (3, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 2)) (KExpr.mul (KExpr.par 26) (KExpr.exp (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 11))))), [(2, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 3)) (KExpr.par 38)), [(3, (-1 : ℚ)), (4, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 3)) (KExpr.mul (KExpr.par 26) (KExpr.exp (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 11))))), [(3, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 37) (KExpr.exp (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 14))))) (KExpr.var 4)), [(4, (-1 : ℚ)), (5, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 27) (KExpr.exp (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 12))))) (KExpr.var 5)), [(5, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 41)) (KExpr.exp (KExpr.mul (KExpr.par 17) (KExpr.qconst (1 : ℚ)))))), [(6, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 6)) (KExpr.mul (KExpr.par 26) (KExpr.exp (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 11))))), [(6, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (1 : ℚ)))) (KExpr.var 6)) (KExpr.par 31)), [(6, (-1 : ℚ)), (13, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 2)) (KExpr.var 13)) (KExpr.par 31)), [(6, (1 : ℚ)), (13, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.npow (KExpr.var 6) 2)) (KExpr.par 29)) (KExpr.par 48)), [(6, (-2 : ℚ)), (7, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 32) (KExpr.exp (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 13))))) (KExpr.var 9)) (KExpr.par 50)), [(6, (2 : ℚ)), (9, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 6)) (KExpr.var 13)) (KExpr.par 29)) (KExpr.par 48)), [(6, (-1 : ℚ)), (13, (-1 : ℚ)), (14, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 7)) (KExpr.par 39)) (KExpr.par 55)), [(7, (-1 : ℚ)), (8, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 7)) (KExpr.mul (KExpr.par 26) (KExpr.exp (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 11))))), [(7, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (1 : ℚ)))) (KExpr.var 7)) (KExpr.par 31)), [(7, (-1 : ℚ)), (14, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 37) (KExpr.exp (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 14))))) (KExpr.var 8)) (KExpr.par 53)), [(8, (-1 : ℚ)), (9, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 27) (KExpr.exp (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 12))))) (KExpr.var 9)) (KExpr.par 46)), [(9, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 10)) (KExpr.par 40)) (KExpr.par 56)), [(10, (-1 : ℚ)), (11, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 10)) (KExpr.mul (KExpr.par 26) (KExpr.exp (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 11))))), [(10, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 37) (KExpr.exp (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 14))))) (KExpr.var 11)) (KExpr.par 54)), [(11, (-1 : ℚ)), (12, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 27) (KExpr.exp (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 12))))) (KExpr.var 12)) (KExpr.par 47)), [(12, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 13)) (KExpr.mul (KExpr.par 26) (KExpr.exp (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 11))))), [(13, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.npow (KExpr.var 13) 2)) (KExpr.par 29)) (KExpr.par 48)), [(13, (-2 : ℚ)), (15, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (1 : ℚ)))) (KExpr.var 14)) (KExpr.par 31)), [(14, (-1 : ℚ)), (15, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 14)) (KExpr.mul (KExpr.par 26) (KExpr.exp (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 11))))), [(14, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 15)) (KExpr.mul (KExpr.par 26) (KExpr.exp (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 11))))), [(15, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 22) (KExpr.exp (KExpr.qconst (0 : ℚ))))) (KExpr.var 17)), [(17, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 22) (KExpr.exp (KExpr.qconst (0 : ℚ))))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.exp (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 9)) (KExpr.mul (KExpr.par 10) (KExpr.qconst (1 : ℚ))))))), [(17, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 23) (KExpr.exp (KExpr.qconst (0 : ℚ))))) (KExpr.var 4)) (KExpr.var 17)), [(17, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 23) (KExpr.exp (KExpr.qconst (0 : ℚ))))) (KExpr.var 4)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.exp (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 9)) (KExpr.mul (KExpr.par 10) (KExpr.qconst (1 : ℚ))))))), [(17, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 23) (KExpr.exp (KExpr.qconst (0 : ℚ))))) (KExpr.var 5)) (KExpr.var 17)), [(17, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 23) (KExpr.exp (KExpr.qconst (0 : ℚ))))) (KExpr.var 5)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.exp (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 9)) (KExpr.mul (KExpr.par 10) (KExpr.qconst (1 : ℚ))))))), [(17, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 23) (KExpr.exp (KExpr.qconst (0 : ℚ))))) (KExpr.var 11)) (KExpr.par 45)) (KExpr.var 17)), [(17, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 23) (KExpr.exp (KExpr.qconst (0 : ℚ))))) (KExpr.var 11)) (KExpr.par 45)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.exp (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 9)) (KExpr.mul (KExpr.par 10) (KExpr.qconst (1 : ℚ))))))), [(17, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 23) (KExpr.exp (KExpr.qconst (0 : ℚ))))) (KExpr.var 12)) (KExpr.par 45)) (KExpr.var 17)), [(17, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 23) (KExpr.exp (KExpr.qconst (0 : ℚ))))) (KExpr.var 12)) (KExpr.par 45)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.exp (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 9)) (KExpr.mul (KExpr.par 10) (KExpr.qconst (1 : ℚ))))))), [(17, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 23) (KExpr.exp (KExpr.qconst (0 : ℚ))))) (KExpr.var 8)) (KExpr.par 44)) (KExpr.var 17)), [(17, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 23) (KExpr.exp (KExpr.qconst (0 : ℚ))))) (KExpr.var 8)) (KExpr.par 44)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.exp (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 9)) (KExpr.mul (KExpr.par 10) (KExpr.qconst (1 : ℚ))))))), [(17, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 23) (KExpr.exp (KExpr.qconst (0 : ℚ))))) (KExpr.var 9)) (KExpr.par 44)) (KExpr.var 17)), [(17, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 23) (KExpr.exp (KExpr.qconst (0 : ℚ))))) (KExpr.var 9)) (KExpr.par 44)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.exp (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 9)) (KExpr.mul (KExpr.par 10) (KExpr.qconst (1 : ℚ))))))), [(17, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 17)) (KExpr.mul (KExpr.par 36) (KExpr.exp (KExpr.qconst (0 : ℚ))))), [(17, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 17)) (KExpr.mul (KExpr.par 19) (KExpr.exp (KExpr.qconst (0 : ℚ))))) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.exp (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 5)) (KExpr.mul (KExpr.par 6) (KExpr.qconst (1 : ℚ))))))), [(18, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 17)) (KExpr.mul (KExpr.par 19) (KExpr.exp (KExpr.qconst (0 : ℚ))))) (KExpr.var 18)), [(18, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 34)) (KExpr.var 18)), [(18, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 20)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (1 : ℚ))) (KExpr.exp (KExpr.mul (KExpr.par 8) (KExpr.qconst (1 : ℚ)))))), [(19, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 20)) (KExpr.var 19)), [(19, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 21)) (KExpr.var 4)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (1 : ℚ))) (KExpr.exp (KExpr.mul (KExpr.par 8) (KExpr.qconst (1 : ℚ)))))), [(19, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 21)) (KExpr.var 4)) (KExpr.var 19)), [(19, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 21)) (KExpr.var 5)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (1 : ℚ))) (KExpr.exp (KExpr.mul (KExpr.par 8) (KExpr.qconst (1 : ℚ)))))), [(19, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 21)) (KExpr.var 5)) (KExpr.var 19)), [(19, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 21)) (KExpr.var 11)) (KExpr.par 43)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (1 : ℚ))) (KExpr.exp (KExpr.mul (KExpr.par 8) (KExpr.qconst (1 : ℚ)))))), [(19, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 21)) (KExpr.var 11)) (KExpr.par 43)) (KExpr.var 19)), [(19, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 21)) (KExpr.var 12)) (KExpr.par 43)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (1 : ℚ))) (KExpr.exp (KExpr.mul (KExpr.par 8) (KExpr.qconst (1 : ℚ)))))), [(19, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 21)) (KExpr.var 12)) (KExpr.par 43)) (KExpr.var 19)), [(19, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 21)) (KExpr.var 8)) (KExpr.par 42)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (1 : ℚ))) (KExpr.exp (KExpr.mul (KExpr.par 8) (KExpr.qconst (1 : ℚ)))))), [(19, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 21)) (KExpr.var 8)) (KExpr.par 42)) (KExpr.var 19)), [(19, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 21)) (KExpr.var 9)) (KExpr.par 42)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (1 : ℚ))) (KExpr.exp (KExpr.mul (KExpr.par 8) (KExpr.qconst (1 : ℚ)))))), [(19, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 21)) (KExpr.var 9)) (KExpr.par 42)) (KExpr.var 19)), [(19, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 35) (KExpr.exp (KExpr.qconst (0 : ℚ))))) (KExpr.var 19)), [(19, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 20)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (1 : ℚ))) (KExpr.exp (KExpr.mul (KExpr.par 7) (KExpr.qconst (1 : ℚ)))))), [(20, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 20)) (KExpr.var 20)), [(20, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 21)) (KExpr.var 4)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (1 : ℚ))) (KExpr.exp (KExpr.mul (KExpr.par 7) (KExpr.qconst (1 : ℚ)))))), [(20, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 21)) (KExpr.var 4)) (KExpr.var 20)), [(20, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 21)) (KExpr.var 5)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (1 : ℚ))) (KExpr.exp (KExpr.mul (KExpr.par 7) (KExpr.qconst (1 : ℚ)))))), [(20, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 21)) (KExpr.var 5)) (KExpr.var 20)), [(20, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 21)) (KExpr.var 11)) (KExpr.par 43)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (1 : ℚ))) (KExpr.exp (KExpr.mul (KExpr.par 7) (KExpr.qconst (1 : ℚ)))))), [(20, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 21)) (KExpr.var 11)) (KExpr.par 43)) (KExpr.var 20)), [(20, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 21)) (KExpr.var 12)) (KExpr.par 43)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (1 : ℚ))) (KExpr.exp (KExpr.mul (KExpr.par 7) (KExpr.qconst (1 : ℚ)))))), [(20, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 21)) (KExpr.var 12)) (KExpr.par 43)) (KExpr.var 20)), [(20, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 21)) (KExpr.var 8)) (KExpr.par 42)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (1 : ℚ))) (KExpr.exp (KExpr.mul (KExpr.par 7) (KExpr.qconst (1 : ℚ)))))), [(20, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 21)) (KExpr.var 8)) (KExpr.par 42)) (KExpr.var 20)), [(20, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 21)) (KExpr.var 9)) (KExpr.par 42)) (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.qconst (1 : ℚ))) (KExpr.exp (KExpr.mul (KExpr.par 7) (KExpr.qconst (1 : ℚ)))))), [(20, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 21)) (KExpr.var 9)) (KExpr.par 42)) (KExpr.var 20)), [(20, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 35) (KExpr.exp (KExpr.qconst (0 : ℚ))))) (KExpr.var 20)) (KExpr.par 52)), [(20, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 18) (KExpr.exp (KExpr.qconst (0 : ℚ))))) (KExpr.var 19)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.exp (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 3)) (KExpr.mul (KExpr.par 4) (KExpr.qconst (1 : ℚ))))))), [(21, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 18) (KExpr.exp (KExpr.qconst (0 : ℚ))))) (KExpr.var 19)) (KExpr.var 21)), [(21, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 18) (KExpr.exp (KExpr.qconst (0 : ℚ))))) (KExpr.var 20)) (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.exp (KExpr.add (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.par 3)) (KExpr.mul (KExpr.par 4) (KExpr.qconst (1 : ℚ))))))), [(21, (1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 18) (KExpr.exp (KExpr.qconst (0 : ℚ))))) (KExpr.var 20)) (KExpr.var 21)), [(21, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.par 33) (KExpr.exp (KExpr.qconst (0 : ℚ))))) (KExpr.var 21)), [(21, (-1 : ℚ))])
]

/-- El campo del modelo: `Fᵢ = Σ_r coef_r(i) · V_r`. -/
def F : Fin 22 → KExpr 22 57 := netF Rx

/-- Dominio ⊇ ortante y cuasi-positividad (Lean ejecuta el comprobador). -/
theorem net_ok : checkNet pos Rx = true := by decide +kernel

/-- Pesos de la combinación con crecimiento lineal (cᵢ ≥ 1). -/
def c : Fin 22 → ℚ := ![(1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ)]

theorem growth_ok : checkGrowth pos c Rx = true := by decide +kernel

/-- θ₀ nominal (PEtab), en racionales exactos. -/
def θq : Fin 57 → ℚ := ![(109006074670317 / 500000000000000 : ℚ), (320759905034371 / 1000000000000000 : ℚ), (41936901194249 / 1000000000000000 : ℚ), (0 : ℚ), (164584533834067 / 200000000000000 : ℚ), (0 : ℚ), (427450996540987 / 1000000000000000 : ℚ), (-154468079589527 / 100000000000000 : ℚ), (-26591786426383 / 50000000000000 : ℚ), (-53 / 500000000000000000000000 : ℚ), (-269095065224839 / 500000000000000 : ℚ), (-599975506316473 / 1000000000000000 : ℚ), (299999999999997 / 100000000000000 : ℚ), (-23823693668421 / 100000000000000 : ℚ), (-174579260575349 / 100000000000000 : ℚ), (-299999999999997 / 100000000000000 : ℚ), (-87595179128819 / 1000000000000000 : ℚ), (-103777794709737 / 200000000000000 : ℚ), (443101158324899 / 1000000000000 : ℚ), (499999999999971 / 500000000000 : ℚ), (182457535743 / 500000000000000 : ℚ), (42523583331 / 25000000000000 : ℚ), (214463346879 / 1000000000000000 : ℚ), (147 / 10000000 : ℚ), (585302658299007 / 1000000000000000 : ℚ), (444087429185171 / 50000000000000 : ℚ), (56476601633 / 25000000000000 : ℚ), (1669890305223 / 25000000000000 : ℚ), (404935859597 / 12500000000000 : ℚ), (261 / 10000000 : ℚ), (941098512801 / 500000000000000 : ℚ), (31271407854883 / 1000000000000000 : ℚ), (37584156164767 / 50000000000000 : ℚ), (92346483698029 / 5000000000000 : ℚ), (8708637255217 / 4000000000000 : ℚ), (65793992138507 / 50000000000000 : ℚ), (163478284431983 / 500000000000000 : ℚ), (373435102254419 / 500000000000000 : ℚ), (26882557408103 / 20000000000000 : ℚ), (254267401784407 / 100000000000000 : ℚ), (228150469537113 / 50000000000000 : ℚ), (26350805070197 / 1000000000000000 : ℚ), (60268173107809 / 200000000000 : ℚ), (30618886308551 / 40000000000000 : ℚ), (224675735902217 / 500000000000000 : ℚ), (126780575679463 / 500000000000000 : ℚ), (391855159071343 / 500000000000000 : ℚ), (353345024355609 / 100000000000000 : ℚ), (974771379091693 / 1000000000000000 : ℚ), (100042475919183 / 100000000000000 : ℚ), (62160442670351 / 50000000000000 : ℚ), (286399421450953 / 1000000000000000 : ℚ), (3220284184053 / 1000000000000000 : ℚ), (308615512251 / 4000000000000 : ℚ), (7960053436549 / 1000000000000000 : ℚ), (2081942203443 / 250000000000000 : ℚ), (69673144126817 / 1000000000000000 : ℚ)]

theorem theta_ok : checkPosParams pos θq = true := by decide +kernel

/-- Condiciones iniciales nominales. -/
def xq : Fin 22 → ℚ := ![(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]

theorem x0_ok : checkNonneg xq = true := by decide +kernel

/-- **Teorema final, sin condiciones pendientes**: para todo T ≥ 0 la solución
nominal existe en [0, T], es ≥ 0, queda en el dominio, y la trayectoria es
diferenciable respecto a θ en θ₀. -/
def final := @network_final _ _ pos Rx net_ok c growth_ok θq theta_ok xq x0_ok

end Models.Raimundez_PCB2020

#print axioms Models.Raimundez_PCB2020.final
