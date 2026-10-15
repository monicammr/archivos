import SpectralConditioning

/-!
# Identificabilidad práctica del problema reducido (verosimilitud perfilada)

Respalda la nota suplementaria sobre la identificabilidad de los subconjuntos seleccionados.
Los parámetros libres del problema reducido son `S ∪ Θ_C` (en escala logarítmica, desplazamiento
`δ` respecto del mínimo `θ̂`); los demás están fijos en `θ₀`. `R δ` es el vector de residuos
escalados por el ruido (`y/σ − dato/σ`) en `θ̂ + δ`, de modo que `χ²(δ) = ‖R δ‖²` y

  `Δχ²(δ) = ‖R δ‖² − ‖R 0‖²`   (`dchi2`).

`A` es la matriz de sensibilidad de los residuos en `θ̂` y `R δ − R 0 − A δ` el resto no lineal.

Resultados:
* `dchi2_lower`: si `θ̂` es estacionario (`⟪R 0, A δ⟫ = 0`, ecuaciones normales) y el resto no
  lineal está acotado por `ε`, entonces `Δχ²(δ) ≥ (‖A δ‖ − ε)² − 2 ‖R 0‖ ε`.
* `info_of_inverse`, `info_of_matrix`: la **información perfilada** del parámetro `j`,
  `I_j = 1 / ((AᵀA)⁻¹)_{jj}`, cumple `I_j · δ_j² ≤ ‖A δ‖²` para todo `δ` (lo que los datos
  informan sobre `θ_j` cuando los demás parámetros libres compensan lo más posible).
* `dchi2_ge_of_coord`: con `t* = (ε + √(c + 2‖R 0‖ε)) / √I_j`, todo `δ` admisible con
  `|δ_j| ≥ t*` tiene `Δχ²(δ) ≥ c`.
* `confidence_coord_lt`: la región de confianza `{δ admisible : Δχ²(δ) < c}` está contenida en
  la franja `|δ_j| < t*`.
* `practically_identifiable`: si `t*` es menor que la distancia de `θ̂_j` a los límites a ambos
  lados, `θ_j` es **prácticamente identificable** (el perfil supera `c` a ambos lados dentro de
  los límites; definición de Raue et al. 2009 con `c = 3,84`).
* `tstar_linear`: con `ε = 0`, `t* = √(c · ((AᵀA)⁻¹)_{jj})`, el semiancho de Wald que se calcula
  numéricamente.
* `local_injective`: identificabilidad local sin hipótesis sobre los datos: si `‖A δ‖ ≥ σ‖δ‖` y
  el resto es `≤ M‖δ‖²`, la aplicación parámetros ↦ salidas es inyectiva en la bola
  `‖δ‖ < σ/M`.

Alcance: los teoremas son generales (cualquier `R`, `A`, `ε`). Para un modelo concreto, `ε`,
`I_j`, `‖R 0‖` y la estacionariedad de `θ̂` se calculan numéricamente; la conclusión es
condicional a esos valores, como en el resto de la formalización.
-/

namespace ProfileIdentifiability

open RealInnerProductSpace Matrix

variable {V W : Type*} [NormedAddCommGroup V] [InnerProductSpace ℝ V]
  [NormedAddCommGroup W] [InnerProductSpace ℝ W]

/-- Aumento del coste `χ² = ‖R‖²` respecto del de `δ = 0` (el mínimo `θ̂`). -/
def dchi2 (R : V → W) (δ : V) : ℝ := ‖R δ‖ ^ 2 - ‖R 0‖ ^ 2

