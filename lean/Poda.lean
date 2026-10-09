import Mathlib.Data.Finset.Card

/-!
# Poda (eliminación hacia atrás): el subconjunto final es mínimo por inclusión

Tras la selección voraz, se intenta quitar parámetros del subconjunto `S` mientras el resultado
siga siendo admisible. `Q T` es el criterio de admisibilidad (en el artículo: `|T| ≥ 2` y
mediana de `e_ajuste(T) ≤ 0,436`); aquí es un predicado arbitrario, de modo que el teorema vale
para cualquier criterio.

`pick T` elige qué parámetro quitar: devuelve `some x` con `x ∈ T` y `Q (T.erase x)`, o `none`
si no se puede quitar ninguno. La implementación (`stage_reclass.py --poda`) prueba los
parámetros en orden creciente de energía `E_j` y quita el primero que puede quitarse: es un caso
particular de `pick`.

* `prune_spec`: si `Q S`, el resultado `R = prune S` cumple
  1. `Q R` (sigue siendo admisible),
  2. `R ⊆ S` (sólo se quitan parámetros),
  3. `∀ x ∈ R, ¬ Q (R.erase x)` (**mínimo por inclusión**: no sobra ningún parámetro).
* El algoritmo termina: cada paso reduce `|T|` (recursión bien fundada en el cardinal).

No se afirma cardinalidad mínima global (problema combinatorio): puede existir otro subconjunto
admisible más pequeño que no contenga a `R`.
-/

namespace Poda

variable {α : Type*} [DecidableEq α]

/-- Eliminación hacia atrás con regla de elección `pick`. -/
def prune (Q : Finset α → Prop) (pick : Finset α → Option α)
    (hpick : ∀ T x, pick T = some x → x ∈ T ∧ Q (T.erase x)) : Finset α → Finset α
  | T =>
    match h : pick T with
    | none => T
    | some x =>
      have : (T.erase x).card < T.card := Finset.card_erase_lt_of_mem (hpick T x h).1
      prune Q pick hpick (T.erase x)
termination_by T => T.card

/-- **Corrección de la poda**: admisible, contenido en `S` y mínimo por inclusión. -/
theorem prune_spec (Q : Finset α → Prop) (pick : Finset α → Option α)
    (hpick : ∀ T x, pick T = some x → x ∈ T ∧ Q (T.erase x))
    (hnone : ∀ T, pick T = none → ∀ x ∈ T, ¬ Q (T.erase x)) :
    ∀ S : Finset α, Q S →
      Q (prune Q pick hpick S) ∧ prune Q pick hpick S ⊆ S ∧
        ∀ x ∈ prune Q pick hpick S, ¬ Q ((prune Q pick hpick S).erase x) := by
  intro S
  induction S using Finset.strongInduction with
  | H T ih =>
    intro hQ
    rw [prune]
    split
    · next h => exact ⟨hQ, subset_rfl, hnone T h⟩
    · next x h =>
      have hx := hpick T x h
      obtain ⟨h1, h2, h3⟩ := ih (T.erase x) (Finset.erase_ssubset hx.1) hx.2
      exact ⟨h1, h2.trans (Finset.erase_subset x T), h3⟩

/-- Forma de uso: existe un subconjunto admisible de `S`, mínimo por inclusión, que se obtiene
con la poda (para cualquier regla de elección válida). -/
theorem exists_minimal_admissible (Q : Finset α → Prop) (pick : Finset α → Option α)
    (hpick : ∀ T x, pick T = some x → x ∈ T ∧ Q (T.erase x))
    (hnone : ∀ T, pick T = none → ∀ x ∈ T, ¬ Q (T.erase x))
    (S : Finset α) (hS : Q S) :
    ∃ R ⊆ S, Q R ∧ ∀ x ∈ R, ¬ Q (R.erase x) := by
  obtain ⟨h1, h2, h3⟩ := prune_spec Q pick hpick hnone S hS
  exact ⟨_, h2, h1, h3⟩

end Poda

#print axioms Poda.prune_spec
