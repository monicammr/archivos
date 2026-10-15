import FirstOrderErrorBound
import Mathlib.Analysis.Calculus.FDeriv.Basic
import Mathlib.Analysis.InnerProductSpace.PiL2

/-!
# Del Jacobiano a la trayectoria: cota de error al fijar parámetros

Sea `F : ℝᵖ → ℝᵐ` el mapa "parámetros ↦ trayectoria muestreada"
(las `m` coordenadas son los pares estado × instante de la malla temporal),
y supongamos que `F` es diferenciable en `θ₀` con derivada `L`
(`HasFDerivAt F L θ₀`). Su matriz es la de sensibilidad
`J i j = (L e_j)_i = ∂F_i/∂θ_j (θ₀)`.

El **modelo reducido** fija los parámetros descartados `Sᶜ` en su valor nominal:
para una perturbación `Δθ`, evalúa `F (θ₀ + Δθ_S)`.

Teorema principal (`trajectory_error_bound`): para todo `η > 0`, para toda
perturbación `Δθ` suficientemente pequeña,

  ‖F(θ₀+Δθ) − F(θ₀+Δθ_S)‖  ≤  √R(S) · ‖Δθ_{Sᶜ}‖ + η · ‖Δθ‖,

con `R(S) = ∑_{j∉S} (JᵀJ)_{jj}` y normas euclídeas. Es decir: el error de la
trayectoria **no lineal** es la cota de energía de primer orden más un término
`o(‖Δθ‖)`.

Hipótesis honesta: la diferenciabilidad de `θ ↦ F θ` se **supone**
(`HasFDerivAt`). Para una EDO `ẋ = f(x, θ)` con `f` de clase C¹ es el teorema
clásico de dependencia diferenciable respecto a parámetros, que (hasta donde
sabemos) aún no está en Mathlib; `sensitivity_jacobian.lean` también lo usa
como hipótesis (`hxθ`).
-/

open scoped BigOperators Topology
open Finset Filter Asymptotics FirstOrderErrorBound

namespace TrajectoryErrorBound

variable {m p : ℕ}

/-- Matriz de sensibilidad asociada a la derivada `L`: `J i j = (L e_j)_i`. -/
noncomputable def jacobianOf (L : EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin m)) :
    Fin m → Fin p → ℝ :=
  fun i j => L (EuclideanSpace.single j 1) i

/-- Perturbación del modelo reducido: conserva `Δθ_j` si `j ∈ S`, y pone `0`
    (parámetro fijado en su valor nominal) si `j ∉ S`. -/
def keepS (S : Finset (Fin p)) (Δθ : EuclideanSpace ℝ (Fin p)) : EuclideanSpace ℝ (Fin p) :=
  WithLp.toLp 2 (fun j => if j ∈ S then Δθ j else 0)

theorem keepS_apply (S : Finset (Fin p)) (Δθ : EuclideanSpace ℝ (Fin p)) (j : Fin p) :
    keepS S Δθ j = if j ∈ S then Δθ j else 0 := rfl

/-- `‖Δθ_S‖ ≤ ‖Δθ‖`. -/
theorem norm_keepS_le (S : Finset (Fin p)) (Δθ : EuclideanSpace ℝ (Fin p)) :
    ‖keepS S Δθ‖ ≤ ‖Δθ‖ := by
  rw [EuclideanSpace.norm_eq, EuclideanSpace.norm_eq]
  apply Real.sqrt_le_sqrt
  apply Finset.sum_le_sum
  intro j _
  rw [keepS_apply]
  split_ifs
  · exact le_rfl
  · simpa using sq_nonneg (Δθ j)

/-- Expansión de una aplicación lineal en la base canónica:
    `(L Δθ)_i = ∑_j J i j · Δθ_j`. -/
theorem clm_apply_eq_linResponse
    (L : EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin m))
    (Δθ : EuclideanSpace ℝ (Fin p)) (i : Fin m) :
    L Δθ i = linResponse (jacobianOf L) (fun j => Δθ j) i := by
  conv_lhs => rw [← (EuclideanSpace.basisFun (Fin p) ℝ).sum_repr Δθ]
  simp only [EuclideanSpace.basisFun_repr, EuclideanSpace.basisFun_apply, map_sum, map_smul]
  rw [show (∑ x, Δθ x • L (EuclideanSpace.single x 1)) i
        = ∑ x, (Δθ x • L (EuclideanSpace.single x 1)) i from Finset.sum_apply i _ _]
  simp only [linResponse, jacobianOf]
  apply Finset.sum_congr rfl
  intro j _
  rw [mul_comm]; rfl