/-- **Cota inferior de Δχ².** En un punto estacionario, con resto no lineal `≤ ε`:
`Δχ²(δ) ≥ (‖A δ‖ − ε)² − 2‖R 0‖ε` (si `ε ≤ ‖A δ‖`). -/
theorem dchi2_lower (R : V → W) (A : V →L[ℝ] W) {ε : ℝ} (δ : V)
    (hstat : ⟪R 0, A δ⟫ = 0) (hrem : ‖R δ - R 0 - A δ‖ ≤ ε) (hε : ε ≤ ‖A δ‖) :
    (‖A δ‖ - ε) ^ 2 - 2 * ‖R 0‖ * ε ≤ dchi2 R δ := by
  set ρ := R δ - R 0 - A δ with hρ
  have hR : R δ = R 0 + (A δ + ρ) := by rw [hρ]; abel
  have h1 : ‖R δ‖ ^ 2 = ‖R 0‖ ^ 2 + 2 * ⟪R 0, A δ + ρ⟫ + ‖A δ + ρ‖ ^ 2 := by
    rw [hR, norm_add_sq_real]
  have h2 : ⟪R 0, A δ + ρ⟫ = ⟪R 0, ρ⟫ := by rw [inner_add_right, hstat, zero_add]
  have h3 : |⟪R 0, ρ⟫| ≤ ‖R 0‖ * ε :=
    (abs_real_inner_le_norm _ _).trans (mul_le_mul_of_nonneg_left hrem (norm_nonneg _))
  have h4 : ‖A δ‖ - ε ≤ ‖A δ + ρ‖ := by
    have : ‖A δ‖ ≤ ‖A δ + ρ‖ + ‖ρ‖ := by
      calc ‖A δ‖ = ‖(A δ + ρ) - ρ‖ := by rw [add_sub_cancel_right]
        _ ≤ ‖A δ + ρ‖ + ‖ρ‖ := norm_sub_le _ _
    linarith
  have h5 : (‖A δ‖ - ε) ^ 2 ≤ ‖A δ + ρ‖ ^ 2 := pow_le_pow_left₀ (by linarith) h4 2
  have h6 := (abs_le.mp h3).1
  unfold dchi2
  rw [h1, h2]
  nlinarith

/-- **Información perfilada** a partir de la columna `w` de `(ZᵀZ)⁻¹` (`ZᵀZ w = e_j`): si
`w_j > 0`, entonces `(1/w_j) · u_j² ≤ ‖Z u‖²` para todo `u`. -/
theorem info_of_inverse {k : ℕ} (Z : EuclideanSpace ℝ (Fin k) →L[ℝ] W) (j : Fin k)
    (w : EuclideanSpace ℝ (Fin k)) (hw : ∀ u, inner ℝ (Z w) (Z u) = u j) (hpos : 0 < w j) :
    ∀ u : EuclideanSpace ℝ (Fin k), (1 / w j) * (u j) ^ 2 ≤ ‖Z u‖ ^ 2 := by
  have hgeo := Identifiability.vif_geometric_of_inverse Z j w hw hpos le_rfl
  intro u
  by_cases h0 : u j = 0
  · rw [h0]; simp
  · set v := (u j)⁻¹ • u with hv
    have hvj : v j = 1 := by simp [hv, h0]
    have hZ : Z u = u j • Z v := by
      rw [hv, map_smul, smul_smul, mul_inv_cancel₀ h0, one_smul]
    have h1 := hgeo v hvj
    rw [hZ, norm_smul, mul_pow, Real.norm_eq_abs, sq_abs]
    nlinarith [sq_nonneg (u j)]

/-- **Información perfilada con la matriz calculada** (`inv(J.T @ J)[j, j]`): si `MᵀM` es
invertible y `((MᵀM)⁻¹)_{jj} > 0`, entonces `I_j · u_j² ≤ ‖M u‖²` con
`I_j = 1 / ((MᵀM)⁻¹)_{jj}`. -/
theorem info_of_matrix {m k : ℕ} (M : Matrix (Fin m) (Fin k) ℝ) (hG : IsUnit (Mᵀ * M).det)
    (j : Fin k) (hpos : 0 < (Mᵀ * M)⁻¹ j j) :
    ∀ u : EuclideanSpace ℝ (Fin k),
      (1 / (Mᵀ * M)⁻¹ j j) * (u j) ^ 2 ≤ ‖SpectralConditioning.matCLM M u‖ ^ 2 := by
  obtain ⟨hw, hwj⟩ := SpectralConditioning.vif_matrix_inverse M hG j
  have := info_of_inverse (SpectralConditioning.matCLM M) j _ hw (by rw [hwj]; exact hpos)
  rwa [hwj] at this

/-- Semiancho del intervalo de confianza garantizado: `t* = (ε + √(c + 2‖r₀‖ε)) / √I`. -/
noncomputable def tstar (I ε c r0 : ℝ) : ℝ := (ε + Real.sqrt (c + 2 * r0 * ε)) / Real.sqrt I

