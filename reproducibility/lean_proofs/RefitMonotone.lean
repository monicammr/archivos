import Mathlib.Order.ConditionallyCompleteLattice.Basic
import Mathlib.Data.Real.Archimedean
import Mathlib.Data.Finset.Basic

/-!
# Reajustar más parámetros nunca empeora el error (e_ajuste monótono)

`r θ ≥ 0` es el error (relativo) del modelo con parámetros `θ` frente a la respuesta del
modelo completo. Al reestimar el subconjunto `S`, los parámetros fuera de `S` quedan en `θ₀`
y los de `S` se mueven dentro de una caja `B` (en el código, `[|θ₀|/10, 10|θ₀|]`):

  `feas S = {θ ∈ B | ∀ j ∉ S, θ j = θ₀ j}`,   `fitErr S = inf { r θ | θ ∈ feas S }`.

* `fitErr_anti`: si `S ⊆ T`, `fitErr T ≤ fitErr S` (más parámetros libres ⇒ error ≤).
  En particular, reajustar también los parámetros de calibración `C` (escalas, offsets) nunca
  empeora: `fitErr (S ∪ C) ≤ fitErr S`.
* `fitErr_le_erel`: `e_ajuste ≤ e_rel`. El punto "sin reajuste" (los de `S` en el valor del
  escenario, el resto en `θ₀`) es factible, así que el mínimo no puede ser mayor.
* `admissible_mono`: si `S` es admisible (`fitErr S ≤ τ`) y `S ⊆ T`, `T` también lo es.
  El criterio de parada del voraz y de la poda es, por tanto, monótono.
-/

namespace RefitMonotone

variable {p : Type*} (r : (p → ℝ) → ℝ) (θ₀ : p → ℝ) (B : Set (p → ℝ))

/-- Parámetros factibles al reestimar sólo `S`. -/
def feas (S : Set p) : Set (p → ℝ) := {θ | θ ∈ B ∧ ∀ j, j ∉ S → θ j = θ₀ j}

/-- Error tras reestimar `S` (ínfimo sobre los factibles). -/
noncomputable def fitErr (S : Set p) : ℝ := sInf (r '' feas θ₀ B S)

lemma feas_mono {S T : Set p} (h : S ⊆ T) : feas θ₀ B S ⊆ feas θ₀ B T := by
  intro θ ⟨hB, hθ⟩
  exact ⟨hB, fun j hj => hθ j (fun hjS => hj (h hjS))⟩

/-- **Monotonía**: más parámetros libres ⇒ error de reajuste menor o igual. -/
theorem fitErr_anti (hr : ∀ θ, 0 ≤ r θ) {S T : Set p} (h : S ⊆ T)
    (hne : (feas θ₀ B S).Nonempty) : fitErr r θ₀ B T ≤ fitErr r θ₀ B S := by
  unfold fitErr
  apply csInf_le_csInf
  · exact ⟨0, by rintro _ ⟨θ, -, rfl⟩; exact hr θ⟩
  · exact hne.image r
  · exact Set.image_mono (feas_mono θ₀ B h)

/-- **Calibración**: reajustar además los parámetros `C` no empeora el error. -/
theorem fitErr_union_le (hr : ∀ θ, 0 ≤ r θ) (S C : Set p)
    (hne : (feas θ₀ B S).Nonempty) : fitErr r θ₀ B (S ∪ C) ≤ fitErr r θ₀ B S :=
  fitErr_anti r θ₀ B hr Set.subset_union_left hne

/-- **e_ajuste ≤ e_rel**: el punto sin reajuste es factible. -/
theorem fitErr_le_erel (hr : ∀ θ, 0 ≤ r θ) (S : Set p) (θs : p → ℝ)
    (hθs : θs ∈ feas θ₀ B S) : fitErr r θ₀ B S ≤ r θs := by
  unfold fitErr
  exact csInf_le ⟨0, by rintro _ ⟨θ, -, rfl⟩; exact hr θ⟩ ⟨θs, hθs, rfl⟩

/-- **Admisibilidad monótona**: si `S` cumple el umbral, cualquier `T ⊇ S` también. -/
theorem admissible_mono (hr : ∀ θ, 0 ≤ r θ) {S T : Set p} (h : S ⊆ T)
    (hne : (feas θ₀ B S).Nonempty) {τ : ℝ} (hS : fitErr r θ₀ B S ≤ τ) :
    fitErr r θ₀ B T ≤ τ :=
  (fitErr_anti r θ₀ B hr h hne).trans hS

end RefitMonotone

#print axioms RefitMonotone.fitErr_anti
#print axioms RefitMonotone.fitErr_le_erel
