import Mathlib.Analysis.ODE.PicardLindelof

/-!
# Existencia global en `[a, b]` para EDOs con campo globalmente Lipschitz

Si `v t` es `K`-Lipschitz (globalmente) para cada `t ∈ [a, b]` y continuo en `t`,
entonces para todo dato inicial `y₀` existe una solución de `α' = v t α` en todo
`[a, b]` con `α a = y₀`. Se prueba pegando soluciones locales de Picard–Lindelöf
(Mathlib) sobre subintervalos de longitud fija `h` con `K h ≤ 1/2`.

Se usa para la ecuación variacional `S' = A(t) S + B(t)`, que es lineal.
-/

open Set Filter Topology NNReal

namespace ODEParamDiff

variable {F : Type*} [NormedAddCommGroup F] [NormedSpace ℝ F] [CompleteSpace F]

/-- `α` resuelve `α' = v t α` en `[a, c]` (derivadas dentro de `[a, c]`). -/
def IsSolOn (v : ℝ → F → F) (a c : ℝ) (α : ℝ → F) : Prop :=
  ∀ t ∈ Icc a c, HasDerivWithinAt α (v t (α t)) (Icc a c) t

set_option linter.deprecated false in
omit [CompleteSpace F] in
lemma isSolOn_self (v : ℝ → F → F) (a : ℝ) (α : ℝ → F) : IsSolOn v a a α := by
  intro t ht
  rw [Icc_self] at ht ⊢
  rw [mem_singleton_iff] at ht
  subst ht
  exact hasDerivWithinAt_iff_hasFDerivWithinAt.mpr
    (HasFDerivWithinAt.of_nhdsWithin_eq_bot (by simp))

/-- Paso de extensión: una solución en `[a, c]` se extiende a `[a, d]` si `K (d - c) ≤ 1/2`. -/
lemma extend_solution (v : ℝ → F → F) (K : ℝ≥0) {a b c d : ℝ}
    (hv : ∀ t ∈ Icc a b, LipschitzWith K (v t))
    (hcont : ∀ y, ContinuousOn (fun t => v t y) (Icc a b))
    (hac : a ≤ c) (hcd : c ≤ d) (hdb : d ≤ b) (hKh : (K : ℝ) * (d - c) ≤ 1 / 2)
    (α : ℝ → F) (hα : IsSolOn v a c α) :
    ∃ γ : ℝ → F, γ a = α a ∧ IsSolOn v a d γ := by
  have hsub : Icc c d ⊆ Icc a b := Icc_subset_Icc hac hdb
  obtain ⟨C, hC⟩ := (isCompact_Icc : IsCompact (Icc c d)).exists_bound_of_continuousOn
    ((hcont (α c)).mono hsub)
  set C₀ : ℝ := max C 0 with hC₀
  have hC₀nn : 0 ≤ C₀ := le_max_right _ _
  set R : ℝ≥0 := ⟨2 * C₀ * (d - c) + 1, by nlinarith [sub_nonneg.2 hcd]⟩ with hR
  set L : ℝ≥0 := ⟨C₀, hC₀nn⟩ + K * R with hL
  let t₀ : Icc c d := ⟨c, left_mem_Icc.2 hcd⟩
  have hPL : IsPicardLindelof v t₀ (α c) R 0 L K :=
    { lipschitzOnWith := fun t ht => (hv t (hsub ht)).lipschitzOnWith
      continuousOn := fun x _ => (hcont x).mono hsub
      norm_le := fun t ht x hx => by
        have h1 := (hv t (hsub ht)).dist_le_mul x (α c)
        have h2 : ‖v t (α c)‖ ≤ C₀ := (hC t ht).trans (le_max_left _ _)
        have h3 : dist x (α c) ≤ R := Metric.mem_closedBall.1 hx
        have h4 : ‖v t x‖ ≤ ‖v t (α c)‖ + dist (v t x) (v t (α c)) := by
          rw [dist_eq_norm]; exact norm_le_insert' _ _
        have hK0 : (0 : ℝ) ≤ K := K.2
        simp only [hL, NNReal.coe_add, NNReal.coe_mul, NNReal.coe_mk]
        nlinarith [mul_le_mul_of_nonneg_left h3 hK0]
      mul_max_le := by
        have hmax : max (d - c) (c - c) = d - c := by
          rw [sub_self]; exact max_eq_left (sub_nonneg.2 hcd)
        simp only [t₀, hmax, hL, hR, NNReal.coe_add, NNReal.coe_mul, NNReal.coe_mk,
          NNReal.coe_zero, sub_zero]
        have hK0 : (0 : ℝ) ≤ K := K.2
        have hdc : 0 ≤ d - c := sub_nonneg.2 hcd
        nlinarith [mul_le_mul_of_nonneg_left hKh (by positivity : (0:ℝ) ≤ 2 * C₀ * (d - c) + 1)] }
  obtain ⟨β, hβ0, hβ⟩ := hPL.exists_eq_forall_mem_Icc_hasDerivWithinAt₀
  have hβc : β c = α c := hβ0
  classical
  let γ : ℝ → F := fun t => if t ≤ c then α t else β t
  have hγα : ∀ y ∈ Icc a c, γ y = α y := fun y hy => if_pos hy.2
  have hγβ : ∀ y ∈ Icc c d, γ y = β y := by
    intro y hy
    by_cases h : y ≤ c
    · have : y = c := le_antisymm h hy.1
      subst this; simp [γ, hβc]
    · simp [γ, h]
  refine ⟨γ, hγα a ⟨le_rfl, hac⟩, ?_⟩
  intro t ht
  rcases lt_trichotomy t c with h | h | h
  · -- t < c: γ = α cerca de t
    have hmem : Icc a c ∈ 𝓝[Icc a d] t :=
      mem_nhdsWithin.2 ⟨Iio c, isOpen_Iio, h, fun y hy => ⟨hy.2.1, le_of_lt hy.1⟩⟩
    have h1 := (hα t ⟨ht.1, h.le⟩).mono_of_mem_nhdsWithin hmem
    have hγt : γ t = α t := hγα t ⟨ht.1, h.le⟩
    rw [hγt]
    refine h1.congr_of_eventuallyEq ?_ hγt
    filter_upwards [hmem] with y hy using hγα y hy
  · -- t = c: unión de [a,c] y [c,d]
    subst h
    have hγt : γ t = α t := hγα t ⟨hac, le_rfl⟩
    rw [hγt]
    have hl : HasDerivWithinAt γ (v t (α t)) (Icc a t) t :=
      (hα t ⟨hac, le_rfl⟩).congr hγα hγt
    have hr : HasDerivWithinAt γ (v t (α t)) (Icc t d) t := by
      have := hβ t ⟨le_rfl, hcd⟩
      rw [hβc] at this
      exact this.congr hγβ (by rw [hγt, hβc])
    have := hl.union hr
    rwa [Icc_union_Icc_eq_Icc hac hcd] at this
  · -- c < t: γ = β cerca de t
    have hmem : Icc c d ∈ 𝓝[Icc a d] t :=
      mem_nhdsWithin.2 ⟨Ioi c, isOpen_Ioi, h, fun y hy => ⟨le_of_lt hy.1, hy.2.2⟩⟩
    have h1 := (hβ t ⟨h.le, ht.2⟩).mono_of_mem_nhdsWithin hmem
    have hγt : γ t = β t := hγβ t ⟨h.le, ht.2⟩
    rw [hγt]
    refine h1.congr_of_eventuallyEq ?_ hγt
    filter_upwards [hmem] with y hy using hγβ y hy

