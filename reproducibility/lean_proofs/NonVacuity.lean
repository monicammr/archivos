import ScaledError
import Poda
import GreedySelection
import RefitMonotone
import IdentifiabilityConditioning
import ProfileIdentifiability

/-!
# Non-vacuity witnesses for the central theorems

A theorem whose hypotheses can never hold, or whose conclusion is a definition that always holds,
is true but says nothing. For each central theorem of the paper this file gives

* a **witness**: a concrete instance in which every hypothesis is proved, so that the theorem
  actually applies (its hypotheses are consistent), and
* where the conclusion is a defined property (κ and VIF filters, practical identifiability), a
  **negative example** in which that property fails, so that the definition is not trivially true.

Every `example` below is checked by the Lean kernel; nothing here is assumed.
-/

open RealInnerProductSpace

/-! ## Theorem 1 (`ScaledError.min_rel_error_eq`): threshold τₑ = √(1 − c²) -/

/-- Witness in `ℝ²`: `d = (1, 0)`, `b = (1, 1)`; both nonzero, so the theorem applies. -/
example : True := by
  let d : EuclideanSpace ℝ (Fin 2) := EuclideanSpace.single 0 1
  let b : EuclideanSpace ℝ (Fin 2) := EuclideanSpace.single 0 1 + EuclideanSpace.single 1 1
  have hd : d ≠ 0 := by
    intro h
    have := congrArg (fun v : EuclideanSpace ℝ (Fin 2) => v 0) h
    simp [d] at this
  have hb : b ≠ 0 := by
    intro h
    have := congrArg (fun v : EuclideanSpace ℝ (Fin 2) => v 0) h
    simp [b] at this
  have _ := ScaledError.min_rel_error_eq d b hd hb
  trivial

/-! ## Theorem 2 (`Poda.prune_spec`, `Poda.prune_inclusion_minimal`): backward elimination -/

namespace NonVacuityPoda

/-- Admissibility predicate of the witness: at least two elements (the rule `|S| ≥ 2`). -/
def Q (T : Finset (Fin 3)) : Prop := 2 ≤ T.card

