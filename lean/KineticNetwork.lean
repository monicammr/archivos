import KineticCheck
import GlobalExistence

/-!
# Redes de reacciones: comprobación completa, incluida la existencia global (C4)

Un modelo se representa como una lista `Rx` de términos de velocidad `V_r : KExpr` con su
columna estequiométrica `[(especie, coeficiente)]`. El campo es
`Fᵢ = Σ_r coef_r(i) · V_r` (`netF`). Sobre esta representación Lean comprueba por cálculo:

* `checkNet`: cada `V_r` está bien definido en el ortante y, para cada especie `i` de su columna,
  si el coeficiente es `< 0` el término se anula cuando `yᵢ = 0` (cuasi-positividad); si es
  `≥ 0`, el término es `≥ 0`.
* `checkGrowth`: con pesos racionales `cᵢ ≥ 1`, cada término con peso `w_r = Σᵢ cᵢ·coefᵢ`
  positivo crece como mucho linealmente (`linOK`), los de peso negativo son `≥ 0`, y los demás
  tienen peso `0`. Entonces `Σᵢ cᵢ Fᵢ(z) ≤ a + b Σᵢ cᵢ zᵢ` en el ortante.

`network_final`: si ambas comprobaciones dan `true`, θ₀ > 0 y x(0) ≥ 0 (también comprobados por
cálculo), **la solución nominal existe en [0, T]** (para todo T), es ≥ 0, permanece en el dominio,
las soluciones existen cerca de θ₀ y la trayectoria es diferenciable respecto a θ.
**No queda ninguna condición sin demostrar.**
-/

open Set Filter Topology KineticRegularity PositivityInvariance KineticCheck KineticCheck.KExpr'

namespace KineticNetwork

variable {n p : ℕ}

/-- Coeficiente de la especie `i` en una columna estequiométrica. -/
def coef (col : List (Fin n × ℚ)) (i : Fin n) : ℚ :=
  (col.map fun e => if e.1 = i then e.2 else 0).sum

/-- `Fᵢ = Σ_r coef_r(i) · V_r`. -/
def netExpr (Rx : List (KExpr n p × List (Fin n × ℚ))) (i : Fin n) : KExpr n p :=
  Rx.foldr (fun t acc => KExpr.add (KExpr.mul (KExpr.qconst (coef t.2 i)) t.1) acc)
    (KExpr.qconst 0)

/-- Campo de la red. -/
def netF (Rx : List (KExpr n p × List (Fin n × ℚ))) : Fin n → KExpr n p := netExpr Rx

lemma eval_netExpr (Rx : List (KExpr n p × List (Fin n × ℚ))) (i : Fin n)
    (z : EuclideanSpace ℝ (Fin n) × EuclideanSpace ℝ (Fin p)) :
    (netExpr Rx i).eval z = (Rx.map fun t => ((coef t.2 i : ℚ) : ℝ) * t.1.eval z).sum := by
  induction Rx with
  | nil => show ((0 : ℚ) : ℝ) = _; simp
  | cons t Rx ih =>
      show ((coef t.2 i : ℚ) : ℝ) * t.1.eval z + (netExpr Rx i).eval z = _
      rw [ih, List.map_cons, List.sum_cons]

lemma ok_netExpr (Rx : List (KExpr n p × List (Fin n × ℚ))) (i : Fin n)
    (z : EuclideanSpace ℝ (Fin n) × EuclideanSpace ℝ (Fin p)) (h : ∀ t ∈ Rx, t.1.ok z) :
    (netExpr Rx i).ok z := by
  induction Rx with
  | nil => trivial
  | cons t Rx ih =>
      exact ⟨⟨trivial, h t List.mem_cons_self⟩,
        ih fun t' ht' => h t' (List.mem_cons_of_mem _ ht')⟩

/-! ## Cuasi-positividad término a término -/

/-- Comprobación de un término. -/
def termOK (pos : Fin p → Bool) (t : KExpr n p × List (Fin n × ℚ)) : Bool :=
  okOrth pos t.1 && t.2.all fun e =>
    if decide (e.2 < 0) then vanishes e.1 t.1 else (isNonneg pos t.1 || vanishes e.1 t.1)

def checkNet (pos : Fin p → Bool) (Rx : List (KExpr n p × List (Fin n × ℚ))) : Bool :=
  Rx.all (termOK pos)

