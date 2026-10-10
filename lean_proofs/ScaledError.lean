import Mathlib.Analysis.InnerProductSpace.Basic
import Mathlib.Analysis.SpecialFunctions.Sqrt

/-!
# cos Δ = error mínimo tras reajustar el tamaño de la respuesta

Sean `a = Δx_full` y `b = Δx_sel ≠ 0`. Si al modelo reducido se le permite reescalar su
respuesta por un factor `α`, el error relativo mínimo es exactamente `√(1 − cos²Δ)`:

* `scaled_error_ge`: para todo `α`, `‖a − α b‖² ≥ ‖a‖² − ⟪a, b⟫² / ‖b‖²`;
* `scaled_error_eq`: la igualdad se alcanza en `α* = ⟪a, b⟫ / ‖b‖²`;
* `scaled_error_cos`: `‖a‖² − ⟪a, b⟫²/‖b‖² = ‖a‖² (1 − cos²Δ)`.

Así `cos Δ ≥ c ⇔ min_α ‖a − α b‖ / ‖a‖ ≤ √(1 − c²)` (p. ej. `c = 0,90 ⇔ error ≤ 0,436`):
cos Δ mide si la respuesta del subconjunto **puede** reproducir la del modelo completo
reajustando su tamaño; `e_rel = ‖a − b‖/‖a‖` (sin reajuste, `α = 1`) es siempre mayor o igual.
-/

open RealInnerProductSpace

namespace ScaledError

variable {W : Type*} [NormedAddCommGroup W] [InnerProductSpace ℝ W]

lemma norm_sub_smul_sq (a b : W) (α : ℝ) :
    ‖a - α • b‖ ^ 2 = ‖a‖ ^ 2 - 2 * α * ⟪a, b⟫ + α ^ 2 * ‖b‖ ^ 2 := by
  rw [@norm_sub_sq_real, inner_smul_right, norm_smul, Real.norm_eq_abs, mul_pow, sq_abs]
  ring

/-- **Cota inferior del error con reescalado.** -/
theorem scaled_error_ge (a b : W) (hb : b ≠ 0) (α : ℝ) :
    ‖a‖ ^ 2 - ⟪a, b⟫ ^ 2 / ‖b‖ ^ 2 ≤ ‖a - α • b‖ ^ 2 := by
  have hb2 : 0 < ‖b‖ ^ 2 := by have := norm_pos_iff.2 hb; positivity
  rw [norm_sub_smul_sq]
  have key : 0 ≤ (α * ‖b‖ ^ 2 - ⟪a, b⟫) ^ 2 / ‖b‖ ^ 2 := by positivity
  have e : (α * ‖b‖ ^ 2 - ⟪a, b⟫) ^ 2 / ‖b‖ ^ 2
      = α ^ 2 * ‖b‖ ^ 2 - 2 * α * ⟪a, b⟫ + ⟪a, b⟫ ^ 2 / ‖b‖ ^ 2 := by
    field_simp; ring
  linarith

/-- **El mínimo se alcanza** en `α* = ⟪a, b⟫ / ‖b‖²`. -/
theorem scaled_error_eq (a b : W) (hb : b ≠ 0) :
    ‖a - (⟪a, b⟫ / ‖b‖ ^ 2) • b‖ ^ 2 = ‖a‖ ^ 2 - ⟪a, b⟫ ^ 2 / ‖b‖ ^ 2 := by
  have hb2 : ‖b‖ ^ 2 ≠ 0 := by have := norm_pos_iff.2 hb; positivity
  rw [norm_sub_smul_sq]
  field_simp; ring

/-- **Forma con cos Δ**: el error mínimo es `‖a‖²(1 − cos²Δ)`. -/
theorem scaled_error_cos (a b : W) (ha : a ≠ 0) (hb : b ≠ 0) :
    ‖a‖ ^ 2 - ⟪a, b⟫ ^ 2 / ‖b‖ ^ 2
      = ‖a‖ ^ 2 * (1 - (⟪a, b⟫ / (‖a‖ * ‖b‖)) ^ 2) := by
  have ha' : ‖a‖ ≠ 0 := norm_ne_zero_iff.2 ha
  have hb' : ‖b‖ ≠ 0 := norm_ne_zero_iff.2 hb
  field_simp

/-- **Error relativo mínimo tras reescalar = √(1 − cos²Δ).** -/
theorem min_rel_error_eq (a b : W) (ha : a ≠ 0) (hb : b ≠ 0) :
    (∀ α : ℝ, Real.sqrt (1 - (⟪a, b⟫ / (‖a‖ * ‖b‖)) ^ 2) ≤ ‖a - α • b‖ / ‖a‖) ∧
    ‖a - (⟪a, b⟫ / ‖b‖ ^ 2) • b‖ / ‖a‖ = Real.sqrt (1 - (⟪a, b⟫ / (‖a‖ * ‖b‖)) ^ 2) := by
  have hna : 0 < ‖a‖ := norm_pos_iff.2 ha
  have hc : ∀ α : ℝ, ‖a - α • b‖ ^ 2 / ‖a‖ ^ 2 ≥ 1 - (⟪a, b⟫ / (‖a‖ * ‖b‖)) ^ 2 := by
    intro α
    have h1 := scaled_error_ge a b hb α
    rw [scaled_error_cos a b ha hb] at h1
    rw [ge_iff_le, le_div_iff₀ (by positivity)]; linarith
  have heq : ‖a - (⟪a, b⟫ / ‖b‖ ^ 2) • b‖ ^ 2 / ‖a‖ ^ 2
      = 1 - (⟪a, b⟫ / (‖a‖ * ‖b‖)) ^ 2 := by
    rw [scaled_error_eq a b hb, scaled_error_cos a b ha hb]; field_simp
  refine ⟨fun α => ?_, ?_⟩
  · have h2 : 1 - (⟪a, b⟫ / (‖a‖ * ‖b‖)) ^ 2 ≤ (‖a - α • b‖ / ‖a‖) ^ 2 := by
      rw [div_pow ‖a - α • b‖]; exact hc α
    calc Real.sqrt (1 - (⟪a, b⟫ / (‖a‖ * ‖b‖)) ^ 2)
        ≤ Real.sqrt ((‖a - α • b‖ / ‖a‖) ^ 2) := Real.sqrt_le_sqrt h2
      _ = ‖a - α • b‖ / ‖a‖ := Real.sqrt_sq (div_nonneg (norm_nonneg _) hna.le)
  · have h3 : (‖a - (⟪a, b⟫ / ‖b‖ ^ 2) • b‖ / ‖a‖) ^ 2 = 1 - (⟪a, b⟫ / (‖a‖ * ‖b‖)) ^ 2 := by
      rw [div_pow ‖a - (⟪a, b⟫ / ‖b‖ ^ 2) • b‖]; exact heq
    rw [← h3, Real.sqrt_sq (div_nonneg (norm_nonneg _) hna.le)]

end ScaledError

#print axioms ScaledError.min_rel_error_eq
