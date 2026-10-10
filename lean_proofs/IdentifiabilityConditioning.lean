import Mathlib.Analysis.InnerProductSpace.PiL2

/-!
# κ y VIF ⇒ estimación por mínimos cuadrados única y estable

Respalda la sección 2.2 del artículo: el criterio `κ ≤ 10`, `VIF ≤ 10` sobre las columnas
L2-normalizadas `Z = J_S D⁻¹` (con `D = diag(‖J_j‖)`) garantiza que el ajuste por mínimos
cuadrados de los parámetros conservados está bien condicionado.

Notación: `σmin`, `σmax` son las cotas `σmin ‖u‖ ≤ ‖Z u‖ ≤ σmax ‖u‖` (los valores singulares
extremos de `Z`), y `κ` cumple `σmax ≤ κ σmin`.

Resultados:
* `IsLSMin.inner_residual_eq_zero`: ecuaciones normales (el residuo es ortogonal a `im Z`).
* `ls_response_stability`: `‖Z (v − v')‖ ≤ ‖y − y'‖` para dos minimizadores.
* `ls_kappa_stability`: con columnas unitarias y `κ(Z) ≤ κ`,
  `‖v − v'‖ ≤ κ ‖y − y'‖` (unicidad y estabilidad).
* `ls_param_kappa_stability`: lo mismo en los parámetros originales:
  `‖D (θ̂ − θ̂')‖ ≤ κ ‖y − y'‖`.
* `ls_vif_coordinate_stability`: si la columna `j` no se aproxima por las demás mejor que
  `1/√V` (es decir `VIF_j ≤ V`), entonces `|v_j − v'_j| ≤ √V ‖y − y'‖`.
-/

open scoped RealInnerProductSpace

namespace Identifiability

section General

variable {V W : Type*} [NormedAddCommGroup V] [InnerProductSpace ℝ V]
  [NormedAddCommGroup W] [InnerProductSpace ℝ W]

/-- `v` es un minimizador de mínimos cuadrados de `‖Z v − y‖`. -/
def IsLSMin (Z : V →L[ℝ] W) (y : W) (v : V) : Prop := ∀ w, ‖Z v - y‖ ≤ ‖Z w - y‖

/-- **Ecuaciones normales**: en un minimizador el residuo es ortogonal a la imagen de `Z`. -/
theorem IsLSMin.inner_residual_eq_zero {Z : V →L[ℝ] W} {y : W} {v : V}
    (hv : IsLSMin Z y v) (w : V) : inner ℝ (Z v - y) (Z w) = 0 := by
  obtain ⟨a, ha⟩ : ∃ a, a = inner ℝ (Z v - y) (Z w) := ⟨_, rfl⟩
  obtain ⟨b, hb⟩ : ∃ b, b = ‖Z w‖ ^ 2 := ⟨_, rfl⟩
  have hb0 : 0 ≤ b := hb ▸ sq_nonneg _
  have key : ∀ t : ℝ, 0 ≤ 2 * t * a + t ^ 2 * b := by
    intro t
    have h2 : ‖Z v - y‖ ^ 2 ≤ ‖Z (v + t • w) - y‖ ^ 2 :=
      pow_le_pow_left₀ (norm_nonneg _) (hv (v + t • w)) 2
    have e : Z (v + t • w) - y = (Z v - y) + t • Z w := by
      rw [map_add, map_smul]; abel
    rw [e, norm_add_sq_real, real_inner_smul_right, norm_smul, mul_pow, Real.norm_eq_abs,
      sq_abs] at h2
    rw [ha, hb]; nlinarith
  obtain ⟨u, hu⟩ : ∃ u, u = a / (b + 1) := ⟨_, rfl⟩
  have hau : a = u * (b + 1) := by rw [hu]; field_simp
  have h1 := key (-u)
  rw [hau] at h1
  have hu2 : u ^ 2 * (b + 2) ≤ 0 := by nlinarith
  have hu0 : u = 0 := by
    have : u ^ 2 ≤ 0 := by
      by_contra hc; push_neg at hc; nlinarith
    exact pow_eq_zero_iff (n := 2) (by norm_num) |>.1 (le_antisymm this (sq_nonneg u))
  rw [← ha, hau, hu0, zero_mul]

