import CosineCertificate
import GreedySelection

/-!
# Robustez numérica: del cálculo aproximado a las hipótesis exactas

El pipeline calcula `J̃` por diferencias finitas y evalúa `R_var`, `κ` y `VIF` numéricamente.
Los teoremas certificados hablan de la sensibilidad exacta `J`. Este archivo demuestra que,
si se conoce una cota del error numérico, las comprobaciones sobre `J̃` **con un margen**
implican las hipótesis exactas.

* `fd_column_error`: error de diferencias finitas `‖(F(θ₀+δ eⱼ) − F(θ₀))/δ − J eⱼ‖ ≤ Lc δ`.
* `rvar_certified_from_approx`: cotas por columna `‖J_j − J̃_j‖ ≤ τ_j` y la comprobación
  `r (K_low + R_up) ≤ K_low` sobre `J̃` implican `R_var(J) ≥ r`.
* `kappa_certified_from_approx` / `vif_certified_from_approx`: si `‖Z − Z̃‖ ≤ τ` y `Z̃` pasa el
  filtro con margen, `Z` cumple `κ ≤ κ₀` y `VIF ≤ V₀`.
* `opNorm_le_frobenius`: `‖D u‖ ≤ √(∑ⱼ ‖D eⱼ‖²) ‖u‖`, para obtener `τ` de los errores por columna.
-/

open scoped BigOperators
open Set Metric FirstOrderErrorBound TrajectoryErrorBound CosineCertificate GreedySelection

namespace NumericalRobustness

variable {m p : ℕ}

/-! ## Diferencias finitas -/

