import KineticNetwork

/-! Modelo `Lucarelli_CellSystems2018` (forma de red), traducido automáticamente de SBML por
`certificados/sbml_to_lean.py`. No editar a mano.

Estados (33): TGFb, Rec, TGFb_pRec, S2, S3, S4, S2_S4_S4, ppS2_ppS2_ppS2, ppS3_ppS3_ppS3, S4_S4_S4, pS2, pS3, ppS2, ppS3, ppS2_ppS2_S4, ppS2_ppS2_ppS3, ppS2_ppS3_ppS3, ppS3_ppS3_S4, ppS2_ppS3_S4, ppS3_S4_S4, ppS2_S4_S4, geneA, geneB, geneC, geneD, geneE, geneF, geneG, geneH, geneI, geneJ, geneK, geneL

Parámetros estimados θ (69): Rec_act, S_dephos, S_dephosphos, S_phos, geneA_act1, geneA_act2, geneA_inh2, geneA_inh3, geneA_turn, geneB_act1, geneB_act2, geneB_act3, geneB_inh2, geneB_inh3, geneB_turn, geneC_act1, geneC_inh2, geneC_inh3, geneC_turn, geneD_act1, geneD_act2, geneD_inh2, geneD_inh3, geneD_turn, geneE_act2, geneE_act3, geneE_inh1, geneE_inh2, geneE_inh3, geneE_turn, geneF_act1, geneF_act2, geneF_act3, geneF_inh1, geneF_turn, geneG_act1, geneG_act2, geneG_inh2, geneG_inh3, geneG_turn, geneH_act2, geneH_act3, geneH_inh1, geneH_inh2, geneH_inh3, geneH_turn, geneI_act1, geneI_inh2, geneI_inh3, geneI_turn, geneJ_inh1, geneJ_inh2, geneJ_inh3, geneJ_turn, geneK_act1, geneK_act2, geneK_inh2, geneK_inh3, geneK_turn, geneL_act2, geneL_inh1, geneL_inh2, geneL_inh3, geneL_turn, init_Rec, k_233, k_234, k_244, pRec_degind
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck KineticNetwork

namespace Models.Lucarelli_CellSystems2018

/-- Máscara de parámetros positivos (nominal > 0 o escala log). -/
def pos : Fin 69 → Bool := fun _ => true

