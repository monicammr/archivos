import Mathlib.Algebra.Order.BigOperators.Ring.Finset
import Mathlib.Data.Real.Sqrt
import Mathlib.Data.Fintype.BigOperators
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring

/-!
# Cota de error de primer orden al fijar parámetros descartados

Sea `J : Fin m → Fin n → ℝ` la matriz de sensibilidad (filas = pares
estado × instante de tiempo, columnas = parámetros) y `S` el conjunto de
parámetros conservados. Para una perturbación `Δθ`, la respuesta linealizada
del modelo completo es `δx = J Δθ`; la del modelo reducido (parámetros de `Sᶜ`
fijados en su valor nominal) es `δx_S = J_S Δθ_S`.

Teorema principal (`first_order_error_sq_bound`):

  ‖J Δθ − J_S Δθ_S‖²  ≤  R(S) · ‖Δθ_{Sᶜ}‖²,   con  R(S) = ∑_{j ∉ S} ‖J_j‖² = ∑_{j∉S} (JᵀJ)_{jj}.

Consecuencia (`first_order_error_from_Rvar`): si la fracción de energía
conservada es `R_var(S) ≥ r` (criterio del Stage 1), entonces

  ‖J Δθ − J_S Δθ_S‖²  ≤  (1 − r) · tr(JᵀJ) · ‖Δθ‖².

Alcance: es una cota sobre la respuesta **linealizada** (primer orden en `Δθ`)
y vale para **cualquier** matriz `J`; no dice nada sobre el resto de Taylor ni
sobre cómo se calculó `J` numéricamente.
-/

open scoped BigOperators
open Finset

namespace FirstOrderErrorBound

variable {m n : ℕ}

/-- Parámetros descartados `Sᶜ` (misma forma que en `FitFromJtJDiagonal`). -/
def removedSet (S : Finset (Fin n)) : Finset (Fin n) :=
  (Finset.univ : Finset (Fin n)).filter (fun j => j ∉ S)

/-- Energía de la columna `j`: `‖J_j‖² = (JᵀJ)_{jj}` (idéntica a `FitFromJtJDiagonal.columnEnergy`). -/
noncomputable def columnEnergy (J : Fin m → Fin n → ℝ) (j : Fin n) : ℝ :=
  ∑ i : Fin m, (J i j) ^ 2

/-- Energía total `tr(JᵀJ)`. -/
noncomputable def totalColumnEnergy (J : Fin m → Fin n → ℝ) : ℝ :=
  ∑ j : Fin n, columnEnergy J j

/-- Energía descartada `R(S) = ∑_{j ∉ S} ‖J_j‖²`. -/
noncomputable def removedColumnEnergy (J : Fin m → Fin n → ℝ) (S : Finset (Fin n)) : ℝ :=
  ∑ j ∈ removedSet S, columnEnergy J j

/-- Energía conservada `∑_{j ∈ S} ‖J_j‖²`. -/
noncomputable def keptColumnEnergy (J : Fin m → Fin n → ℝ) (S : Finset (Fin n)) : ℝ :=
  ∑ j ∈ S, columnEnergy J j

/-- Respuesta linealizada del modelo completo: `(J Δθ)_i`. -/
def linResponse (J : Fin m → Fin n → ℝ) (Δθ : Fin n → ℝ) : Fin m → ℝ :=
  fun i => ∑ j : Fin n, J i j * Δθ j

/-- Respuesta linealizada del modelo reducido (parámetros de `Sᶜ` fijos): `(J_S Δθ_S)_i`. -/
def reducedResponse (J : Fin m → Fin n → ℝ) (S : Finset (Fin n)) (Δθ : Fin n → ℝ) :
    Fin m → ℝ :=
  fun i => ∑ j ∈ S, J i j * Δθ j

/-- Norma euclídea al cuadrado de un vector. -/
def sqNorm {k : ℕ} (v : Fin k → ℝ) : ℝ := ∑ i : Fin k, (v i) ^ 2

