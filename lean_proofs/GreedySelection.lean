import IdentifiabilityConditioning

/-!
# El algoritmo greedy de selección (sección 2.3) y sus garantías

Los parámetros se recorren en orden descendente de energía `E_j`. Para cada candidato `j`:
si el conjunto ya cumple el criterio de parada (`stop`, p. ej. `R_var ≥ 0.89` y `|S| ≥ 2`)
se termina; si `S ∪ {j}` pasa el filtro de colinealidad (`ok`: `κ ≤ 10` y `VIF ≤ 10`) se
acepta; si no, `j` se descarta **permanentemente**.

Resultados (para `ok`, `stop` cualesquiera):
* `greedy_ok`: el resultado siempre pasa el filtro (si el conjunto inicial lo pasa).
* `greedy_subset`: el resultado está formado por candidatos.
* `greedy_discard_permanent`: si el filtro es **antimonótono** (quitar parámetros no lo
  empeora), todo candidato descartado tampoco sería aceptado por el conjunto final, salvo
  que el algoritmo se haya detenido por el criterio de parada.

Instancia concreta: `okKappa` (κ ≤ κ₀ sobre los parámetros de `S`) y `okVIF`
(VIF_j ≤ V para `j ∈ S`) son antimonótonos, y el resultado cumple las hipótesis de los
teoremas de estabilidad de `IdentifiabilityConditioning.lean`.
-/

namespace GreedySelection

variable {α : Type*} [DecidableEq α]

/-- El algoritmo greedy con descarte permanente. -/
def greedy (ok stop : Finset α → Prop) [DecidablePred ok] [DecidablePred stop] :
    List α → Finset α → Finset α
  | [], S => S
  | j :: rest, S =>
      if stop S then S
      else if ok (insert j S) then greedy ok stop rest (insert j S)
      else greedy ok stop rest S

variable (ok stop : Finset α → Prop) [DecidablePred ok] [DecidablePred stop]

/-- El resultado siempre pasa el filtro `ok`. -/
theorem greedy_ok (l : List α) (S : Finset α) (hS : ok S) : ok (greedy ok stop l S) := by
  induction l generalizing S with
  | nil => simpa [greedy] using hS
  | cons j rest ih =>
    simp only [greedy]
    split_ifs with h1 h2
    · exact hS
    · exact ih _ h2
    · exact ih _ hS

/-- El resultado contiene al conjunto inicial y solo añade candidatos de la lista. -/
theorem greedy_subset (l : List α) (S : Finset α) :
    S ⊆ greedy ok stop l S ∧ greedy ok stop l S ⊆ S ∪ l.toFinset := by
  induction l generalizing S with
  | nil => simp [greedy]
  | cons j rest ih =>
    simp only [greedy]
    split_ifs with h1 h2
    · exact ⟨subset_rfl, Finset.subset_union_left⟩
    · obtain ⟨a, b⟩ := ih (insert j S)
      refine ⟨(Finset.subset_insert j S).trans a, b.trans ?_⟩
      intro x hx
      simp only [Finset.mem_union, Finset.mem_insert, List.mem_toFinset, List.mem_cons] at hx ⊢
      tauto
    · obtain ⟨a, b⟩ := ih S
      refine ⟨a, b.trans ?_⟩
      intro x hx
      simp only [Finset.mem_union, List.mem_toFinset, List.mem_cons] at hx ⊢
      tauto

/-- **Descarte permanente.** Si `ok` es antimonótono, todo candidato `j` de la lista que no
quedó en el resultado `R` cumple: o bien `R ∪ {j}` no pasa el filtro, o bien el algoritmo se
detuvo por el criterio de parada (`stop R`). -/
theorem greedy_discard_permanent
    (hanti : ∀ S T : Finset α, S ⊆ T → ok T → ok S)
    (l : List α) (S : Finset α) :
    ∀ j ∈ l, j ∉ greedy ok stop l S →
      ¬ ok (insert j (greedy ok stop l S)) ∨ stop (greedy ok stop l S) := by
  induction l generalizing S with
  | nil => simp
  | cons j rest ih =>
    intro i hi hiR
    simp only [greedy] at hiR ⊢
    split_ifs with h1 h2
    · exact Or.inr h1
    · rw [if_neg h1, if_pos h2] at hiR
      rcases List.mem_cons.1 hi with rfl | hi'
      · exact absurd ((greedy_subset ok stop rest _).1 (Finset.mem_insert_self _ _)) hiR
      · exact ih _ i hi' hiR
    · rw [if_neg h1, if_neg h2] at hiR
      rcases List.mem_cons.1 hi with rfl | hi'
      · left
        intro hok
        apply h2
        apply hanti _ _ _ hok
        exact Finset.insert_subset_insert _ (greedy_subset ok stop rest S).1
      · exact ih _ i hi' hiR

end GreedySelection

/-! ## Instancia: filtros κ y VIF sobre la matriz normalizada -/

namespace GreedySelection

open Identifiability

variable {p : ℕ} {W : Type*} [NormedAddCommGroup W] [InnerProductSpace ℝ W]