/-- Términos de velocidad con su columna estequiométrica (67 términos). -/
def Rx : List (KExpr 33 69 × List (Fin 33 × ℚ)) := [
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.var 1)) (KExpr.par 0)) (KExpr.var 0)), [(0, (-100 / 1317 : ℚ)), (1, (-100 / 1317 : ℚ)), (2, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.var 2)) (KExpr.par 68)), [(2, (-100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.var 3)) (KExpr.par 3)) (KExpr.var 2)), [(3, (-100 / 1317 : ℚ)), (12, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.par 1)) (KExpr.var 10)), [(3, (100 / 1317 : ℚ)), (10, (-100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.var 4)) (KExpr.par 3)) (KExpr.var 2)), [(4, (-100 / 1317 : ℚ)), (13, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.par 1)) (KExpr.var 11)), [(4, (100 / 1317 : ℚ)), (11, (-100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.qconst (2 : ℚ))) (KExpr.par 2)) (KExpr.var 14)), [(5, (100 / 1317 : ℚ)), (10, (100 / 1317 : ℚ)), (12, (100 / 1317 : ℚ)), (14, (-100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.qconst (2 : ℚ))) (KExpr.par 2)) (KExpr.var 17)), [(5, (100 / 1317 : ℚ)), (11, (100 / 1317 : ℚ)), (13, (100 / 1317 : ℚ)), (17, (-100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.npow (KExpr.var 5) 2)) (KExpr.par 67)) (KExpr.var 12)), [(5, (-200 / 1317 : ℚ)), (12, (-100 / 1317 : ℚ)), (20, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.par 2)) (KExpr.var 20)), [(5, (200 / 1317 : ℚ)), (10, (100 / 1317 : ℚ)), (20, (-100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.par 2)) (KExpr.var 19)), [(5, (200 / 1317 : ℚ)), (11, (100 / 1317 : ℚ)), (19, (-100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.var 5)) (KExpr.par 66)) (KExpr.var 12)) (KExpr.var 13)), [(5, (-100 / 1317 : ℚ)), (12, (-100 / 1317 : ℚ)), (13, (-100 / 1317 : ℚ)), (18, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.par 2)) (KExpr.var 18)), [(5, (200 / 1317 : ℚ)), (10, (100 / 1317 : ℚ)), (11, (100 / 1317 : ℚ)), (12, (100 / 1317 : ℚ)), (13, (100 / 1317 : ℚ)), (18, (-200 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.qconst (3 : ℚ))) (KExpr.par 2)) (KExpr.var 7)), [(7, (-100 / 1317 : ℚ)), (10, (100 / 1317 : ℚ)), (12, (200 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.qconst (3 : ℚ))) (KExpr.par 2)) (KExpr.var 8)), [(8, (-100 / 1317 : ℚ)), (11, (100 / 1317 : ℚ)), (13, (200 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.par 2)) (KExpr.var 12)), [(10, (100 / 1317 : ℚ)), (12, (-100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.qconst (2 : ℚ))) (KExpr.par 2)) (KExpr.var 15)), [(10, (100 / 1317 : ℚ)), (12, (100 / 1317 : ℚ)), (13, (100 / 1317 : ℚ)), (15, (-100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.par 2)) (KExpr.var 16)), [(10, (100 / 1317 : ℚ)), (13, (200 / 1317 : ℚ)), (16, (-100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.par 2)) (KExpr.var 13)), [(11, (100 / 1317 : ℚ)), (13, (-100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.par 2)) (KExpr.var 15)), [(11, (100 / 1317 : ℚ)), (12, (200 / 1317 : ℚ)), (15, (-100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.qconst (2 : ℚ))) (KExpr.par 2)) (KExpr.var 16)), [(11, (100 / 1317 : ℚ)), (12, (100 / 1317 : ℚ)), (13, (100 / 1317 : ℚ)), (16, (-100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.par 65)) (KExpr.var 12)) (KExpr.npow (KExpr.var 13) 2)), [(12, (-100 / 1317 : ℚ)), (13, (-200 / 1317 : ℚ)), (16, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.par 8) (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 6) (KExpr.var 20)) (KExpr.mul (KExpr.par 7) (KExpr.var 16))) (KExpr.qconst (1 : ℚ))))), [(21, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.mul (KExpr.par 5) (KExpr.var 20)) (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 6) (KExpr.var 20)) (KExpr.mul (KExpr.par 7) (KExpr.var 16))) (KExpr.qconst (1 : ℚ))))), [(21, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.mul (KExpr.par 4) (KExpr.var 18)) (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 6) (KExpr.var 20)) (KExpr.mul (KExpr.par 7) (KExpr.var 16))) (KExpr.qconst (1 : ℚ))))), [(21, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.var 21)) (KExpr.par 8)), [(21, (-100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.par 14) (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 12) (KExpr.var 20)) (KExpr.mul (KExpr.par 13) (KExpr.var 16))) (KExpr.qconst (1 : ℚ))))), [(22, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.mul (KExpr.par 10) (KExpr.var 20)) (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 12) (KExpr.var 20)) (KExpr.mul (KExpr.par 13) (KExpr.var 16))) (KExpr.qconst (1 : ℚ))))), [(22, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.mul (KExpr.par 9) (KExpr.var 18)) (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 12) (KExpr.var 20)) (KExpr.mul (KExpr.par 13) (KExpr.var 16))) (KExpr.qconst (1 : ℚ))))), [(22, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.mul (KExpr.par 11) (KExpr.var 16)) (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 12) (KExpr.var 20)) (KExpr.mul (KExpr.par 13) (KExpr.var 16))) (KExpr.qconst (1 : ℚ))))), [(22, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.var 22)) (KExpr.par 14)), [(22, (-100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.par 18) (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 16) (KExpr.var 20)) (KExpr.mul (KExpr.par 17) (KExpr.var 16))) (KExpr.qconst (1 : ℚ))))), [(23, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.mul (KExpr.par 15) (KExpr.var 18)) (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 16) (KExpr.var 20)) (KExpr.mul (KExpr.par 17) (KExpr.var 16))) (KExpr.qconst (1 : ℚ))))), [(23, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.var 23)) (KExpr.par 18)), [(23, (-100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.par 23) (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 21) (KExpr.var 20)) (KExpr.mul (KExpr.par 22) (KExpr.var 16))) (KExpr.qconst (1 : ℚ))))), [(24, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.mul (KExpr.par 20) (KExpr.var 20)) (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 21) (KExpr.var 20)) (KExpr.mul (KExpr.par 22) (KExpr.var 16))) (KExpr.qconst (1 : ℚ))))), [(24, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.mul (KExpr.par 19) (KExpr.var 18)) (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 21) (KExpr.var 20)) (KExpr.mul (KExpr.par 22) (KExpr.var 16))) (KExpr.qconst (1 : ℚ))))), [(24, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.var 24)) (KExpr.par 23)), [(24, (-100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.par 29) (KExpr.add (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 27) (KExpr.var 20)) (KExpr.mul (KExpr.par 26) (KExpr.var 18))) (KExpr.mul (KExpr.par 28) (KExpr.var 16))) (KExpr.qconst (1 : ℚ))))), [(25, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.mul (KExpr.par 24) (KExpr.var 20)) (KExpr.add (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 27) (KExpr.var 20)) (KExpr.mul (KExpr.par 26) (KExpr.var 18))) (KExpr.mul (KExpr.par 28) (KExpr.var 16))) (KExpr.qconst (1 : ℚ))))), [(25, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.mul (KExpr.par 25) (KExpr.var 16)) (KExpr.add (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 27) (KExpr.var 20)) (KExpr.mul (KExpr.par 26) (KExpr.var 18))) (KExpr.mul (KExpr.par 28) (KExpr.var 16))) (KExpr.qconst (1 : ℚ))))), [(25, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.var 25)) (KExpr.par 29)), [(25, (-100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.par 34) (KExpr.add (KExpr.mul (KExpr.par 33) (KExpr.var 18)) (KExpr.qconst (1 : ℚ))))), [(26, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.mul (KExpr.par 31) (KExpr.var 20)) (KExpr.add (KExpr.mul (KExpr.par 33) (KExpr.var 18)) (KExpr.qconst (1 : ℚ))))), [(26, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.mul (KExpr.par 30) (KExpr.var 18)) (KExpr.add (KExpr.mul (KExpr.par 33) (KExpr.var 18)) (KExpr.qconst (1 : ℚ))))), [(26, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.mul (KExpr.par 32) (KExpr.var 16)) (KExpr.add (KExpr.mul (KExpr.par 33) (KExpr.var 18)) (KExpr.qconst (1 : ℚ))))), [(26, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.var 26)) (KExpr.par 34)), [(26, (-100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.par 39) (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 37) (KExpr.var 20)) (KExpr.mul (KExpr.par 38) (KExpr.var 16))) (KExpr.qconst (1 : ℚ))))), [(27, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.mul (KExpr.par 36) (KExpr.var 20)) (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 37) (KExpr.var 20)) (KExpr.mul (KExpr.par 38) (KExpr.var 16))) (KExpr.qconst (1 : ℚ))))), [(27, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.mul (KExpr.par 35) (KExpr.var 18)) (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 37) (KExpr.var 20)) (KExpr.mul (KExpr.par 38) (KExpr.var 16))) (KExpr.qconst (1 : ℚ))))), [(27, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.var 27)) (KExpr.par 39)), [(27, (-100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.par 45) (KExpr.add (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 43) (KExpr.var 20)) (KExpr.mul (KExpr.par 42) (KExpr.var 18))) (KExpr.mul (KExpr.par 44) (KExpr.var 16))) (KExpr.qconst (1 : ℚ))))), [(28, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.mul (KExpr.par 40) (KExpr.var 20)) (KExpr.add (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 43) (KExpr.var 20)) (KExpr.mul (KExpr.par 42) (KExpr.var 18))) (KExpr.mul (KExpr.par 44) (KExpr.var 16))) (KExpr.qconst (1 : ℚ))))), [(28, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.mul (KExpr.par 41) (KExpr.var 16)) (KExpr.add (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 43) (KExpr.var 20)) (KExpr.mul (KExpr.par 42) (KExpr.var 18))) (KExpr.mul (KExpr.par 44) (KExpr.var 16))) (KExpr.qconst (1 : ℚ))))), [(28, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.var 28)) (KExpr.par 45)), [(28, (-100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.par 49) (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 47) (KExpr.var 20)) (KExpr.mul (KExpr.par 48) (KExpr.var 16))) (KExpr.qconst (1 : ℚ))))), [(29, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.mul (KExpr.par 46) (KExpr.var 18)) (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 47) (KExpr.var 20)) (KExpr.mul (KExpr.par 48) (KExpr.var 16))) (KExpr.qconst (1 : ℚ))))), [(29, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.var 29)) (KExpr.par 49)), [(29, (-100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.par 53) (KExpr.add (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 51) (KExpr.var 20)) (KExpr.mul (KExpr.par 50) (KExpr.var 18))) (KExpr.mul (KExpr.par 52) (KExpr.var 16))) (KExpr.qconst (1 : ℚ))))), [(30, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.var 30)) (KExpr.par 53)), [(30, (-100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.par 58) (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 56) (KExpr.var 20)) (KExpr.mul (KExpr.par 57) (KExpr.var 16))) (KExpr.qconst (1 : ℚ))))), [(31, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.mul (KExpr.par 55) (KExpr.var 20)) (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 56) (KExpr.var 20)) (KExpr.mul (KExpr.par 57) (KExpr.var 16))) (KExpr.qconst (1 : ℚ))))), [(31, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.mul (KExpr.par 54) (KExpr.var 18)) (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 56) (KExpr.var 20)) (KExpr.mul (KExpr.par 57) (KExpr.var 16))) (KExpr.qconst (1 : ℚ))))), [(31, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.var 31)) (KExpr.par 58)), [(31, (-100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.par 63) (KExpr.add (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 61) (KExpr.var 20)) (KExpr.mul (KExpr.par 60) (KExpr.var 18))) (KExpr.mul (KExpr.par 62) (KExpr.var 16))) (KExpr.qconst (1 : ℚ))))), [(32, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.div (KExpr.mul (KExpr.par 59) (KExpr.var 20)) (KExpr.add (KExpr.add (KExpr.add (KExpr.mul (KExpr.par 61) (KExpr.var 20)) (KExpr.mul (KExpr.par 60) (KExpr.var 18))) (KExpr.mul (KExpr.par 62) (KExpr.var 16))) (KExpr.qconst (1 : ℚ))))), [(32, (100 / 1317 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1317 / 100 : ℚ)) (KExpr.var 32)) (KExpr.par 63)), [(32, (-100 / 1317 : ℚ))])
]

