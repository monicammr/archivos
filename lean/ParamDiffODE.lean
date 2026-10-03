import GlobalLipschitzODE
import Mathlib.Analysis.ODE.Gronwall
import Mathlib.Analysis.Calculus.MeanValue
import Mathlib.Analysis.Calculus.FDeriv.Prod
import Mathlib.Analysis.Calculus.Deriv.Mul
import Mathlib.Topology.MetricSpace.Thickening
import Mathlib.Topology.UniformSpace.HeineCantor
import Mathlib.Topology.Order.IntermediateValue
import Mathlib.Analysis.Normed.Operator.Prod
import Mathlib.Analysis.Normed.Module.FiniteDimension

/-!
# Dependencia diferenciable de las soluciones de una EDO respecto a los parámetros

Sea `ẋ = f(x, θ)` con `f : E × P → E` de clase C¹ (`E`, `P` de dimensión finita) y
`x θ : ℝ → E` soluciones en `[0, T]` con el mismo dato inicial, para `θ` cerca de `θ₀`.
Entonces, para cada `t ∈ [0, T]`, la aplicación `θ ↦ x θ t` es diferenciable en `θ₀`,
y su derivada `S t` es la solución de la ecuación variacional
`S' = (∂ₓf) S + ∂_θ f`, `S 0 = 0`.

Estructura de la prueba:
1. `S` existe en todo `[0, T]` (EDO lineal, `GlobalLipschitzODE.lean`).
2. Linealización uniforme de `f` a lo largo de la trayectoria nominal (compacidad).
3. Grönwall (Mathlib) comparando `x (θ₀+h)` con `x θ₀ + S h`, más un argumento de
   inducción continua para que `x (θ₀+h)` no salga de un tubo alrededor de `x θ₀`.
-/

open Set Filter Topology NNReal Metric Asymptotics

namespace ODEParamDiff

section Linearization

variable {G H : Type*} [NormedAddCommGroup G] [NormedSpace ℝ G] [ProperSpace G]
  [NormedAddCommGroup H] [NormedSpace ℝ H]

