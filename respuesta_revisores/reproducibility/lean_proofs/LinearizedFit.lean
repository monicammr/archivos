import ScaledError

/-!
# e_ajuste linealizado (sistemas grandes) y su relación con el e_ajuste real

En los sistemas grandes, e_ajuste se calculó a primer orden: con `d = Δy_full` y `A = J_S`
(columnas de la matriz de sensibilidad relativa del subconjunto `S`),

  `e_lin = min_c ‖d − A c‖ / ‖d‖`   (mínimos cuadrados).

* `lin_le_scaled`: si `v*` minimiza `‖d − v‖` sobre un subespacio `V` y `b ∈ V` (p. ej.
  `b = J_S h_S`, la respuesta lineal del subconjunto en el escenario), entonces
  `‖d − v*‖ ≤ ‖d‖ · √(1 − cos²(d, b))`: el e_ajuste linealizado nunca supera el error tras
  reescalar (ScaledError), y por tanto tampoco e_rel lineal.
* `fit_upper_of_lin` / `fit_lower_of_lin`: con resto de Taylor `‖F c − A c‖ ≤ M ‖c‖²`
  (`F c` = cambio real de las salidas al mover `θ_S` en `c`; cota de segundo orden como en
  `CosineCertificate.taylor_bound`), el error real en el óptimo lineal `c*` cumple
  `‖F c* − d‖ ≤ ‖A c* − d‖ + M ‖c*‖²`, y para cualquier `c` con `‖c‖ ≤ ρ`,
  `‖F c − d‖ ≥ e_lin‖d‖ − M ρ²`. Es decir, `|e_fit − e_lin| ≤ M ρ² / ‖d‖` en la bola de radio
  `ρ` que contiene los óptimos: la diferencia es de segundo orden en la perturbación.
-/

namespace LinearizedFit

open RealInnerProductSpace

variable {W : Type*} [NormedAddCommGroup W] [InnerProductSpace ℝ W]

/-- **El ajuste lineal no supera el error tras reescalar** (en un subespacio que contiene `b`). -/
theorem lin_le_scaled (V : Submodule ℝ W) (d b v : W) (hb : b ∈ V) (hd : d ≠ 0) (hb0 : b ≠ 0)
    (hv : ∀ w ∈ V, ‖d - v‖ ≤ ‖d - w‖) :
    ‖d - v‖ ≤ ‖d‖ * Real.sqrt (1 - (⟪d, b⟫ / (‖d‖ * ‖b‖)) ^ 2) := by
  have hmem : (⟪d, b⟫ / ‖b‖ ^ 2) • b ∈ V := V.smul_mem _ hb
  have h1 := hv _ hmem
  have h2 := (ScaledError.min_rel_error_eq d b hd hb0).2
  have hnd : 0 < ‖d‖ := norm_pos_iff.2 hd
  rw [div_eq_iff hnd.ne'] at h2
  calc ‖d - v‖ ≤ ‖d - (⟪d, b⟫ / ‖b‖ ^ 2) • b‖ := h1
    _ = _ := by rw [h2]; ring

variable {U : Type*} [NormedAddCommGroup U]

omit [InnerProductSpace ℝ W] in
/-- **Cota superior**: el error real en el óptimo lineal no excede `e_lin + M‖c‖²`. -/
theorem fit_upper_of_lin (F A : U → W) (d : W) (M : ℝ) (c : U)
    (hT : ‖F c - A c‖ ≤ M * ‖c‖ ^ 2) : ‖F c - d‖ ≤ ‖A c - d‖ + M * ‖c‖ ^ 2 := by
  calc ‖F c - d‖ = ‖(F c - A c) + (A c - d)‖ := by congr 1; abel
    _ ≤ ‖F c - A c‖ + ‖A c - d‖ := norm_add_le _ _
    _ ≤ ‖A c - d‖ + M * ‖c‖ ^ 2 := by linarith

omit [InnerProductSpace ℝ W] in
/-- **Cota inferior**: en la bola `‖c‖ ≤ ρ`, el error real es al menos `e_lin‖d‖ − Mρ²`,
donde `elin` es el mínimo del problema lineal (`elin ≤ ‖A c − d‖` para todo `c`). -/
theorem fit_lower_of_lin (F A : U → W) (d : W) (M ρ elin : ℝ) (hM : 0 ≤ M)
    (hT : ∀ c, ‖F c - A c‖ ≤ M * ‖c‖ ^ 2) (hmin : ∀ c, elin ≤ ‖A c - d‖)
    (c : U) (hc : ‖c‖ ≤ ρ) : elin - M * ρ ^ 2 ≤ ‖F c - d‖ := by
  have h1 : ‖A c - d‖ ≤ ‖F c - d‖ + ‖F c - A c‖ := by
    calc ‖A c - d‖ = ‖(F c - d) - (F c - A c)‖ := by congr 1; abel
      _ ≤ ‖F c - d‖ + ‖F c - A c‖ := norm_sub_le _ _
  have h2 : M * ‖c‖ ^ 2 ≤ M * ρ ^ 2 :=
    mul_le_mul_of_nonneg_left (pow_le_pow_left₀ (norm_nonneg _) hc 2) hM
  linarith [hmin c, hT c]

end LinearizedFit

#print axioms LinearizedFit.lin_le_scaled
#print axioms LinearizedFit.fit_lower_of_lin
