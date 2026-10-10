import CertifiedFiniteODE

/-!
# Certificados de cos Δ con el error lineal exacto y versión local (sin `Lc`)

Dos refinamientos de `CosineCertificate`:

* **(A1) Error lineal exacto.** En lugar de la cota de Cauchy–Schwarz
  `‖J_{Sᶜ} h_{Sᶜ}‖ ≤ √R(S) ‖h_{Sᶜ}‖`, se usa directamente `‖J (h − h_S)‖`, que es calculable
  para cada escenario y nunca es peor:
  - `finite_trajectory_error_exact`:
    `‖F(θ₀+h) − F(θ₀+h_S)‖ ≤ ‖J(h − h_S)‖ + 2 Lc ‖h‖²`;
  - `finite_cos_certificate_exact`: certificado de cos Δ con ese término;
  - `certified_cos_ode_exact`: la versión para la EDO con `Lc` formal.

* **(A2) Certificado local.** Para una dirección fija `h`, si `J h ≠ 0` y `J h_S ≠ 0`,
  `cos Δ(s h) → cos(J h, J h_S)` cuando `s → 0⁺` (`tendsto_cos_delta`). Por tanto, si el coseno
  *lineal* (calculado con la matriz de sensibilidad) supera `c`, entonces `cos Δ(s h) > c` para
  toda perturbación suficientemente pequeña en esa dirección (`eventually_cos_delta_gt`), sin
  necesidad de conocer `Lc`. `local_cos_ode` es la versión para la EDO.
-/

open Set Filter Topology Metric FirstOrderErrorBound TrajectoryErrorBound ODEParamDiff
  CertifiedODEReduction CosineCertificate SensitivityLipschitz CertifiedFiniteODE

namespace ExactLinearCertificate

/-- Coseno entre dos vectores (con el convenio `0/0 = 0` de Lean). -/
noncomputable def cosv {W : Type*} [NormedAddCommGroup W] [InnerProductSpace ℝ W]
    (a b : W) : ℝ :=
  inner ℝ a b / (‖a‖ * ‖b‖)

section Generic

variable {W : Type*} [NormedAddCommGroup W] [InnerProductSpace ℝ W]