lemma coef_mul_nonneg {pos : Fin p → Bool} {t : KExpr n p × List (Fin n × ℚ)}
    (ht : termOK pos t = true) {y : EuclideanSpace ℝ (Fin n)} {θ : EuclideanSpace ℝ (Fin p)}
    (hy : Nonneg y) (hθ : PosParams pos θ) (i : Fin n) (hyi : y i = 0) :
    0 ≤ ((coef t.2 i : ℚ) : ℝ) * t.1.eval (y, θ) := by
  simp only [termOK, Bool.and_eq_true, List.all_eq_true] at ht
  obtain ⟨-, hcol⟩ := ht
  unfold coef
  generalize t.2 = col0 at hcol ⊢
  induction col0 with
  | nil => simp
  | cons e col ih =>
      have he := hcol e List.mem_cons_self
      have hrest : ∀ e' ∈ col, (if decide (e'.2 < 0) then vanishes e'.1 t.1
          else (isNonneg pos t.1 || vanishes e'.1 t.1)) = true :=
        fun e' h' => hcol e' (List.mem_cons_of_mem _ h')
      rw [List.map_cons, List.sum_cons, Rat.cast_add, add_mul]
      refine add_nonneg ?_ (ih hrest)
      by_cases hei : e.1 = i
      · rw [if_pos hei]
        subst hei
        by_cases hs : e.2 < 0
        · rw [if_pos (decide_eq_true hs)] at he
          rw [vanishes_sound e.1 hyi t.1 he, mul_zero]
        · rw [if_neg (by simpa using hs)] at he
          simp only [Bool.or_eq_true] at he
          rcases he with he | he
          · exact mul_nonneg (by exact_mod_cast not_lt.1 hs) (isNonneg_sound hy hθ t.1 he)
          · rw [vanishes_sound e.1 hyi t.1 he, mul_zero]
      · rw [if_neg hei]; simp

/-- La red comprobada tiene dominio ⊇ ortante y es cuasi-positiva. -/
theorem checkNet_sound {pos : Fin p → Bool} {Rx : List (KExpr n p × List (Fin n × ℚ))}
    (h : checkNet pos Rx = true) {θ : EuclideanSpace ℝ (Fin p)} (hθ : PosParams pos θ) :
    (∀ y, Nonneg y → (y, θ) ∈ domain (netF Rx)) ∧
    (∀ y, Nonneg y → ∀ i, y i = 0 → 0 ≤ field (netF Rx) y θ i) := by
  simp only [checkNet, List.all_eq_true] at h
  refine ⟨fun y hy i => ok_netExpr Rx i _ fun t ht => ?_, fun y hy i hyi => ?_⟩
  · have := h t ht
    simp only [termOK, Bool.and_eq_true] at this
    exact okOrth_sound hy hθ t.1 this.1
  · show 0 ≤ (netExpr Rx i).eval (y, θ)
    rw [eval_netExpr]
    apply List.sum_nonneg
    intro x hx
    obtain ⟨t, ht, rfl⟩ := List.mem_map.1 hx
    exact coef_mul_nonneg (h t ht) hy hθ i hyi

/-! ## Crecimiento lineal -/

/-- Sin concentraciones. -/
def varfree : KExpr n p → Bool
  | .const _ => true
  | .qconst _ => true
  | .var _ => false
  | .par _ => true
  | .add a b => varfree a && varfree b
  | .sub a b => varfree a && varfree b
  | .mul a b => varfree a && varfree b
  | .div a b => varfree a && varfree b
  | .npow a _ => varfree a
  | .rpow a _ => varfree a
  | .exp a => varfree a
  | .log a => varfree a

