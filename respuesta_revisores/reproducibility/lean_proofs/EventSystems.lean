import LocalExistence

/-!
# Hipótesis 2: sistemas con eventos en tiempos fijos

Los teoremas de diferenciabilidad suponen un campo C¹ sin discontinuidades. Aquí se extienden a
sistemas con **eventos en tiempos fijos** (como Smith_BMCSystBiol2013: estímulos de insulina en
`t = t_ins, 2880, 2895`, con `t_ins` fijo): la integración se divide en tramos `k = 0, 1, 2, …`
de duración `L k`; en el tramo `k` el estado (en tiempo local `s ∈ [0, L k]`) resuelve
`ẏ = f_k(y, θ)`, y al final del tramo un mapa de reinicio `R_k` (la asignación del evento, que
puede ser la identidad salvo en las componentes reasignadas) da el estado inicial del tramo
siguiente.

`event_hasFDerivAt`: si cada `f_k` es C¹ en un abierto que contiene el tramo nominal, cada
`R_k` es diferenciable en el punto nominal y el dato inicial es diferenciable, entonces las
soluciones de todos los tramos existen para `θ` cerca de `θ₀` y la trayectoria es diferenciable
en `θ₀` en todo instante de todo tramo. Solo se necesita la trayectoria nominal.
-/

open Set Filter Topology

namespace EventSystems

variable {n : ℕ} {P : Type*} [NormedAddCommGroup P] [NormedSpace ℝ P] [FiniteDimensional ℝ P]