/-- **Lema genérico de certificado.** Si `0 < A ≤ ‖a‖`, `‖a − b‖ ≤ e` y `e² ≤ (1 − c²) A²` con
`c > 0`, entonces `b ≠ 0` y `cos(a, b) ≥ c`. -/
theorem cos_certificate_of_bounds (a b : W) {A e c : ℝ} (hc : 0 < c) (hA : 0 < A)
    (hAa : A ≤ ‖a‖) (he : ‖a - b‖ ≤ e) (hcert : e ^ 2 ≤ (1 - c ^ 2) * A ^ 2) :
    b ≠ 0 ∧ c ≤ cosv a b := by
  have hapos : 0 < ‖a‖ := lt_of_lt_of_le hA hAa
  have he0 : 0 ≤ e := (norm_nonneg _).trans he
  set ε := e / ‖a‖ with hεdef
  have hε0 : 0 ≤ ε := div_nonneg he0 hapos.le
  have hrel : ‖a - b‖ ≤ ε * ‖a‖ := by rw [hεdef, div_mul_cancel₀ _ hapos.ne']; exact he
  have hc1 : c ^ 2 ≤ 1 := by
    by_contra hcon; push_neg at hcon
    have : (1 - c ^ 2) * A ^ 2 < 0 :=
      mul_neg_of_neg_of_pos (by linarith) (sq_pos_of_pos hA)
    nlinarith [sq_nonneg e]
  have hce : c ^ 2 + ε ^ 2 ≤ 1 := by
    have hA2 : A ^ 2 ≤ ‖a‖ ^ 2 := pow_le_pow_left₀ hA.le hAa 2
    have : e ^ 2 ≤ (1 - c ^ 2) * ‖a‖ ^ 2 :=
      hcert.trans (mul_le_mul_of_nonneg_left hA2 (by linarith))
    have hε2 : ε ^ 2 = e ^ 2 / ‖a‖ ^ 2 := by rw [hεdef, div_pow]
    rw [hε2]
    have : e ^ 2 / ‖a‖ ^ 2 ≤ 1 - c ^ 2 := by
      rw [div_le_iff₀ (by positivity)]; linarith
    linarith
  have hε1 : ε < 1 := by
    have : ε ^ 2 < 1 := by nlinarith [sq_pos_of_pos hc]
    nlinarith
  exact cos_ge_of_rel_error a b hc.le hε0 hε1 hce hrel (norm_pos_iff.1 hapos)

/-- `cosv` es invariante por un mismo reescalado positivo de ambos vectores. -/
lemma cosv_smul (a b : W) {r : ℝ} (hr : 0 < r) : cosv (r • a) (r • b) = cosv a b := by
  unfold cosv
  rw [inner_smul_left, inner_smul_right, norm_smul, norm_smul, Real.norm_eq_abs,
    abs_of_pos hr]
  simp only [RCLike.conj_to_real]
  by_cases h : ‖a‖ * ‖b‖ = 0
  · have : r * ‖a‖ * (r * ‖b‖) = 0 := by
      calc r * ‖a‖ * (r * ‖b‖) = r * r * (‖a‖ * ‖b‖) := by ring
        _ = 0 := by rw [h, mul_zero]
    rw [this, h, div_zero, div_zero]
  · field_simp

/-- `cosv` es continua en todo par de vectores no nulos. -/
lemma continuousAt_cosv {a b : W} (ha : a ≠ 0) (hb : b ≠ 0) :
    ContinuousAt (fun z : W × W => cosv z.1 z.2) (a, b) := by
  unfold cosv
  apply ContinuousAt.div
  · exact (continuous_fst.inner continuous_snd).continuousAt
  · exact ((continuous_norm.comp continuous_fst).mul
      (continuous_norm.comp continuous_snd)).continuousAt
  · exact mul_ne_zero (norm_ne_zero_iff.2 ha) (norm_ne_zero_iff.2 hb)

end Generic

variable {m p : ℕ}

/-- `keepS` es lineal: `(s h)_S = s h_S`. -/
lemma keepS_smul (S : Finset (Fin p)) (s : ℝ) (h : EuclideanSpace ℝ (Fin p)) :
    keepS S (s • h) = s • keepS S h := by
  ext j
  simp only [keepS_apply, PiLp.smul_apply, smul_eq_mul]
  split_ifs <;> simp

/-! ## A1. Error lineal exacto -/

/-- El término lineal exacto es la norma del vector `∑_{j ∉ S} J_{·j} h_j`, calculable
directamente con la matriz de sensibilidad. -/
theorem norm_linear_part_eq
    (L : EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin m))
    (S : Finset (Fin p)) (h : EuclideanSpace ℝ (Fin p)) :
    ‖L h - L (keepS S h)‖
      = Real.sqrt (∑ i, (∑ j ∈ removedSet S, jacobianOf L i j * h j) ^ 2) := by
  rw [EuclideanSpace.norm_eq]
  congr 1
  apply Finset.sum_congr rfl
  intro i _
  rw [Real.norm_eq_abs, sq_abs, PiLp.sub_apply, clm_apply_eq_linResponse,
    clm_keepS_eq_reducedResponse, response_sub_reduced]

