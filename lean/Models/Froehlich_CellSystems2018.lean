import Models.Froehlich_CellSystems2018.Part0
import Models.Froehlich_CellSystems2018.Part1
import Models.Froehlich_CellSystems2018.Part2
import Models.Froehlich_CellSystems2018.Part3
import Models.Froehlich_CellSystems2018.Part4
import Models.Froehlich_CellSystems2018.Part5
import Models.Froehlich_CellSystems2018.Part6
import Models.Froehlich_CellSystems2018.Part7
import Models.Froehlich_CellSystems2018.Part8
import Models.Froehlich_CellSystems2018.Part9
import Models.Froehlich_CellSystems2018.Part10
import Models.Froehlich_CellSystems2018.Part11

/-! Modelo `Froehlich_CellSystems2018` (forma de red, 4487 términos en 12 módulos).
Estados: 1228; parámetros estimados θ: 4088. Generado por `certificados/sbml_to_lean.py`. -/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

open KineticRegularity KineticCheck KineticNetwork

namespace Models.Froehlich_CellSystems2018

def Rx : List (KExpr 1228 4088 × List (Fin 1228 × ℚ)) := Rx_0 ++ Rx_1 ++ Rx_2 ++ Rx_3 ++ Rx_4 ++ Rx_5 ++ Rx_6 ++ Rx_7 ++ Rx_8 ++ Rx_9 ++ Rx_10 ++ Rx_11

def F : Fin 1228 → KExpr 1228 4088 := netF Rx

theorem net_ok : checkNet pos Rx = true := by
  simp only [Rx, checkNet_append, net_ok_0, net_ok_1, net_ok_2, net_ok_3, net_ok_4, net_ok_5, net_ok_6, net_ok_7, net_ok_8, net_ok_9, net_ok_10, net_ok_11, Bool.and_self]

theorem growth_ok : checkGrowth pos c Rx = true := by
  simp only [Rx, checkGrowth_append, growth_ok_0, growth_ok_1, growth_ok_2, growth_ok_3, growth_ok_4, growth_ok_5, growth_ok_6, growth_ok_7, growth_ok_8, growth_ok_9, growth_ok_10, growth_ok_11, Bool.and_self]

/-- θ₀ > 0: se comprueba la lista una vez (tiempo lineal) en vez de acceder a cada
componente por índice (tiempo cuadrático). -/
theorem theta_ok : checkPosParams pos θq = true := by
  have hL : θqL.all (fun q => decide (0 < q)) = true := by decide +kernel
  rw [List.all_eq_true] at hL
  simp only [checkPosParams, List.all_eq_true, List.mem_finRange, true_implies,
    Bool.or_eq_true, decide_eq_true_eq]
  intro j
  right
  simp only [θq]
  rw [List.getD_eq_getElem?_getD]
  cases h : θqL[j.val]? with
  | none => simp
  | some x => simpa using hL x (List.mem_of_getElem? h)

theorem x0_ok : checkNonneg xq = true := by decide +kernel

/-- **Teorema final, sin condiciones pendientes.** -/
def final := @network_final _ _ pos Rx net_ok c growth_ok θq theta_ok xq x0_ok

end Models.Froehlich_CellSystems2018

#print axioms Models.Froehlich_CellSystems2018.final
