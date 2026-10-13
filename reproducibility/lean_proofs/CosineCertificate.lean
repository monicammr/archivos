import TrajectoryErrorBound
import Mathlib.Analysis.Calculus.MeanValue

/-!
# cos Δ y perturbaciones finitas: certificados no asintóticos

El artículo valida cada reducción con `cos Δ = ⟨Δx_full, Δx_sel⟩ / (‖Δx_full‖ ‖Δx_sel‖)`,
donde `Δx_full = F(θ₀+Δθ) − F(θ₀)` y `Δx_sel = F(θ₀+Δθ_S) − F(θ₀)`, para perturbaciones
finitas (±5 % … ±50 %). Aquí se demuestra:

* `cos_lower_of_rel_error`: si `‖a − b‖ ≤ ε ‖a‖` y `c² + ε² ≤ 1`, entonces
  `⟨a, b⟩ ≥ c ‖a‖ ‖b‖` (con `c = 0.9` basta `ε² ≤ 0.19`).
* `taylor_bound`: si la derivada `DF` es `Lc`-Lipschitz en la bola de radio `ρ₀`, entonces
  `‖F(θ₀+h) − F(θ₀) − DF(θ₀) h‖ ≤ Lc ‖h‖²` (cota explícita, no asintótica).
* `finite_trajectory_error`: **cota explícita para perturbaciones finitas**
  `‖F(θ₀+h) − F(θ₀+h_S)‖ ≤ √R(S) ‖h_{Sᶜ}‖ + 2 Lc ‖h‖²` para todo `‖h‖ ≤ ρ₀`.
* `finite_cos_certificate`: **certificado de cos Δ para una perturbación concreta `h`**:
  si `(√R ‖h_{Sᶜ}‖ + 2 Lc ‖h‖²)² ≤ (1 − c²)(‖DF(θ₀) h‖ − Lc ‖h‖²)²`, entonces `cos Δ ≥ c`.
  Todas las cantidades son calculables para cada escenario.
-/

open scoped BigOperators
open Set Metric FirstOrderErrorBound TrajectoryErrorBound

namespace CosineCertificate

section Cos

variable {W : Type*} [NormedAddCommGroup W] [InnerProductSpace ℝ W]

/-- **Cota inferior del coseno a partir del error relativo.** -/
theorem cos_lower_of_rel_error (a b : W) {ε c : ℝ}
    (hce : c ^ 2 + ε ^ 2 ≤ 1) (h : ‖a - b‖ ≤ ε * ‖a‖) :
    c * (‖a‖ * ‖b‖) ≤ inner ℝ a b := by
  have h1 : ‖a - b‖ ^ 2 = ‖a‖ ^ 2 - 2 * inner ℝ a b + ‖b‖ ^ 2 := norm_sub_sq_real a b
  have h2 : ‖a - b‖ ^ 2 ≤ ε ^ 2 * ‖a‖ ^ 2 := by
    have := pow_le_pow_left₀ (norm_nonneg _) h 2
    rwa [mul_pow] at this
  have h3 : 0 ≤ (c * ‖a‖ - ‖b‖) ^ 2 := sq_nonneg _
  nlinarith [sq_nonneg ‖a‖, norm_nonneg a, norm_nonneg b]

/-- Si además `ε < 1` y `a ≠ 0`, entonces `b ≠ 0` y `cos Δ ≥ c`. -/
theorem cos_ge_of_rel_error (a b : W) {ε c : ℝ} (hc : 0 ≤ c) (hε : 0 ≤ ε) (hε1 : ε < 1)
    (hce : c ^ 2 + ε ^ 2 ≤ 1) (h : ‖a - b‖ ≤ ε * ‖a‖) (ha : a ≠ 0) :
    b ≠ 0 ∧ c ≤ inner ℝ a b / (‖a‖ * ‖b‖) := by
  have hna : 0 < ‖a‖ := norm_pos_iff.2 ha
  have hnb : 0 < ‖b‖ := by
    have := norm_sub_norm_le a b
    have : (1 - ε) * ‖a‖ ≤ ‖b‖ := by nlinarith
    nlinarith
  refine ⟨norm_pos_iff.1 hnb, ?_⟩
  rw [le_div_iff₀ (mul_pos hna hnb)]
  exact cos_lower_of_rel_error a b hce h

end Cos

section Finite

variable {m p : ℕ}