/-- **(A1) Cota explícita con el error lineal exacto.** Para todo `‖h‖ ≤ ρ₀`:
`‖F(θ₀+h) − F(θ₀+h_S)‖ ≤ ‖J (h − h_S)‖ + 2 Lc ‖h‖²`, con `J = DF(θ₀)`. -/
theorem finite_trajectory_error_exact
    (F : EuclideanSpace ℝ (Fin p) → EuclideanSpace ℝ (Fin m))
    (DF : EuclideanSpace ℝ (Fin p) → (EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin m)))
    (θ₀ : EuclideanSpace ℝ (Fin p)) {ρ₀ Lc : ℝ} (hLc : 0 ≤ Lc)
    (hDF : ∀ θ ∈ closedBall θ₀ ρ₀, HasFDerivAt F (DF θ) θ)
    (hLip : ∀ θ ∈ closedBall θ₀ ρ₀, ‖DF θ - DF θ₀‖ ≤ Lc * ‖θ - θ₀‖)
    (S : Finset (Fin p)) (h : EuclideanSpace ℝ (Fin p)) (hh : ‖h‖ ≤ ρ₀) :
    ‖F (θ₀ + h) - F (θ₀ + keepS S h)‖
      ≤ ‖DF θ₀ h - DF θ₀ (keepS S h)‖ + 2 * Lc * ‖h‖ ^ 2 := by
  have hk := norm_keepS_le S h
  have t1 := taylor_bound F DF θ₀ hLc hDF hLip h hh
  have t2 := taylor_bound F DF θ₀ hLc hDF hLip (keepS S h) (hk.trans hh)
  have hsq : ‖keepS S h‖ ^ 2 ≤ ‖h‖ ^ 2 := pow_le_pow_left₀ (norm_nonneg _) hk 2
  have e : F (θ₀ + h) - F (θ₀ + keepS S h)
      = (DF θ₀ h - DF θ₀ (keepS S h)) + (F (θ₀ + h) - F θ₀ - DF θ₀ h)
        - (F (θ₀ + keepS S h) - F θ₀ - DF θ₀ (keepS S h)) := by abel
  rw [e]
  calc _ ≤ ‖DF θ₀ h - DF θ₀ (keepS S h)‖ + ‖F (θ₀ + h) - F θ₀ - DF θ₀ h‖
          + ‖F (θ₀ + keepS S h) - F θ₀ - DF θ₀ (keepS S h)‖ :=
        (norm_sub_le _ _).trans (add_le_add_right (norm_add_le _ _) _)
    _ ≤ _ := by nlinarith [mul_le_mul_of_nonneg_left hsq hLc]

/-- La cota exacta nunca es peor que la de `R(S)`. -/
theorem exact_le_Rvar_bound
    (L : EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin m))
    (S : Finset (Fin p)) (h : EuclideanSpace ℝ (Fin p)) :
    ‖L h - L (keepS S h)‖
      ≤ Real.sqrt (removedColumnEnergy (jacobianOf L) S)
          * Real.sqrt (removedParamSq S (fun j => h j)) :=
  linear_part_bound L S h

