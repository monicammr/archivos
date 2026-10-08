import Models.Chen_MSB2009.Part0
import Models.Chen_MSB2009.Part1
import Models.Chen_MSB2009.Part2
import Models.Chen_MSB2009.Part3

/-! Modelo `Chen_MSB2009` (forma de red, 1243 términos en 4 módulos).
Estados: 501; parámetros estimados θ: 152. Generado por `certificados/sbml_to_lean.py`. -/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck KineticNetwork

namespace Models.Chen_MSB2009

def Rx : List (KExpr 501 152 × List (Fin 501 × ℚ)) := Rx_0 ++ Rx_1 ++ Rx_2 ++ Rx_3

def F : Fin 501 → KExpr 501 152 := netF Rx

theorem net_ok : checkNet pos Rx = true := by
  simp only [Rx, checkNet_append, net_ok_0, net_ok_1, net_ok_2, net_ok_3, Bool.and_self]

theorem growth_ok : checkGrowth pos c Rx = true := by
  simp only [Rx, checkGrowth_append, growth_ok_0, growth_ok_1, growth_ok_2, growth_ok_3, Bool.and_self]

theorem theta_ok : checkPosParams pos θq = true := by decide +kernel

theorem x0_ok : checkNonneg xq = true := by decide +kernel

/-- **Teorema final, sin condiciones pendientes.** -/
def final := @network_final _ _ pos Rx net_ok c growth_ok θq theta_ok xq x0_ok

end Models.Chen_MSB2009

#print axioms Models.Chen_MSB2009.final
