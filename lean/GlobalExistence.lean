import PositivityInvariance
import GlobalLipschitzODE

/-!
# Existencia global de la solución nominal (condición C4)

Los teoremas de diferenciabilidad suponen que la solución nominal existe en todo `[0, T]`. Aquí se
**demuestra** esa existencia para la clase de modelos con crecimiento lineal de una combinación
positiva de concentraciones:

* `v` es C¹ en un abierto `U` que contiene el ortante `≥ 0`;
* `v` es cuasi-positivo (una especie ausente no puede consumirse);
* existe `c` con `cᵢ ≥ c_min > 0` y `a, b ≥ 0` tales que, en el ortante,
  `Σᵢ cᵢ vᵢ(z) ≤ a + b Σᵢ cᵢ zᵢ` (p. ej. conservación de masa con síntesis y degradación).

`exists_global_solution`: para todo dato inicial `≥ 0` y todo `T ≥ 0` existe una solución en
`[0, T]`, que además es `≥ 0`.

Prueba: se trunca el campo a una caja `[0, B]ⁿ` (`w = v ∘ clampB`, globalmente Lipschitz porque
`v` es C¹ en la caja compacta y convexa); `exists_solution_Icc` da una solución global del sistema
truncado; es `≥ 0` por `nonneg_core`; Grönwall sobre `φ = Σ cᵢ xᵢ` la acota, luego nunca llega al
borde superior de la caja y resuelve el sistema original.
-/

open Set Filter Topology Metric NNReal PositivityInvariance ODEParamDiff

namespace GlobalExistence

variable {n : ℕ}

/-- Truncamiento a la caja `[0, B]ⁿ`. -/
noncomputable def clampB (B : ℝ) (z : EuclideanSpace ℝ (Fin n)) : EuclideanSpace ℝ (Fin n) :=
  WithLp.toLp 2 (fun i => max 0 (min B (z i)))

lemma clampB_apply (B : ℝ) (z : EuclideanSpace ℝ (Fin n)) (i : Fin n) :
    clampB B z i = max 0 (min B (z i)) := rfl

lemma clampB_nonneg (B : ℝ) (z : EuclideanSpace ℝ (Fin n)) : Nonneg (clampB B z) :=
  fun _ => le_max_left _ _

lemma clampB_le {B : ℝ} (hB : 0 ≤ B) (z : EuclideanSpace ℝ (Fin n)) (i : Fin n) :
    clampB B z i ≤ B := max_le hB (min_le_left _ _)

lemma clampB_pos (B : ℝ) (z : EuclideanSpace ℝ (Fin n)) : clampB B (pos z) = clampB B z := by
  ext i
  rw [clampB_apply, clampB_apply, pos_apply]
  rcases le_total (z i) 0 with h | h
  · rw [max_eq_right h]
    have h1 : min B 0 ≤ 0 := min_le_right _ _
    have h2 : min B (z i) ≤ 0 := (min_le_right _ _).trans h
    rw [max_eq_left h1, max_eq_left h2]
  · rw [max_eq_left h]

lemma clampB_eq {B : ℝ} {z : EuclideanSpace ℝ (Fin n)} (hz : Nonneg z) (hzB : ∀ i, z i ≤ B) :
    clampB B z = z := by
  ext i
  rw [clampB_apply, min_eq_right (hzB i), max_eq_right (hz i)]

