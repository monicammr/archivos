import IdentifiabilityConditioning
import Mathlib.Analysis.InnerProductSpace.Spectrum
import Mathlib.Analysis.InnerProductSpace.Adjoint
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse

/-!
# κ y VIF tal como se calculan numéricamente (teorema espectral y matriz inversa)

`IdentifiabilityConditioning` formula κ y VIF mediante desigualdades
(`σmin ‖u‖ ≤ ‖Z u‖ ≤ σmax ‖u‖`, `⟨Z w, Z u⟩ = u_j`). Aquí se demuestra que esas hipótesis las
cumplen exactamente las cantidades que calcula el código (numpy):

* **κ.** Sea `G = Zᵀ Z` (la matriz de Gram, `gram Z`), simétrica. Por el teorema espectral
  (`LinearMap.IsSymmetric.eigenvectorBasis`) tiene autovalores `λ₁ ≥ … ≥ λ_k ≥ 0`:
  - `sq_norm_apply_eq_sum`: `‖Z u‖² = ∑ λ_i c_i²` (coordenadas en la base de autovectores);
  - `opNorm_eq_sqrt_lamMax`: `‖Z‖ = √λ_max = σ_max`;
  - `sqrt_lamMin_mul_le` y `le_sqrt_lamMin`: `√λ_min` es la **mejor** constante `σmin`;
  - `ls_kappa_stability_spectral`: con `κ = √(λ_max/λ_min) = σ_max/σ_min` (= `numpy.linalg.cond`
    de `Z`, pues los valores singulares de `Z` son `√λ_i`) se obtiene `‖v − v'‖ ≤ κ ‖y − y'‖`.
  - `gram_toEuclideanLin`: para `Z` dada por una matriz `M`, `gram Z` es la matriz `Mᵀ M`.
* **VIF.** Para `Z` dada por la matriz `M` con `Mᵀ M` invertible, `w = (MᵀM)⁻¹ e_j` cumple
  `⟨Z w, Z u⟩ = u_j` y `w_j = ((MᵀM)⁻¹)_{jj}` (`vif_matrix_inverse`); por tanto
  `ls_vif_matrix_stability`: si `((MᵀM)⁻¹)_{jj} ≤ V` entonces `|v_j − v'_j| ≤ √V ‖y − y'‖`.
-/

open scoped RealInnerProductSpace
open Identifiability Matrix

namespace SpectralConditioning

variable {k m : ℕ}

/-- Operador de Gram `G = Z† Z` (en coordenadas, `Zᵀ Z`). -/
noncomputable def gram (Z : EuclideanSpace ℝ (Fin k) →L[ℝ] EuclideanSpace ℝ (Fin m)) :
    EuclideanSpace ℝ (Fin k) →ₗ[ℝ] EuclideanSpace ℝ (Fin k) :=
  ((ContinuousLinearMap.adjoint Z).comp Z : EuclideanSpace ℝ (Fin k) →L[ℝ] _)

lemma inner_gram (Z : EuclideanSpace ℝ (Fin k) →L[ℝ] EuclideanSpace ℝ (Fin m))
    (u v : EuclideanSpace ℝ (Fin k)) : inner ℝ (gram Z u) v = inner ℝ (Z u) (Z v) := by
  simp only [gram, ContinuousLinearMap.coe_coe, ContinuousLinearMap.comp_apply,
    ContinuousLinearMap.adjoint_inner_left]

lemma gram_isSymmetric (Z : EuclideanSpace ℝ (Fin k) →L[ℝ] EuclideanSpace ℝ (Fin m)) :
    (gram Z).IsSymmetric := by
  intro u v
  rw [inner_gram, real_inner_comm (gram Z v) u, inner_gram]
  exact real_inner_comm _ _

lemma finrank_eq : Module.finrank ℝ (EuclideanSpace ℝ (Fin k)) = k := finrank_euclideanSpace_fin