/-- **Taylor con derivada Lipschitz**: `‖F(θ₀+h) − F(θ₀) − DF(θ₀) h‖ ≤ Lc ‖h‖²`. -/
theorem taylor_bound
    (F : EuclideanSpace ℝ (Fin p) → EuclideanSpace ℝ (Fin m))
    (DF : EuclideanSpace ℝ (Fin p) → (EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin m)))
    (θ₀ : EuclideanSpace ℝ (Fin p)) {ρ₀ Lc : ℝ} (hLc : 0 ≤ Lc)
    (hDF : ∀ θ ∈ closedBall θ₀ ρ₀, HasFDerivAt F (DF θ) θ)
    (hLip : ∀ θ ∈ closedBall θ₀ ρ₀, ‖DF θ - DF θ₀‖ ≤ Lc * ‖θ - θ₀‖)
    (h : EuclideanSpace ℝ (Fin p)) (hh : ‖h‖ ≤ ρ₀) :
    ‖F (θ₀ + h) - F θ₀ - DF θ₀ h‖ ≤ Lc * ‖h‖ ^ 2 := by
  have hsub : closedBall θ₀ ‖h‖ ⊆ closedBall θ₀ ρ₀ := closedBall_subset_closedBall hh
  have key := (convex_closedBall θ₀ ‖h‖).norm_image_sub_le_of_norm_hasFDerivWithin_le'
    (f := F) (f' := DF) (φ := DF θ₀) (C := Lc * ‖h‖)
    (fun θ hθ => (hDF θ (hsub hθ)).hasFDerivWithinAt)
    (fun θ hθ => (hLip θ (hsub hθ)).trans
      (mul_le_mul_of_nonneg_left (by rw [← dist_eq_norm]; exact mem_closedBall.1 hθ) hLc))
    (mem_closedBall_self (norm_nonneg h))
    (mem_closedBall.2 (by rw [dist_eq_norm, add_sub_cancel_left]))
  rw [add_sub_cancel_left] at key
  calc _ ≤ Lc * ‖h‖ * ‖h‖ := key
    _ = Lc * ‖h‖ ^ 2 := by ring

/-- **Cota explícita para perturbaciones finitas.** Para todo `‖h‖ ≤ ρ₀`:
`‖F(θ₀+h) − F(θ₀+h_S)‖ ≤ √R(S) ‖h_{Sᶜ}‖ + 2 Lc ‖h‖²`, con `R(S)` la energía descartada de
`J = DF(θ₀)`. -/
theorem finite_trajectory_error
    (F : EuclideanSpace ℝ (Fin p) → EuclideanSpace ℝ (Fin m))
    (DF : EuclideanSpace ℝ (Fin p) → (EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin m)))
    (θ₀ : EuclideanSpace ℝ (Fin p)) {ρ₀ Lc : ℝ} (hLc : 0 ≤ Lc)
    (hDF : ∀ θ ∈ closedBall θ₀ ρ₀, HasFDerivAt F (DF θ) θ)
    (hLip : ∀ θ ∈ closedBall θ₀ ρ₀, ‖DF θ - DF θ₀‖ ≤ Lc * ‖θ - θ₀‖)
    (S : Finset (Fin p)) (h : EuclideanSpace ℝ (Fin p)) (hh : ‖h‖ ≤ ρ₀) :
    ‖F (θ₀ + h) - F (θ₀ + keepS S h)‖
      ≤ Real.sqrt (removedColumnEnergy (jacobianOf (DF θ₀)) S)
          * Real.sqrt (removedParamSq S (fun j => h j)) + 2 * Lc * ‖h‖ ^ 2 := by
  have hk := norm_keepS_le S h
  have t1 := taylor_bound F DF θ₀ hLc hDF hLip h hh
  have t2 := taylor_bound F DF θ₀ hLc hDF hLip (keepS S h) (hk.trans hh)
  have hlin := linear_part_bound (DF θ₀) S h
  have hsq : ‖keepS S h‖ ^ 2 ≤ ‖h‖ ^ 2 := pow_le_pow_left₀ (norm_nonneg _) hk 2
  have e : F (θ₀ + h) - F (θ₀ + keepS S h)
      = (DF θ₀ h - DF θ₀ (keepS S h)) + (F (θ₀ + h) - F θ₀ - DF θ₀ h)
        - (F (θ₀ + keepS S h) - F θ₀ - DF θ₀ (keepS S h)) := by abel
  rw [e]
  calc _ ≤ ‖DF θ₀ h - DF θ₀ (keepS S h)‖ + ‖F (θ₀ + h) - F θ₀ - DF θ₀ h‖
          + ‖F (θ₀ + keepS S h) - F θ₀ - DF θ₀ (keepS S h)‖ :=
        (norm_sub_le _ _).trans (add_le_add_right (norm_add_le _ _) _)
    _ ≤ _ := by nlinarith [mul_le_mul_of_nonneg_left hsq hLc]

