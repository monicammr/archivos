import GreedySelection
import TrajectoryErrorBound

/-!
# Mecanismos detrás de los patrones de robustez (sección 3.2)

La clasificación A–D es empírica, pero sus mecanismos se pueden demostrar:

* **Patrón D (efectos opuestos):** si una combinación `u ≠ 0` de parámetros de `S` no cambia
  la respuesta linealizada (`Z u = 0`, p. ej. `J_a = λ J_b` con `u = e_a − λ e_b`), entonces
  (i) ningún `κ₀` acepta `S` (`not_okKappa_of_kernel`), y (ii) la estimación por mínimos
  cuadrados no es única: `v` y `v + u` ajustan igual (`ls_not_unique_of_kernel`).
* **Patrón A (estructura dispersa / leyes de conservación):** si la energía descartada es
  nula (`R(S) = 0`, columnas descartadas nulas), la reducción es exacta a primer orden:
  `J Δθ = J_S Δθ_S` (`exact_reduction_of_zero_energy`).
-/

open Identifiability GreedySelection FirstOrderErrorBound TrajectoryErrorBound

namespace PatternMechanisms

variable {p : ℕ} {W : Type*} [NormedAddCommGroup W] [InnerProductSpace ℝ W]

/-- **Patrón D, filtro κ.** Si existe `u ≠ 0` soportado en `S` con `Z u = 0`, ningún `κ₀`
acepta `S`. -/
theorem not_okKappa_of_kernel (Z : EuclideanSpace ℝ (Fin p) →L[ℝ] W) (κ₀ : ℝ)
    (S : Finset (Fin p)) (u : EuclideanSpace ℝ (Fin p)) (hu : SupportedOn S u) (hu0 : u ≠ 0)
    (hZu : Z u = 0) : ¬ okKappa Z κ₀ S := by
  rintro ⟨σmin, σmax, hσ, _, hb⟩
  have h := (hb u hu).1
  rw [hZu, norm_zero] at h
  have : 0 < σmin * ‖u‖ := mul_pos hσ (norm_pos_iff.2 hu0)
  linarith

/-- **Patrón D, identificabilidad.** Si `Z u = 0`, todo minimizador `v` tiene otro
minimizador distinto `v + u`: los parámetros no son identificables. -/
theorem ls_not_unique_of_kernel {V : Type*} [NormedAddCommGroup V] [InnerProductSpace ℝ V]
    (Z : V →L[ℝ] W) (y : W) (v u : V) (hu0 : u ≠ 0) (hZu : Z u = 0)
    (hv : IsLSMin Z y v) : IsLSMin Z y (v + u) ∧ v + u ≠ v := by
  refine ⟨fun w => ?_, fun h => hu0 (by simpa using h)⟩
  rw [map_add, hZu, add_zero]; exact hv w

/-- Caso concreto de efectos opuestos: si la columna `a` es `λ` veces la columna `b`
(`a ≠ b`), el vector `u = e_a − λ e_b` es no nulo y `Z u = 0`. -/
theorem opposing_pair_kernel (Z : EuclideanSpace ℝ (Fin p) →L[ℝ] W) {a b : Fin p} (hab : a ≠ b)
    (lam : ℝ) (hcol : Z (EuclideanSpace.single a 1) = lam • Z (EuclideanSpace.single b 1)) :
    EuclideanSpace.single a (1 : ℝ) - lam • EuclideanSpace.single b 1 ≠ 0 ∧
      Z (EuclideanSpace.single a 1 - lam • EuclideanSpace.single b 1) = 0 := by
  refine ⟨fun h => ?_, by rw [map_sub, map_smul, hcol, sub_self]⟩
  have := congrArg (fun v : EuclideanSpace ℝ (Fin p) => v a) h
  simp [EuclideanSpace.single_apply, hab] at this

/-- **Patrón A, reducción exacta.** Si la energía descartada es nula, la respuesta
linealizada del modelo reducido coincide con la del completo para toda perturbación. -/
theorem exact_reduction_of_zero_energy {m : ℕ}
    (L : EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin m)) (S : Finset (Fin p))
    (hR : removedColumnEnergy (jacobianOf L) S = 0) (Δθ : EuclideanSpace ℝ (Fin p)) :
    L Δθ = L (keepS S Δθ) := by
  have h := linear_part_bound L S Δθ
  rw [hR, Real.sqrt_zero, zero_mul] at h
  exact sub_eq_zero.1 (norm_le_zero_iff.1 h)

end PatternMechanisms