lemma dist_clampB_le (B : ℝ) (y y' : EuclideanSpace ℝ (Fin n)) :
    dist (clampB B y) (clampB B y') ≤ dist y y' := by
  rw [EuclideanSpace.dist_eq, EuclideanSpace.dist_eq]
  apply Real.sqrt_le_sqrt
  apply Finset.sum_le_sum
  intro i _
  rw [Real.dist_eq, Real.dist_eq, clampB_apply, clampB_apply, max_comm 0, max_comm 0]
  refine pow_le_pow_left₀ (abs_nonneg _) ((abs_max_sub_max_le_abs _ _ _).trans ?_) 2
  have := abs_min_sub_min_le_max B (y i) B (y' i)
  simpa using this

/-- La caja `[0, B]ⁿ`. -/
def box (B : ℝ) : Set (EuclideanSpace ℝ (Fin n)) := {z | Nonneg z ∧ ∀ i, z i ≤ B}

lemma clampB_mem {B : ℝ} (hB : 0 ≤ B) (z : EuclideanSpace ℝ (Fin n)) : clampB B z ∈ box B :=
  ⟨clampB_nonneg B z, clampB_le hB z⟩

lemma convex_box (B : ℝ) : Convex ℝ (box (n := n) B) := by
  intro x hx y hy a b ha hb hab
  refine ⟨fun i => ?_, fun i => ?_⟩
  · simp only [PiLp.add_apply, PiLp.smul_apply, smul_eq_mul]
    exact add_nonneg (mul_nonneg ha (hx.1 i)) (mul_nonneg hb (hy.1 i))
  · simp only [PiLp.add_apply, PiLp.smul_apply, smul_eq_mul]
    have h1 := mul_le_mul_of_nonneg_left (hx.2 i) ha
    have h2 := mul_le_mul_of_nonneg_left (hy.2 i) hb
    have h3 : a * B + b * B = B := by rw [← add_mul, hab, one_mul]
    linarith

lemma isCompact_box (B : ℝ) : IsCompact (box (n := n) B) := by
  apply Metric.isCompact_of_isClosed_isBounded
  · have : box (n := n) B = ⋂ i, ({z : EuclideanSpace ℝ (Fin n) | 0 ≤ z i} ∩ {z | z i ≤ B}) := by
      ext z; simp [box, Nonneg, forall_and]
    rw [this]
    have hc : ∀ i : Fin n, Continuous fun z : EuclideanSpace ℝ (Fin n) => z i := fun i =>
      (EuclideanSpace.proj i : EuclideanSpace ℝ (Fin n) →L[ℝ] ℝ).continuous
    exact isClosed_iInter fun i =>
      (isClosed_le continuous_const (hc i)).inter (isClosed_le (hc i) continuous_const)
  · rw [Metric.isBounded_iff_subset_closedBall 0]
    refine ⟨Real.sqrt (∑ _i : Fin n, B ^ 2), fun z hz => ?_⟩
    rw [mem_closedBall, dist_zero_right, EuclideanSpace.norm_eq]
    apply Real.sqrt_le_sqrt
    apply Finset.sum_le_sum
    intro i _
    rw [Real.norm_eq_abs, sq_abs]
    exact pow_le_pow_left₀ (hz.1 i) (hz.2 i) 2


/-- Un campo C¹ en un abierto que contiene la caja es Lipschitz en la caja. -/
lemma lipschitzOn_box (v : EuclideanSpace ℝ (Fin n) → EuclideanSpace ℝ (Fin n))
    {U : Set (EuclideanSpace ℝ (Fin n))} (hU : IsOpen U) (hv : ContDiffOn ℝ 1 v U)
    (B : ℝ) (hbox : box B ⊆ U) : ∃ L : ℝ≥0, LipschitzOnWith L v (box B) := by
  have hDv : ContinuousOn (fderiv ℝ v) (box B) :=
    (hv.continuousOn_fderiv_of_isOpen hU le_rfl).mono hbox
  obtain ⟨M, hM⟩ := (isCompact_box B).exists_bound_of_continuousOn hDv
  refine ⟨⟨max M 0, le_max_right _ _⟩, ?_⟩
  refine (convex_box B).lipschitzOnWith_of_nnnorm_hasFDerivWithin_le
    (f' := fderiv ℝ v) (fun z hz => ?_) (fun z hz => ?_)
  · exact ((hv.contDiffAt (hU.mem_nhds (hbox hz))).differentiableAt le_rfl).hasFDerivAt
      |>.hasFDerivWithinAt
  · rw [← NNReal.coe_le_coe, coe_nnnorm, NNReal.coe_mk]
    exact (hM z hz).trans (le_max_left _ _)

/-- **Existencia global de la solución (condición C4).** -/
theorem exists_global_solution (v : EuclideanSpace ℝ (Fin n) → EuclideanSpace ℝ (Fin n))
    {U : Set (EuclideanSpace ℝ (Fin n))} (hU : IsOpen U) (hv : ContDiffOn ℝ 1 v U)
    (horth : ∀ z, Nonneg z → z ∈ U)
    (hqp : ∀ z, Nonneg z → ∀ i, z i = 0 → 0 ≤ v z i)
    (c : Fin n → ℝ) {cmin a b : ℝ} (hcmin : 0 < cmin) (hc : ∀ i, cmin ≤ c i)
    (ha : 0 ≤ a) (hb : 0 ≤ b)
    (hgrowth : ∀ z, Nonneg z → ∑ i, c i * v z i ≤ a + b * ∑ i, c i * z i)
    (x0 : EuclideanSpace ℝ (Fin n)) (hx0 : Nonneg x0) {T : ℝ} (hT : 0 ≤ T) :
    ∃ x : ℝ → EuclideanSpace ℝ (Fin n), x 0 = x0 ∧
      ∀ t ∈ Icc 0 T, HasDerivWithinAt x (v (x t)) (Icc 0 T) t ∧ Nonneg (x t) := by
  have hcpos : ∀ i, 0 < c i := fun i => hcmin.trans_le (hc i)
  set K' : ℝ := b + 1 with hK'
  have hK'pos : 0 < K' := by rw [hK']; linarith
  set φ0 : ℝ := ∑ i, c i * x0 i with hφ0
  have hφ0 : 0 ≤ φ0 := Finset.sum_nonneg fun i _ => mul_nonneg (hcpos i).le (hx0 i)
  set E1 := Real.exp (K' * T) with hE1
  have hE1' : 1 ≤ E1 := Real.one_le_exp (mul_nonneg hK'pos.le hT)
  set M : ℝ := φ0 * E1 + a / K' * (E1 - 1) with hM
  have hM0 : 0 ≤ M := add_nonneg (mul_nonneg hφ0 (by linarith))
    (mul_nonneg (div_nonneg ha hK'pos.le) (by linarith))
  set B : ℝ := M / cmin + 1 with hB
  have hB0 : 0 ≤ B := by rw [hB]; have := div_nonneg hM0 hcmin.le; linarith
  have hbox : box B ⊆ U := fun z hz => horth z hz.1
  obtain ⟨L, hL⟩ := lipschitzOn_box v hU hv B hbox
  -- campo truncado
  set w : EuclideanSpace ℝ (Fin n) → EuclideanSpace ℝ (Fin n) := fun z => v (clampB B z)
    with hw
  have hwLip : LipschitzWith L w := LipschitzWith.of_dist_le_mul fun y y' => by
    have := hL.dist_le_mul _ (clampB_mem hB0 y) _ (clampB_mem hB0 y')
    exact this.trans (mul_le_mul_of_nonneg_left (dist_clampB_le B y y') L.2)
  obtain ⟨α, hα0, hαsol⟩ := exists_solution_Icc (fun _ => w) L hT (fun _ _ => hwLip)
    (fun _ => continuousOn_const) x0
  have hα : ∀ t ∈ Icc 0 T, HasDerivWithinAt α (w (α t)) (Icc 0 T) t := hαsol
  -- positividad del sistema truncado
  have hnn : ∀ t ∈ Icc 0 T, Nonneg (α t) := by
    refine nonneg_core w α (K := 0) le_rfl hα (by rw [hα0]; exact hx0) ?_ ?_
    · intro t _
      have : w (pos (α t)) = w (α t) := by simp only [hw, clampB_pos]
      rw [this, sub_self, norm_zero]; positivity
    · intro t _ i hi
      have hy : clampB B (pos (α t)) i = 0 := by
        rw [clampB_apply, hi, min_eq_right hB0, max_self]
      exact hqp _ (clampB_nonneg _ _) i hy
  -- Grönwall sobre φ = Σ cᵢ αᵢ
  set φ : ℝ → ℝ := fun t => ∑ i, c i * α t i with hφdef
  set φ' : ℝ → ℝ := fun t => ∑ i, c i * w (α t) i with hφ'def
  have hφd : ∀ t ∈ Icc 0 T, HasDerivWithinAt φ (φ' t) (Icc 0 T) t := by
    intro t ht
    apply HasDerivWithinAt.fun_sum
    intro i _
    have hxi : HasDerivWithinAt (fun t => α t i) (w (α t) i) (Icc 0 T) t := by
      have := (EuclideanSpace.proj i : EuclideanSpace ℝ (Fin n) →L[ℝ] ℝ).hasFDerivAt
        |>.comp_hasDerivWithinAt t (hα t ht)
      simpa using this
    exact hxi.const_mul (c i)
  have hφc : ContinuousOn φ (Icc 0 T) := fun t ht => (hφd t ht).continuousWithinAt
  have hφ0' : ∀ t ∈ Icc 0 T, 0 ≤ φ t := fun t ht =>
    Finset.sum_nonneg fun i _ => mul_nonneg (hcpos i).le (hnn t ht i)
  have hbound : ∀ t ∈ Icc 0 T, φ' t ≤ K' * φ t + a := by
    intro t ht
    have h1 := hgrowth (clampB B (α t)) (clampB_nonneg _ _)
    have h2 : ∑ i, c i * clampB B (α t) i ≤ φ t := by
      apply Finset.sum_le_sum
      intro i _
      apply mul_le_mul_of_nonneg_left _ (hcpos i).le
      rw [clampB_apply]
      exact max_le (hnn t ht i) (min_le_right _ _)
    have h3 := hφ0' t ht
    show ∑ i, c i * v (clampB B (α t)) i ≤ K' * φ t + a
    nlinarith [mul_le_mul_of_nonneg_left h2 hb]
  have hIci : ∀ t ∈ Ico 0 T, Icc 0 T ∈ 𝓝[Ici t] t := fun t ht =>
    mem_of_superset (Icc_mem_nhdsGE ht.2) (Icc_subset_Icc ht.1 le_rfl)
  have gron := le_gronwallBound_of_liminf_deriv_right_le (f := φ) (f' := φ')
    (δ := φ0) (K := K') (ε := a) hφc
    (fun t ht r hr => ((hφd t (Ico_subset_Icc_self ht)).mono_of_mem_nhdsWithin
      (hIci t ht)).liminf_right_slope_le hr)
    (by show ∑ i, c i * α 0 i ≤ φ0; rw [hα0])
    (fun t ht => hbound t (Ico_subset_Icc_self ht))
  have hφM : ∀ t ∈ Icc 0 T, φ t ≤ M := by
    intro t ht
    have g := gron t ht
    rw [sub_zero, gronwallBound_of_K_ne_0 hK'pos.ne'] at g
    simp only at g
    have he : Real.exp (K' * t) ≤ E1 :=
      Real.exp_le_exp.2 (mul_le_mul_of_nonneg_left ht.2 hK'pos.le)
    have h1 := mul_le_mul_of_nonneg_left he hφ0
    have h2 := mul_le_mul_of_nonneg_left (sub_le_sub_right he 1) (div_nonneg ha hK'pos.le)
    rw [hM]; linarith
  -- la solución truncada no llega al borde superior: resuelve el sistema original
  have hbelow : ∀ t ∈ Icc 0 T, ∀ i, α t i ≤ B := by
    intro t ht i
    have h1 : c i * α t i ≤ φ t :=
      Finset.single_le_sum (f := fun j => c j * α t j)
        (fun j _ => mul_nonneg (hcpos j).le (hnn t ht j)) (Finset.mem_univ i)
    have h2 : cmin * α t i ≤ c i * α t i := mul_le_mul_of_nonneg_right (hc i) (hnn t ht i)
    have h3 : α t i ≤ M / cmin := by
      rw [le_div_iff₀ hcmin]; linarith [hφM t ht]
    rw [hB]; linarith
  refine ⟨α, hα0, fun t ht => ⟨?_, hnn t ht⟩⟩
  have : w (α t) = v (α t) := by
    simp only [hw]; rw [clampB_eq (hnn t ht) (hbelow t ht)]
  rw [← this]; exact hα t ht

end GlobalExistence

#print axioms GlobalExistence.exists_global_solution