/-- Autovalores de `ZᵀZ`, en orden decreciente. -/
noncomputable def lam (Z : EuclideanSpace ℝ (Fin k) →L[ℝ] EuclideanSpace ℝ (Fin m)) :
    Fin k → ℝ :=
  (gram_isSymmetric Z).eigenvalues finrank_eq

/-- Base ortonormal de autovectores de `ZᵀZ` (vectores singulares derechos de `Z`). -/
noncomputable def evec (Z : EuclideanSpace ℝ (Fin k) →L[ℝ] EuclideanSpace ℝ (Fin m)) :
    OrthonormalBasis (Fin k) ℝ (EuclideanSpace ℝ (Fin k)) :=
  (gram_isSymmetric Z).eigenvectorBasis finrank_eq

lemma lam_antitone (Z : EuclideanSpace ℝ (Fin k) →L[ℝ] EuclideanSpace ℝ (Fin m)) :
    Antitone (lam Z) :=
  (gram_isSymmetric Z).eigenvalues_antitone finrank_eq

lemma gram_evec (Z : EuclideanSpace ℝ (Fin k) →L[ℝ] EuclideanSpace ℝ (Fin m)) (i : Fin k) :
    gram Z (evec Z i) = lam Z i • evec Z i := by
  have := (gram_isSymmetric Z).apply_eigenvectorBasis finrank_eq i
  simp only [RCLike.ofReal_real_eq_id, id_eq] at this
  exact this

/-- `‖Z vᵢ‖² = λᵢ`: los autovalores son los cuadrados de los valores singulares. -/
lemma sq_norm_apply_evec (Z : EuclideanSpace ℝ (Fin k) →L[ℝ] EuclideanSpace ℝ (Fin m))
    (i : Fin k) : ‖Z (evec Z i)‖ ^ 2 = lam Z i := by
  rw [← real_inner_self_eq_norm_sq, ← inner_gram, gram_evec, real_inner_smul_left,
    real_inner_self_eq_norm_sq, (evec Z).orthonormal.1 i, one_pow, mul_one]

lemma lam_nonneg (Z : EuclideanSpace ℝ (Fin k) →L[ℝ] EuclideanSpace ℝ (Fin m)) (i : Fin k) :
    0 ≤ lam Z i := by
  rw [← sq_norm_apply_evec]; positivity

/-- **Teorema espectral aplicado a `Z`:** `‖Z u‖² = ∑ᵢ λᵢ cᵢ²` y `‖u‖² = ∑ᵢ cᵢ²`, con `c` las
coordenadas de `u` en la base de autovectores. -/
theorem sq_norm_apply_eq_sum (Z : EuclideanSpace ℝ (Fin k) →L[ℝ] EuclideanSpace ℝ (Fin m))
    (u : EuclideanSpace ℝ (Fin k)) :
    ‖Z u‖ ^ 2 = ∑ i, lam Z i * ((evec Z).repr u i) ^ 2 := by
  have hrep : ∀ i, (evec Z).repr (gram Z u) i = lam Z i * (evec Z).repr u i := by
    intro i
    have := (gram_isSymmetric Z).eigenvectorBasis_apply_self_apply finrank_eq u i
    simpa [lam, evec] using this
  rw [← real_inner_self_eq_norm_sq, ← inner_gram, ← (evec Z).repr.inner_map_map,
    PiLp.inner_apply]
  apply Finset.sum_congr rfl
  intro i _
  rw [hrep, real_inner_eq_re_inner, RCLike.re_to_real]
  simp only [inner, RCLike.conj_to_real]
  ring

theorem sq_norm_eq_sum (Z : EuclideanSpace ℝ (Fin k) →L[ℝ] EuclideanSpace ℝ (Fin m))
    (u : EuclideanSpace ℝ (Fin k)) :
    ‖u‖ ^ 2 = ∑ i, ((evec Z).repr u i) ^ 2 := by
  rw [← (evec Z).repr.norm_map u, EuclideanSpace.norm_sq_eq]
  simp [Real.norm_eq_abs, sq_abs]