/-- **Certificado de cos Δ para una perturbación finita `h`.** Sean
`Δx_full = F(θ₀+h) − F(θ₀)`, `Δx_sel = F(θ₀+h_S) − F(θ₀)`,
`e := √R ‖h_{Sᶜ}‖ + 2 Lc ‖h‖²` (cota del error) y `A := ‖DF(θ₀) h‖ − Lc ‖h‖²` (cota inferior
de la respuesta). Si `0 < A`, `0 < c` y `e² ≤ (1 − c²) A²`, entonces `Δx_sel ≠ 0` y
`cos Δ ≥ c`. -/
theorem finite_cos_certificate
    (F : EuclideanSpace ℝ (Fin p) → EuclideanSpace ℝ (Fin m))
    (DF : EuclideanSpace ℝ (Fin p) → (EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin m)))
    (θ₀ : EuclideanSpace ℝ (Fin p)) {ρ₀ Lc c : ℝ} (hLc : 0 ≤ Lc) (hc : 0 < c)
    (hDF : ∀ θ ∈ closedBall θ₀ ρ₀, HasFDerivAt F (DF θ) θ)
    (hLip : ∀ θ ∈ closedBall θ₀ ρ₀, ‖DF θ - DF θ₀‖ ≤ Lc * ‖θ - θ₀‖)
    (S : Finset (Fin p)) (h : EuclideanSpace ℝ (Fin p)) (hh : ‖h‖ ≤ ρ₀)
    (hA : 0 < ‖DF θ₀ h‖ - Lc * ‖h‖ ^ 2)
    (hcert : (Real.sqrt (removedColumnEnergy (jacobianOf (DF θ₀)) S)
          * Real.sqrt (removedParamSq S (fun j => h j)) + 2 * Lc * ‖h‖ ^ 2) ^ 2
        ≤ (1 - c ^ 2) * (‖DF θ₀ h‖ - Lc * ‖h‖ ^ 2) ^ 2) :
    F (θ₀ + keepS S h) - F θ₀ ≠ 0 ∧
      c ≤ inner ℝ (F (θ₀ + h) - F θ₀) (F (θ₀ + keepS S h) - F θ₀)
        / (‖F (θ₀ + h) - F θ₀‖ * ‖F (θ₀ + keepS S h) - F θ₀‖) := by
  set eB := Real.sqrt (removedColumnEnergy (jacobianOf (DF θ₀)) S)
          * Real.sqrt (removedParamSq S (fun j => h j)) + 2 * Lc * ‖h‖ ^ 2 with heB
  set A := ‖DF θ₀ h‖ - Lc * ‖h‖ ^ 2 with hAdef
  set a := F (θ₀ + h) - F θ₀ with ha
  set b := F (θ₀ + keepS S h) - F θ₀ with hb
  have heB0 : 0 ≤ eB := by positivity
  -- cota inferior de la respuesta completa
  have hA' : A ≤ ‖a‖ := by
    have t1 := taylor_bound F DF θ₀ hLc hDF hLip h hh
    have e : DF θ₀ h = a - (F (θ₀ + h) - F θ₀ - DF θ₀ h) := by rw [ha]; abel
    have key : ‖DF θ₀ h‖ ≤ ‖a‖ + ‖F (θ₀ + h) - F θ₀ - DF θ₀ h‖ := by
      calc ‖DF θ₀ h‖ = ‖a - (F (θ₀ + h) - F θ₀ - DF θ₀ h)‖ := congrArg _ e
        _ ≤ _ := norm_sub_le _ _
    rw [hAdef]; linarith
  have hapos : 0 < ‖a‖ := lt_of_lt_of_le hA hA'
  -- cota del error
  have herr : ‖a - b‖ ≤ eB := by
    have e : a - b = F (θ₀ + h) - F (θ₀ + keepS S h) := by rw [ha, hb]; abel
    rw [e]; exact finite_trajectory_error F DF θ₀ hLc hDF hLip S h hh
  -- error relativo ε = eB / ‖a‖ con c² + ε² ≤ 1
  set ε := eB / ‖a‖ with hεdef
  have hε0 : 0 ≤ ε := div_nonneg heB0 hapos.le
  have hrel : ‖a - b‖ ≤ ε * ‖a‖ := by rw [hεdef, div_mul_cancel₀ _ hapos.ne']; exact herr
  have hc1 : c ^ 2 ≤ 1 := by
    by_contra hcon; push_neg at hcon
    have : (1 - c ^ 2) * A ^ 2 < 0 :=
      mul_neg_of_neg_of_pos (by linarith) (sq_pos_of_pos hA)
    nlinarith [sq_nonneg eB]
  have hce : c ^ 2 + ε ^ 2 ≤ 1 := by
    have hA2 : A ^ 2 ≤ ‖a‖ ^ 2 := pow_le_pow_left₀ hA.le hA' 2
    have : eB ^ 2 ≤ (1 - c ^ 2) * ‖a‖ ^ 2 :=
      hcert.trans (mul_le_mul_of_nonneg_left hA2 (by linarith))
    have hε2 : ε ^ 2 = eB ^ 2 / ‖a‖ ^ 2 := by rw [hεdef, div_pow]
    rw [hε2]
    have : eB ^ 2 / ‖a‖ ^ 2 ≤ 1 - c ^ 2 := by
      rw [div_le_iff₀ (by positivity)]; linarith
    linarith
  have hε1 : ε < 1 := by
    have : ε ^ 2 < 1 := by nlinarith [sq_pos_of_pos hc]
    nlinarith
  exact cos_ge_of_rel_error a b hc.le hε0 hε1 hce hrel (norm_pos_iff.1 hapos)

end Finite

end CosineCertificate