/-- **(A1) Certificado de cos Δ con el error lineal exacto.** Con
`e := ‖J(h − h_S)‖ + 2 Lc ‖h‖²` y `A := ‖J h‖ − Lc ‖h‖²`: si `0 < A`, `0 < c` y
`e² ≤ (1 − c²) A²`, entonces `Δx_sel ≠ 0` y `cos Δ ≥ c`. -/
theorem finite_cos_certificate_exact
    (F : EuclideanSpace ℝ (Fin p) → EuclideanSpace ℝ (Fin m))
    (DF : EuclideanSpace ℝ (Fin p) → (EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin m)))
    (θ₀ : EuclideanSpace ℝ (Fin p)) {ρ₀ Lc c : ℝ} (hLc : 0 ≤ Lc) (hc : 0 < c)
    (hDF : ∀ θ ∈ closedBall θ₀ ρ₀, HasFDerivAt F (DF θ) θ)
    (hLip : ∀ θ ∈ closedBall θ₀ ρ₀, ‖DF θ - DF θ₀‖ ≤ Lc * ‖θ - θ₀‖)
    (S : Finset (Fin p)) (h : EuclideanSpace ℝ (Fin p)) (hh : ‖h‖ ≤ ρ₀)
    (hA : 0 < ‖DF θ₀ h‖ - Lc * ‖h‖ ^ 2)
    (hcert : (‖DF θ₀ h - DF θ₀ (keepS S h)‖ + 2 * Lc * ‖h‖ ^ 2) ^ 2
        ≤ (1 - c ^ 2) * (‖DF θ₀ h‖ - Lc * ‖h‖ ^ 2) ^ 2) :
    F (θ₀ + keepS S h) - F θ₀ ≠ 0 ∧
      c ≤ cosv (F (θ₀ + h) - F θ₀) (F (θ₀ + keepS S h) - F θ₀) := by
  have hA' : ‖DF θ₀ h‖ - Lc * ‖h‖ ^ 2 ≤ ‖F (θ₀ + h) - F θ₀‖ := by
    have t1 := taylor_bound F DF θ₀ hLc hDF hLip h hh
    have e : DF θ₀ h = (F (θ₀ + h) - F θ₀) - (F (θ₀ + h) - F θ₀ - DF θ₀ h) := by abel
    have key : ‖DF θ₀ h‖ ≤ ‖F (θ₀ + h) - F θ₀‖ + ‖F (θ₀ + h) - F θ₀ - DF θ₀ h‖ := by
      calc ‖DF θ₀ h‖ = ‖(F (θ₀ + h) - F θ₀) - (F (θ₀ + h) - F θ₀ - DF θ₀ h)‖ :=
            congrArg _ e
        _ ≤ _ := norm_sub_le _ _
    linarith
  have herr : ‖(F (θ₀ + h) - F θ₀) - (F (θ₀ + keepS S h) - F θ₀)‖
      ≤ ‖DF θ₀ h - DF θ₀ (keepS S h)‖ + 2 * Lc * ‖h‖ ^ 2 := by
    rw [sub_sub_sub_cancel_right]
    exact finite_trajectory_error_exact F DF θ₀ hLc hDF hLip S h hh
  exact cos_certificate_of_bounds _ _ hc hA hA' herr hcert

/-- **(A1) Certificado de cos Δ para la EDO con el error lineal exacto y `Lc` formal.**
Mismas hipótesis que `certified_cos_ode`; la condición del certificado usa `‖J(h − h_S)‖`. -/
theorem certified_cos_ode_exact {n N : ℕ}
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
        let J := sampledCLM S₀ tk
        0 < ‖J h‖ - Lc * ‖h‖ ^ 2 →
        (‖J h - J (keepS Sset h)‖ + 2 * Lc * ‖h‖ ^ 2) ^ 2
          ≤ (1 - c ^ 2) * (‖J h‖ - Lc * ‖h‖ ^ 2) ^ 2 →
        sampled x tk (θ₀ + keepS Sset h) - sampled x tk θ₀ ≠ 0 ∧
        c ≤ cosv (sampled x tk (θ₀ + h) - sampled x tk θ₀)
              (sampled x tk (θ₀ + keepS Sset h) - sampled x tk θ₀) := by
  set g := fun z : EuclideanSpace ℝ (Fin n) × EuclideanSpace ℝ (Fin p) => f z.1 z.2 with hg
  have hdiff : ∀ z ∈ K, HasFDerivAt g (fderiv ℝ g z) z := fun z hz =>
    ((hf.contDiffAt (hU.mem_nhds (hKU hz))).differentiableAt le_rfl).hasFDerivAt
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
  intro Sset h c hh hc e Lc J hA hcert
  have he1 : 1 ≤ e := Real.one_le_exp (mul_nonneg hM₁.le hT)
  have hLs0 : 0 ≤ M₂ * e * e * ((e - 1) / M₁) := by
    apply mul_nonneg (by positivity) (div_nonneg (by linarith) hM₁.le)
  have hLc0 : 0 ≤ Lc := mul_nonneg (Real.sqrt_nonneg _) hLs0
  have hDF : ∀ θ ∈ closedBall θ₀ ρ₀,
      HasFDerivAt (sampled x tk) (sampledCLM (Sf θ) tk) θ := fun θ hθ =>
    hasFDerivAt_sampled x tk θ (Sf θ) (fun k => hSfder θ hθ (tk k) (htk k))
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
  exact finite_cos_certificate_exact (sampled x tk) (fun θ => sampledCLM (Sf θ) tk) θ₀
    hLc0 hc hDF hLip Sset h hh hA hcert

