import Models.Chen_MSB2009.Base

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck KineticNetwork

namespace Models.Chen_MSB2009

def Rx_3 : List (KExpr 501 152 × List (Fin 501 × ℚ)) := [
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.var 424) (KExpr.var 391)) (KExpr.par 4))), [(391, (-1 : ℚ)), (392, (1 : ℚ)), (424, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 392) (KExpr.par 72))), [(391, (1 : ℚ)), (392, (-1 : ℚ)), (424, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.var 424) (KExpr.var 392)) (KExpr.par 4))), [(392, (-1 : ℚ)), (393, (1 : ℚ)), (424, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 393) (KExpr.par 72))), [(392, (1 : ℚ)), (393, (-1 : ℚ)), (424, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 405) (KExpr.par 141))), [(394, (1 : ℚ)), (403, (1 : ℚ)), (405, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.var 395) (KExpr.var 398)) (KExpr.par 57))), [(395, (-1 : ℚ)), (398, (-1 : ℚ)), (400, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 400) (KExpr.par 136))), [(395, (1 : ℚ)), (398, (1 : ℚ)), (400, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 400) (KExpr.par 137))), [(396, (1 : ℚ)), (400, (-1 : ℚ)), (401, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.var 396) (KExpr.var 403)) (KExpr.par 58))), [(396, (-1 : ℚ)), (403, (-1 : ℚ)), (405, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 405) (KExpr.par 139))), [(396, (1 : ℚ)), (403, (1 : ℚ)), (405, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 404) (KExpr.par 141))), [(396, (1 : ℚ)), (403, (1 : ℚ)), (404, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.var 398) (KExpr.var 397)) (KExpr.par 57))), [(397, (-1 : ℚ)), (398, (-1 : ℚ)), (399, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 399) (KExpr.par 136))), [(397, (1 : ℚ)), (398, (1 : ℚ)), (399, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 399) (KExpr.par 138))), [(399, (-1 : ℚ)), (401, (1 : ℚ)), (402, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.var 403) (KExpr.var 402)) (KExpr.par 59))), [(402, (-1 : ℚ)), (403, (-1 : ℚ)), (404, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 404) (KExpr.par 140))), [(402, (1 : ℚ)), (403, (1 : ℚ)), (404, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 466) (KExpr.par 82))), [(402, (1 : ℚ)), (466, (-1 : ℚ)), (468, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 467) (KExpr.par 82))), [(402, (1 : ℚ)), (467, (-1 : ℚ)), (468, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 425) (KExpr.par 70))), [(423, (1 : ℚ)), (424, (1 : ℚ)), (425, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 427) (KExpr.par 70))), [(424, (1 : ℚ)), (426, (1 : ℚ)), (427, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.var 452) (KExpr.var 470)) (KExpr.par 12))), [(452, (-1 : ℚ)), (470, (-1 : ℚ)), (475, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 475) (KExpr.par 83))), [(452, (1 : ℚ)), (470, (1 : ℚ)), (475, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.var 453) (KExpr.var 470)) (KExpr.par 12))), [(453, (-1 : ℚ)), (470, (-1 : ℚ)), (472, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 472) (KExpr.par 83))), [(453, (1 : ℚ)), (470, (1 : ℚ)), (472, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.var 454) (KExpr.var 470)) (KExpr.par 12))), [(454, (-1 : ℚ)), (470, (-1 : ℚ)), (474, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 474) (KExpr.par 83))), [(454, (1 : ℚ)), (470, (1 : ℚ)), (474, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.var 455) (KExpr.var 470)) (KExpr.par 12))), [(455, (-1 : ℚ)), (470, (-1 : ℚ)), (473, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 473) (KExpr.par 83))), [(455, (1 : ℚ)), (470, (1 : ℚ)), (473, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.var 456) (KExpr.var 470)) (KExpr.par 12))), [(456, (-1 : ℚ)), (470, (-1 : ℚ)), (476, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 476) (KExpr.par 83))), [(456, (1 : ℚ)), (470, (1 : ℚ)), (476, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.var 457) (KExpr.var 470)) (KExpr.par 12))), [(457, (-1 : ℚ)), (470, (-1 : ℚ)), (471, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 471) (KExpr.par 83))), [(457, (1 : ℚ)), (470, (1 : ℚ)), (471, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.var 458) (KExpr.var 470)) (KExpr.par 12))), [(458, (-1 : ℚ)), (470, (-1 : ℚ)), (477, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 477) (KExpr.par 83))), [(458, (1 : ℚ)), (470, (1 : ℚ)), (477, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.var 482)) (KExpr.par 149)), [(481, (1 : ℚ)), (482, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.npow (KExpr.var 483) 2) (KExpr.par 21))), [(483, (-2 : ℚ)), (485, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 485) (KExpr.par 92))), [(483, (2 : ℚ)), (485, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.mul (KExpr.var 483) (KExpr.var 487)) (KExpr.par 21))), [(483, (-1 : ℚ)), (487, (-1 : ℚ)), (494, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 494) (KExpr.par 92))), [(483, (1 : ℚ)), (487, (1 : ℚ)), (494, (-1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 486) (KExpr.par 46))), [(486, (-1 : ℚ)), (488, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.npow (KExpr.var 487) 2) (KExpr.par 21))), [(487, (-2 : ℚ)), (493, (1 : ℚ))]),
  ((KExpr.mul (KExpr.qconst (1 : ℚ)) (KExpr.mul (KExpr.var 493) (KExpr.par 92))), [(487, (2 : ℚ)), (493, (-1 : ℚ))]),
  ((KExpr.qconst (1 : ℚ)), [(500, (1 : ℚ))])
]

theorem net_ok_3 : checkNet pos Rx_3 = true := by decide +kernel

theorem growth_ok_3 : checkGrowth pos c Rx_3 = true := by decide +kernel

end Models.Chen_MSB2009
