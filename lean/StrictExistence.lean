import GlobalExistence

/-!
# Existencia global con positividad estricta

Algunos modelos sólo están bien definidos si ciertas especies son **estrictamente** positivas
(p. ej. una incidencia `β·S·I/N` exige `N > 0`; una potencia de Hill `Z^n` con `n` real exige
`Z > 0`). Sea `Σ` (máscara `sx`) el conjunto de especies con dato inicial `> 0` y
`P = {y ≥ 0, yⱼ > 0 para j ∈ Σ}` (`SPos`).

`exists_global_solution_strict`: si `v` es C¹ en un abierto `U ⊇ P`, cuasi-positivo en `P`
(para las especies fuera de `Σ`), el consumo de cada especie de `Σ` es como mucho
proporcional a ella en cada caja acotada (`vᵢ(z) ≥ −C zᵢ` si `z ∈ P`, `z ≤ B`), y se cumple la
cota de crecimiento lineal con pesos `cᵢ ≥ c_min > 0`, entonces para todo dato inicial en `P`
y todo `T ≥ 0` existe la solución en `[0, T]` y **permanece en `P`**.

Prueba: se fija la cota superior `B` de Grönwall (no depende del truncamiento), la constante de
consumo `C` en la caja `[0, B]`, y `ε = (m₀/2)·e^{−(C+1)T}`, con `m₀` el mínimo de los datos
iniciales de `Σ`. Se trunca el campo a la caja compacta y convexa
`Q = {ε ≤ zⱼ ≤ B (j ∈ Σ), 0 ≤ zⱼ ≤ B (j ∉ Σ)} ⊆ P`; el sistema truncado tiene solución global.
Por comparación con la frontera `g(t) = (m₀/2)e^{−(C+1)t}`, cada especie de `Σ` queda `≥ g ≥ ε`;
las demás quedan `≥ 0` (`nonneg_core`); Grönwall da la cota `B`. Así el truncamiento no actúa y
la solución truncada resuelve el sistema original.
-/

open Set Filter Topology Metric NNReal PositivityInvariance ODEParamDiff GlobalExistence

namespace StrictExistence

variable {n : ℕ}

/-- Región estricta `P`: `y ≥ 0` e `yⱼ > 0` para `j ∈ Σ`. -/
def SPos (sx : Fin n → Bool) (y : EuclideanSpace ℝ (Fin n)) : Prop :=
  Nonneg y ∧ ∀ j, sx j = true → 0 < y j

/-- Cota inferior de la caja: `ε` en `Σ`, `0` fuera. -/
noncomputable def lo (sx : Fin n → Bool) (ε : ℝ) (i : Fin n) : ℝ := if sx i then ε else 0

lemma lo_nonneg (sx : Fin n → Bool) {ε : ℝ} (hε : 0 ≤ ε) (i : Fin n) : 0 ≤ lo sx ε i := by
  unfold lo; split_ifs <;> simp [hε]

lemma lo_le (sx : Fin n → Bool) {ε B : ℝ} (hε : 0 ≤ ε) (hεB : ε ≤ B) (i : Fin n) :
    lo sx ε i ≤ B := by
  unfold lo; split_ifs <;> linarith

/-- Truncamiento a la caja `Q`. -/
noncomputable def clampQ (sx : Fin n → Bool) (ε B : ℝ) (z : EuclideanSpace ℝ (Fin n)) :
    EuclideanSpace ℝ (Fin n) :=
  WithLp.toLp 2 (fun i => max (lo sx ε i) (min B (z i)))

lemma clampQ_apply (sx : Fin n → Bool) (ε B : ℝ) (z : EuclideanSpace ℝ (Fin n)) (i : Fin n) :
    clampQ sx ε B z i = max (lo sx ε i) (min B (z i)) := rfl

/-- La caja `Q`. -/
def boxQ (sx : Fin n → Bool) (ε B : ℝ) : Set (EuclideanSpace ℝ (Fin n)) :=
  {z | ∀ i, lo sx ε i ≤ z i ∧ z i ≤ B}

