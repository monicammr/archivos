import KineticRegularity

/-!
# Positividad: las concentraciones que empiezan `≥ 0` siguen `≥ 0`

Hipótesis de **cuasi-positividad** (estándar en redes de reacciones): en todo punto `y ≥ 0` con
`yᵢ = 0`, la velocidad `vᵢ(y)` es `≥ 0` (una especie ausente no puede consumirse).

* `nonneg_core`: versión cuantitativa en un intervalo, con una condición de Lipschitz entre `x`
  y su parte positiva `x⁺`; prueba por Grönwall sobre `ψ = Σᵢ min(xᵢ, 0)²` (`ψ' ≤ 2Kψ`, `ψ(0) = 0`).
* `nonneg_of_quasiPositive`: si `v` es C¹ en un abierto `U` que contiene los puntos `≥ 0` de la
  trayectoria, la trayectoria permanece en el ortante `≥ 0` (inducción continua; sólo usa
  Lipschitz local).
* `kinetic_nonneg`: para modelos cinéticos (`KExpr`) cuyo dominio contiene el ortante
  `≥ 0` (p. ej. Michaelis–Menten y Hill con `K > 0`), la trayectoria es `≥ 0` **y por tanto queda
  en el dominio**.
* `kinetic_hasFDerivAt_of_nonneg`: el teorema de diferenciabilidad para modelos cinéticos sin la
  hipótesis "la trayectoria nominal está en el dominio": basta un dato inicial `≥ 0`.
-/

open Set Filter Topology Metric Asymptotics

namespace PositivityInvariance

variable {n : ℕ}

/-- Vector con todas las componentes `≥ 0`. -/
def Nonneg (y : EuclideanSpace ℝ (Fin n)) : Prop := ∀ i, 0 ≤ y i

/-- Parte positiva componente a componente. -/
noncomputable def pos (y : EuclideanSpace ℝ (Fin n)) : EuclideanSpace ℝ (Fin n) :=
  WithLp.toLp 2 (fun i => max (y i) 0)

lemma pos_apply (y : EuclideanSpace ℝ (Fin n)) (i : Fin n) : pos y i = max (y i) 0 := rfl

lemma pos_nonneg (y : EuclideanSpace ℝ (Fin n)) : Nonneg (pos y) := fun _ => le_max_right _ _

lemma pos_eq_self {y : EuclideanSpace ℝ (Fin n)} (hy : Nonneg y) : pos y = y := by
  ext i; rw [pos_apply, max_eq_left (hy i)]

lemma dist_pos_le (y y' : EuclideanSpace ℝ (Fin n)) : dist (pos y) (pos y') ≤ dist y y' := by
  rw [EuclideanSpace.dist_eq, EuclideanSpace.dist_eq]
  apply Real.sqrt_le_sqrt
  apply Finset.sum_le_sum
  intro i _
  rw [Real.dist_eq, Real.dist_eq, pos_apply, pos_apply]
  exact pow_le_pow_left₀ (abs_nonneg _) (abs_max_sub_max_le_abs _ _ _) 2

lemma sub_pos_apply (y : EuclideanSpace ℝ (Fin n)) (i : Fin n) :
    (y - pos y) i = min (y i) 0 := by
  rw [PiLp.sub_apply, pos_apply]
  rcases le_total (y i) 0 with h | h
  · rw [max_eq_right h, min_eq_left h, sub_zero]
  · rw [max_eq_left h, min_eq_right h, sub_self]

lemma pos_apply_eq_zero {y : EuclideanSpace ℝ (Fin n)} {i : Fin n} (h : y i < 0) :
    pos y i = 0 := by rw [pos_apply, max_eq_right h.le]

lemma isClosed_nonneg : IsClosed {y : EuclideanSpace ℝ (Fin n) | Nonneg y} := by
  have : {y : EuclideanSpace ℝ (Fin n) | Nonneg y} = ⋂ i, {y | 0 ≤ y i} := by
    ext y; simp [Nonneg]
  rw [this]
  exact isClosed_iInter fun i =>
    isClosed_le continuous_const (EuclideanSpace.proj i : EuclideanSpace ℝ (Fin n) →L[ℝ] ℝ).continuous