lemma eval_varfree (e : KExpr n p) (h : varfree e = true) (y y' : EuclideanSpace ℝ (Fin n))
    (θ : EuclideanSpace ℝ (Fin p)) : e.eval (y, θ) = e.eval (y', θ) := by
  induction e with
  | const c => rfl
  | qconst q => rfl
  | var i => exact absurd h (by simp [varfree])
  | par j => rfl
  | add a b ha hb =>
      simp only [varfree, Bool.and_eq_true] at h
      show a.eval _ + b.eval _ = a.eval _ + b.eval _; rw [ha h.1, hb h.2]
  | sub a b ha hb =>
      simp only [varfree, Bool.and_eq_true] at h
      show a.eval _ - b.eval _ = a.eval _ - b.eval _; rw [ha h.1, hb h.2]
  | mul a b ha hb =>
      simp only [varfree, Bool.and_eq_true] at h
      show a.eval _ * b.eval _ = a.eval _ * b.eval _; rw [ha h.1, hb h.2]
  | div a b ha hb =>
      simp only [varfree, Bool.and_eq_true] at h
      show a.eval _ / b.eval _ = a.eval _ / b.eval _; rw [ha h.1, hb h.2]
  | npow a k ha => show a.eval _ ^ k = a.eval _ ^ k; rw [ha h]
  | rpow a r ha => show a.eval _ ^ r = a.eval _ ^ r; rw [ha h]
  | exp a ha => show Real.exp (a.eval _) = Real.exp (a.eval _); rw [ha h]
  | log a ha => show Real.log (a.eval _) = Real.log (a.eval _); rw [ha h]

variable (pos : Fin p → Bool)

/-- Acotado inferiormente por una constante positiva en el ortante. -/
def lowerpos : KExpr n p → Bool
  | .add a b => (varfree a && varfree b && isPos pos (.add a b)) ||
      (lowerpos a && isNonneg pos b) || (isNonneg pos a && lowerpos b)
  | e => varfree e && isPos pos e

/-- Cota inferior constante. -/
noncomputable def lowval (θ : EuclideanSpace ℝ (Fin p)) : KExpr n p → ℝ
  | .add a b =>
      if varfree a && varfree b && isPos pos (.add a b) then (KExpr.add a b).eval (0, θ)
      else if lowerpos pos a && isNonneg pos b then lowval θ a else lowval θ b
  | e => e.eval (0, θ)

/-- Crecimiento como mucho lineal en el ortante. -/
def linOK : KExpr n p → Bool
  | .var _ => true
  | .add a b => (varfree a && varfree b) || (linOK a && linOK b)
  | .mul a b => (varfree a && varfree b) || (varfree a && isNonneg pos a && linOK b) ||
      (linOK a && varfree b && isNonneg pos b)
  | .div a b => (varfree a && varfree b) || (linOK a && isNonneg pos a && lowerpos pos b)
  | e => varfree e

/-- Cota lineal `e ≤ A + B Σ zⱼ`, devuelta como `(A, B)`. -/
noncomputable def linBound (θ : EuclideanSpace ℝ (Fin p)) : KExpr n p → ℝ × ℝ
  | .var _ => (0, 1)
  | .add a b =>
      if varfree a && varfree b then (max 0 ((KExpr.add a b).eval (0, θ)), 0)
      else ((linBound θ a).1 + (linBound θ b).1, (linBound θ a).2 + (linBound θ b).2)
  | .mul a b =>
      if varfree a && varfree b then (max 0 ((KExpr.mul a b).eval (0, θ)), 0)
      else if varfree a && isNonneg pos a && linOK pos b then
        (a.eval (0, θ) * (linBound θ b).1, a.eval (0, θ) * (linBound θ b).2)
      else (b.eval (0, θ) * (linBound θ a).1, b.eval (0, θ) * (linBound θ a).2)
  | .div a b =>
      if varfree a && varfree b then (max 0 ((KExpr.div a b).eval (0, θ)), 0)
      else ((linBound θ a).1 / lowval pos θ b, (linBound θ a).2 / lowval pos θ b)
  | e => (max 0 (e.eval (0, θ)), 0)

variable {pos}

/-- Suma de las concentraciones. -/
def ssum (y : EuclideanSpace ℝ (Fin n)) : ℝ := ∑ j, y j

lemma ssum_nonneg {y : EuclideanSpace ℝ (Fin n)} (hy : Nonneg y) : 0 ≤ ssum y :=
  Finset.sum_nonneg fun j _ => hy j

theorem lowerpos_sound {y : EuclideanSpace ℝ (Fin n)} (hy : Nonneg y) {θ : EuclideanSpace ℝ (Fin p)}
    (hθ : PosParams pos θ) :
    ∀ e : KExpr n p, lowerpos pos e = true → 0 < lowval pos θ e ∧ lowval pos θ e ≤ e.eval (y, θ) := by
  have hz : Nonneg (0 : EuclideanSpace ℝ (Fin n)) := KineticCheck.nonneg_zero
  have base : ∀ e : KExpr n p, (varfree e && isPos pos e) = true →
      0 < e.eval (0, θ) ∧ e.eval (0, θ) ≤ e.eval (y, θ) := by
    intro e h
    simp only [Bool.and_eq_true] at h
    exact ⟨isPos_sound hz hθ e h.2, le_of_eq (eval_varfree e h.1 0 y θ)⟩
  intro e
  induction e with
  | add a b ha hb =>
      intro h
      simp only [lowerpos, Bool.or_eq_true, Bool.and_eq_true] at h
      simp only [lowval]
      by_cases h1 : (varfree a && varfree b && isPos pos (KExpr.add a b)) = true
      · rw [if_pos h1]
        simp only [Bool.and_eq_true] at h1
        have hvf : (varfree (KExpr.add a b) && isPos pos (KExpr.add a b)) = true := by
          simp [varfree, h1.1.1, h1.1.2, h1.2]
        exact base _ hvf
      · rw [if_neg h1]
        have hab : a.eval (y, θ) + b.eval (y, θ) = (KExpr.add a b).eval (y, θ) := rfl
        rcases h with (h | ⟨h2, h3⟩) | ⟨h2, h3⟩
        · exact absurd (by simp [h.1.1, h.1.2, h.2]) h1
        · rw [if_pos (by simp [h2, h3])]
          obtain ⟨p1, p2⟩ := ha h2
          refine ⟨p1, ?_⟩
          rw [← hab]; linarith [isNonneg_sound hy hθ b h3]
        · by_cases h4 : (lowerpos pos a && isNonneg pos b) = true
          · rw [if_pos h4]
            simp only [Bool.and_eq_true] at h4
            obtain ⟨p1, p2⟩ := ha h4.1
            refine ⟨p1, ?_⟩
            rw [← hab]; linarith [isNonneg_sound hy hθ b h4.2]
          · rw [if_neg h4]
            obtain ⟨p1, p2⟩ := hb h3
            refine ⟨p1, ?_⟩
            rw [← hab]; linarith [isNonneg_sound hy hθ a h2]
  | const c => intro h; exact base _ (by simpa only [lowerpos] using h)
  | qconst q => intro h; exact base _ (by simpa only [lowerpos] using h)
  | var i => intro h; exact base _ (by simpa only [lowerpos] using h)
  | par j => intro h; exact base _ (by simpa only [lowerpos] using h)
  | sub a b _ _ => intro h; exact base _ (by simpa only [lowerpos] using h)
  | mul a b _ _ => intro h; exact base _ (by simpa only [lowerpos] using h)
  | div a b _ _ => intro h; exact base _ (by simpa only [lowerpos] using h)
  | npow a k _ => intro h; exact base _ (by simpa only [lowerpos] using h)
  | rpow a r _ => intro h; exact base _ (by simpa only [lowerpos] using h)
  | exp a _ => intro h; exact base _ (by simpa only [lowerpos] using h)
  | log a _ => intro h; exact base _ (by simpa only [lowerpos] using h)

theorem linBound_sound {y : EuclideanSpace ℝ (Fin n)} (hy : Nonneg y)
    {θ : EuclideanSpace ℝ (Fin p)} (hθ : PosParams pos θ) :
    ∀ e : KExpr n p, linOK pos e = true →
      0 ≤ (linBound pos θ e).1 ∧ 0 ≤ (linBound pos θ e).2 ∧
      e.eval (y, θ) ≤ (linBound pos θ e).1 + (linBound pos θ e).2 * ssum y := by
  have hz : Nonneg (0 : EuclideanSpace ℝ (Fin n)) := KineticCheck.nonneg_zero
  have hS := ssum_nonneg hy
  have vf : ∀ e : KExpr n p, varfree e = true →
      0 ≤ max 0 (e.eval (0, θ)) ∧ (0 : ℝ) ≤ 0 ∧
      e.eval (y, θ) ≤ max 0 (e.eval (0, θ)) + 0 * ssum y := by
    intro e h
    refine ⟨le_max_left _ _, le_rfl, ?_⟩
    rw [zero_mul, add_zero, eval_varfree e h y 0 θ]; exact le_max_right _ _
  intro e
  induction e with
  | var i =>
      intro _
      refine ⟨le_rfl, zero_le_one, ?_⟩
      show y i ≤ 0 + 1 * ssum y
      rw [zero_add, one_mul]
      exact Finset.single_le_sum (f := fun j => y j) (fun j _ => hy j) (Finset.mem_univ i)
  | add a b ha hb =>
      intro h
      simp only [linBound]
      by_cases h1 : (varfree a && varfree b) = true
      · rw [if_pos h1]
        exact vf (KExpr.add a b) (by simpa [varfree] using h1)
      · rw [if_neg h1]
        simp only [linOK, Bool.or_eq_true, Bool.and_eq_true] at h
        rcases h with h | h
        · exact absurd (by simp [h.1, h.2]) h1
        obtain ⟨a1, a2, a3⟩ := ha h.1
        obtain ⟨b1, b2, b3⟩ := hb h.2
        refine ⟨add_nonneg a1 b1, add_nonneg a2 b2, ?_⟩
        show a.eval (y, θ) + b.eval (y, θ) ≤ _
        nlinarith
  | mul a b ha hb =>
      intro h
      simp only [linBound]
      by_cases h1 : (varfree a && varfree b) = true
      · rw [if_pos h1]
        exact vf (KExpr.mul a b) (by simpa [varfree] using h1)
      · rw [if_neg h1]
        simp only [linOK, Bool.or_eq_true, Bool.and_eq_true] at h
        by_cases h2 : (varfree a && isNonneg pos a && linOK pos b) = true
        · rw [if_pos h2]
          simp only [Bool.and_eq_true] at h2
          have hk : 0 ≤ a.eval (0, θ) := isNonneg_sound hz hθ a h2.1.2
          have hka : a.eval (y, θ) = a.eval (0, θ) := eval_varfree a h2.1.1 y 0 θ
          obtain ⟨b1, b2, b3⟩ := hb h2.2
          refine ⟨mul_nonneg hk b1, mul_nonneg hk b2, ?_⟩
          show a.eval (y, θ) * b.eval (y, θ) ≤ _
          rw [hka]; nlinarith [mul_le_mul_of_nonneg_left b3 hk]
        · rw [if_neg h2]
          rcases h with (h | h) | h
          · exact absurd (by simp [h.1, h.2]) h1
          · exact absurd (by simp [h.1.1, h.1.2, h.2]) h2
          have hk : 0 ≤ b.eval (0, θ) := isNonneg_sound hz hθ b h.2
          have hkb : b.eval (y, θ) = b.eval (0, θ) := eval_varfree b h.1.2 y 0 θ
          obtain ⟨a1, a2, a3⟩ := ha h.1.1
          refine ⟨mul_nonneg hk a1, mul_nonneg hk a2, ?_⟩
          show a.eval (y, θ) * b.eval (y, θ) ≤ _
          rw [hkb]; nlinarith [mul_le_mul_of_nonneg_right a3 hk]
  | div a b ha hb =>
      intro h
      simp only [linBound]
      by_cases h1 : (varfree a && varfree b) = true
      · rw [if_pos h1]
        exact vf (KExpr.div a b) (by simpa [varfree] using h1)
      · rw [if_neg h1]
        simp only [linOK, Bool.or_eq_true, Bool.and_eq_true] at h
        rcases h with h | h
        · exact absurd (by simp [h.1, h.2]) h1
        obtain ⟨a1, a2, a3⟩ := ha h.1.1
        obtain ⟨l1, l2⟩ := lowerpos_sound hy hθ b h.2
        have ha0 : 0 ≤ a.eval (y, θ) := isNonneg_sound hy hθ a h.1.2
        refine ⟨div_nonneg a1 l1.le, div_nonneg a2 l1.le, ?_⟩
        show a.eval (y, θ) / b.eval (y, θ) ≤ _
        calc a.eval (y, θ) / b.eval (y, θ) ≤ a.eval (y, θ) / lowval pos θ b :=
              div_le_div_of_nonneg_left ha0 l1 l2
          _ ≤ ((linBound pos θ a).1 + (linBound pos θ a).2 * ssum y) / lowval pos θ b :=
              div_le_div_of_nonneg_right a3 l1.le
          _ = _ := by ring
  | const c => intro h; exact vf _ h
  | qconst q => intro h; exact vf _ h
  | par j => intro h; exact vf _ h
  | sub a b _ _ => intro h; exact vf _ h
  | npow a k _ => intro h; exact vf _ h
  | rpow a r _ => intro h; exact vf _ h
  | exp a _ => intro h; exact vf _ h
  | log a _ => intro h; exact vf _ h

/-- Peso de un término: `Σ cᵢ · coefᵢ`. -/
def wgt (c : Fin n → ℚ) (col : List (Fin n × ℚ)) : ℚ := (col.map fun e => c e.1 * e.2).sum

variable (pos) in
def growthOK (c : Fin n → ℚ) (t : KExpr n p × List (Fin n × ℚ)) : Bool :=
  decide (wgt c t.2 = 0) || (decide (wgt c t.2 < 0) && isNonneg pos t.1) ||
    (decide (0 < wgt c t.2) && linOK pos t.1)

variable (pos) in
def checkGrowth (c : Fin n → ℚ) (Rx : List (KExpr n p × List (Fin n × ℚ))) : Bool :=
  (List.finRange n).all (fun i => decide (1 ≤ c i)) && Rx.all (growthOK pos c)

lemma sum_c_coef (c : Fin n → ℚ) (col : List (Fin n × ℚ)) :
    ∑ i, (c i : ℝ) * ((coef col i : ℚ) : ℝ) = ((wgt c col : ℚ) : ℝ) := by
  induction col with
  | nil => simp [coef, wgt]
  | cons e col ih =>
      have h1 : ∀ i, (c i : ℝ) * ((coef (e :: col) i : ℚ) : ℝ)
          = (c i : ℝ) * (((if e.1 = i then e.2 else 0 : ℚ)) : ℝ)
            + (c i : ℝ) * ((coef col i : ℚ) : ℝ) := by
        intro i; simp only [coef, List.map_cons, List.sum_cons]; push_cast; ring
      rw [Finset.sum_congr rfl fun i _ => h1 i, Finset.sum_add_distrib, ih]
      have h2 : ∑ i, (c i : ℝ) * (((if e.1 = i then e.2 else 0 : ℚ)) : ℝ)
          = (c e.1 : ℝ) * (e.2 : ℝ) := by
        rw [Finset.sum_eq_single e.1]
        · simp
        · intro b _ hb; rw [if_neg (Ne.symm hb)]; simp
        · intro h; exact absurd (Finset.mem_univ _) h
      rw [h2]; simp only [wgt, List.map_cons, List.sum_cons]; push_cast; ring

lemma sum_c_netExpr (c : Fin n → ℚ) (Rx : List (KExpr n p × List (Fin n × ℚ)))
    (z : EuclideanSpace ℝ (Fin n) × EuclideanSpace ℝ (Fin p)) :
    ∑ i, (c i : ℝ) * (netExpr Rx i).eval z
      = (Rx.map fun t => ((wgt c t.2 : ℚ) : ℝ) * t.1.eval z).sum := by
  induction Rx with
  | nil => show ∑ x, (c x : ℝ) * ((0 : ℚ) : ℝ) = _; simp
  | cons t Rx ih =>
      have h1 : ∀ i, (c i : ℝ) * (netExpr (t :: Rx) i).eval z
          = (c i : ℝ) * ((coef t.2 i : ℚ) : ℝ) * t.1.eval z
            + (c i : ℝ) * (netExpr Rx i).eval z := by
        intro i
        show (c i : ℝ) * (((coef t.2 i : ℚ) : ℝ) * t.1.eval z + (netExpr Rx i).eval z) = _
        ring
      rw [Finset.sum_congr rfl fun i _ => h1 i, Finset.sum_add_distrib, ih, ← Finset.sum_mul,
        sum_c_coef, List.map_cons, List.sum_cons]

/-- **Cota de crecimiento** de una red comprobada. -/
theorem checkGrowth_sound {c : Fin n → ℚ} {Rx : List (KExpr n p × List (Fin n × ℚ))}
    (h : checkGrowth pos c Rx = true) {θ : EuclideanSpace ℝ (Fin p)} (hθ : PosParams pos θ) :
    ∃ a b : ℝ, 0 ≤ a ∧ 0 ≤ b ∧ ∀ y, Nonneg y →
      ∑ i, (c i : ℝ) * field (netF Rx) y θ i ≤ a + b * ∑ i, (c i : ℝ) * y i := by
  simp only [checkGrowth, Bool.and_eq_true, List.all_eq_true, List.mem_finRange,
    true_implies, decide_eq_true_eq] at h
  obtain ⟨hc1, hR⟩ := h
  -- cotas por término
  let A : KExpr n p × List (Fin n × ℚ) → ℝ := fun t =>
    if 0 < wgt c t.2 then (wgt c t.2 : ℝ) * (linBound pos θ t.1).1 else 0
  let Bt : KExpr n p × List (Fin n × ℚ) → ℝ := fun t =>
    if 0 < wgt c t.2 then (wgt c t.2 : ℝ) * (linBound pos θ t.1).2 else 0
  have hz : Nonneg (0 : EuclideanSpace ℝ (Fin n)) := KineticCheck.nonneg_zero
  have hterm : ∀ t ∈ Rx, ∀ y, Nonneg y →
      0 ≤ A t ∧ 0 ≤ Bt t ∧ ((wgt c t.2 : ℚ) : ℝ) * t.1.eval (y, θ) ≤ A t + Bt t * ssum y := by
    intro t ht y hy
    have hg := hR t ht
    simp only [growthOK, Bool.or_eq_true, Bool.and_eq_true, decide_eq_true_eq] at hg
    by_cases hw : 0 < wgt c t.2
    · have hlin : linOK pos t.1 = true := by
        rcases hg with (h0 | ⟨h0, -⟩) | ⟨-, h0⟩
        · exact absurd h0 hw.ne'
        · exact absurd h0 (not_lt.2 hw.le)
        · exact h0
      obtain ⟨l1, l2, l3⟩ := linBound_sound hy hθ t.1 hlin
      have hw' : (0 : ℝ) < (wgt c t.2 : ℝ) := by exact_mod_cast hw
      simp only [A, Bt, if_pos hw]
      refine ⟨mul_nonneg hw'.le l1, mul_nonneg hw'.le l2, ?_⟩
      nlinarith [mul_le_mul_of_nonneg_left l3 hw'.le]
    · simp only [A, Bt, if_neg hw]
      refine ⟨le_rfl, le_rfl, ?_⟩
      rw [zero_add, zero_mul]
      rcases hg with (h0 | ⟨h0, h1⟩) | ⟨h0, -⟩
      · rw [h0]; simp
      · have : ((wgt c t.2 : ℚ) : ℝ) < 0 := by exact_mod_cast h0
        exact mul_nonpos_of_nonpos_of_nonneg this.le (isNonneg_sound hy hθ t.1 h1)
      · exact absurd h0 hw
  refine ⟨(Rx.map A).sum, (Rx.map Bt).sum,
    List.sum_nonneg fun x hx => by
      obtain ⟨t, ht, rfl⟩ := List.mem_map.1 hx; exact (hterm t ht 0 hz).1,
    List.sum_nonneg fun x hx => by
      obtain ⟨t, ht, rfl⟩ := List.mem_map.1 hx; exact (hterm t ht 0 hz).2.1, ?_⟩
  intro y hy
  have hsum : ∑ i, (c i : ℝ) * field (netF Rx) y θ i
      = (Rx.map fun t => ((wgt c t.2 : ℚ) : ℝ) * t.1.eval (y, θ)).sum :=
    sum_c_netExpr c Rx (y, θ)
  have hle : (Rx.map fun t => ((wgt c t.2 : ℚ) : ℝ) * t.1.eval (y, θ)).sum
      ≤ (Rx.map fun t => A t + Bt t * ssum y).sum := by
    apply List.sum_le_sum
    intro t ht
    exact (hterm t ht y hy).2.2
  have hsplit : (Rx.map fun t => A t + Bt t * ssum y).sum
      = (Rx.map A).sum + (Rx.map Bt).sum * ssum y := by
    rw [List.sum_map_add, List.sum_map_mul_right]
  have hS : ssum y ≤ ∑ i, (c i : ℝ) * y i := by
    apply Finset.sum_le_sum
    intro i _
    have : (1 : ℝ) ≤ (c i : ℝ) := by exact_mod_cast hc1 i
    nlinarith [hy i]
  have hB0 : 0 ≤ (Rx.map Bt).sum := List.sum_nonneg fun x hx => by
    obtain ⟨t, ht, rfl⟩ := List.mem_map.1 hx; exact (hterm t ht 0 hz).2.1
  rw [hsum]
  calc _ ≤ (Rx.map fun t => A t + Bt t * ssum y).sum := hle
    _ = (Rx.map A).sum + (Rx.map Bt).sum * ssum y := hsplit
    _ ≤ _ := by nlinarith [mul_le_mul_of_nonneg_left hS hB0]

/-! ## Teorema final: sin condiciones pendientes -/

lemma c_ge_one {c : Fin n → ℚ} {Rx : List (KExpr n p × List (Fin n × ℚ))}
    (h : checkGrowth pos c Rx = true) (i : Fin n) : (1 : ℝ) ≤ (c i : ℝ) := by
  simp only [checkGrowth, Bool.and_eq_true, List.all_eq_true, List.mem_finRange,
    true_implies, decide_eq_true_eq] at h
  exact_mod_cast h.1 i

/-- Existencia global de la solución nominal para una red comprobada. -/
theorem network_exists (Rx : List (KExpr n p × List (Fin n × ℚ)))
    (hN : checkNet pos Rx = true) (c : Fin n → ℚ) (hG : checkGrowth pos c Rx = true)
    {θ₀ : EuclideanSpace ℝ (Fin p)} (hθ₀ : PosParams pos θ₀)
    (x0 : EuclideanSpace ℝ (Fin n)) (hx0 : Nonneg x0) {T : ℝ} (hT : 0 ≤ T) :
    ∃ x₀ : ℝ → EuclideanSpace ℝ (Fin n), x₀ 0 = x0 ∧
      ∀ t ∈ Icc 0 T, HasDerivWithinAt x₀ (field (netF Rx) (x₀ t) θ₀) (Icc 0 T) t ∧
        Nonneg (x₀ t) := by
  obtain ⟨horth, hqp⟩ := checkNet_sound hN hθ₀
  obtain ⟨a, b, ha, hb, hgr⟩ := checkGrowth_sound hG hθ₀
  set U : Set (EuclideanSpace ℝ (Fin n)) := (fun y => (y, θ₀)) ⁻¹' domain (netF Rx)
  have hcont : Continuous fun y : EuclideanSpace ℝ (Fin n) => (y, θ₀) :=
    continuous_id.prodMk continuous_const
  have hU : IsOpen U := (isOpen_domain _).preimage hcont
  have hv : ContDiffOn ℝ 1 (fun y => field (netF Rx) y θ₀) U :=
    (contDiffOn_field (netF Rx)).comp (contDiff_id.prodMk contDiff_const).contDiffOn
      (fun y hy => hy)
  exact GlobalExistence.exists_global_solution (fun y => field (netF Rx) y θ₀) hU hv
    (fun z hz => horth z hz) (fun z hz i hi => hqp z hz i hi) (fun i => (c i : ℝ))
    one_pos (c_ge_one hG) ha hb (fun z hz => hgr z hz) x0 hx0 hT

/-- **Teorema final de una red comprobada (dato inicial constante).** Sin condiciones
pendientes: la solución nominal existe en `[0, T]`, es `≥ 0` y queda en el dominio; las
soluciones existen cerca de `θ₀` y la trayectoria es diferenciable respecto a `θ`. -/
theorem network_final (Rx : List (KExpr n p × List (Fin n × ℚ)))
    (hN : checkNet pos Rx = true) (c : Fin n → ℚ) (hG : checkGrowth pos c Rx = true)
    (θq : Fin p → ℚ) (hθ : checkPosParams pos θq = true)
    (xq : Fin n → ℚ) (hx : checkNonneg xq = true) {T : ℝ} (hT : 0 ≤ T) :
    ∃ x₀ : ℝ → EuclideanSpace ℝ (Fin n), x₀ 0 = qvec xq ∧
      (∀ t ∈ Icc 0 T,
        HasDerivWithinAt x₀ (field (netF Rx) (x₀ t) (qvec θq)) (Icc 0 T) t ∧
        Nonneg (x₀ t) ∧ (x₀ t, qvec θq) ∈ domain (netF Rx)) ∧
      ∃ x : EuclideanSpace ℝ (Fin p) → ℝ → EuclideanSpace ℝ (Fin n), x (qvec θq) = x₀ ∧
        (∀ᶠ θ in 𝓝 (qvec θq), x θ 0 = qvec xq ∧
          ∀ t ∈ Icc 0 T, HasDerivWithinAt (x θ) (field (netF Rx) (x θ t) θ) (Icc 0 T) t) ∧
        ∃ S : ℝ → (EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin n)), S 0 = 0 ∧
          ∀ t ∈ Icc 0 T, HasFDerivAt (fun θ => x θ t) (S t) (qvec θq) := by
  have hθ₀ := posParams_qvec hθ
  obtain ⟨horth, hqp⟩ := checkNet_sound hN hθ₀
  obtain ⟨x₀, h0, hsol⟩ := network_exists Rx hN c hG hθ₀ (qvec xq) (nonneg_qvec hx) hT
  refine ⟨x₀, h0, fun t ht => ⟨(hsol t ht).1, (hsol t ht).2, horth _ (hsol t ht).2⟩, ?_⟩
  exact kinetic_hasFDerivAt_of_nonneg (netF Rx) hT x₀ (qvec θq) horth hqp
    (fun t ht => (hsol t ht).1) (by rw [h0]; exact nonneg_qvec hx) (fun _ => qvec xq) 0
    (hasFDerivAt_const _ _) h0.symm

/-- **Teorema final de una red comprobada, con condición inicial `x₀(θ) = G(θ)`.** -/
theorem network_final_init (Rx : List (KExpr n p × List (Fin n × ℚ)))
    (hN : checkNet pos Rx = true) (c : Fin n → ℚ) (hG : checkGrowth pos c Rx = true)
    (G : Fin n → KExpr n p) (hI : checkInit pos G = true)
    (θq : Fin p → ℚ) (hθ : checkPosParams pos θq = true) {T : ℝ} (hT : 0 ≤ T) :
    ∃ x₀ : ℝ → EuclideanSpace ℝ (Fin n), x₀ 0 = field G 0 (qvec θq) ∧
      (∀ t ∈ Icc 0 T,
        HasDerivWithinAt x₀ (field (netF Rx) (x₀ t) (qvec θq)) (Icc 0 T) t ∧
        Nonneg (x₀ t) ∧ (x₀ t, qvec θq) ∈ domain (netF Rx)) ∧
      ∃ x : EuclideanSpace ℝ (Fin p) → ℝ → EuclideanSpace ℝ (Fin n), x (qvec θq) = x₀ ∧
        (∀ᶠ θ in 𝓝 (qvec θq), x θ 0 = field G 0 θ ∧
          ∀ t ∈ Icc 0 T, HasDerivWithinAt (x θ) (field (netF Rx) (x θ t) θ) (Icc 0 T) t) ∧
        ∃ S : ℝ → (EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin n)),
          S 0 = fderiv ℝ (fun θ => field G 0 θ) (qvec θq) ∧
          ∀ t ∈ Icc 0 T, HasFDerivAt (fun θ => x θ t) (S t) (qvec θq) := by
  have hθ₀ := posParams_qvec hθ
  obtain ⟨horth, hqp⟩ := checkNet_sound hN hθ₀
  have hx0 := init_nonneg hI hθ₀
  obtain ⟨x₀, h0, hsol⟩ := network_exists Rx hN c hG hθ₀ _ hx0 hT
  refine ⟨x₀, h0, fun t ht => ⟨(hsol t ht).1, (hsol t ht).2, horth _ (hsol t ht).2⟩, ?_⟩
  exact kinetic_hasFDerivAt_of_nonneg (netF Rx) hT x₀ (qvec θq) horth hqp
    (fun t ht => (hsol t ht).1) (by rw [h0]; exact hx0) (fun θ => field G 0 θ) _
    (init_differentiable hI hθ₀).hasFDerivAt h0.symm

end KineticNetwork

#print axioms KineticNetwork.checkNet_sound
#print axioms KineticNetwork.checkGrowth_sound
#print axioms KineticNetwork.network_final
#print axioms KineticNetwork.network_final_init