lemma clampQ_mem (sx : Fin n → Bool) {ε B : ℝ} (hε : 0 ≤ ε) (hεB : ε ≤ B)
    (z : EuclideanSpace ℝ (Fin n)) : clampQ sx ε B z ∈ boxQ sx ε B :=
  fun i => ⟨le_max_left _ _, max_le (lo_le sx hε hεB i) (min_le_left _ _)⟩

lemma boxQ_sPos (sx : Fin n → Bool) {ε B : ℝ} (hε : 0 < ε) {z : EuclideanSpace ℝ (Fin n)}
    (hz : z ∈ boxQ sx ε B) : SPos sx z := by
  refine ⟨fun i => (lo_nonneg sx hε.le i).trans (hz i).1, fun j hj => ?_⟩
  have := (hz j).1
  simp only [lo, hj, if_true] at this
  linarith

lemma clampQ_pos (sx : Fin n → Bool) {ε : ℝ} (hε : 0 ≤ ε) (B : ℝ)
    (z : EuclideanSpace ℝ (Fin n)) : clampQ sx ε B (pos z) = clampQ sx ε B z := by
  ext i
  rw [clampQ_apply, clampQ_apply, pos_apply]
  have hl := lo_nonneg sx hε i
  rcases le_total (z i) 0 with h | h
  · rw [max_eq_right h]
    have h1 : min B 0 ≤ lo sx ε i := (min_le_right _ _).trans hl
    have h2 : min B (z i) ≤ lo sx ε i := (min_le_right _ _).trans (h.trans hl)
    rw [max_eq_left h1, max_eq_left h2]
  · rw [max_eq_left h]

lemma clampQ_eq {sx : Fin n → Bool} {ε B : ℝ} {z : EuclideanSpace ℝ (Fin n)}
    (hlo : ∀ i, lo sx ε i ≤ z i) (hzB : ∀ i, z i ≤ B) : clampQ sx ε B z = z := by
  ext i
  rw [clampQ_apply, min_eq_right (hzB i), max_eq_right (hlo i)]