/-- **Diferenciabilidad respecto a `θ` para sistemas con eventos en tiempos fijos.** -/
theorem event_hasFDerivAt
    (f : ℕ → EuclideanSpace ℝ (Fin n) → P → EuclideanSpace ℝ (Fin n))
    (U : ℕ → Set (EuclideanSpace ℝ (Fin n) × P)) (hU : ∀ k, IsOpen (U k))
    (hf : ∀ k, ContDiffOn ℝ 1 (fun z : EuclideanSpace ℝ (Fin n) × P => f k z.1 z.2) (U k))
    (L : ℕ → ℝ) (hL : ∀ k, 0 ≤ L k)
    (R : ℕ → EuclideanSpace ℝ (Fin n) → P → EuclideanSpace ℝ (Fin n))
    (y₀ : ℕ → ℝ → EuclideanSpace ℝ (Fin n)) (θ₀ : P)
    (hy₀ : ∀ k, ∀ t ∈ Icc 0 (L k),
      HasDerivWithinAt (y₀ k) (f k (y₀ k t) θ₀) (Icc 0 (L k)) t)
    (hγ : ∀ k, ∀ t ∈ Icc 0 (L k), (y₀ k t, θ₀) ∈ U k)
    (hR : ∀ k, DifferentiableAt ℝ (fun z : EuclideanSpace ℝ (Fin n) × P => R k z.1 z.2)
      (y₀ k (L k), θ₀))
    (hlink : ∀ k, y₀ (k + 1) 0 = R k (y₀ k (L k)) θ₀)
    (x0 : P → EuclideanSpace ℝ (Fin n)) (hx0 : DifferentiableAt ℝ x0 θ₀)
    (hx00 : x0 θ₀ = y₀ 0 0) :
    ∃ Y : ℕ → P → ℝ → EuclideanSpace ℝ (Fin n),
      (∀ k, Y k θ₀ = y₀ k) ∧
      (∀ k, ∀ᶠ θ in 𝓝 θ₀, ∀ t ∈ Icc 0 (L k),
        HasDerivWithinAt (Y k θ) (f k (Y k θ t) θ) (Icc 0 (L k)) t) ∧
      (∀ᶠ θ in 𝓝 θ₀, Y 0 θ 0 = x0 θ) ∧
      (∀ k, ∀ᶠ θ in 𝓝 θ₀, Y (k + 1) θ 0 = R k (Y k θ (L k)) θ) ∧
      (∀ k, ∀ s ∈ Icc 0 (L k), DifferentiableAt ℝ (fun θ => Y k θ s) θ₀) := by
  -- un tramo: dato inicial diferenciable ⇒ familia de soluciones diferenciable
  have step : ∀ k (ι : P → EuclideanSpace ℝ (Fin n)), DifferentiableAt ℝ ι θ₀ →
      ι θ₀ = y₀ k 0 → ∃ y : P → ℝ → EuclideanSpace ℝ (Fin n), y θ₀ = y₀ k ∧
        (∀ᶠ θ in 𝓝 θ₀, y θ 0 = ι θ ∧ ∀ t ∈ Icc 0 (L k),
          HasDerivWithinAt (y θ) (f k (y θ t) θ) (Icc 0 (L k)) t) ∧
        ∀ s ∈ Icc 0 (L k), DifferentiableAt ℝ (fun θ => y θ s) θ₀ := by
    intro k ι hι hι0
    obtain ⟨y, hyθ₀, hev, S, -, -, hSder⟩ :=
      LocalExistence.hasFDerivAt_of_nominal_solution (f k) (hU k) (hf k) (hL k) (y₀ k) θ₀
        (hy₀ k) (hγ k) ι (fderiv ℝ ι θ₀) hι.hasFDerivAt hι0
    exact ⟨y, hyθ₀, hev, fun s hs => (hSder s hs).differentiableAt⟩
  choose! Fam hFam using step
  -- construcción recursiva de los tramos
  let Y : ℕ → P → ℝ → EuclideanSpace ℝ (Fin n) := fun k =>
    Nat.rec (motive := fun _ => P → ℝ → EuclideanSpace ℝ (Fin n)) (Fam 0 x0)
      (fun k Yk => Fam (k + 1) (fun θ => R k (Yk θ (L k)) θ)) k
  -- dato inicial de cada tramo
  let init : ℕ → P → EuclideanSpace ℝ (Fin n) := fun k =>
    Nat.casesOn (motive := fun _ => P → EuclideanSpace ℝ (Fin n)) k x0
      (fun k => fun θ => R k (Y k θ (L k)) θ)
  have hYinit : ∀ k, Y k = Fam k (init k) := fun k => by cases k <;> rfl
  have hinit0 : init 0 = x0 := rfl
  have hinits : ∀ k, init (k + 1) = fun θ => R k (Y k θ (L k)) θ := fun k => rfl
  -- el dato inicial de cada tramo es diferenciable y coincide con el nominal
  have key : ∀ k, DifferentiableAt ℝ (init k) θ₀ ∧ init k θ₀ = y₀ k 0 := by
    intro k
    induction k with
    | zero => exact ⟨hx0, hx00⟩
    | succ k ih =>
        obtain ⟨hYθ₀, -, hdiff⟩ := hFam k (init k) ih.1 ih.2
        rw [← hYinit] at hYθ₀ hdiff
        rw [hinits]
        refine ⟨?_, ?_⟩
        · have h1 : DifferentiableAt ℝ (fun θ => (Y k θ (L k), θ)) θ₀ :=
            (hdiff (L k) ⟨hL k, le_rfl⟩).prodMk differentiableAt_id
          have h2 : DifferentiableAt ℝ (fun z : EuclideanSpace ℝ (Fin n) × P => R k z.1 z.2)
              (Y k θ₀ (L k), θ₀) := by rw [hYθ₀]; exact hR k
          have h3 := DifferentiableAt.comp (f := fun θ => (Y k θ (L k), θ)) θ₀ h2 h1
          exact h3
        · show R k (Y k θ₀ (L k)) θ₀ = y₀ (k + 1) 0
          rw [hYθ₀, hlink]
  have hprop : ∀ k, Y k θ₀ = y₀ k ∧
      (∀ᶠ θ in 𝓝 θ₀, Y k θ 0 = init k θ ∧ ∀ t ∈ Icc 0 (L k),
        HasDerivWithinAt (Y k θ) (f k (Y k θ t) θ) (Icc 0 (L k)) t) ∧
      ∀ s ∈ Icc 0 (L k), DifferentiableAt ℝ (fun θ => Y k θ s) θ₀ := by
    intro k
    rw [hYinit k]
    exact hFam k (init k) (key k).1 (key k).2
  refine ⟨Y, fun k => (hprop k).1, fun k => (hprop k).2.1.mono fun θ h => h.2,
    (hprop 0).2.1.mono fun θ h => by rw [h.1, hinit0], fun k => ?_, fun k => (hprop k).2.2⟩
  exact (hprop (k + 1)).2.1.mono fun θ h => by rw [h.1, hinits]

end EventSystems

#print axioms EventSystems.event_hasFDerivAt
