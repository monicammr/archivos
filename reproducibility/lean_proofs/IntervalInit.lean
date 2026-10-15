import StrictNetwork

/-!
# Condiciones iniciales θ-dependientes evaluadas por intervalos racionales

Algunos modelos fijan el dato inicial en el estado estacionario, con fórmulas `G(θ)` que llevan
raíces cuadradas (`a^(1/2)`) y restas. El signo de `G(θ₀)` no se deduce de la sintaxis, pero sí
se puede **certificar** evaluando `G` en `θ₀` (racional) con aritmética de intervalos exacta en
`ℚ`: cada raíz cuadrada se acota con candidatos `l, u` que Lean comprueba (`l² ≤ x ≤ u²`).

* `ival θq e`: intervalo racional `[l, u]` que contiene `e(θq)`, y certificado de que `e` está
  bien definida en `θq` (denominadores `≠ 0`, bases de raíces `> 0`). `ival_sound`.
* `checkInitI`: el intervalo de cada `Gᵢ(θ₀)` es `≥ 0`, y `> 0` en `Σ`.
* `strict_final_initI`: el teorema final de `StrictNetwork` con esta comprobación del dato
  inicial. Sin condiciones pendientes.
-/

open Set Filter Topology KineticRegularity PositivityInvariance KineticCheck KineticNetwork
  StrictExistence StrictNetwork

namespace IntervalInit

variable {n p : ℕ}

/-- Raíz entera por bisección (sólo da candidatos; la cota se comprueba aparte). -/
def bsqrt : ℕ → ℕ → ℕ → ℕ → ℕ
  | 0, _, lo, _ => lo
  | f + 1, m, lo, hi =>
      if hi ≤ lo + 1 then lo
      else if (lo + hi) / 2 * ((lo + hi) / 2) ≤ m then bsqrt f m ((lo + hi) / 2) hi
      else bsqrt f m lo ((lo + hi) / 2)

/-- Escala de la aproximación: `10³⁰`. -/
def Dq : ℚ := 10 ^ 30

/-- Candidato a cota inferior de `√x`. -/
def sqLo (x : ℚ) : ℚ :=
  (bsqrt 400 (⌊x * Dq ^ 2⌋.toNat) 0 (⌊x * Dq ^ 2⌋.toNat + 1) : ℚ) / Dq

/-- Candidato a cota superior de `√x`. -/
def sqHi (x : ℚ) : ℚ := sqLo x + 1 / Dq

/-- Producto de intervalos. -/
def imul (a b : ℚ × ℚ) : ℚ × ℚ :=
  (min (min (a.1 * b.1) (a.1 * b.2)) (min (a.2 * b.1) (a.2 * b.2)),
    max (max (a.1 * b.1) (a.1 * b.2)) (max (a.2 * b.1) (a.2 * b.2)))

/-- Evaluación por intervalos en `θ = θq` (las potencias reales se tratan como raíces
cuadradas; `ival_sound` lo exige como hipótesis). -/
def ival (θq : Fin p → ℚ) : KExpr n p → Option (ℚ × ℚ)
  | .qconst q => some (q, q)
  | .par j => some (θq j, θq j)
  | .add a b =>
      match ival θq a, ival θq b with
      | some x, some z => some (x.1 + z.1, x.2 + z.2)
      | _, _ => none
  | .sub a b =>
      match ival θq a, ival θq b with
      | some x, some z => some (x.1 - z.2, x.2 - z.1)
      | _, _ => none
  | .mul a b =>
      match ival θq a, ival θq b with
      | some x, some z => some (imul x z)
      | _, _ => none
  | .div a b =>
      match ival θq a, ival θq b with
      | some x, some z =>
          if 0 < z.1 ∨ z.2 < 0 then some (imul x (1 / z.2, 1 / z.1)) else none
      | _, _ => none
  | .npow a k =>
      match ival θq a with
      | some x => if 0 ≤ x.1 then some (x.1 ^ k, x.2 ^ k) else none
      | none => none
  | .rpow a _ =>
      match ival θq a with
      | some x =>
          if 0 < x.1 ∧ 0 ≤ sqLo x.1 ∧ sqLo x.1 * sqLo x.1 ≤ x.1 ∧ 0 ≤ sqHi x.2 ∧
              x.2 ≤ sqHi x.2 * sqHi x.2 then some (sqLo x.1, sqHi x.2) else none
      | none => none
  | _ => none