lemma dist_clampQ_le (sx : Fin n → Bool) (ε B : ℝ) (y y' : EuclideanSpace ℝ (Fin n)) :
    dist (clampQ sx ε B y) (clampQ sx ε B y') ≤ dist y y' := by
  rw [EuclideanSpace.dist_eq, EuclideanSpace.dist_eq]
  apply Real.sqrt_le_sqrt
  apply Finset.sum_le_sum
  intro i _
  rw [Real.dist_eq, Real.dist_eq, clampQ_apply, clampQ_apply, max_comm (lo sx ε i),
    max_comm (lo sx ε i)]
  refine pow_le_pow_left₀ (abs_nonneg _) ((abs_max_sub_max_le_abs _ _ _).trans ?_) 2
  have := abs_min_sub_min_le_max B (y i) B (y' i)
  simpa using this

lemma convex_boxQ (sx : Fin n → Bool) (ε B : ℝ) : Convex ℝ (boxQ sx ε B) := by
  intro x hx y hy a b ha hb hab i
  simp only [PiLp.add_apply, PiLp.smul_apply, smul_eq_mul]
  have h3 : ∀ u : ℝ, a * u + b * u = u := fun u => by rw [← add_mul, hab, one_mul]
  constructor
  · have h1 := mul_le_mul_of_nonneg_left (hx i).1 ha
    have h2 := mul_le_mul_of_nonneg_left (hy i).1 hb
    have := h3 (lo sx ε i); linarith
  · have h1 := mul_le_mul_of_nonneg_left (hx i).2 ha
    have h2 := mul_le_mul_of_nonneg_left (hy i).2 hb
    have := h3 B; linarith

lemma isCompact_boxQ (sx : Fin n → Bool) {ε : ℝ} (hε : 0 ≤ ε) (B : ℝ) :
    IsCompact (boxQ sx ε B) := by
  apply Metric.isCompact_of_isClosed_isBounded
  · have : boxQ sx ε B = ⋂ i, ({z : EuclideanSpace ℝ (Fin n) | lo sx ε i ≤ z i} ∩
        {z | z i ≤ B}) := by
      ext z; simp [boxQ, forall_and]
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
    exact pow_le_pow_left₀ ((lo_nonneg sx hε i).trans (hz i).1) (hz i).2 2

lemma lipschitzOn_boxQ (sx : Fin n → Bool) (v : EuclideanSpace ℝ (Fin n) → EuclideanSpace ℝ (Fin n))
    {U : Set (EuclideanSpace ℝ (Fin n))} (hU : IsOpen U) (hv : ContDiffOn ℝ 1 v U)
    {ε : ℝ} (hε : 0 ≤ ε) (B : ℝ) (hbox : boxQ sx ε B ⊆ U) :
    ∃ L : ℝ≥0, LipschitzOnWith L v (boxQ sx ε B) := by
  have hDv : ContinuousOn (fderiv ℝ v) (boxQ sx ε B) :=
    (hv.continuousOn_fderiv_of_isOpen hU le_rfl).mono hbox
  obtain ⟨M, hM⟩ := (isCompact_boxQ sx hε B).exists_bound_of_continuousOn hDv
  refine ⟨⟨max M 0, le_max_right _ _⟩, ?_⟩
  refine (convex_boxQ sx ε B).lipschitzOnWith_of_nnnorm_hasFDerivWithin_le
    (f' := fderiv ℝ v) (fun z hz => ?_) (fun z hz => ?_)
  · exact ((hv.contDiffAt (hU.mem_nhds (hbox hz))).differentiableAt le_rfl).hasFDerivAt
      |>.hasFDerivWithinAt
  · rw [← NNReal.coe_le_coe, coe_nnnorm, NNReal.coe_mk]
    exact (hM z hz).trans (le_max_left _ _)

/-- **Existencia global con positividad estricta.** -/
theorem exists_global_solution_strict (sx : Fin n → Bool)
    (v : EuclideanSpace ℝ (Fin n) → EuclideanSpace ℝ (Fin n))
    {U : Set (EuclideanSpace ℝ (Fin n))} (hU : IsOpen U) (hv : ContDiffOn ℝ 1 v U)
    (hP : ∀ z, SPos sx z → z ∈ U)
    (hqp : ∀ z, SPos sx z → ∀ i, z i = 0 → 0 ≤ v z i)
    (hdecay : ∀ B : ℝ, ∃ C : ℝ, 0 ≤ C ∧ ∀ z, SPos sx z → (∀ j, z j ≤ B) →
      ∀ i, sx i = true → -C * z i ≤ v z i)
    (c : Fin n → ℝ) {cmin a b : ℝ} (hcmin : 0 < cmin) (hc : ∀ i, cmin ≤ c i)
    (ha : 0 ≤ a) (hb : 0 ≤ b)
    (hgrowth : ∀ z, SPos sx z → ∑ i, c i * v z i ≤ a + b * ∑ i, c i * z i)
    (x0 : EuclideanSpace ℝ (Fin n)) (hx0 : SPos sx x0) {T : ℝ} (hT : 0 ≤ T) :
    ∃ x : ℝ → EuclideanSpace ℝ (Fin n), x 0 = x0 ∧
      ∀ t ∈ Icc 0 T, HasDerivWithinAt x (v (x t)) (Icc 0 T) t ∧ SPos sx (x t) := by
  have hcpos : ∀ i, 0 < c i := fun i => hcmin.trans_le (hc i)
  set K' : ℝ := b + 1 with hK'
  have hK'pos : 0 < K' := by rw [hK']; linarith
  set φ0 : ℝ := ∑ i, c i * x0 i with hφ0
  have hφ0 : 0 ≤ φ0 := Finset.sum_nonneg fun i _ => mul_nonneg (hcpos i).le (hx0.1 i)
  set E1 := Real.exp (K' * T) with hE1
  have hE1' : 1 ≤ E1 := Real.one_le_exp (mul_nonneg hK'pos.le hT)
  set M : ℝ := φ0 * E1 + a / K' * (E1 - 1) with hM
  have hM0 : 0 ≤ M := add_nonneg (mul_nonneg hφ0 (by linarith))
    (mul_nonneg (div_nonneg ha hK'pos.le) (by linarith))
  set B : ℝ := M / cmin + 1 with hB
  have hB1 : 1 ≤ B := by rw [hB]; have := div_nonneg hM0 hcmin.le; linarith
  have hB0 : 0 ≤ B := by linarith
  -- constante de consumo en la caja [0, B]
  obtain ⟨C, hC0, hC⟩ := hdecay B
  -- mínimo de los datos iniciales de Σ
  obtain ⟨m0, hm0, hm01, hm0le⟩ : ∃ m0 : ℝ, 0 < m0 ∧ m0 ≤ 1 ∧
      ∀ i, sx i = true → m0 ≤ x0 i := by
    by_cases hs : (Finset.univ.filter fun i => sx i = true).Nonempty
    · obtain ⟨j, hj, hmin⟩ := Finset.exists_min_image _ (fun i => x0 i) hs
      refine ⟨min (x0 j) 1, lt_min (hx0.2 j (Finset.mem_filter.1 hj).2) one_pos,
        min_le_right _ _, fun i hi => (min_le_left _ _).trans
          (hmin i (Finset.mem_filter.2 ⟨Finset.mem_univ _, hi⟩))⟩
    · exact ⟨1, one_pos, le_rfl, fun i hi =>
        absurd ⟨i, Finset.mem_filter.2 ⟨Finset.mem_univ _, hi⟩⟩ hs⟩
  set K1 : ℝ := C + 1 with hK1
  have hK1pos : 0 < K1 := by rw [hK1]; linarith
  set g : ℝ → ℝ := fun t => m0 / 2 * Real.exp (-(K1 * t)) with hg
  set ε : ℝ := m0 / 2 * Real.exp (-(K1 * T)) with hε
  have hεpos : 0 < ε := mul_pos (half_pos hm0) (Real.exp_pos _)
  have hgε : ∀ t ∈ Icc 0 T, ε ≤ g t := fun t ht =>
    mul_le_mul_of_nonneg_left (Real.exp_le_exp.2 (by nlinarith [ht.2]))
      (half_pos hm0).le
  have hgm : ∀ t ∈ Icc 0 T, g t ≤ m0 / 2 := fun t ht => by
    have : Real.exp (-(K1 * t)) ≤ 1 := Real.exp_le_one_iff.2 (by nlinarith [ht.1])
    simpa [hg] using mul_le_mul_of_nonneg_left this (half_pos hm0).le
  have hεB : ε ≤ B := by
    have := hgm 0 ⟨le_rfl, hT⟩; have := hgε 0 ⟨le_rfl, hT⟩; linarith
  have hboxU : boxQ sx ε B ⊆ U := fun z hz => hP z (boxQ_sPos sx hεpos hz)
  obtain ⟨L, hL⟩ := lipschitzOn_boxQ sx v hU hv hεpos.le B hboxU
  -- campo truncado
  set w : EuclideanSpace ℝ (Fin n) → EuclideanSpace ℝ (Fin n) := fun z => v (clampQ sx ε B z)
    with hw
  have hwLip : LipschitzWith L w := LipschitzWith.of_dist_le_mul fun y y' => by
    have := hL.dist_le_mul _ (clampQ_mem sx hεpos.le hεB y) _ (clampQ_mem sx hεpos.le hεB y')
    exact this.trans (mul_le_mul_of_nonneg_left (dist_clampQ_le sx ε B y y') L.2)
  obtain ⟨α, hα0, hαsol⟩ := exists_solution_Icc (fun _ => w) L hT (fun _ _ => hwLip)
    (fun _ => continuousOn_const) x0
  have hα : ∀ t ∈ Icc 0 T, HasDerivWithinAt α (w (α t)) (Icc 0 T) t := hαsol
  have hcomp : ∀ i, ∀ t ∈ Icc 0 T,
      HasDerivWithinAt (fun t => α t i) (w (α t) i) (Icc 0 T) t := by
    intro i t ht
    have := (EuclideanSpace.proj i : EuclideanSpace ℝ (Fin n) →L[ℝ] ℝ).hasFDerivAt
      |>.comp_hasDerivWithinAt t (hα t ht)
    simpa using this
  have hIci : ∀ t ∈ Ico 0 T, Icc 0 T ∈ 𝓝[Ici t] t := fun t ht =>
    mem_of_superset (Icc_mem_nhdsGE ht.2) (Icc_subset_Icc ht.1 le_rfl)
  -- cota inferior de las especies de Σ (comparación con g)
  have hlow : ∀ i, sx i = true → ∀ t ∈ Icc 0 T, g t ≤ α t i := by
    intro i hi
    have key := image_le_of_deriv_right_lt_deriv_boundary' (a := 0) (b := T)
      (f := fun t => -α t i) (f' := fun t => -w (α t) i)
      (B := fun t => -g t) (B' := fun t => K1 * g t)
      (fun t ht => ((hcomp i t ht).neg).continuousWithinAt)
      (fun t ht => ((hcomp i t (Ico_subset_Icc_self ht)).neg).mono_of_mem_nhdsWithin
        (hIci t ht))
      (by
        show -α 0 i ≤ -(m0 / 2 * Real.exp (-(K1 * 0)))
        rw [hα0, mul_zero, neg_zero, Real.exp_zero, mul_one]
        have := hm0le i hi; linarith)
      (fun t _ => by
        have : Continuous fun t : ℝ => -(m0 / 2 * Real.exp (-(K1 * t))) := by fun_prop
        exact this.continuousWithinAt)
      (fun t _ => by
        have h1 : HasDerivAt (fun t : ℝ => -(K1 * t)) (-(K1 * 1)) t :=
          ((hasDerivAt_id t).const_mul K1).neg
        have h2 := (h1.exp.const_mul (m0 / 2)).neg
        have h3 : -(m0 / 2 * (Real.exp (-(K1 * t)) * -(K1 * 1))) = K1 * g t := by
          simp only [hg]; ring
        rw [h3] at h2
        exact h2.hasDerivWithinAt)
      (by
        intro t ht heq
        have ht' := Ico_subset_Icc_self ht
        have hαt : α t i = g t := by simp only at heq; linarith
        -- en ese instante el truncamiento no actúa sobre la componente i
        have hci : clampQ sx ε B (α t) i = g t := by
          rw [clampQ_apply, hαt, min_eq_right ((hgm t ht').trans (by linarith)),
            max_eq_right (by simp only [lo, hi, if_true]; exact hgε t ht')]
        have hd := hC (clampQ sx ε B (α t))
          (boxQ_sPos sx hεpos (clampQ_mem sx hεpos.le hεB _))
          (fun j => (clampQ_mem sx hεpos.le hεB _ j).2) i hi
        rw [hci] at hd
        have hgpos : 0 < g t := mul_pos (half_pos hm0) (Real.exp_pos _)
        show -w (α t) i < K1 * g t
        simp only [hw]
        rw [hK1]; nlinarith)
    intro t ht
    have := key ht
    simp only at this
    linarith
  have hlowε : ∀ i, sx i = true → ∀ t ∈ Icc 0 T, ε ≤ α t i := fun i hi t ht =>
    (hgε t ht).trans (hlow i hi t ht)
  -- positividad del sistema truncado
  have hnn : ∀ t ∈ Icc 0 T, Nonneg (α t) := by
    refine nonneg_core w α (K := 0) le_rfl hα (by rw [hα0]; exact hx0.1) ?_ ?_
    · intro t _
      have : w (pos (α t)) = w (α t) := by simp only [hw, clampQ_pos sx hεpos.le]
      rw [this, sub_self, norm_zero]; positivity
    · intro t ht i hi
      have hneg : α t i ≤ 0 := by
        have : max (α t i) 0 = 0 := hi
        rw [max_eq_right_iff] at this; exact this
      cases hsi : sx i with
      | true => have := hlowε i hsi t ht; linarith
      | false =>
        have hy : clampQ sx ε B (pos (α t)) i = 0 := by
          rw [clampQ_apply, hi, min_eq_right hB0]; simp [lo, hsi]
        exact hqp _ (boxQ_sPos sx hεpos (clampQ_mem sx hεpos.le hεB _)) i hy
  have hlo : ∀ t ∈ Icc 0 T, ∀ i, lo sx ε i ≤ α t i := by
    intro t ht i
    unfold lo
    split_ifs with hsi
    · exact hlowε i hsi t ht
    · exact hnn t ht i
  -- Grönwall sobre φ = Σ cᵢ αᵢ
  set φ : ℝ → ℝ := fun t => ∑ i, c i * α t i with hφdef
  set φ' : ℝ → ℝ := fun t => ∑ i, c i * w (α t) i with hφ'def
  have hφd : ∀ t ∈ Icc 0 T, HasDerivWithinAt φ (φ' t) (Icc 0 T) t := by
    intro t ht
    apply HasDerivWithinAt.fun_sum
    intro i _
    exact (hcomp i t ht).const_mul (c i)
  have hφc : ContinuousOn φ (Icc 0 T) := fun t ht => (hφd t ht).continuousWithinAt
  have hφ0' : ∀ t ∈ Icc 0 T, 0 ≤ φ t := fun t ht =>
    Finset.sum_nonneg fun i _ => mul_nonneg (hcpos i).le (hnn t ht i)
  have hbound : ∀ t ∈ Icc 0 T, φ' t ≤ K' * φ t + a := by
    intro t ht
    have h1 := hgrowth (clampQ sx ε B (α t))
      (boxQ_sPos sx hεpos (clampQ_mem sx hεpos.le hεB _))
    have h2 : ∑ i, c i * clampQ sx ε B (α t) i ≤ φ t := by
      apply Finset.sum_le_sum
      intro i _
      apply mul_le_mul_of_nonneg_left _ (hcpos i).le
      rw [clampQ_apply]
      exact max_le (hlo t ht i) (min_le_right _ _)
    have h3 := hφ0' t ht
    have h4 : 0 ≤ ∑ i, c i * clampQ sx ε B (α t) i :=
      Finset.sum_nonneg fun i _ => mul_nonneg (hcpos i).le
        ((boxQ_sPos sx hεpos (clampQ_mem sx hεpos.le hεB _)).1 i)
    show ∑ i, c i * v (clampQ sx ε B (α t)) i ≤ K' * φ t + a
    nlinarith [mul_le_mul_of_nonneg_left h2 hb]
  have gron := le_gronwallBound_of_liminf_deriv_right_le (f := φ) (f' := φ')
    (δ := φ0) (K := K') (ε := a) hφc
    (fun t ht r hr => ((hφd t (Ico_subset_Icc_self ht)).mono_of_mem_nhdsWithin
      (hIci t ht)).liminf_right_slope_le hr)
    (by show ∑ i, c i * α 0 i ≤ φ0; rw [hα0])
    (fun t ht => hbound t (Ico_subset_Icc_self ht))
  have hφM : ∀ t ∈ Icc 0 T, φ t ≤ M := by
    intro t ht
    have g' := gron t ht
    rw [sub_zero, gronwallBound_of_K_ne_0 hK'pos.ne'] at g'
    simp only at g'
    have he : Real.exp (K' * t) ≤ E1 :=
      Real.exp_le_exp.2 (mul_le_mul_of_nonneg_left ht.2 hK'pos.le)
    have h1 := mul_le_mul_of_nonneg_left he hφ0
    have h2 := mul_le_mul_of_nonneg_left (sub_le_sub_right he 1) (div_nonneg ha hK'pos.le)
    rw [hM]; linarith
  have hbelow : ∀ t ∈ Icc 0 T, ∀ i, α t i ≤ B := by
    intro t ht i
    have h1 : c i * α t i ≤ φ t :=
      Finset.single_le_sum (f := fun j => c j * α t j)
        (fun j _ => mul_nonneg (hcpos j).le (hnn t ht j)) (Finset.mem_univ i)
    have h2 : cmin * α t i ≤ c i * α t i := mul_le_mul_of_nonneg_right (hc i) (hnn t ht i)
    have h3 : α t i ≤ M / cmin := by
      rw [le_div_iff₀ hcmin]; linarith [hφM t ht]
    rw [hB]; linarith
  refine ⟨α, hα0, fun t ht => ⟨?_, hnn t ht, fun j hj => hεpos.trans_le (hlowε j hj t ht)⟩⟩
  have : w (α t) = v (α t) := by
    simp only [hw]; rw [clampQ_eq (hlo t ht) (hbelow t ht)]
  rw [← this]; exact hα t ht

end StrictExistence

#print axioms StrictExistence.exists_global_solution_strict