/-- `‖Δθ_{Sᶜ}‖²`: magnitud de la perturbación en los parámetros descartados. -/
def removedParamSq (S : Finset (Fin n)) (Δθ : Fin n → ℝ) : ℝ :=
  ∑ j ∈ removedSet S, (Δθ j) ^ 2

/-! ## Identidades básicas -/

theorem sqNorm_nonneg {k : ℕ} (v : Fin k → ℝ) : 0 ≤ sqNorm v :=
  Finset.sum_nonneg fun _ _ => sq_nonneg _

theorem columnEnergy_nonneg (J : Fin m → Fin n → ℝ) (j : Fin n) : 0 ≤ columnEnergy J j :=
  Finset.sum_nonneg fun _ _ => sq_nonneg _

theorem removedColumnEnergy_nonneg (J : Fin m → Fin n → ℝ) (S : Finset (Fin n)) :
    0 ≤ removedColumnEnergy J S :=
  Finset.sum_nonneg fun j _ => columnEnergy_nonneg J j

theorem removedParamSq_nonneg (S : Finset (Fin n)) (Δθ : Fin n → ℝ) :
    0 ≤ removedParamSq S Δθ :=
  Finset.sum_nonneg fun _ _ => sq_nonneg _

/-- Separar una suma sobre todos los parámetros en conservados + descartados. -/
theorem sum_split (S : Finset (Fin n)) (f : Fin n → ℝ) :
    ∑ j : Fin n, f j = ∑ j ∈ S, f j + ∑ j ∈ removedSet S, f j := by
  rw [← Finset.sum_filter_add_sum_filter_not (Finset.univ : Finset (Fin n)) (fun j => j ∈ S)]
  congr 1
  apply Finset.sum_congr _ (fun _ _ => rfl)
  ext j; simp

/-- `tr(JᵀJ) = energía conservada + energía descartada`. -/
theorem total_eq_kept_add_removed (J : Fin m → Fin n → ℝ) (S : Finset (Fin n)) :
    totalColumnEnergy J = keptColumnEnergy J S + removedColumnEnergy J S :=
  sum_split S (columnEnergy J)

/-- El error de truncamiento es exactamente la contribución de las columnas descartadas. -/
theorem response_sub_reduced (J : Fin m → Fin n → ℝ) (S : Finset (Fin n))
    (Δθ : Fin n → ℝ) (i : Fin m) :
    linResponse J Δθ i - reducedResponse J S Δθ i = ∑ j ∈ removedSet S, J i j * Δθ j := by
  simp only [linResponse, reducedResponse]
  rw [sum_split S (fun j => J i j * Δθ j)]
  ring

/-! ## Teorema principal -/

/-- **Cota de error de primer orden (forma cuadrática).**
    `‖J Δθ − J_S Δθ_S‖² ≤ R(S) · ‖Δθ_{Sᶜ}‖²`. -/
theorem first_order_error_sq_bound (J : Fin m → Fin n → ℝ) (S : Finset (Fin n))
    (Δθ : Fin n → ℝ) :
    sqNorm (fun i => linResponse J Δθ i - reducedResponse J S Δθ i)
      ≤ removedColumnEnergy J S * removedParamSq S Δθ := by
  simp only [sqNorm, response_sub_reduced]
  calc ∑ i : Fin m, (∑ j ∈ removedSet S, J i j * Δθ j) ^ 2
      ≤ ∑ i : Fin m, (∑ j ∈ removedSet S, (J i j) ^ 2) * ∑ j ∈ removedSet S, (Δθ j) ^ 2 :=
        Finset.sum_le_sum fun i _ => Finset.sum_mul_sq_le_sq_mul_sq _ _ _
    _ = (∑ i : Fin m, ∑ j ∈ removedSet S, (J i j) ^ 2) * ∑ j ∈ removedSet S, (Δθ j) ^ 2 := by
        rw [Finset.sum_mul]
    _ = removedColumnEnergy J S * removedParamSq S Δθ := by
        rw [Finset.sum_comm]; rfl