/-- `u` está soportado en `S` (los parámetros fuera de `S` están fijos). -/
def SupportedOn (S : Finset (Fin p)) (u : EuclideanSpace ℝ (Fin p)) : Prop := ∀ i ∉ S, u i = 0

/-- Filtro κ: existen `σmin > 0` y `σmax ≤ κ₀ σmin` con
`σmin ‖u‖ ≤ ‖Z u‖ ≤ σmax ‖u‖` para todo `u` soportado en `S` (es decir `κ(Z_S) ≤ κ₀`). -/
def okKappa (Z : EuclideanSpace ℝ (Fin p) →L[ℝ] W) (κ₀ : ℝ) (S : Finset (Fin p)) : Prop :=
  ∃ σmin σmax : ℝ, 0 < σmin ∧ σmax ≤ κ₀ * σmin ∧
    ∀ u, SupportedOn S u → σmin * ‖u‖ ≤ ‖Z u‖ ∧ ‖Z u‖ ≤ σmax * ‖u‖

/-- Filtro VIF: para cada `j ∈ S`, toda combinación soportada en `S` con `u_j = 1` cumple
`‖Z u‖² ≥ 1/V` (es decir `VIF_j(Z_S) ≤ V`). -/
def okVIF (Z : EuclideanSpace ℝ (Fin p) →L[ℝ] W) (V : ℝ) (S : Finset (Fin p)) : Prop :=
  ∀ j ∈ S, ∀ u, SupportedOn S u → u j = 1 → 1 / V ≤ ‖Z u‖ ^ 2

lemma supportedOn_mono {S T : Finset (Fin p)} (hST : S ⊆ T) {u : EuclideanSpace ℝ (Fin p)}
    (hu : SupportedOn S u) : SupportedOn T u := fun i hi => hu i (fun h => hi (hST h))

/-- El filtro κ es antimonótono: quitar parámetros no aumenta κ. -/
theorem okKappa_anti (Z : EuclideanSpace ℝ (Fin p) →L[ℝ] W) (κ₀ : ℝ) :
    ∀ S T : Finset (Fin p), S ⊆ T → okKappa Z κ₀ T → okKappa Z κ₀ S := by
  rintro S T hST ⟨σmin, σmax, h0, hk, hb⟩
  exact ⟨σmin, σmax, h0, hk, fun u hu => hb u (supportedOn_mono hST hu)⟩

/-- El filtro VIF es antimonótono: quitar parámetros no aumenta ningún VIF. -/
theorem okVIF_anti (Z : EuclideanSpace ℝ (Fin p) →L[ℝ] W) (V : ℝ) :
    ∀ S T : Finset (Fin p), S ⊆ T → okVIF Z V T → okVIF Z V S := by
  intro S T hST h j hj u hu huj
  exact h j (hST hj) u (supportedOn_mono hST hu) huj

/-- **Garantía del algoritmo de la sección 2.3.** Con el filtro conjunto κ ≤ κ₀ y VIF ≤ V
y cualquier criterio de parada, el subconjunto devuelto `R` (empezando desde `∅`):
1. cumple `κ(Z_R) ≤ κ₀` y `VIF_j(Z_R) ≤ V` para todo `j ∈ R`;
2. está formado por candidatos de la lista;
3. todo candidato descartado seguiría violando el filtro con `R`
   (salvo que el algoritmo se detuviera por el criterio de parada). -/
theorem greedy_kappa_vif_guarantee (Z : EuclideanSpace ℝ (Fin p) →L[ℝ] W) (κ₀ V : ℝ)
    (stop : Finset (Fin p) → Prop) [DecidablePred stop]
    [DecidablePred (fun S => okKappa Z κ₀ S ∧ okVIF Z V S)] (l : List (Fin p)) :
    let R := greedy (fun S => okKappa Z κ₀ S ∧ okVIF Z V S) stop l ∅
    (okKappa Z κ₀ R ∧ okVIF Z V R) ∧ R ⊆ l.toFinset ∧
      ∀ j ∈ l, j ∉ R →
        ¬ (okKappa Z κ₀ (insert j R) ∧ okVIF Z V (insert j R)) ∨ stop R := by
  intro R
  have hempty : okKappa Z κ₀ ∅ ∧ okVIF Z V ∅ := by
    refine ⟨⟨1, κ₀, one_pos, by simp, fun u hu => ?_⟩, fun j hj => absurd hj (by simp)⟩
    have hu0 : u = 0 := by
      ext i; exact hu i (by simp)
    subst hu0; simp
  refine ⟨greedy_ok (fun S => okKappa Z κ₀ S ∧ okVIF Z V S) stop l ∅ hempty, ?_, ?_⟩
  · simpa using (greedy_subset (fun S => okKappa Z κ₀ S ∧ okVIF Z V S) stop l ∅).2
  · exact greedy_discard_permanent _ stop
      (fun S T hST h => ⟨okKappa_anti Z κ₀ S T hST h.1, okVIF_anti Z V S T hST h.2⟩) l ∅

end GreedySelection

#print axioms GreedySelection.greedy_kappa_vif_guarantee