/-! ## A2. Certificado local: límite de cos Δ cuando la perturbación tiende a cero -/

/-- **(A2) Límite de cos Δ.** Si `F` es diferenciable en `θ₀` con derivada `J`, y `J h ≠ 0`,
`J h_S ≠ 0`, entonces
`cos Δ(s h) = cos(F(θ₀+s h) − F(θ₀), F(θ₀+s h_S) − F(θ₀)) → cos(J h, J h_S)` cuando `s → 0⁺`. -/
theorem tendsto_cos_delta
    (F : EuclideanSpace ℝ (Fin p) → EuclideanSpace ℝ (Fin m))
    (J : EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin m))
    (θ₀ : EuclideanSpace ℝ (Fin p)) (hF : HasFDerivAt F J θ₀)
    (S : Finset (Fin p)) (h : EuclideanSpace ℝ (Fin p))
    (hJh : J h ≠ 0) (hJhS : J (keepS S h) ≠ 0) :
    Tendsto (fun s : ℝ => cosv (F (θ₀ + s • h) - F θ₀) (F (θ₀ + keepS S (s • h)) - F θ₀))
      (𝓝[>] 0) (𝓝 (cosv (J h) (J (keepS S h)))) := by
  -- cociente incremental en la dirección v
  have hquot : ∀ v : EuclideanSpace ℝ (Fin p),
      Tendsto (fun s : ℝ => s⁻¹ • (F (θ₀ + s • v) - F θ₀)) (𝓝[>] 0) (𝓝 (J v)) := by
    intro v
    have := hF.lim v (c := fun s : ℝ => s⁻¹) (l := 𝓝[>] 0)
      (tendsto_norm_atTop_atTop.comp tendsto_inv_nhdsGT_zero)
    simpa only [inv_inv] using this
  have hpair := (hquot h).prodMk_nhds (hquot (keepS S h))
  have hc := (continuousAt_cosv hJh hJhS).tendsto.comp hpair
  apply hc.congr'
  filter_upwards [self_mem_nhdsWithin] with s hs
  simp only [Function.comp_apply]
  rw [cosv_smul _ _ (inv_pos.2 hs), keepS_smul]

/-- **(A2) Certificado local sin `Lc`.** Si el coseno lineal `cos(J h, J h_S)` (calculado con la
matriz de sensibilidad) es mayor que `c`, entonces `cos Δ(s h) > c` para todo `s > 0`
suficientemente pequeño. -/
theorem eventually_cos_delta_gt
    (F : EuclideanSpace ℝ (Fin p) → EuclideanSpace ℝ (Fin m))
    (J : EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin m))
    (θ₀ : EuclideanSpace ℝ (Fin p)) (hF : HasFDerivAt F J θ₀)
    (S : Finset (Fin p)) (h : EuclideanSpace ℝ (Fin p))
    (hJh : J h ≠ 0) (hJhS : J (keepS S h) ≠ 0) {c : ℝ}
    (hlin : c < cosv (J h) (J (keepS S h))) :
    ∀ᶠ s in 𝓝[>] (0 : ℝ),
      c < cosv (F (θ₀ + s • h) - F θ₀) (F (θ₀ + keepS S (s • h)) - F θ₀) :=
  (tendsto_cos_delta F J θ₀ hF S h hJh hJhS).eventually_const_lt hlin

/-- Forma explícita: existe `s₀ > 0` tal que `cos Δ(s h) > c` para todo `s ∈ (0, s₀)`. -/
theorem exists_cos_delta_gt
    (F : EuclideanSpace ℝ (Fin p) → EuclideanSpace ℝ (Fin m))
    (J : EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin m))
    (θ₀ : EuclideanSpace ℝ (Fin p)) (hF : HasFDerivAt F J θ₀)
    (S : Finset (Fin p)) (h : EuclideanSpace ℝ (Fin p))
    (hJh : J h ≠ 0) (hJhS : J (keepS S h) ≠ 0) {c : ℝ}
    (hlin : c < cosv (J h) (J (keepS S h))) :
    ∃ s₀ : ℝ, 0 < s₀ ∧ ∀ s ∈ Ioo 0 s₀,
      c < cosv (F (θ₀ + s • h) - F θ₀) (F (θ₀ + keepS S (s • h)) - F θ₀) := by
  obtain ⟨s₀, hs₀, hsub⟩ := (mem_nhdsGT_iff_exists_Ioo_subset).1
    (eventually_cos_delta_gt F J θ₀ hF S h hJh hJhS hlin)
  exact ⟨s₀, hs₀, fun s hs => hsub hs⟩