/-- **Cota de error de primer orden (forma con normas).**
    `‖J Δθ − J_S Δθ_S‖ ≤ √R(S) · ‖Δθ_{Sᶜ}‖`. -/
theorem first_order_error_bound (J : Fin m → Fin n → ℝ) (S : Finset (Fin n))
    (Δθ : Fin n → ℝ) :
    Real.sqrt (sqNorm (fun i => linResponse J Δθ i - reducedResponse J S Δθ i))
      ≤ Real.sqrt (removedColumnEnergy J S) * Real.sqrt (removedParamSq S Δθ) := by
  rw [← Real.sqrt_mul (removedColumnEnergy_nonneg J S)]
  exact Real.sqrt_le_sqrt (first_order_error_sq_bound J S Δθ)

/-- `‖Δθ_{Sᶜ}‖² ≤ ‖Δθ‖²`. -/
theorem removedParamSq_le (S : Finset (Fin n)) (Δθ : Fin n → ℝ) :
    removedParamSq S Δθ ≤ sqNorm Δθ :=
  Finset.sum_le_sum_of_subset_of_nonneg (Finset.subset_univ _)
    (fun _ _ _ => sq_nonneg _)

/-- **Conexión con el criterio del Stage 1 (energía descartada ≤ ε·tr(JᵀJ)).**
    `‖J Δθ − J_S Δθ_S‖² ≤ ε · tr(JᵀJ) · ‖Δθ‖²`. -/
theorem first_order_error_from_removed_fraction (J : Fin m → Fin n → ℝ)
    (S : Finset (Fin n)) (Δθ : Fin n → ℝ) (ε : ℝ)
    (h_removed : removedColumnEnergy J S ≤ ε * totalColumnEnergy J) :
    sqNorm (fun i => linResponse J Δθ i - reducedResponse J S Δθ i)
      ≤ ε * totalColumnEnergy J * sqNorm Δθ := by
  have hR := removedColumnEnergy_nonneg J S
  have hP := removedParamSq_nonneg S Δθ
  have hPle := removedParamSq_le S Δθ
  calc sqNorm (fun i => linResponse J Δθ i - reducedResponse J S Δθ i)
      ≤ removedColumnEnergy J S * removedParamSq S Δθ := first_order_error_sq_bound J S Δθ
    _ ≤ removedColumnEnergy J S * sqNorm Δθ := mul_le_mul_of_nonneg_left hPle hR
    _ ≤ ε * totalColumnEnergy J * sqNorm Δθ :=
        mul_le_mul_of_nonneg_right h_removed (sqNorm_nonneg Δθ)

/-- **Forma con `R_var`.** Si la fracción conservada cumple
    `keptColumnEnergy ≥ r · tr(JᵀJ)` (p. ej. `r = 0.89`), entonces
    `‖J Δθ − J_S Δθ_S‖² ≤ (1 − r) · tr(JᵀJ) · ‖Δθ‖²`. -/
theorem first_order_error_from_Rvar (J : Fin m → Fin n → ℝ)
    (S : Finset (Fin n)) (Δθ : Fin n → ℝ) (r : ℝ)
    (h_kept : r * totalColumnEnergy J ≤ keptColumnEnergy J S) :
    sqNorm (fun i => linResponse J Δθ i - reducedResponse J S Δθ i)
      ≤ (1 - r) * totalColumnEnergy J * sqNorm Δθ := by
  apply first_order_error_from_removed_fraction J S Δθ (1 - r)
  have := total_eq_kept_add_removed J S
  linarith

end FirstOrderErrorBound

#print axioms FirstOrderErrorBound.first_order_error_sq_bound
#print axioms FirstOrderErrorBound.first_order_error_bound
#print axioms FirstOrderErrorBound.first_order_error_from_removed_fraction
#print axioms FirstOrderErrorBound.first_order_error_from_Rvar