/-- **Existencia global en `[a, b]`** para un campo globalmente `K`-Lipschitz y continuo en `t`. -/
theorem exists_solution_Icc (v : ℝ → F → F) (K : ℝ≥0) {a b : ℝ} (hab : a ≤ b)
    (hv : ∀ t ∈ Icc a b, LipschitzWith K (v t))
    (hcont : ∀ y, ContinuousOn (fun t => v t y) (Icc a b)) (y₀ : F) :
    ∃ α : ℝ → F, α a = y₀ ∧ IsSolOn v a b α := by
  set h : ℝ := 1 / (2 * (K : ℝ) + 2) with hh
  have hK0 : (0 : ℝ) ≤ K := K.2
  have hpos : 0 < h := by positivity
  have hKh : (K : ℝ) * h ≤ 1 / 2 := by
    rw [hh, mul_one_div, div_le_iff₀ (by positivity)]; nlinarith
  have hstep : ∀ x : ℝ, min (x + h) b ≤ min x b + h := by
    intro x
    rcases min_choice x b with h1 | h1 <;> rw [h1]
    · exact min_le_left _ _
    · linarith [min_le_right (x + h) b]
  have key : ∀ k : ℕ, ∃ α : ℝ → F, α a = y₀ ∧ IsSolOn v a (min (a + k * h) b) α := by
    intro k
    induction k with
    | zero =>
      refine ⟨fun _ => y₀, rfl, ?_⟩
      simpa [min_eq_left hab] using isSolOn_self v a (fun _ => y₀)
    | succ k ih =>
      obtain ⟨α, hα0, hα⟩ := ih
      have hc : a ≤ min (a + k * h) b := le_min (by nlinarith [k.cast_nonneg (α := ℝ)]) hab
      have hcd : min (a + k * h) b ≤ min (a + (k + 1 : ℕ) * h) b := by
        apply min_le_min_right; push_cast; nlinarith
      have hdc : min (a + (k + 1 : ℕ) * h) b - min (a + k * h) b ≤ h := by
        have := hstep (a + k * h); push_cast
        rw [show a + ((k : ℝ) + 1) * h = a + k * h + h by ring]; linarith
      have hKd : (K : ℝ) * (min (a + (k + 1 : ℕ) * h) b - min (a + k * h) b) ≤ 1 / 2 :=
        (mul_le_mul_of_nonneg_left hdc hK0).trans hKh
      obtain ⟨γ, hγ0, hγ⟩ := extend_solution v K hv hcont hc hcd (min_le_right _ _) hKd α hα
      exact ⟨γ, hγ0.trans hα0, hγ⟩
  obtain ⟨k, hk⟩ := exists_nat_ge ((b - a) / h)
  obtain ⟨α, h0, hα⟩ := key k
  have hb : min (a + k * h) b = b := by
    apply min_eq_right
    have := (div_le_iff₀ hpos).1 hk
    linarith
  exact ⟨α, h0, hb ▸ hα⟩

end ODEParamDiff