/-- Exponentes de las potencias reales. -/
def rpowExps : KExpr n p → List ℝ
  | .rpow a r => r :: rpowExps a
  | .add a b => rpowExps a ++ rpowExps b
  | .sub a b => rpowExps a ++ rpowExps b
  | .mul a b => rpowExps a ++ rpowExps b
  | .div a b => rpowExps a ++ rpowExps b
  | .npow a _ => rpowExps a
  | .exp a => rpowExps a
  | .log a => rpowExps a
  | _ => []

lemma mul_mem_corners {x y a1 a2 b1 b2 : ℝ} (hx1 : a1 ≤ x) (hx2 : x ≤ a2) (hy1 : b1 ≤ y)
    (hy2 : y ≤ b2) :
    min (min (a1 * b1) (a1 * b2)) (min (a2 * b1) (a2 * b2)) ≤ x * y ∧
      x * y ≤ max (max (a1 * b1) (a1 * b2)) (max (a2 * b1) (a2 * b2)) := by
  -- lineal en x para y fijo, y lineal en y en cada extremo
  have hA : min (a1 * y) (a2 * y) ≤ x * y ∧ x * y ≤ max (a1 * y) (a2 * y) := by
    rcases le_total 0 y with hy | hy
    · exact ⟨(min_le_left _ _).trans (mul_le_mul_of_nonneg_right hx1 hy),
        (mul_le_mul_of_nonneg_right hx2 hy).trans (le_max_right _ _)⟩
    · exact ⟨(min_le_right _ _).trans (mul_le_mul_of_nonpos_right hx2 hy),
        (mul_le_mul_of_nonpos_right hx1 hy).trans (le_max_left _ _)⟩
  have hB : ∀ a : ℝ, min (a * b1) (a * b2) ≤ a * y ∧ a * y ≤ max (a * b1) (a * b2) := by
    intro a
    rcases le_total 0 a with ha | ha
    · exact ⟨(min_le_left _ _).trans (mul_le_mul_of_nonneg_left hy1 ha),
        (mul_le_mul_of_nonneg_left hy2 ha).trans (le_max_right _ _)⟩
    · exact ⟨(min_le_right _ _).trans (mul_le_mul_of_nonpos_left hy2 ha),
        (mul_le_mul_of_nonpos_left hy1 ha).trans (le_max_left _ _)⟩
  obtain ⟨h1, h2⟩ := hB a1
  obtain ⟨h3, h4⟩ := hB a2
  constructor
  · refine le_trans ?_ hA.1
    exact le_min ((min_le_left _ _).trans h1) ((min_le_right _ _).trans h3)
  · refine hA.2.trans ?_
    exact max_le (h2.trans (le_max_left _ _)) (h4.trans (le_max_right _ _))

lemma imul_sound {x y : ℝ} {a b : ℚ × ℚ} (hx1 : (a.1 : ℝ) ≤ x) (hx2 : x ≤ a.2)
    (hy1 : (b.1 : ℝ) ≤ y) (hy2 : y ≤ b.2) :
    ((imul a b).1 : ℝ) ≤ x * y ∧ x * y ≤ (imul a b).2 := by
  have := mul_mem_corners hx1 hx2 hy1 hy2
  simp only [imul]
  push_cast
  exact this

