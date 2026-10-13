import CertifiedODEReduction
import CosineCertificate
import SensitivityLipschitz

/-!
# Certificado de cos Δ para la EDO, con `Lc` acotado formalmente

Une `ParamDiffODE` (sensibilidad en cada `θ`), `SensitivityLipschitz` (la sensibilidad es
Lipschitz en `θ` con constante explícita) y `CosineCertificate` (certificado de cos Δ para
perturbaciones finitas). La constante `Lc` deja de ser un dato: es

  `Lc = √N · M₂ e² (e − 1) / M₁`,   `e = exp(M₁ T)`,

con `M₁`, `M₂` cotas de la primera y la segunda derivada de `f` en una región convexa `K` que
contiene las trayectorias, y `N` el número de instantes de muestreo.
-/

open Set Filter Topology Metric FirstOrderErrorBound TrajectoryErrorBound ODEParamDiff
  CertifiedODEReduction CosineCertificate SensitivityLipschitz

namespace CertifiedFiniteODE

variable {n p N : ℕ}

/-- Coordenada `i` de un vector de `ℝⁿ` como forma lineal continua. -/
noncomputable def coord (i : Fin n) : EuclideanSpace ℝ (Fin n) →L[ℝ] ℝ :=
  (ContinuousLinearMap.proj i).comp
    ((EuclideanSpace.equiv (Fin n) ℝ : EuclideanSpace ℝ (Fin n) ≃L[ℝ] (Fin n → ℝ)) :
      EuclideanSpace ℝ (Fin n) →L[ℝ] (Fin n → ℝ))

/-- Derivada de la trayectoria muestreada construida a partir de la sensibilidad `S`. -/
noncomputable def sampledCLM (S : ℝ → (EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin n)))
    (tk : Fin N → ℝ) : EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin (N * n)) :=
  ((EuclideanSpace.equiv (Fin (N * n)) ℝ).symm :
      (Fin (N * n) → ℝ) →L[ℝ] EuclideanSpace ℝ (Fin (N * n))).comp
    (ContinuousLinearMap.pi fun i =>
      (coord (finProdFinEquiv.symm i).2).comp (S (tk (finProdFinEquiv.symm i).1)))

lemma sampledCLM_apply (S : ℝ → (EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin n)))
    (tk : Fin N → ℝ) (u : EuclideanSpace ℝ (Fin p)) (i : Fin (N * n)) :
    sampledCLM S tk u i = S (tk (finProdFinEquiv.symm i).1) u (finProdFinEquiv.symm i).2 := rfl

lemma hasFDerivAt_sampled (x : EuclideanSpace ℝ (Fin p) → ℝ → EuclideanSpace ℝ (Fin n))
    (tk : Fin N → ℝ) (θ : EuclideanSpace ℝ (Fin p))
    (S : ℝ → (EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin n)))
    (hS : ∀ k, HasFDerivAt (fun θ => x θ (tk k)) (S (tk k)) θ) :
    HasFDerivAt (sampled x tk) (sampledCLM S tk) θ := by
  have hG : HasFDerivAt (fun θ => fun i : Fin (N * n) =>
      x θ (tk (finProdFinEquiv.symm i).1) (finProdFinEquiv.symm i).2)
      (ContinuousLinearMap.pi fun i =>
        (coord (finProdFinEquiv.symm i).2).comp (S (tk (finProdFinEquiv.symm i).1))) θ := by
    rw [hasFDerivAt_pi]
    intro i
    exact (coord _).hasFDerivAt.comp θ (hS _)
  exact (EuclideanSpace.equiv (Fin (N * n)) ℝ).symm.hasFDerivAt.comp θ hG

lemma jacobianOf_sampledCLM (S : ℝ → (EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin n)))
    (tk : Fin N → ℝ) : jacobianOf (sampledCLM S tk) = sensMatrix S tk := by
  funext i j; rfl