/-- `(L Δθ_S)_i = ∑_{j∈S} J i j · Δθ_j`. -/
theorem clm_keepS_eq_reducedResponse
    (L : EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin m))
    (S : Finset (Fin p)) (Δθ : EuclideanSpace ℝ (Fin p)) (i : Fin m) :
    L (keepS S Δθ) i = reducedResponse (jacobianOf L) S (fun j => Δθ j) i := by
  rw [clm_apply_eq_linResponse]
  simp only [linResponse, reducedResponse, keepS_apply]
  simp [mul_ite, Finset.sum_ite_mem]

/-- Parte lineal del error: `‖L Δθ − L Δθ_S‖ ≤ √R(S) · ‖Δθ_{Sᶜ}‖`. -/
theorem linear_part_bound
    (L : EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin m))
    (S : Finset (Fin p)) (Δθ : EuclideanSpace ℝ (Fin p)) :
    ‖L Δθ - L (keepS S Δθ)‖
      ≤ Real.sqrt (removedColumnEnergy (jacobianOf L) S)
          * Real.sqrt (removedParamSq S (fun j => Δθ j)) := by
  have h := first_order_error_bound (jacobianOf L) S (fun j => Δθ j)
  have heq : ‖L Δθ - L (keepS S Δθ)‖
      = Real.sqrt (sqNorm (fun i => linResponse (jacobianOf L) (fun j => Δθ j) i
                    - reducedResponse (jacobianOf L) S (fun j => Δθ j) i)) := by
    rw [EuclideanSpace.norm_eq]
    congr 1
    apply Finset.sum_congr rfl
    intro i _
    rw [Real.norm_eq_abs, sq_abs, PiLp.sub_apply, clm_apply_eq_linResponse,
      clm_keepS_eq_reducedResponse]
  rw [heq]; exact h

/-- `‖Δθ_{Sᶜ}‖² ≤ ‖Δθ‖²` en forma de raíces. -/
theorem sqrt_removedParamSq_le (S : Finset (Fin p)) (Δθ : EuclideanSpace ℝ (Fin p)) :
    Real.sqrt (removedParamSq S (fun j => Δθ j)) ≤ ‖Δθ‖ := by
  rw [EuclideanSpace.norm_eq]
  apply Real.sqrt_le_sqrt
  calc removedParamSq S (fun j => Δθ j) ≤ sqNorm (fun j => Δθ j) := removedParamSq_le S _
    _ = ∑ j, ‖Δθ j‖ ^ 2 := by
        simp only [sqNorm, Real.norm_eq_abs, sq_abs]

/-- El resto no lineal `F(θ₀+Δθ) − F(θ₀+Δθ_S) − L(Δθ − Δθ_S)` es `o(‖Δθ‖)`. -/
theorem remainder_isLittleO
    (F : EuclideanSpace ℝ (Fin p) → EuclideanSpace ℝ (Fin m))
    (L : EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin m))
    (θ₀ : EuclideanSpace ℝ (Fin p)) (hF : HasFDerivAt F L θ₀) (S : Finset (Fin p)) :
    (fun Δθ => (F (θ₀ + Δθ) - F (θ₀ + keepS S Δθ)) - (L Δθ - L (keepS S Δθ)))
      =o[𝓝 0] (fun Δθ => Δθ) := by
  have hr := hasFDerivAt_iff_isLittleO_nhds_zero.mp hF
  have hk_bigO : (fun Δθ => keepS S Δθ) =O[𝓝 (0 : EuclideanSpace ℝ (Fin p))] (fun Δθ => Δθ) :=
    isBigO_of_le _ (fun Δθ => norm_keepS_le S Δθ)
  have hk_tendsto : Tendsto (fun Δθ => keepS S Δθ) (𝓝 0) (𝓝 0) := by
    rw [tendsto_zero_iff_norm_tendsto_zero]
    refine squeeze_zero (fun _ => norm_nonneg _) (fun Δθ => norm_keepS_le S Δθ) ?_
    simpa using (continuous_norm.tendsto (0 : EuclideanSpace ℝ (Fin p)))
  have hr_k : (fun Δθ => F (θ₀ + keepS S Δθ) - F θ₀ - L (keepS S Δθ))
      =o[𝓝 0] (fun Δθ => Δθ) :=
    (hr.comp_tendsto hk_tendsto).trans_isBigO hk_bigO
  refine (hr.sub hr_k).congr_left ?_
  intro Δθ
  abel

