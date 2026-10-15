import ParamDiffODE

/-!
# Existencia de soluciones para parámetros cercanos (se elimina la hipótesis `hsol`)

`hasFDerivAt_solution_param_init` supone que las soluciones existen en `[0, T]` para todo `θ`
cerca de `θ₀`. Aquí se **demuestra** esa hipótesis a partir de la existencia de la sola
trayectoria nominal `x₀` (la que se integra numéricamente en `θ₀`):

* `exists_solutions_near`: si `f` es C¹ en un abierto `U` que contiene la trayectoria nominal,
  y el dato inicial `x0 θ` es continuo en `θ₀`, existe una familia `x θ` de soluciones en
  `[0, T]` para todo `θ` cerca de `θ₀`, con `x θ₀ = x₀` y `(x θ t, θ) ∈ U`.
* `hasFDerivAt_of_nominal_solution`: combinando con `hasFDerivAt_solution_param_init`, la
  trayectoria es diferenciable respecto a `θ` en `θ₀` **sin suponer nada sobre `θ ≠ θ₀`**.

Idea de la prueba: se trunca el campo a un tubo alrededor de `x₀` con un "clamp" coordenada a
coordenada (1-Lipschitz), lo que da un campo globalmente Lipschitz; `exists_solution_Icc` da una
solución global del campo truncado; Grönwall muestra que, si `θ` está cerca de `θ₀`, esa solución
nunca sale de la zona donde el truncamiento es la identidad, luego resuelve la EDO original.
-/

open Set Filter Topology Metric NNReal ODEParamDiff

namespace LocalExistence

section Clamp

variable {n : ℕ}

/-- Truncamiento coordenada a coordenada a la caja `[-c, c]ⁿ`. -/
noncomputable def clampE (c : ℝ) (y : EuclideanSpace ℝ (Fin n)) : EuclideanSpace ℝ (Fin n) :=
  WithLp.toLp 2 (fun i => max (-c) (min c (y i)))

lemma clampE_apply (c : ℝ) (y : EuclideanSpace ℝ (Fin n)) (i : Fin n) :
    clampE c y i = max (-c) (min c (y i)) := rfl

lemma abs_clamp_sub_le (c a b : ℝ) :
    |max (-c) (min c a) - max (-c) (min c b)| ≤ |a - b| := by
  rw [max_comm (-c), max_comm (-c)]
  refine (abs_max_sub_max_le_abs _ _ _).trans ?_
  have := abs_min_sub_min_le_max c a c b
  simpa using this