/-- **Paso 4.** Si `‖S(t_k) − S'(t_k)‖ ≤ B` para todo `k`, entonces
`‖sampledCLM S − sampledCLM S'‖ ≤ √N · B`. -/
theorem sampledCLM_sub_le (S S' : ℝ → (EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin n)))
    (tk : Fin N → ℝ) {B : ℝ} (hB0 : 0 ≤ B) (hB : ∀ k, ‖S (tk k) - S' (tk k)‖ ≤ B) :
    ‖sampledCLM S tk - sampledCLM S' tk‖ ≤ Real.sqrt N * B := by
  refine ContinuousLinearMap.opNorm_le_bound _ (by positivity) fun u => ?_
  have hsq : ‖(sampledCLM S tk - sampledCLM S' tk) u‖ ^ 2
      = ∑ k : Fin N, ‖(S (tk k) - S' (tk k)) u‖ ^ 2 := by
    rw [EuclideanSpace.norm_sq_eq, ← (finProdFinEquiv : Fin N × Fin n ≃ Fin (N * n)).sum_comp,
      Fintype.sum_prod_type]
    apply Finset.sum_congr rfl
    intro k _
    rw [EuclideanSpace.norm_sq_eq]
    apply Finset.sum_congr rfl
    intro s _
    simp only [ContinuousLinearMap.sub_apply, PiLp.sub_apply, sampledCLM_apply]
    have hks : (finProdFinEquiv : Fin N × Fin n ≃ Fin (N * n)).symm
        (finProdFinEquiv (k, s)) = (k, s) := Equiv.symm_apply_apply _ _
    rw [hks]
  have hk : ∀ k, ‖(S (tk k) - S' (tk k)) u‖ ^ 2 ≤ B ^ 2 * ‖u‖ ^ 2 := fun k => by
    rw [← mul_pow]
    exact pow_le_pow_left₀ (norm_nonneg _)
      (((S (tk k) - S' (tk k)).le_opNorm u).trans
        (mul_le_mul_of_nonneg_right (hB k) (norm_nonneg _))) 2
  have hsum : ‖(sampledCLM S tk - sampledCLM S' tk) u‖ ^ 2 ≤ (Real.sqrt N * B * ‖u‖) ^ 2 := by
    rw [hsq, mul_pow, mul_pow, Real.sq_sqrt (Nat.cast_nonneg N)]
    calc ∑ k : Fin N, ‖(S (tk k) - S' (tk k)) u‖ ^ 2 ≤ ∑ _k : Fin N, B ^ 2 * ‖u‖ ^ 2 :=
          Finset.sum_le_sum fun k _ => hk k
      _ = N * B ^ 2 * ‖u‖ ^ 2 := by simp [Finset.sum_const, Finset.card_univ]; ring
  exact (pow_le_pow_iff_left₀ (norm_nonneg _) (by positivity) two_ne_zero).1 hsum

/-- **Certificado de cos Δ para la EDO (Lc formal).**

Hipótesis:
* `f` es C¹ en un abierto `U`; `K ⊆ U` es convexo y en `K` se cumple `‖Df‖ ≤ M₁` y
  `‖Df z − Df z'‖ ≤ M₂ ‖z − z'‖`;
* las soluciones existen en `[0, T]` para `θ` en un abierto `Θ ⊇ B(θ₀, ρ₀)`, con el mismo dato
  inicial, y `(x(θ,t), θ) ∈ K` para `θ ∈ B(θ₀, ρ₀)`;
* los instantes `t_k` están en `[0, T]`.

Conclusión: existe la sensibilidad `S₀` en `θ₀` (con `S₀ 0 = 0`, la derivada de la
trayectoria) tal que, para toda perturbación `h` con `‖h‖ ≤ ρ₀`, todo conjunto `Sset` y todo
`c > 0`, si con `J = sensMatrix S₀`, `Lc = √N · M₂ e² (e − 1)/M₁`
  `(√R(Sset) ‖h_{Sᶜ}‖ + 2 Lc ‖h‖²)² ≤ (1 − c²)(‖J h‖ − Lc ‖h‖²)²` y `‖J h‖ > Lc ‖h‖²`,
entonces `cos Δ ≥ c` para la trayectoria muestreada. -/
theorem certified_cos_ode
    (f : EuclideanSpace ℝ (Fin n) → EuclideanSpace ℝ (Fin p) → EuclideanSpace ℝ (Fin n))
    {U : Set (EuclideanSpace ℝ (Fin n) × EuclideanSpace ℝ (Fin p))} (hU : IsOpen U)
    (hf : ContDiffOn ℝ 1 (fun z : EuclideanSpace ℝ (Fin n) × EuclideanSpace ℝ (Fin p) =>
      f z.1 z.2) U)
    {K : Set (EuclideanSpace ℝ (Fin n) × EuclideanSpace ℝ (Fin p))} (hKconv : Convex ℝ K)
    (hKU : K ⊆ U) {M₁ M₂ : ℝ} (hM₁ : 0 < M₁) (hM₂ : 0 ≤ M₂)
    (hM1 : ∀ z ∈ K, ‖fderiv ℝ (fun z : EuclideanSpace ℝ (Fin n) × EuclideanSpace ℝ (Fin p) =>
      f z.1 z.2) z‖ ≤ M₁)
    (hM2 : ∀ z ∈ K, ∀ z' ∈ K,
      ‖fderiv ℝ (fun z : EuclideanSpace ℝ (Fin n) × EuclideanSpace ℝ (Fin p) => f z.1 z.2) z
        - fderiv ℝ (fun z : EuclideanSpace ℝ (Fin n) × EuclideanSpace ℝ (Fin p) =>
          f z.1 z.2) z'‖ ≤ M₂ * ‖z - z'‖)
    {T : ℝ} (hT : 0 ≤ T) (x : EuclideanSpace ℝ (Fin p) → ℝ → EuclideanSpace ℝ (Fin n))
    (θ₀ : EuclideanSpace ℝ (Fin p)) {ρ₀ : ℝ}
    {Θ : Set (EuclideanSpace ℝ (Fin p))} (hΘ : IsOpen Θ) (hBΘ : closedBall θ₀ ρ₀ ⊆ Θ)
    (hsol : ∀ θ ∈ Θ, ∀ t ∈ Icc 0 T, HasDerivWithinAt (x θ) (f (x θ t) θ) (Icc 0 T) t)
    (hinit : ∀ θ ∈ Θ, x θ 0 = x θ₀ 0)
    (hK : ∀ θ ∈ closedBall θ₀ ρ₀, ∀ t ∈ Icc 0 T, (x θ t, θ) ∈ K)
    (tk : Fin N → ℝ) (htk : ∀ k, tk k ∈ Icc 0 T) (hρ₀ : 0 ≤ ρ₀) :
    ∃ S₀ : ℝ → (EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin n)),
      S₀ 0 = 0 ∧ (∀ t ∈ Icc 0 T, HasFDerivAt (fun θ => x θ t) (S₀ t) θ₀) ∧
      ∀ (Sset : Finset (Fin p)) (h : EuclideanSpace ℝ (Fin p)) {c : ℝ}, ‖h‖ ≤ ρ₀ → 0 < c →
        let e := Real.exp (M₁ * T)
        let Lc := Real.sqrt N * (M₂ * e * e * ((e - 1) / M₁))
        0 < ‖sampledCLM S₀ tk h‖ - Lc * ‖h‖ ^ 2 →
        (Real.sqrt (removedColumnEnergy (sensMatrix S₀ tk) Sset)
            * Real.sqrt (removedParamSq Sset (fun j => h j)) + 2 * Lc * ‖h‖ ^ 2) ^ 2
          ≤ (1 - c ^ 2) * (‖sampledCLM S₀ tk h‖ - Lc * ‖h‖ ^ 2) ^ 2 →
        sampled x tk (θ₀ + keepS Sset h) - sampled x tk θ₀ ≠ 0 ∧
        c ≤ inner ℝ (sampled x tk (θ₀ + h) - sampled x tk θ₀)
              (sampled x tk (θ₀ + keepS Sset h) - sampled x tk θ₀)
          / (‖sampled x tk (θ₀ + h) - sampled x tk θ₀‖
              * ‖sampled x tk (θ₀ + keepS Sset h) - sampled x tk θ₀‖) := by
  set g := fun z : EuclideanSpace ℝ (Fin n) × EuclideanSpace ℝ (Fin p) => f z.1 z.2 with hg
  have hdiff : ∀ z ∈ K, HasFDerivAt g (fderiv ℝ g z) z := fun z hz =>
    ((hf.contDiffAt (hU.mem_nhds (hKU hz))).differentiableAt le_rfl).hasFDerivAt
  -- sensibilidad en cada θ de la bola
  have hex : ∀ θ ∈ closedBall θ₀ ρ₀, ∃ S : ℝ → (EuclideanSpace ℝ (Fin p) →L[ℝ]
      EuclideanSpace ℝ (Fin n)), S 0 = 0 ∧
      (∀ t ∈ Icc 0 T, HasDerivWithinAt S
        ((fderiv ℝ g (x θ t, θ)).comp (ContinuousLinearMap.inl ℝ _ _) ∘L S t
          + (fderiv ℝ g (x θ t, θ)).comp (ContinuousLinearMap.inr ℝ _ _)) (Icc 0 T) t) ∧
      ∀ t ∈ Icc 0 T, HasFDerivAt (fun θ => x θ t) (S t) θ := by
    intro θ hθ
    have hθΘ : Θ ∈ 𝓝 θ := hΘ.mem_nhds (hBΘ hθ)
    exact hasFDerivAt_solution_param_on f hU hf hT x θ
      (fun t ht => hKU (hK θ hθ t ht))
      (Filter.mem_of_superset hθΘ fun θ' hθ' => hsol θ' hθ')
      (Filter.mem_of_superset hθΘ fun θ' hθ' => by
        show x θ' 0 = x θ 0
        rw [hinit θ' hθ', hinit θ (hBΘ hθ)])
  choose! Sf hSf0 hSfvar hSfder using hex
  have hθ₀ : θ₀ ∈ closedBall θ₀ ρ₀ := mem_closedBall_self hρ₀
  refine ⟨Sf θ₀, hSf0 θ₀ hθ₀, hSfder θ₀ hθ₀, ?_⟩
  intro Sset h c hh hc e Lc hA hcert
  have he1 : 1 ≤ e := Real.one_le_exp (mul_nonneg hM₁.le hT)
  have hLs0 : 0 ≤ M₂ * e * e * ((e - 1) / M₁) := by
    apply mul_nonneg (by positivity) (div_nonneg (by linarith) hM₁.le)
  have hLc0 : 0 ≤ Lc := mul_nonneg (Real.sqrt_nonneg _) hLs0
  -- derivada de la trayectoria muestreada en cada θ de la bola
  have hDF : ∀ θ ∈ closedBall θ₀ ρ₀,
      HasFDerivAt (sampled x tk) (sampledCLM (Sf θ) tk) θ := fun θ hθ =>
    hasFDerivAt_sampled x tk θ (Sf θ) (fun k => hSfder θ hθ (tk k) (htk k))
  -- Lipschitz de la derivada
  have hLip : ∀ θ ∈ closedBall θ₀ ρ₀,
      ‖sampledCLM (Sf θ) tk - sampledCLM (Sf θ₀) tk‖ ≤ Lc * ‖θ - θ₀‖ := by
    intro θ hθ
    have hsl := sens_lipschitz g (fderiv ℝ g) K hKconv hdiff hM₁ hM₂ hM1 hM2 x θ θ₀
      (fun t ht => hsol θ (hBΘ hθ) t ht) (fun t ht => hsol θ₀ (hBΘ hθ₀) t ht)
      (by rw [hinit θ (hBΘ hθ)]) (hK θ hθ) (hK θ₀ hθ₀) (Sf θ) (Sf θ₀)
      (hSfvar θ hθ) (hSfvar θ₀ hθ₀) (hSf0 θ hθ) (hSf0 θ₀ hθ₀)
    have := sampledCLM_sub_le (Sf θ) (Sf θ₀) tk (B := ‖θ - θ₀‖ * (M₂ * e * e * ((e - 1) / M₁)))
      (by positivity) (fun k => hsl (tk k) (htk k))
    calc _ ≤ Real.sqrt N * (‖θ - θ₀‖ * (M₂ * e * e * ((e - 1) / M₁))) := this
      _ = Lc * ‖θ - θ₀‖ := by ring
  have hcos := finite_cos_certificate (sampled x tk) (fun θ => sampledCLM (Sf θ) tk) θ₀
    hLc0 hc hDF hLip Sset h hh hA (by rw [jacobianOf_sampledCLM]; exact hcert)
  exact hcos

end CertifiedFiniteODE