/-- **Cota de error de trayectoria (no lineal, local).**
    Para todo `η > 0`, para `Δθ` suficientemente pequeño:
    `‖F(θ₀+Δθ) − F(θ₀+Δθ_S)‖ ≤ √R(S) · ‖Δθ_{Sᶜ}‖ + η ‖Δθ‖`. -/
theorem trajectory_error_bound
    (F : EuclideanSpace ℝ (Fin p) → EuclideanSpace ℝ (Fin m))
    (L : EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin m))
    (θ₀ : EuclideanSpace ℝ (Fin p)) (hF : HasFDerivAt F L θ₀) (S : Finset (Fin p))
    {η : ℝ} (hη : 0 < η) :
    ∀ᶠ Δθ in 𝓝 (0 : EuclideanSpace ℝ (Fin p)),
      ‖F (θ₀ + Δθ) - F (θ₀ + keepS S Δθ)‖
        ≤ Real.sqrt (removedColumnEnergy (jacobianOf L) S)
            * Real.sqrt (removedParamSq S (fun j => Δθ j)) + η * ‖Δθ‖ := by
  filter_upwards [(remainder_isLittleO F L θ₀ hF S).def hη] with Δθ hΔ
  calc ‖F (θ₀ + Δθ) - F (θ₀ + keepS S Δθ)‖
      ≤ ‖L Δθ - L (keepS S Δθ)‖
        + ‖(F (θ₀ + Δθ) - F (θ₀ + keepS S Δθ)) - (L Δθ - L (keepS S Δθ))‖ :=
          norm_le_insert' _ _
    _ ≤ _ := add_le_add (linear_part_bound L S Δθ) hΔ

/-- **Forma con el criterio del Stage 1.** Si `R_var(S) ≥ r`
    (energía conservada ≥ `r · tr(JᵀJ)`), entonces para todo `η > 0` y `Δθ`
    pequeño: `‖F(θ₀+Δθ) − F(θ₀+Δθ_S)‖ ≤ (√((1−r)·tr(JᵀJ)) + η) · ‖Δθ‖`. -/
theorem trajectory_error_from_Rvar
    (F : EuclideanSpace ℝ (Fin p) → EuclideanSpace ℝ (Fin m))
    (L : EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin m))
    (θ₀ : EuclideanSpace ℝ (Fin p)) (hF : HasFDerivAt F L θ₀) (S : Finset (Fin p))
    (r : ℝ)
    (h_kept : r * totalColumnEnergy (jacobianOf L)
                ≤ keptColumnEnergy (jacobianOf L) S)
    {η : ℝ} (hη : 0 < η) :
    ∀ᶠ Δθ in 𝓝 (0 : EuclideanSpace ℝ (Fin p)),
      ‖F (θ₀ + Δθ) - F (θ₀ + keepS S Δθ)‖
        ≤ (Real.sqrt ((1 - r) * totalColumnEnergy (jacobianOf L)) + η) * ‖Δθ‖ := by
  have hR : removedColumnEnergy (jacobianOf L) S
      ≤ (1 - r) * totalColumnEnergy (jacobianOf L) := by
    have := total_eq_kept_add_removed (jacobianOf L) S
    linarith
  filter_upwards [trajectory_error_bound F L θ₀ hF S hη] with Δθ hΔ
  have h1 : Real.sqrt (removedColumnEnergy (jacobianOf L) S)
      ≤ Real.sqrt ((1 - r) * totalColumnEnergy (jacobianOf L)) := Real.sqrt_le_sqrt hR
  have h2 := sqrt_removedParamSq_le S Δθ
  have h3 : 0 ≤ Real.sqrt (removedParamSq S (fun j => Δθ j)) := Real.sqrt_nonneg _
  have h4 : 0 ≤ Real.sqrt ((1 - r) * totalColumnEnergy (jacobianOf L)) := Real.sqrt_nonneg _
  calc ‖F (θ₀ + Δθ) - F (θ₀ + keepS S Δθ)‖
      ≤ Real.sqrt (removedColumnEnergy (jacobianOf L) S)
          * Real.sqrt (removedParamSq S (fun j => Δθ j)) + η * ‖Δθ‖ := hΔ
    _ ≤ Real.sqrt ((1 - r) * totalColumnEnergy (jacobianOf L)) * ‖Δθ‖ + η * ‖Δθ‖ := by
        have := mul_le_mul h1 h2 h3 h4
        linarith
    _ = (Real.sqrt ((1 - r) * totalColumnEnergy (jacobianOf L)) + η) * ‖Δθ‖ := by ring

end TrajectoryErrorBound

#print axioms TrajectoryErrorBound.trajectory_error_bound
#print axioms TrajectoryErrorBound.trajectory_error_from_Rvar