/-- Si todos los autovalores están en `[lo, hi]`, entonces `lo ‖u‖² ≤ ‖Z u‖² ≤ hi ‖u‖²`. -/
theorem sq_norm_bounds (Z : EuclideanSpace ℝ (Fin k) →L[ℝ] EuclideanSpace ℝ (Fin m))
    {lo hi : ℝ} (hlo : ∀ i, lo ≤ lam Z i) (hhi : ∀ i, lam Z i ≤ hi)
    (u : EuclideanSpace ℝ (Fin k)) :
    lo * ‖u‖ ^ 2 ≤ ‖Z u‖ ^ 2 ∧ ‖Z u‖ ^ 2 ≤ hi * ‖u‖ ^ 2 := by
  rw [sq_norm_apply_eq_sum, sq_norm_eq_sum Z u, Finset.mul_sum, Finset.mul_sum]
  exact ⟨Finset.sum_le_sum fun i _ => mul_le_mul_of_nonneg_right (hlo i) (sq_nonneg _),
    Finset.sum_le_sum fun i _ => mul_le_mul_of_nonneg_right (hhi i) (sq_nonneg _)⟩

section Extremes

variable (hk : 0 < k)
include hk

/-- Índice del mayor autovalor (los autovalores están ordenados de forma decreciente). -/
def iMax : Fin k := ⟨0, hk⟩
/-- Índice del menor autovalor. -/
def iMin : Fin k := ⟨k - 1, by omega⟩

lemma lam_le_max (Z : EuclideanSpace ℝ (Fin k) →L[ℝ] EuclideanSpace ℝ (Fin m)) (i : Fin k) :
    lam Z i ≤ lam Z (iMax hk) :=
  lam_antitone Z (Fin.mk_le_mk.2 (Nat.zero_le _) |>.trans (le_refl i))

lemma min_le_lam (Z : EuclideanSpace ℝ (Fin k) →L[ℝ] EuclideanSpace ℝ (Fin m)) (i : Fin k) :
    lam Z (iMin hk) ≤ lam Z i :=
  lam_antitone Z (show i ≤ iMin hk from Fin.mk_le_mk.2 (by have := i.2; simp; omega))

/-- `√λ_min ‖u‖ ≤ ‖Z u‖ ≤ √λ_max ‖u‖`. -/
theorem norm_bounds (Z : EuclideanSpace ℝ (Fin k) →L[ℝ] EuclideanSpace ℝ (Fin m))
    (u : EuclideanSpace ℝ (Fin k)) :
    Real.sqrt (lam Z (iMin hk)) * ‖u‖ ≤ ‖Z u‖ ∧ ‖Z u‖ ≤ Real.sqrt (lam Z (iMax hk)) * ‖u‖ := by
  obtain ⟨h1, h2⟩ := sq_norm_bounds Z (min_le_lam hk Z) (lam_le_max hk Z) u
  have hmin := lam_nonneg Z (iMin hk)
  have hmax := lam_nonneg Z (iMax hk)
  constructor
  · apply (pow_le_pow_iff_left₀ (by positivity) (norm_nonneg _) two_ne_zero).1
    rw [mul_pow, Real.sq_sqrt hmin]; exact h1
  · apply (pow_le_pow_iff_left₀ (norm_nonneg _) (by positivity) two_ne_zero).1
    rw [mul_pow, Real.sq_sqrt hmax]; exact h2

/-- **σ_max = √λ_max = ‖Z‖** (norma de operador). -/
theorem opNorm_eq_sqrt_lamMax (Z : EuclideanSpace ℝ (Fin k) →L[ℝ] EuclideanSpace ℝ (Fin m)) :
    ‖Z‖ = Real.sqrt (lam Z (iMax hk)) := by
  apply le_antisymm
  · exact ContinuousLinearMap.opNorm_le_bound _ (Real.sqrt_nonneg _)
      fun u => (norm_bounds hk Z u).2
  · have h := Z.le_opNorm (evec Z (iMax hk))
    rw [(evec Z).orthonormal.1, mul_one] at h
    have he : Real.sqrt (lam Z (iMax hk)) = ‖Z (evec Z (iMax hk))‖ := by
      rw [← sq_norm_apply_evec, Real.sqrt_sq (norm_nonneg _)]
    rw [he]; exact h