/-- **Corrección de la evaluación por intervalos.** -/
theorem ival_sound (θq : Fin p → ℚ) (y : EuclideanSpace ℝ (Fin n)) :
    ∀ e : KExpr n p, (∀ r ∈ rpowExps e, r = 1 / 2) → ∀ l u : ℚ, ival θq e = some (l, u) →
      e.ok (y, qvec θq) ∧ (l : ℝ) ≤ e.eval (y, qvec θq) ∧ e.eval (y, qvec θq) ≤ u := by
  intro e
  induction e with
  | qconst q =>
      intro _ l u h; simp only [ival, Option.some.injEq, Prod.mk.injEq] at h
      obtain ⟨rfl, rfl⟩ := h; exact ⟨trivial, le_rfl, le_rfl⟩
  | par j =>
      intro _ l u h; simp only [ival, Option.some.injEq, Prod.mk.injEq] at h
      obtain ⟨rfl, rfl⟩ := h; exact ⟨trivial, le_rfl, le_rfl⟩
  | add a b ha hb =>
      intro hH l u h
      have hHa : ∀ r ∈ rpowExps a, r = 1 / 2 := fun r hr =>
        hH r (by simp [rpowExps, hr])
      have hHb : ∀ r ∈ rpowExps b, r = 1 / 2 := fun r hr =>
        hH r (by simp [rpowExps, hr])
      simp only [ival] at h
      cases ea : ival θq a with
      | none => simp [ea] at h
      | some x =>
        cases eb : ival θq b with
        | none => simp [ea, eb] at h
        | some z =>
          simp only [ea, eb, Option.some.injEq, Prod.mk.injEq] at h
          obtain ⟨rfl, rfl⟩ := h
          obtain ⟨a0, a1, a2⟩ := ha hHa x.1 x.2 ea
          obtain ⟨b0, b1, b2⟩ := hb hHb z.1 z.2 eb
          refine ⟨⟨a0, b0⟩, ?_, ?_⟩
          · push_cast; show _ ≤ a.eval _ + b.eval _; linarith
          · push_cast; show a.eval _ + b.eval _ ≤ _; linarith
  | sub a b ha hb =>
      intro hH l u h
      have hHa : ∀ r ∈ rpowExps a, r = 1 / 2 := fun r hr =>
        hH r (by simp [rpowExps, hr])
      have hHb : ∀ r ∈ rpowExps b, r = 1 / 2 := fun r hr =>
        hH r (by simp [rpowExps, hr])
      simp only [ival] at h
      cases ea : ival θq a with
      | none => simp [ea] at h
      | some x =>
        cases eb : ival θq b with
        | none => simp [ea, eb] at h
        | some z =>
          simp only [ea, eb, Option.some.injEq, Prod.mk.injEq] at h
          obtain ⟨rfl, rfl⟩ := h
          obtain ⟨a0, a1, a2⟩ := ha hHa x.1 x.2 ea
          obtain ⟨b0, b1, b2⟩ := hb hHb z.1 z.2 eb
          refine ⟨⟨a0, b0⟩, ?_, ?_⟩
          · push_cast; show _ ≤ a.eval _ - b.eval _; linarith
          · push_cast; show a.eval _ - b.eval _ ≤ _; linarith
  | mul a b ha hb =>
      intro hH l u h
      have hHa : ∀ r ∈ rpowExps a, r = 1 / 2 := fun r hr =>
        hH r (by simp [rpowExps, hr])
      have hHb : ∀ r ∈ rpowExps b, r = 1 / 2 := fun r hr =>
        hH r (by simp [rpowExps, hr])
      simp only [ival] at h
      cases ea : ival θq a with
      | none => simp [ea] at h
      | some x =>
        cases eb : ival θq b with
        | none => simp [ea, eb] at h
        | some z =>
          simp only [ea, eb, Option.some.injEq] at h
          obtain ⟨a0, a1, a2⟩ := ha hHa x.1 x.2 ea
          obtain ⟨b0, b1, b2⟩ := hb hHb z.1 z.2 eb
          have := imul_sound a1 a2 b1 b2
          rw [h] at this
          exact ⟨⟨a0, b0⟩, this⟩
  | div a b ha hb =>
      intro hH l u h
      have hHa : ∀ r ∈ rpowExps a, r = 1 / 2 := fun r hr =>
        hH r (by simp [rpowExps, hr])
      have hHb : ∀ r ∈ rpowExps b, r = 1 / 2 := fun r hr =>
        hH r (by simp [rpowExps, hr])
      simp only [ival] at h
      cases ea : ival θq a with
      | none => simp [ea] at h
      | some x =>
        cases eb : ival θq b with
        | none => simp [ea, eb] at h
        | some z =>
          simp only [ea, eb] at h
          split_ifs at h with hz
          simp only [Option.some.injEq] at h
          obtain ⟨a0, a1, a2⟩ := ha hHa x.1 x.2 ea
          obtain ⟨b0, b1, b2⟩ := hb hHb z.1 z.2 eb
          -- 1/b ∈ [1/z₂, 1/z₁]
          have hinv : ((1 / z.2 : ℚ) : ℝ) ≤ 1 / b.eval (y, qvec θq) ∧
              1 / b.eval (y, qvec θq) ≤ ((1 / z.1 : ℚ) : ℝ) := by
            push_cast
            rcases hz with hz | hz
            · have hz' : (0 : ℝ) < z.1 := by exact_mod_cast hz
              exact ⟨one_div_le_one_div_of_le (hz'.trans_le b1) b2,
                one_div_le_one_div_of_le hz' b1⟩
            · have hz' : (z.2 : ℝ) < 0 := by exact_mod_cast hz
              exact ⟨one_div_le_one_div_of_neg_of_le hz' b2,
                one_div_le_one_div_of_neg_of_le (b2.trans_lt hz') b1⟩
          have hb0 : b.eval (y, qvec θq) ≠ 0 := by
            rcases hz with hz | hz
            · have hz' : (0 : ℝ) < z.1 := by exact_mod_cast hz
              exact (hz'.trans_le b1).ne'
            · have hz' : (z.2 : ℝ) < 0 := by exact_mod_cast hz
              exact (b2.trans_lt hz').ne
          have := imul_sound (b := ((1 / z.2 : ℚ), (1 / z.1 : ℚ))) a1 a2 hinv.1 hinv.2
          rw [h] at this
          refine ⟨⟨a0, b0, hb0⟩, ?_⟩
          show (l : ℝ) ≤ a.eval _ / b.eval _ ∧ a.eval _ / b.eval _ ≤ u
          rw [div_eq_mul_one_div]; exact this
  | npow a k ha =>
      intro hH l u h
      simp only [ival] at h
      cases ea : ival θq a with
      | none => simp [ea] at h
      | some x =>
        simp only [ea] at h
        split_ifs at h with hx
        simp only [Option.some.injEq, Prod.mk.injEq] at h
        obtain ⟨rfl, rfl⟩ := h
        obtain ⟨a0, a1, a2⟩ := ha hH x.1 x.2 ea
        have hx' : (0 : ℝ) ≤ x.1 := by exact_mod_cast hx
        refine ⟨a0, ?_, ?_⟩
        · push_cast; exact pow_le_pow_left₀ hx' a1 k
        · push_cast; exact pow_le_pow_left₀ (hx'.trans a1) a2 k
  | rpow a r ha =>
      intro hH l u h
      have hr : r = 1 / 2 := hH r (by simp [rpowExps])
      have hHa : ∀ r ∈ rpowExps a, r = 1 / 2 := fun r' hr' =>
        hH r' (by simp [rpowExps, hr'])
      simp only [ival] at h
      cases ea : ival θq a with
      | none => simp [ea] at h
      | some x =>
        simp only [ea] at h
        split_ifs at h with hx
        simp only [Option.some.injEq, Prod.mk.injEq] at h
        obtain ⟨rfl, rfl⟩ := h
        obtain ⟨hx1, hl0, hl, hu0, hu⟩ := hx
        obtain ⟨a0, a1, a2⟩ := ha hHa x.1 x.2 ea
        have hx1' : (0 : ℝ) < x.1 := by exact_mod_cast hx1
        have hpos : 0 < a.eval (y, qvec θq) := hx1'.trans_le a1
        refine ⟨⟨a0, hpos⟩, ?_, ?_⟩
        · show ((sqLo x.1 : ℚ) : ℝ) ≤ a.eval _ ^ r
          rw [hr, ← Real.sqrt_eq_rpow]
          apply Real.le_sqrt_of_sq_le
          have h1 : ((sqLo x.1 * sqLo x.1 : ℚ) : ℝ) ≤ x.1 := by exact_mod_cast hl
          push_cast at h1
          nlinarith
        · show a.eval _ ^ r ≤ ((sqHi x.2 : ℚ) : ℝ)
          rw [hr, ← Real.sqrt_eq_rpow, Real.sqrt_le_iff]
          have h0 : (0 : ℝ) ≤ sqHi x.2 := by exact_mod_cast hu0
          have h1 : (x.2 : ℝ) ≤ ((sqHi x.2 * sqHi x.2 : ℚ) : ℝ) := by exact_mod_cast hu
          push_cast at h1
          exact ⟨h0, by nlinarith⟩
  | const c => intro _ l u h; simp [ival] at h
  | var i => intro _ l u h; simp [ival] at h
  | exp a _ => intro _ l u h; simp [ival] at h
  | log a _ => intro _ l u h; simp [ival] at h

/-- Dato inicial comprobado por intervalos: `Gᵢ(θ₀) ≥ 0`, y `> 0` en `Σ`. -/
def checkInitI (sx : Fin n → Bool) (θq : Fin p → ℚ) (G : Fin n → KExpr n p) : Bool :=
  (List.finRange n).all fun i =>
    match ival θq (G i) with
    | some x => decide (0 ≤ x.1) && (!sx i || decide (0 < x.1))
    | none => false

theorem initI_sound {sx : Fin n → Bool} {θq : Fin p → ℚ} {G : Fin n → KExpr n p}
    (h : checkInitI sx θq G = true) (hH : ∀ i, ∀ r ∈ rpowExps (G i), r = 1 / 2) :
    ((0 : EuclideanSpace ℝ (Fin n)), qvec θq) ∈ domain G ∧ SPos sx (field G 0 (qvec θq)) := by
  simp only [checkInitI, List.all_eq_true, List.mem_finRange, true_implies] at h
  have key : ∀ i, (G i).ok (0, qvec θq) ∧ 0 ≤ (G i).eval (0, qvec θq) ∧
      (sx i = true → 0 < (G i).eval (0, qvec θq)) := by
    intro i
    have hi := h i
    cases e : ival θq (G i) with
    | none => rw [e] at hi; simp at hi
    | some x =>
      rw [e] at hi
      simp only [Bool.and_eq_true, decide_eq_true_eq, Bool.or_eq_true, Bool.not_eq_eq_eq_not,
        Bool.not_true] at hi
      obtain ⟨ok, l, -⟩ := ival_sound θq 0 (G i) (hH i) x.1 x.2 e
      have h0 : (0 : ℝ) ≤ x.1 := by exact_mod_cast hi.1
      refine ⟨ok, h0.trans l, fun hs => ?_⟩
      rcases hi.2 with h' | h'
      · rw [hs] at h'; exact absurd h' (by decide)
      · have : (0 : ℝ) < x.1 := by exact_mod_cast h'
        exact this.trans_le l
  exact ⟨fun i => (key i).1, fun i => (key i).2.1, fun i hi => (key i).2.2 hi⟩

/-- **Teorema final con positividad estricta y dato inicial certificado por intervalos.** Sin
condiciones pendientes: la solución nominal existe en `[0, T]`, las especies de `Σ` permanecen
`> 0`, queda en el dominio, y la trayectoria es diferenciable respecto a `θ`, con
`S(0) = ∂G/∂θ`. -/
theorem strict_final_initI (pos : Fin p → Bool) (ub : Fin p → Option ℚ × Option ℚ) (sx : Fin n → Bool)
    (Rx : List (KExpr n p × List (Fin n × ℚ)))
    (hN : checkNetS pos ub sx Rx = true) (c : Fin n → ℚ) (hG : checkGrowthS pos ub c Rx = true)
    (G : Fin n → KExpr n p) (θq : Fin p → ℚ) (hI : checkInitI sx θq G = true)
    (hH : ∀ i, ∀ r ∈ rpowExps (G i), r = 1 / 2)
    (hθ : checkPosParams pos θq = true) (hU : checkUB ub θq = true) {T : ℝ} (hT : 0 ≤ T) :
    ∃ x₀ : ℝ → EuclideanSpace ℝ (Fin n), x₀ 0 = field G 0 (qvec θq) ∧
      (∀ t ∈ Icc 0 T,
        HasDerivWithinAt x₀ (field (netF Rx) (x₀ t) (qvec θq)) (Icc 0 T) t ∧
        SPos sx (x₀ t) ∧ (x₀ t, qvec θq) ∈ domain (netF Rx)) ∧
      ∃ x : EuclideanSpace ℝ (Fin p) → ℝ → EuclideanSpace ℝ (Fin n), x (qvec θq) = x₀ ∧
        (∀ᶠ θ in 𝓝 (qvec θq), x θ 0 = field G 0 θ ∧
          ∀ t ∈ Icc 0 T, HasDerivWithinAt (x θ) (field (netF Rx) (x θ t) θ) (Icc 0 T) t) ∧
        ∃ S : ℝ → (EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin n)),
          S 0 = fderiv ℝ (fun θ => field G 0 θ) (qvec θq) ∧
          ∀ t ∈ Icc 0 T, HasFDerivAt (fun θ => x θ t) (S t) (qvec θq) := by
  have hθ₀ : PP pos ub (qvec θq) := ⟨posParams_qvec hθ, ub_qvec hU⟩
  obtain ⟨hdom0, hpos0⟩ := initI_sound hI hH
  obtain ⟨hdom, -, -⟩ := checkNetS_sound hN hθ₀
  obtain ⟨x₀, h0, hsol⟩ := strict_exists Rx hN c hG hθ₀ _ hpos0 hT
  refine ⟨x₀, h0, fun t ht => ⟨(hsol t ht).1, (hsol t ht).2, hdom _ (hsol t ht).2⟩, ?_⟩
  have hcd : ContDiffAt ℝ 1 (fun z : EuclideanSpace ℝ (Fin n) × EuclideanSpace ℝ (Fin p) =>
      field G z.1 z.2) (0, qvec θq) :=
    (contDiffOn_field G).contDiffAt ((isOpen_domain G).mem_nhds hdom0)
  have hin : DifferentiableAt ℝ (fun θ : EuclideanSpace ℝ (Fin p) =>
      ((0 : EuclideanSpace ℝ (Fin n)), θ)) (qvec θq) :=
    (differentiableAt_const _).prodMk differentiableAt_id
  have hdiff : DifferentiableAt ℝ (fun θ => field G 0 θ) (qvec θq) :=
    DifferentiableAt.comp (f := fun θ => ((0 : EuclideanSpace ℝ (Fin n)), θ)) (qvec θq)
      (hcd.differentiableAt le_rfl) hin
  obtain ⟨x, hx, hev, S, hS0, -, hS⟩ := kinetic_hasFDerivAt (netF Rx) hT x₀ (qvec θq)
    (fun t ht => (hsol t ht).1) (fun t ht => hdom _ (hsol t ht).2) (fun θ => field G 0 θ) _
    hdiff.hasFDerivAt h0.symm
  exact ⟨x, hx, hev, S, hS0, hS⟩

end IntervalInit

#print axioms IntervalInit.strict_final_initI

#print axioms IntervalInit.ival_sound