/-- El campo del modelo: `Fᵢ = Σ_r coef_r(i) · V_r`. -/
def F : Fin 33 → KExpr 33 69 := netF Rx

/-- Dominio ⊇ ortante y cuasi-positividad (Lean ejecuta el comprobador). -/
theorem net_ok : checkNet pos Rx = true := by decide +kernel

/-- Pesos de la combinación con crecimiento lineal (cᵢ ≥ 1). -/
def c : Fin 33 → ℚ := fun _ => (1 : ℚ)

theorem growth_ok : checkGrowth pos c Rx = true := by decide +kernel

/-- θ₀ nominal (PEtab), en racionales exactos. -/
def θq : Fin 69 → ℚ := ![(5969840220269 / 1000000000000000 : ℚ), (6953548146873 / 25000000000000 : ℚ), (47612869772851 / 1000000000000000 : ℚ), (188560518414783 / 500000000000000 : ℚ), (14141482569873 / 1000000000000000 : ℚ), (32190500151 / 40000000000000 : ℚ), (46327226117843 / 1000000000000000 : ℚ), (42027371711 / 1600000000000 : ℚ), (114312387943 / 25000000000000 : ℚ), (459613121530843 / 1000000000000000 : ℚ), (36691709669863 / 500000000000000 : ℚ), (30882914826193 / 1000000000000000 : ℚ), (370681610238963 / 500000000000000 : ℚ), (51096253005329 / 125000000000000 : ℚ), (2812426923747 / 250000000000000 : ℚ), (7148127389081 / 1000000000000000 : ℚ), (18280189253089 / 1000000000000000 : ℚ), (7071579465141 / 200000000000000 : ℚ), (3788712045359 / 1000000000000000 : ℚ), (5598225269929 / 500000000000000 : ℚ), (274226711471 / 1000000000000000 : ℚ), (43627223194393 / 500000000000000 : ℚ), (3172289880739 / 31250000000000 : ℚ), (404381477799 / 500000000000000 : ℚ), (100646343942677 / 100000000000000 : ℚ), (119862653214783 / 20000000000000 : ℚ), (161498243061609 / 20000000000000 : ℚ), (141088296804943 / 100000000000000 : ℚ), (48003507024729 / 5000000000000 : ℚ), (123153223674769 / 1000000000000000 : ℚ), (498704968538967 / 500000000000 : ℚ), (101459134398437 / 500000000000000 : ℚ), (8264046188167 / 400000000000 : ℚ), (180874131735147 / 50000000000000 : ℚ), (183914072534321 / 5000000000000 : ℚ), (157862106596631 / 250000000000 : ℚ), (558423040781623 / 10000000000000 : ℚ), (17226968457893 / 1000000000000000 : ℚ), (98713842107 / 125000000000000 : ℚ), (29852886647117 / 100000000000 : ℚ), (27940450018047 / 312500000000 : ℚ), (499970637735631 / 500000000000 : ℚ), (999998157205339 / 1000000000000 : ℚ), (37867023347391 / 2000000000000 : ℚ), (218414317332393 / 1000000000000 : ℚ), (39697283479443 / 40000000000000 : ℚ), (930363565946309 / 100000000000000 : ℚ), (159413556925591 / 500000000000 : ℚ), (499992156901293 / 500000000000 : ℚ), (3283125626569 / 1000000000000000 : ℚ), (238552562127343 / 500000000000000 : ℚ), (9916494960393 / 1000000000000000 : ℚ), (4269289315363 / 500000000000000 : ℚ), (14037170066501 / 1000000000000000 : ℚ), (12554063210037 / 1000000000000000 : ℚ), (138829721273 / 500000000000000 : ℚ), (135229129075373 / 100000000000000 : ℚ), (243517542511281 / 100000000000000 : ℚ), (1802014604909 / 500000000000000 : ℚ), (469494240947 / 1000000000000000 : ℚ), (8084691558281 / 6250000000000 : ℚ), (62052638950287 / 1000000000000000 : ℚ), (134647700641231 / 1000000000000000 : ℚ), (14959914457387 / 1000000000000000 : ℚ), (22946627785211 / 12500000000000 : ℚ), (71042939697897 / 500000000000000 : ℚ), (97245616667 / 250000000000000 : ℚ), (839675013568961 / 100000000000000000000 : ℚ), (516941024359 / 12500000000000 : ℚ)]