/-- **Estabilidad de la respuesta ajustada**: `‖Z v − Z v'‖ ≤ ‖y − y'‖`. -/
theorem ls_response_stability {Z : V →L[ℝ] W} {y y' : W} {v v' : V}
    (hv : IsLSMin Z y v) (hv' : IsLSMin Z y' v') : ‖Z (v - v')‖ ≤ ‖y - y'‖ := by
  have h1 := hv.inner_residual_eq_zero (v - v')
  have h2 := hv'.inner_residual_eq_zero (v - v')
  have e : (Z v - y) - (Z v' - y') = Z (v - v') - (y - y') := by rw [map_sub]; abel
  have h3 : inner ℝ (Z (v - v') - (y - y')) (Z (v - v')) = 0 := by
    rw [← e, inner_sub_left, h1, h2, sub_zero]
  rw [inner_sub_left, real_inner_self_eq_norm_sq, sub_eq_zero] at h3
  have h4 : ‖Z (v - v')‖ ^ 2 ≤ ‖y - y'‖ * ‖Z (v - v')‖ := h3 ▸ real_inner_le_norm _ _
  nlinarith [norm_nonneg (Z (v - v')), norm_nonneg (y - y')]

/-- **Unicidad y estabilidad con cota inferior** `σmin ‖u‖ ≤ ‖Z u‖`. -/
theorem ls_param_stability {Z : V →L[ℝ] W} {σmin : ℝ} (hσ : 0 < σmin)
    (hlow : ∀ u, σmin * ‖u‖ ≤ ‖Z u‖) {y y' : W} {v v' : V}
    (hv : IsLSMin Z y v) (hv' : IsLSMin Z y' v') : ‖v - v'‖ ≤ ‖y - y'‖ / σmin := by
  rw [le_div_iff₀ hσ, mul_comm]
  exact (hlow _).trans (ls_response_stability hv hv')

/-- Unicidad del estimador: con los mismos datos, el minimizador es único. -/
theorem ls_unique {Z : V →L[ℝ] W} {σmin : ℝ} (hσ : 0 < σmin)
    (hlow : ∀ u, σmin * ‖u‖ ≤ ‖Z u‖) {y : W} {v v' : V}
    (hv : IsLSMin Z y v) (hv' : IsLSMin Z y v') : v = v' := by
  have := ls_param_stability hσ hlow hv hv'
  rw [sub_self, norm_zero, zero_div] at this
  exact sub_eq_zero.1 (norm_le_zero_iff.1 this)

end General

section Columns

variable {k : ℕ} {W : Type*} [NormedAddCommGroup W] [InnerProductSpace ℝ W]

/-- Con columnas de norma 1 (`‖Z e_j‖ = 1`), `σmax ≥ 1`; por tanto `κ σmin ≥ 1`. -/
theorem one_le_kappa_mul_sigmaMin (Z : EuclideanSpace ℝ (Fin k) →L[ℝ] W)
    (hunit : ∀ j, ‖Z (EuclideanSpace.single j 1)‖ = 1) (j₀ : Fin k)
    {σmin σmax κ : ℝ} (hup : ∀ u, ‖Z u‖ ≤ σmax * ‖u‖) (hκ : σmax ≤ κ * σmin) :
    1 ≤ κ * σmin := by
  have := hup (EuclideanSpace.single j₀ 1)
  rw [hunit, EuclideanSpace.norm_single, norm_one, mul_one] at this
  linarith

/-- **κ ⇒ estimación estable.** Columnas L2-normalizadas, `σmin ‖u‖ ≤ ‖Z u‖ ≤ σmax ‖u‖` y
`σmax ≤ κ σmin` (es decir `κ(Z) ≤ κ`). Entonces dos ajustes por mínimos cuadrados con datos
`y`, `y'` cumplen `‖v − v'‖ ≤ κ ‖y − y'‖`. Con `κ ≤ 10`: el error en los parámetros
escalados es a lo sumo 10 veces la perturbación de los datos. -/
theorem ls_kappa_stability (Z : EuclideanSpace ℝ (Fin k) →L[ℝ] W)
    (hunit : ∀ j, ‖Z (EuclideanSpace.single j 1)‖ = 1) (j₀ : Fin k)
    {σmin σmax κ : ℝ} (hσ : 0 < σmin)
    (hlow : ∀ u, σmin * ‖u‖ ≤ ‖Z u‖) (hup : ∀ u, ‖Z u‖ ≤ σmax * ‖u‖) (hκ : σmax ≤ κ * σmin)
    {y y' : W} {v v' : EuclideanSpace ℝ (Fin k)}
    (hv : IsLSMin Z y v) (hv' : IsLSMin Z y' v') : ‖v - v'‖ ≤ κ * ‖y - y'‖ := by
  have h1 := ls_param_stability hσ hlow hv hv'
  have h2 := one_le_kappa_mul_sigmaMin Z hunit j₀ hup hκ
  have h3 : 1 / σmin ≤ κ := by rw [div_le_iff₀ hσ]; linarith
  calc ‖v - v'‖ ≤ ‖y - y'‖ / σmin := h1
    _ = (1 / σmin) * ‖y - y'‖ := by ring
    _ ≤ κ * ‖y - y'‖ := mul_le_mul_of_nonneg_right h3 (norm_nonneg _)

/-- **Versión en los parámetros originales.** Si `J_S = Z ∘ D` con `D` invertible
(`D = diag(‖J_j‖)`), y `θ̂`, `θ̂'` minimizan `‖J_S θ − y‖`, `‖J_S θ − y'‖`, entonces
`‖D (θ̂ − θ̂')‖ ≤ κ ‖y − y'‖`. -/
theorem ls_param_kappa_stability (Z : EuclideanSpace ℝ (Fin k) →L[ℝ] W)
    (D : EuclideanSpace ℝ (Fin k) ≃L[ℝ] EuclideanSpace ℝ (Fin k))
    (hunit : ∀ j, ‖Z (EuclideanSpace.single j 1)‖ = 1) (j₀ : Fin k)
    {σmin σmax κ : ℝ} (hσ : 0 < σmin)
    (hlow : ∀ u, σmin * ‖u‖ ≤ ‖Z u‖) (hup : ∀ u, ‖Z u‖ ≤ σmax * ‖u‖) (hκ : σmax ≤ κ * σmin)
    {y y' : W} {θ θ' : EuclideanSpace ℝ (Fin k)}
    (hθ : IsLSMin (Z.comp (D : EuclideanSpace ℝ (Fin k) →L[ℝ] EuclideanSpace ℝ (Fin k))) y θ)
    (hθ' : IsLSMin (Z.comp (D : EuclideanSpace ℝ (Fin k) →L[ℝ] EuclideanSpace ℝ (Fin k))) y' θ') :
    ‖D (θ - θ')‖ ≤ κ * ‖y - y'‖ := by
  have transfer : ∀ {y : W} {θ}, IsLSMin (Z.comp (D : EuclideanSpace ℝ (Fin k) →L[ℝ]
      EuclideanSpace ℝ (Fin k))) y θ → IsLSMin Z y (D θ) := by
    intro y θ h w
    have := h (D.symm w)
    simpa using this
  rw [map_sub]
  exact ls_kappa_stability Z hunit j₀ hσ hlow hup hκ (transfer hθ) (transfer hθ')

/-- **VIF ⇒ estabilidad por parámetro.** Si toda combinación `u` con `u_j = 1` cumple
`‖Z u‖² ≥ 1/V` (la columna `j` dista al menos `1/√V` del espacio generado por las demás, i.e.
`VIF_j ≤ V`), entonces `|v_j − v'_j| ≤ √V ‖y − y'‖`. Con `VIF ≤ 10`: cada parámetro
escalado se mueve a lo sumo `√10 ≈ 3.16` veces la perturbación de los datos. -/
theorem ls_vif_coordinate_stability (Z : EuclideanSpace ℝ (Fin k) →L[ℝ] W) (j : Fin k)
    {Vb : ℝ} (hV : 0 < Vb)
    (hvif : ∀ u : EuclideanSpace ℝ (Fin k), u j = 1 → 1 / Vb ≤ ‖Z u‖ ^ 2)
    {y y' : W} {v v' : EuclideanSpace ℝ (Fin k)}
    (hv : IsLSMin Z y v) (hv' : IsLSMin Z y' v') :
    |v j - v' j| ≤ Real.sqrt Vb * ‖y - y'‖ := by
  have hresp := ls_response_stability hv hv'
  set d := v - v' with hd
  have hdj : d j = v j - v' j := by simp [hd]
  rw [← hdj]
  by_cases h0 : d j = 0
  · rw [h0, abs_zero]; positivity
  · set u := (d j)⁻¹ • d with hu
    have huj : u j = 1 := by simp [hu, h0]
    have hZu : Z d = d j • Z u := by
      rw [hu, map_smul, smul_smul, mul_inv_cancel₀ h0, one_smul]
    have hlow : 1 / Real.sqrt Vb ≤ ‖Z u‖ := by
      have h1 := hvif u huj
      have hs : (1 / Real.sqrt Vb) ^ 2 = 1 / Vb := by
        rw [div_pow, one_pow, Real.sq_sqrt hV.le]
      rw [← hs] at h1
      exact abs_le_of_sq_le_sq' h1 (norm_nonneg _) |>.2 |> fun h => by
        nlinarith [abs_nonneg (1 / Real.sqrt Vb), norm_nonneg (Z u)]
    have hsq : 0 < Real.sqrt Vb := Real.sqrt_pos.2 hV
    have : |d j| * (1 / Real.sqrt Vb) ≤ ‖y - y'‖ := by
      calc |d j| * (1 / Real.sqrt Vb) ≤ |d j| * ‖Z u‖ :=
            mul_le_mul_of_nonneg_left hlow (abs_nonneg _)
        _ = ‖Z d‖ := by rw [hZu, norm_smul, Real.norm_eq_abs]
        _ ≤ ‖y - y'‖ := hresp
    rw [mul_one_div, div_le_iff₀ hsq] at this
    linarith

/-- **Del VIF calculado a la hipótesis geométrica.** Sea `w` la columna `j` de `(ZᵀZ)⁻¹`,
caracterizada por `⟨Z w, Z u⟩ = u_j` para todo `u` (es decir `ZᵀZ w = e_j`). Entonces
`VIF_j = w_j = ((ZᵀZ)⁻¹)_{jj}`, y si `VIF_j ≤ V`, toda combinación con `u_j = 1` cumple
`‖Z u‖² ≥ 1/V`. -/
theorem vif_geometric_of_inverse (Z : EuclideanSpace ℝ (Fin k) →L[ℝ] W) (j : Fin k)
    (w : EuclideanSpace ℝ (Fin k)) (hw : ∀ u, inner ℝ (Z w) (Z u) = u j)
    {Vb : ℝ} (hV : 0 < Vb) (hvif : w j ≤ Vb) :
    ∀ u : EuclideanSpace ℝ (Fin k), u j = 1 → 1 / Vb ≤ ‖Z u‖ ^ 2 := by
  intro u hu
  have hwj : w j = ‖Z w‖ ^ 2 := by rw [← hw w, real_inner_self_eq_norm_sq]
  have h1 : 1 ≤ ‖Z w‖ * ‖Z u‖ := by
    rw [← hu, ← hw u]; exact real_inner_le_norm _ _
  have h2 : 1 ≤ ‖Z w‖ ^ 2 * ‖Z u‖ ^ 2 := by
    have := pow_le_pow_left₀ zero_le_one h1 2
    rw [one_pow, mul_pow] at this; exact this
  rw [div_le_iff₀ hV]
  rw [← hwj] at h2
  nlinarith [sq_nonneg ‖Z u‖]

/-- **VIF (fórmula de la matriz inversa) ⇒ estabilidad por parámetro.** Combinación de
`vif_geometric_of_inverse` y `ls_vif_coordinate_stability`: si `((ZᵀZ)⁻¹)_{jj} ≤ V`, entonces
`|v_j − v'_j| ≤ √V ‖y − y'‖`. -/
theorem ls_vif_inverse_stability (Z : EuclideanSpace ℝ (Fin k) →L[ℝ] W) (j : Fin k)
    (w : EuclideanSpace ℝ (Fin k)) (hw : ∀ u, inner ℝ (Z w) (Z u) = u j)
    {Vb : ℝ} (hV : 0 < Vb) (hvif : w j ≤ Vb)
    {y y' : W} {v v' : EuclideanSpace ℝ (Fin k)}
    (hv : IsLSMin Z y v) (hv' : IsLSMin Z y' v') :
    |v j - v' j| ≤ Real.sqrt Vb * ‖y - y'‖ :=
  ls_vif_coordinate_stability Z j hV (vif_geometric_of_inverse Z j w hw hV hvif) hv hv'

end Columns

end Identifiability

#print axioms Identifiability.ls_param_kappa_stability
#print axioms Identifiability.ls_vif_coordinate_stability
#print axioms Identifiability.ls_vif_inverse_stability