/-- **Error de diferencias finitas** con paso `δ` en la dirección `v` (`‖v‖ = 1`):
`‖(F(θ₀ + δ v) − F(θ₀))/δ − DF(θ₀) v‖ ≤ Lc δ`. -/
theorem fd_column_error
    (F : EuclideanSpace ℝ (Fin p) → EuclideanSpace ℝ (Fin m))
    (DF : EuclideanSpace ℝ (Fin p) → (EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin m)))
    (θ₀ : EuclideanSpace ℝ (Fin p)) {ρ₀ Lc δ : ℝ} (hLc : 0 ≤ Lc) (hδ : 0 < δ) (hδρ : δ ≤ ρ₀)
    (hDF : ∀ θ ∈ closedBall θ₀ ρ₀, HasFDerivAt F (DF θ) θ)
    (hLip : ∀ θ ∈ closedBall θ₀ ρ₀, ‖DF θ - DF θ₀‖ ≤ Lc * ‖θ - θ₀‖)
    (v : EuclideanSpace ℝ (Fin p)) (hv : ‖v‖ = 1) :
    ‖δ⁻¹ • (F (θ₀ + δ • v) - F θ₀) - DF θ₀ v‖ ≤ Lc * δ := by
  have hn : ‖δ • v‖ = δ := by rw [norm_smul, hv, mul_one, Real.norm_of_nonneg hδ.le]
  have t := taylor_bound F DF θ₀ hLc hDF hLip (δ • v) (by rw [hn]; exact hδρ)
  rw [hn] at t
  have e : δ⁻¹ • (F (θ₀ + δ • v) - F θ₀) - DF θ₀ v
      = δ⁻¹ • (F (θ₀ + δ • v) - F θ₀ - DF θ₀ (δ • v)) := by
    simp only [map_smul, smul_sub, smul_smul, inv_mul_cancel₀ hδ.ne', one_smul]
  rw [e, norm_smul, Real.norm_of_nonneg (inv_nonneg.2 hδ.le)]
  calc δ⁻¹ * ‖F (θ₀ + δ • v) - F θ₀ - DF θ₀ (δ • v)‖ ≤ δ⁻¹ * (Lc * δ ^ 2) :=
        mul_le_mul_of_nonneg_left t (inv_nonneg.2 hδ.le)
    _ = Lc * δ := by field_simp

/-! ## R_var certificado a partir de columnas aproximadas -/

/-- Columna `j` de `J` como vector euclídeo. -/
noncomputable def col (J : Fin m → Fin p → ℝ) (j : Fin p) : EuclideanSpace ℝ (Fin m) :=
  WithLp.toLp 2 (fun i => J i j)

lemma columnEnergy_eq_norm_sq (J : Fin m → Fin p → ℝ) (j : Fin p) :
    columnEnergy J j = ‖col J j‖ ^ 2 := by
  rw [EuclideanSpace.norm_sq_eq]
  simp [columnEnergy, col, Real.norm_eq_abs, sq_abs]

/-- **R_var certificado.** Sean `J̃` las columnas calculadas con `‖J_j − J̃_j‖ ≤ τ_j`.
Definimos `K_low = ∑_{j∈S} (max(‖J̃_j‖ − τ_j, 0))²` y `R_up = ∑_{j∉S} (‖J̃_j‖ + τ_j)²`.
Si `0 ≤ r ≤ 1` y `r (K_low + R_up) ≤ K_low`, entonces la sensibilidad exacta cumple
`r · tr(JᵀJ) ≤ energía conservada`, que es la hipótesis del teorema certificado. -/
theorem rvar_certified_from_approx (J Jt : Fin m → Fin p → ℝ) (τ : Fin p → ℝ)
    (S : Finset (Fin p)) (hτ : ∀ j, ‖col J j - col Jt j‖ ≤ τ j)
    {r : ℝ} (hr0 : 0 ≤ r) (hr1 : r ≤ 1)
    (hcheck : r * ((∑ j ∈ S, (max (‖col Jt j‖ - τ j) 0) ^ 2)
        + ∑ j ∈ removedSet S, (‖col Jt j‖ + τ j) ^ 2)
      ≤ ∑ j ∈ S, (max (‖col Jt j‖ - τ j) 0) ^ 2) :
    r * totalColumnEnergy J ≤ keptColumnEnergy J S := by
  have hτ0 : ∀ j, 0 ≤ τ j := fun j => (norm_nonneg _).trans (hτ j)
  have hlow : ∑ j ∈ S, (max (‖col Jt j‖ - τ j) 0) ^ 2 ≤ keptColumnEnergy J S := by
    apply Finset.sum_le_sum
    intro j _
    rw [columnEnergy_eq_norm_sq]
    apply pow_le_pow_left₀ (le_max_right _ _)
    apply max_le _ (norm_nonneg _)
    have := norm_le_insert' (col Jt j) (col J j)
    rw [norm_sub_rev] at this
    linarith [hτ j]
  have hup : removedColumnEnergy J S ≤ ∑ j ∈ removedSet S, (‖col Jt j‖ + τ j) ^ 2 := by
    apply Finset.sum_le_sum
    intro j _
    rw [columnEnergy_eq_norm_sq]
    apply pow_le_pow_left₀ (norm_nonneg _)
    have := norm_le_insert' (col J j) (col Jt j)
    linarith [hτ j]
  have htot := total_eq_kept_add_removed J S
  rw [htot]
  nlinarith [mul_le_mul_of_nonneg_left hup hr0,
    mul_le_mul_of_nonneg_left hlow (by linarith : (0 : ℝ) ≤ 1 - r)]

/-! ## κ y VIF certificados a partir de una matriz aproximada -/

section Filters

variable {W : Type*} [NormedAddCommGroup W] [InnerProductSpace ℝ W]

/-- **Norma de operador acotada por la norma de Frobenius (por columnas).** -/
theorem opNorm_le_frobenius (D : EuclideanSpace ℝ (Fin p) →L[ℝ] W) (u : EuclideanSpace ℝ (Fin p)) :
    ‖D u‖ ≤ Real.sqrt (∑ j, ‖D (EuclideanSpace.single j 1)‖ ^ 2) * ‖u‖ := by
  have hu : u = ∑ j, u j • EuclideanSpace.single j (1 : ℝ) := by
    conv_lhs => rw [← (EuclideanSpace.basisFun (Fin p) ℝ).sum_repr u]
    simp
  have hDu : D u = ∑ j, u j • D (EuclideanSpace.single j 1) := by
    conv_lhs => rw [hu]
    rw [map_sum]; simp only [map_smul]
  have h1 : ‖D u‖ ≤ ∑ j, |u j| * ‖D (EuclideanSpace.single j 1)‖ := by
    rw [hDu]
    refine (norm_sum_le _ _).trans (le_of_eq ?_)
    apply Finset.sum_congr rfl
    intro j _
    rw [norm_smul, Real.norm_eq_abs]
  have h2 : (∑ j, |u j| * ‖D (EuclideanSpace.single j 1)‖) ^ 2
      ≤ (∑ j, |u j| ^ 2) * ∑ j, ‖D (EuclideanSpace.single j 1)‖ ^ 2 :=
    Finset.sum_mul_sq_le_sq_mul_sq _ _ _
  have hn : ‖u‖ = Real.sqrt (∑ j, |u j| ^ 2) := by
    rw [EuclideanSpace.norm_eq]; simp [Real.norm_eq_abs]
  rw [hn, ← Real.sqrt_mul' _ (Finset.sum_nonneg fun j _ => sq_nonneg _), mul_comm
    (∑ j, ‖D (EuclideanSpace.single j 1)‖ ^ 2)]
  refine h1.trans ?_
  apply Real.le_sqrt_of_sq_le
  exact h2

/-- **κ certificado.** Si `‖(Z − Z̃) u‖ ≤ τ ‖u‖` para todo `u`, `Z̃` cumple
`σ̃min ‖u‖ ≤ ‖Z̃ u‖ ≤ σ̃max ‖u‖` en los vectores soportados en `S`, `τ < σ̃min` y
`σ̃max + τ ≤ κ₀ (σ̃min − τ)`, entonces `Z` pasa el filtro `κ ≤ κ₀` en `S`. -/
theorem kappa_certified_from_approx (Z Zt : EuclideanSpace ℝ (Fin p) →L[ℝ] W) {τ : ℝ}
    (hτ : ∀ u, ‖(Z - Zt) u‖ ≤ τ * ‖u‖) (S : Finset (Fin p)) {σmin σmax κ₀ : ℝ}
    (hb : ∀ u, SupportedOn S u → σmin * ‖u‖ ≤ ‖Zt u‖ ∧ ‖Zt u‖ ≤ σmax * ‖u‖)
    (hgap : τ < σmin) (hmargin : σmax + τ ≤ κ₀ * (σmin - τ)) :
    okKappa Z κ₀ S := by
  refine ⟨σmin - τ, σmax + τ, by linarith, hmargin, fun u hu => ⟨?_, ?_⟩⟩
  · have h1 := (hb u hu).1
    have h2 := norm_sub_norm_le (Zt u) (Zt u - Z u)
    rw [sub_sub_cancel] at h2
    have h3 : ‖Zt u - Z u‖ ≤ τ * ‖u‖ := by
      rw [← norm_neg, neg_sub, ← ContinuousLinearMap.sub_apply]; exact hτ u
    nlinarith
  · have h1 := (hb u hu).2
    have h2 := norm_le_insert' (Z u) (Zt u)
    have h3 : ‖Z u - Zt u‖ ≤ τ * ‖u‖ := by rw [← ContinuousLinearMap.sub_apply]; exact hτ u
    nlinarith

/-- **VIF certificado.** Con las mismas hipótesis sobre `Z̃` (cota inferior `σ̃min`) y
`‖(Z − Z̃) u‖ ≤ τ ‖u‖`, si `Z̃` pasa el filtro `VIF ≤ Ṽ` en `S` y `τ < σ̃min`, entonces `Z`
pasa el filtro `VIF ≤ Ṽ / (1 − τ/σ̃min)²`. -/
theorem vif_certified_from_approx (Z Zt : EuclideanSpace ℝ (Fin p) →L[ℝ] W) {τ : ℝ}
    (hτ0 : 0 ≤ τ) (hτ : ∀ u, ‖(Z - Zt) u‖ ≤ τ * ‖u‖) (S : Finset (Fin p)) {σmin Vt : ℝ}
    (hlow : ∀ u, SupportedOn S u → σmin * ‖u‖ ≤ ‖Zt u‖) (hgap : τ < σmin)
    (hvif : okVIF Zt Vt S) :
    okVIF Z (Vt / (1 - τ / σmin) ^ 2) S := by
  intro j hj u hu huj
  have hσ : 0 < σmin := lt_of_le_of_lt hτ0 hgap
  have hq : 0 < 1 - τ / σmin := by rw [sub_pos, div_lt_one hσ]; exact hgap
  have h1 := hvif j hj u hu huj
  have hun : ‖u‖ ≤ ‖Zt u‖ / σmin := by rw [le_div_iff₀ hσ, mul_comm]; exact hlow u hu
  have h3 : ‖Zt u - Z u‖ ≤ τ * ‖u‖ := by
    rw [← norm_neg, neg_sub, ← ContinuousLinearMap.sub_apply]; exact hτ u
  have h2 := norm_sub_norm_le (Zt u) (Zt u - Z u)
  rw [sub_sub_cancel] at h2
  have hZ : (1 - τ / σmin) * ‖Zt u‖ ≤ ‖Z u‖ := by
    have : τ * ‖u‖ ≤ τ / σmin * ‖Zt u‖ := by
      calc τ * ‖u‖ ≤ τ * (‖Zt u‖ / σmin) := mul_le_mul_of_nonneg_left hun hτ0
        _ = τ / σmin * ‖Zt u‖ := by ring
    nlinarith
  have hZ2 : (1 - τ / σmin) ^ 2 * ‖Zt u‖ ^ 2 ≤ ‖Z u‖ ^ 2 := by
    rw [← mul_pow]; exact pow_le_pow_left₀ (by positivity) hZ 2
  rw [one_div, inv_div]
  calc (1 - τ / σmin) ^ 2 / Vt = (1 - τ / σmin) ^ 2 * (1 / Vt) := by ring
    _ ≤ (1 - τ / σmin) ^ 2 * ‖Zt u‖ ^ 2 := mul_le_mul_of_nonneg_left h1 (by positivity)
    _ ≤ ‖Z u‖ ^ 2 := hZ2

end Filters

end NumericalRobustness