/-- `√λ_min` es una cota inferior válida: `√λ_min ‖u‖ ≤ ‖Z u‖`. -/
theorem sqrt_lamMin_mul_le (Z : EuclideanSpace ℝ (Fin k) →L[ℝ] EuclideanSpace ℝ (Fin m))
    (u : EuclideanSpace ℝ (Fin k)) : Real.sqrt (lam Z (iMin hk)) * ‖u‖ ≤ ‖Z u‖ :=
  (norm_bounds hk Z u).1

/-- … y es la **mejor** posible: toda `σ` con `σ ‖u‖ ≤ ‖Z u‖` cumple `σ ≤ √λ_min = σ_min`. -/
theorem le_sqrt_lamMin (Z : EuclideanSpace ℝ (Fin k) →L[ℝ] EuclideanSpace ℝ (Fin m)) {σ : ℝ}
    (hσ : ∀ u, σ * ‖u‖ ≤ ‖Z u‖) : σ ≤ Real.sqrt (lam Z (iMin hk)) := by
  have h := hσ (evec Z (iMin hk))
  rw [(evec Z).orthonormal.1, mul_one] at h
  rwa [← sq_norm_apply_evec, Real.sqrt_sq (norm_nonneg _)]

/-- **κ espectral ⇒ estimación estable.** Con columnas L2-normalizadas y `λ_min > 0`, dos
ajustes por mínimos cuadrados cumplen `‖v − v'‖ ≤ √(λ_max/λ_min) ‖y − y'‖`, donde
`√(λ_max/λ_min) = σ_max/σ_min` es el número de condición que calcula `numpy.linalg.cond(Z)`. -/
theorem ls_kappa_stability_spectral
    (Z : EuclideanSpace ℝ (Fin k) →L[ℝ] EuclideanSpace ℝ (Fin m))
    (hunit : ∀ j, ‖Z (EuclideanSpace.single j 1)‖ = 1)
    (hpos : 0 < lam Z (iMin hk))
    {y y' : EuclideanSpace ℝ (Fin m)} {v v' : EuclideanSpace ℝ (Fin k)}
    (hv : IsLSMin Z y v) (hv' : IsLSMin Z y' v') :
    ‖v - v'‖ ≤ Real.sqrt (lam Z (iMax hk) / lam Z (iMin hk)) * ‖y - y'‖ := by
  have hκ : Real.sqrt (lam Z (iMax hk))
      ≤ Real.sqrt (lam Z (iMax hk) / lam Z (iMin hk)) * Real.sqrt (lam Z (iMin hk)) := by
    rw [← Real.sqrt_mul (div_nonneg (lam_nonneg Z _) hpos.le), div_mul_cancel₀ _ hpos.ne']
  exact ls_kappa_stability Z hunit (iMax hk) (Real.sqrt_pos.2 hpos)
    (fun u => (norm_bounds hk Z u).1) (fun u => (norm_bounds hk Z u).2) hκ hv hv'

end Extremes

/-! ## Conexión con matrices -/

/-- Aplicación lineal continua asociada a una matriz `M` (la matriz de sensibilidad escalada). -/
noncomputable def matCLM (M : Matrix (Fin m) (Fin k) ℝ) :
    EuclideanSpace ℝ (Fin k) →L[ℝ] EuclideanSpace ℝ (Fin m) :=
  LinearMap.toContinuousLinearMap (Matrix.toEuclideanLin M)

lemma matCLM_apply (M : Matrix (Fin m) (Fin k) ℝ) (u : EuclideanSpace ℝ (Fin k)) :
    matCLM M u = WithLp.toLp 2 (M *ᵥ WithLp.ofLp u) := rfl

lemma inner_matCLM (M : Matrix (Fin m) (Fin k) ℝ) (u v : EuclideanSpace ℝ (Fin k)) :
    inner ℝ (matCLM M u) (matCLM M v)
      = WithLp.ofLp u ⬝ᵥ ((Mᵀ * M) *ᵥ WithLp.ofLp v) := by
  rw [matCLM_apply, matCLM_apply, EuclideanSpace.inner_toLp_toLp, star_trivial]
  symm
  rw [← Matrix.mulVec_mulVec, Matrix.dotProduct_mulVec, Matrix.vecMul_transpose,
    dotProduct_comm]

/-- `gram (matCLM M)` es la matriz `Mᵀ M` (lo que calcula `Z.T @ Z`). -/
theorem gram_toEuclideanLin (M : Matrix (Fin m) (Fin k) ℝ) (u : EuclideanSpace ℝ (Fin k)) :
    gram (matCLM M) u = WithLp.toLp 2 ((Mᵀ * M) *ᵥ WithLp.ofLp u) := by
  apply ext_inner_right ℝ
  intro v
  rw [inner_gram, real_inner_comm (matCLM M v) (matCLM M u), inner_matCLM,
    EuclideanSpace.inner_eq_star_dotProduct, star_trivial, WithLp.ofLp_toLp]

/-- **VIF mediante la matriz inversa.** Si `MᵀM` es invertible y `w = (MᵀM)⁻¹ e_j`, entonces
`⟨Z w, Z u⟩ = u_j` para todo `u` (hipótesis de `vif_geometric_of_inverse`) y
`w_j = ((MᵀM)⁻¹)_{jj}`. -/
theorem vif_matrix_inverse (M : Matrix (Fin m) (Fin k) ℝ) (hG : IsUnit (Mᵀ * M).det)
    (j : Fin k) :
    (∀ u, inner ℝ (matCLM M (WithLp.toLp 2 ((Mᵀ * M)⁻¹ *ᵥ Pi.single j 1))) (matCLM M u)
      = u j) ∧
    (WithLp.toLp 2 ((Mᵀ * M)⁻¹ *ᵥ Pi.single j 1) : EuclideanSpace ℝ (Fin k)) j
      = (Mᵀ * M)⁻¹ j j := by
  constructor
  · intro u
    rw [real_inner_comm, inner_matCLM]
    simp only [WithLp.ofLp_toLp]
    rw [Matrix.mulVec_mulVec, Matrix.mul_nonsing_inv _ hG, Matrix.one_mulVec,
      dotProduct_single, mul_one]
    rfl
  · show ((Mᵀ * M)⁻¹ *ᵥ Pi.single j 1) j = (Mᵀ * M)⁻¹ j j
    simp [Matrix.mulVec, dotProduct_single]

/-- **VIF calculado con `inv(Z.T @ Z)` ⇒ estabilidad por parámetro.** Si
`((MᵀM)⁻¹)_{jj} ≤ V`, entonces `|v_j − v'_j| ≤ √V ‖y − y'‖`. -/
theorem ls_vif_matrix_stability (M : Matrix (Fin m) (Fin k) ℝ) (hG : IsUnit (Mᵀ * M).det)
    (j : Fin k) {Vb : ℝ} (hV : 0 < Vb) (hvif : (Mᵀ * M)⁻¹ j j ≤ Vb)
    {y y' : EuclideanSpace ℝ (Fin m)} {v v' : EuclideanSpace ℝ (Fin k)}
    (hv : IsLSMin (matCLM M) y v) (hv' : IsLSMin (matCLM M) y' v') :
    |v j - v' j| ≤ Real.sqrt Vb * ‖y - y'‖ := by
  obtain ⟨hw, hwj⟩ := vif_matrix_inverse M hG j
  exact ls_vif_inverse_stability (matCLM M) j _ hw hV (by rw [hwj]; exact hvif) hv hv'

end SpectralConditioning

#print axioms SpectralConditioning.ls_kappa_stability_spectral
#print axioms SpectralConditioning.opNorm_eq_sqrt_lamMax
#print axioms SpectralConditioning.ls_vif_matrix_stability
#print axioms SpectralConditioning.gram_toEuclideanLin