/-- `a ↦ min(a, 0)²` es derivable con derivada `2 min(a, 0)`. -/
lemma hasDerivAt_negSq (a : ℝ) : HasDerivAt (fun a : ℝ => (min a 0) ^ 2) (2 * min a 0) a := by
  rcases lt_trichotomy a 0 with h | h | h
  · have heq : (fun a : ℝ => (min a 0) ^ 2) =ᶠ[𝓝 a] fun a => a ^ 2 := by
      filter_upwards [Iio_mem_nhds h] with y hy
      rw [min_eq_left (le_of_lt hy)]
    have hd := (hasDerivAt_pow 2 a).congr_of_eventuallyEq heq
    rw [min_eq_left h.le]
    convert hd using 1
    norm_num
  · subst h
    have key : (fun y : ℝ => (min y 0) ^ 2) =o[𝓝 0] fun y => y := by
      refine (IsBigO.of_bound 1 (Eventually.of_forall fun y => ?_)).trans_isLittleO
        (isLittleO_pow_id one_lt_two)
      rw [one_mul, Real.norm_eq_abs, Real.norm_eq_abs, abs_of_nonneg (sq_nonneg _),
        abs_of_nonneg (sq_nonneg _)]
      rcases le_total y 0 with hy | hy
      · rw [min_eq_left hy]
      · rw [min_eq_right hy]; nlinarith [sq_nonneg y]
    rw [hasDerivAt_iff_isLittleO]
    refine key.congr' (Eventually.of_forall fun y => ?_) (Eventually.of_forall fun y => ?_)
    · simp
    · simp
  · have heq : (fun a : ℝ => (min a 0) ^ 2) =ᶠ[𝓝 a] fun _ => (0 : ℝ) := by
      filter_upwards [Ioi_mem_nhds h] with y hy
      rw [min_eq_right hy.le]; norm_num
    have hd := (hasDerivAt_const a (0 : ℝ)).congr_of_eventuallyEq heq
    rw [min_eq_right h.le, mul_zero]
    exact hd