lemma dist_clampE_le (c : ℝ) (y y' : EuclideanSpace ℝ (Fin n)) :
    dist (clampE c y) (clampE c y') ≤ dist y y' := by
  rw [EuclideanSpace.dist_eq, EuclideanSpace.dist_eq]
  apply Real.sqrt_le_sqrt
  apply Finset.sum_le_sum
  intro i _
  rw [Real.dist_eq, Real.dist_eq, clampE_apply, clampE_apply]
  exact pow_le_pow_left₀ (abs_nonneg _) (abs_clamp_sub_le c _ _) 2

lemma lipschitz_clampE (c : ℝ) : LipschitzWith 1 (clampE (n := n) c) :=
  LipschitzWith.of_dist_le_mul fun y y' => by
    simpa using dist_clampE_le c y y'

/-- El truncamiento es la identidad en la bola de radio `c`. -/
lemma clampE_eq {c : ℝ} {y : EuclideanSpace ℝ (Fin n)} (hy : ‖y‖ ≤ c) : clampE c y = y := by
  ext i
  rw [clampE_apply]
  have h := (PiLp.norm_apply_le y i).trans hy
  rw [Real.norm_eq_abs] at h
  obtain ⟨h1, h2⟩ := abs_le.1 h
  rw [min_eq_right h2, max_eq_right h1]

lemma clampE_zero {c : ℝ} (hc : 0 ≤ c) : clampE c (0 : EuclideanSpace ℝ (Fin n)) = 0 :=
  clampE_eq (by rw [norm_zero]; exact hc)

/-- La imagen del truncamiento está en la bola de radio `(n + 1) c`. -/
lemma norm_clampE_le {c : ℝ} (hc : 0 ≤ c) (y : EuclideanSpace ℝ (Fin n)) :
    ‖clampE c y‖ ≤ (n + 1) * c := by
  rw [EuclideanSpace.norm_eq]
  have hi : ∀ i, ‖clampE c y i‖ ^ 2 ≤ c ^ 2 := by
    intro i
    rw [Real.norm_eq_abs, clampE_apply]
    apply pow_le_pow_left₀ (abs_nonneg _) _ 2
    exact abs_le.2 ⟨le_max_left _ _, max_le (by linarith) (min_le_left _ _)⟩
  have hsum : ∑ i, ‖clampE c y i‖ ^ 2 ≤ ((n + 1) * c) ^ 2 := by
    calc ∑ i, ‖clampE c y i‖ ^ 2 ≤ ∑ _i : Fin n, c ^ 2 := Finset.sum_le_sum fun i _ => hi i
      _ = n * c ^ 2 := by simp [Finset.sum_const, Finset.card_univ]
      _ ≤ ((n + 1) * c) ^ 2 := by
          have hn : (0 : ℝ) ≤ n := Nat.cast_nonneg n
          nlinarith [sq_nonneg c, mul_nonneg hn (sq_nonneg c)]
  calc Real.sqrt (∑ i, ‖clampE c y i‖ ^ 2) ≤ Real.sqrt (((n + 1) * c) ^ 2) :=
        Real.sqrt_le_sqrt hsum
    _ = (n + 1) * c := Real.sqrt_sq (by positivity)

end Clamp

variable {n : ℕ} {P : Type*} [NormedAddCommGroup P] [NormedSpace ℝ P] [FiniteDimensional ℝ P]

set_option maxHeartbeats 2000000 in
/-- **Existencia de soluciones para `θ` cerca de `θ₀`.** Si `f` es C¹ en el abierto `U`, `x₀`
resuelve `ẋ = f(x, θ₀)` en `[0, T]` con `(x₀ t, θ₀) ∈ U`, y el dato inicial `x0 θ` es continuo
en `θ₀` con `x0 θ₀ = x₀ 0`, entonces existe una familia `x θ` con `x θ₀ = x₀` que, para todo
`θ` cerca de `θ₀`, resuelve `ẋ = f(x, θ)` en `[0, T]`, con `x θ 0 = x0 θ` y `(x θ t, θ) ∈ U`. -/
theorem exists_solutions_near
    (f : EuclideanSpace ℝ (Fin n) → P → EuclideanSpace ℝ (Fin n))
    {U : Set (EuclideanSpace ℝ (Fin n) × P)} (hU : IsOpen U)
    (hf : ContDiffOn ℝ 1 (fun z : EuclideanSpace ℝ (Fin n) × P => f z.1 z.2) U)
    {T : ℝ} (hT : 0 ≤ T) (x₀ : ℝ → EuclideanSpace ℝ (Fin n)) (θ₀ : P)
    (hx₀ : ∀ t ∈ Icc 0 T, HasDerivWithinAt x₀ (f (x₀ t) θ₀) (Icc 0 T) t)
    (hγU : ∀ t ∈ Icc 0 T, (x₀ t, θ₀) ∈ U)
    (x0 : P → EuclideanSpace ℝ (Fin n)) (hx0c : ContinuousAt x0 θ₀) (hx00 : x0 θ₀ = x₀ 0) :
    ∃ x : P → ℝ → EuclideanSpace ℝ (Fin n), x θ₀ = x₀ ∧
      ∀ᶠ θ in 𝓝 θ₀, x θ 0 = x0 θ ∧ ∀ t ∈ Icc 0 T,
        HasDerivWithinAt (x θ) (f (x θ t) θ) (Icc 0 T) t ∧ (x θ t, θ) ∈ U := by
  obtain ⟨g, hg⟩ : ∃ g : EuclideanSpace ℝ (Fin n) × P → EuclideanSpace ℝ (Fin n),
      g = fun z => f z.1 z.2 := ⟨_, rfl⟩
  have hfg : ∀ y θ, f y θ = g (y, θ) := fun y θ => by rw [hg]
  rw [← hg] at hf
  have hx₀c : ContinuousOn x₀ (Icc 0 T) := fun t ht => (hx₀ t ht).continuousWithinAt
  have hγcont : ContinuousOn (fun t => (x₀ t, θ₀)) (Icc 0 T) := hx₀c.prodMk continuousOn_const
  obtain ⟨K₀, hK₀def⟩ : ∃ K₀ : Set (EuclideanSpace ℝ (Fin n) × P),
      K₀ = (fun t => (x₀ t, θ₀)) '' Icc 0 T := ⟨_, rfl⟩
  have hK₀ : IsCompact K₀ := hK₀def ▸ isCompact_Icc.image_of_continuousOn hγcont
  have hγK₀ : ∀ t ∈ Icc 0 T, (x₀ t, θ₀) ∈ K₀ := fun t ht => hK₀def ▸ mem_image_of_mem _ ht
  obtain ⟨R, hR, hRU⟩ := hK₀.exists_cthickening_subset_open hU
    (by rw [hK₀def]; rintro _ ⟨t, ht, rfl⟩; exact hγU t ht)
  have hK₁ : IsCompact (cthickening R K₀) := hK₀.cthickening
  have hDg : ContinuousOn (fderiv ℝ g) (cthickening R K₀) :=
    (hf.continuousOn_fderiv_of_isOpen hU le_rfl).mono hRU
  have hdiffK : ∀ z ∈ cthickening R K₀, HasFDerivAt g (fderiv ℝ g z) z := fun z hz =>
    ((hf.contDiffAt (hU.mem_nhds (hRU hz))).differentiableAt le_rfl).hasFDerivAt
  obtain ⟨M, hM⟩ := hK₁.exists_bound_of_continuousOn hDg
  obtain ⟨M', hM'pos, hMM'⟩ : ∃ M' : ℝ≥0, (0 : ℝ) < M' ∧
      ∀ z ∈ cthickening R K₀, ‖fderiv ℝ g z‖ ≤ M' :=
    ⟨⟨max M 0 + 1, by positivity⟩, by simp only [NNReal.coe_mk]; positivity,
      fun z hz => by simp only [NNReal.coe_mk]; linarith [hM z hz, le_max_left M 0]⟩
  have hball : ∀ t ∈ Icc 0 T, closedBall (x₀ t, θ₀) R ⊆ cthickening R K₀ := fun t ht =>
    closedBall_subset_cthickening (hγK₀ t ht) R
  have hgLip : ∀ t ∈ Icc 0 T, LipschitzOnWith M' g (closedBall (x₀ t, θ₀) R) := by
    intro t ht
    refine (convex_closedBall _ _).lipschitzOnWith_of_nnnorm_hasFDerivWithin_le
      (fun z hz => (hdiffK z (hball t ht hz)).hasFDerivWithinAt) ?_
    intro z hz
    rw [← NNReal.coe_le_coe, coe_nnnorm]; exact hMM' z (hball t ht hz)
  -- constantes
  obtain ⟨c, hcdef⟩ : ∃ c : ℝ, c = R / (n + 1) := ⟨_, rfl⟩
  have hc : 0 < c := by rw [hcdef]; positivity
  have hcR : (n + 1) * c = R := by rw [hcdef]; field_simp
  have hcR' : c ≤ R := by
    rw [← hcR]; have : (0 : ℝ) ≤ n := Nat.cast_nonneg n; nlinarith
  obtain ⟨EK, hEK⟩ : ∃ EK, EK = Real.exp (M' * T) := ⟨_, rfl⟩
  obtain ⟨CT, hCT⟩ : ∃ CT, CT = (EK - 1) / M' := ⟨_, rfl⟩
  have hEK1 : 1 ≤ EK := hEK ▸ Real.one_le_exp (mul_nonneg hM'pos.le hT)
  have hCT0 : 0 ≤ CT := by rw [hCT]; exact div_nonneg (by linarith) hM'pos.le
  obtain ⟨r1, hr1⟩ : ∃ r1, r1 = min R (c / (2 * (M' * (CT + 1)))) := ⟨_, rfl⟩
  obtain ⟨r2, hr2⟩ : ∃ r2, r2 = c / (2 * EK) := ⟨_, rfl⟩
  have hr1pos : 0 < r1 := by rw [hr1]; exact lt_min hR (by positivity)
  have hr2pos : 0 < r2 := by rw [hr2]; positivity
  -- construcción para un `θ` bueno
  have main : ∀ θ, dist θ θ₀ < r1 → dist (x0 θ) (x0 θ₀) < r2 →
      ∃ α : ℝ → EuclideanSpace ℝ (Fin n), α 0 = x0 θ ∧ ∀ t ∈ Icc 0 T,
        HasDerivWithinAt α (f (α t) θ) (Icc 0 T) t ∧ (α t, θ) ∈ U := by
    intro θ hθ1 hθ2
    have hθR : dist θ θ₀ ≤ R := hθ1.le.trans (by rw [hr1]; exact min_le_left _ _)
    have hθε : dist θ θ₀ * (2 * (M' * (CT + 1))) < c := by
      have : dist θ θ₀ < c / (2 * (M' * (CT + 1))) :=
        hθ1.trans_le (by rw [hr1]; exact min_le_right _ _)
      rwa [lt_div_iff₀ (by positivity)] at this
    have hθδ : dist (x0 θ) (x0 θ₀) * (2 * EK) < c := by
      rwa [hr2, lt_div_iff₀ (by positivity)] at hθ2
    -- campo truncado
    set v : ℝ → EuclideanSpace ℝ (Fin n) → EuclideanSpace ℝ (Fin n) :=
      fun t y => g (x₀ t + clampE c (y - x₀ t), θ) with hv
    have hpt : ∀ t ∈ Icc 0 T, ∀ y, (x₀ t + clampE c (y - x₀ t), θ) ∈ closedBall (x₀ t, θ₀) R := by
      intro t ht y
      rw [mem_closedBall, Prod.dist_eq]
      refine max_le ?_ hθR
      rw [dist_eq_norm, add_sub_cancel_left, ← hcR]
      exact norm_clampE_le hc.le _
    have hvLip : ∀ t ∈ Icc 0 T, LipschitzWith M' (v t) := by
      intro t ht
      refine LipschitzWith.of_dist_le_mul fun y y' => ?_
      have h1 := (hgLip t ht).dist_le_mul _ (hpt t ht y) _ (hpt t ht y')
      refine h1.trans (mul_le_mul_of_nonneg_left ?_ M'.2)
      rw [Prod.dist_eq, dist_self, max_eq_left dist_nonneg, dist_add_left]
      refine (dist_clampE_le c _ _).trans ?_
      rw [dist_sub_right]
    have hclampc : Continuous (clampE (n := n) c) := (lipschitz_clampE c).continuous
    have hvcont : ∀ y, ContinuousOn (fun t => v t y) (Icc 0 T) := by
      intro y
      have hin : ContinuousOn (fun t => (x₀ t + clampE c (y - x₀ t), θ)) (Icc 0 T) :=
        (hx₀c.add (hclampc.comp_continuousOn (continuousOn_const.sub hx₀c))).prodMk
          continuousOn_const
      exact hf.continuousOn.comp hin (fun t ht => hRU (hball t ht (hpt t ht y)))
    obtain ⟨α, hα0, hαsol⟩ := exists_solution_Icc v M' hT hvLip hvcont (x0 θ)
    have hαc : ContinuousOn α (Icc 0 T) := fun t ht => (hαsol t ht).continuousWithinAt
    have hIci : ∀ t ∈ Ico 0 T, Icc 0 T ∈ 𝓝[Ici t] t := fun t ht =>
      mem_of_superset (Icc_mem_nhdsGE ht.2) (Icc_subset_Icc ht.1 le_rfl)
    have hdef : ∀ t ∈ Icc 0 T, dist (f (x₀ t) θ₀) (v t (x₀ t)) ≤ M' * dist θ θ₀ := by
      intro t ht
      have hvx : v t (x₀ t) = g (x₀ t, θ) := by
        simp only [hv, sub_self, clampE_zero hc.le, add_zero]
      rw [hvx, hfg]
      have hmem : (x₀ t, θ) ∈ closedBall (x₀ t, θ₀) R := by
        rw [mem_closedBall, Prod.dist_eq, dist_self]; exact max_le hR.le hθR
      have := (hgLip t ht).dist_le_mul _ (mem_closedBall_self hR.le) _ hmem
      rwa [Prod.dist_eq, dist_self, max_eq_right dist_nonneg, dist_comm θ₀] at this
    have key := dist_le_of_approx_trajectories_ODE_of_mem
      (v := v) (s := fun _ => univ) (K := M')
      (f := α) (f' := fun t => v t (α t)) (εf := 0)
      (g := x₀) (g' := fun t => f (x₀ t) θ₀) (εg := M' * dist θ θ₀)
      (δ := dist (x0 θ) (x0 θ₀))
      (fun t ht => (hvLip t (Ico_subset_Icc_self ht)).lipschitzOnWith)
      hαc
      (fun t ht => (hαsol t (Ico_subset_Icc_self ht)).mono_of_mem_nhdsWithin (hIci t ht))
      (fun t _ => by simp)
      (fun _ _ => mem_univ _)
      hx₀c
      (fun t ht => (hx₀ t (Ico_subset_Icc_self ht)).mono_of_mem_nhdsWithin (hIci t ht))
      (fun t ht => hdef t (Ico_subset_Icc_self ht))
      (fun _ _ => mem_univ _)
      (by rw [hα0, ← hx00])
    have hclose : ∀ t ∈ Icc 0 T, ‖α t - x₀ t‖ ≤ c := by
      intro t ht
      have k1 := key t ht
      rw [zero_add, sub_zero, gronwallBound_of_K_ne_0 (ne_of_gt hM'pos)] at k1
      simp only at k1
      rw [← dist_eq_norm]
      have hexp : Real.exp (M' * t) ≤ EK := by
        rw [hEK]; exact Real.exp_le_exp.2 (mul_le_mul_of_nonneg_left ht.2 hM'pos.le)
      have hδ0 : 0 ≤ dist (x0 θ) (x0 θ₀) := dist_nonneg
      have hε0 : 0 ≤ (M' : ℝ) * dist θ θ₀ := mul_nonneg M'.2 dist_nonneg
      have h1 := mul_le_mul_of_nonneg_left hexp hδ0
      have h2 : (M' : ℝ) * dist θ θ₀ / M' * (Real.exp (M' * t) - 1)
          ≤ (M' : ℝ) * dist θ θ₀ / M' * (EK - 1) :=
        mul_le_mul_of_nonneg_left (by linarith) (div_nonneg hε0 hM'pos.le)
      have h3 : (M' : ℝ) * dist θ θ₀ / M' * (EK - 1) = dist θ θ₀ * (M' * CT) := by
        rw [hCT]; field_simp
      have h4 : dist θ θ₀ * (M' * CT) ≤ dist θ θ₀ * (M' * (CT + 1)) :=
        mul_le_mul_of_nonneg_left (by nlinarith [M'.2]) dist_nonneg
      nlinarith
    refine ⟨α, hα0, fun t ht => ⟨?_, ?_⟩⟩
    · have hvα : v t (α t) = f (α t) θ := by
        simp only [hv]
        rw [clampE_eq (hclose t ht), add_sub_cancel, hfg]
      rw [← hvα]; exact hαsol t ht
    · apply hRU (hball t ht _)
      rw [mem_closedBall, Prod.dist_eq, dist_eq_norm]
      exact max_le ((hclose t ht).trans hcR') hθR
  -- familia de soluciones
  have hex : ∀ θ, ∃ α : ℝ → EuclideanSpace ℝ (Fin n),
      (dist θ θ₀ < r1 ∧ dist (x0 θ) (x0 θ₀) < r2) → (α 0 = x0 θ ∧ ∀ t ∈ Icc 0 T,
        HasDerivWithinAt α (f (α t) θ) (Icc 0 T) t ∧ (α t, θ) ∈ U) := by
    intro θ
    by_cases hθ : dist θ θ₀ < r1 ∧ dist (x0 θ) (x0 θ₀) < r2
    · obtain ⟨α, hα⟩ := main θ hθ.1 hθ.2
      exact ⟨α, fun _ => hα⟩
    · exact ⟨x₀, fun h => absurd h hθ⟩
  choose αf hαf using hex
  classical
  refine ⟨fun θ => if θ = θ₀ then x₀ else αf θ, by simp, ?_⟩
  have h1 : ∀ᶠ θ in 𝓝 θ₀, dist θ θ₀ < r1 := ball_mem_nhds θ₀ hr1pos
  have h2 : ∀ᶠ θ in 𝓝 θ₀, dist (x0 θ) (x0 θ₀) < r2 := hx0c (ball_mem_nhds _ hr2pos)
  filter_upwards [h1, h2] with θ hθ1 hθ2
  by_cases hθ : θ = θ₀
  · simp only [if_pos hθ]
    subst hθ
    exact ⟨hx00.symm, fun t ht => ⟨hx₀ t ht, hγU t ht⟩⟩
  · simp only [if_neg hθ]
    exact hαf θ ⟨hθ1, hθ2⟩

/-- **Diferenciabilidad respecto a `θ` a partir sólo de la solución nominal.** Con las hipótesis
de `exists_solutions_near` y un dato inicial diferenciable (`x0` con derivada `D0` en `θ₀`), la
familia de soluciones existe cerca de `θ₀` y su trayectoria es diferenciable en `θ₀` con
sensibilidad `S` que resuelve la ecuación variacional a lo largo de `x₀`. -/
theorem hasFDerivAt_of_nominal_solution
    (f : EuclideanSpace ℝ (Fin n) → P → EuclideanSpace ℝ (Fin n))
    {U : Set (EuclideanSpace ℝ (Fin n) × P)} (hU : IsOpen U)
    (hf : ContDiffOn ℝ 1 (fun z : EuclideanSpace ℝ (Fin n) × P => f z.1 z.2) U)
    {T : ℝ} (hT : 0 ≤ T) (x₀ : ℝ → EuclideanSpace ℝ (Fin n)) (θ₀ : P)
    (hx₀ : ∀ t ∈ Icc 0 T, HasDerivWithinAt x₀ (f (x₀ t) θ₀) (Icc 0 T) t)
    (hγU : ∀ t ∈ Icc 0 T, (x₀ t, θ₀) ∈ U)
    (x0 : P → EuclideanSpace ℝ (Fin n)) (D0 : P →L[ℝ] EuclideanSpace ℝ (Fin n))
    (hx0 : HasFDerivAt x0 D0 θ₀) (hx00 : x0 θ₀ = x₀ 0) :
    ∃ x : P → ℝ → EuclideanSpace ℝ (Fin n), x θ₀ = x₀ ∧
      (∀ᶠ θ in 𝓝 θ₀, x θ 0 = x0 θ ∧
        ∀ t ∈ Icc 0 T, HasDerivWithinAt (x θ) (f (x θ t) θ) (Icc 0 T) t) ∧
      ∃ S : ℝ → (P →L[ℝ] EuclideanSpace ℝ (Fin n)), S 0 = D0 ∧
        (∀ t ∈ Icc 0 T, HasDerivWithinAt S
          ((fderiv ℝ (fun z : EuclideanSpace ℝ (Fin n) × P => f z.1 z.2) (x₀ t, θ₀)).comp
              (ContinuousLinearMap.inl ℝ _ P) ∘L S t
            + (fderiv ℝ (fun z : EuclideanSpace ℝ (Fin n) × P => f z.1 z.2) (x₀ t, θ₀)).comp
              (ContinuousLinearMap.inr ℝ _ P)) (Icc 0 T) t) ∧
        ∀ t ∈ Icc 0 T, HasFDerivAt (fun θ => x θ t) (S t) θ₀ := by
  obtain ⟨x, hxθ₀, hev⟩ :=
    exists_solutions_near f hU hf hT x₀ θ₀ hx₀ hγU x0 hx0.continuousAt hx00
  have hsol : ∀ᶠ θ in 𝓝 θ₀, ∀ t ∈ Icc 0 T,
      HasDerivWithinAt (x θ) (f (x θ t) θ) (Icc 0 T) t :=
    hev.mono fun θ h t ht => (h.2 t ht).1
  have hinit : ∀ᶠ θ in 𝓝 θ₀, x θ 0 = x0 θ := hev.mono fun θ h => h.1
  have hγU' : ∀ t ∈ Icc 0 T, (x θ₀ t, θ₀) ∈ U := by rw [hxθ₀]; exact hγU
  obtain ⟨S, hS0, hSvar, hSder⟩ :=
    hasFDerivAt_solution_param_init f hU hf hT x θ₀ hγU' hsol x0 D0 hx0 hinit
  rw [hxθ₀] at hSvar
  exact ⟨x, hxθ₀, hev.mono fun θ h => ⟨h.1, fun t ht => (h.2 t ht).1⟩, S, hS0, hSvar, hSder⟩

end LocalExistence

#print axioms LocalExistence.exists_solutions_near
#print axioms LocalExistence.hasFDerivAt_of_nominal_solution