/-- Removal rule: remove the smallest element while at least three remain. -/
def pick (T : Finset (Fin 3)) : Option (Fin 3) :=
  if h : 3 ≤ T.card then some (T.min' (Finset.card_pos.1 (by omega))) else none

theorem hpick : ∀ T x, pick T = some x → x ∈ T ∧ Q (T.erase x) := by
  intro T x h
  unfold pick at h
  split_ifs at h with h3
  · cases h
    refine ⟨Finset.min'_mem _ _, ?_⟩
    unfold Q
    rw [Finset.card_erase_of_mem (Finset.min'_mem _ _)]
    omega

theorem hnone : ∀ T, pick T = none → ∀ x ∈ T, ¬ Q (T.erase x) := by
  intro T h x hx
  unfold pick at h
  split_ifs at h with h3
  unfold Q
  rw [Finset.card_erase_of_mem hx]
  omega

theorem hmono : ∀ U T : Finset (Fin 3), U ⊆ T → Q U → Q T :=
  fun _ _ hUT hU => le_trans hU (Finset.card_le_card hUT)

/-- Witness: starting from all three elements, the hypotheses of both theorems hold, and the
result is admissible, contained in the start set and minimal (no element can be removed, no
proper subset admissible). -/
example : let R := Poda.prune Q pick hpick Finset.univ
    Q R ∧ R ⊆ Finset.univ ∧ (∀ x ∈ R, ¬ Q (R.erase x)) ∧ ∀ U, U ⊂ R → ¬ Q U := by
  intro R
  have hS : Q (Finset.univ : Finset (Fin 3)) := by unfold Q; simp
  obtain ⟨h1, h2, h3⟩ := Poda.prune_spec Q pick hpick hnone Finset.univ hS
  obtain ⟨-, -, h4⟩ := Poda.prune_inclusion_minimal Q pick hpick hnone hmono Finset.univ hS
  exact ⟨h1, h2, h3, h4⟩

end NonVacuityPoda

/-! ## Greedy selection with κ and VIF filters (`GreedySelection`) -/

namespace NonVacuityGreedy

open GreedySelection

/-- The κ filter holds for the identity (orthonormal columns) with κ₀ = 1. -/
example : okKappa (ContinuousLinearMap.id ℝ (EuclideanSpace ℝ (Fin 2))) 1 Finset.univ :=
  ⟨1, 1, one_pos, by norm_num, fun u _ => by simp⟩

/-- The κ filter fails for the zero map on a nonempty set: the definition is not trivially true. -/
example (κ₀ : ℝ) : ¬ okKappa (0 : EuclideanSpace ℝ (Fin 2) →L[ℝ] EuclideanSpace ℝ (Fin 2)) κ₀ {0} := by
  rintro ⟨σmin, σmax, h0, -, hb⟩
  have hs : SupportedOn {0} (EuclideanSpace.single (0 : Fin 2) (1 : ℝ)) := by
    intro i hi
    have : i ≠ 0 := by simpa using hi
    simp [EuclideanSpace.single_apply, this]
  have := (hb _ hs).1
  simp at this
  linarith

/-- The VIF filter fails for the zero map on a nonempty set. -/
example (V : ℝ) (hV : 0 < V) :
    ¬ okVIF (0 : EuclideanSpace ℝ (Fin 2) →L[ℝ] EuclideanSpace ℝ (Fin 2)) V {0} := by
  intro h
  have hs : SupportedOn {0} (EuclideanSpace.single (0 : Fin 2) (1 : ℝ)) := by
    intro i hi
    have : i ≠ 0 := by simpa using hi
    simp [EuclideanSpace.single_apply, this]
  have := h 0 (by simp) _ hs (by simp)
  simp at this
  have : 0 < 1 / V := by positivity
  linarith

end NonVacuityGreedy

/-! ## Re-estimation never increases the error (`RefitMonotone.admissible_mono`) -/

/-- Witness with one parameter: `r θ = |θ 0 − 1|`, θ₀ = 0, box = everything. Re-estimating the
parameter (`T = univ`) is admissible whenever not re-estimating it (`S = ∅`) is. -/
example (τ : ℝ) (hS : RefitMonotone.fitErr (fun θ : Fin 1 → ℝ => |θ 0 - 1|) 0 Set.univ ∅ ≤ τ) :
    RefitMonotone.fitErr (fun θ : Fin 1 → ℝ => |θ 0 - 1|) 0 Set.univ Set.univ ≤ τ :=
  RefitMonotone.admissible_mono _ _ _ (fun θ => abs_nonneg _) (Set.empty_subset _)
    ⟨0, Set.mem_univ _, fun _ _ => rfl⟩ hS

/-! ## Practical identifiability (`ProfileIdentifiability`) -/

namespace NonVacuityProfile

open ProfileIdentifiability

lemma sqrt_384_lt (b : ℝ) (hb : 3.84 < b ^ 2) (hb0 : 0 < b) : Real.sqrt 3.84 < b :=
  (Real.sqrt_lt' hb0).2 hb

/-- **Nonlinear witness** of `practically_identifiable_grad`: residual `R δ = δ + δ²/100` on the
admissible set `F = [−3, 3]`, linearisation `A = id`, information `I = 1`, residual at the optimum
`R 0 = 0` (so `γ = 0`), nonlinear remainder `δ²/100 ≤ ε = 0.09` on `F`, and bounds at distance 3.
All hypotheses are proved, including the remainder bound on the whole of `F`. -/
example : PracticallyIdentifiable (fun δ : ℝ => δ + δ ^ 2 / 100) id (Set.Icc (-3) 3) 3.84 3 3 := by
  have hR0 : ‖(fun δ : ℝ => δ + δ ^ 2 / 100) 0‖ = 0 := by simp
  have ht : tstarGrad 1 0.09 0 3.84 ‖(fun δ : ℝ => δ + δ ^ 2 / 100) 0‖ < 3 := by
    rw [hR0]; unfold tstarGrad
    have : Real.sqrt (0 ^ 2 + 3.84 + 2 * 0 * 0.09 + 2 * 0 * 0.09) < 2.91 := by
      have := sqrt_384_lt 2.91 (by norm_num) (by norm_num); norm_num at this ⊢; exact this
    rw [Real.sqrt_one]; linarith
  refine practically_identifiable_grad (fun δ : ℝ => δ + δ ^ 2 / 100) (ContinuousLinearMap.id ℝ ℝ)
    id (Set.Icc (-3) 3) (ε := 0.09) (γ := 0) (I := 1) (by norm_num) (by norm_num) le_rfl one_pos
    (fun δ => by simp [Real.norm_eq_abs, sq_abs]) (fun δ => by simp) ?_ ht ht
  intro δ hδ
  obtain ⟨h1, h2⟩ := hδ
  have : δ + δ ^ 2 / 100 - (0 + 0 ^ 2 / 100) - δ = δ ^ 2 / 100 := by ring
  simp only [ContinuousLinearMap.id_apply, this, Real.norm_eq_abs]
  rw [abs_of_nonneg (by positivity)]
  nlinarith

/-- Witness of the relative-remainder tail theorem `practically_identifiable_rel_tail`: same
residual, `η = 0.03` (on `F = [−3, 3]`, `δ²/100 ≤ 0.03 |δ|`), tail from `t = 2.1`. -/
example : PracticallyIdentifiable (fun δ : ℝ => δ + δ ^ 2 / 100) id (Set.Icc (-3) 3) 3.84 3 3 := by
  have hR0 : ‖(fun δ : ℝ => δ + δ ^ 2 / 100) 0‖ = 0 := by simp
  have ht : tstarRel 1 0.03 0 3.84 ‖(fun δ : ℝ => δ + δ ^ 2 / 100) 0‖ ≤ 2.1 := by
    rw [hR0]; unfold tstarRel
    have : Real.sqrt ((0 + 0.03 * 0) ^ 2 + (1 - 0.03) ^ 2 * 3.84) < 1.97 := by
      have := sqrt_384_lt 1.97 (by norm_num) (by norm_num)
      have h2 : Real.sqrt ((0 + 0.03 * 0) ^ 2 + (1 - 0.03) ^ 2 * 3.84) ≤ Real.sqrt 3.84 :=
        Real.sqrt_le_sqrt (by norm_num)
      linarith
    rw [Real.sqrt_one, div_le_iff₀ (by norm_num)]; linarith
  refine practically_identifiable_rel_tail (fun δ : ℝ => δ + δ ^ 2 / 100)
    (ContinuousLinearMap.id ℝ ℝ) id (Set.Icc (-3) 3) (η := 0.03) (γ := 0) (I := 1)
    (tlo := 2.1) (thi := 2.1) (by norm_num) (by norm_num) (by norm_num) le_rfl one_pos
    (fun δ => by simp [Real.norm_eq_abs, sq_abs]) (fun δ => by simp) ht ht (by norm_num)
    (by norm_num) ?_
  intro δ hδ _
  obtain ⟨h1, h2⟩ := hδ
  have : δ + δ ^ 2 / 100 - (0 + 0 ^ 2 / 100) - δ = δ ^ 2 / 100 := by ring
  simp only [ContinuousLinearMap.id_apply, this, Real.norm_eq_abs]
  rw [abs_of_nonneg (by positivity)]
  rcases le_total 0 δ with h | h
  · rw [abs_of_nonneg h]; nlinarith
  · rw [abs_of_nonpos h]; nlinarith

/-- Negative example: a residual that does not depend on the parameter (flat profile) is not
practically identifiable, so the definition is not trivially satisfied. -/
example : ¬ PracticallyIdentifiable (fun _ : ℝ => (0 : ℝ)) id Set.univ 3.84 3 3 := by
  rintro ⟨tlo, thi, -, -, -, -, h⟩
  have := h thi trivial (Or.inr le_rfl)
  simp [dchi2] at this
  norm_num at this

end NonVacuityProfile

/-! ## Stability of the linearised least-squares problem (`Identifiability.ls_kappa_stability`) -/

/-- Witness: the identity on `ℝ²` has unit columns and κ = 1; least-squares solutions of `y` and
`y'` are `y` and `y'` themselves, and the theorem gives `‖v − v'‖ ≤ ‖y − y'‖`. -/
example (y y' : EuclideanSpace ℝ (Fin 2)) : ‖y - y'‖ ≤ 1 * ‖y - y'‖ := by
  have hunit : ∀ j, ‖(ContinuousLinearMap.id ℝ (EuclideanSpace ℝ (Fin 2)))
      (EuclideanSpace.single j 1)‖ = 1 := by intro j; simp
  exact Identifiability.ls_kappa_stability (ContinuousLinearMap.id ℝ _) hunit 0 (σmax := 1)
    one_pos (fun u => by simp) (fun u => by simp) (by norm_num)
    (fun w => by simp) (fun w => by simp)

#print axioms NonVacuityPoda.hpick