theorem theta_ok : checkPosParams pos θq = true := by decide +kernel

/-- Condición inicial x₀(θ) (asignaciones iniciales de SBML). -/
def G : Fin 33 → KExpr 33 69 := ![
  (KExpr.qconst (0 : ℚ)),
  (KExpr.par 64),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (0 : ℚ)),
  (KExpr.qconst (1 : ℚ)),
  (KExpr.qconst (1 : ℚ)),
  (KExpr.qconst (1 : ℚ)),
  (KExpr.qconst (1 : ℚ)),
  (KExpr.qconst (1 : ℚ)),
  (KExpr.qconst (1 : ℚ)),
  (KExpr.qconst (1 : ℚ)),
  (KExpr.qconst (1 : ℚ)),
  (KExpr.qconst (1 : ℚ)),
  (KExpr.qconst (1 : ℚ)),
  (KExpr.qconst (1 : ℚ)),
  (KExpr.qconst (1 : ℚ))
]

theorem init_ok : checkInit pos G = true := by decide +kernel

/-- **Teorema final, sin condiciones pendientes** (condición inicial x₀(θ)). -/
def final := @network_final_init _ _ pos Rx net_ok c growth_ok G init_ok θq theta_ok

end Models.Lucarelli_CellSystems2018

#print axioms Models.Lucarelli_CellSystems2018.final