/-- **Linealización uniforme** de una función C¹ cerca de un compacto `K₀`. -/
theorem uniform_linearization {g : G → H} (hg : ContDiff ℝ 1 g) {K₀ : Set G}
    (hK₀ : IsCompact K₀) {η : ℝ} (hη : 0 < η) :
    ∃ δ > 0, δ ≤ 1 ∧ ∀ z ∈ K₀, ∀ w, ‖w - z‖ ≤ δ →
      ‖g w - g z - fderiv ℝ g z (w - z)‖ ≤ η * ‖w - z‖ := by
  have hK₁ : IsCompact (cthickening 1 K₀) := hK₀.cthickening
  have hDg : Continuous (fderiv ℝ g) := hg.continuous_fderiv le_rfl
  have hunif := hK₁.uniformContinuousOn_of_continuous hDg.continuousOn
  rw [Metric.uniformContinuousOn_iff] at hunif
  obtain ⟨δ₂, hδ₂, hδ₂'⟩ := hunif η hη
  refine ⟨min (δ₂ / 2) 1, by positivity, min_le_right _ _, ?_⟩
  intro z hz w hw
  have hzK₁ : z ∈ cthickening 1 K₀ := self_subset_cthickening _ hz
  set φ : G → H := fun u => g u - fderiv ℝ g z u with hφ
  have hdiff : ∀ u, HasFDerivAt φ (fderiv ℝ g u - fderiv ℝ g z) u := fun u =>
    ((hg.differentiable le_rfl u).hasFDerivAt).sub (fderiv ℝ g z).hasFDerivAt
  have hbound : ∀ u ∈ closedBall z (min (δ₂ / 2) 1), ‖fderiv ℝ φ u‖ ≤ η := by
    intro u hu
    rw [(hdiff u).fderiv]
    have hu' := mem_closedBall.1 hu
    have huK : u ∈ cthickening 1 K₀ :=
      mem_cthickening_of_dist_le u z 1 K₀ hz (hu'.trans (min_le_right _ _))
    have hdist : dist u z < δ₂ :=
      lt_of_le_of_lt (hu'.trans (min_le_left _ _)) (by linarith)
    have := hδ₂' u huK z hzK₁ hdist
    rw [dist_eq_norm] at this
    exact this.le
  have hmv := (convex_closedBall z (min (δ₂ / 2) 1)).norm_image_sub_le_of_norm_fderiv_le
    (fun u _ => (hdiff u).differentiableAt) hbound
    (mem_closedBall_self (by positivity)) (mem_closedBall.2 (by rw [dist_eq_norm]; exact hw))
  have heq : φ w - φ z = g w - g z - fderiv ℝ g z (w - z) := by
    simp only [hφ, map_sub]; abel
  rw [← heq]; exact hmv

end Linearization

section Tube

variable {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]

/-- **Grönwall en un tubo.** Si `yh` es una solución aproximada (defecto `≤ εg`) que
permanece a distancia `≤ σ` de la trayectoria nominal `x₀`, y `xθ` es una solución exacta
con el mismo dato inicial, entonces `xθ` no sale del tubo de radio `ρ` y
`dist (xθ t) (yh t) ≤ εg · (e^{KT} − 1)/K` en todo `[0, T]`. -/
theorem tube_gronwall {T ρ σ εg : ℝ} {K : ℝ≥0} (hK : 0 < (K : ℝ)) (hT : 0 ≤ T)
    (v : E → E) (x₀ xθ yh yh' : ℝ → E)
    (hLip : ∀ t ∈ Icc 0 T, LipschitzOnWith K v (closedBall (x₀ t) ρ))
    (hx₀ : ContinuousOn x₀ (Icc 0 T))
    (hxθ : ∀ t ∈ Icc 0 T, HasDerivWithinAt xθ (v (xθ t)) (Icc 0 T) t)
    (hyh : ∀ t ∈ Icc 0 T, HasDerivWithinAt yh (yh' t) (Icc 0 T) t)
    (hdef : ∀ t ∈ Icc 0 T, dist (yh' t) (v (yh t)) ≤ εg)
    (hσ : ∀ t ∈ Icc 0 T, dist (yh t) (x₀ t) ≤ σ) (hσρ : σ ≤ ρ)
    (h0 : xθ 0 = yh 0) (hεg : 0 ≤ εg)
    (hsmall : εg * ((Real.exp (K * T) - 1) / K) + σ < ρ / 2) :
    ∀ t ∈ Icc 0 T, dist (xθ t) (yh t) ≤ εg * ((Real.exp (K * T) - 1) / K) := by
  obtain ⟨CT, hCT⟩ : ∃ CT, CT = (Real.exp (K * T) - 1) / K := ⟨_, rfl⟩
  rw [← hCT] at hsmall ⊢
  have hCT0 : 0 ≤ CT := by
    rw [hCT]; apply div_nonneg _ hK.le
    linarith [Real.one_le_exp (mul_nonneg hK.le hT)]
  have hxθc : ContinuousOn xθ (Icc 0 T) := fun t ht => (hxθ t ht).continuousWithinAt
  have hyhc : ContinuousOn yh (Icc 0 T) := fun t ht => (hyh t ht).continuousWithinAt
  have hyhm : ∀ t ∈ Icc 0 T, yh t ∈ closedBall (x₀ t) ρ := fun t ht =>
    mem_closedBall.2 ((hσ t ht).trans hσρ)
  have gron : ∀ b ∈ Icc 0 T, (∀ u ∈ Ico 0 b, xθ u ∈ closedBall (x₀ u) ρ) →
      ∀ u ∈ Icc 0 b, dist (xθ u) (yh u) ≤ εg * CT := by
    intro b hb hmem u hu
    have hsub : Icc 0 b ⊆ Icc 0 T := Icc_subset_Icc le_rfl hb.2
    have hIci : ∀ t ∈ Ico 0 b, Icc 0 T ∈ 𝓝[Ici t] t := fun t ht =>
      mem_of_superset (Icc_mem_nhdsGE (ht.2.trans_le hb.2)) (Icc_subset_Icc ht.1 le_rfl)
    have key := dist_le_of_approx_trajectories_ODE_of_mem
      (v := fun _ y => v y) (s := fun t => closedBall (x₀ t) ρ) (K := K)
      (f := xθ) (f' := fun t => v (xθ t)) (εf := 0)
      (g := yh) (g' := yh') (εg := εg) (δ := 0)
      (fun t ht => hLip t (hsub (Ico_subset_Icc_self ht)))
      (hxθc.mono hsub)
      (fun t ht => (hxθ t (hsub (Ico_subset_Icc_self ht))).mono_of_mem_nhdsWithin (hIci t ht))
      (fun t _ => by simp)
      hmem
      (hyhc.mono hsub)
      (fun t ht => (hyh t (hsub (Ico_subset_Icc_self ht))).mono_of_mem_nhdsWithin (hIci t ht))
      (fun t ht => hdef t (hsub (Ico_subset_Icc_self ht)))
      (fun t ht => hyhm t (hsub (Ico_subset_Icc_self ht)))
      (by simp [h0])
      u hu
    refine key.trans ?_
    simp only [gronwallBound_of_K_ne_0 hK.ne', zero_mul, zero_add, sub_zero]
    have hexp : Real.exp (K * u) ≤ Real.exp (K * T) :=
      Real.exp_le_exp.2 (mul_le_mul_of_nonneg_left (hu.2.trans hb.2) hK.le)
    calc εg / K * (Real.exp (K * u) - 1) ≤ εg / K * (Real.exp (K * T) - 1) :=
          mul_le_mul_of_nonneg_left (by linarith) (div_nonneg hεg hK.le)
      _ = εg * CT := by rw [hCT]; ring
  -- confinamiento por inducción continua
  have hdc : ContinuousOn (fun u => dist (xθ u) (x₀ u)) (Icc 0 T) := continuous_dist.comp_continuousOn (hxθc.prodMk hx₀)
  have hconf : Icc 0 T ⊆ (fun u => dist (xθ u) (x₀ u)) ⁻¹' Iic (ρ / 2) := by
    have hclosed : IsClosed ((fun u => dist (xθ u) (x₀ u)) ⁻¹' Iic (ρ / 2) ∩ Icc 0 T) := by
      have := hdc.preimage_isClosed_of_isClosed isClosed_Icc (isClosed_Iic (a := ρ / 2))
      rwa [inter_comm] at this
    refine hclosed.Icc_subset_of_forall_mem_nhdsGT_of_Icc_subset ?_ ?_
    · show dist (xθ 0) (x₀ 0) ≤ ρ / 2
      rw [h0]
      have := hσ 0 ⟨le_rfl, hT⟩
      nlinarith [mul_nonneg hεg hCT0]
    · intro t ht hsubt
      have htT : t ∈ Icc 0 T := ⟨ht.1, ht.2.le⟩
      have hmem : ∀ u ∈ Ico 0 t, xθ u ∈ closedBall (x₀ u) ρ := fun u hu =>
        mem_closedBall.2 ((show dist (xθ u) (x₀ u) ≤ ρ / 2 from hsubt ⟨hu.1, hu.2.le⟩).trans
          (by nlinarith [mul_nonneg hεg hCT0, dist_nonneg (x := yh 0) (y := x₀ 0),
            hσ 0 ⟨le_rfl, hT⟩]))
      have hg := gron t htT hmem t ⟨ht.1, le_rfl⟩
      have hlt : dist (xθ t) (x₀ t) < ρ / 2 := by
        have := dist_triangle (xθ t) (yh t) (x₀ t)
        linarith [hσ t htT]
      have hev : ∀ᶠ u in 𝓝[Icc 0 T] t, dist (xθ u) (x₀ u) < ρ / 2 :=
        (hdc t htT).eventually (gt_mem_nhds hlt)
      have hle : 𝓝[>] t ≤ 𝓝[Icc 0 T] t :=
        nhdsWithin_le_of_mem (mem_of_superset (Ioc_mem_nhdsGT ht.2)
          (Ioc_subset_Icc_self.trans (Icc_subset_Icc ht.1 le_rfl)))
      exact (hev.filter_mono hle).mono fun u hu => (show dist (xθ u) (x₀ u) ≤ ρ / 2 from hu.le)
  have hρ : 0 ≤ ρ := by
    nlinarith [mul_nonneg hεg hCT0, dist_nonneg (x := yh 0) (y := x₀ 0), hσ 0 ⟨le_rfl, hT⟩]
  exact gron T ⟨hT, le_rfl⟩ fun u hu =>
    mem_closedBall.2 ((show dist (xθ u) (x₀ u) ≤ ρ / 2 from hconf ⟨hu.1, hu.2.le⟩).trans
      (by linarith))

end Tube

section Main

variable {E P : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E] [FiniteDimensional ℝ E]
  [NormedAddCommGroup P] [NormedSpace ℝ P] [FiniteDimensional ℝ P]

omit [FiniteDimensional ℝ E] [FiniteDimensional ℝ P] in
lemma norm_comp_inl_le (L : E × P →L[ℝ] E) :
    ‖L.comp (ContinuousLinearMap.inl ℝ E P)‖ ≤ ‖L‖ := by
  refine ContinuousLinearMap.opNorm_le_bound _ (norm_nonneg _) fun u => ?_
  simp only [ContinuousLinearMap.comp_apply, ContinuousLinearMap.inl_apply]
  calc ‖L (u, 0)‖ ≤ ‖L‖ * ‖(u, (0 : P))‖ := L.le_opNorm _
    _ = ‖L‖ * ‖u‖ := by simp

omit [FiniteDimensional ℝ E] [FiniteDimensional ℝ P] in
lemma clm_prod_apply_split (L : E × P →L[ℝ] E) (u : E) (k : P) :
    L (u, k) = L.comp (ContinuousLinearMap.inl ℝ E P) u
      + L.comp (ContinuousLinearMap.inr ℝ E P) k := by
  rw [ContinuousLinearMap.comp_apply, ContinuousLinearMap.comp_apply, ← map_add]
  congr 1
  ext <;> simp

omit [FiniteDimensional ℝ E] [FiniteDimensional ℝ P] in
/-- Lipschitz de `y ↦ f y θ` en una bola, a partir de una cota de la derivada conjunta. -/
lemma lipschitzOn_slice (f : E → P → E) (hf : ContDiff ℝ 1 (fun z : E × P => f z.1 z.2))
    (θ : P) (c : E) (ρ : ℝ) (Kset : Set (E × P)) (M : ℝ≥0)
    (hM : ∀ z ∈ Kset, ‖fderiv ℝ (fun z : E × P => f z.1 z.2) z‖ ≤ M)
    (hball : ∀ y ∈ closedBall c ρ, (y, θ) ∈ Kset) :
    LipschitzOnWith M (fun y => f y θ) (closedBall c ρ) := by
  have hder : ∀ y ∈ closedBall c ρ, HasFDerivWithinAt (fun y => f y θ)
      ((fderiv ℝ (fun z : E × P => f z.1 z.2) (y, θ)).comp
        ((ContinuousLinearMap.id ℝ E).prod 0)) (closedBall c ρ) y := by
    intro y _
    have h1 : HasFDerivAt (fun z : E × P => f z.1 z.2)
        (fderiv ℝ (fun z : E × P => f z.1 z.2) (y, θ)) (y, θ) :=
      (hf.differentiable le_rfl (y, θ)).hasFDerivAt
    have h2 : HasFDerivAt (fun y : E => (y, θ)) ((ContinuousLinearMap.id ℝ E).prod 0) y :=
      (hasFDerivAt_id y).prodMk (hasFDerivAt_const θ y)
    exact (h1.comp y h2).hasFDerivWithinAt
  refine (convex_closedBall _ _).lipschitzOnWith_of_nnnorm_hasFDerivWithin_le hder ?_
  intro y hy
  rw [← NNReal.coe_le_coe, coe_nnnorm]
  calc ‖(fderiv ℝ (fun z : E × P => f z.1 z.2) (y, θ)).comp
          ((ContinuousLinearMap.id ℝ E).prod 0)‖
      ≤ ‖fderiv ℝ (fun z : E × P => f z.1 z.2) (y, θ)‖
          * ‖(ContinuousLinearMap.id ℝ E).prod (0 : E →L[ℝ] P)‖ :=
        ContinuousLinearMap.opNorm_comp_le _ _
    _ ≤ M * 1 := by
        apply mul_le_mul (hM _ (hball y hy)) _ (norm_nonneg _) (NNReal.coe_nonneg _)
        rw [ContinuousLinearMap.opNorm_prod, Prod.norm_mk, norm_zero]
        exact max_le (ContinuousLinearMap.norm_id_le) zero_le_one
    _ = M := mul_one _

set_option maxHeartbeats 1000000 in
/-- **Dependencia diferenciable respecto a parámetros.**

Hipótesis: `f` es C¹ en `(x, θ)`; para `θ` cerca de `θ₀`, `x θ` resuelve
`ẋ = f(x, θ)` en `[0, T]` con el mismo dato inicial que `x θ₀`.

Conclusión: existe `S : ℝ → (P →L[ℝ] E)` con `S 0 = 0`, que resuelve la ecuación
variacional `S' = (∂ₓf)·S + ∂_θ f` a lo largo de `x θ₀`, y tal que para todo
`t ∈ [0, T]`, `HasFDerivAt (fun θ => x θ t) (S t) θ₀`. -/
theorem hasFDerivAt_solution_param
    (f : E → P → E) (hf : ContDiff ℝ 1 (fun z : E × P => f z.1 z.2))
    {T : ℝ} (hT : 0 ≤ T) (x : P → ℝ → E) (θ₀ : P)
    (hsol : ∀ᶠ θ in 𝓝 θ₀, ∀ t ∈ Icc 0 T, HasDerivWithinAt (x θ) (f (x θ t) θ) (Icc 0 T) t)
    (hinit : ∀ᶠ θ in 𝓝 θ₀, x θ 0 = x θ₀ 0) :
    ∃ S : ℝ → (P →L[ℝ] E), S 0 = 0 ∧
      (∀ t ∈ Icc 0 T, HasDerivWithinAt S
        ((fderiv ℝ (fun z : E × P => f z.1 z.2) (x θ₀ t, θ₀)).comp
            (ContinuousLinearMap.inl ℝ E P) ∘L S t
          + (fderiv ℝ (fun z : E × P => f z.1 z.2) (x θ₀ t, θ₀)).comp
            (ContinuousLinearMap.inr ℝ E P)) (Icc 0 T) t) ∧
      ∀ t ∈ Icc 0 T, HasFDerivAt (fun θ => x θ t) (S t) θ₀ := by
  obtain ⟨g, hg⟩ : ∃ g : E × P → E, g = fun z => f z.1 z.2 := ⟨_, rfl⟩
  rw [← hg] at hf ⊢
  have hDg : Continuous (fderiv ℝ g) := hf.continuous_fderiv le_rfl
  have hsol0 := hsol.self_of_nhds
  have hx0cont : ContinuousOn (x θ₀) (Icc 0 T) := fun t ht => (hsol0 t ht).continuousWithinAt
  have hγcont : ContinuousOn (fun t => (x θ₀ t, θ₀)) (Icc 0 T) := hx0cont.prodMk continuousOn_const
  obtain ⟨K₀, hK₀def⟩ : ∃ K₀ : Set (E × P), K₀ = (fun t => (x θ₀ t, θ₀)) '' Icc 0 T := ⟨_, rfl⟩
  have hK₀ : IsCompact K₀ := hK₀def ▸ isCompact_Icc.image_of_continuousOn hγcont
  have hγK₀ : ∀ t ∈ Icc 0 T, (x θ₀ t, θ₀) ∈ K₀ := fun t ht => hK₀def ▸ mem_image_of_mem _ ht
  have hK₁ : IsCompact (cthickening 1 K₀) := hK₀.cthickening
  obtain ⟨M, hM⟩ := hK₁.exists_bound_of_continuousOn hDg.continuousOn
  obtain ⟨M', hM'pos, hMM'⟩ : ∃ M' : ℝ≥0, (0 : ℝ) < M' ∧
      ∀ z ∈ cthickening 1 K₀, ‖fderiv ℝ g z‖ ≤ M' :=
    ⟨⟨max M 0 + 1, by positivity⟩, by simp only [NNReal.coe_mk]; positivity,
      fun z hz => by simp only [NNReal.coe_mk]; linarith [hM z hz, le_max_left M 0]⟩
  -- (1) Ecuación variacional: existencia global de `S`
  have hAbound : ∀ t ∈ Icc 0 T,
      ‖(fderiv ℝ g (x θ₀ t, θ₀)).comp (ContinuousLinearMap.inl ℝ E P)‖ ≤ M' := fun t ht =>
    (norm_comp_inl_le _).trans (hMM' _ (self_subset_cthickening _ (hγK₀ t ht)))
  have hwLip : ∀ t ∈ Icc 0 T, LipschitzWith M' (fun S : P →L[ℝ] E =>
      (fderiv ℝ g (x θ₀ t, θ₀)).comp (ContinuousLinearMap.inl ℝ E P) ∘L S
        + (fderiv ℝ g (x θ₀ t, θ₀)).comp (ContinuousLinearMap.inr ℝ E P)) := by
    intro t ht
    refine LipschitzWith.of_dist_le_mul fun S S' => ?_
    rw [dist_eq_norm, dist_eq_norm, add_sub_add_right_eq_sub, ← ContinuousLinearMap.comp_sub]
    exact (ContinuousLinearMap.opNorm_comp_le _ _).trans
      (mul_le_mul_of_nonneg_right (hAbound t ht) (norm_nonneg _))
  have hDgγ : ContinuousOn (fun t => fderiv ℝ g (x θ₀ t, θ₀)) (Icc 0 T) :=
    hDg.comp_continuousOn hγcont
  have hwcont : ∀ S : P →L[ℝ] E, ContinuousOn (fun t =>
      (fderiv ℝ g (x θ₀ t, θ₀)).comp (ContinuousLinearMap.inl ℝ E P) ∘L S
        + (fderiv ℝ g (x θ₀ t, θ₀)).comp (ContinuousLinearMap.inr ℝ E P)) (Icc 0 T) :=
    fun S => ((hDgγ.clm_comp continuousOn_const).clm_comp continuousOn_const).add
      (hDgγ.clm_comp continuousOn_const)
  obtain ⟨S, hS0, hS⟩ := exists_solution_Icc _ M' hT hwLip hwcont 0
  have hScont : ContinuousOn S (Icc 0 T) := fun t ht => (hS t ht).continuousWithinAt
  obtain ⟨Smax, hSmax⟩ := isCompact_Icc.exists_bound_of_continuousOn hScont
  obtain ⟨Sm, hSm0, hSbound⟩ : ∃ Sm : ℝ, 0 ≤ Sm ∧ ∀ t ∈ Icc 0 T, ‖S t‖ ≤ Sm :=
    ⟨max Smax 0, le_max_right _ _, fun t ht => (hSmax t ht).trans (le_max_left _ _)⟩
  refine ⟨S, hS0, fun t ht => hS t ht, ?_⟩
  -- (2) Estimación principal
  have main : ∀ ε > 0, ∀ᶠ h in 𝓝 (0 : P), ∀ t ∈ Icc 0 T,
      ‖x (θ₀ + h) t - x θ₀ t - S t h‖ ≤ ε * ‖h‖ := by
    intro ε hε
    obtain ⟨CT, hCT, hCT0⟩ : ∃ CT : ℝ, CT = (Real.exp (M' * T) - 1) / M' ∧ 0 ≤ CT :=
      ⟨_, rfl, div_nonneg (by linarith [Real.one_le_exp (mul_nonneg hM'pos.le hT)]) hM'pos.le⟩
    obtain ⟨η, hη, hηdef⟩ : ∃ η : ℝ, 0 < η ∧ η * (Sm + 1) * CT ≤ ε := by
      refine ⟨ε / ((CT + 1) * (Sm + 1)), by positivity, ?_⟩
      have e : ε / ((CT + 1) * (Sm + 1)) * (Sm + 1) * CT = ε * (CT / (CT + 1)) := by
        field_simp
      rw [e]
      exact mul_le_of_le_one_right hε.le ((div_le_one (by positivity)).2 (by linarith))
    obtain ⟨δ₁, hδ₁, hδ₁1, hlin⟩ := uniform_linearization hf hK₀ hη
    obtain ⟨c, hc, hc0⟩ : ∃ c : ℝ, c = η * (Sm + 1) * CT ∧ 0 ≤ c := ⟨_, rfl, by positivity⟩
    obtain ⟨r, hr, hr1, hr2⟩ : ∃ r : ℝ, 0 < r ∧ (Sm + 1) * r ≤ δ₁ ∧ (c + Sm + 1) * r ≤ δ₁ / 2 := by
      refine ⟨min (δ₁ / (Sm + 1)) (δ₁ / (2 * (c + Sm + 1))), by positivity, ?_, ?_⟩
      · rw [mul_comm, ← le_div_iff₀ (by positivity)]; exact min_le_left _ _
      · rw [mul_comm, ← le_div_iff₀ (by positivity), div_div]; exact min_le_right _ _
    have htend : Tendsto (fun h : P => θ₀ + h) (𝓝 0) (𝓝 θ₀) := by
      simpa using (tendsto_const_nhds (x := θ₀)).add (tendsto_id (x := 𝓝 (0 : P)))
    filter_upwards [htend.eventually (hsol.and hinit), Metric.ball_mem_nhds (0 : P) hr]
      with h hsh hh
    obtain ⟨hsolh, hinith⟩ := hsh
    rw [mem_ball_zero_iff] at hh
    have hh1 : (Sm + 1) * ‖h‖ ≤ δ₁ :=
      le_trans (mul_le_mul_of_nonneg_left hh.le (by positivity)) hr1
    have hh2 : (c + Sm) * ‖h‖ < δ₁ / 2 := by
      have h1 : (c + Sm) * ‖h‖ ≤ (c + Sm) * r :=
        mul_le_mul_of_nonneg_left hh.le (by positivity)
      have h2 : (c + Sm) * r < (c + Sm + 1) * r := by linarith
      linarith
    have hhle : ‖h‖ ≤ (Sm + 1) * ‖h‖ := le_mul_of_one_le_left (norm_nonneg _) (by linarith)
    have hSmle : Sm * ‖h‖ ≤ (Sm + 1) * ‖h‖ :=
      mul_le_mul_of_nonneg_right (by linarith) (norm_nonneg _)
    have hhδ : ‖h‖ ≤ δ₁ := hhle.trans hh1
    have hSth : ∀ t ∈ Icc 0 T, ‖S t h‖ ≤ Sm * ‖h‖ := fun t ht =>
      ((S t).le_opNorm h).trans (mul_le_mul_of_nonneg_right (hSbound t ht) (norm_nonneg _))
    have hdiff : ∀ t ∈ Icc 0 T, ((x θ₀ t + S t h, θ₀ + h) : E × P) - (x θ₀ t, θ₀) = (S t h, h) :=
      fun t _ => by ext <;> simp
    have hwz : ∀ t ∈ Icc 0 T, ‖((x θ₀ t + S t h, θ₀ + h) : E × P) - (x θ₀ t, θ₀)‖
        ≤ (Sm + 1) * ‖h‖ := by
      intro t ht
      rw [hdiff t ht, Prod.norm_mk]
      exact max_le ((hSth t ht).trans hSmle) hhle
    have key := tube_gronwall (K := M') (ρ := δ₁) (σ := Sm * ‖h‖)
      (εg := η * (Sm + 1) * ‖h‖) hM'pos hT (fun y => f y (θ₀ + h)) (x θ₀) (x (θ₀ + h))
      (fun t => x θ₀ t + S t h)
      (fun t => f (x θ₀ t) θ₀ + ((fderiv ℝ g (x θ₀ t, θ₀)).comp (ContinuousLinearMap.inl ℝ E P)
          ∘L S t + (fderiv ℝ g (x θ₀ t, θ₀)).comp (ContinuousLinearMap.inr ℝ E P)) h)
      (fun t ht => lipschitzOn_slice f (hg ▸ hf) (θ₀ + h) (x θ₀ t) δ₁ (cthickening 1 K₀) M'
        (fun z hz => hg ▸ hMM' z hz) (fun y hy => by
          apply mem_cthickening_of_dist_le (y, θ₀ + h) (x θ₀ t, θ₀) 1 K₀ (hγK₀ t ht)
          rw [Prod.dist_eq]
          apply max_le
          · exact (mem_closedBall.1 hy).trans hδ₁1
          · rw [dist_self_add_left]; exact hhδ.trans hδ₁1))
      hx0cont hsolh
      (fun t ht => by
        have h1 := (hS t ht).clm_apply (hasDerivWithinAt_const t (Icc 0 T) h)
        simpa using (hsol0 t ht).add h1)
      (fun t ht => by
        have hl := hlin (x θ₀ t, θ₀) (hγK₀ t ht) (x θ₀ t + S t h, θ₀ + h) ((hwz t ht).trans hh1)
        rw [hdiff t ht] at hl
        rw [dist_comm, dist_eq_norm]
        have hsplit := clm_prod_apply_split (fderiv ℝ g (x θ₀ t, θ₀)) (S t h) h
        have hgv : ∀ a b, g (a, b) = f a b := fun a b => by rw [hg]
        rw [hgv, hgv, hsplit] at hl
        have heq : f (x θ₀ t + S t h) (θ₀ + h) - (f (x θ₀ t) θ₀
            + ((fderiv ℝ g (x θ₀ t, θ₀)).comp (ContinuousLinearMap.inl ℝ E P) ∘L S t
              + (fderiv ℝ g (x θ₀ t, θ₀)).comp (ContinuousLinearMap.inr ℝ E P)) h)
            = f (x θ₀ t + S t h) (θ₀ + h) - f (x θ₀ t) θ₀
              - ((fderiv ℝ g (x θ₀ t, θ₀)).comp (ContinuousLinearMap.inl ℝ E P) (S t h)
                + (fderiv ℝ g (x θ₀ t, θ₀)).comp (ContinuousLinearMap.inr ℝ E P) h) := by
          simp only [ContinuousLinearMap.add_apply, ContinuousLinearMap.comp_apply]; abel
        rw [heq]
        refine hl.trans ?_
        rw [Prod.norm_mk]
        calc η * max ‖S t h‖ ‖h‖ ≤ η * ((Sm + 1) * ‖h‖) :=
              mul_le_mul_of_nonneg_left (max_le ((hSth t ht).trans hSmle) hhle) hη.le
          _ = η * (Sm + 1) * ‖h‖ := by ring)
      (fun t ht => by rw [dist_self_add_left]; exact hSth t ht)
      (hSmle.trans hh1)
      (by simp [hinith, hS0])
      (by positivity)
      (by
        rw [← hCT]
        have : η * (Sm + 1) * ‖h‖ * CT + Sm * ‖h‖ = (c + Sm) * ‖h‖ := by rw [hc]; ring
        rw [this]; exact hh2)
    intro t ht
    have hk := key t ht
    rw [← hCT, dist_eq_norm] at hk
    have : x (θ₀ + h) t - x θ₀ t - S t h = x (θ₀ + h) t - (x θ₀ t + S t h) := by abel
    rw [this]
    refine hk.trans ?_
    calc η * (Sm + 1) * ‖h‖ * CT = (η * (Sm + 1) * CT) * ‖h‖ := by ring
      _ ≤ ε * ‖h‖ := mul_le_mul_of_nonneg_right hηdef (norm_nonneg _)
  intro t ht
  rw [hasFDerivAt_iff_isLittleO_nhds_zero, isLittleO_iff]
  intro ε hε
  filter_upwards [main ε hε] with h hh
  exact hh t ht

end Main

end ODEParamDiff