/-- **El perfil supera el umbral.** Si `θ̂` es estacionario, el resto no lineal es `≤ ε` en `δ`
y la información perfilada de la coordenada `φ` es `I > 0`, entonces `|φ δ| ≥ t*` implica
`Δχ²(δ) ≥ c`. -/
theorem dchi2_ge_of_coord (R : V → W) (A : V →L[ℝ] W) (φ : V → ℝ) {ε c I : ℝ}
    (hc : 0 ≤ c) (hε0 : 0 ≤ ε) (hI : 0 < I)
    (hinfo : ∀ δ, I * (φ δ) ^ 2 ≤ ‖A δ‖ ^ 2) (δ : V)
    (hstat : ⟪R 0, A δ⟫ = 0) (hrem : ‖R δ - R 0 - A δ‖ ≤ ε)
    (ht : tstar I ε c ‖R 0‖ ≤ |φ δ|) : c ≤ dchi2 R δ := by
  set s := Real.sqrt (c + 2 * ‖R 0‖ * ε) with hs
  have harg : 0 ≤ c + 2 * ‖R 0‖ * ε := by positivity
  have hs2 : s ^ 2 = c + 2 * ‖R 0‖ * ε := Real.sq_sqrt harg
  have hs0 : 0 ≤ s := Real.sqrt_nonneg _
  have hsI : 0 < Real.sqrt I := Real.sqrt_pos.2 hI
  -- √I · |φ δ| ≤ ‖A δ‖
  have hA : Real.sqrt I * |φ δ| ≤ ‖A δ‖ := by
    have h1 : (Real.sqrt I * |φ δ|) ^ 2 ≤ ‖A δ‖ ^ 2 := by
      rw [mul_pow, Real.sq_sqrt hI.le, sq_abs]; exact hinfo δ
    exact (abs_le_of_sq_le_sq' h1 (norm_nonneg _)).2
  -- ε + s ≤ √I · |φ δ|
  have hts : ε + s ≤ Real.sqrt I * |φ δ| := by
    have := mul_le_mul_of_nonneg_left ht hsI.le
    unfold tstar at this
    rwa [mul_div_cancel₀ _ hsI.ne'] at this
  have hAε : ε ≤ ‖A δ‖ := by linarith
  have hlow := dchi2_lower R A δ hstat hrem hAε
  have hsq : s ^ 2 ≤ (‖A δ‖ - ε) ^ 2 := pow_le_pow_left₀ hs0 (by linarith) 2
  linarith

/-- **Región de confianza acotada.** Con las hipótesis de `dchi2_ge_of_coord` en todo el conjunto
admisible `F`, todo `δ ∈ F` con `Δχ²(δ) < c` cumple `|φ δ| < t*`. -/
theorem confidence_coord_lt (R : V → W) (A : V →L[ℝ] W) (φ : V → ℝ) (F : Set V)
    {ε c I : ℝ} (hc : 0 ≤ c) (hε0 : 0 ≤ ε) (hI : 0 < I)
    (hinfo : ∀ δ, I * (φ δ) ^ 2 ≤ ‖A δ‖ ^ 2) (hstat : ∀ δ, ⟪R 0, A δ⟫ = 0)
    (hrem : ∀ δ ∈ F, ‖R δ - R 0 - A δ‖ ≤ ε) :
    ∀ δ ∈ F, dchi2 R δ < c → |φ δ| < tstar I ε c ‖R 0‖ := by
  intro δ hδ hlt
  by_contra h
  push_neg at h
  exact absurd (dchi2_ge_of_coord R A φ hc hε0 hI hinfo δ (hstat δ) (hrem δ hδ) h) (not_le.2 hlt)

/-- **Identificabilidad práctica** de la coordenada `φ` dentro de los límites `[−d₋, d₊]`
(distancias de `θ̂_j` a los límites): existen `0 < t₋ < d₋` y `0 < t₊ < d₊` tales que todo `δ`
admisible con `φ δ ≤ −t₋` o `φ δ ≥ t₊` tiene `Δχ²(δ) ≥ c`; es decir, el perfil de `θ_j` supera
el umbral `c` a ambos lados antes de llegar a los límites, y el intervalo de confianza
`{t : perfil(t) < c}` está contenido en `(−t₋, t₊)`. -/
def PracticallyIdentifiable (R : V → W) (φ : V → ℝ) (F : Set V) (c dlo dhi : ℝ) : Prop :=
  ∃ tlo thi : ℝ, 0 < tlo ∧ tlo < dlo ∧ 0 < thi ∧ thi < dhi ∧
    ∀ δ ∈ F, (φ δ ≤ -tlo ∨ thi ≤ φ δ) → c ≤ dchi2 R δ

/-- **Teorema principal.** Si `θ̂` es estacionario, el resto no lineal es `≤ ε` en el conjunto
admisible, la información perfilada es `I > 0` y `t* < d₋`, `t* < d₊`, entonces `θ_j` es
prácticamente identificable dentro de los límites (con `c > 0`). -/
theorem practically_identifiable (R : V → W) (A : V →L[ℝ] W) (φ : V → ℝ) (F : Set V)
    {ε c I dlo dhi : ℝ} (hc : 0 < c) (hε0 : 0 ≤ ε) (hI : 0 < I)
    (hinfo : ∀ δ, I * (φ δ) ^ 2 ≤ ‖A δ‖ ^ 2) (hstat : ∀ δ, ⟪R 0, A δ⟫ = 0)
    (hrem : ∀ δ ∈ F, ‖R δ - R 0 - A δ‖ ≤ ε)
    (hlo : tstar I ε c ‖R 0‖ < dlo) (hhi : tstar I ε c ‖R 0‖ < dhi) :
    PracticallyIdentifiable R φ F c dlo dhi := by
  have hpos : 0 < tstar I ε c ‖R 0‖ := by
    unfold tstar
    have : 0 < Real.sqrt (c + 2 * ‖R 0‖ * ε) := Real.sqrt_pos.2 (by positivity)
    exact div_pos (by linarith) (Real.sqrt_pos.2 hI)
  refine ⟨_, _, hpos, hlo, hpos, hhi, fun δ hδ hside => ?_⟩
  apply dchi2_ge_of_coord R A φ hc.le hε0 hI hinfo δ (hstat δ) (hrem δ hδ)
  rcases hside with h | h
  · rw [abs_of_neg (by linarith)]; linarith
  · rw [abs_of_pos (by linarith)]; exact h

/-- **Caso lineal: semiancho de Wald.** Con `ε = 0` e `I = 1/w` (`w = ((AᵀA)⁻¹)_{jj} > 0`),
`t* = √(c · w)`, el semiancho del intervalo lineal calculado numéricamente. -/
theorem tstar_linear {c w r0 : ℝ} (hc : 0 ≤ c) (hw : 0 < w) :
    tstar (1 / w) 0 c r0 = Real.sqrt (c * w) := by
  unfold tstar
  rw [mul_zero, add_zero, zero_add, Real.sqrt_div' _ hw.le, Real.sqrt_one, div_div_eq_mul_div,
    div_one, Real.sqrt_mul hc]

/-- **Identificabilidad local (estructural) del problema reducido.** Si `‖A δ‖ ≥ σ‖δ‖`
(`A` inyectiva, `σ` = menor valor singular) y el resto es `≤ M‖δ‖²` en la bola de radio `r`,
dos parámetros distintos en la bola `‖δ‖ < σ/M` producen salidas distintas. -/
theorem local_injective (G : V → W) (A : V →L[ℝ] W) {σ M r : ℝ}
    (hA : ∀ δ, σ * ‖δ‖ ≤ ‖A δ‖) (hrem : ∀ δ, ‖δ‖ ≤ r → ‖G δ - G 0 - A δ‖ ≤ M * ‖δ‖ ^ 2)
    (δ : V) (hδ : δ ≠ 0) (hr : ‖δ‖ ≤ r) (hsm : M * ‖δ‖ < σ) : G δ ≠ G 0 := by
  intro hG
  have h1 := hrem δ hr
  rw [hG, sub_self, zero_sub, norm_neg] at h1
  have hn : 0 < ‖δ‖ := norm_pos_iff.2 hδ
  have h2 := hA δ
  nlinarith

/-! ## Mínimo numérico: gradiente residual `γ`

El optimizador termina con una tolerancia y, a veces, en un límite del dominio, así que la
estacionariedad exacta `⟪R 0, A δ⟫ = 0` sólo se cumple aproximadamente. Se sustituye por
`|⟪R 0, A δ⟫| ≤ γ ‖A δ‖`, que vale con `γ = ‖P r₀‖` (proyección ortogonal de `r₀` sobre la
imagen de `A`, calculable como `‖A (AᵀA)⁻¹ Aᵀ r₀‖`). Con `γ = 0` se recuperan los resultados
anteriores. -/

/-- **Cota inferior de Δχ² con gradiente residual.**
`Δχ²(δ) ≥ (‖A δ‖ − ε)² − 2γ‖A δ‖ − 2‖R 0‖ε` (si `ε ≤ ‖A δ‖`). -/
theorem dchi2_lower_grad (R : V → W) (A : V →L[ℝ] W) {ε γ : ℝ} (δ : V)
    (hstat : |⟪R 0, A δ⟫| ≤ γ * ‖A δ‖) (hrem : ‖R δ - R 0 - A δ‖ ≤ ε) (hε : ε ≤ ‖A δ‖) :
    (‖A δ‖ - ε) ^ 2 - 2 * γ * ‖A δ‖ - 2 * ‖R 0‖ * ε ≤ dchi2 R δ := by
  set ρ := R δ - R 0 - A δ with hρ
  have hR : R δ = R 0 + (A δ + ρ) := by rw [hρ]; abel
  have h1 : ‖R δ‖ ^ 2 = ‖R 0‖ ^ 2 + 2 * ⟪R 0, A δ + ρ⟫ + ‖A δ + ρ‖ ^ 2 := by
    rw [hR, norm_add_sq_real]
  have h2 : ⟪R 0, A δ + ρ⟫ = ⟪R 0, A δ⟫ + ⟪R 0, ρ⟫ := inner_add_right _ _ _
  have h3 : |⟪R 0, ρ⟫| ≤ ‖R 0‖ * ε :=
    (abs_real_inner_le_norm _ _).trans (mul_le_mul_of_nonneg_left hrem (norm_nonneg _))
  have h4 : ‖A δ‖ - ε ≤ ‖A δ + ρ‖ := by
    have : ‖A δ‖ ≤ ‖A δ + ρ‖ + ‖ρ‖ := by
      calc ‖A δ‖ = ‖(A δ + ρ) - ρ‖ := by rw [add_sub_cancel_right]
        _ ≤ ‖A δ + ρ‖ + ‖ρ‖ := norm_sub_le _ _
    linarith
  have h5 : (‖A δ‖ - ε) ^ 2 ≤ ‖A δ + ρ‖ ^ 2 := pow_le_pow_left₀ (by linarith) h4 2
  have h6 := (abs_le.mp h3).1
  have h7 := (abs_le.mp hstat).1
  unfold dchi2
  rw [h1, h2]
  nlinarith

/-- Semiancho garantizado con gradiente residual:
`t* = (ε + γ + √(γ² + c + 2‖r₀‖ε + 2γε)) / √I`. -/
noncomputable def tstarGrad (I ε γ c r0 : ℝ) : ℝ :=
  (ε + γ + Real.sqrt (γ ^ 2 + c + 2 * r0 * ε + 2 * γ * ε)) / Real.sqrt I

/-- Con `γ = 0`, `tstarGrad` coincide con `tstar`. -/
theorem tstarGrad_zero (I ε c r0 : ℝ) : tstarGrad I ε 0 c r0 = tstar I ε c r0 := by
  unfold tstarGrad tstar; ring_nf

/-- **El perfil supera el umbral (mínimo numérico).** -/
theorem dchi2_ge_of_coord_grad (R : V → W) (A : V →L[ℝ] W) (φ : V → ℝ) {ε γ c I : ℝ}
    (hc : 0 ≤ c) (hε0 : 0 ≤ ε) (hγ0 : 0 ≤ γ) (hI : 0 < I)
    (hinfo : ∀ δ, I * (φ δ) ^ 2 ≤ ‖A δ‖ ^ 2) (δ : V)
    (hstat : |⟪R 0, A δ⟫| ≤ γ * ‖A δ‖) (hrem : ‖R δ - R 0 - A δ‖ ≤ ε)
    (ht : tstarGrad I ε γ c ‖R 0‖ ≤ |φ δ|) : c ≤ dchi2 R δ := by
  set K := γ ^ 2 + c + 2 * ‖R 0‖ * ε + 2 * γ * ε with hK
  set s := Real.sqrt K with hs
  have hK0 : 0 ≤ K := by positivity
  have hs2 : s ^ 2 = K := Real.sq_sqrt hK0
  have hs0 : 0 ≤ s := Real.sqrt_nonneg _
  have hsI : 0 < Real.sqrt I := Real.sqrt_pos.2 hI
  have hA : Real.sqrt I * |φ δ| ≤ ‖A δ‖ := by
    have h1 : (Real.sqrt I * |φ δ|) ^ 2 ≤ ‖A δ‖ ^ 2 := by
      rw [mul_pow, Real.sq_sqrt hI.le, sq_abs]; exact hinfo δ
    exact (abs_le_of_sq_le_sq' h1 (norm_nonneg _)).2
  have hts : ε + γ + s ≤ Real.sqrt I * |φ δ| := by
    have := mul_le_mul_of_nonneg_left ht hsI.le
    unfold tstarGrad at this
    rwa [mul_div_cancel₀ _ hsI.ne'] at this
  set x := ‖A δ‖ - ε with hx
  have hxγ : γ + s ≤ x := by linarith
  have hlow := dchi2_lower_grad R A δ hstat hrem (by linarith)
  have hsq : s ^ 2 ≤ (x - γ) ^ 2 := pow_le_pow_left₀ hs0 (by linarith) 2
  have hAx : ‖A δ‖ = x + ε := by rw [hx]; ring
  rw [hAx] at hlow
  nlinarith

/-- **Teorema principal con mínimo numérico.** Igual que `practically_identifiable`, con la
estacionariedad aproximada `|⟪R 0, A δ⟫| ≤ γ‖A δ‖` y `tstarGrad` en lugar de `tstar`. -/
theorem practically_identifiable_grad (R : V → W) (A : V →L[ℝ] W) (φ : V → ℝ) (F : Set V)
    {ε γ c I dlo dhi : ℝ} (hc : 0 < c) (hε0 : 0 ≤ ε) (hγ0 : 0 ≤ γ) (hI : 0 < I)
    (hinfo : ∀ δ, I * (φ δ) ^ 2 ≤ ‖A δ‖ ^ 2)
    (hstat : ∀ δ, |⟪R 0, A δ⟫| ≤ γ * ‖A δ‖)
    (hrem : ∀ δ ∈ F, ‖R δ - R 0 - A δ‖ ≤ ε)
    (hlo : tstarGrad I ε γ c ‖R 0‖ < dlo) (hhi : tstarGrad I ε γ c ‖R 0‖ < dhi) :
    PracticallyIdentifiable R φ F c dlo dhi := by
  have hpos : 0 < tstarGrad I ε γ c ‖R 0‖ := by
    unfold tstarGrad
    have : 0 < Real.sqrt (γ ^ 2 + c + 2 * ‖R 0‖ * ε + 2 * γ * ε) :=
      Real.sqrt_pos.2 (by positivity)
    exact div_pos (by linarith) (Real.sqrt_pos.2 hI)
  refine ⟨_, _, hpos, hlo, hpos, hhi, fun δ hδ hside => ?_⟩
  apply dchi2_ge_of_coord_grad R A φ hc.le hε0 hγ0 hI hinfo δ (hstat δ) (hrem δ hδ)
  rcases hside with h | h
  · rw [abs_of_neg (by linarith)]; linarith
  · rw [abs_of_pos (by linarith)]; exact h

/-- **`γ` mediante la proyección.** Si `p` es la proyección de `R 0` sobre la imagen de `A`
(es decir, `R 0 − p` es ortogonal a la imagen) y `‖p‖ ≤ γ`, entonces
`|⟪R 0, A δ⟫| ≤ γ‖A δ‖` para todo `δ`. -/
theorem stat_of_projection (A : V →L[ℝ] W) (r0 p : W) {γ : ℝ}
    (horth : ∀ δ, ⟪r0 - p, A δ⟫ = 0) (hp : ‖p‖ ≤ γ) :
    ∀ δ, |⟪r0, A δ⟫| ≤ γ * ‖A δ‖ := by
  intro δ
  have : ⟪r0, A δ⟫ = ⟪p, A δ⟫ := by
    have h := horth δ
    rw [inner_sub_left] at h; linarith
  rw [this]
  exact (abs_real_inner_le_norm _ _).trans (mul_le_mul_of_nonneg_right hp (norm_nonneg _))

end ProfileIdentifiability

#print axioms ProfileIdentifiability.practically_identifiable_grad
#print axioms ProfileIdentifiability.stat_of_projection
#print axioms ProfileIdentifiability.tstarGrad_zero
#print axioms ProfileIdentifiability.dchi2_lower
#print axioms ProfileIdentifiability.info_of_matrix
#print axioms ProfileIdentifiability.practically_identifiable
#print axioms ProfileIdentifiability.tstar_linear
#print axioms ProfileIdentifiability.local_injective
