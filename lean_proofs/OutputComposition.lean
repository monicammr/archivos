import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Analysis.Normed.Group.Basic
import Mathlib.Algebra.Order.BigOperators.Group.Finset

/-!
# De los estados a las salidas medidas: y_i = h(g_i(x(t_i), θ)) / σ_i

Las cotas de error del desarrollo (trayectorias, `CosineCertificate`, `CertifiedFiniteODE`) están
sobre los estados `x(t)`. El método usa las salidas medidas de PEtab. Este módulo transfiere esas
cotas a las salidas:

* `output_sq_bound`: si cada salida `y_i = G_i (x(t_i))` es Lipschitz en el estado con constante
  `K_i` (que incluye `1/σ_i` y la transformación), entonces
  `Σ_i (y_i − y'_i)² ≤ K² · Σ_i ‖x(t_i) − x'(t_i)‖²`, con `K = max_i K_i`.
* `output_uniform_bound`: si además `‖x(t) − x'(t)‖ ≤ ε` en todo instante (cota de trayectoria),
  `Σ_i (y_i − y'_i)² ≤ m · K² · ε²` (m = número de mediciones).
* `log_lipschitz`: la transformación logarítmica es Lipschitz con constante `1/c` donde la
  salida es `≥ c > 0`; la positividad de las especies está demostrada en `PositivityInvariance`
  y `StrictNetwork`. Igual para `log10` (constante `1/(c log 10)`).
-/

namespace OutputComposition

open Finset

variable {E : Type*} [SeminormedAddCommGroup E] {ι : Type*}

/-- **Cota de salidas a partir de los estados** (suma de cuadrados). -/
theorem output_sq_bound (s : Finset ι) (G : ι → E → ℝ) (x x' : ι → E) (K : ℝ)
    (hK : ∀ i ∈ s, |G i (x i) - G i (x' i)| ≤ K * ‖x i - x' i‖) :
    ∑ i ∈ s, (G i (x i) - G i (x' i)) ^ 2 ≤ K ^ 2 * ∑ i ∈ s, ‖x i - x' i‖ ^ 2 := by
  rw [mul_sum]
  apply sum_le_sum
  intro i hi
  have h1 := hK i hi
  have h0 : 0 ≤ |G i (x i) - G i (x' i)| := abs_nonneg _
  calc (G i (x i) - G i (x' i)) ^ 2 = |G i (x i) - G i (x' i)| ^ 2 := (sq_abs _).symm
    _ ≤ (K * ‖x i - x' i‖) ^ 2 := pow_le_pow_left₀ h0 h1 2
    _ = K ^ 2 * ‖x i - x' i‖ ^ 2 := by ring

/-- **Cota uniforme**: con `‖x(t_i) − x'(t_i)‖ ≤ ε` para todas las mediciones. -/
theorem output_uniform_bound (s : Finset ι) (G : ι → E → ℝ) (x x' : ι → E) (K ε : ℝ)
    (hK : ∀ i ∈ s, |G i (x i) - G i (x' i)| ≤ K * ‖x i - x' i‖)
    (hε : ∀ i ∈ s, ‖x i - x' i‖ ≤ ε) :
    ∑ i ∈ s, (G i (x i) - G i (x' i)) ^ 2 ≤ s.card * K ^ 2 * ε ^ 2 := by
  refine (output_sq_bound s G x x' K hK).trans ?_
  have : ∑ i ∈ s, ‖x i - x' i‖ ^ 2 ≤ ∑ _i ∈ s, ε ^ 2 := by
    apply sum_le_sum
    intro i hi
    exact pow_le_pow_left₀ (norm_nonneg _) (hε i hi) 2
  rw [sum_const, nsmul_eq_mul] at this
  nlinarith [sq_nonneg K]

/-- **log es Lipschitz** con constante `1/c` en `[c, ∞)`, `c > 0`. -/
theorem log_lipschitz {a b c : ℝ} (hc : 0 < c) (ha : c ≤ a) (hb : c ≤ b) :
    |Real.log a - Real.log b| ≤ |a - b| / c := by
  have ha0 : 0 < a := hc.trans_le ha
  have hb0 : 0 < b := hc.trans_le hb
  -- log u − log v ≤ (u − v)/v  (de log z ≤ z − 1 con z = u/v)
  have key : ∀ u v : ℝ, 0 < u → 0 < v → Real.log u - Real.log v ≤ (u - v) / v := by
    intro u v hu hv
    have := Real.log_le_sub_one_of_pos (div_pos hu hv)
    rw [Real.log_div hu.ne' hv.ne'] at this
    calc Real.log u - Real.log v ≤ u / v - 1 := this
      _ = (u - v) / v := by field_simp
  rw [abs_le]
  constructor
  · -- −(|a−b|/c) ≤ log a − log b, i.e. log b − log a ≤ |a−b|/c
    have h := key b a hb0 ha0
    have : (b - a) / a ≤ |a - b| / c := by
      rcases le_or_gt (b - a) 0 with h1 | h1
      · exact (div_nonpos_of_nonpos_of_nonneg h1 ha0.le).trans (div_nonneg (abs_nonneg _) hc.le)
      · rw [abs_sub_comm, abs_of_pos h1]
        exact div_le_div_of_nonneg_left h1.le hc ha
    linarith
  · have h := key a b ha0 hb0
    have : (a - b) / b ≤ |a - b| / c := by
      rcases le_or_gt (a - b) 0 with h1 | h1
      · exact (div_nonpos_of_nonpos_of_nonneg h1 hb0.le).trans (div_nonneg (abs_nonneg _) hc.le)
      · rw [abs_of_pos h1]
        exact div_le_div_of_nonneg_left h1.le hc hb
    linarith

/-- **log10** (`log x / log 10`) es Lipschitz con constante `1/(c · log 10)` en `[c, ∞)`. -/
theorem log10_lipschitz {a b c : ℝ} (hc : 0 < c) (ha : c ≤ a) (hb : c ≤ b) :
    |Real.log a / Real.log 10 - Real.log b / Real.log 10| ≤ |a - b| / (c * Real.log 10) := by
  have h10 : 0 < Real.log 10 := Real.log_pos (by norm_num)
  rw [← sub_div, abs_div, abs_of_pos h10, div_le_div_iff₀ h10 (mul_pos hc h10)]
  have := log_lipschitz hc ha hb
  rw [le_div_iff₀ hc] at this
  nlinarith

end OutputComposition

#print axioms OutputComposition.output_uniform_bound
#print axioms OutputComposition.log10_lipschitz