/-- **(A2) Versión para la EDO.** Si la solución es C¹ en un abierto alrededor de la trayectoria
nominal (`hγU`), las soluciones existen cerca de `θ₀` con el mismo dato inicial, y el coseno lineal
calculado con la matriz de sensibilidad muestreada supera `c`, entonces `cos Δ(s h) > c` para toda
perturbación suficientemente pequeña en la dirección `h`. No interviene `Lc`. -/
theorem local_cos_ode {n N : ℕ}
    (f : EuclideanSpace ℝ (Fin n) → EuclideanSpace ℝ (Fin p) → EuclideanSpace ℝ (Fin n))
    {U : Set (EuclideanSpace ℝ (Fin n) × EuclideanSpace ℝ (Fin p))} (hU : IsOpen U)
    (hf : ContDiffOn ℝ 1 (fun z : EuclideanSpace ℝ (Fin n) × EuclideanSpace ℝ (Fin p) =>
      f z.1 z.2) U)
    {T : ℝ} (hT : 0 ≤ T) (x : EuclideanSpace ℝ (Fin p) → ℝ → EuclideanSpace ℝ (Fin n))
    (θ₀ : EuclideanSpace ℝ (Fin p))
    (hγU : ∀ t ∈ Icc 0 T, (x θ₀ t, θ₀) ∈ U)
    (hsol : ∀ᶠ θ in 𝓝 θ₀, ∀ t ∈ Icc 0 T, HasDerivWithinAt (x θ) (f (x θ t) θ) (Icc 0 T) t)
    (hinit : ∀ᶠ θ in 𝓝 θ₀, x θ 0 = x θ₀ 0)
    (tk : Fin N → ℝ) (htk : ∀ k, tk k ∈ Icc 0 T) :
    ∃ S₀ : ℝ → (EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin n)),
      S₀ 0 = 0 ∧ (∀ t ∈ Icc 0 T, HasFDerivAt (fun θ => x θ t) (S₀ t) θ₀) ∧
      ∀ (Sset : Finset (Fin p)) (h : EuclideanSpace ℝ (Fin p)) {c : ℝ},
        sampledCLM S₀ tk h ≠ 0 → sampledCLM S₀ tk (keepS Sset h) ≠ 0 →
        c < cosv (sampledCLM S₀ tk h) (sampledCLM S₀ tk (keepS Sset h)) →
        ∃ s₀ : ℝ, 0 < s₀ ∧ ∀ s ∈ Ioo 0 s₀,
          c < cosv (sampled x tk (θ₀ + s • h) - sampled x tk θ₀)
                (sampled x tk (θ₀ + keepS Sset (s • h)) - sampled x tk θ₀) := by
  obtain ⟨S₀, hS0, -, hSder⟩ := hasFDerivAt_solution_param_on f hU hf hT x θ₀ hγU hsol hinit
  refine ⟨S₀, hS0, hSder, ?_⟩
  intro Sset h c h1 h2 hlin
  exact exists_cos_delta_gt (sampled x tk) (sampledCLM S₀ tk) θ₀
    (hasFDerivAt_sampled x tk θ₀ S₀ (fun k => hSder (tk k) (htk k))) Sset h h1 h2 hlin

end ExactLinearCertificate

#print axioms ExactLinearCertificate.certified_cos_ode_exact
#print axioms ExactLinearCertificate.tendsto_cos_delta
#print axioms ExactLinearCertificate.local_cos_ode