/-- **Núcleo (Grönwall).** En `[a, b]`, si `x' = v(x)`, `x(a) ≥ 0`,
`‖v(x) − v(x⁺)‖ ≤ K ‖x − x⁺‖` a lo largo de la trayectoria y `v` es cuasi-positiva en `x⁺`,
entonces `x(t) ≥ 0` en `[a, b]`. -/
theorem nonneg_core (v : EuclideanSpace ℝ (Fin n) → EuclideanSpace ℝ (Fin n))
    (x : ℝ → EuclideanSpace ℝ (Fin n)) {a b K : ℝ} (hK : 0 ≤ K)
    (hx : ∀ t ∈ Icc a b, HasDerivWithinAt x (v (x t)) (Icc a b) t)
    (hxa : Nonneg (x a))
    (hLip : ∀ t ∈ Icc a b, ‖v (x t) - v (pos (x t))‖ ≤ K * ‖x t - pos (x t)‖)
    (hqp : ∀ t ∈ Icc a b, ∀ i, pos (x t) i = 0 → 0 ≤ v (pos (x t)) i) :
    ∀ t ∈ Icc a b, Nonneg (x t) := by
  set ψ : ℝ → ℝ := fun t => ∑ i, (min (x t i) 0) ^ 2 with hψdef
  set ψ' : ℝ → ℝ := fun t => ∑ i, 2 * min (x t i) 0 * v (x t) i with hψ'def
  have hψ : ∀ t ∈ Icc a b, HasDerivWithinAt ψ (ψ' t) (Icc a b) t := by
    intro t ht
    apply HasDerivWithinAt.fun_sum
    intro i _
    have hxi : HasDerivWithinAt (fun t => x t i) (v (x t) i) (Icc a b) t := by
      have := (EuclideanSpace.proj i : EuclideanSpace ℝ (Fin n) →L[ℝ] ℝ).hasFDerivAt
        |>.comp_hasDerivWithinAt t (hx t ht)
      simpa using this
    exact (hasDerivAt_negSq (x t i)).comp_hasDerivWithinAt t hxi
  have hψc : ContinuousOn ψ (Icc a b) := fun t ht => (hψ t ht).continuousWithinAt
  -- ψ = ‖x − x⁺‖²
  have hψnorm : ∀ t, ψ t = ‖x t - pos (x t)‖ ^ 2 := by
    intro t
    rw [EuclideanSpace.norm_sq_eq]
    apply Finset.sum_congr rfl
    intro i _
    rw [Real.norm_eq_abs, sq_abs, sub_pos_apply]
  have hψ0 : ∀ t, 0 ≤ ψ t := fun t => by rw [hψnorm]; positivity
  -- ψ' ≤ 2K ψ
  have hbound : ∀ t ∈ Icc a b, ψ' t ≤ (2 * K) * ψ t := by
    intro t ht
    set m : Fin n → ℝ := fun i => min (x t i) 0 with hm
    set d : Fin n → ℝ := fun i => v (x t) i - v (pos (x t)) i with hd
    set w : Fin n → ℝ := fun i => v (pos (x t)) i with hw
    have hsplit : ψ' t = 2 * ∑ i, m i * d i + 2 * ∑ i, m i * w i := by
      simp only [hψ'def, hm, hd, hw, Finset.mul_sum, ← Finset.sum_add_distrib]
      apply Finset.sum_congr rfl; intro i _; ring
    have hneg : ∑ i, m i * w i ≤ 0 := by
      apply Finset.sum_nonpos
      intro i _
      by_cases hxi : x t i < 0
      · have hwi : 0 ≤ w i := hqp t ht i (pos_apply_eq_zero hxi)
        have hmi : m i ≤ 0 := min_le_right _ _
        nlinarith
      · push_neg at hxi
        simp [hm, min_eq_right hxi]
    have hmsq : ∑ i, m i ^ 2 = ψ t := rfl
    have hdsq : ∑ i, d i ^ 2 = ‖v (x t) - v (pos (x t))‖ ^ 2 := by
      rw [EuclideanSpace.norm_sq_eq]
      apply Finset.sum_congr rfl
      intro i _
      rw [Real.norm_eq_abs, sq_abs, PiLp.sub_apply]
    have hCS := Finset.sum_mul_sq_le_sq_mul_sq Finset.univ m d
    have hL2 : ‖v (x t) - v (pos (x t))‖ ^ 2 ≤ K ^ 2 * ψ t := by
      rw [hψnorm, ← mul_pow]
      exact pow_le_pow_left₀ (norm_nonneg _) (hLip t ht) 2
    have hsq : (∑ i, m i * d i) ^ 2 ≤ (K * ψ t) ^ 2 := by
      rw [hmsq, hdsq] at hCS
      calc (∑ i, m i * d i) ^ 2 ≤ ψ t * ‖v (x t) - v (pos (x t))‖ ^ 2 := hCS
        _ ≤ ψ t * (K ^ 2 * ψ t) := mul_le_mul_of_nonneg_left hL2 (hψ0 t)
        _ = (K * ψ t) ^ 2 := by ring
    have hmd : ∑ i, m i * d i ≤ K * ψ t :=
      (abs_le_of_sq_le_sq' hsq (mul_nonneg hK (hψ0 t))).2
    rw [hsplit]; linarith
  -- Grönwall con δ = ε = 0
  have hIci : ∀ t ∈ Ico a b, Icc a b ∈ 𝓝[Ici t] t := fun t ht =>
    mem_of_superset (Icc_mem_nhdsGE ht.2) (Icc_subset_Icc ht.1 le_rfl)
  have hψa : ψ a ≤ 0 := by
    apply le_of_eq
    apply Finset.sum_eq_zero
    intro i _
    rw [min_eq_right (hxa i)]; norm_num
  have gron := le_gronwallBound_of_liminf_deriv_right_le (f := ψ) (f' := ψ')
    (δ := 0) (K := 2 * K) (ε := 0) hψc
    (fun t ht r hr => ((hψ t (Ico_subset_Icc_self ht)).mono_of_mem_nhdsWithin
      (hIci t ht)).liminf_right_slope_le hr)
    hψa (fun t ht => by rw [add_zero]; exact hbound t (Ico_subset_Icc_self ht))
  intro t ht i
  have h1 : ψ t ≤ 0 := by
    have := gron t ht; rwa [gronwallBound_ε0_δ0] at this
  have h2 : (min (x t i) 0) ^ 2 ≤ ψ t :=
    Finset.single_le_sum (f := fun i => (min (x t i) 0) ^ 2) (fun j _ => sq_nonneg _)
      (Finset.mem_univ i)
  have h3 : min (x t i) 0 = 0 := by
    have : (min (x t i) 0) ^ 2 = 0 := le_antisymm (h2.trans h1) (sq_nonneg _)
    exact pow_eq_zero_iff two_ne_zero |>.1 this
  by_contra hlt
  push_neg at hlt
  rw [min_eq_left hlt.le] at h3
  linarith

/-- **Invariancia del ortante `≥ 0`.** Si `v` es C¹ en un abierto `U`, cuasi-positiva en los
puntos `≥ 0` de `U`, `x' = v(x)` en `[0, T]`, `x(0) ≥ 0` y todo punto `≥ 0` de la trayectoria
está en `U`, entonces `x(t) ≥ 0` en `[0, T]`. -/
theorem nonneg_of_quasiPositive (v : EuclideanSpace ℝ (Fin n) → EuclideanSpace ℝ (Fin n))
    {U : Set (EuclideanSpace ℝ (Fin n))} (hU : IsOpen U) (hv : ContDiffOn ℝ 1 v U)
    (hqp : ∀ y ∈ U, Nonneg y → ∀ i, y i = 0 → 0 ≤ v y i)
    {T : ℝ} (x : ℝ → EuclideanSpace ℝ (Fin n))
    (hx : ∀ t ∈ Icc 0 T, HasDerivWithinAt x (v (x t)) (Icc 0 T) t)
    (hxU : ∀ t ∈ Icc 0 T, Nonneg (x t) → x t ∈ U) (hx0 : Nonneg (x 0)) :
    ∀ t ∈ Icc 0 T, Nonneg (x t) := by
  have hxc : ContinuousOn x (Icc 0 T) := fun t ht => (hx t ht).continuousWithinAt
  set s : Set ℝ := {t | Nonneg (x t)} with hs
  have hclosed : IsClosed (s ∩ Icc 0 T) := by
    have := hxc.preimage_isClosed_of_isClosed isClosed_Icc isClosed_nonneg
    rwa [inter_comm] at this
  have hsub : Icc 0 T ⊆ s := by
    refine hclosed.Icc_subset_of_forall_mem_nhdsWithin hx0 ?_
    rintro t ⟨hts, htT⟩
    have htI : t ∈ Icc 0 T := Ico_subset_Icc_self htT
    have hyU : x t ∈ U := hxU t htI hts
    -- Lipschitz local de `v` alrededor de `x t`
    obtain ⟨K, W, hW, hLipW⟩ := (hv.contDiffAt (hU.mem_nhds hyU)).exists_lipschitzOnWith
    obtain ⟨r, hr, hball⟩ := Metric.mem_nhds_iff.1 (inter_mem hW (hU.mem_nhds hyU))
    -- continuidad de `x` en `t`
    obtain ⟨δ, hδ, hδx⟩ := Metric.continuousWithinAt_iff.1 (hxc t htI) r hr
    set b := min (t + δ / 2) T with hb
    have htb : t < b := lt_min (by linarith) htT.2
    have hbT : b ≤ T := min_le_right _ _
    have hIsub : Icc t b ⊆ Icc 0 T := Icc_subset_Icc htI.1 hbT
    have hnear : ∀ u ∈ Icc t b, dist (x u) (x t) < r := by
      intro u hu
      apply hδx (hIsub hu)
      rw [Real.dist_eq, abs_of_nonneg (by linarith [hu.1])]
      have : u ≤ t + δ / 2 := hu.2.trans (min_le_left _ _)
      linarith
    have hposnear : ∀ u ∈ Icc t b, dist (pos (x u)) (x t) < r := by
      intro u hu
      have := dist_pos_le (x u) (x t)
      rw [pos_eq_self hts] at this
      exact this.trans_lt (hnear u hu)
    have hcore := nonneg_core v x (a := t) (b := b) K.2
      (fun u hu => (hx u (hIsub hu)).mono hIsub) hts
      (fun u hu => by
        have h1 := hLipW.dist_le_mul (x u) (hball (mem_ball.2 (hnear u hu))).1
          (pos (x u)) (hball (mem_ball.2 (hposnear u hu))).1
        rwa [dist_eq_norm, dist_eq_norm] at h1)
      (fun u hu i hi => hqp _ (hball (mem_ball.2 (hposnear u hu))).2 (pos_nonneg _) i hi)
    exact mem_of_superset (Ioo_mem_nhdsGT htb) fun u hu => hcore u (Ioo_subset_Icc_self hu)
  exact fun t ht => hsub ht

open KineticRegularity KExpr

/-- **Modelos cinéticos: positividad y permanencia en el dominio.** Si el dominio del modelo
contiene el ortante `≥ 0` (para el `θ` dado) y el modelo es cuasi-positivo, toda solución con dato
inicial `≥ 0` es `≥ 0` y permanece en el dominio. -/
theorem kinetic_nonneg {p : ℕ} (F : Fin n → KExpr n p) (θ : EuclideanSpace ℝ (Fin p))
    (horth : ∀ y : EuclideanSpace ℝ (Fin n), Nonneg y → (y, θ) ∈ domain F)
    (hqp : ∀ y : EuclideanSpace ℝ (Fin n), Nonneg y → ∀ i, y i = 0 → 0 ≤ field F y θ i)
    {T : ℝ} (x : ℝ → EuclideanSpace ℝ (Fin n))
    (hx : ∀ t ∈ Icc 0 T, HasDerivWithinAt x (field F (x t) θ) (Icc 0 T) t)
    (hx0 : Nonneg (x 0)) :
    ∀ t ∈ Icc 0 T, Nonneg (x t) ∧ (x t, θ) ∈ domain F := by
  set U : Set (EuclideanSpace ℝ (Fin n)) := (fun y => (y, θ)) ⁻¹' domain F with hUdef
  have hcont : Continuous fun y : EuclideanSpace ℝ (Fin n) => (y, θ) :=
    continuous_id.prodMk continuous_const
  have hU : IsOpen U := (isOpen_domain F).preimage hcont
  have hv : ContDiffOn ℝ 1 (fun y => field F y θ) U :=
    (contDiffOn_field F).comp (contDiff_id.prodMk contDiff_const).contDiffOn
      (fun y hy => hy)
  have hnn := nonneg_of_quasiPositive (fun y => field F y θ) hU hv
    (fun y _ hy i hi => hqp y hy i hi) x hx (fun t _ ht => horth (x t) ht) hx0
  exact fun t ht => ⟨hnn t ht, horth (x t) (hnn t ht)⟩

/-- **Diferenciabilidad para modelos cinéticos con dato inicial `≥ 0`.** Igual que
`kinetic_hasFDerivAt`, pero la hipótesis "la trayectoria nominal está en el dominio" se sustituye
por: el dominio contiene el ortante `≥ 0`, el modelo es cuasi-positivo y `x₀(0) ≥ 0`. -/
theorem kinetic_hasFDerivAt_of_nonneg {p : ℕ} (F : Fin n → KExpr n p)
    {T : ℝ} (hT : 0 ≤ T) (x₀ : ℝ → EuclideanSpace ℝ (Fin n)) (θ₀ : EuclideanSpace ℝ (Fin p))
    (horth : ∀ y : EuclideanSpace ℝ (Fin n), Nonneg y → (y, θ₀) ∈ domain F)
    (hqp : ∀ y : EuclideanSpace ℝ (Fin n), Nonneg y → ∀ i, y i = 0 → 0 ≤ field F y θ₀ i)
    (hx₀ : ∀ t ∈ Icc 0 T, HasDerivWithinAt x₀ (field F (x₀ t) θ₀) (Icc 0 T) t)
    (hpos0 : Nonneg (x₀ 0))
    (x0 : EuclideanSpace ℝ (Fin p) → EuclideanSpace ℝ (Fin n))
    (D0 : EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin n))
    (hx0 : HasFDerivAt x0 D0 θ₀) (hx00 : x0 θ₀ = x₀ 0) :
    ∃ x : EuclideanSpace ℝ (Fin p) → ℝ → EuclideanSpace ℝ (Fin n), x θ₀ = x₀ ∧
      (∀ᶠ θ in 𝓝 θ₀, x θ 0 = x0 θ ∧
        ∀ t ∈ Icc 0 T, HasDerivWithinAt (x θ) (field F (x θ t) θ) (Icc 0 T) t) ∧
      ∃ S : ℝ → (EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin n)), S 0 = D0 ∧
        ∀ t ∈ Icc 0 T, HasFDerivAt (fun θ => x θ t) (S t) θ₀ := by
  have hdom : ∀ t ∈ Icc 0 T, (x₀ t, θ₀) ∈ domain F := fun t ht =>
    (kinetic_nonneg F θ₀ horth hqp x₀ hx₀ hpos0 t ht).2
  obtain ⟨x, h1, h2, S, h3, -, h4⟩ := kinetic_hasFDerivAt F hT x₀ θ₀ hx₀ hdom x0 D0 hx0 hx00
  exact ⟨x, h1, h2, S, h3, h4⟩

/-! ### Ejemplo: producción constante y degradación de Michaelis–Menten

`ẋ = θ₀ − θ₁ x / (θ₂ + x)`. Con `θ₀ ≥ 0` y `θ₂ > 0` se cumplen las dos hipótesis
(`horth` y `hqp`), luego la concentración es `≥ 0` y la trayectoria está en el dominio. -/

/-- El modelo de ejemplo. -/
def exampleModel : Fin 1 → KExpr 1 3 := fun _ => sub (par 0) (mm (par 1) (par 2) (var 0))

theorem exampleModel_orth (θ : EuclideanSpace ℝ (Fin 3)) (h2 : 0 < θ 2)
    (y : EuclideanSpace ℝ (Fin 1)) (hy : Nonneg y) : (y, θ) ∈ domain exampleModel := by
  intro i
  exact ⟨trivial, ok_mm trivial trivial trivial h2 (hy 0)⟩

theorem exampleModel_qp (θ : EuclideanSpace ℝ (Fin 3)) (h0 : 0 ≤ θ 0)
    (y : EuclideanSpace ℝ (Fin 1)) (_ : Nonneg y) (i : Fin 1) (hi : y i = 0) :
    0 ≤ field exampleModel y θ i := by
  have hi0 : y 0 = 0 := by rw [← Fin.fin_one_eq_zero i]; exact hi
  show 0 ≤ θ 0 - θ 1 * y 0 / (θ 2 + y 0)
  rw [hi0, mul_zero, zero_div, sub_zero]
  exact h0

/-- En el ejemplo, toda solución con `x(0) ≥ 0` es `≥ 0` y permanece en el dominio. -/
theorem exampleModel_nonneg (θ : EuclideanSpace ℝ (Fin 3)) (h0 : 0 ≤ θ 0) (h2 : 0 < θ 2)
    {T : ℝ} (x : ℝ → EuclideanSpace ℝ (Fin 1))
    (hx : ∀ t ∈ Icc 0 T, HasDerivWithinAt x (field exampleModel (x t) θ) (Icc 0 T) t)
    (hx0 : Nonneg (x 0)) :
    ∀ t ∈ Icc 0 T, Nonneg (x t) ∧ (x t, θ) ∈ domain exampleModel :=
  kinetic_nonneg exampleModel θ (exampleModel_orth θ h2) (exampleModel_qp θ h0) x hx hx0

end PositivityInvariance

#print axioms PositivityInvariance.nonneg_of_quasiPositive
#print axioms PositivityInvariance.kinetic_nonneg
#print axioms PositivityInvariance.kinetic_hasFDerivAt_of_nonneg
#print axioms PositivityInvariance.exampleModel_nonneg
